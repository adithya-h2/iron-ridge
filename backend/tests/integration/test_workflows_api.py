"""Workflow API integration tests."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_current_user, get_workflow_status_service
from app.schemas.auth import UserResponse
from app.schemas.workflow import WorkflowStatusResponse, WorkflowTimelineResponse


@pytest.fixture
def mock_user():
    return UserResponse(
        user_id=uuid4(),
        email="test@ironridge.com",
        role="admin",
        is_active=True,
    )


@pytest.fixture
def mock_workflow_service():
    service = AsyncMock()
    deal_id = uuid4()
    service.get_status = AsyncMock(
        return_value=WorkflowStatusResponse(
            deal_id=deal_id,
            workflow_id=uuid4(),
            current_agent="LISA",
            current_status="QUALIFIED",
            progress_percentage=25,
        )
    )
    service.get_timeline = AsyncMock(
        return_value=WorkflowTimelineResponse(
            deal_id=deal_id,
            events=[],
            total=0,
            page=1,
            page_size=20,
            pages=1,
        )
    )
    return service


@pytest.fixture
async def client(mock_user, mock_workflow_service):
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_workflow_status_service] = lambda: mock_workflow_service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_workflow_status(client, mock_workflow_service):
    deal_id = mock_workflow_service.get_status.return_value.deal_id
    response = await client.get(f"/api/v1/workflows/{deal_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["current_status"] == "QUALIFIED"


@pytest.mark.asyncio
async def test_get_workflow_timeline(client, mock_workflow_service):
    deal_id = mock_workflow_service.get_timeline.return_value.deal_id
    response = await client.get(f"/api/v1/workflows/{deal_id}/timeline")
    assert response.status_code == 200
    assert response.json()["data"]["events"] == []
