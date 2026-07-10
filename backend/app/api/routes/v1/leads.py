"""Universal lead intake API — v1."""

from fastapi import APIRouter, Depends, Request, status

from app.api.deps import get_lead_intake_service
from app.schemas.common import ApiResponse
from app.schemas.lead import LeadIntakeRequest, LeadIntakeResponse
from app.services.lead_intake import LeadIntakeService

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


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
    service: LeadIntakeService = Depends(get_lead_intake_service),
) -> ApiResponse[LeadIntakeResponse]:
    result = await service.intake(data)
    return ApiResponse(success=True, data=result, request_id=_rid(request))
