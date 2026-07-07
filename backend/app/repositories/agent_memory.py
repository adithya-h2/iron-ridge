"""Agent memory repository."""

import json
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select

from app.models.agent_memory import AgentMemory
from app.repositories.base import BaseRepository


class AgentMemoryRepository(BaseRepository[AgentMemory]):
    model = AgentMemory
    pk_column = "memory_id"

    async def get_by_deal_and_agent(
        self, deal_id: UUID, agent_name: str
    ) -> AgentMemory | None:
        result = await self.session.execute(
            select(AgentMemory).where(
                AgentMemory.deal_id == deal_id,
                AgentMemory.agent_name == agent_name,
            )
        )
        return result.scalar_one_or_none()

    async def upsert_execution(
        self,
        deal_id: UUID,
        agent_name: str,
        prompt: str,
        response: str,
        tokens: int,
        execution_time_ms: float,
        summary: str | None = None,
    ) -> AgentMemory:
        context = json.dumps(
            {
                "prompt": prompt,
                "response": response,
                "tokens": tokens,
                "execution_time_ms": execution_time_ms,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        existing = await self.get_by_deal_and_agent(deal_id, agent_name)
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        if existing:
            existing.context = context
            existing.summary = summary
            existing.updated_at = now
            await self.session.flush()
            await self.session.refresh(existing)
            return existing
        return await self.create(
            deal_id=deal_id,
            agent_name=agent_name,
            context=context,
            summary=summary,
            updated_at=now,
        )
