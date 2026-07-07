"""Customer routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.deps import get_customer_service, require_auth
from app.schemas.auth import UserResponse
from app.schemas.common import ApiResponse, PaginatedResponse, PaginationParams
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.services.customer import CustomerService

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


@router.post("", response_model=ApiResponse[CustomerResponse], status_code=status.HTTP_201_CREATED)
async def create_customer(
    request: Request,
    data: CustomerCreate,
    service: CustomerService = Depends(get_customer_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[CustomerResponse]:
    customer = await service.create(data)
    return ApiResponse(success=True, data=customer, request_id=_rid(request))


@router.get("", response_model=ApiResponse[PaginatedResponse[CustomerResponse]])
async def list_customers(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    service: CustomerService = Depends(get_customer_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[PaginatedResponse[CustomerResponse]]:
    pagination = PaginationParams(page=page, page_size=page_size)
    result = await service.search(search, pagination) if search else await service.list(pagination)
    return ApiResponse(success=True, data=result, request_id=_rid(request))


@router.get("/{customer_id}", response_model=ApiResponse[CustomerResponse])
async def get_customer(
    request: Request,
    customer_id: UUID,
    service: CustomerService = Depends(get_customer_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[CustomerResponse]:
    customer = await service.get(customer_id)
    return ApiResponse(success=True, data=customer, request_id=_rid(request))


@router.patch("/{customer_id}", response_model=ApiResponse[CustomerResponse])
async def update_customer(
    request: Request,
    customer_id: UUID,
    data: CustomerUpdate,
    service: CustomerService = Depends(get_customer_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[CustomerResponse]:
    customer = await service.update(customer_id, data)
    return ApiResponse(success=True, data=customer, request_id=_rid(request))


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID,
    service: CustomerService = Depends(get_customer_service),
    _: UserResponse = Depends(require_auth),
) -> None:
    await service.delete(customer_id)
