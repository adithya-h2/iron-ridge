"""Health, readiness, and metrics endpoint tests."""

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client():
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("healthy", "degraded")
    assert "database" in data


@pytest.mark.asyncio
async def test_ready_endpoint(client):
    response = await client.get("/ready")
    assert response.status_code in (200, 503)
    assert "ready" in response.json()


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    response = await client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "uptime_seconds" in data
    assert "requests" in data
