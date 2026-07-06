"""
app/database/database.py

SQLAlchemy async engine and declarative Base.

Responsibility:
    - Creates and owns the async engine (connection pool to Supabase PostgreSQL)
    - Exports `Base` — the superclass for all SQLAlchemy ORM models
    - Exports `engine` — used by session.py and for health checks

Design decisions:
    1. `create_async_engine` — mandatory for async FastAPI endpoints.
       Blocking sync engine would deadlock async event loops.

    2. Pool settings come from config — tuned for Supabase connection limits.
       Supabase free tier: max 60 connections.
       pool_size=5, max_overflow=10 → max 15 connections, safe margin.

    3. `NullPool` is intentionally NOT used here (it's for serverless/Lambda
       where you can't keep connections alive). We have a persistent server.

    4. `echo=settings.db_echo` — shows SQL in logs during development only.
       NEVER enable in production (leaks query data into logs).
"""

import logging

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """
    Declarative base class for all SQLAlchemy ORM models.

    All model classes in app/models/ inherit from this.
    SQLAlchemy uses this to track the metadata (table definitions)
    needed by Alembic for migrations.

    Usage:
        from app.database.database import Base

        class Customer(Base):
            __tablename__ = "customers"
            ...
    """
    pass


def create_engine() -> AsyncEngine:
    """
    Build and return the SQLAlchemy async engine.

    Called once at application startup (not per-request).
    The engine manages the connection pool to Supabase PostgreSQL.

    Returns:
        AsyncEngine: The configured async database engine.
    """
    logger.info(
        "Creating async database engine",
        extra={"pool_size": settings.db_pool_size, "max_overflow": settings.db_max_overflow},
    )

    return create_async_engine(
        settings.database_url,
        echo=settings.db_echo,               # Log SQL only in dev
        pool_size=settings.db_pool_size,      # Persistent connections in pool
        max_overflow=settings.db_max_overflow, # Burst connections above pool_size
        pool_timeout=settings.db_pool_timeout, # Wait N seconds for a free connection
        pool_recycle=settings.db_pool_recycle, # Recycle connections to avoid TCP timeouts
        pool_pre_ping=True,                    # Verify connection alive before using it
	connect_args={
		"statement_cache_size": 0,
	},
        # pool_pre_ping prevents "server closed connection unexpectedly" errors
        # that happen after Supabase pauses an idle connection.
    )


# Module-level engine singleton.
# Instantiated once when this module is first imported.
# Shared across all requests via the session factory in session.py.
engine: AsyncEngine = create_engine()
