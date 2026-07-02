"""
app/models/deal.py

SQLAlchemy ORM model for the `deals` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : deals
Primary key  : deal_id (uuid)

Columns (exact match to deployed schema):
    deal_id          uuid        NOT NULL  PK
    customer_id      uuid        NULL      FK -> customers.customer_id
    status           varchar     NULL
    priority         varchar     NULL
    current_agent    varchar     NULL
    lead_score       int4        NULL
    approval_status  varchar     NULL
    created_at       timestamp   NULL
    updated_at       timestamp   NULL

Foreign keys FROM this table:
    deals.customer_id -> customers.customer_id

Foreign keys TO this table:
    agent_memory.deal_id, audit_logs.deal_id, bom.deal_id,
    lead_validation.deal_id, orders.deal_id, quotations.deal_id,
    requirements.deal_id
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Deal(Base):
    """ORM model for the `deals` table. The central business entity."""

    __tablename__ = "deals"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    deal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # ------------------------------------------------------------------
    # Columns — exact names and types from deployed schema
    # ------------------------------------------------------------------
    customer_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.customer_id", ondelete="NO ACTION"),
        nullable=True,
    )
    status: Mapped[str | None] = mapped_column(String, nullable=True)
    priority: Mapped[str | None] = mapped_column(String, nullable=True)
    current_agent: Mapped[str | None] = mapped_column(String, nullable=True)
    lead_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    approval_status: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    customer: Mapped["Customer"] = relationship(  # type: ignore[name-defined]
        "Customer",
        back_populates="deals",
        lazy="select",
    )
    lead_validations: Mapped[list["LeadValidation"]] = relationship(  # type: ignore[name-defined]
        "LeadValidation",
        back_populates="deal",
        lazy="select",
    )
    requirements: Mapped[list["Requirement"]] = relationship(  # type: ignore[name-defined]
        "Requirement",
        back_populates="deal",
        lazy="select",
    )
    quotations: Mapped[list["Quotation"]] = relationship(  # type: ignore[name-defined]
        "Quotation",
        back_populates="deal",
        lazy="select",
    )
    orders: Mapped[list["Order"]] = relationship(  # type: ignore[name-defined]
        "Order",
        back_populates="deal",
        lazy="select",
    )
    boms: Mapped[list["BOM"]] = relationship(  # type: ignore[name-defined]
        "BOM",
        back_populates="deal",
        lazy="select",
    )
    agent_memories: Mapped[list["AgentMemory"]] = relationship(  # type: ignore[name-defined]
        "AgentMemory",
        back_populates="deal",
        lazy="select",
    )
    audit_logs: Mapped[list["AuditLog"]] = relationship(  # type: ignore[name-defined]
        "AuditLog",
        back_populates="deal",
        lazy="select",
    )

    def __repr__(self) -> str:
        return f"<Deal id={self.deal_id} status={self.status!r} agent={self.current_agent!r}>"
