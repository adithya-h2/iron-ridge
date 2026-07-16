"""Workflow retry tracking service."""

from uuid import UUID

from app.repositories.workflow_execution_state import WorkflowExecutionStateRepository


class WorkflowRetryService:
    def __init__(self, retry_repo: WorkflowExecutionStateRepository) -> None:
        self.retry_repo = retry_repo

    async def record_failure(self, deal_id: UUID, error: str, retryable: bool = True) -> None:
        await self.retry_repo.record_failure(deal_id, error, retryable)

    async def record_retry_attempt(self, deal_id: UUID) -> None:
        await self.retry_repo.record_retry_attempt(deal_id)
