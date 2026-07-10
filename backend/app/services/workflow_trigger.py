"""Triggers workflow events after lead intake."""

from uuid import UUID, uuid4

from app.core.enums import LeadSource
from app.repositories.lead_creation import LeadCreationRepository
from app.services.workflow import WorkflowService


class WorkflowTriggerService:
    def __init__(self, workflow_service: WorkflowService) -> None:
        self.workflow_service = workflow_service

    def generate_workflow_id(self) -> UUID:
        return LeadCreationRepository.new_workflow_id()

    async def trigger_lead_created(
        self,
        workflow_id: UUID,
        deal_id: UUID,
        source: LeadSource,
        payload: dict,
    ) -> UUID:
        await self.workflow_service.publish_lead_created(
            workflow_id=workflow_id,
            deal_id=deal_id,
            source=source,
            payload=payload,
        )
        return workflow_id
