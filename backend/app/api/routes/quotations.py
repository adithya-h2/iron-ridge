"""Quotation / pricing routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import Response

from app.api.deps import get_deal_service, get_pricing_service, get_quotation_pdf_service, require_auth
from app.core.config import settings
from app.core.exceptions import ForbiddenError
from app.schemas.auth import UserResponse
from app.schemas.common import ApiResponse
from app.schemas.quotation import QuotationCreate, QuotationResponse
from app.services.deal import DealService
from app.services.pricing import PricingService
from app.services.quotation_pdf import QuotationPdfService

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


@router.get("/{quotation_id}/pdf")
async def get_quotation_pdf(
    quotation_id: UUID,
    pricing_service: PricingService = Depends(get_pricing_service),
    deal_service: DealService = Depends(get_deal_service),
    pdf_service: QuotationPdfService = Depends(get_quotation_pdf_service),
    _: UserResponse = Depends(require_auth),
) -> Response:
    if not settings.feature_pdf_export:
        raise ForbiddenError("PDF export is disabled")
    quotation = await pricing_service.get(quotation_id)
    company_name = None
    if quotation.deal_id:
        company_name = await deal_service.get_company_name(quotation.deal_id)
    pdf_bytes = pdf_service.generate(quotation, company_name)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="quotation-{quotation_id}.pdf"'},
    )


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
