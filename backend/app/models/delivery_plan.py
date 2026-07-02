"""
app/models/delivery_plan.py

SQLAlchemy ORM model for the `delivery_plan` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : delivery_plan
Primary key  : delivery_id (uuid)

Columns (exact match):
    delivery_id       uuid       NOT NULL  PK
    order_id          uuid       NULL      FK -> orders.order_id
    delivery_month    varchar    NULL
    planned_quantity  int4       NULL
    planned_date      date       NULL
    delivery_status   varchar    NULL
"""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class DeliveryPlan(Base):
    """ORM model for the `delivery_plan` table. Managed by Adam."""

    __tablename__ = "delivery_plan"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    delivery_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Columns — exact names and types from deployed schema
    # ------------------------------------------------------------------
    order_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.order_id", ondelete="NO ACTION"),
        nullable=True,
    )
    delivery_month: Mapped[str | None] = mapped_column(String, nullable=True)
    planned_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    planned_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    delivery_status: Mapped[str | None] = mapped_column(String, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    order: Mapped["Order"] = relationship(  # type: ignore[name-defined]
        "Order",
        back_populates="delivery_plans",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<DeliveryPlan id={self.delivery_id} "
            f"order={self.order_id} month={self.delivery_month!r} "
            f"status={self.delivery_status!r}>"
        )
