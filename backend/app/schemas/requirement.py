"""Requirement Pydantic schemas."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RequirementCreate(BaseModel):
    deal_id: UUID | None = None
    vehicle_model: str | None = None
    vehicle_type: str | None = None
    quantity: int | None = None
    delivery_start: date | None = None
    delivery_end: date | None = None
    monthly_delivery: int | None = None
    budget: Decimal | None = None
    special_requirements: str | None = None


class RequirementUpdate(BaseModel):
    vehicle_model: str | None = None
    vehicle_type: str | None = None
    quantity: int | None = None
    delivery_start: date | None = None
    delivery_end: date | None = None
    monthly_delivery: int | None = None
    budget: Decimal | None = None
    special_requirements: str | None = None


class RequirementResponse(BaseModel):
    requirement_id: UUID
    deal_id: UUID | None = None
    vehicle_model: str | None = None
    vehicle_type: str | None = None
    quantity: int | None = None
    delivery_start: date | None = None
    delivery_end: date | None = None
    monthly_delivery: int | None = None
    budget: Decimal | None = None
    special_requirements: str | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
