"""Authentication integration tests."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_auth_service, get_current_user
from app.core.enums import UserRole
from app.core.exceptions import UnauthorizedError, ValidationAppError
from app.schemas.auth import TokenResponse, UserCreate, UserResponse


@pytest.fixture
def mock_auth_service():
    service = AsyncMock()
    service.login = AsyncMock(return_value=TokenResponse(access_token="valid-token"))
    service.register = AsyncMock(
        return_value=UserResponse(
            user_id=uuid4(),
            email="sales@ironridge.com",
            role=UserRole.SALES.value,
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )
    )
    return service


@pytest.fixture
async def auth_client(mock_auth_service):
    from app.main import app

    app.dependency_overrides[get_auth_service] = lambda: mock_auth_service
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_success(auth_client, mock_auth_service):
    response = await auth_client.post(
        "/auth/login",
        data={"username": "admin@ironridge.com", "password": "secret"},
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["access_token"] == "valid-token"
    mock_auth_service.login.assert_awaited_once()


@pytest.mark.asyncio
async def test_login_bad_password(auth_client, mock_auth_service):
    mock_auth_service.login = AsyncMock(side_effect=UnauthorizedError("Invalid email or password"))
    response = await auth_client.post(
        "/auth/login",
        data={"username": "admin@ironridge.com", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_register_requires_admin(auth_client):
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: UserResponse(
        user_id=uuid4(),
        email="sales@ironridge.com",
        role=UserRole.SALES.value,
        is_active=True,
    )
    response = await auth_client.post(
        "/auth/register",
        json={"email": "new@ironridge.com", "password": "pass123", "role": "sales"},
    )
    assert response.status_code == 403
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_register_admin_success(auth_client, mock_auth_service):
    from app.main import app

    app.dependency_overrides[get_current_user] = lambda: UserResponse(
        user_id=uuid4(),
        email="admin@ironridge.com",
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    response = await auth_client.post(
        "/auth/register",
        json={"email": "sales@ironridge.com", "password": "pass123", "role": "sales"},
    )
    assert response.status_code == 201
    assert response.json()["success"] is True
    app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.asyncio
async def test_protected_route_without_token():
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/customers")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_role_rejected():
    from app.services.auth import AuthService

    repo = AsyncMock()
    service = AuthService(repo)
    with pytest.raises(ValidationAppError, match="Invalid role"):
        await service.register(UserCreate(email="x@y.com", password="pass", role="superuser"))
