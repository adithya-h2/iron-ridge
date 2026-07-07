"""Approval Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ApprovalCreate(BaseModel):
    quotation_id: UUID | None = None
    approved_by: str | None = None
    decision: str | None = None
    remarks: str | None = None


class ApprovalDecideRequest(BaseModel):
    decision: str
    approved_by: str | None = "Victor"
    remarks: str | None = None


class ApprovalResponse(BaseModel):
    approval_id: UUID
    quotation_id: UUID | None = None
    approved_by: str | None = None
    decision: str | None = None
    remarks: str | None = None
    approved_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
