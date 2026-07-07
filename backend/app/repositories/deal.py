"""Deal repository."""

from uuid import UUID

from sqlalchemy import select

from app.models.deal import Deal
from app.repositories.base import BaseRepository, PaginatedResult
from app.schemas.common import PaginationParams


class DealRepository(BaseRepository[Deal]):
    model = Deal
    pk_column = "deal_id"

    async def get_by_status(
        self, status: str, pagination: PaginationParams | None = None
    ) -> PaginatedResult[Deal]:
        return await self.get_all(pagination, filters={"status": status})

    async def get_by_customer(self, customer_id: UUID) -> list[Deal]:
        return await self.filter_by(customer_id=customer_id)

    async def get_with_customer(self, deal_id: UUID) -> Deal | None:
        result = await self.session.execute(select(Deal).where(Deal.deal_id == deal_id))
        return result.scalar_one_or_none()
