"""Dashboard API routes."""

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_dashboard_service, require_auth
from app.core.config import settings
from app.core.exceptions import ForbiddenError
from app.schemas.auth import UserResponse
from app.schemas.common import ApiResponse
from app.schemas.dashboard import (
    DashboardAgentsResponse,
    DashboardApprovalsResponse,
    DashboardOrdersResponse,
    DashboardPipelineResponse,
    DashboardRevenueResponse,
    DashboardSummaryResponse,
)
from app.services.dashboard import DashboardService

router = APIRouter()


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _check_dashboard_enabled() -> None:
    if not settings.feature_dashboard:
        raise ForbiddenError("Dashboard API is disabled")


@router.get("/summary", response_model=ApiResponse[DashboardSummaryResponse])
async def dashboard_summary(
    request: Request,
    service: DashboardService = Depends(get_dashboard_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[DashboardSummaryResponse]:
    _check_dashboard_enabled()
    data = await service.get_summary()
    return ApiResponse(success=True, data=data, request_id=_rid(request))


@router.get("/pipeline", response_model=ApiResponse[DashboardPipelineResponse])
async def dashboard_pipeline(
    request: Request,
    service: DashboardService = Depends(get_dashboard_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[DashboardPipelineResponse]:
    _check_dashboard_enabled()
    data = await service.get_pipeline()
    return ApiResponse(success=True, data=data, request_id=_rid(request))


@router.get("/agents", response_model=ApiResponse[DashboardAgentsResponse])
async def dashboard_agents(
    request: Request,
    service: DashboardService = Depends(get_dashboard_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[DashboardAgentsResponse]:
    _check_dashboard_enabled()
    data = await service.get_agents()
    return ApiResponse(success=True, data=data, request_id=_rid(request))


@router.get("/revenue", response_model=ApiResponse[DashboardRevenueResponse])
async def dashboard_revenue(
    request: Request,
    service: DashboardService = Depends(get_dashboard_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[DashboardRevenueResponse]:
    _check_dashboard_enabled()
    data = await service.get_revenue()
    return ApiResponse(success=True, data=data, request_id=_rid(request))


@router.get("/orders", response_model=ApiResponse[DashboardOrdersResponse])
async def dashboard_orders(
    request: Request,
    service: DashboardService = Depends(get_dashboard_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[DashboardOrdersResponse]:
    _check_dashboard_enabled()
    data = await service.get_orders()
    return ApiResponse(success=True, data=data, request_id=_rid(request))


@router.get("/approvals", response_model=ApiResponse[DashboardApprovalsResponse])
async def dashboard_approvals(
    request: Request,
    service: DashboardService = Depends(get_dashboard_service),
    _: UserResponse = Depends(require_auth),
) -> ApiResponse[DashboardApprovalsResponse]:
    _check_dashboard_enabled()
    data = await service.get_approvals()
    return ApiResponse(success=True, data=data, request_id=_rid(request))
