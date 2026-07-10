"""Auth service unit tests."""

from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.core.enums import UserRole
from app.core.exceptions import UnauthorizedError, ValidationAppError
from app.schemas.auth import LoginRequest, UserCreate
from app.services.auth import AuthService


@pytest.fixture
def auth_service():
    repo = AsyncMock()
    return AuthService(repo)


@pytest.mark.asyncio
async def test_register_validates_role(auth_service):
    with pytest.raises(ValidationAppError):
        await auth_service.register(UserCreate(email="a@b.com", password="x", role="invalid"))


@pytest.mark.asyncio
async def test_login_invalid_role_in_db(auth_service):
    user = MagicMock()
    user.email = "bad@ironridge.com"
    user.hashed_password = auth_service.user_repo  # placeholder
    user.is_active = True
    user.role = "not-a-real-role"
    user.user_id = uuid4()

    from app.core.security import hash_password

    user.hashed_password = hash_password("secret")
    auth_service.user_repo.get_by_email = AsyncMock(return_value=user)

    with pytest.raises(UnauthorizedError, match="Account configuration error"):
        await auth_service.login(LoginRequest(username="bad@ironridge.com", password="secret"))
