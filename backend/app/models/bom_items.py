"""
app/models/bom_items.py

SQLAlchemy ORM model for the `bom_items` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : bom_items
Primary key  : item_id (uuid)

Columns (exact match):
    item_id         uuid       NOT NULL  PK
    bom_id          uuid       NULL      FK -> bom.bom_id
    component_name  varchar    NULL
    component_type  varchar    NULL
    quantity        int4       NULL
    unit_price      numeric    NULL
    subtotal        numeric    NULL
"""

import uuid
from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class BOMItem(Base):
    """ORM model for the `bom_items` table. Line items within a BOM."""

    __tablename__ = "bom_items"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Columns — exact names and types from deployed schema
    # ------------------------------------------------------------------
    bom_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("bom.bom_id", ondelete="NO ACTION"),
        nullable=True,
    )
    component_name: Mapped[str | None] = mapped_column(String, nullable=True)
    component_type: Mapped[str | None] = mapped_column(String, nullable=True)
    quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    bom: Mapped["BOM"] = relationship(  # type: ignore[name-defined]
        "BOM",
        back_populates="items",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<BOMItem id={self.item_id} "
            f"component={self.component_name!r} qty={self.quantity}>"
        )
