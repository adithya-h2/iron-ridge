"""Consultation request Pydantic schemas."""

import re
import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ConsultationRequestCreate(BaseModel):
    organization_name: str = Field(..., min_length=1)
    organization_type: str = Field(..., min_length=1)
    department: str | None = None
    website: str | None = None
    contact_person: str = Field(..., min_length=1)
    job_title: str | None = None
    business_email: EmailStr
    phone_number: str = Field(..., min_length=1)
    preferred_contact_method: str | None = None
    country: str = Field(..., min_length=1)
    state: str = Field(..., min_length=1)
    city: str = Field(..., min_length=1)
    vehicle_category: str = Field(..., min_length=1)
    estimated_quantity: str = Field(..., min_length=1)
    purchase_timeline: str = Field(..., min_length=1)
    requirement_summary: str | None = Field(None, max_length=500)
    consent: bool = Field(...)

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        # Standard phone number regex matching the frontend pattern
        phone_regex = re.compile(r"^[\+]?[(]?[0-9]{3}[)]?[-\s\.]?[0-9]{3}[-\s\.]?[0-9]{4,6}$")
        if not phone_regex.match(v.strip()):
            raise ValueError("Enter a valid phone number")
        return v.strip()

    @field_validator("consent")
    @classmethod
    def validate_consent(cls, v: bool) -> bool:
        if v is not True:
            raise ValueError("You must agree to the consent policy to proceed")
        return v


class ConsultationRequestResponse(BaseModel):
    id: uuid.UUID
    organization_name: str
    organization_type: str
    department: str | None = None
    website: str | None = None
    contact_person: str
    job_title: str | None = None
    business_email: str
    phone_number: str
    preferred_contact_method: str | None = None
    country: str
    state: str
    city: str
    vehicle_category: str
    estimated_quantity: str
    purchase_timeline: str
    requirement_summary: str | None = None
    consent: bool
    status: str
    lead_score: int | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConsultationCreateSuccessResponse(BaseModel):
    status: str = "success"
    consultation_id: uuid.UUID
    message: str = "Consultation request submitted successfully."
