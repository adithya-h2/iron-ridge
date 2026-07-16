"""Production config validation tests."""

import os
import pytest


def test_production_rejects_default_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")
    monkeypatch.setenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
    monkeypatch.setenv("ADMIN_PASSWORD", "secure-admin-pass")
    monkeypatch.setenv("AGENT_API_KEY", "prod-agent-key")

    from app.core.config import Settings

    with pytest.raises(ValueError, match="SECRET_KEY"):
        Settings()


def test_production_accepts_secure_config(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ADMIN_PASSWORD", "secure-admin-pass")
    monkeypatch.setenv("AGENT_API_KEY", "prod-agent-key")

    from app.core.config import Settings

    settings = Settings()
    assert settings.is_production


def test_database_url_normalizes_postgres_scheme(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@localhost:5432/db")

    from app.core.config import Settings

    settings = Settings()
    assert settings.database_url == "postgresql+asyncpg://u:p@localhost:5432/db"
