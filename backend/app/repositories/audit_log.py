"""Audit log repository — append-only."""

from typing import Any
from uuid import UUID

from sqlalchemy import asc, func, select

from app.models.audit_log import AuditLog
from app.repositories.base import BaseRepository, PaginatedResult
from app.schemas.common import PaginationParams


class AuditLogRepository(BaseRepository[AuditLog]):
    model = AuditLog
    pk_column = "audit_id"

    async def create_log(self, **kwargs: Any) -> AuditLog:
        return await self.create(**kwargs)

    async def delete(self, entity_id: Any) -> None:
        raise NotImplementedError("Audit logs are append-only")

    async def update(self, entity_id: Any, **kwargs: Any) -> AuditLog:
        raise NotImplementedError("Audit logs are append-only")

    async def get_by_deal(
        self, deal_id: UUID, pagination: PaginationParams | None = None
    ) -> PaginatedResult[AuditLog]:
        return await self.get_all(pagination, filters={"deal_id": deal_id})

    async def get_by_deal_ordered(
        self, deal_id: UUID, pagination: PaginationParams | None = None
    ) -> PaginatedResult[AuditLog]:
        pagination = pagination or PaginationParams()
        query = (
            select(AuditLog)
            .where(AuditLog.deal_id == deal_id)
            .order_by(asc(AuditLog.created_at))
        )
        count_query = select(func.count()).select_from(
            select(AuditLog).where(AuditLog.deal_id == deal_id).subquery()
        )
        total = (await self.session.execute(count_query)).scalar_one()
        offset = (pagination.page - 1) * pagination.page_size
        result = await self.session.execute(query.offset(offset).limit(pagination.page_size))
        items = list(result.scalars().all())
        pages = max(1, (total + pagination.page_size - 1) // pagination.page_size)
        return PaginatedResult(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            pages=pages,
        )

    async def get_median_completion_hours(self) -> float | None:
        """Median hours from first to last audit for deals that reached DELIVERED."""
        from app.core.enums import DealStatus

        subq = (
            select(
                AuditLog.deal_id,
                func.min(AuditLog.created_at).label("started"),
                func.max(AuditLog.created_at).label("ended"),
            )
            .where(AuditLog.new_status == DealStatus.DELIVERED.value)
            .group_by(AuditLog.deal_id)
            .subquery()
        )
        result = await self.session.execute(
            select(
                func.percentile_cont(0.5).within_group(
                    func.extract("epoch", subq.c.ended - subq.c.started) / 3600.0
                )
            )
        )
        value = result.scalar_one_or_none()
        return float(value) if value is not None else None
