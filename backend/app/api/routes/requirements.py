"""Requirement routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from app.api.deps import get_requirement_service, require_auth
from app.schemas.auth import UserResponse
from app.schemas.common import ApiResponse
from app.schemas.requirement import RequirementCreate, RequirementResponse, RequirementUpdate
from app.services.requirement import RequirementService

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


@router.post("", response_model=ApiResponse[RequirementResponse], status_code=status.HTTP_201_CREATED)
async def create_requirement(
    request: Request,
    data: RequirementCreate,
    service: RequirementService = Depends(get_requirement_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[RequirementResponse]:
    req = await service.create(data)
    return ApiResponse(success=True, data=req, request_id=_rid(request))


@router.get("/deal/{deal_id}", response_model=ApiResponse[list[RequirementResponse]])
async def list_by_deal(
    request: Request,
    deal_id: UUID,
    service: RequirementService = Depends(get_requirement_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[list[RequirementResponse]]:
    items = await service.list_by_deal(deal_id)
    return ApiResponse(success=True, data=items, request_id=_rid(request))


@router.patch("/{requirement_id}", response_model=ApiResponse[RequirementResponse])
async def update_requirement(
    request: Request,
    requirement_id: UUID,
    data: RequirementUpdate,
    service: RequirementService = Depends(get_requirement_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[RequirementResponse]:
    req = await service.update(requirement_id, data)
    return ApiResponse(success=True, data=req, request_id=_rid(request))
