"""Order Pydantic schemas."""

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OrderCreate(BaseModel):
    deal_id: UUID | None = None
    quotation_id: UUID | None = None
    erp_reference: str | None = None
    order_status: str | None = None
    production_start: date | None = None
    production_end: date | None = None


class OrderUpdate(BaseModel):
    erp_reference: str | None = None
    order_status: str | None = None
    production_start: date | None = None
    production_end: date | None = None


class OrderResponse(BaseModel):
    order_id: UUID
    deal_id: UUID | None = None
    quotation_id: UUID | None = None
    erp_reference: str | None = None
    order_status: str | None = None
    production_start: date | None = None
    production_end: date | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
