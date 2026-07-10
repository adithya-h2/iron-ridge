"""Authentication routes."""

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_service, require_auth, require_roles
from app.core.enums import UserRole
from app.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.schemas.common import ApiResponse
from app.services.auth import AuthService

router = APIRouter()


@router.post("/login", response_model=ApiResponse[TokenResponse])
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> ApiResponse[TokenResponse]:
    token = await auth_service.login(LoginRequest(username=form_data.username, password=form_data.password))
    return ApiResponse(success=True, data=token)


@router.post("/register", response_model=ApiResponse[UserResponse], status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
    _: UserResponse = Depends(require_roles(UserRole.ADMIN)),
) -> ApiResponse[UserResponse]:
    user = await auth_service.register(data)
    return ApiResponse(success=True, data=user)


@router.get("/me", response_model=ApiResponse[UserResponse])
async def me(user: UserResponse = Depends(require_auth)) -> ApiResponse[UserResponse]:
    return ApiResponse(success=True, data=user)
