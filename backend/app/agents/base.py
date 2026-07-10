"""Base agent class — shared execution pipeline."""

import json
import logging
import re
from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from app.agents.llm_client import LLMClient
from app.core.enums import AgentName
from app.core.validators import parse_uuid_optional
from app.repositories.agent_memory import AgentMemoryRepository
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse
from app.services.audit import AuditService

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    agent_name: AgentName

    def __init__(
        self,
        llm_client: LLMClient,
        memory_repo: AgentMemoryRepository,
        audit_service: AuditService,
    ) -> None:
        self.llm_client = llm_client
        self.memory_repo = memory_repo
        self.audit_service = audit_service

    @abstractmethod
    def validate_input(self, input_data: AgentExecuteRequest) -> None:
        ...

    @abstractmethod
    def build_prompt(self, context: dict[str, Any]) -> str:
        ...

    @abstractmethod
    async def process_response(
        self, input_data: AgentExecuteRequest, llm_output: str
    ) -> AgentExecuteResponse:
        ...

    async def save_memory(
        self,
        deal_id: UUID | None,
        prompt: str,
        response: str,
        tokens: int,
        execution_time_ms: float,
        summary: str | None = None,
    ) -> None:
        if deal_id is None:
            return
        await self.memory_repo.upsert_execution(
            deal_id=deal_id,
            agent_name=self.agent_name.value,
            prompt=prompt,
            response=response,
            tokens=tokens,
            execution_time_ms=execution_time_ms,
            summary=summary,
        )

    async def write_audit(
        self,
        deal_id: UUID | None,
        action: str,
        previous_status: str | None = None,
        new_status: str | None = None,
        reason: str | None = None,
    ) -> None:
        if deal_id is None:
            return
        await self.audit_service.log_action(
            deal_id=deal_id,
            agent_name=self.agent_name.value,
            action=action,
            previous_status=previous_status,
            new_status=new_status,
            reason=reason,
        )

    def _parse_json_from_llm(self, text: str) -> dict[str, Any]:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return {"summary": text}

    async def execute(self, input_data: AgentExecuteRequest) -> AgentExecuteResponse:
        self.validate_input(input_data)
        context = input_data.model_dump(exclude_none=True)
        prompt = self.build_prompt(context)
        system = f"You are {self.agent_name.value}, an AI sales agent for Iron Ridge Fire Apparatus."

        llm_result = await self.llm_client.complete(prompt, system)
        result = await self.process_response(input_data, llm_result.content)

        deal_uuid = parse_uuid_optional(input_data.deal_id)
        parsed = self._parse_json_from_llm(llm_result.content)
        await self.save_memory(
            deal_uuid,
            prompt,
            llm_result.content,
            llm_result.tokens,
            llm_result.execution_time_ms,
            summary=parsed.get("summary"),
        )
        return result
