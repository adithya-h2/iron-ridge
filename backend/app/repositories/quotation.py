"""Quotation repository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models.quotation import Quotation
from app.repositories.base import BaseRepository


class QuotationRepository(BaseRepository[Quotation]):
    model = Quotation
    pk_column = "quotation_id"

    async def get_with_items(self, quotation_id: UUID) -> Quotation | None:
        result = await self.session.execute(
            select(Quotation)
            .options(selectinload(Quotation.items))
            .where(Quotation.quotation_id == quotation_id)
        )
        return result.scalar_one_or_none()

    async def get_with_items_or_raise(self, quotation_id: UUID) -> Quotation:
        quotation = await self.get_with_items(quotation_id)
        if quotation is None:
            raise NotFoundError(
                "Quotation not found",
                details={"quotation_id": str(quotation_id)},
            )
        return quotation
