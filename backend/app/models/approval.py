"""
app/models/approval.py

SQLAlchemy ORM model for the `approvals` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : approvals
Primary key  : approval_id (uuid)

Columns (exact match):
    approval_id   uuid        NOT NULL  PK
    quotation_id  uuid        NULL      FK -> quotations.quotation_id
    approved_by   varchar     NULL
    decision      varchar     NULL
    remarks       text        NULL
    approved_at   timestamp   NULL

NOTE: No deal_id FK in this table (approvals link via quotation only).
NOTE: approved_by (not approver_name), remarks (not comments).
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class Approval(Base):
    """ORM model for the `approvals` table. Victor's human-in-the-loop decision."""

    __tablename__ = "approvals"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    approval_id: Mapped[uuid.UUID] = mapped_column(
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
    approved_by: Mapped[str | None] = mapped_column(String, nullable=True)
    decision: Mapped[str | None] = mapped_column(String, nullable=True)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    quotation: Mapped["Quotation"] = relationship(  # type: ignore[name-defined]
        "Quotation",
        back_populates="approvals",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<Approval id={self.approval_id} "
            f"decision={self.decision!r} by={self.approved_by!r}>"
        )
