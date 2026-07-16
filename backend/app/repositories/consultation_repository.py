"""Consultation repository."""

from typing import Any
from uuid import UUID

from app.models.consultation import Consultation
from app.repositories.base import BaseRepository, PaginatedResult
from app.schemas.common import PaginationParams


class ConsultationRepository(BaseRepository[Consultation]):
    model = Consultation
    pk_column = "id"

    async def list(
        self,
        pagination: PaginationParams | None = None,
        filters: dict[str, Any] | None = None,
    ) -> PaginatedResult[Consultation]:
        """List and paginate consultation requests."""
        return await self.get_all(pagination=pagination, filters=filters)

    async def update_status(self, consultation_id: UUID, status: str) -> Consultation:
        """Update the validation status of a consultation request."""
        return await self.update(consultation_id, status=status)

    async def update_score(self, consultation_id: UUID, lead_score: int) -> Consultation:
        """Update the lead score of a consultation request."""
        return await self.update(consultation_id, lead_score=lead_score)
