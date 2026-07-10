"""Neil — Requirements agent."""

from datetime import datetime, timezone
from typing import Any

from app.agents.base import BaseAgent
from app.core.enums import AgentName, DealStatus
from app.core.exceptions import ValidationAppError
from app.core.validators import parse_int_field, parse_uuid
from app.repositories.requirement import RequirementRepository
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse
from app.services.pipeline import PipelineService


class NeilAgent(BaseAgent):
    agent_name = AgentName.NEIL

    def __init__(
        self,
        llm_client,
        memory_repo,
        audit_service,
        requirement_repo: RequirementRepository,
        pipeline_service: PipelineService,
    ) -> None:
        super().__init__(llm_client, memory_repo, audit_service)
        self.requirement_repo = requirement_repo
        self.pipeline_service = pipeline_service

    def validate_input(self, input_data: AgentExecuteRequest) -> None:
        if not input_data.deal_id:
            raise ValidationAppError("deal_id is required for Neil agent")

    def build_prompt(self, context: dict[str, Any]) -> str:
        return (
            f"Capture sales requirements. Vehicle: {context.get('vehicle_type')}, "
            f"Quantity: {context.get('required_quantity')}. "
            f"Return JSON with requirements (string) and summary."
        )

    async def process_response(
        self, input_data: AgentExecuteRequest, llm_output: str
    ) -> AgentExecuteResponse:
        parsed = self._parse_json_from_llm(llm_output)
        deal_id = parse_uuid(input_data.deal_id, "deal_id")
        qty = parse_int_field(input_data.required_quantity, "required_quantity", default=1)
        requirements_text = parsed.get("requirements", parsed.get("summary", ""))
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        await self.requirement_repo.create(
            deal_id=deal_id,
            vehicle_type=input_data.vehicle_type,
            quantity=qty,
            special_requirements=requirements_text,
            created_at=now,
        )
        await self.pipeline_service.transition(
            deal_id, DealStatus.REQUIREMENTS.value, AgentName.NEIL.value, "Gathering requirements"
        )
        await self.pipeline_service.transition(
            deal_id,
            DealStatus.REQUIREMENTS_COLLECTED.value,
            AgentName.NEIL.value,
            "Requirements captured",
        )
        return AgentExecuteResponse(
            deal_id=str(deal_id),
            org_name=input_data.org_name,
            status=DealStatus.REQUIREMENTS_COLLECTED.value,
            current_agent=AgentName.NEIL.value,
            requirements=requirements_text,
        )
