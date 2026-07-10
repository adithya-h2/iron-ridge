"""Lead intake API integration tests."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_lead_intake_service
from app.core.enums import LeadSource
from app.schemas.lead import LeadIntakeResponse


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
