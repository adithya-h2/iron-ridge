"""Paul — Pricing / BOM agent."""

from typing import Any
from uuid import UUID

from app.agents.base import BaseAgent
from app.core.enums import AgentName, ApprovalStatus, DealStatus
from app.core.exceptions import ValidationAppError
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse
from app.services.approval import ApprovalService
from app.services.pipeline import PipelineService
from app.services.pricing import PricingService


class PaulAgent(BaseAgent):
    agent_name = AgentName.PAUL

    def __init__(
        self,
        llm_client,
        memory_repo,
        audit_service,
        pricing_service: PricingService,
        pipeline_service: PipelineService,
        approval_service: ApprovalService,
    ) -> None:
        super().__init__(llm_client, memory_repo, audit_service)
        self.pricing_service = pricing_service
        self.pipeline_service = pipeline_service
        self.approval_service = approval_service

    def validate_input(self, input_data: AgentExecuteRequest) -> None:
        if not input_data.deal_id:
            raise ValidationAppError("deal_id is required for Paul agent")

    def build_prompt(self, context: dict[str, Any]) -> str:
        return (
            f"Generate pricing summary for {context.get('vehicle_type')}, "
            f"qty {context.get('required_quantity')}. Return JSON with summary."
        )

    async def process_response(
        self, input_data: AgentExecuteRequest, llm_output: str
    ) -> AgentExecuteResponse:
        deal_id = UUID(input_data.deal_id)  # type: ignore[arg-type]
        qty = int(input_data.required_quantity or 1)
        vehicle_type = input_data.vehicle_type or "Ambulance"

        quotation = await self.pricing_service.generate_quotation(deal_id, vehicle_type, qty)
        await self.pipeline_service.transition(
            deal_id, DealStatus.PRICING.value, AgentName.PAUL.value, "Generating pricing"
        )
        await self.pipeline_service.transition(
            deal_id,
            DealStatus.PRICED.value,
            AgentName.PAUL.value,
            "Quotation generated",
        )
        await self.approval_service.request_approval(quotation.quotation_id)

        return AgentExecuteResponse(
            deal_id=str(deal_id),
            status=DealStatus.PRICED.value,
            current_agent=AgentName.PAUL.value,
            quotation_id=str(quotation.quotation_id),
            quotation_generated="true",
            approval_status=ApprovalStatus.PENDING.value,
        )
