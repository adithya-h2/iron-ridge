"""Workflow engine abstraction — no direct n8n coupling."""

import logging
from typing import Protocol
from uuid import UUID

import httpx

from app.core.config import settings
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
    """Logs workflow events; optionally POSTs to n8n when feature_n8n_publish is enabled."""

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
        if not (settings.feature_n8n_publish and settings.n8n_webhook_base_url):
            return

        url = settings.n8n_webhook_base_url.rstrip("/")
        body = {
            "workflow_id": str(workflow_id),
            "deal_id": str(deal_id),
            "source": source.value,
            **payload,
        }
        request_id = payload.get("request_id")
        log_extra = {
            "url": url,
            "deal_id": str(deal_id),
            "workflow_id": str(workflow_id),
            "request_id": request_id,
        }
        try:
            async with httpx.AsyncClient(timeout=settings.n8n_timeout_seconds) as client:
                response = await client.post(url, json=body)
            if response.status_code >= 400:
                logger.warning(
                    "n8n publish failed",
                    extra={
                        **log_extra,
                        "status_code": response.status_code,
                        "response_body": response.text[:500],
                    },
                )
        except Exception as exc:
            logger.warning(
                "n8n publish failed",
                extra={**log_extra, "error": str(exc)},
            )
