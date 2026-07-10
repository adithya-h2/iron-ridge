"""Slack service unit tests."""

import hashlib
import hmac
import json
import time
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.enums import ApprovalStatus
from app.services.slack import SlackService


@pytest.fixture
def slack_service(monkeypatch):
    monkeypatch.setattr("app.services.slack.settings.slack_bot_token", "")
    monkeypatch.setattr("app.services.slack.settings.slack_signing_secret", "test-secret")
    approval_repo = AsyncMock()
    quotation_repo = AsyncMock()
    approval_service = AsyncMock()
    return SlackService(approval_repo, quotation_repo, approval_service)


def test_verify_signature_valid(slack_service, monkeypatch):
    monkeypatch.setattr("app.services.slack.settings.slack_signing_secret", "test-secret")
    ts = str(int(time.time()))
    body = b"payload=test"
    sig_basestring = f"v0:{ts}:{body.decode()}"
    sig = "v0=" + hmac.new(
        b"test-secret", sig_basestring.encode(), hashlib.sha256
    ).hexdigest()
    assert slack_service.verify_signature(ts, body, sig)


def test_verify_signature_invalid(slack_service):
    assert not slack_service.verify_signature(str(int(time.time())), b"body", "v0=bad")


@pytest.mark.asyncio
async def test_send_approval_skips_without_token(slack_service):
    await slack_service.send_approval_request(uuid4(), uuid4())


@pytest.mark.asyncio
async def test_order_notification_skips_without_token(slack_service):
    await slack_service.send_order_created_notification(uuid4(), uuid4(), "Acme")


@pytest.mark.asyncio
async def test_pipeline_failure_logs_without_token(slack_service):
    await slack_service.send_pipeline_failure_notification(uuid4(), "MARTY", "timeout")


@pytest.mark.asyncio
async def test_handle_interaction_approve(slack_service, monkeypatch):
    monkeypatch.setattr("app.services.slack.settings.slack_bot_token", "")
    qid = uuid4()
    approval = MagicMock()
    approval.approval_id = uuid4()
    slack_service.approval_repo.filter_by = AsyncMock(return_value=[approval])
    slack_service.approval_service.decide = AsyncMock()

    payload = {
        "actions": [
            {
                "value": json.dumps(
                    {"approval_action": "approve", "quotation_id": str(qid)}
                )
            }
        ]
    }
    result = await slack_service.handle_interaction(payload)
    assert result["decision"] == ApprovalStatus.APPROVED.value
    slack_service.approval_service.decide.assert_awaited_once()
