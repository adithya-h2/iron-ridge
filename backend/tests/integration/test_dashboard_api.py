"""Dashboard API integration tests."""

from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_current_user, get_dashboard_service
from app.schemas.auth import UserResponse
from app.schemas.dashboard import (
    DashboardAgentsResponse,
    DashboardApprovalsResponse,
    DashboardOrdersResponse,
    DashboardPipelineResponse,
    DashboardRevenueResponse,
    DashboardSummaryResponse,
    PipelineStageCount,
)


@pytest.fixture
def mock_user():
    return UserResponse(user_id=uuid4(), email="admin@ironridge.com", role="admin", is_active=True)


@pytest.fixture
def mock_dashboard_service():
    service = AsyncMock()
    service.get_summary = AsyncMock(
        return_value=DashboardSummaryResponse(
            total_deals=10,
            deals_by_status=[PipelineStageCount(status="LEAD", count=5)],
            total_revenue=Decimal("100000"),
            pending_approvals=2,
            active_orders=3,
        )
    )
    service.get_pipeline = AsyncMock(return_value=DashboardPipelineResponse(stages=[]))
    service.get_agents = AsyncMock(return_value=DashboardAgentsResponse(agents=[]))
    service.get_revenue = AsyncMock(
        return_value=DashboardRevenueResponse(monthly=[], total=Decimal("0"))
    )
    service.get_orders = AsyncMock(
        return_value=DashboardOrdersResponse(by_status=[], recent=[])
    )
    service.get_approvals = AsyncMock(
        return_value=DashboardApprovalsResponse(by_decision=[], pending=[])
    )
    return service


@pytest.fixture
async def client(mock_user, mock_dashboard_service):
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_dashboard_service] = lambda: mock_dashboard_service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_dashboard_summary(client):
    response = await client.get("/dashboard/summary")
    assert response.status_code == 200
    assert response.json()["data"]["total_deals"] == 10


@pytest.mark.asyncio
async def test_dashboard_pipeline(client):
    response = await client.get("/dashboard/pipeline")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_dashboard_agents(client):
    response = await client.get("/dashboard/agents")
    assert response.status_code == 200
