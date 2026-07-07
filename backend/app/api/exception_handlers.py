"""Global FastAPI exception handlers."""

import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions import AppError
from app.schemas.common import ApiResponse, ErrorDetail

logger = logging.getLogger(__name__)


def _request_id(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


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
        logger.warning(
            "Application error",
            extra={"error_code": exc.code, "error_message": exc.message, "request_id": _request_id(request)},
        )
        return _error_response(request, exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _error_response(
            request,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VALIDATION_ERROR",
            "Request validation failed",
            {"errors": exc.errors()},
        )

    @app.exception_handler(SQLAlchemyError)
    async def database_error_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
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
