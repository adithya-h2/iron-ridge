"""Quotation Pydantic schemas."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class QuotationItemCreate(BaseModel):
    component_name: str | None = None
    quantity: int | None = None
    unit_price: Decimal | None = None
    discount: Decimal | None = None
    total: Decimal | None = None


class QuotationItemResponse(BaseModel):
    quotation_item_id: UUID
    quotation_id: UUID | None = None
    component_name: str | None = None
    quantity: int | None = None
    unit_price: Decimal | None = None
    discount: Decimal | None = None
    total: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)


class QuotationCreate(BaseModel):
    deal_id: UUID | None = None
    quotation_version: str | None = None
    subtotal: Decimal | None = None
    discount: Decimal | None = None
    tax: Decimal | None = None
    grand_total: Decimal | None = None
    quotation_status: str | None = None
    items: list[QuotationItemCreate] = []


class QuotationUpdate(BaseModel):
    quotation_version: str | None = None
    subtotal: Decimal | None = None
    discount: Decimal | None = None
    tax: Decimal | None = None
    grand_total: Decimal | None = None
    quotation_status: str | None = None


class QuotationResponse(BaseModel):
    quotation_id: UUID
    deal_id: UUID | None = None
    quotation_version: str | None = None
    subtotal: Decimal | None = None
    discount: Decimal | None = None
    tax: Decimal | None = None
    grand_total: Decimal | None = None
    quotation_status: str | None = None
    created_at: datetime | None = None
    items: list[QuotationItemResponse] = []

    model_config = ConfigDict(from_attributes=True)
