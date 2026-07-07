"""Shared Pydantic schemas and API response envelope."""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str | None = None
    sort_order: str = Field(default="asc", pattern="^(asc|desc)$")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    error: ErrorDetail | None = None
    request_id: str | None = None


class WorkflowEventResponse(BaseModel):
    """DTO returned by agent endpoints for n8n orchestration."""

    deal_id: str | None = None
    status: str | None = None
    current_agent: str | None = None
    lead_score: int | None = None
    qualified: bool | None = None
    quotation_id: str | None = None
    quotation_generated: str | None = None
    order_id: str | None = None
    approval_status: str | None = None
    requirements: str | None = None
    reason: str | None = None
    org_name: str | None = None

    model_config = ConfigDict(extra="allow")
