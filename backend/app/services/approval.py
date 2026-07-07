"""Approval business service."""

from datetime import datetime, timezone
from uuid import UUID

from app.core.enums import AgentName, ApprovalStatus, DealStatus
from app.repositories.approval import ApprovalRepository
from app.repositories.quotation import QuotationRepository
from app.schemas.approval import ApprovalCreate, ApprovalDecideRequest, ApprovalResponse
from app.services.audit import AuditService
from app.services.pipeline import PipelineService


class ApprovalService:
    def __init__(
        self,
        approval_repo: ApprovalRepository,
        quotation_repo: QuotationRepository,
        pipeline_service: PipelineService,
        audit_service: AuditService,
    ) -> None:
        self.approval_repo = approval_repo
        self.quotation_repo = quotation_repo
        self.pipeline_service = pipeline_service
        self.audit_service = audit_service

    async def create(self, data: ApprovalCreate) -> ApprovalResponse:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        approval = await self.approval_repo.create(
            **data.model_dump(exclude_unset=True),
            approved_at=now if data.decision else None,
        )
        return ApprovalResponse.model_validate(approval)

    async def get(self, approval_id: UUID) -> ApprovalResponse:
        a = await self.approval_repo.get_by_id_or_raise(approval_id)
        return ApprovalResponse.model_validate(a)

    async def request_approval(self, quotation_id: UUID) -> ApprovalResponse:
        quotation = await self.quotation_repo.get_by_id_or_raise(quotation_id)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        approval = await self.approval_repo.create(
            quotation_id=quotation_id,
            decision=ApprovalStatus.PENDING.value,
            approved_at=None,
        )
        if quotation.deal_id:
            await self.pipeline_service.transition(
                quotation.deal_id,
                DealStatus.APPROVAL_PENDING.value,
                AgentName.VICTOR.value,
                "Approval requested",
                approval_status=ApprovalStatus.PENDING.value,
            )
            await self.audit_service.log_action(
                deal_id=quotation.deal_id,
                agent_name=AgentName.VICTOR.value,
                action="approval_requested",
                new_status=DealStatus.APPROVAL_PENDING.value,
            )
        return ApprovalResponse.model_validate(approval)

    async def decide(self, approval_id: UUID, data: ApprovalDecideRequest) -> ApprovalResponse:
        approval = await self.approval_repo.get_by_id_or_raise(approval_id)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        updated = await self.approval_repo.update(
            approval_id,
            decision=data.decision,
            approved_by=data.approved_by,
            remarks=data.remarks,
            approved_at=now,
        )
        quotation = await self.quotation_repo.get_by_id(approval.quotation_id) if approval.quotation_id else None
        if quotation and quotation.deal_id:
            await self.pipeline_service.set_approval_status(
                quotation.deal_id,
                data.decision,
                data.approved_by or AgentName.VICTOR.value,
            )
            await self.audit_service.log_action(
                deal_id=quotation.deal_id,
                agent_name=data.approved_by,
                action="approval_decided",
                new_status=data.decision,
                reason=data.remarks,
            )
        return ApprovalResponse.model_validate(updated)
