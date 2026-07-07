"""Customer Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CustomerCreate(BaseModel):
    company_name: str | None = None
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    industry: str | None = None
    ownership_type: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None


class CustomerUpdate(BaseModel):
    company_name: str | None = None
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    industry: str | None = None
    ownership_type: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None


class CustomerResponse(BaseModel):
    customer_id: UUID
    company_name: str | None = None
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    industry: str | None = None
    ownership_type: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    total: int
    page: int
    page_size: int
    pages: int
