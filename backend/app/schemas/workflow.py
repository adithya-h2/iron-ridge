"""Workflow status and timeline schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class WorkflowCustomerSummary(BaseModel):
    customer_id: UUID | None = None
    company_name: str | None = None
    contact_person: str | None = None
    email: str | None = None

    model_config = ConfigDict(from_attributes=True)


class WorkflowRetryState(BaseModel):
    attempt_count: int = 0
    last_attempt: datetime | None = None
    last_error: str | None = None
    retryable: bool = True


class WorkflowStatusResponse(BaseModel):
    deal_id: UUID
    customer: WorkflowCustomerSummary | None = None
    workflow_id: UUID | None = None
    current_agent: str | None = None
    current_status: str | None = None
    progress_percentage: int = 0
    created_at: datetime | None = None
    updated_at: datetime | None = None
    estimated_completion: datetime | None = None
    retry: WorkflowRetryState | None = None


class WorkflowTimelineEvent(BaseModel):
    timestamp: datetime | None = None
    agent: str | None = None
    status: str | None = None
    action: str | None = None
    message: str | None = None


class WorkflowTimelineResponse(BaseModel):
    deal_id: UUID
    events: list[WorkflowTimelineEvent]
    total: int
    page: int
    page_size: int
    pages: int
