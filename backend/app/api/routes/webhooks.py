"""n8n and Slack webhook routes."""

import json
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_agent_orchestrator, get_slack_service
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.slack import SlackService

router = APIRouter()


@router.post("/n8n/lead", response_model=AgentExecuteResponse)
async def n8n_lead_webhook(
    request: Request,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
) -> AgentExecuteResponse:
    """Entry point for n8n webhook — forwards to Marty agent."""
    body = await request.json()
    input_data = AgentExecuteRequest(**body)
    return await orchestrator.execute("marty", input_data)


@router.post("/approval-request")
async def approval_request_webhook(
    deal_id: UUID,
    quotation_id: UUID,
    grand_total: str | None = None,
    slack_service: SlackService = Depends(get_slack_service),
) -> dict:
    await slack_service.send_approval_request(deal_id, quotation_id, grand_total)
    return {"ok": True, "message": "Approval request sent to Slack"}


@router.post("/slack/interactions")
async def slack_interaction(
    request: Request,
    slack_service: SlackService = Depends(get_slack_service),
) -> dict:
    body = await request.body()
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "0")
    signature = request.headers.get("X-Slack-Signature", "")
    if not slack_service.verify_signature(timestamp, body, signature):
        return {"ok": False, "error": "Invalid signature"}

    form = await request.form()
    payload = json.loads(form.get("payload", "{}"))
    return await slack_service.handle_interaction(payload)
