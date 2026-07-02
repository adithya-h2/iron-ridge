"""
migrations/env.py

Alembic migration environment — configured for async SQLAlchemy.

Critical design decisions:
    1. ASYNC engine — standard Alembic uses sync. We must use
       `run_async_migrations()` with `AsyncEngine` to be compatible
       with our async SQLAlchemy setup.

    2. DATABASE_URL from environment — never hardcoded.
       Reads from settings (which reads from .env).

    3. `target_metadata = Base.metadata` — Alembic compares this against
       the live database to generate migration scripts.
       Base.metadata is only complete if ALL models have been imported,
       which is why `app.database.base` imports every model.

    4. `compare_type=True` — Alembic will detect column type changes
       (e.g., VARCHAR(100) → VARCHAR(255)) and include them in autogenerate.

    5. `include_schemas=True` — supports PostgreSQL schemas (e.g., 'public').
"""

import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

# Ensure the backend root is on the Python path
# so `from app.xxx import yyy` works from migrations/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.core.config import settings
from app.database.base import Base  # noqa: F401 — imports Base + all models

# ---------------------------------------------------------------------------
# Alembic Config Object
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override the URL from environment — ignores the dummy in alembic.ini
config.set_main_option("sqlalchemy.url", settings.database_url)

# This is what Alembic uses to compare against live DB schema
target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline Migrations (generates SQL without a live connection)
# ---------------------------------------------------------------------------

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    Generates SQL scripts without connecting to the database.
    Useful for reviewing migrations before applying them.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        include_schemas=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online Migrations (applies changes to live database)
# ---------------------------------------------------------------------------

def do_run_migrations(connection) -> None:
    """Configure Alembic context and run migrations against a live connection."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,       # Detect column type changes
        include_schemas=True,    # Support PostgreSQL schemas
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Create an async engine and run migrations.

    Must use async engine (asyncpg) because our models are defined
    for async SQLAlchemy. Using a sync engine here would cause
    metadata mismatches.
    """
    connectable = create_async_engine(settings.database_url)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migrations — runs the async coroutine."""
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
