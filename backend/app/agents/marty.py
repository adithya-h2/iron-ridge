"""Marty — Marketing / Lead agent."""

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.agents.base import BaseAgent
from app.core.enums import AgentName, DealStatus
from app.core.exceptions import ValidationAppError
from app.repositories.customer import CustomerRepository
from app.repositories.deal import DealRepository
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse


class MartyAgent(BaseAgent):
    agent_name = AgentName.MARTY

    def __init__(
        self,
        llm_client,
        memory_repo,
        audit_service,
        customer_repo: CustomerRepository,
        deal_repo: DealRepository,
    ) -> None:
        super().__init__(llm_client, memory_repo, audit_service)
        self.customer_repo = customer_repo
        self.deal_repo = deal_repo

    def validate_input(self, input_data: AgentExecuteRequest) -> None:
        if not input_data.org_name:
            raise ValidationAppError("org_name is required for Marty agent")

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

        customer = await self.customer_repo.create(
            company_name=input_data.org_name,
            city=input_data.city,
            country=input_data.country,
            industry="Healthcare" if input_data.org_name else None,
            created_at=now,
            updated_at=now,
        )
        deal = await self.deal_repo.create(
            customer_id=customer.customer_id,
            status=DealStatus.LEAD.value,
            current_agent=AgentName.MARTY.value,
            lead_score=lead_score,
            created_at=now,
            updated_at=now,
        )
        await self.write_audit(
            deal.deal_id, "lead_created", new_status=DealStatus.LEAD.value, reason="New lead intake"
        )
        return AgentExecuteResponse(
            deal_id=str(deal.deal_id),
            org_name=input_data.org_name,
            status=DealStatus.LEAD.value,
            current_agent=AgentName.MARTY.value,
            lead_score=lead_score,
        )
