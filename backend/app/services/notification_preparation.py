"""Prepares notification payloads after lead intake."""

import logging
from uuid import UUID

from app.schemas.lead import LeadIntakeResponse, NormalizedLead
from app.services.notification import NotificationService

logger = logging.getLogger(__name__)


class NotificationPreparationService:
    def __init__(self, notification_service: NotificationService) -> None:
        self.notification_service = notification_service

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

    def build_n8n_webhook_payload(
        self,
        lead: NormalizedLead,
        response: LeadIntakeResponse,
        *,
        request_id: str | None = None,
    ) -> dict:
        """Payload for n8n webhook (Edit Fields reads $json.body.*)."""
        first_name = None
        if lead.contact_person:
            parts = lead.contact_person.strip().split()
            first_name = parts[0] if parts else None

        payload: dict = {
            "event": "lead_intake",
            "deal_id": str(response.deal_id),
            "customer_id": str(response.customer_id),
            "workflow_id": str(response.workflow_id),
            "org_name": lead.company_name,
            "company_name": lead.company_name,
            "first_name": first_name,
            "email": lead.email,
            "phone": lead.phone,
            "city": lead.city,
            "country": lead.country,
            "vehicle_type": lead.vehicle_type,
            "required_quantity": (
                str(lead.required_quantity) if lead.required_quantity is not None else None
            ),
            "source": lead.source.value,
            "submission_channel": lead.submission_channel,
            "is_duplicate": response.is_duplicate,
        }
        if request_id:
            payload["request_id"] = request_id
        return payload

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
        await self.notification_service.notify_lead_created(
            company_name=lead.company_name or "Unknown",
            deal_id=str(response.deal_id),
            workflow_id=str(response.workflow_id),
            source=lead.source,
            submission_channel=lead.submission_channel,
            is_duplicate=response.is_duplicate,
            email=lead.email,
        )
