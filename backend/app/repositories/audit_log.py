"""Audit log repository — append-only."""

from typing import Any
from uuid import UUID

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
