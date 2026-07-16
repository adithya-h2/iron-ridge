"""AI agent execution routes — n8n compatible (JSON + form dual-parser)."""

import logging

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_agent_orchestrator, require_agent_access
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse
from app.schemas.auth import UserResponse
from app.services.agent_orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter()


async def parse_agent_input(request: Request) -> AgentExecuteRequest:
    """
    Accept JSON body OR form-encoded fields (n8n compatibility).
    JSON values take precedence over form when both are present.
    """
    json_data: dict = {}
    form_data: dict = {}

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                json_data = body
        except Exception:
            pass

    try:
        form = await request.form()
        form_data = {k: str(v) for k, v in form.items() if v is not None and str(v).strip()}
    except Exception:
        pass

    merged = {**form_data}
    for key, value in json_data.items():
        if value is not None and (not isinstance(value, str) or value.strip()):
            merged[key] = value

    return AgentExecuteRequest(**merged)


async def _execute_agent(
    agent_name: str,
    request: Request,
    input_data: AgentExecuteRequest,
    orchestrator: AgentOrchestrator,
) -> AgentExecuteResponse:
    request.state.agent_name = agent_name
    if input_data.deal_id:
        request.state.deal_id = input_data.deal_id
    return await orchestrator.execute(agent_name, input_data)


@router.post("/marty", response_model=AgentExecuteResponse)
async def execute_marty(
    request: Request,
    input_data: AgentExecuteRequest = Depends(parse_agent_input),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    _: UserResponse | None = Depends(require_agent_access),
) -> AgentExecuteResponse:
    return await _execute_agent("marty", request, input_data, orchestrator)


@router.post("/lisa", response_model=AgentExecuteResponse)
async def execute_lisa(
    request: Request,
    input_data: AgentExecuteRequest = Depends(parse_agent_input),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    _: UserResponse | None = Depends(require_agent_access),
) -> AgentExecuteResponse:
    return await _execute_agent("lisa", request, input_data, orchestrator)


@router.post("/neil", response_model=AgentExecuteResponse)
async def execute_neil(
    request: Request,
    input_data: AgentExecuteRequest = Depends(parse_agent_input),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    _: UserResponse | None = Depends(require_agent_access),
) -> AgentExecuteResponse:
    return await _execute_agent("neil", request, input_data, orchestrator)


@router.post("/paul", response_model=AgentExecuteResponse)
async def execute_paul(
    request: Request,
    input_data: AgentExecuteRequest = Depends(parse_agent_input),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    _: UserResponse | None = Depends(require_agent_access),
) -> AgentExecuteResponse:
    return await _execute_agent("paul", request, input_data, orchestrator)


@router.post("/sally", response_model=AgentExecuteResponse)
async def execute_sally(
    request: Request,
    input_data: AgentExecuteRequest = Depends(parse_agent_input),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    _: UserResponse | None = Depends(require_agent_access),
) -> AgentExecuteResponse:
    return await _execute_agent("sally", request, input_data, orchestrator)


@router.post("/adam", response_model=AgentExecuteResponse)
async def execute_adam(
    request: Request,
    input_data: AgentExecuteRequest = Depends(parse_agent_input),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    _: UserResponse | None = Depends(require_agent_access),
) -> AgentExecuteResponse:
    return await _execute_agent("adam", request, input_data, orchestrator)
