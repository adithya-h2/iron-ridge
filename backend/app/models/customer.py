"""
app/models/customer.py

SQLAlchemy ORM model for the `customers` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : customers
Primary key  : customer_id (uuid)

Columns (exact match to deployed schema):
    customer_id     uuid         NOT NULL  PK
    company_name    varchar      NULL
    contact_person  varchar      NULL
    email           varchar      NULL
    phone           varchar      NULL
    website         varchar      NULL
    industry        varchar      NULL
    ownership_type  varchar      NULL
    address         text         NULL
    city            varchar      NULL
    state           varchar      NULL
    country         varchar      NULL
    created_at      timestamp    NULL
    updated_at      timestamp    NULL

Foreign keys referencing this table:
    deals.customer_id -> customers.customer_id
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Customer(Base):
    """ORM model for the `customers` table."""

    __tablename__ = "customers"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Columns — exact names and types from deployed schema
    # ------------------------------------------------------------------
    company_name: Mapped[str | None] = mapped_column(String, nullable=True)
    contact_person: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    website: Mapped[str | None] = mapped_column(String, nullable=True)
    industry: Mapped[str | None] = mapped_column(String, nullable=True)
    ownership_type: Mapped[str | None] = mapped_column(String, nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)
    state: Mapped[str | None] = mapped_column(String, nullable=True)
    country: Mapped[str | None] = mapped_column(String, nullable=True)

    # Timestamps — database stores without timezone (matches schema: timestamp)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    deals: Mapped[list["Deal"]] = relationship(  # type: ignore[name-defined]
        "Deal",
        back_populates="customer",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Customer id={self.customer_id} company={self.company_name!r}>"
