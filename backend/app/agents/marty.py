"""Marty — Marketing / Lead agent."""

from datetime import datetime, timezone
from typing import Any

from app.agents.base import BaseAgent
from app.core.enums import AgentName, DealStatus, LeadSource
from app.core.exceptions import ValidationAppError
from app.core.validators import parse_uuid_optional
from app.repositories.deal import DealRepository
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse
from app.schemas.lead import LeadIntakeRequest
from app.services.lead_intake import LeadIntakeService


class MartyAgent(BaseAgent):
    agent_name = AgentName.MARTY

    def __init__(
        self,
        llm_client,
        memory_repo,
        audit_service,
        lead_intake_service: LeadIntakeService,
        deal_repo: DealRepository,
    ) -> None:
        super().__init__(llm_client, memory_repo, audit_service)
        self.lead_intake_service = lead_intake_service
        self.deal_repo = deal_repo

    def validate_input(self, input_data: AgentExecuteRequest) -> None:
        if not input_data.deal_id and not input_data.org_name:
            raise ValidationAppError("org_name is required for Marty agent when deal_id is absent")

    def build_prompt(self, context: dict[str, Any]) -> str:
        return (
            f"Score this fire apparatus sales lead (0-100). "
            f"Company: {context.get('org_name')}, "
            f"Vehicle: {context.get('vehicle_type')}, "
            f"Quantity: {context.get('required_quantity')}, "
            f"Location: {context.get('city')}, {context.get('country')}. "
            f"Return JSON with lead_score (integer) and summary."
        )

    async def process_response(
        self, input_data: AgentExecuteRequest, llm_output: str
    ) -> AgentExecuteResponse:
        parsed = self._parse_json_from_llm(llm_output)
        lead_score = int(parsed.get("lead_score", 75))
        now = datetime.now(timezone.utc).replace(tzinfo=None)

        existing_deal_id = parse_uuid_optional(input_data.deal_id)
        if existing_deal_id:
            deal = await self.deal_repo.update(
                existing_deal_id,
                lead_score=lead_score,
                current_agent=AgentName.MARTY.value,
                updated_at=now,
            )
            org_name = input_data.org_name
        else:
            intake_result = await self.lead_intake_service.intake(
                LeadIntakeRequest(
                    source=LeadSource.API,
                    submission_channel="marty_agent",
                    org_name=input_data.org_name,
                    city=input_data.city,
                    country=input_data.country,
                    vehicle_type=input_data.vehicle_type,
                    required_quantity=input_data.required_quantity,
                )
            )
            deal = await self.deal_repo.update(
                intake_result.deal_id,
                lead_score=lead_score,
                current_agent=AgentName.MARTY.value,
                updated_at=now,
            )
            org_name = intake_result.company_name or input_data.org_name

        await self.write_audit(
            deal.deal_id,
            "lead_scored",
            new_status=DealStatus.LEAD.value,
            reason=f"Marty scored lead: {lead_score}",
        )
        return AgentExecuteResponse(
            deal_id=str(deal.deal_id),
            org_name=org_name,
            status=DealStatus.LEAD.value,
            current_agent=AgentName.MARTY.value,
            lead_score=lead_score,
        )
