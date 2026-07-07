"""Order routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from app.api.deps import get_order_service, require_auth
from app.schemas.auth import UserResponse
from app.schemas.common import ApiResponse
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.services.order import OrderService

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


@router.post("", response_model=ApiResponse[OrderResponse], status_code=status.HTTP_201_CREATED)
async def create_order(
    request: Request,
    data: OrderCreate,
    service: OrderService = Depends(get_order_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[OrderResponse]:
    order = await service.create(data)
    return ApiResponse(success=True, data=order, request_id=_rid(request))


@router.get("/{order_id}", response_model=ApiResponse[OrderResponse])
async def get_order(
    request: Request,
    order_id: UUID,
    service: OrderService = Depends(get_order_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[OrderResponse]:
    order = await service.get(order_id)
    return ApiResponse(success=True, data=order, request_id=_rid(request))


@router.patch("/{order_id}", response_model=ApiResponse[OrderResponse])
async def update_order(
    request: Request,
    order_id: UUID,
    data: OrderUpdate,
    service: OrderService = Depends(get_order_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[OrderResponse]:
    order = await service.update(order_id, data)
    return ApiResponse(success=True, data=order, request_id=_rid(request))
