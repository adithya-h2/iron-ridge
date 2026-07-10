"""Additional API endpoint integration tests."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_current_user, get_customer_service, get_requirement_service
from app.core.enums import UserRole
from app.schemas.auth import UserResponse
from app.schemas.common import PaginatedResponse
from app.schemas.customer import CustomerResponse
from app.schemas.requirement import RequirementResponse


def _admin_user() -> UserResponse:
    return UserResponse(
        user_id=uuid4(),
        email="admin@ironridge.com",
        role=UserRole.ADMIN.value,
        is_active=True,
    )


@pytest.fixture
async def api_client():
    from app.main import app

    app.dependency_overrides[get_current_user] = _admin_user
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_customers_list_with_auth(api_client):
    from app.main import app

    mock_service = AsyncMock()
    mock_service.list = AsyncMock(
        return_value=PaginatedResponse(items=[], total=0, page=1, page_size=20, pages=0)
    )
    app.dependency_overrides[get_customer_service] = lambda: mock_service

    response = await api_client.get("/customers")
    assert response.status_code == 200
    assert response.json()["success"] is True


@pytest.mark.asyncio
async def test_requirements_list_by_deal(api_client):
    from app.main import app

    deal_id = uuid4()
    mock_service = AsyncMock()
    mock_service.list_by_deal = AsyncMock(return_value=[])
    app.dependency_overrides[get_requirement_service] = lambda: mock_service

    response = await api_client.get(f"/requirements/deal/{deal_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_service.list_by_deal.assert_awaited_once_with(deal_id)


@pytest.mark.asyncio
async def test_health_sanitized_error_in_production(monkeypatch):
    from app.main import app
    from app.core.config import settings

    monkeypatch.setattr(settings, "app_env", "production")
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")
    if response.status_code == 503:
        db = response.json().get("database", {})
        assert db.get("error") == "Database connection failed"
