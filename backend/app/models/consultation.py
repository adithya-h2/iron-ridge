"""
app/models/consultation.py

SQLAlchemy ORM model for the `consultation_requests` table.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Consultation(Base):
    """ORM model for the `consultation_requests` table."""

    __tablename__ = "consultation_requests"

    # Primary Key
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Organization Information
    organization_name: Mapped[str] = mapped_column(String, nullable=False)
    organization_type: Mapped[str] = mapped_column(String, nullable=False)
    department: Mapped[str | None] = mapped_column(String, nullable=True)
    website: Mapped[str | None] = mapped_column(String, nullable=True)

    # Contact Information
    contact_person: Mapped[str] = mapped_column(String, nullable=False)
    job_title: Mapped[str | None] = mapped_column(String, nullable=True)
    business_email: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    preferred_contact_method: Mapped[str | None] = mapped_column(String, nullable=True)

    # Location
    country: Mapped[str] = mapped_column(String, nullable=False)
    state: Mapped[str] = mapped_column(String, nullable=False)
    city: Mapped[str] = mapped_column(String, nullable=False)

    # Purchase Interest
    vehicle_category: Mapped[str] = mapped_column(String, nullable=False)
    estimated_quantity: Mapped[str] = mapped_column(String, nullable=False)
    purchase_timeline: Mapped[str] = mapped_column(String, nullable=False)
    requirement_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Consent
    consent: Mapped[bool] = mapped_column(Boolean, nullable=False)

    # Workflow / Output Status
    status: Mapped[str] = mapped_column(String, default="PENDING_VALIDATION", nullable=False)
    lead_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<Consultation id={self.id} org={self.organization_name!r} status={self.status!r}>"
