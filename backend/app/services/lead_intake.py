"""Universal lead intake orchestrator — single entry point for all channels."""

from app.core.enums import AgentName, DealStatus
from app.repositories.lead_creation import LeadCreationRepository
from app.schemas.lead import LeadIntakeRequest, LeadIntakeResponse, NormalizedLead
from app.services.audit import AuditService
from app.services.duplicate_detection import DuplicateDetectionService
from app.services.lead_validator import LeadValidator
from app.services.notification_preparation import NotificationPreparationService
from app.services.workflow_trigger import WorkflowTriggerService


class LeadIntakeService:
    def __init__(
        self,
        lead_creation_repo: LeadCreationRepository,
        lead_validator: LeadValidator,
        duplicate_detection: DuplicateDetectionService,
        audit_service: AuditService,
        workflow_trigger: WorkflowTriggerService,
        notification_preparation: NotificationPreparationService,
    ) -> None:
        self.lead_creation_repo = lead_creation_repo
        self.lead_validator = lead_validator
        self.duplicate_detection = duplicate_detection
        self.audit_service = audit_service
        self.workflow_trigger = workflow_trigger
        self.notification_preparation = notification_preparation

    async def intake(self, request: LeadIntakeRequest) -> LeadIntakeResponse:
        normalized = self.lead_validator.validate_and_normalize(request)

        duplicate = await self.duplicate_detection.find_duplicate(normalized)
        workflow_id = self.workflow_trigger.generate_workflow_id()

        result = await self.lead_creation_repo.create_lead(
            normalized,
            workflow_id=workflow_id,
            existing_customer_id=duplicate.customer_id if duplicate else None,
        )

        await self.audit_service.log_action(
            deal_id=result.deal_id,
            agent_name=AgentName.MARTY.value,
            action="lead_intake",
            new_status=DealStatus.LEAD.value,
            reason=(
                f"Lead intake via {normalized.source.value}/{normalized.submission_channel}"
                + (f" (duplicate match: {duplicate.match_reason})" if duplicate else "")
            ),
        )

        response = LeadIntakeResponse(
            deal_id=result.deal_id,
            customer_id=result.customer_id,
            workflow_id=result.workflow_id,
            lead_source=result.lead_source,
            submission_channel=result.submission_channel,
            status=result.status,
            is_duplicate=duplicate is not None,
            matched_customer_id=duplicate.customer_id if duplicate else None,
            lead_score=None,
            company_name=normalized.company_name,
        )

        await self.workflow_trigger.trigger_lead_created(
            workflow_id=result.workflow_id,
            deal_id=result.deal_id,
            source=normalized.source,
            payload=self.notification_preparation.build_lead_notification_payload(
                normalized,
                result.deal_id,
                result.workflow_id,
                duplicate is not None,
            ),
        )

        await self.notification_preparation.notify_lead_created(normalized, response)
        return response

    async def intake_from_normalized(
        self,
        normalized: NormalizedLead,
        *,
        reuse_workflow_id: bool = False,
    ) -> LeadIntakeResponse:
        """Used by Marty/webhook adapters with pre-mapped fields."""
        request = LeadIntakeRequest(
            source=normalized.source,
            submission_channel=normalized.submission_channel,
            company_name=normalized.company_name,
            contact_person=normalized.contact_person,
            email=normalized.email,
            phone=normalized.phone,
            city=normalized.city,
            country=normalized.country,
            vehicle_type=normalized.vehicle_type,
            required_quantity=normalized.required_quantity,
        )
        return await self.intake(request)
