"""Approval routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from app.api.deps import get_approval_service, require_auth
from app.core.enums import ApprovalStatus
from app.schemas.approval import ApprovalCreate, ApprovalDecideRequest, ApprovalRequestBody, ApprovalResponse
from app.schemas.auth import UserResponse
from app.schemas.common import ApiResponse
from app.services.approval import ApprovalService

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


@router.post("", response_model=ApiResponse[ApprovalResponse], status_code=status.HTTP_201_CREATED)
async def create_approval(
    request: Request,
    data: ApprovalCreate,
    service: ApprovalService = Depends(get_approval_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[ApprovalResponse]:
    approval = await service.create(data)
    return ApiResponse(success=True, data=approval, request_id=_rid(request))


@router.get("/{approval_id}", response_model=ApiResponse[ApprovalResponse])
async def get_approval(
    request: Request,
    approval_id: UUID,
    service: ApprovalService = Depends(get_approval_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[ApprovalResponse]:
    approval = await service.get(approval_id)
    return ApiResponse(success=True, data=approval, request_id=_rid(request))


@router.post("/{approval_id}/approve", response_model=ApiResponse[ApprovalResponse])
async def approve_approval(
    request: Request,
    approval_id: UUID,
    service: ApprovalService = Depends(get_approval_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[ApprovalResponse]:
    approval = await service.decide(
        approval_id,
        ApprovalDecideRequest(decision=ApprovalStatus.APPROVED.value),
    )
    return ApiResponse(success=True, data=approval, request_id=_rid(request))


@router.post("/{approval_id}/reject", response_model=ApiResponse[ApprovalResponse])
async def reject_approval(
    request: Request,
    approval_id: UUID,
    service: ApprovalService = Depends(get_approval_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[ApprovalResponse]:
    approval = await service.decide(
        approval_id,
        ApprovalDecideRequest(decision=ApprovalStatus.REJECTED.value),
    )
    return ApiResponse(success=True, data=approval, request_id=_rid(request))


@router.post("/{approval_id}/decide", response_model=ApiResponse[ApprovalResponse])
async def decide_approval(
    request: Request,
    approval_id: UUID,
    data: ApprovalDecideRequest,
    service: ApprovalService = Depends(get_approval_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[ApprovalResponse]:
    approval = await service.decide(approval_id, data)
    return ApiResponse(success=True, data=approval, request_id=_rid(request))


@router.post("/request", response_model=ApiResponse[ApprovalResponse], status_code=status.HTTP_201_CREATED)
async def request_approval_body(
    request: Request,
    data: ApprovalRequestBody,
    service: ApprovalService = Depends(get_approval_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[ApprovalResponse]:
    approval = await service.request_approval(data.quotation_id)
    return ApiResponse(success=True, data=approval, request_id=_rid(request))


@router.post("/request/{quotation_id}", response_model=ApiResponse[ApprovalResponse])
async def request_approval(
    request: Request,
    quotation_id: UUID,
    service: ApprovalService = Depends(get_approval_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[ApprovalResponse]:
    approval = await service.request_approval(quotation_id)
    return ApiResponse(success=True, data=approval, request_id=_rid(request))
