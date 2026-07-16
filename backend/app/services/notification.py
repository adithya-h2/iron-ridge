"""Unified notification service — Slack, Email, SMS (stub)."""

import logging
import smtplib
from email.mime.text import MIMEText

from app.core.config import settings
from app.core.enums import LeadSource
from app.schemas.notification import (
    ChannelDeliveryResult,
    NotificationChannel,
    NotificationRequest,
    NotificationResult,
    NotificationTemplate,
)
from app.services.slack import SlackService

logger = logging.getLogger(__name__)


def format_notification(template: NotificationTemplate, context: dict) -> tuple[str, str]:
    """Return (subject, body) for a notification template."""
    company = context.get("company_name") or context.get("org_name") or "Unknown"
    deal_id = context.get("deal_id", "N/A")

    templates = {
        NotificationTemplate.LEAD_CREATED: (
            f"New Lead — {company}",
            f"New lead received from {context.get('source', 'API')}.\n"
            f"Company: {company}\nDeal: {deal_id}",
        ),
        NotificationTemplate.LEAD_VALIDATED: (
            f"Lead Validated — {company}",
            f"Lead {deal_id} has been validated and qualified.",
        ),
        NotificationTemplate.APPROVAL_REQUEST: (
            f"Approval Required — Deal {deal_id}",
            f"Quotation {context.get('quotation_id', 'N/A')} requires approval.\n"
            f"Total: {context.get('grand_total', 'N/A')}",
        ),
        NotificationTemplate.APPROVAL_DECIDED: (
            f"Approval {context.get('decision', 'updated')} — Deal {deal_id}",
            f"Decision: {context.get('decision')}\nRemarks: {context.get('remarks', '')}",
        ),
        NotificationTemplate.ORDER_CREATED: (
            f"Order Created — Deal {deal_id}",
            f"Order {context.get('order_id', 'N/A')} created for {company}.",
        ),
        NotificationTemplate.PIPELINE_FAILURE: (
            f"Pipeline Failure — Deal {deal_id}",
            f"Agent: {context.get('agent', 'unknown')}\nError: {context.get('error', 'unknown')}",
        ),
        NotificationTemplate.GENERIC: (
            context.get("subject", "Iron Ridge Notification"),
            context.get("body", context.get("message", "Notification from Iron Ridge.")),
        ),
    }
    return templates.get(template, templates[NotificationTemplate.GENERIC])


class NotificationService:
    def __init__(self, slack_service: SlackService | None = None) -> None:
        self.slack_service = slack_service

    async def send(self, request: NotificationRequest) -> NotificationResult:
        subject, body = format_notification(request.template, request.context)
        deliveries: list[ChannelDeliveryResult] = []

        for channel in request.channels:
            if channel == NotificationChannel.SLACK:
                deliveries.append(await self._send_slack(request, subject, body))
            elif channel == NotificationChannel.EMAIL:
                deliveries.append(await self._send_email(subject, body, request.context))
            elif channel == NotificationChannel.SMS:
                deliveries.append(
                    ChannelDeliveryResult(
                        channel=channel,
                        success=False,
                        detail="SMS channel not configured",
                    )
                )
        return NotificationResult(template=request.template, deliveries=deliveries)

    async def _send_slack(
        self, request: NotificationRequest, subject: str, body: str
    ) -> ChannelDeliveryResult:
        if not settings.slack_bot_token or not self.slack_service:
            return ChannelDeliveryResult(
                channel=NotificationChannel.SLACK,
                success=False,
                detail="Slack not configured",
            )
        try:
            if request.template == NotificationTemplate.APPROVAL_REQUEST:
                from uuid import UUID

                deal_id = UUID(str(request.context["deal_id"]))
                quotation_id = UUID(str(request.context["quotation_id"]))
                await self.slack_service.send_approval_request(
                    deal_id,
                    quotation_id,
                    request.context.get("grand_total"),
                )
            else:
                await self.slack_service.client.chat_postMessage(
                    channel=settings.slack_approval_channel,
                    text=f"*{subject}*\n{body}",
                )
            return ChannelDeliveryResult(channel=NotificationChannel.SLACK, success=True)
        except Exception as exc:
            logger.warning("Slack notification failed", extra={"error": str(exc)})
            return ChannelDeliveryResult(
                channel=NotificationChannel.SLACK, success=False, detail=str(exc)
            )

    async def _send_email(
        self, subject: str, body: str, context: dict
    ) -> ChannelDeliveryResult:
        if not settings.email_enabled or not settings.smtp_host:
            return ChannelDeliveryResult(
                channel=NotificationChannel.EMAIL,
                success=False,
                detail="Email not configured",
            )
        recipient = context.get("email") or settings.email_from
        if not recipient:
            return ChannelDeliveryResult(
                channel=NotificationChannel.EMAIL,
                success=False,
                detail="No recipient email",
            )
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = settings.email_from
            msg["To"] = recipient
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as server:
                if settings.smtp_user and settings.smtp_password:
                    server.starttls()
                    server.login(settings.smtp_user, settings.smtp_password)
                server.send_message(msg)
            return ChannelDeliveryResult(channel=NotificationChannel.EMAIL, success=True)
        except Exception as exc:
            logger.warning("Email notification failed", extra={"error": str(exc)})
            return ChannelDeliveryResult(
                channel=NotificationChannel.EMAIL, success=False, detail=str(exc)
            )

    async def notify_lead_created(
        self,
        company_name: str,
        deal_id: str,
        workflow_id: str,
        source: LeadSource,
        submission_channel: str,
        is_duplicate: bool,
        email: str | None = None,
    ) -> NotificationResult:
        return await self.send(
            NotificationRequest(
                template=NotificationTemplate.LEAD_CREATED,
                channels=[NotificationChannel.SLACK],
                context={
                    "company_name": company_name,
                    "deal_id": deal_id,
                    "workflow_id": workflow_id,
                    "source": source.value,
                    "submission_channel": submission_channel,
                    "is_duplicate": is_duplicate,
                    "email": email,
                },
            )
        )
