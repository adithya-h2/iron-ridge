"""Universal lead intake API — v1."""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, Request, status

from app.api.deps import (
    get_lead_intake_service,
    get_lead_validator,
    get_notification_preparation_service,
    get_workflow_trigger_service,
)
from app.core.config import settings
from app.core.enums import LeadSource
from app.schemas.common import ApiResponse
from app.schemas.lead import LeadIntakeRequest, LeadIntakeResponse
from app.services.lead_intake import LeadIntakeService
from app.services.lead_validator import LeadValidator
from app.services.notification_preparation import NotificationPreparationService
from app.services.workflow_trigger import WorkflowTriggerService

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


async def _publish_lead_created_to_n8n(
    workflow_trigger: WorkflowTriggerService,
    workflow_id: UUID,
    deal_id: UUID,
    source: LeadSource,
    payload: dict,
) -> None:
    await workflow_trigger.trigger_lead_created(
        workflow_id=workflow_id,
        deal_id=deal_id,
        source=source,
        payload=payload,
    )


@router.post(
    "",
    response_model=ApiResponse[LeadIntakeResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Universal lead intake",
    description=(
        "Single entry point for all lead channels (website, dashboard, API, email, "
        "CSV, WhatsApp, voice, trade show, phone). Validates, deduplicates, creates "
        "customer + deal, audits, and triggers workflow."
    ),
)
async def create_lead(
    request: Request,
    data: LeadIntakeRequest,
    background_tasks: BackgroundTasks,
    service: LeadIntakeService = Depends(get_lead_intake_service),
    workflow_trigger: WorkflowTriggerService = Depends(get_workflow_trigger_service),
    notification_preparation: NotificationPreparationService = Depends(
        get_notification_preparation_service
    ),
    lead_validator: LeadValidator = Depends(get_lead_validator),
) -> ApiResponse[LeadIntakeResponse]:
    result = await service.intake(data)
    if settings.feature_n8n_publish and settings.n8n_webhook_base_url:
        normalized = lead_validator.validate_and_normalize(data)
        payload = notification_preparation.build_n8n_webhook_payload(
            normalized,
            result,
            request_id=_rid(request),
        )
        background_tasks.add_task(
            _publish_lead_created_to_n8n,
            workflow_trigger,
            result.workflow_id,
            result.deal_id,
            normalized.source,
            payload,
        )
    return ApiResponse(success=True, data=result, request_id=_rid(request))
