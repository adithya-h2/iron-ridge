"""Centralized audit logging service."""

from datetime import datetime, timezone
from uuid import UUID

from app.repositories.audit_log import AuditLogRepository
from app.schemas.audit import AuditLogResponse
from app.schemas.common import PaginatedResponse, PaginationParams


class AuditService:
    def __init__(self, audit_repo: AuditLogRepository) -> None:
        self.audit_repo = audit_repo

    async def log_action(
        self,
        deal_id: UUID | None,
        agent_name: str | None,
        action: str,
        previous_status: str | None = None,
        new_status: str | None = None,
        reason: str | None = None,
    ) -> AuditLogResponse:
        log = await self.audit_repo.create_log(
            deal_id=deal_id,
            agent_name=agent_name,
            action=action,
            previous_status=previous_status,
            new_status=new_status,
            reason=reason,
            created_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        return AuditLogResponse.model_validate(log)

    async def log_status_change(
        self,
        deal_id: UUID,
        agent_name: str | None,
        previous_status: str | None,
        new_status: str,
        reason: str | None = None,
    ) -> AuditLogResponse:
        return await self.log_action(
            deal_id=deal_id,
            agent_name=agent_name,
            action="status_changed",
            previous_status=previous_status,
            new_status=new_status,
            reason=reason,
        )

    async def get_by_deal(
        self, deal_id: UUID, pagination: PaginationParams | None = None
    ) -> PaginatedResponse:
        result = await self.audit_repo.get_by_deal(deal_id, pagination)
        return PaginatedResponse(
            items=[AuditLogResponse.model_validate(i) for i in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            pages=result.pages,
        )
