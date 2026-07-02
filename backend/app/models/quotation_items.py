"""
app/models/quotation_items.py

SQLAlchemy ORM model for the `quotation_items` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : quotation_items
Primary key  : quotation_item_id (uuid)

Columns (exact match):
    quotation_item_id  uuid       NOT NULL  PK
    quotation_id       uuid       NULL      FK -> quotations.quotation_id
    component_name     varchar    NULL
    quantity           int4       NULL
    unit_price         numeric    NULL
    discount           numeric    NULL
    total              numeric    NULL
"""

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class QuotationItem(Base):
    """ORM model for the `quotation_items` table. Line items within a quotation."""

    __tablename__ = "quotation_items"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    quotation_item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Columns — exact names and types from deployed schema
    # ------------------------------------------------------------------
    quotation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quotations.quotation_id", ondelete="NO ACTION"),
        nullable=True,
    )
    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    discount: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    total: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    quotation: Mapped["Quotation"] = relationship(  # type: ignore[name-defined]
        "Quotation",
        back_populates="items",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<QuotationItem id={self.quotation_item_id} "
            f"component={self.component_name!r} qty={self.quantity} total={self.total}>"
        )
