"""
app/models/discount_master.py

SQLAlchemy ORM model for the `discount_master` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : discount_master
Primary key  : discount_id (uuid)

Columns (exact match):
    discount_id          uuid       NOT NULL  PK
    minimum_quantity     int4       NULL
    maximum_quantity     int4       NULL
    discount_percentage  numeric    NULL
    approval_required    bool       NULL
"""

import uuid
from decimal import Decimal

from sqlalchemy import Boolean, Integer, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class DiscountMaster(Base):
    """ORM model for the `discount_master` table. Discount rules reference data."""

    __tablename__ = "discount_master"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    discount_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Columns — exact names and types from deployed schema
    # ------------------------------------------------------------------
    minimum_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    maximum_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    discount_percentage: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    approval_required: Mapped[bool | None] = mapped_column(Boolean, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<DiscountMaster id={self.discount_id} "
            f"pct={self.discount_percentage} approval={self.approval_required}>"
        )
