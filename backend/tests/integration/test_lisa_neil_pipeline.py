"""Lisa → Neil pipeline transition integration test (in-memory fake repo)."""

import asyncio
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.agents.lisa import LisaAgent
from app.agents.neil import NeilAgent
from app.core.enums import DealStatus
from app.core.exceptions import InvalidTransitionError
from app.schemas.agent import AgentExecuteRequest
from app.services.pipeline import PipelineService


class FakeDealRepo:
    """Simulates DealRepository with in-memory status tracking."""

    def __init__(self, status: str = "LEAD") -> None:
        self.deal_id = uuid4()
        self.deal = MagicMock()
        self.deal.deal_id = self.deal_id
        self.deal.status = status
        self.deal.customer_id = uuid4()
        self.deal.priority = None
        self.deal.approval_status = None
        self.deal.lead_source = None
        self.deal.workflow_id = None
        self.deal.submission_channel = None
        self.deal.created_at = None
        self.deal.updated_at = None

    async def get_latest_lead_by_company_name(self, company_name: str):
        if self.deal.status == DealStatus.LEAD.value:
            return self.deal
        return None

    async def get_by_id(self, deal_id):
        if str(deal_id) == str(self.deal_id):
            return self.deal
        return None

    async def get_by_id_or_raise(self, deal_id):
        deal = await self.get_by_id(deal_id)
        if deal is None:
            raise Exception("not found")
        return deal

    async def update(self, deal_id, **kwargs):
        for key, value in kwargs.items():
            if value is not None and hasattr(self.deal, key):
                setattr(self.deal, key, value)
        return self.deal


@pytest.fixture
def fake_repo():
    return FakeDealRepo("LEAD")


@pytest.fixture
def pipeline(fake_repo):
    audit = AsyncMock()
    audit.log_status_change = AsyncMock()
    audit.log_action = AsyncMock()
    return PipelineService(fake_repo, audit)


@pytest.mark.asyncio
async def test_lisa_resolves_deal_id_from_org_name(pipeline, fake_repo):
    lisa = LisaAgent(
        AsyncMock(),
        AsyncMock(),
        pipeline.audit_service,
        fake_repo,
        AsyncMock(),
        pipeline,
    )
    req = AgentExecuteRequest(org_name="Test Corp", lead_score=85)
    await lisa.process_response(req, '{"qualified": true, "lead_score": 85}')
    assert req.deal_id == str(fake_repo.deal_id)
    assert fake_repo.deal.status == DealStatus.QUALIFIED.value


@pytest.mark.asyncio
async def test_lisa_qualifies_then_neil_transitions(pipeline, fake_repo):
    lisa = LisaAgent(
        AsyncMock(),
        AsyncMock(),
        pipeline.audit_service,
        fake_repo,
        AsyncMock(),
        pipeline,
    )
    neil = NeilAgent(
        AsyncMock(),
        AsyncMock(),
        pipeline.audit_service,
        AsyncMock(),
        pipeline,
    )
    deal_id = str(fake_repo.deal_id)
    lisa_req = AgentExecuteRequest(deal_id=deal_id, org_name="Test Corp", lead_score=85)
    await lisa.process_response(lisa_req, '{"qualified": true, "lead_score": 85}')
    assert fake_repo.deal.status == DealStatus.QUALIFIED.value

    neil_req = AgentExecuteRequest(
        deal_id=deal_id,
        org_name="Test Corp",
        vehicle_type="Ambulance",
        required_quantity=1,
    )
    await neil.process_response(neil_req, '{"requirements": "Standard config"}')
    assert fake_repo.deal.status == DealStatus.REQUIREMENTS_COLLECTED.value


@pytest.mark.asyncio
async def test_neil_fails_when_deal_still_lead(pipeline, fake_repo):
    neil = NeilAgent(
        AsyncMock(),
        AsyncMock(),
        pipeline.audit_service,
        AsyncMock(),
        pipeline,
    )
    deal_id = str(fake_repo.deal_id)
    neil_req = AgentExecuteRequest(
        deal_id=deal_id,
        vehicle_type="Ambulance",
        required_quantity=1,
    )
    with pytest.raises(InvalidTransitionError, match="LEAD.*REQUIREMENTS"):
        await neil.process_response(neil_req, '{"requirements": "test"}')
