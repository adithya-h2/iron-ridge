"""Audit log routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request

from app.api.deps import get_audit_service, require_auth
from app.schemas.auth import UserResponse
from app.schemas.common import ApiResponse, PaginatedResponse, PaginationParams
from app.schemas.audit import AuditLogResponse
from app.services.audit import AuditService

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


@router.get("", response_model=ApiResponse[PaginatedResponse[AuditLogResponse]])
async def list_audit_logs(
    request: Request,
    deal_id: UUID,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: AuditService = Depends(get_audit_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[PaginatedResponse[AuditLogResponse]]:
    pagination = PaginationParams(page=page, page_size=page_size)
    result = await service.get_by_deal(deal_id, pagination)
    return ApiResponse(success=True, data=result, request_id=_rid(request))
