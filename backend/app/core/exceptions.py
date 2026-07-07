"""Application exception hierarchy."""

from typing import Any


class AppError(Exception):
    """Base application error."""

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(message)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="NOT_FOUND", status_code=404, details=details)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="CONFLICT", status_code=409, details=details)


class InvalidTransitionError(ConflictError):
    def __init__(self, message: str = "Invalid status transition", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, details=details)
        self.code = "INVALID_TRANSITION"


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="UNAUTHORIZED", status_code=401, details=details)


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="FORBIDDEN", status_code=403, details=details)


class ValidationAppError(AppError):
    def __init__(self, message: str = "Validation error", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="VALIDATION_ERROR", status_code=422, details=details)


class DatabaseError(AppError):
    def __init__(self, message: str = "Database error", details: dict[str, Any] | None = None) -> None:
        super().__init__(message, code="DATABASE_ERROR", status_code=500, details=details)
