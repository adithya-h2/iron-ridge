"""
app/core/config.py

Application configuration loaded from environment variables using Pydantic Settings.

Design decision:
    Pydantic Settings validates all config at startup. If DATABASE_URL is missing
    or malformed, the app refuses to start — fail fast, not fail silently.

    All other modules import `settings` from here. There is exactly ONE settings
    instance in the entire application (singleton via module-level instantiation).
"""

from functools import lru_cache
from typing import Literal

from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Iron Ridge backend configuration.

    Reads from environment variables and .env file automatically.
    All fields are type-validated by Pydantic v2.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore unexpected env vars — prevents startup crashes
    )

    # -----------------------------------------------------------------------
    # Application
    # -----------------------------------------------------------------------
    app_name: str = "Iron Ridge Intelligent Sales Workflow"
    app_env: Literal["development", "staging", "production"] = "development"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"

    # -----------------------------------------------------------------------
    # Server
    # -----------------------------------------------------------------------
    host: str = "0.0.0.0"
    port: int = 8000

    # -----------------------------------------------------------------------
    # Database
    # -----------------------------------------------------------------------
    database_url: str  # Required — must be postgresql+asyncpg://...

    # SQLAlchemy async engine pool settings
    db_pool_size: int = 5          # Connections kept alive in pool
    db_max_overflow: int = 10      # Extra connections allowed above pool_size
    db_pool_timeout: int = 30      # Seconds to wait for a connection
    db_pool_recycle: int = 1800    # Recycle connections after 30 min (avoids stale)
    db_echo: bool = False          # Set True in dev to log all SQL queries

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """
        Ensure the URL uses the asyncpg driver.

        SQLAlchemy's async engine requires postgresql+asyncpg://.
        A plain postgresql:// URL will cause a 'This method is not available
        in an async context' error at runtime.
        """
        if not v.startswith("postgresql+asyncpg://"):
            raise ValueError(
                "DATABASE_URL must start with 'postgresql+asyncpg://'. "
                "Standard 'postgresql://' is not compatible with async SQLAlchemy."
            )
        return v

    # -----------------------------------------------------------------------
    # JWT Authentication
    # -----------------------------------------------------------------------
    secret_key: str = "CHANGE_ME_IN_PRODUCTION"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # -----------------------------------------------------------------------
    # AI Providers
    # -----------------------------------------------------------------------
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    ai_provider: Literal["openai", "anthropic"] = "openai"

    # -----------------------------------------------------------------------
    # n8n (external orchestrator)
    # -----------------------------------------------------------------------
    n8n_webhook_base_url: str = ""

    # -----------------------------------------------------------------------
    # Slack (human-in-the-loop notifications ONLY)
    # -----------------------------------------------------------------------
    slack_bot_token: str = ""
    slack_approval_channel: str = "#sales-approvals"

    # -----------------------------------------------------------------------
    # Redis (optional caching layer)
    # -----------------------------------------------------------------------
    redis_url: str = ""

    # -----------------------------------------------------------------------
    # CORS
    # -----------------------------------------------------------------------
    allowed_origins: str = "http://localhost:3000"

    @property
    def allowed_origins_list(self) -> list[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """True when running in production environment."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """True when running in development environment."""
        return self.app_env == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Return the cached Settings singleton.

    Using @lru_cache ensures Settings() is instantiated exactly once.
    This is the FastAPI-recommended pattern for configuration — avoids
    re-reading .env on every request.

    Usage:
        from app.core.config import get_settings
        settings = get_settings()

    In FastAPI dependencies:
        settings: Settings = Depends(get_settings)
    """
    return Settings()


# Module-level singleton — import this directly for convenience
settings: Settings = get_settings()
