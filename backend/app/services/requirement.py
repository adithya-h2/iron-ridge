"""Requirement business service."""

from datetime import datetime, timezone
from uuid import UUID

from app.repositories.requirement import RequirementRepository
from app.schemas.requirement import RequirementCreate, RequirementResponse, RequirementUpdate


class RequirementService:
    def __init__(self, requirement_repo: RequirementRepository) -> None:
        self.requirement_repo = requirement_repo

    async def create(self, data: RequirementCreate) -> RequirementResponse:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        req = await self.requirement_repo.create(
            **data.model_dump(exclude_unset=True),
            created_at=now,
        )
        return RequirementResponse.model_validate(req)

    async def list_by_deal(self, deal_id: UUID) -> list[RequirementResponse]:
        items = await self.requirement_repo.filter_by(deal_id=deal_id)
        return [RequirementResponse.model_validate(i) for i in items]

    async def update(self, requirement_id: UUID, data: RequirementUpdate) -> RequirementResponse:
        req = await self.requirement_repo.update(
            requirement_id,
            **data.model_dump(exclude_unset=True),
        )
        return RequirementResponse.model_validate(req)
