"""Pytest configuration and shared fixtures."""

import os
import sys
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("DATABASE_SSL", "false")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest")


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
