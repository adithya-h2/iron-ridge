"""Global FastAPI exception handlers."""

import logging
from typing import Any
from uuid import UUID

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.exceptions import AppError
from app.core.log_context import set_log_context
from app.database.session import AsyncSessionFactory
from app.repositories.workflow_execution_state import WorkflowExecutionStateRepository
from app.schemas.common import ApiResponse, ErrorDetail
from app.services.workflow_retry import WorkflowRetryService

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def _extract_deal_id(request: Request) -> UUID | None:
    deal_id = getattr(request.state, "deal_id", None)
    if deal_id:
        try:
            return UUID(str(deal_id))
        except ValueError:
            return None
    return None


async def _record_agent_failure(request: Request, error: str) -> None:
    if not settings.feature_retry_tracking:
        return
    if not request.url.path.startswith("/agents/"):
        return
    deal_id = _extract_deal_id(request)
    if deal_id is None:
        return
    try:
        async with AsyncSessionFactory() as session:
            await WorkflowRetryService(WorkflowExecutionStateRepository(session)).record_failure(
                deal_id, error
            )
            await session.commit()
    except Exception as exc:
        logger.warning("Failed to record workflow retry state", extra={"error": str(exc)})


def _error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    body = ApiResponse(
        success=False,
        data=None,
        error=ErrorDetail(code=code, message=message, details=details or {}),
        request_id=_request_id(request),
    )
    return JSONResponse(status_code=status_code, content=body.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        set_log_context(deal_id=getattr(request.state, "deal_id", None))
        await _record_agent_failure(request, exc.message)
        logger.warning(
            "Application error",
            extra={"error_code": exc.code, "error_message": exc.message, "request_id": _request_id(request)},
        )
        return _error_response(request, exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        details: dict[str, Any] = {}
        if not settings.is_production:
            errors = []
            for err in exc.errors():
                err_copy = dict(err)
                if "ctx" in err_copy and isinstance(err_copy["ctx"], dict):
                    err_copy["ctx"] = {
                        k: str(v) if isinstance(v, Exception) else v
                        for k, v in err_copy["ctx"].items()
                    }
                errors.append(err_copy)
            details["errors"] = errors
        
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        if request.url.path.startswith("/api/v1/consultations"):
            status_code = status.HTTP_400_BAD_REQUEST
            
        return _error_response(
            request,
            status_code,
            "VALIDATION_ERROR",
            "Request validation failed",
            details,
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
        await _record_agent_failure(request, str(exc))
        logger.warning(
            "Value error",
            extra={"error": str(exc), "request_id": _request_id(request)},
        )
        return _error_response(
            request,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VALIDATION_ERROR",
            str(exc) or "Invalid input value",
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        await _record_agent_failure(request, "Database error")
        logger.error(
            "Database error",
            extra={"error": str(exc), "request_id": _request_id(request)},
            exc_info=True,
        )
        return _error_response(
            request,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "DATABASE_ERROR",
            "A database error occurred",
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        await _record_agent_failure(request, str(exc))
        logger.error(
            "Unhandled error",
            extra={"error": str(exc), "request_id": _request_id(request)},
            exc_info=True,
        )
        return _error_response(
            request,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
            "An unexpected error occurred",
        )
