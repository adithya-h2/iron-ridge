"""Security utility unit tests."""

from uuid import uuid4

from app.core.enums import UserRole
from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hashing():
    hashed = hash_password("secret123")
    assert verify_password("secret123", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_roundtrip():
    user_id = uuid4()
    token = create_access_token("test@example.com", UserRole.ADMIN, user_id)
    payload = decode_access_token(token)
    assert payload["sub"] == "test@example.com"
    assert payload["role"] == "admin"
    assert payload["user_id"] == str(user_id)
