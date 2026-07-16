"""Lead intake API integration tests."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_lead_intake_service
from app.core.enums import LeadSource
from app.schemas.lead import LeadIntakeRequest, LeadIntakeResponse, NormalizedLead


@pytest.fixture
def mock_lead_intake():
    service = AsyncMock()
    service.intake = AsyncMock(
        return_value=LeadIntakeResponse(
            deal_id=uuid4(),
            customer_id=uuid4(),
            workflow_id=uuid4(),
            lead_source=LeadSource.WEBSITE.value,
            submission_channel="web_form",
            status="LEAD",
            is_duplicate=False,
            company_name="Test Corp",
        )
    )
    return service


@pytest.fixture
async def leads_client(mock_lead_intake):
    from app.main import app

    app.dependency_overrides[get_lead_intake_service] = lambda: mock_lead_intake
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_lead_success(leads_client, mock_lead_intake):
    response = await leads_client.post(
        "/api/v1/leads",
        json={
            "source": "WEBSITE",
            "submission_channel": "web_form",
            "company_name": "Test Corp",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["status"] == "LEAD"
    mock_lead_intake.intake.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_lead_schedules_n8n_publish_when_enabled(monkeypatch, mock_lead_intake):
    from app.api.routes.v1 import leads as leads_route

    monkeypatch.setattr(leads_route.settings, "feature_n8n_publish", True)
    monkeypatch.setattr(
        leads_route.settings,
        "n8n_webhook_base_url",
        "https://n8n.example.app/webhook/test-uuid",
    )

    background_tasks = MagicMock()
    request = MagicMock()
    request.state.request_id = "req-test-1"

    workflow_trigger = MagicMock()
    notification_preparation = MagicMock()
    notification_preparation.build_n8n_webhook_payload.return_value = {
        "deal_id": "deal-1",
        "request_id": "req-test-1",
    }

    lead_validator = MagicMock()
    lead_validator.validate_and_normalize.return_value = NormalizedLead(
        source=LeadSource.WEBSITE,
        submission_channel="web_form",
        company_name="Test Corp",
    )

    data = LeadIntakeRequest(
        source=LeadSource.WEBSITE,
        submission_channel="web_form",
        company_name="Test Corp",
    )

    response = await leads_route.create_lead(
        request,
        data,
        background_tasks,
        mock_lead_intake,
        workflow_trigger,
        notification_preparation,
        lead_validator,
    )

    assert response.success is True
    background_tasks.add_task.assert_called_once()
    call_args = background_tasks.add_task.call_args
    assert call_args.args[0] is leads_route._publish_lead_created_to_n8n


@pytest.mark.asyncio
async def test_create_lead_validation_error(leads_client, mock_lead_intake):
    from app.main import app

    from app.core.exceptions import ValidationAppError

    mock_lead_intake.intake = AsyncMock(
        side_effect=ValidationAppError("company_name or org_name is required")
    )
    response = await leads_client.post(
        "/api/v1/leads",
        json={"source": "API", "submission_channel": "test"},
    )
    assert response.status_code == 422
    app.dependency_overrides.pop(get_lead_intake_service, None)


@pytest.mark.asyncio
async def test_n8n_lead_webhook_delegates(mock_lead_intake):
    from app.main import app

    app.dependency_overrides[get_lead_intake_service] = lambda: mock_lead_intake
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            "/webhooks/n8n/lead",
            json={"org_name": "County EMS", "city": "Denver"},
        )
    assert response.status_code == 200
    assert response.json()["success"] is True
    app.dependency_overrides.clear()
