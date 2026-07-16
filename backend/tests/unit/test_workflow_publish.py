"""n8n workflow publish unit tests."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.core.config import settings
from app.core.enums import LeadSource
from app.schemas.lead import LeadIntakeResponse, NormalizedLead
from app.services.notification_preparation import NotificationPreparationService
from app.services.workflow import StubWorkflowService


@pytest.fixture
def enable_n8n_publish(monkeypatch):
    monkeypatch.setattr(settings, "feature_n8n_publish", True)
    monkeypatch.setattr(
        settings,
        "n8n_webhook_base_url",
        "https://n8n.example.app/webhook/abc-123/",
    )


def test_build_n8n_webhook_payload_maps_fields():
    service = NotificationPreparationService(notification_service=MagicMock())
    normalized = NormalizedLead(
        source=LeadSource.WEBSITE,
        submission_channel="web_form",
        company_name="Metro EMS",
        contact_person="Jane Doe",
        email="jane@example.com",
        phone="+15551234567",
        city="Denver",
        country="US",
        vehicle_type="Ambulance",
        required_quantity=2,
    )
    response = LeadIntakeResponse(
        deal_id=uuid4(),
        customer_id=uuid4(),
        workflow_id=uuid4(),
        lead_source="WEBSITE",
        submission_channel="web_form",
        status="LEAD",
        is_duplicate=False,
        company_name="Metro EMS",
    )

    payload = service.build_n8n_webhook_payload(
        normalized,
        response,
        request_id="req-abc",
    )

    assert payload["org_name"] == "Metro EMS"
    assert payload["first_name"] == "Jane"
    assert payload["deal_id"] == str(response.deal_id)
    assert payload["customer_id"] == str(response.customer_id)
    assert payload["workflow_id"] == str(response.workflow_id)
    assert payload["vehicle_type"] == "Ambulance"
    assert payload["required_quantity"] == "2"
    assert payload["request_id"] == "req-abc"


@pytest.mark.asyncio
async def test_publish_posts_to_full_webhook_url(enable_n8n_publish):
    workflow_id = uuid4()
    deal_id = uuid4()

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "ok"

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.workflow.httpx.AsyncClient", return_value=mock_client):
        service = StubWorkflowService()
        await service.publish_lead_created(
            workflow_id,
            deal_id,
            LeadSource.WEBSITE,
            {"event": "lead_intake", "request_id": "req-1"},
        )

    mock_client.post.assert_awaited_once()
    url = mock_client.post.await_args.args[0]
    assert url == "https://n8n.example.app/webhook/abc-123"
    assert "/lead-created" not in url
    body = mock_client.post.await_args.kwargs["json"]
    assert body["deal_id"] == str(deal_id)
    assert body["workflow_id"] == str(workflow_id)
    assert body["request_id"] == "req-1"


@pytest.mark.asyncio
async def test_publish_connection_failure_does_not_raise(enable_n8n_publish):
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=ConnectionError("timeout"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.workflow.httpx.AsyncClient", return_value=mock_client):
        service = StubWorkflowService()
        await service.publish_lead_created(
            uuid4(),
            uuid4(),
            LeadSource.WEBSITE,
            {},
        )


@pytest.mark.asyncio
async def test_publish_non_2xx_does_not_raise(enable_n8n_publish):
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "internal error"

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    with patch("app.services.workflow.httpx.AsyncClient", return_value=mock_client):
        service = StubWorkflowService()
        await service.publish_lead_created(
            uuid4(),
            uuid4(),
            LeadSource.WEBSITE,
            {},
        )


@pytest.mark.asyncio
async def test_publish_skipped_when_feature_disabled(monkeypatch):
    monkeypatch.setattr(settings, "feature_n8n_publish", False)
    monkeypatch.setattr(settings, "n8n_webhook_base_url", "https://n8n.example/webhook/x")

    with patch("app.services.workflow.httpx.AsyncClient") as mock_client_cls:
        service = StubWorkflowService()
        await service.publish_lead_created(uuid4(), uuid4(), LeadSource.WEBSITE, {})
        mock_client_cls.assert_not_called()
