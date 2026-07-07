"""Adam — Delivery agent."""

from datetime import date
from typing import Any
from uuid import UUID

from app.agents.base import BaseAgent
from app.core.enums import AgentName, DealStatus
from app.core.exceptions import ValidationAppError
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse
from app.services.order import OrderService
from app.services.pipeline import PipelineService


class AdamAgent(BaseAgent):
    agent_name = AgentName.ADAM

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
        if not input_data.deal_id or not input_data.order_id:
            raise ValidationAppError("deal_id and order_id are required for Adam agent")

    def build_prompt(self, context: dict[str, Any]) -> str:
        return (
            f"Plan delivery for customer {context.get('customer_name')}, "
            f"order {context.get('order_id')}. Return JSON with summary."
        )

    async def process_response(
        self, input_data: AgentExecuteRequest, llm_output: str
    ) -> AgentExecuteResponse:
        deal_id = UUID(input_data.deal_id)  # type: ignore[arg-type]
        order_id = UUID(input_data.order_id)  # type: ignore[arg-type]

        today = date.today()
        await self.order_service.create_delivery_plan(
            order_id=order_id,
            delivery_month=today.strftime("%B %Y"),
            planned_quantity=1,
            planned_date=today,
        )
        await self.pipeline_service.transition(
            deal_id,
            DealStatus.DELIVERED.value,
            AgentName.ADAM.value,
            "Delivery completed",
        )
        return AgentExecuteResponse(
            deal_id=str(deal_id),
            status=DealStatus.DELIVERED.value,
            current_agent=AgentName.ADAM.value,
            order_id=str(order_id),
            org_name=input_data.customer_name,
        )
