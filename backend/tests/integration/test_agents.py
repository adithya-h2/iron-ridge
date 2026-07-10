"""Agent route integration tests — JSON + form dual-parser."""

from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_agent_orchestrator
from app.schemas.agent import AgentExecuteResponse


@pytest.fixture
def mock_orchestrator():
    orch = AsyncMock()
    orch.execute = AsyncMock(
        return_value=AgentExecuteResponse(
            deal_id="550e8400-e29b-41d4-a716-446655440000",
            status="LEAD",
            current_agent="MARTY",
            lead_score=85,
        )
    )
    return orch


@pytest.fixture
async def agent_client(mock_orchestrator):
    from app.main import app

    app.dependency_overrides[get_agent_orchestrator] = lambda: mock_orchestrator
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_marty_accepts_json(agent_client, mock_orchestrator):
    response = await agent_client.post(
        "/agents/marty",
        json={"org_name": "City Fire Dept", "vehicle_type": "Ambulance"},
    )
    assert response.status_code == 200
    mock_orchestrator.execute.assert_awaited_once()
    call_args = mock_orchestrator.execute.call_args[0][1]
    assert call_args.org_name == "City Fire Dept"


@pytest.mark.asyncio
async def test_marty_accepts_form(agent_client, mock_orchestrator):
    response = await agent_client.post(
        "/agents/marty",
        data={"org_name": "County EMS", "city": "Denver"},
    )
    assert response.status_code == 200
    call_args = mock_orchestrator.execute.call_args[0][1]
    assert call_args.org_name == "County EMS"


@pytest.mark.asyncio
async def test_lisa_missing_deal_id_returns_422(agent_client, mock_orchestrator):
    from app.core.exceptions import ValidationAppError

    mock_orchestrator.execute = AsyncMock(
        side_effect=ValidationAppError("deal_id is required for Lisa agent")
    )
    response = await agent_client.post("/agents/lisa", json={"org_name": "Test"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_uuid_returns_422(agent_client, mock_orchestrator):
    from app.core.exceptions import ValidationAppError

    mock_orchestrator.execute = AsyncMock(
        side_effect=ValidationAppError("Invalid deal_id: must be a valid UUID")
    )
    response = await agent_client.post(
        "/agents/neil",
        json={"deal_id": "not-a-uuid", "vehicle_type": "Ambulance"},
    )
    assert response.status_code == 422
