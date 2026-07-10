"""Prepares notification payloads after lead intake."""

import logging
from uuid import UUID

from app.core.config import settings
from app.schemas.lead import LeadIntakeResponse, NormalizedLead
from app.services.slack import SlackService

logger = logging.getLogger(__name__)


class NotificationPreparationService:
    def __init__(self, slack_service: SlackService | None = None) -> None:
        self.slack_service = slack_service

    def build_lead_notification_payload(
        self,
        lead: NormalizedLead,
        deal_id: UUID,
        workflow_id: UUID,
        is_duplicate: bool,
    ) -> dict:
        return {
            "event": "lead_intake",
            "deal_id": str(deal_id),
            "workflow_id": str(workflow_id),
            "company_name": lead.company_name,
            "source": lead.source.value,
            "submission_channel": lead.submission_channel,
            "is_duplicate": is_duplicate,
            "email": lead.email,
            "phone": lead.phone,
        }

    async def notify_lead_created(
        self,
        lead: NormalizedLead,
        response: LeadIntakeResponse,
    ) -> None:
        payload = self.build_lead_notification_payload(
            lead,
            response.deal_id,
            response.workflow_id,
            response.is_duplicate,
        )
        logger.info("Lead notification prepared", extra=payload)
        if not settings.slack_bot_token or not self.slack_service:
            return
        try:
            await self.slack_service.client.chat_postMessage(
                channel=settings.slack_approval_channel,
                text=(
                    f"*New Lead* — {lead.company_name}\n"
                    f"Source: {lead.source.value} via {lead.submission_channel}\n"
                    f"Deal: `{response.deal_id}`"
                ),
            )
        except Exception as exc:
            logger.warning("Slack lead notification failed", extra={"error": str(exc)})
