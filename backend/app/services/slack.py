"""Slack integration for Victor approval workflow."""

import hashlib
import hmac
import json
import logging
import time
from uuid import UUID

from slack_sdk.web.async_client import AsyncWebClient

from app.core.config import settings
from app.core.enums import AgentName, ApprovalStatus
from app.core.exceptions import ValidationAppError
from app.repositories.approval import ApprovalRepository
from app.repositories.quotation import QuotationRepository
from app.services.approval import ApprovalService

logger = logging.getLogger(__name__)


class SlackService:
    def __init__(
        self,
        approval_repo: ApprovalRepository,
        quotation_repo: QuotationRepository,
        approval_service: ApprovalService,
    ) -> None:
        self.approval_repo = approval_repo
        self.quotation_repo = quotation_repo
        self.approval_service = approval_service
        self._client: AsyncWebClient | None = None

    @property
    def client(self) -> AsyncWebClient:
        if self._client is None:
            self._client = AsyncWebClient(token=settings.slack_bot_token)
        return self._client

    async def send_approval_request(
        self,
        deal_id: UUID,
        quotation_id: UUID,
        grand_total: str | None = None,
    ) -> None:
        if not settings.slack_bot_token:
            logger.warning("Slack bot token not configured — skipping notification")
            return

        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"*Approval Required* — Deal `{deal_id}`\n"
                        f"Quotation: `{quotation_id}`\n"
                        f"Total: {grand_total or 'N/A'}"
                    ),
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Approve"},
                        "style": "primary",
                        "action_id": "approve",
                        "value": json.dumps({"approval_action": "approve", "quotation_id": str(quotation_id)}),
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Reject"},
                        "style": "danger",
                        "action_id": "reject",
                        "value": json.dumps({"approval_action": "reject", "quotation_id": str(quotation_id)}),
                    },
                ],
            },
        ]
        await self.client.chat_postMessage(
            channel=settings.slack_approval_channel,
            text=f"Approval required for deal {deal_id}",
            blocks=blocks,
        )

    def verify_signature(self, timestamp: str, body: bytes, signature: str) -> bool:
        if not settings.slack_signing_secret:
            return True
        if abs(time.time() - int(timestamp)) > 60 * 5:
            return False
        sig_basestring = f"v0:{timestamp}:{body.decode()}"
        computed = "v0=" + hmac.new(
            settings.slack_signing_secret.encode(),
            sig_basestring.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(computed, signature)

    async def handle_interaction(self, payload: dict) -> dict:
        actions = payload.get("actions", [])
        if not actions:
            raise ValidationAppError("No actions in Slack payload")

        action_value = json.loads(actions[0].get("value", "{}"))
        quotation_id = UUID(action_value["quotation_id"])
        decision = (
            ApprovalStatus.APPROVED.value
            if action_value.get("approval_action") == "approve"
            else ApprovalStatus.REJECTED.value
        )

        approvals = await self.approval_repo.filter_by(quotation_id=quotation_id)
        if not approvals:
            raise ValidationAppError("No pending approval found")

        approval = approvals[0]
        await self.approval_service.decide(
            approval.approval_id,
            ApprovalDecideRequest(
                decision=decision,
                approved_by=AgentName.VICTOR.value,
                remarks="Slack decision",
            ),
        )
        return {"ok": True, "decision": decision}
