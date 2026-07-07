"""Deal business service."""

from datetime import datetime, timezone
from uuid import UUID

from app.core.enums import DealStatus
from app.repositories.deal import DealRepository
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.deal import DealCreate, DealResponse, DealTransitionRequest, DealUpdate
from app.services.audit import AuditService
from app.services.pipeline import PipelineService


class DealService:
    def __init__(
        self,
        deal_repo: DealRepository,
        audit_service: AuditService,
        pipeline_service: PipelineService,
    ) -> None:
        self.deal_repo = deal_repo
        self.audit_service = audit_service
        self.pipeline_service = pipeline_service

    async def create(self, data: DealCreate) -> DealResponse:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        deal = await self.deal_repo.create(
            **data.model_dump(exclude_unset=True),
            status=data.status or DealStatus.LEAD.value,
            created_at=now,
            updated_at=now,
        )
        await self.audit_service.log_action(
            deal_id=deal.deal_id,
            agent_name=data.current_agent,
            action="deal_created",
            new_status=deal.status,
        )
        return DealResponse.model_validate(deal)

    async def get(self, deal_id: UUID) -> DealResponse:
        deal = await self.deal_repo.get_by_id_or_raise(deal_id)
        return DealResponse.model_validate(deal)

    async def list(
        self,
        pagination: PaginationParams | None = None,
        status: str | None = None,
    ) -> PaginatedResponse[DealResponse]:
        if status:
            result = await self.deal_repo.get_by_status(status, pagination)
        else:
            result = await self.deal_repo.get_all(pagination)
        return PaginatedResponse(
            items=[DealResponse.model_validate(i) for i in result.items],
            total=result.total,
            page=result.page,
            page_size=result.page_size,
            pages=result.pages,
        )

    async def update(self, deal_id: UUID, data: DealUpdate) -> DealResponse:
        deal = await self.deal_repo.update(
            deal_id,
            **data.model_dump(exclude_unset=True),
            updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        return DealResponse.model_validate(deal)

    async def delete(self, deal_id: UUID) -> None:
        await self.deal_repo.delete(deal_id)

    async def transition(self, deal_id: UUID, data: DealTransitionRequest) -> DealResponse:
        return await self.pipeline_service.transition(
            deal_id=deal_id,
            new_status=data.new_status,
            agent_name=data.agent_name,
            reason=data.reason,
        )
