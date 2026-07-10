"""Full pipeline transition matrix unit tests."""

import pytest

from app.core.enums import DealStatus, PIPELINE_TRANSITIONS
from app.core.exceptions import InvalidTransitionError
from app.services.pipeline import PipelineService


class FakeDealRepo:
    def __init__(self, status: str | None = "LEAD"):
        self.deal = type(
            "Deal",
            (),
            {"status": status, "deal_id": "00000000-0000-0000-0000-000000000001"},
        )()

    async def get_by_id(self, deal_id):
        return self.deal

    async def update(self, deal_id, **kwargs):
        for k, v in kwargs.items():
            setattr(self.deal, k, v)
        return self.deal


class FakeAuditService:
    def __init__(self):
        self.logs: list[dict] = []

    async def log_status_change(self, **kwargs):
        self.logs.append(kwargs)


@pytest.fixture
def pipeline():
    return PipelineService(FakeDealRepo(), FakeAuditService())


def _all_statuses() -> list[DealStatus]:
    return list(DealStatus)


@pytest.mark.parametrize("from_status,allowed_targets", PIPELINE_TRANSITIONS.items())
def test_allowed_transitions(from_status, allowed_targets, pipeline):
    for target in allowed_targets:
        pipeline.validate_transition(from_status.value, target.value)


@pytest.mark.parametrize("from_status,allowed_targets", PIPELINE_TRANSITIONS.items())
def test_forbidden_transitions(from_status, allowed_targets, pipeline):
    allowed_values = {t.value for t in allowed_targets}
    for status in _all_statuses():
        if status == from_status:
            continue
        if status.value in allowed_values:
            continue
        with pytest.raises(InvalidTransitionError):
            pipeline.validate_transition(from_status.value, status.value)


def test_new_deal_must_start_at_lead(pipeline):
    with pytest.raises(InvalidTransitionError):
        pipeline.validate_transition(None, DealStatus.QUALIFIED.value)


@pytest.mark.asyncio
async def test_happy_path_lead_to_delivered():
    """LEAD → ... → DELIVERED via service layer transitions."""
    audit = FakeAuditService()
    repo = FakeDealRepo("LEAD")
    pipeline = PipelineService(repo, audit)

    path = [
        DealStatus.QUALIFICATION,
        DealStatus.QUALIFIED,
        DealStatus.REQUIREMENTS,
        DealStatus.REQUIREMENTS_COLLECTED,
        DealStatus.PRICING,
        DealStatus.PRICED,
        DealStatus.APPROVAL_PENDING,
        DealStatus.APPROVED,
        DealStatus.ORDER_CREATED,
        DealStatus.PRODUCTION,
        DealStatus.DELIVERED,
    ]

    deal_id = "00000000-0000-0000-0000-000000000001"
    for target in path:
        await pipeline.transition(deal_id, target.value, "TEST", f"Move to {target.value}")

    assert repo.deal.status == DealStatus.DELIVERED.value
    assert len(audit.logs) == len(path)
    assert audit.logs[0]["previous_status"] == "LEAD"
    assert audit.logs[-1]["new_status"] == DealStatus.DELIVERED.value
