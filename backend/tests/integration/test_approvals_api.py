"""Approval alias endpoint tests."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_approval_service, get_current_user
from app.core.enums import ApprovalStatus
from app.schemas.approval import ApprovalResponse
from app.schemas.auth import UserResponse


@pytest.fixture
def mock_user():
    return UserResponse(user_id=uuid4(), email="admin@ironridge.com", role="admin", is_active=True)


@pytest.fixture
def mock_approval_service():
    service = AsyncMock()
    approval_id = uuid4()
    quotation_id = uuid4()
    service.request_approval = AsyncMock(
        return_value=ApprovalResponse(
            approval_id=approval_id,
            quotation_id=quotation_id,
            decision=ApprovalStatus.PENDING.value,
        )
    )
    service.decide = AsyncMock(
        return_value=ApprovalResponse(
            approval_id=approval_id,
            quotation_id=quotation_id,
            decision=ApprovalStatus.APPROVED.value,
        )
    )
    return service


@pytest.fixture
async def client(mock_user, mock_approval_service):
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_approval_service] = lambda: mock_approval_service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_request_approval_body(client, mock_approval_service):
    quotation_id = uuid4()
    response = await client.post("/approvals/request", json={"quotation_id": str(quotation_id)})
    assert response.status_code == 201
    mock_approval_service.request_approval.assert_awaited_once()


@pytest.mark.asyncio
async def test_approve_endpoint(client, mock_approval_service):
    approval_id = uuid4()
    response = await client.post(f"/approvals/{approval_id}/approve")
    assert response.status_code == 200
    mock_approval_service.decide.assert_awaited_once()


@pytest.mark.asyncio
async def test_reject_endpoint(client, mock_approval_service):
    approval_id = uuid4()
    response = await client.post(f"/approvals/{approval_id}/reject")
    assert response.status_code == 200
    mock_approval_service.decide.assert_awaited_once()
