"""Workflow engine abstraction — no direct n8n coupling."""

import logging
from typing import Protocol
from uuid import UUID

from app.core.enums import LeadSource

logger = logging.getLogger(__name__)


class WorkflowService(Protocol):
    async def publish_lead_created(
        self,
        workflow_id: UUID,
        deal_id: UUID,
        source: LeadSource,
        payload: dict,
    ) -> None:
        ...


class StubWorkflowService:
    """Logs workflow events; Sprint B adds N8nWorkflowAdapter."""

    async def publish_lead_created(
        self,
        workflow_id: UUID,
        deal_id: UUID,
        source: LeadSource,
        payload: dict,
    ) -> None:
        logger.info(
            "Workflow event published (stub)",
            extra={
                "workflow_id": str(workflow_id),
                "deal_id": str(deal_id),
                "source": source.value,
                "event": "lead_created",
                "payload_keys": list(payload.keys()),
            },
        )
