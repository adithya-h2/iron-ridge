"""Consultation routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status

from app.api.deps import get_consultation_service, require_auth
from app.core.exceptions import NotFoundError
from app.schemas.auth import UserResponse
from app.schemas.common import ApiResponse, PaginatedResponse, PaginationParams
from app.schemas.consultation import (
    ConsultationRequestCreate,
    ConsultationRequestResponse,
    ConsultationCreateSuccessResponse,
)
from app.services.consultation_service import ConsultationService

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


@router.post(
    "",
    response_model=ConsultationCreateSuccessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new consultation request",
    description="Create a new consultation request submitted from the Iron Ridge website.",
)
async def create_consultation(
    request: Request,
    data: ConsultationRequestCreate,
    service: ConsultationService = Depends(get_consultation_service),
) -> ConsultationCreateSuccessResponse:
    """Create a new consultation request and trigger n8n validation workflow."""
    return await service.create_consultation(data)


@router.get(
    "/{consultation_id}",
    response_model=ApiResponse[ConsultationRequestResponse],
    summary="Retrieve a consultation request",
    description="Get details of a specific consultation request by ID.",
)
async def get_consultation(
    request: Request,
    consultation_id: UUID,
    service: ConsultationService = Depends(get_consultation_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[ConsultationRequestResponse]:
    """Get a consultation request by UUID."""
    consultation = await service.get_consultation(consultation_id)
    if not consultation:
        raise NotFoundError(
            "Consultation request not found",
            details={"id": str(consultation_id)},
        )
    return ApiResponse(
        success=True,
        data=ConsultationRequestResponse.model_validate(consultation),
        request_id=_rid(request),
    )


@router.get(
    "",
    response_model=ApiResponse[PaginatedResponse[ConsultationRequestResponse]],
    summary="List consultation requests",
    description="List and paginate all consultation requests.",
)
async def list_consultations(
    request: Request,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: ConsultationService = Depends(get_consultation_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[PaginatedResponse[ConsultationRequestResponse]]:
    """List and paginate consultation requests."""
    pagination = PaginationParams(page=page, page_size=page_size)
    paginated_result = await service.list_consultations(pagination)
    
    # Adapt PaginatedResult to PaginatedResponse
    items_response = [
        ConsultationRequestResponse.model_validate(item)
        for item in paginated_result.items
    ]
    
    response_data = PaginatedResponse(
        items=items_response,
        total=paginated_result.total,
        page=paginated_result.page,
        page_size=paginated_result.page_size,
        pages=paginated_result.pages,
    )
    
    return ApiResponse(
        success=True,
        data=response_data,
        request_id=_rid(request),
    )
