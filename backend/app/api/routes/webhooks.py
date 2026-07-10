"""n8n and Slack webhook routes."""

import json
from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_agent_orchestrator, get_lead_intake_service, get_slack_service
from app.core.enums import LeadSource
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse
from app.schemas.common import ApiResponse
from app.schemas.lead import LeadIntakeRequest, LeadIntakeResponse
from app.services.agent_orchestrator import AgentOrchestrator
from app.services.lead_intake import LeadIntakeService
from app.services.slack import SlackService

router = APIRouter()


@router.post("/n8n/lead", response_model=ApiResponse[LeadIntakeResponse])
async def n8n_lead_webhook(
    request: Request,
    lead_intake_service: LeadIntakeService = Depends(get_lead_intake_service),
) -> ApiResponse[LeadIntakeResponse]:
    """Entry point for n8n webhook — delegates to universal lead intake."""
    body = await request.json()
    if not isinstance(body, dict):
        body = {}
    intake_request = LeadIntakeRequest(
        source=LeadSource.API,
        submission_channel="n8n",
        org_name=body.get("org_name"),
        company_name=body.get("company_name"),
        email=body.get("email"),
        phone=body.get("phone"),
        city=body.get("city"),
        country=body.get("country"),
        vehicle_type=body.get("vehicle_type"),
        required_quantity=body.get("required_quantity"),
        contact_person=body.get("contact_person"),
    )
    result = await lead_intake_service.intake(intake_request)
    return ApiResponse(success=True, data=result)


@router.post("/n8n/lead/marty", response_model=AgentExecuteResponse)
async def n8n_lead_marty_webhook(
    request: Request,
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
) -> AgentExecuteResponse:
    """Legacy n8n → Marty scoring path (backward compatible)."""
    body = await request.json()
    input_data = AgentExecuteRequest(**body) if isinstance(body, dict) else AgentExecuteRequest()
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
