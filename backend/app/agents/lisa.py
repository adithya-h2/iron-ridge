"""Lisa — Lead Qualification agent."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from app.agents.base import BaseAgent
from app.core.enums import AgentName, DealStatus
from app.core.exceptions import ValidationAppError
from app.core.validators import parse_int_field, parse_uuid
from app.repositories.deal import DealRepository
from app.repositories.lead_validation import LeadValidationRepository
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse
from app.services.pipeline import PipelineService


class LisaAgent(BaseAgent):
    agent_name = AgentName.LISA

    def __init__(
        self,
        llm_client,
        memory_repo,
        audit_service,
        deal_repo: DealRepository,
        lead_validation_repo: LeadValidationRepository,
        pipeline_service: PipelineService,
    ) -> None:
        super().__init__(llm_client, memory_repo, audit_service)
        self.deal_repo = deal_repo
        self.lead_validation_repo = lead_validation_repo
        self.pipeline_service = pipeline_service

    def validate_input(self, input_data: AgentExecuteRequest) -> None:
        if not input_data.deal_id and not input_data.org_name:
            raise ValidationAppError("deal_id or org_name is required for Lisa agent")

    async def _resolve_deal_id(self, input_data: AgentExecuteRequest):
        if input_data.deal_id:
            return parse_uuid(input_data.deal_id, "deal_id")

        company = (input_data.org_name or input_data.company_name or "").strip()
        deal = await self.deal_repo.get_latest_lead_by_company_name(company)
        if deal is None:
            raise ValidationAppError(
                f"No LEAD deal found for company '{company}'",
                details={"org_name": company},
            )
        input_data.deal_id = str(deal.deal_id)
        return deal.deal_id

    def build_prompt(self, context: dict[str, Any]) -> str:
        return (
            f"Qualify this lead. Company: {context.get('org_name')}, "
            f"Lead score: {context.get('lead_score')}. "
            f"Return JSON with qualified (boolean), confidence_score (0-1), and summary."
        )

    async def process_response(
        self, input_data: AgentExecuteRequest, llm_output: str
    ) -> AgentExecuteResponse:
        parsed = self._parse_json_from_llm(llm_output)
        deal_id = await self._resolve_deal_id(input_data)
        lead_score = parse_int_field(input_data.lead_score or parsed.get("lead_score", 75), "lead_score", default=75)
        qualified = lead_score >= 80 or bool(parsed.get("qualified", False))
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        await self.lead_validation_repo.create(
            deal_id=deal_id,
            company_verified=True,
            email_verified=True,
            confidence_score=Decimal(str(parsed.get("confidence_score", 0.85))),
            lead_score=lead_score,
            validation_summary=parsed.get("summary"),
            validated_at=now,
        )

        if qualified:
            await self.pipeline_service.transition(
                deal_id, DealStatus.QUALIFICATION.value, AgentName.LISA.value, "Starting qualification"
            )
            await self.pipeline_service.transition(
                deal_id, DealStatus.QUALIFIED.value, AgentName.LISA.value, "Lead qualified"
            )
            status = DealStatus.QUALIFIED.value
        else:
            await self.pipeline_service.transition(
                deal_id, DealStatus.QUALIFICATION.value, AgentName.LISA.value, "Starting qualification"
            )
            await self.pipeline_service.transition(
                deal_id, DealStatus.REJECTED.value, AgentName.LISA.value, "Low lead score"
            )
            status = DealStatus.REJECTED.value

        return AgentExecuteResponse(
            deal_id=str(deal_id),
            org_name=input_data.org_name,
            status=status,
            current_agent=AgentName.LISA.value,
            lead_score=lead_score,
            qualified=qualified,
            reason=None if qualified else "LOW Lead Score",
        )
