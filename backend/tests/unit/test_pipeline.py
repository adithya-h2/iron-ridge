"""Pipeline state machine unit tests."""

import pytest

from app.core.enums import DealStatus, PIPELINE_TRANSITIONS
from app.core.exceptions import InvalidTransitionError
from app.services.pipeline import PipelineService


class FakeDealRepo:
    def __init__(self, status: str | None = "LEAD"):
        self.deal = type("Deal", (), {"status": status, "deal_id": "00000000-0000-0000-0000-000000000001"})()

    async def get_by_id(self, deal_id):
        return self.deal

    async def update(self, deal_id, **kwargs):
        for k, v in kwargs.items():
            setattr(self.deal, k, v)
        return self.deal


class FakeAuditService:
    async def log_status_change(self, **kwargs):
        return None


@pytest.fixture
def pipeline():
    return PipelineService(FakeDealRepo(), FakeAuditService())


def test_valid_transitions_defined():
    assert DealStatus.LEAD in PIPELINE_TRANSITIONS
    assert DealStatus.QUALIFIED in PIPELINE_TRANSITIONS[DealStatus.LEAD] or DealStatus.QUALIFICATION in PIPELINE_TRANSITIONS[DealStatus.LEAD]


def test_validate_rejects_unknown_status(pipeline):
    with pytest.raises(InvalidTransitionError):
        pipeline.validate_transition("LEAD", "UNKNOWN")


def test_validate_lead_to_qualification(pipeline):
    pipeline.validate_transition("LEAD", "QUALIFICATION")


def test_validate_rejects_lead_to_delivered(pipeline):
    with pytest.raises(InvalidTransitionError):
        pipeline.validate_transition("LEAD", "DELIVERED")
