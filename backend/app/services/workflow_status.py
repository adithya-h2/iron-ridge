"""Read-only workflow status and timeline service."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from app.core.enums import DealStatus, PIPELINE_ORDER, pipeline_progress_percentage
from app.core.exceptions import NotFoundError
from app.repositories.audit_log import AuditLogRepository
from app.repositories.deal import DealRepository
from app.repositories.workflow_execution_state import WorkflowExecutionStateRepository
from app.schemas.common import PaginationParams
from app.schemas.workflow import (
    WorkflowCustomerSummary,
    WorkflowRetryState,
    WorkflowStatusResponse,
    WorkflowTimelineEvent,
    WorkflowTimelineResponse,
)


class WorkflowStatusService:
    DEFAULT_STEP_HOURS = 4.0

    def __init__(
        self,
        deal_repo: DealRepository,
        audit_repo: AuditLogRepository,
        retry_repo: WorkflowExecutionStateRepository | None = None,
    ) -> None:
        self.deal_repo = deal_repo
        self.audit_repo = audit_repo
        self.retry_repo = retry_repo

    async def get_status(self, deal_id: UUID) -> WorkflowStatusResponse:
        deal = await self.deal_repo.get_with_customer_or_raise(deal_id)
        customer = None
        if deal.customer:
            customer = WorkflowCustomerSummary.model_validate(deal.customer)

        progress = pipeline_progress_percentage(deal.status)
        estimated = await self._estimate_completion(deal.status, deal.updated_at)

        retry = None
        if self.retry_repo:
            state = await self.retry_repo.get_by_deal_id(deal_id)
            if state:
                retry = WorkflowRetryState(
                    attempt_count=state.attempt_count,
                    last_attempt=state.last_attempt_at,
                    last_error=state.last_error,
                    retryable=state.retryable,
                )

        return WorkflowStatusResponse(
            deal_id=deal.deal_id,
            customer=customer,
            workflow_id=deal.workflow_id,
            current_agent=deal.current_agent,
            current_status=deal.status,
            progress_percentage=progress,
            created_at=deal.created_at,
            updated_at=deal.updated_at,
            estimated_completion=estimated,
            retry=retry,
        )

    async def get_timeline(
        self, deal_id: UUID, pagination: PaginationParams | None = None
    ) -> WorkflowTimelineResponse:
        deal = await self.deal_repo.get_by_id(deal_id)
        if deal is None:
            raise NotFoundError("Deal not found", details={"deal_id": str(deal_id)})

        result = await self.audit_repo.get_by_deal_ordered(deal_id, pagination)
        events = [
            WorkflowTimelineEvent(
                timestamp=log.created_at,
                agent=log.agent_name,
                status=log.new_status,
                action=log.action,
                message=log.reason
                or (
                    f"{log.previous_status} → {log.new_status}"
                    if log.previous_status or log.new_status
                    else log.action
                ),
            )
            for log in result.items
        ]
        return WorkflowTimelineResponse(
            deal_id=deal_id,
            events=events,
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            pages=result.pages,
        )

    async def _estimate_completion(
        self, status: str | None, updated_at: datetime | None
    ) -> datetime | None:
        if not status or status in (DealStatus.DELIVERED.value, DealStatus.REJECTED.value):
            return None
        if updated_at is None:
            return None

        try:
            current = DealStatus(status)
        except ValueError:
            return None
        if current not in PIPELINE_ORDER:
            return None

        remaining_steps = len(PIPELINE_ORDER) - PIPELINE_ORDER.index(current) - 1
        if remaining_steps <= 0:
            return None

        median_hours = await self.audit_repo.get_median_completion_hours()
        step_hours = (
            median_hours / len(PIPELINE_ORDER) if median_hours else self.DEFAULT_STEP_HOURS
        )
        hours_left = remaining_steps * step_hours
        base = updated_at
        if base.tzinfo is not None:
            base = base.replace(tzinfo=None)
        return base + timedelta(hours=hours_left)
