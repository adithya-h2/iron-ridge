"""Deal repository."""

from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import selectinload

from app.core.enums import DealStatus
from app.core.exceptions import NotFoundError
from app.models.customer import Customer
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
        result = await self.session.execute(
            select(Deal)
            .options(selectinload(Deal.customer))
            .where(Deal.deal_id == deal_id)
        )
        return result.scalar_one_or_none()

    async def get_with_customer_or_raise(self, deal_id: UUID) -> Deal:
        deal = await self.get_with_customer(deal_id)
        if deal is None:
            raise NotFoundError("Deal not found", details={"deal_id": str(deal_id)})
        return deal

    async def get_latest_lead_by_company_name(self, company_name: str) -> Deal | None:
        """Find the most recent LEAD deal for a company (n8n deal_id fallback)."""
        result = await self.session.execute(
            select(Deal)
            .join(Customer, Deal.customer_id == Customer.customer_id)
            .where(Deal.status == DealStatus.LEAD.value)
            .where(Customer.company_name.ilike(company_name.strip()))
            .order_by(desc(Deal.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()
