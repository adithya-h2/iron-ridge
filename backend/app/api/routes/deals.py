"""Deal routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.deps import get_deal_service, require_auth
from app.schemas.auth import UserResponse
from app.schemas.common import ApiResponse, PaginatedResponse, PaginationParams
from app.schemas.deal import DealCreate, DealResponse, DealTransitionRequest, DealUpdate
from app.services.deal import DealService

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


@router.post("", response_model=ApiResponse[DealResponse], status_code=status.HTTP_201_CREATED)
async def create_deal(
    request: Request,
    data: DealCreate,
    service: DealService = Depends(get_deal_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[DealResponse]:
    deal = await service.create(data)
    return ApiResponse(success=True, data=deal, request_id=_rid(request))


@router.get("", response_model=ApiResponse[PaginatedResponse[DealResponse]])
async def list_deals(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = None,
    service: DealService = Depends(get_deal_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[PaginatedResponse[DealResponse]]:
    pagination = PaginationParams(page=page, page_size=page_size)
    result = await service.list(pagination, status=status)
    return ApiResponse(success=True, data=result, request_id=_rid(request))


@router.get("/{deal_id}", response_model=ApiResponse[DealResponse])
async def get_deal(
    request: Request,
    deal_id: UUID,
    service: DealService = Depends(get_deal_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[DealResponse]:
    deal = await service.get(deal_id)
    return ApiResponse(success=True, data=deal, request_id=_rid(request))


@router.patch("/{deal_id}", response_model=ApiResponse[DealResponse])
async def update_deal(
    request: Request,
    deal_id: UUID,
    data: DealUpdate,
    service: DealService = Depends(get_deal_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[DealResponse]:
    deal = await service.update(deal_id, data)
    return ApiResponse(success=True, data=deal, request_id=_rid(request))


@router.post("/{deal_id}/transition", response_model=ApiResponse[DealResponse])
async def transition_deal(
    request: Request,
    deal_id: UUID,
    data: DealTransitionRequest,
    service: DealService = Depends(get_deal_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[DealResponse]:
    deal = await service.transition(deal_id, data)
    return ApiResponse(success=True, data=deal, request_id=_rid(request))


@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deal(
    deal_id: UUID,
    service: DealService = Depends(get_deal_service),
    _: UserResponse = Depends(require_auth),
) -> None:
    await service.delete(deal_id)
