"""
app/models/price_master.py

SQLAlchemy ORM model for the `price_master` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : price_master
Primary key  : price_id (uuid)

Columns (exact match):
    price_id        uuid       NOT NULL  PK
    component_name  varchar    NULL
    component_type  varchar    NULL
    unit_price      numeric    NULL
    currency        varchar    NULL
    effective_date  date       NULL
"""

import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class PriceMaster(Base):
    """ORM model for the `price_master` table. Component pricing reference data."""

    __tablename__ = "price_master"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    price_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Columns — exact names and types from deployed schema
    # ------------------------------------------------------------------
    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
    component_type: Mapped[str | None] = mapped_column(String, nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    currency: Mapped[str | None] = mapped_column(String, nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<PriceMaster id={self.price_id} "
            f"component={self.component_name!r} price={self.unit_price}>"
        )
