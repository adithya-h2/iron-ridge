"""Consultation request service."""

import logging
from uuid import UUID
import httpx

from app.core.config import settings
from app.models.consultation import Consultation
from app.repositories.consultation_repository import ConsultationRepository
from app.schemas.consultation import ConsultationRequestCreate, ConsultationCreateSuccessResponse

logger = logging.getLogger(__name__)


class ConsultationService:
    def __init__(self, repo: ConsultationRepository) -> None:
        self.repo = repo

    async def create_consultation(
        self, request_data: ConsultationRequestCreate
    ) -> ConsultationCreateSuccessResponse:
        """
        Validate and save the incoming request, trigger n8n webhook, and return response.
        """
        logger.info(
            "Received incoming consultation request",
            extra={
                "organization_name": request_data.organization_name,
                "business_email": request_data.business_email,
            },
        )

        # Save to database
        consultation = await self.repo.create(
            organization_name=request_data.organization_name,
            organization_type=request_data.organization_type,
            department=request_data.department,
            website=request_data.website,
            contact_person=request_data.contact_person,
            job_title=request_data.job_title,
            business_email=request_data.business_email,
            phone_number=request_data.phone_number,
            preferred_contact_method=request_data.preferred_contact_method,
            country=request_data.country,
            state=request_data.state,
            city=request_data.city,
            vehicle_category=request_data.vehicle_category,
            estimated_quantity=request_data.estimated_quantity,
            purchase_timeline=request_data.purchase_timeline,
            requirement_summary=request_data.requirement_summary,
            consent=request_data.consent,
        )

        logger.info(
            "Consultation request saved to database",
            extra={"consultation_id": str(consultation.id)},
        )

        # Trigger n8n webhook (non-blocking / error-resilient)
        await self._trigger_n8n_webhook(consultation)

        return ConsultationCreateSuccessResponse(consultation_id=consultation.id)

    async def get_consultation(self, consultation_id: UUID) -> Consultation | None:
        """Retrieve a consultation request by ID."""
        return await self.repo.get_by_id(consultation_id)

    async def list_consultations(self, pagination=None, filters=None):
        """List and paginate all consultation requests."""
        return await self.repo.list(pagination=pagination, filters=filters)

    async def _trigger_n8n_webhook(self, consultation: Consultation) -> None:
        webhook_url = settings.n8n_webhook_url
        if not webhook_url:
            logger.warning(
                "N8N_WEBHOOK_URL not configured. Skipping webhook trigger.",
                extra={"consultation_id": str(consultation.id)},
            )
            return

        payload = {
            "consultation_id": str(consultation.id),
            "organization_name": consultation.organization_name,
            "organization_type": consultation.organization_type,
            "contact_person": consultation.contact_person,
            "email": consultation.business_email,
            "phone": consultation.phone_number,
            "vehicle_category": consultation.vehicle_category,
            "estimated_quantity": consultation.estimated_quantity,
            "country": consultation.country,
            "state": consultation.state,
            "city": consultation.city,
            "purchase_timeline": consultation.purchase_timeline,
            "requirement_summary": consultation.requirement_summary,
        }

        logger.info(
            "Triggering n8n webhook",
            extra={"webhook_url": webhook_url, "consultation_id": str(consultation.id)},
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    webhook_url,
                    json=payload,
                    timeout=settings.n8n_timeout_seconds or 15.0,
                )
            
            if response.status_code >= 400:
                logger.error(
                    "n8n webhook returned error status code",
                    extra={
                        "status_code": response.status_code,
                        "response_text": response.text,
                        "consultation_id": str(consultation.id),
                    },
                )
            else:
                logger.info(
                    "n8n webhook triggered successfully",
                    extra={
                        "status_code": response.status_code,
                        "consultation_id": str(consultation.id),
                    },
                )
        except Exception as exc:
            # Resilient to webhook failure — do not fail the API response
            logger.error(
                "Failed to trigger n8n webhook due to an exception",
                extra={"error": str(exc), "consultation_id": str(consultation.id)},
                exc_info=True,
            )
