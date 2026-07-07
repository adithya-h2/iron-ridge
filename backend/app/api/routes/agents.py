"""AI agent execution routes — n8n compatible."""

from fastapi import APIRouter, Depends, Form, Request

from app.api.deps import get_agent_orchestrator, get_current_user
from app.schemas.agent import AgentExecuteRequest, AgentExecuteResponse
from app.schemas.auth import UserResponse
from app.services.agent_orchestrator import AgentOrchestrator

router = APIRouter()


async def _parse_agent_input(
    deal_id: str | None = Form(None),
    org_name: str | None = Form(None),
    vehicle_type: str | None = Form(None),
    required_quantity: str | None = Form(None),
    city: str | None = Form(None),
    country: str | None = Form(None),
    lead_score: str | None = Form(None),
    requirements: str | None = Form(None),
    quotation_id: str | None = Form(None),
    approval_status: str | None = Form(None),
    order_id: str | None = Form(None),
    customer_name: str | None = Form(None),
) -> AgentExecuteRequest:
    return AgentExecuteRequest(
        deal_id=deal_id,
        org_name=org_name,
        vehicle_type=vehicle_type,
        required_quantity=required_quantity,
        city=city,
        country=country,
        lead_score=lead_score,
        requirements=requirements,
        quotation_id=quotation_id,
        approval_status=approval_status,
        order_id=order_id,
        customer_name=customer_name,
    )


async def _execute_agent(
    agent_name: str,
    request: Request,
    input_data: AgentExecuteRequest,
    orchestrator: AgentOrchestrator,
    user: UserResponse | None,
) -> AgentExecuteResponse:
    request.state.agent_name = agent_name
    return await orchestrator.execute(agent_name, input_data)


@router.post("/marty", response_model=AgentExecuteResponse)
async def execute_marty(
    request: Request,
    input_data: AgentExecuteRequest = Depends(_parse_agent_input),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    user: UserResponse | None = Depends(get_current_user),
) -> AgentExecuteResponse:
    return await _execute_agent("marty", request, input_data, orchestrator, user)


@router.post("/lisa", response_model=AgentExecuteResponse)
async def execute_lisa(
    request: Request,
    input_data: AgentExecuteRequest = Depends(_parse_agent_input),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    user: UserResponse | None = Depends(get_current_user),
) -> AgentExecuteResponse:
    return await _execute_agent("lisa", request, input_data, orchestrator, user)


@router.post("/neil", response_model=AgentExecuteResponse)
async def execute_neil(
    request: Request,
    input_data: AgentExecuteRequest = Depends(_parse_agent_input),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    user: UserResponse | None = Depends(get_current_user),
) -> AgentExecuteResponse:
    return await _execute_agent("neil", request, input_data, orchestrator, user)


@router.post("/paul", response_model=AgentExecuteResponse)
async def execute_paul(
    request: Request,
    input_data: AgentExecuteRequest = Depends(_parse_agent_input),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    user: UserResponse | None = Depends(get_current_user),
) -> AgentExecuteResponse:
    return await _execute_agent("paul", request, input_data, orchestrator, user)


@router.post("/sally", response_model=AgentExecuteResponse)
async def execute_sally(
    request: Request,
    input_data: AgentExecuteRequest = Depends(_parse_agent_input),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    user: UserResponse | None = Depends(get_current_user),
) -> AgentExecuteResponse:
    return await _execute_agent("sally", request, input_data, orchestrator, user)


@router.post("/adam", response_model=AgentExecuteResponse)
async def execute_adam(
    request: Request,
    input_data: AgentExecuteRequest = Depends(_parse_agent_input),
    orchestrator: AgentOrchestrator = Depends(get_agent_orchestrator),
    user: UserResponse | None = Depends(get_current_user),
) -> AgentExecuteResponse:
    return await _execute_agent("adam", request, input_data, orchestrator, user)
