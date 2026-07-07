"""Deal Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DealCreate(BaseModel):
    customer_id: UUID | None = None
    status: str | None = None
    priority: str | None = None
    current_agent: str | None = None
    lead_score: int | None = None
    approval_status: str | None = None


class DealUpdate(BaseModel):
    customer_id: UUID | None = None
    status: str | None = None
    priority: str | None = None
    current_agent: str | None = None
    lead_score: int | None = None
    approval_status: str | None = None


class DealTransitionRequest(BaseModel):
    new_status: str
    agent_name: str | None = None
    reason: str | None = None


class DealResponse(BaseModel):
    deal_id: UUID
    customer_id: UUID | None = None
    status: str | None = None
    priority: str | None = None
    current_agent: str | None = None
    lead_score: int | None = None
    approval_status: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class DealListResponse(BaseModel):
    items: list[DealResponse]
    total: int
    page: int
    page_size: int
    pages: int
