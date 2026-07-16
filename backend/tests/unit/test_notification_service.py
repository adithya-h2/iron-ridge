"""NotificationService unit tests."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.enums import LeadSource
from app.schemas.notification import NotificationChannel, NotificationRequest, NotificationTemplate
from app.services.notification import NotificationService, format_notification


def test_format_notification_lead_created():
    subject, body = format_notification(
        NotificationTemplate.LEAD_CREATED,
        {"company_name": "City Fire", "deal_id": "abc", "source": "API"},
    )
    assert "City Fire" in subject
    assert "abc" in body


@pytest.mark.asyncio
async def test_send_slack_not_configured():
    service = NotificationService(slack_service=None)
    result = await service.send(
        NotificationRequest(
            template=NotificationTemplate.GENERIC,
            channels=[NotificationChannel.SLACK],
            context={"message": "test"},
        )
    )
    assert result.deliveries[0].success is False


@pytest.mark.asyncio
async def test_notify_lead_created_delegates(monkeypatch):
    slack = MagicMock()
    slack.client = AsyncMock()
    slack.client.chat_postMessage = AsyncMock()
    monkeypatch.setattr("app.services.notification.settings.slack_bot_token", "xoxb-test")
    service = NotificationService(slack_service=slack)
    await service.notify_lead_created(
        company_name="Test Corp",
        deal_id=str(uuid4()),
        workflow_id=str(uuid4()),
        source=LeadSource.API,
        submission_channel="test",
        is_duplicate=False,
    )
    slack.client.chat_postMessage.assert_awaited_once()
