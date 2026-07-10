"""Authentication service."""

from datetime import datetime, timezone
from uuid import UUID

from app.core.enums import UserRole
from app.core.exceptions import ConflictError, UnauthorizedError, ValidationAppError
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse


class AuthService:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    @staticmethod
    def _validate_role(role: str) -> str:
        valid_roles = {r.value for r in UserRole if r != UserRole.AGENT}
        if role not in valid_roles:
            raise ValidationAppError(
                f"Invalid role: {role}",
                details={"allowed_roles": sorted(valid_roles)},
            )
        return role

    async def register(self, data: UserCreate) -> UserResponse:
        role = self._validate_role(data.role)
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ConflictError("Email already registered")
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        user = await self.user_repo.create(
            email=data.email,
            hashed_password=hash_password(data.password),
            role=role,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        return UserResponse.model_validate(user)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.username)
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Invalid email or password")
        if not user.is_active:
            raise UnauthorizedError("Account is disabled")
        try:
            role = UserRole(user.role)
        except ValueError as exc:
            raise UnauthorizedError("Account configuration error") from exc
        token = create_access_token(user.email, role, user.user_id)
        return TokenResponse(access_token=token)

    async def get_user(self, user_id: UUID) -> UserResponse:
        user = await self.user_repo.get_by_id_or_raise(user_id)
        return UserResponse.model_validate(user)

    async def ensure_admin_exists(self, email: str, password: str) -> None:
        existing = await self.user_repo.get_by_email(email)
        if existing:
            return
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        await self.user_repo.create(
            email=email,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN.value,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
