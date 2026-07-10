"""Sally — Order Management agent."""

from typing import Any

from app.agents.base import BaseAgent
from app.core.enums import AgentName, DealStatus
from app.core.exceptions import ValidationAppError
from app.core.validators import parse_uuid
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse
from app.services.order import OrderService
from app.services.pipeline import PipelineService


class SallyAgent(BaseAgent):
    agent_name = AgentName.SALLY

    def __init__(
        self,
        llm_client,
        memory_repo,
        audit_service,
        order_service: OrderService,
        pipeline_service: PipelineService,
    ) -> None:
        super().__init__(llm_client, memory_repo, audit_service)
        self.order_service = order_service
        self.pipeline_service = pipeline_service

    def validate_input(self, input_data: AgentExecuteRequest) -> None:
        if not input_data.deal_id or not input_data.quotation_id:
            raise ValidationAppError("deal_id and quotation_id are required for Sally agent")

    def build_prompt(self, context: dict[str, Any]) -> str:
        return f"Create order for deal {context.get('deal_id')}. Return JSON with summary."

    async def process_response(
        self, input_data: AgentExecuteRequest, llm_output: str
    ) -> AgentExecuteResponse:
        deal_id = parse_uuid(input_data.deal_id, "deal_id")
        quotation_id = parse_uuid(input_data.quotation_id, "quotation_id")

        approval_status = (input_data.approval_status or "").upper()
        if approval_status == "APPROVED":
            await self.pipeline_service.transition(
                deal_id,
                DealStatus.APPROVED.value,
                AgentName.SALLY.value,
                "Pre-approved by Victor via n8n",
                approval_status="APPROVED",
            )

        order = await self.order_service.create_from_quotation(deal_id, quotation_id)
        await self.pipeline_service.transition(
            deal_id,
            DealStatus.ORDER_CREATED.value,
            AgentName.SALLY.value,
            "Order created",
        )
        await self.pipeline_service.transition(
            deal_id,
            DealStatus.PRODUCTION.value,
            AgentName.SALLY.value,
            "Production started",
        )
        return AgentExecuteResponse(
            deal_id=str(deal_id),
            status=DealStatus.ORDER_CREATED.value,
            current_agent=AgentName.SALLY.value,
            order_id=str(order.order_id),
            quotation_id=str(quotation_id),
        )
