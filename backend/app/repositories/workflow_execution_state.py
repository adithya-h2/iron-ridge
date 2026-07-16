"""Workflow execution state repository."""

from datetime import datetime, timezone
from uuid import UUID

from app.models.workflow_execution_state import WorkflowExecutionState
from app.repositories.base import BaseRepository


class WorkflowExecutionStateRepository(BaseRepository[WorkflowExecutionState]):
    model = WorkflowExecutionState
    pk_column = "deal_id"

    async def get_by_deal_id(self, deal_id: UUID) -> WorkflowExecutionState | None:
        return await self.get_by_id(deal_id)

    async def record_failure(self, deal_id: UUID, error: str, retryable: bool = True) -> WorkflowExecutionState:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        existing = await self.get_by_deal_id(deal_id)
        if existing:
            return await self.update(
                deal_id,
                attempt_count=existing.attempt_count + 1,
                last_attempt_at=now,
                last_error=error[:2000],
                retryable=retryable,
                updated_at=now,
            )
        return await self.create(
            deal_id=deal_id,
            attempt_count=1,
            last_attempt_at=now,
            last_error=error[:2000],
            retryable=retryable,
            updated_at=now,
        )

    async def record_retry_attempt(self, deal_id: UUID) -> WorkflowExecutionState:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        existing = await self.get_by_deal_id(deal_id)
        if existing:
            return await self.update(
                deal_id,
                attempt_count=existing.attempt_count + 1,
                last_attempt_at=now,
                updated_at=now,
            )
        return await self.create(
            deal_id=deal_id,
            attempt_count=1,
            last_attempt_at=now,
            retryable=True,
            updated_at=now,
        )
