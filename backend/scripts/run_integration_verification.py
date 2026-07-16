"""
Iron Ridge integration verification runner (Phases 5-13 evidence collection).
Does NOT print secrets. Run from backend/: python scripts/run_integration_verification.py
"""
from __future__ import annotations

import asyncio
import json
import sys
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

# Ensure backend root on path
sys.path.insert(0, ".")

from app.core.config import settings
from app.database.session import AsyncSessionFactory

BASE = "http://localhost:8000"
UNIQUE = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:8]
RESULTS: dict[str, Any] = {"unique_id": UNIQUE, "phases": {}}


def _headers() -> dict[str, str]:
    h: dict[str, str] = {"Content-Type": "application/json"}
    if settings.agent_api_key and "your-agent" not in settings.agent_api_key:
        h["X-API-KEY"] = settings.agent_api_key
    return h


async def phase5_health(client: httpx.AsyncClient) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for path in ("/health", "/ready", "/metrics", "/docs"):
        try:
            r = await client.get(f"{BASE}{path}", timeout=15.0)
            out[path] = {"status": r.status_code, "ok": r.status_code < 400}
            if path == "/health":
                out[path]["body"] = r.json()
        except Exception as exc:
            out[path] = {"status": None, "ok": False, "error": str(exc)}
    return out


async def phase6_lead_intake(client: httpx.AsyncClient) -> dict[str, Any]:
    payload = {
        "source": "WEBSITE",
        "submission_channel": "web_form",
        "company_name": f"Iron Ridge Integration Test {UNIQUE}",
        "contact_person": "QA Tester",
        "email": f"integration-test-{UNIQUE}@example.com",
        "phone": "5550109999",
        "city": "Madison",
        "state": "WI",
        "country": "USA",
        "vehicle_type": "Ambulance",
        "required_quantity": 1,
    }
    r1 = await client.post(f"{BASE}/api/v1/leads", json=payload, timeout=30.0)
    body1 = r1.json()
    r2 = await client.post(f"{BASE}/api/v1/leads", json=payload, timeout=30.0)
    body2 = r2.json()

    deal_id = body1.get("data", {}).get("deal_id")
    customer_id = body1.get("data", {}).get("customer_id")

    db_check: dict[str, Any] = {}
    if deal_id and customer_id:
        async with AsyncSessionFactory() as session:
            db_check = await _verify_lead_in_db(session, deal_id, customer_id)

    return {
        "first": {"status": r1.status_code, "success": body1.get("success"), "data": body1.get("data")},
        "duplicate": {
            "status": r2.status_code,
            "success": body2.get("success"),
            "is_duplicate": body2.get("data", {}).get("is_duplicate"),
            "customer_id": body2.get("data", {}).get("customer_id"),
            "deal_id": body2.get("data", {}).get("deal_id"),
        },
        "db": db_check,
    }


async def _verify_lead_in_db(session: AsyncSession, deal_id: str, customer_id: str) -> dict[str, Any]:
    deal = (
        await session.execute(
            text(
                "SELECT deal_id, customer_id, status, current_agent, workflow_id "
                "FROM deals WHERE deal_id = :did"
            ),
            {"did": deal_id},
        )
    ).mappings().first()
    customer = (
        await session.execute(
            text("SELECT customer_id, company_name, email FROM customers WHERE customer_id = :cid"),
            {"cid": customer_id},
        )
    ).mappings().first()
    audit_count = (
        await session.execute(
            text("SELECT COUNT(*) AS c FROM audit_logs WHERE deal_id = :did"),
            {"did": deal_id},
        )
    ).scalar()
    deal_count_for_customer = (
        await session.execute(
            text("SELECT COUNT(*) AS c FROM deals WHERE customer_id = :cid"),
            {"cid": customer_id},
        )
    ).scalar()
    return {
        "deal": dict(deal) if deal else None,
        "customer": dict(customer) if customer else None,
        "audit_count": audit_count,
        "deal_count_for_customer": deal_count_for_customer,
    }


async def phase7_agent_chain(client: httpx.AsyncClient, deal_id: str, org_name: str) -> dict[str, Any]:
    chain: dict[str, Any] = {}
    h = _headers()

    async def post_agent(name: str, extra: dict | None = None) -> dict[str, Any]:
        body = {"deal_id": deal_id, "org_name": org_name, "vehicle_type": "Ambulance", "required_quantity": 1}
        if extra:
            body.update(extra)
        r = await client.post(f"{BASE}/agents/{name}", json=body, headers=h, timeout=120.0)
        try:
            data = r.json()
        except Exception:
            data = {"raw": r.text[:500]}
        return {"status": r.status_code, "body": data}

    chain["marty"] = await post_agent("marty")
    marty_body = chain["marty"]["body"]
    lead_score = marty_body.get("lead_score") if isinstance(marty_body, dict) else None

    chain["lisa"] = await post_agent("lisa", {"lead_score": lead_score or 85})
    chain["neil"] = await post_agent("neil")
    neil_body = chain["neil"]["body"]
    requirements = neil_body.get("requirements") if isinstance(neil_body, dict) else "Standard ambulance configuration"
    chain["paul"] = await post_agent("paul", {"requirements": requirements or "Standard ambulance configuration"})

    paul_body = chain["paul"]["body"]
    quotation_id = paul_body.get("quotation_id") if isinstance(paul_body, dict) else None

    # Victor approval
    if quotation_id:
        ar = await client.post(
            f"{BASE}/approvals/{quotation_id}/approve",
            json={"decided_by": "integration-test", "notes": "Approved for QA"},
            headers=h,
            timeout=60.0,
        )
        chain["victor_approve"] = {"status": ar.status_code, "body": ar.json() if ar.content else {}}
    else:
        chain["victor_approve"] = {"status": None, "skipped": True, "reason": "no quotation_id from Paul"}

    chain["sally"] = await post_agent(
        "sally",
        {"quotation_id": quotation_id, "approval_status": "APPROVED"} if quotation_id else None,
    )
    sally_body = chain["sally"]["body"]
    order_id = sally_body.get("order_id") if isinstance(sally_body, dict) else None
    chain["adam"] = await post_agent("adam", {"order_id": order_id, "customer_name": org_name})

    async with AsyncSessionFactory() as session:
        final_deal = (
            await session.execute(
                text("SELECT status, current_agent FROM deals WHERE deal_id = :did"),
                {"did": deal_id},
            )
        ).mappings().first()
        chain["final_deal_status"] = dict(final_deal) if final_deal else None

    return chain


async def phase13_failures(client: httpx.AsyncClient, deal_id: str) -> dict[str, Any]:
    h = _headers()
    out: dict[str, Any] = {}

    r_invalid = await client.post(f"{BASE}/api/v1/leads", json={"source": "WEBSITE"}, timeout=15.0)
    out["invalid_lead"] = {"status": r_invalid.status_code, "success": r_invalid.json().get("success")}

    r_bad_key = await client.post(
        f"{BASE}/agents/marty",
        json={"deal_id": deal_id},
        headers={"X-API-KEY": "invalid-key-12345", "Content-Type": "application/json"},
        timeout=15.0,
    )
    out["invalid_api_key_dev"] = {
        "status": r_bad_key.status_code,
        "note": "In development, invalid key may still pass if open access",
    }

    r_bad_transition = await client.post(
        f"{BASE}/agents/adam",
        json={"deal_id": deal_id},
        headers=h,
        timeout=15.0,
    )
    out["invalid_transition"] = {"status": r_bad_transition.status_code, "body": r_bad_transition.json()}

    return out


async def main() -> None:
    RESULTS["config"] = {
        "feature_n8n_publish": settings.feature_n8n_publish,
        "n8n_webhook_base_url": "SET" if settings.n8n_webhook_base_url else "MISSING",
        "agent_api_key": "SET" if settings.agent_api_key and "your-agent" not in settings.agent_api_key else "PLACEHOLDER",
        "app_env": settings.app_env,
    }

    async with httpx.AsyncClient() as client:
        RESULTS["phases"]["5_health"] = await phase5_health(client)
        if not RESULTS["phases"]["5_health"].get("/health", {}).get("ok"):
            print(json.dumps(RESULTS, indent=2, default=str))
            sys.exit(1)

        RESULTS["phases"]["6_lead_intake"] = await phase6_lead_intake(client)
        deal_id = RESULTS["phases"]["6_lead_intake"]["first"]["data"]["deal_id"]
        org_name = RESULTS["phases"]["6_lead_intake"]["first"]["data"].get("company_name") or f"Iron Ridge Integration Test {UNIQUE}"

        RESULTS["phases"]["7_agent_chain"] = await phase7_agent_chain(client, deal_id, org_name)
        RESULTS["phases"]["13_failures"] = await phase13_failures(client, deal_id)

    print(json.dumps(RESULTS, indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
