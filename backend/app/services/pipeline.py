"""Pipeline state machine service."""

from datetime import datetime, timezone
from uuid import UUID

from app.core.enums import AgentName, ApprovalStatus, DealStatus, PIPELINE_TRANSITIONS
from app.core.exceptions import InvalidTransitionError, NotFoundError
from app.repositories.deal import DealRepository
from app.schemas.deal import DealResponse
from app.services.audit import AuditService


class PipelineService:
    def __init__(self, deal_repo: DealRepository, audit_service: AuditService) -> None:
        self.deal_repo = deal_repo
        self.audit_service = audit_service

    def _parse_status(self, status: str | None) -> DealStatus | None:
        if status is None:
            return None
        try:
            return DealStatus(status)
        except ValueError:
            return None

    def validate_transition(self, current: str | None, new: str) -> None:
        current_enum = self._parse_status(current)
        try:
            new_enum = DealStatus(new)
        except ValueError as exc:
            raise InvalidTransitionError(
                f"Unknown status: {new}",
                details={"current": current, "new": new},
            ) from exc

        if current_enum is None:
            if new_enum != DealStatus.LEAD:
                raise InvalidTransitionError(
                    "New deals must start at LEAD",
                    details={"new": new},
                )
            return

        allowed = PIPELINE_TRANSITIONS.get(current_enum, set())
        if new_enum not in allowed:
            raise InvalidTransitionError(
                f"Cannot transition from {current_enum.value} to {new_enum.value}",
                details={"current": current_enum.value, "new": new_enum.value, "allowed": [s.value for s in allowed]},
            )

    async def transition(
        self,
        deal_id: UUID,
        new_status: str,
        agent_name: str | None = None,
        reason: str | None = None,
        approval_status: str | None = None,
        lead_score: int | None = None,
    ) -> DealResponse:
        deal = await self.deal_repo.get_by_id(deal_id)
        if deal is None:
            raise NotFoundError("Deal not found", details={"deal_id": str(deal_id)})

        previous = deal.status
        self.validate_transition(previous, new_status)

        update_fields: dict = {
            "status": new_status,
            "updated_at": datetime.now(timezone.utc).replace(tzinfo=None),
        }
        if agent_name:
            update_fields["current_agent"] = agent_name
        if approval_status:
            update_fields["approval_status"] = approval_status
        if lead_score is not None:
            update_fields["lead_score"] = lead_score

        updated = await self.deal_repo.update(deal_id, **update_fields)
        await self.audit_service.log_status_change(
            deal_id=deal_id,
            agent_name=agent_name,
            previous_status=previous,
            new_status=new_status,
            reason=reason,
        )
        return DealResponse.model_validate(updated)

    async def set_approval_status(
        self, deal_id: UUID, approval_status: str, agent_name: str = AgentName.VICTOR.value
    ) -> DealResponse:
        if approval_status == ApprovalStatus.APPROVED.value:
            return await self.transition(
                deal_id, DealStatus.APPROVED.value, agent_name, "Approval granted"
            )
        if approval_status == ApprovalStatus.REJECTED.value:
            return await self.transition(
                deal_id,
                DealStatus.REJECTED.value,
                agent_name,
                "Approval rejected",
                approval_status=approval_status,
            )
        deal = await self.deal_repo.update(
            deal_id,
            approval_status=approval_status,
            current_agent=agent_name,
            updated_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        return DealResponse.model_validate(deal)
