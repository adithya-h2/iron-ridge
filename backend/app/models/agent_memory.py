"""
app/models/agent_memory.py

SQLAlchemy ORM model for the `agent_memory` table.

Source of truth: Supabase schema dump (tools/schema_dump.json)
Table name   : agent_memory
Primary key  : memory_id (uuid)

Columns (exact match):
    memory_id   uuid        NOT NULL  PK
    deal_id     uuid        NULL      FK -> deals.deal_id
    agent_name  varchar     NULL
    context     text        NULL
    summary     text        NULL
    updated_at  timestamp   NULL

NOTE: context is TEXT (not JSONB). No created_at — schema only has updated_at.
"""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base


class AgentMemory(Base):
    """ORM model for the `agent_memory` table. Per-agent LLM context store."""

    __tablename__ = "agent_memory"

    # ------------------------------------------------------------------
    # Primary Key
    # ------------------------------------------------------------------
    memory_id: Mapped[uuid.UUID] = mapped_column(
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
    context: Mapped[str | None] = mapped_column(Text, nullable=True)   # TEXT not JSONB
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    deal: Mapped["Deal"] = relationship(  # type: ignore[name-defined]
        "Deal",
        back_populates="agent_memories",
        lazy="select",
    )

    def __repr__(self) -> str:
        return (
            f"<AgentMemory id={self.memory_id} "
            f"agent={self.agent_name!r} deal={self.deal_id}>"
        )
