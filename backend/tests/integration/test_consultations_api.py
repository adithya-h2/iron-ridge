"""Integration tests for consultations API."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4, UUID

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_consultation_service, get_current_user
from app.core.enums import UserRole
from app.schemas.auth import UserResponse
from app.schemas.consultation import ConsultationCreateSuccessResponse, ConsultationRequestResponse
from app.core.config import settings


def _admin_user() -> UserResponse:
    return UserResponse(
        user_id=uuid4(),
        email="admin@ironridge.com",
        role=UserRole.ADMIN.value,
        is_active=True,
    )


@pytest.fixture
def enable_webhook_url(monkeypatch):
    monkeypatch.setattr(settings, "n8n_webhook_url", "https://n8n.example.com/webhook/consultation")
    monkeypatch.setattr(settings, "n8n_timeout_seconds", 5)


@pytest.fixture
async def unauth_client():
    from app.main import app
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def auth_client():
    from app.main import app
    app.dependency_overrides[get_current_user] = _admin_user
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_consultation_missing_fields(unauth_client):
    response = await unauth_client.post(
        "/api/v1/consultations",
        json={
            "organization_name": "Seattle Fire"
        }
    )
    # Validation error must return 400 Bad Request
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_create_consultation_invalid_email_phone(unauth_client):
    response = await unauth_client.post(
        "/api/v1/consultations",
        json={
            "organization_name": "Seattle Fire",
            "organization_type": "Fire Department",
            "contact_person": "Chief Miller",
            "business_email": "invalid-email",
            "phone_number": "12345",  # invalid format
            "country": "USA",
            "state": "WA",
            "city": "Seattle",
            "vehicle_category": "Fire Engine",
            "estimated_quantity": "2-5",
            "purchase_timeline": "Within 3 Months",
            "consent": True
        }
    )
    assert response.status_code == 400
    assert response.json()["success"] is False


@pytest.mark.asyncio
async def test_create_consultation_success(unauth_client, enable_webhook_url):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "ok"

    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=mock_response)
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    payload = {
        "organization_name": "Seattle Fire",
        "organization_type": "Fire Department",
        "department": "Logistics",
        "website": "https://seattle.gov",
        "contact_person": "Chief Miller",
        "job_title": "Chief",
        "business_email": "miller@seattle.gov",
        "phone_number": "2065550199",
        "preferred_contact_method": "Email",
        "country": "USA",
        "state": "WA",
        "city": "Seattle",
        "vehicle_category": "Fire Engine",
        "estimated_quantity": "2-5",
        "purchase_timeline": "Within 3 Months",
        "requirement_summary": "Looking for two fire engine apparatuses.",
        "consent": True
    }

    with patch("app.services.consultation_service.httpx.AsyncClient", return_value=mock_client):
        response = await unauth_client.post(
            "/api/v1/consultations",
            json=payload
        )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "success"
    assert "consultation_id" in body
    assert body["message"] == "Consultation request submitted successfully."

    # Verify webhook mock was called
    mock_client.post.assert_awaited_once()
    post_args = mock_client.post.await_args
    assert post_args.args[0] == "https://n8n.example.com/webhook/consultation"
    webhook_payload = post_args.kwargs["json"]
    assert webhook_payload["organization_name"] == "Seattle Fire"
    assert webhook_payload["email"] == "miller@seattle.gov"
    assert webhook_payload["phone"] == "2065550199"


@pytest.mark.asyncio
async def test_create_consultation_webhook_fails_does_not_fail_api(unauth_client, enable_webhook_url):
    # Webhook raises exception
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(side_effect=Exception("Connection timed out"))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)

    payload = {
        "organization_name": "Seattle Fire",
        "organization_type": "Fire Department",
        "contact_person": "Chief Miller",
        "business_email": "miller@seattle.gov",
        "phone_number": "2065550199",
        "country": "USA",
        "state": "WA",
        "city": "Seattle",
        "vehicle_category": "Fire Engine",
        "estimated_quantity": "2-5",
        "purchase_timeline": "Within 3 Months",
        "consent": True
    }

    with patch("app.services.consultation_service.httpx.AsyncClient", return_value=mock_client):
        response = await unauth_client.post(
            "/api/v1/consultations",
            json=payload
        )

    # API MUST succeed with 201 even when the webhook fails!
    assert response.status_code == 201
    assert response.json()["status"] == "success"


@pytest.mark.asyncio
async def test_get_consultation_unauthorized(unauth_client):
    c_id = uuid4()
    response = await unauth_client.get(f"/api/v1/consultations/{c_id}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_consultation_not_found(auth_client):
    c_id = uuid4()
    response = await auth_client.get(f"/api/v1/consultations/{c_id}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_get_consultation_success(auth_client, enable_webhook_url):
    # Create a consultation first (using the public route)
    mock_client = AsyncMock()
    mock_client.post = AsyncMock(return_value=MagicMock(status_code=200))
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = MagicMock()

    payload = {
        "organization_name": "WA EMS",
        "organization_type": "EMS Provider",
        "contact_person": "Dr. Smith",
        "business_email": "smith@waems.org",
        "phone_number": "2065550111",
        "country": "USA",
        "state": "WA",
        "city": "Olympia",
        "vehicle_category": "Ambulance",
        "estimated_quantity": "1",
        "purchase_timeline": "Immediate",
        "consent": True
    }

    with patch("app.services.consultation_service.httpx.AsyncClient", return_value=mock_client):
        create_res = await auth_client.post(
            "/api/v1/consultations",
            json=payload
        )
    assert create_res.status_code == 201
    consultation_id = create_res.json()["consultation_id"]

    # Now retrieve it
    get_res = await auth_client.get(f"/api/v1/consultations/{consultation_id}")
    assert get_res.status_code == 200
    body = get_res.json()
    assert body["success"] is True
    assert body["data"]["organization_name"] == "WA EMS"
    assert body["data"]["status"] == "PENDING_VALIDATION"
    assert body["data"]["lead_score"] is None


@pytest.mark.asyncio
async def test_list_consultations_unauthorized(unauth_client):
    response = await unauth_client.get("/api/v1/consultations")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_consultations_success(auth_client):
    response = await auth_client.get("/api/v1/consultations")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "items" in body["data"]
    assert "total" in body["data"]
