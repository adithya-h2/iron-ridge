"""
app/database/database.py

SQLAlchemy async engine and declarative Base.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Declarative base class for all SQLAlchemy ORM models."""
    pass


def _connect_args() -> dict:
    """asyncpg connect_args — SSL required for Supabase from cloud hosts."""
    args: dict = {"statement_cache_size": 0}
    if settings.database_ssl:
        args["ssl"] = "require"
    return args


def create_engine() -> AsyncEngine:
    """Build and return the SQLAlchemy async engine."""
    logger.info(
        "Creating async database engine",
        extra={
            "pool_size": settings.db_pool_size,
            "max_overflow": settings.db_max_overflow,
            "database_ssl": settings.database_ssl,
        },
    )

    return create_async_engine(
        settings.database_url,
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
        pool_pre_ping=True,
        connect_args=_connect_args(),
    )


engine: AsyncEngine = create_engine()
