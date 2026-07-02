"""
app/database/session.py

Async SQLAlchemy session factory and FastAPI dependency.

Responsibility:
    - Creates `AsyncSession` instances per request
    - Provides `get_db_session` — a FastAPI dependency that manages
      session lifecycle (open → yield → commit/rollback → close)

Design decisions:
    1. `AsyncSession` (not `Session`) — required for async endpoints.

    2. `expire_on_commit=False` — prevents SQLAlchemy from expiring
       object attributes after commit, which would trigger additional
       SELECT queries when accessing relationships after a commit.
       In an async context this is especially important because lazy
       loading is NOT supported (it requires a sync I/O call).

    3. `autoflush=False` — we flush explicitly. This gives us control
       over when SQL hits the DB within a transaction.

    4. The `get_db_session` generator:
       - Opens session
       - Yields to the route handler
       - Commits on success
       - Rolls back on any exception
       - Always closes the session (releases connection back to pool)

    5. `async_sessionmaker` (SQLAlchemy 2.x) replaces the older
       `sessionmaker` call pattern and is compatible with async engines.
"""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.database import engine

logger = logging.getLogger(__name__)

# Session factory — creates new AsyncSession objects bound to the shared engine.
# Instantiated once; each call to AsyncSessionFactory() creates a new session.
AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # See module docstring — prevents lazy-load errors
    autoflush=False,         # Explicit flush control
    autocommit=False,        # We commit manually inside the dependency
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a managed async database session.

    Yields an `AsyncSession` that is automatically committed on success
    and rolled back on any unhandled exception. The session is always
    closed after the request completes, returning the connection to the pool.

    Usage in routes:
        from fastapi import Depends
        from sqlalchemy.ext.asyncio import AsyncSession
        from app.database.session import get_db_session

        @router.get("/example")
        async def example_route(db: AsyncSession = Depends(get_db_session)):
            ...

    Usage in repositories (via service → repository DI):
        All repositories receive an AsyncSession injected via Depends().
        They NEVER create their own sessions.

    Yields:
        AsyncSession: Active database session for the current request.

    Raises:
        Re-raises any exception after rolling back the transaction.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
            logger.debug("Database session committed successfully.")
        except Exception as exc:
            await session.rollback()
            logger.error(
                "Database session rolled back due to exception.",
                extra={"error": str(exc)},
                exc_info=True,
            )
            raise
        finally:
            await session.close()
            logger.debug("Database session closed.")
