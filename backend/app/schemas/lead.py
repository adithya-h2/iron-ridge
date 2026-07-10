"""Lead intake Pydantic schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.core.enums import LeadSource


class LeadIntakeRequest(BaseModel):
    """Universal lead intake request — all entry channels normalize to this."""

    source: LeadSource
    submission_channel: str = Field(..., min_length=1, max_length=50)
    org_name: str | None = None
    company_name: str | None = None
    contact_person: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    website: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    industry: str | None = None
    vehicle_type: str | None = None
    required_quantity: int | str | None = None
    notes: str | None = None

    model_config = ConfigDict(extra="allow")

    @field_validator("source", mode="before")
    @classmethod
    def normalize_source(cls, v: str | LeadSource) -> LeadSource:
        if isinstance(v, LeadSource):
            return v
        return LeadSource(str(v).upper())


class NormalizedLead(BaseModel):
    """Validated and normalized lead data for persistence."""

    source: LeadSource
    submission_channel: str
    company_name: str
    contact_person: str | None = None
    email: str | None = None
    phone: str | None = None
    website: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    industry: str | None = None
    vehicle_type: str | None = None
    required_quantity: int | None = None
    notes: str | None = None


class LeadIntakeResponse(BaseModel):
    deal_id: UUID
    customer_id: UUID
    workflow_id: UUID
    lead_source: str
    submission_channel: str
    status: str
    is_duplicate: bool = False
    matched_customer_id: UUID | None = None
    lead_score: int | None = None
    company_name: str | None = None

    model_config = ConfigDict(from_attributes=True)


class LeadCreationResult(BaseModel):
    """Internal result from LeadCreationRepository."""

    customer_id: UUID
    deal_id: UUID
    workflow_id: UUID
    lead_source: str
    submission_channel: str
    status: str

    model_config = ConfigDict(from_attributes=True)
