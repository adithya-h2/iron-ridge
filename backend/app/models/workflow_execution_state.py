"""Workflow execution state ORM model (retry tracking)."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class WorkflowExecutionState(Base):
    __tablename__ = "workflow_execution_state"

    deal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("deals.deal_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    attempt_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    retryable: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
