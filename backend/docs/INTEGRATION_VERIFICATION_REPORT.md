# Iron Ridge Integration Verification Report

**Date:** 2026-07-14  
**Scope:** Backend + n8n integration verification (Phases 1–15)  
**Commit status:** No commits or pushes made during this verification.

---

## 1. Executive Result

| Criterion | Result |
|-----------|--------|
| **Overall** | **PARTIAL PASS** |
| Demo-ready (backend agent chain) | **Yes** — direct backend agent pipeline verified to `DELIVERED` |
| Backend stable | **Yes** — 102/102 automated tests pass, startup healthy |
| Backend ↔ n8n integration verified | **No** — `FEATURE_N8N_PUBLISH=false`, placeholder n8n URL, live Cloud workflow not observed |

**Summary:** The FastAPI backend, Supabase persistence, universal lead intake, and full agent chain work when invoked directly. Automatic n8n orchestration and public tunnel connectivity were **not verified** in this run due to configuration gaps. Duplicate-deal architecture risk remains documented for Path A+B.

---

## 2. Environment

| Component | Status |
|-----------|--------|
| Backend process | Running on `http://localhost:8000` |
| Database (Supabase) | **Connected** — `DATABASE_URL` SET, valid `postgresql+asyncpg://` format |
| Migration head | **`003_add_workflow_execution_state`** (current = head) |
| n8n connectivity | **Not reachable** — `N8N_WEBHOOK_BASE_URL` is PLACEHOLDER (`https://your-n8n-instance.com/webhook`) |
| Public tunnel (ngrok) | **Not verified** — local [`n8n/iron-ridge.json`](../n8n/iron-ridge.json) references stale `upright-sassy-handcuff.ngrok-free.dev` |
| Redis | SET in `.env` but **unreachable** → `/ready` returns 503 |

### Configuration audit (secrets redacted)

| Variable | Status |
|----------|--------|
| `DATABASE_URL` | SET |
| `SECRET_KEY` | PLACEHOLDER |
| `AGENT_API_KEY` | PLACEHOLDER |
| `N8N_WEBHOOK_BASE_URL` | PLACEHOLDER |
| `FEATURE_N8N_PUBLISH` | **false** (defaults; not set in `.env`) |
| `LLM_TIMEOUT_SECONDS` | Uses default (30) |
| `N8N_TIMEOUT_SECONDS` | Uses default (15) |
| `REDIS_URL` | SET (causes `/ready` 503 when Redis not running) |
| `SMTP_*` | OPTIONAL / not configured |
| `OPENAI_API_KEY` | PLACEHOLDER |
| `SLACK_BOT_TOKEN` | PLACEHOLDER |
| `METRICS_ENABLED` | true |
| `ALLOWED_ORIGINS` | SET (`localhost:3000`) |
| `APP_ENV` | development |

---

## 3. Automated Tests

| Metric | Result |
|--------|--------|
| **Passed** | **102** |
| **Failed** | 0 |
| **Skipped** | 0 |
| **Warnings** | 1 (RuntimeWarning in `test_slack.py` mock) |
| **Execution time** | ~150s |
| **Baseline match** | Matches documented 102-pass baseline |

Command: `pytest -q` from `backend/`

---

## 4. Lead Intake Test

**Test ID:** `20260714052602-688a1edd`

| Check | Result |
|-------|--------|
| HTTP status | **201 Created** |
| `success` | `true` |
| `deal_id` | `a34162d0-5920-4039-9018-d4714af170b0` |
| `customer_id` | `f7b0dcbc-4aff-4e16-a69a-71674411ccb7` |
| `workflow_id` | `f4e22b3a-a120-4889-ba67-5521ed7a9dbc` |
| `lead_source` | `WEBSITE` |
| `submission_channel` | `web_form` |
| Customer in DB | Verified |
| Deal in DB | Verified (`status=LEAD`, `current_agent=MARTY`) |
| Audit log | 1 entry on first submission |

### Duplicate submission (same payload resubmitted)

| Check | Result |
|-------|--------|
| HTTP status | 201 |
| `is_duplicate` | **true** |
| `customer_id` | **Same** (`f7b0dcbc-...`) — customer reused |
| `deal_id` | **New** (`44acd1f7-...`) — second deal created |
| Deals per customer | **2** (by design: customer dedup only, always new deal) |

---

## 5. Agent Chain (Direct Backend Test)

Deal: `a34162d0-5920-4039-9018-d4714af170b0`

| Agent | HTTP | Input Status | Output Status | DB Persisted | Result |
|-------|------|--------------|---------------|--------------|--------|
| Marty | 200 | LEAD | LEAD, score=85 | Yes | **PASS** |
| Lisa | 200 | LEAD | QUALIFIED | Yes | **PASS** |
| Neil | 200 | QUALIFIED | REQUIREMENTS_COLLECTED | Yes | **PASS** |
| Paul | 200 | REQUIREMENTS_COLLECTED | PRICED, quotation created | Yes (items via selectinload) | **PASS** — no MissingGreenlet |
| Victor | 401 | N/A | JWT required on `/approvals/*` | Approval row PENDING | **SKIP** — auth required; Sally used n8n-style bypass |
| Sally | 200 | `approval_status=APPROVED` in body | ORDER_CREATED | Yes | **PASS** (n8n contract simulation) |
| Adam | 200 | order_id provided | **DELIVERED** | Yes | **PASS** |

**Final deal status:** `DELIVERED` / `current_agent=ADAM`

**Note:** Victor approval endpoints require JWT (`require_auth`), not `X-API-KEY`. n8n workflow uses a Set node for Victor; Sally accepts `approval_status=APPROVED` from n8n body to transition without JWT approval API call.

---

## 6. Backend → n8n Integration

| Check | Result |
|-------|--------|
| Trigger method | `StubWorkflowService.publish_lead_created()` → POST `{N8N_WEBHOOK_BASE_URL}/lead-created` |
| Enabled? | **No** — `FEATURE_N8N_PUBLISH=false` |
| Payload contract (when enabled) | `workflow_id`, `deal_id`, `source`, `event`, `company_name`, `submission_channel`, `is_duplicate`, `email`, `phone` |
| `customer_id` in payload | **No** |
| Automatic n8n execution confirmed | **No** — publish disabled + placeholder URL timeout |
| Duplicate deal risk (Path A+B) | **HIGH** — documented; not triggered this run because n8n publish disabled |
| Transaction race risk | **Yes** — n8n called before DB commit (pre-existing architecture) |

**Probe result:** POST to placeholder URL → `ConnectTimeout`

---

## 7. Database Consistency (Golden-Path Deal)

Deal `a34162d0-5920-4039-9018-d4714af170b0`:

| Entity | Status |
|--------|--------|
| customer | OK — linked |
| deal | OK — `DELIVERED`, `approval_status=APPROVED` |
| lead_validation | 1 row |
| requirements | 1 row |
| quotations | 1 row |
| quotation_items | Present (Paul path) |
| approvals | 1 row — **`decision=PENDING`** while deal is APPROVED |
| orders | 1 row |
| delivery_plan | Linked via `order_id` (not `deal_id`) |
| audit_logs | Multiple entries |
| workflow_execution_state | Not populated for n8n failure path |

**Consistency gap:** When Sally receives `approval_status=APPROVED` from n8n (bypassing JWT approval API), the `approvals` table row remains `PENDING` while `deals.approval_status=APPROVED`. Order was created successfully.

---

## 8. Bugs Found

### Bug 1 — Startup failure: missing `text` import (FIXED)

| Field | Detail |
|-------|--------|
| Symptom | Backend failed to start: `NameError: name 'text' is not defined` |
| Root cause | [`app/main.py`](app/main.py) lifespan DB check used `text("SELECT 1")` without import |
| Fix | Added `from sqlalchemy import text` |
| Regression test | Existing health/startup path; verified backend starts cleanly |
| Status | **Fixed locally** (not committed) |

### Finding 2 — `/ready` returns 503 when Redis configured but unreachable (NOT FIXED)

| Field | Detail |
|-------|--------|
| Symptom | `GET /ready` → 503 |
| Root cause | `REDIS_URL` set but Redis not running; readiness requires Redis connected or skipped |
| Recommendation | Clear `REDIS_URL` in dev if Redis unused, or start Redis |
| Status | Configuration issue, not code defect |

### Finding 3 — Approval record not updated when Sally pre-approves via n8n body (NOT FIXED)

| Field | Detail |
|-------|--------|
| Symptom | `approvals.decision=PENDING` while deal reached `DELIVERED` with `approval_status=APPROVED` |
| Root cause | [`SallyAgent`](app/agents/sally.py) transitions deal on `approval_status=APPROVED` but does not call `ApprovalService.decide()` |
| Impact | Audit/reporting inconsistency; n8n golden path may mask this |
| Recommendation | Minimal fix: when Sally receives `APPROVED`, update pending approval record — deferred pending approval |

---

## 9. Remaining Risks

1. **Path A+B duplicate deals** — If `FEATURE_N8N_PUBLISH=true` and live n8n still runs `Create Deal`, backend deal + n8n deal will coexist.
2. **Pre-commit n8n race** — n8n HTTP called before transaction commit; sync Marty callback may not see deal.
3. **n8n integration unverified** — Requires real `N8N_WEBHOOK_BASE_URL`, `FEATURE_N8N_PUBLISH=true`, active ngrok, and n8n Cloud execution log review.
4. **Stale local n8n JSON** — [`n8n/iron-ridge.json`](../n8n/iron-ridge.json) `active: false`, old ngrok, empty Create Deal body.
5. **Victor JWT vs n8n Set node** — Approval API requires auth; n8n simulates approval via Sally body field.
6. **AGENT_API_KEY placeholder** — Production agent auth not configured.
7. **Duplicate resubmission** — Always creates new deal (intentional per current code).

---

## 10. Demo Readiness

### Safe to demonstrate

- `POST /api/v1/leads` from frontend or curl → customer + deal in Supabase
- Direct agent chain via `POST /agents/{marty,lisa,neil,paul,sally,adam}` in development
- `GET /health`, `GET /docs`, `GET /metrics`
- Full pytest suite (102 pass)

### Not yet verified

- Automatic n8n workflow trigger after lead intake
- Full golden-path E2E through n8n Cloud (Marty → Adam without manual agent calls)
- n8n Cloud → backend via public ngrok URL
- Duplicate-deal prevention for Path A (backend + n8n Create Deal)
- Production `X-API-KEY` enforcement

### Startup order

```bash
# Terminal 1 — backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 — frontend (optional)
cd frontend
npm run dev

# Terminal 3 — ngrok (required for n8n Cloud → local backend)
ngrok http 8000
# Update n8n Cloud HTTP nodes + N8N_WEBHOOK_BASE_URL in .env
```

### Test data strategy

- Use unique suffix: `Iron Ridge Integration Test <timestamp-uuid>@example.com`
- Do not reuse production customer emails
- Expect 2 deals if submitting same lead twice (duplicate customer, new deal)

### To enable n8n integration testing

```env
FEATURE_N8N_PUBLISH=true
N8N_WEBHOOK_BASE_URL=https://<your-n8n-cloud>/webhook/<workflow-id>
AGENT_API_KEY=<real-key-matching-n8n-nodes>
```

Ensure live n8n workflow:
- Receives `/lead-created` with `deal_id`
- **Skips Create Deal** when `deal_id` present (Path A)
- Uses current ngrok/public URL for agent HTTP nodes

---

## Phase Summary

| Phase | Result |
|-------|--------|
| 1 Static audit | Complete (see plan) |
| 2 Environment | Complete — gaps documented |
| 3 Migrations | **PASS** — head `003`, all tables exist |
| 4 Pytest | **PASS** — 102/102 |
| 5 Health | **PARTIAL** — `/health` 200, `/ready` 503 (Redis), `/metrics` 200, `/docs` 200 |
| 6 Lead intake | **PASS** |
| 7 Agent chain | **PASS** (Victor via Sally bypass) |
| 8 Async audit | **PASS** — Paul selectinload preserved; no repo commits |
| 9 n8n publish | **BLOCKED** — feature disabled, placeholder URL |
| 10 n8n→backend | **NOT VERIFIED** — no active public tunnel |
| 11 Contract audit | Documented from local JSON + code (live Cloud not inspected) |
| 12 Golden path E2E | **NOT RUN** — prerequisites not met |
| 13 Failure paths | Invalid lead 422; invalid transition 422; dev open agent access |
| 14 DB consistency | **PARTIAL** — approval PENDING mismatch noted |
| 15 Final verification | **PASS** — 102 tests, backend healthy |

---

## Verification Scripts Added (local, not committed requirement)

| Script | Purpose |
|--------|---------|
| [`scripts/audit_env.py`](scripts/audit_env.py) | Env audit without printing secrets |
| [`scripts/run_integration_verification.py`](scripts/run_integration_verification.py) | Phases 5–7, 13 evidence collection |
| [`scripts/verify_tables.py`](scripts/verify_tables.py) | Phase 3 table existence |
| [`scripts/audit_deal_consistency.py`](scripts/audit_deal_consistency.py) | Phase 14 deal audit |

Re-run integration checks:

```bash
cd backend
python scripts/run_integration_verification.py
pytest -q
```
