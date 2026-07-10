"""Validator unit tests."""

import pytest

from app.core.exceptions import ValidationAppError
from app.core.validators import parse_int_field, parse_uuid, parse_uuid_optional


def test_parse_uuid_valid():
    uid = parse_uuid("550e8400-e29b-41d4-a716-446655440000", "deal_id")
    assert str(uid) == "550e8400-e29b-41d4-a716-446655440000"


def test_parse_uuid_missing():
    with pytest.raises(ValidationAppError, match="deal_id is required"):
        parse_uuid(None, "deal_id")


def test_parse_uuid_invalid():
    with pytest.raises(ValidationAppError, match="Invalid deal_id"):
        parse_uuid("not-a-uuid", "deal_id")


def test_parse_uuid_optional_none():
    assert parse_uuid_optional(None) is None


def test_parse_int_field_default():
    assert parse_int_field(None, "qty", default=1) == 1


def test_parse_int_field_invalid():
    with pytest.raises(ValidationAppError, match="Invalid qty"):
        parse_int_field("abc", "qty")
