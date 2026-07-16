"""Lead intake unit tests."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.enums import LeadSource
from app.core.exceptions import ValidationAppError
from app.schemas.lead import LeadIntakeRequest, NormalizedLead
from app.services.duplicate_detection import DuplicateDetectionService, DuplicateMatch
from app.services.lead_intake import LeadIntakeService
from app.services.lead_validator import LeadValidator


def test_lead_validator_requires_company():
    validator = LeadValidator()
    with pytest.raises(ValidationAppError, match="company_name or org_name"):
        validator.validate_and_normalize(
            LeadIntakeRequest(source=LeadSource.WEBSITE, submission_channel="web_form")
        )


def test_lead_validator_normalizes_org_name():
    validator = LeadValidator()
    result = validator.validate_and_normalize(
        LeadIntakeRequest(
            source=LeadSource.API,
            submission_channel="n8n",
            org_name="  City Fire Dept  ",
            email="Admin@Example.COM",
        )
    )
    assert result.company_name == "City Fire Dept"
    assert result.email == "admin@example.com"


def test_lead_validator_invalid_quantity():
    validator = LeadValidator()
    with pytest.raises(ValidationAppError, match="required_quantity"):
        validator.validate_and_normalize(
            LeadIntakeRequest(
                source=LeadSource.API,
                submission_channel="test",
                org_name="Test Co",
                required_quantity="not-a-number",
            )
        )


@pytest.mark.asyncio
async def test_duplicate_detection_finds_match():
    customer_id = uuid4()
    repo = MagicMock()
    existing = MagicMock()
    existing.customer_id = customer_id
    existing.email = "test@example.com"
    existing.phone = None
    existing.company_name = "Acme"
    repo.session.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=lambda: existing))
    service = DuplicateDetectionService(repo)
    match = await service.find_duplicate(
        NormalizedLead(
            source=LeadSource.EMAIL,
            submission_channel="inbox",
            company_name="Acme",
            email="test@example.com",
        )
    )
    assert match is not None
    assert match.customer_id == customer_id


@pytest.mark.asyncio
async def test_lead_intake_service_happy_path():
    customer_id = uuid4()
    deal_id = uuid4()
    workflow_id = uuid4()

    lead_creation_repo = AsyncMock()
    lead_creation_repo.create_lead = AsyncMock(
        return_value=MagicMock(
            customer_id=customer_id,
            deal_id=deal_id,
            workflow_id=workflow_id,
            lead_source="WEBSITE",
            submission_channel="web_form",
            status="LEAD",
        )
    )

    duplicate_detection = AsyncMock()
    duplicate_detection.find_duplicate = AsyncMock(return_value=None)

    audit_service = AsyncMock()
    workflow_trigger = MagicMock()
    workflow_trigger.generate_workflow_id = MagicMock(return_value=workflow_id)
    workflow_trigger.trigger_lead_created = AsyncMock(return_value=workflow_id)

    notification = AsyncMock()

    service = LeadIntakeService(
        lead_creation_repo=lead_creation_repo,
        lead_validator=LeadValidator(),
        duplicate_detection=duplicate_detection,
        audit_service=audit_service,
        workflow_trigger=workflow_trigger,
        notification_preparation=notification,
    )

    result = await service.intake(
        LeadIntakeRequest(
            source=LeadSource.WEBSITE,
            submission_channel="web_form",
            company_name="Metro EMS",
        )
    )
    assert result.deal_id == deal_id
    assert result.workflow_id == workflow_id
    assert result.is_duplicate is False
    audit_service.log_action.assert_awaited_once()
    workflow_trigger.trigger_lead_created.assert_not_called()
