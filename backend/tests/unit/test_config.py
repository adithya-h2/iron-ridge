"""Production config validation tests."""

import os
import pytest


def test_production_rejects_default_secret(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")
    monkeypatch.setenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
    monkeypatch.setenv("ADMIN_PASSWORD", "secure-admin-pass")
    monkeypatch.setenv("AGENT_API_KEY", "prod-agent-key")

    from pydantic_settings import BaseSettings

    # Clear cached settings
    from app.core import config as config_module

    config_module.get_settings.cache_clear()

    with pytest.raises(ValueError, match="SECRET_KEY"):
        config_module.Settings()

    config_module.get_settings.cache_clear()


def test_production_accepts_secure_config(monkeypatch):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost:5432/db")
    monkeypatch.setenv("SECRET_KEY", "a" * 32)
    monkeypatch.setenv("ADMIN_PASSWORD", "secure-admin-pass")
    monkeypatch.setenv("AGENT_API_KEY", "prod-agent-key")

    from app.core import config as config_module

    config_module.get_settings.cache_clear()
    settings = config_module.Settings()
    assert settings.is_production
    config_module.get_settings.cache_clear()
