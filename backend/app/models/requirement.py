"""
app/models/requirement.py

SQLAlchemy ORM model for the `requirements` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : requirements
Primary key  : requirement_id (uuid)

Columns (exact match):
    requirement_id        uuid       NOT NULL  PK
    deal_id               uuid       NULL      FK -> deals.deal_id
    vehicle_model         varchar    NULL
    vehicle_type          varchar    NULL
    quantity              int4       NULL
    delivery_start        date       NULL
    delivery_end          date       NULL
    monthly_delivery      int4       NULL
    budget                numeric    NULL
    special_requirements  text       NULL
    created_at            timestamp  NULL
"""

import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Requirement(Base):
    """ORM model for the `requirements` table. Captured by Neil."""

    __tablename__ = "requirements"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    requirement_id: Mapped[uuid.UUID] = mapped_column(
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
    vehicle_model: Mapped[str | None] = mapped_column(String, nullable=True)
    vehicle_type: Mapped[str | None] = mapped_column(String, nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    delivery_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    monthly_delivery: Mapped[int | None] = mapped_column(Integer, nullable=True)
    budget: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    special_requirements: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    deal: Mapped["Deal"] = relationship(  # type: ignore[name-defined]
        "Deal",
        back_populates="requirements",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<Requirement id={self.requirement_id} "
            f"deal={self.deal_id} vehicle={self.vehicle_type!r}>"
        )
