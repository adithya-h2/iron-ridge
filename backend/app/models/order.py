"""
app/models/order.py

SQLAlchemy ORM model for the `orders` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : orders
Primary key  : order_id (uuid)

Columns (exact match):
    order_id          uuid       NOT NULL  PK
    deal_id           uuid       NULL      FK -> deals.deal_id
    quotation_id      uuid       NULL      FK -> quotations.quotation_id
    erp_reference     varchar    NULL
    order_status      varchar    NULL
    production_start  date       NULL
    production_end    date       NULL
    created_at        timestamp  NULL

Foreign keys TO this table:
    delivery_plan.order_id -> orders.order_id
"""

import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Order(Base):
    """ORM model for the `orders` table. Managed by Sally."""

    __tablename__ = "orders"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    order_id: Mapped[uuid.UUID] = mapped_column(
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
    quotation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("quotations.quotation_id", ondelete="NO ACTION"),
        nullable=True,
    )
    erp_reference: Mapped[str | None] = mapped_column(String, nullable=True)
    order_status: Mapped[str | None] = mapped_column(String, nullable=True)
    production_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    production_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    deal: Mapped["Deal"] = relationship(  # type: ignore[name-defined]
        "Deal",
        back_populates="orders",
        lazy="select",
    )
    quotation: Mapped["Quotation"] = relationship(  # type: ignore[name-defined]
        "Quotation",
        back_populates="orders",
        lazy="select",
    )
    delivery_plans: Mapped[list["DeliveryPlan"]] = relationship(  # type: ignore[name-defined]
        "DeliveryPlan",
        back_populates="order",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<Order id={self.order_id} "
            f"status={self.order_status!r} erp={self.erp_reference!r}>"
        )
