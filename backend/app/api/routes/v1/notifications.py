"""Notification trigger API for n8n."""

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_notification_service, require_agent_access
from app.schemas.auth import UserResponse
from app.schemas.common import ApiResponse
from app.schemas.notification import NotificationRequest, NotificationResult
from app.services.notification import NotificationService

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


@router.post("", response_model=ApiResponse[NotificationResult])
async def send_notification(
    request: Request,
    body: NotificationRequest,
    service: NotificationService = Depends(get_notification_service),
    _: UserResponse | None = Depends(require_agent_access),
) -> ApiResponse[NotificationResult]:
    if body.deal_id:
        request.state.deal_id = str(body.deal_id)
    if body.workflow_id:
        request.state.workflow_id = str(body.workflow_id)
    result = await service.send(body)
    return ApiResponse(success=True, data=result, request_id=_rid(request))
