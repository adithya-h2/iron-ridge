"""Health, readiness, and metrics endpoints."""

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.services.health import HealthService

router = APIRouter()


def get_health_service() -> HealthService:
    return HealthService()


@router.get("/health", tags=["System"])
async def health_check(
    service: HealthService = Depends(get_health_service),
) -> JSONResponse:
    """Liveness probe — app is running."""
    content = await service.get_health()
    code = status.HTTP_200_OK if content["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=code, content=content)


@router.get("/ready", tags=["System"])
async def readiness_check(
    service: HealthService = Depends(get_health_service),
) -> JSONResponse:
    """Readiness probe — dependencies available."""
    result = await service.get_readiness()
    code = status.HTTP_200_OK if result["ready"] else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(status_code=code, content=result)


@router.get("/metrics", tags=["System"])
async def metrics(
    service: HealthService = Depends(get_health_service),
) -> JSONResponse:
    """Operational metrics snapshot."""
    if not settings.metrics_enabled:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Metrics disabled"})
    return JSONResponse(status_code=status.HTTP_200_OK, content=await service.get_metrics())
