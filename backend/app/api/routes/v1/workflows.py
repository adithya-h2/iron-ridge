"""Workflow status and timeline API routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.api.deps import (
    get_workflow_retry_service,
    get_workflow_status_service,
    require_auth,
)
from app.schemas.auth import UserResponse
from app.schemas.common import ApiResponse, PaginationParams
from app.schemas.workflow import WorkflowStatusResponse, WorkflowTimelineResponse
from app.services.workflow_retry import WorkflowRetryService
from app.services.workflow_status import WorkflowStatusService

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


@router.get("/{deal_id}", response_model=ApiResponse[WorkflowStatusResponse])
async def get_workflow_status(
    request: Request,
    deal_id: UUID,
    service: WorkflowStatusService = Depends(get_workflow_status_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[WorkflowStatusResponse]:
    request.state.deal_id = str(deal_id)
    status_data = await service.get_status(deal_id)
    if status_data.workflow_id:
        request.state.workflow_id = str(status_data.workflow_id)
    return ApiResponse(success=True, data=status_data, request_id=_rid(request))


@router.get("/{deal_id}/timeline", response_model=ApiResponse[WorkflowTimelineResponse])
async def get_workflow_timeline(
    request: Request,
    deal_id: UUID,
    pagination: PaginationParams = Depends(),
    service: WorkflowStatusService = Depends(get_workflow_status_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[WorkflowTimelineResponse]:
    request.state.deal_id = str(deal_id)
    timeline = await service.get_timeline(deal_id, pagination)
    return ApiResponse(success=True, data=timeline, request_id=_rid(request))


@router.post("/{deal_id}/retry", response_model=ApiResponse[dict])
async def record_workflow_retry(
    request: Request,
    deal_id: UUID,
    retry_service: WorkflowRetryService = Depends(get_workflow_retry_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[dict]:
    """Record an explicit retry attempt (n8n); does not re-run agents."""
    await retry_service.record_retry_attempt(deal_id)
    return ApiResponse(
        success=True,
        data={"deal_id": str(deal_id), "recorded": True},
        request_id=_rid(request),
    )
