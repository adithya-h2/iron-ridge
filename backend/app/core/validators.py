"""Shared input parsing utilities for agents and API routes."""

from uuid import UUID

from app.core.exceptions import ValidationAppError


def parse_uuid(value: str | None, field_name: str = "id") -> UUID:
    """Parse a required UUID string; raise ValidationAppError on failure."""
    if not value or not str(value).strip():
        raise ValidationAppError(f"{field_name} is required")
    try:
        return UUID(str(value).strip())
    except (ValueError, AttributeError) as exc:
        raise ValidationAppError(
            f"Invalid {field_name}: must be a valid UUID",
            details={"field": field_name, "value": str(value)},
        ) from exc


def parse_uuid_optional(value: str | None) -> UUID | None:
    """Parse an optional UUID string; raise ValidationAppError on invalid format."""
    if value is None or not str(value).strip():
        return None
    try:
        return UUID(str(value).strip())
    except (ValueError, AttributeError) as exc:
        raise ValidationAppError(
            "Invalid deal_id: must be a valid UUID",
            details={"field": "deal_id", "value": str(value)},
        ) from exc


def parse_int_field(
    value: str | int | None,
    field_name: str = "value",
    default: int | None = None,
) -> int:
    """Parse an integer field from form/JSON input."""
    if value is None or (isinstance(value, str) and not value.strip()):
        if default is not None:
            return default
        raise ValidationAppError(f"{field_name} is required")
    try:
        return int(value)
    except (ValueError, TypeError) as exc:
        raise ValidationAppError(
            f"Invalid {field_name}: must be an integer",
            details={"field": field_name, "value": str(value)},
        ) from exc
