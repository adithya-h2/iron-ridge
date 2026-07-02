"""
app/models/audit_log.py

SQLAlchemy ORM model for the `audit_logs` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : audit_logs   (NOT audit_log — deployed name is plural)
Primary key  : audit_id (uuid)

Columns (exact match):
    audit_id         uuid       NOT NULL  PK
    deal_id          uuid       NULL      FK -> deals.deal_id
    agent_name       varchar    NULL
    action           varchar    NULL
    previous_status  varchar    NULL
    new_status       varchar    NULL
    reason           text       NULL
    created_at       timestamp  NULL

NOTE: Table is `audit_logs` (plural). No updated_at — append-only log.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class AuditLog(Base):
    """
    ORM model for the `audit_logs` table.

    Append-only audit trail of every status change and agent action.
    Records are NEVER modified after creation.
    """

    __tablename__ = "audit_logs"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    audit_id: Mapped[uuid.UUID] = mapped_column(
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
    agent_name: Mapped[str | None] = mapped_column(String, nullable=True)
    action: Mapped[str | None] = mapped_column(String, nullable=True)
    previous_status: Mapped[str | None] = mapped_column(String, nullable=True)
    new_status: Mapped[str | None] = mapped_column(String, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    deal: Mapped["Deal"] = relationship(  # type: ignore[name-defined]
        "Deal",
        back_populates="audit_logs",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<AuditLog id={self.audit_id} "
            f"agent={self.agent_name!r} action={self.action!r} "
            f"deal={self.deal_id}>"
        )
