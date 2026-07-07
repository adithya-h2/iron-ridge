"""Requirement routes."""

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require_auth
from app.database.session import get_db_session
from app.repositories.requirement import RequirementRepository
from app.schemas.auth import UserResponse
from app.schemas.common import ApiResponse
from app.schemas.requirement import RequirementCreate, RequirementResponse, RequirementUpdate

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


@router.post("", response_model=ApiResponse[RequirementResponse], status_code=status.HTTP_201_CREATED)
async def create_requirement(
    request: Request,
    data: RequirementCreate,
    db: AsyncSession = Depends(get_db_session),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[RequirementResponse]:
    from datetime import datetime, timezone

    repo = RequirementRepository(db)
    req = await repo.create(**data.model_dump(exclude_unset=True), created_at=datetime.now(timezone.utc).replace(tzinfo=None))
    return ApiResponse(success=True, data=RequirementResponse.model_validate(req), request_id=_rid(request))


@router.get("/deal/{deal_id}", response_model=ApiResponse[list[RequirementResponse]])
async def list_by_deal(
    request: Request,
    deal_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[list[RequirementResponse]]:
    repo = RequirementRepository(db)
    items = await repo.filter_by(deal_id=deal_id)
    return ApiResponse(success=True, data=[RequirementResponse.model_validate(i) for i in items], request_id=_rid(request))


@router.patch("/{requirement_id}", response_model=ApiResponse[RequirementResponse])
async def update_requirement(
    request: Request,
    requirement_id: UUID,
    data: RequirementUpdate,
    db: AsyncSession = Depends(get_db_session),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[RequirementResponse]:
    repo = RequirementRepository(db)
    req = await repo.update(requirement_id, **data.model_dump(exclude_unset=True))
    return ApiResponse(success=True, data=RequirementResponse.model_validate(req), request_id=_rid(request))
