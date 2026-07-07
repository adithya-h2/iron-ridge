"""Quotation / pricing routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status

from app.api.deps import get_pricing_service, require_auth
from app.schemas.auth import UserResponse
from app.schemas.common import ApiResponse
from app.schemas.quotation import QuotationCreate, QuotationResponse
from app.services.pricing import PricingService

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


@router.post("", response_model=ApiResponse[QuotationResponse], status_code=status.HTTP_201_CREATED)
async def create_quotation(
    request: Request,
    data: QuotationCreate,
    service: PricingService = Depends(get_pricing_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[QuotationResponse]:
    quotation = await service.create(data)
    return ApiResponse(success=True, data=quotation, request_id=_rid(request))


@router.get("/{quotation_id}", response_model=ApiResponse[QuotationResponse])
async def get_quotation(
    request: Request,
    quotation_id: UUID,
    service: PricingService = Depends(get_pricing_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[QuotationResponse]:
    quotation = await service.get(quotation_id)
    return ApiResponse(success=True, data=quotation, request_id=_rid(request))


@router.post("/generate/{deal_id}", response_model=ApiResponse[QuotationResponse])
async def generate_quotation(
    request: Request,
    deal_id: UUID,
    vehicle_type: str = "Ambulance",
    quantity: int = 1,
    service: PricingService = Depends(get_pricing_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[QuotationResponse]:
    quotation = await service.generate_quotation(deal_id, vehicle_type, quantity)
    return ApiResponse(success=True, data=quotation, request_id=_rid(request))
