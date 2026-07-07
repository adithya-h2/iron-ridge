"""Audit log Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AuditLogResponse(BaseModel):
    audit_id: UUID
    deal_id: UUID | None = None
    agent_name: str | None = None
    action: str | None = None
    previous_status: str | None = None
    new_status: str | None = None
    reason: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    pages: int
