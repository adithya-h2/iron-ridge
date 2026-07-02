"""
app/models/lead_validation.py

SQLAlchemy ORM model for the `lead_validation` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : lead_validation   (NOT lead_validations — deployed name preserved)
Primary key  : validation_id (uuid)

Columns (exact match):
    validation_id       uuid        NOT NULL  PK
    deal_id             uuid        NULL      FK -> deals.deal_id
    website_verified    bool        NULL
    phone_verified      bool        NULL
    email_verified      bool        NULL
    linkedin_verified   bool        NULL
    company_verified    bool        NULL
    hospital_beds       int4        NULL
    annual_revenue      numeric     NULL
    employee_count      int4        NULL
    confidence_score    numeric     NULL
    lead_score          int4        NULL
    validation_summary  text        NULL
    validated_at        timestamp   NULL
"""

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, Text
from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class LeadValidation(Base):
    """ORM model for the `lead_validation` table. Owned by Lisa."""

    __tablename__ = "lead_validation"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    validation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Columns — exact names and types from deployed schema
    # ------------------------------------------------------------------
    deal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("deals.deal_id", ondelete="NO ACTION"),
        nullable=True,
    )
    website_verified: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    phone_verified: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    email_verified: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    linkedin_verified: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    company_verified: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    hospital_beds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    annual_revenue: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    confidence_score: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    lead_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    validation_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    validated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    deal: Mapped["Deal"] = relationship(  # type: ignore[name-defined]
        "Deal",
        back_populates="lead_validations",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<LeadValidation id={self.validation_id} "
            f"deal={self.deal_id} score={self.lead_score}>"
        )
