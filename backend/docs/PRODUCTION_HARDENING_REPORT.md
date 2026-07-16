# Production Hardening Report

**Date:** 2026-07-10  
**Sprint:** Production Hardening  
**Test Result:** 102 passed (0 failures)

---

## Summary

Production hardening features were added without modifying agent business logic, breaking existing APIs, or redesigning architecture. All existing endpoints remain functional; new endpoints were added alongside them.

---

## 1. Workflow Status API

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/workflows/{deal_id}` | Deal workflow status with customer, progress %, ETA, retry state |
| `GET /api/v1/workflows/{deal_id}/timeline` | Chronological audit trail (paginated) |
| `POST /api/v1/workflows/{deal_id}/retry` | Record explicit n8n retry attempt |

**Files:** `app/services/workflow_status.py`, `app/api/routes/v1/workflows.py`, `app/schemas/workflow.py`

**Progress:** Computed from `PIPELINE_ORDER` in `app/core/enums.py`.

---

## 2. Approval API Aliases

| New Endpoint | Delegates To |
|--------------|--------------|
| `POST /approvals/request` | `ApprovalService.request_approval()` |
| `POST /approvals/{id}/approve` | `ApprovalService.decide(APPROVED)` |
| `POST /approvals/{id}/reject` | `ApprovalService.decide(REJECTED)` |

Existing routes (`/decide`, `/request/{quotation_id}`, etc.) unchanged.

---

## 3. NotificationService

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/notifications` | n8n trigger — template + channels |

**Channels:** Slack (live), Email (SMTP when configured), SMS (stub).

`NotificationPreparationService` refactored to delegate to `NotificationService`.

---

## 4. Quotation PDF

| Endpoint | Description |
|----------|-------------|
| `GET /quotations/{quotation_id}/pdf` | Downloadable PDF (reportlab) |

Eager-loaded quotation items + customer name via `DealRepository.get_with_customer()`.

---

## 5. Dashboard APIs

| Endpoint | Description |
|----------|-------------|
| `GET /dashboard/summary` | Deal counts, revenue, pending approvals |
| `GET /dashboard/pipeline` | Pipeline stage counts (ordered) |
| `GET /dashboard/agents` | Active agent distribution |
| `GET /dashboard/revenue` | Monthly revenue rollup |
| `GET /dashboard/orders` | Order status counts + recent |
| `GET /dashboard/approvals` | Approval decision counts + pending |

Single-query aggregations via `DashboardRepository` — no N+1.

---

## 6. Health Endpoints

| Endpoint | Type |
|----------|------|
| `GET /health` | Liveness (DB ping, 503 on failure) |
| `GET /ready` | Readiness (DB + Redis + config checks) |
| `GET /metrics` | JSON metrics (uptime, request counts, dependency status) |

---

## 7. Retry Tracking

**Migration:** `003_add_workflow_execution_state`

Table `workflow_execution_state` (deal-level):
- `attempt_count`, `last_attempt_at`, `last_error`, `retryable`

Passive recording on `/agents/*` failures via exception handlers. Exposed in workflow status response.

---

## 8. Structured Logging

- `app/core/log_context.py` — contextvars for `request_id`, `deal_id`, `workflow_id`, `agent`
- `RequestLoggingMiddleware` — extracts deal_id from URL, records metrics
- `JSONFormatter` — injects context into all log lines

---

## 9. Configuration

New settings in `app/core/config.py` and `.env.example`:
- HTTP timeouts (`LLM_TIMEOUT_SECONDS`, `N8N_TIMEOUT_SECONDS`)
- Email SMTP settings
- Feature flags (`FEATURE_PDF_EXPORT`, `FEATURE_DASHBOARD`, etc.)
- PDF branding
- `METRICS_ENABLED`

`StubWorkflowService` optionally POSTs to n8n when `FEATURE_N8N_PUBLISH=true`.

---

## 10. Files Added

```
app/api/routes/v1/workflows.py
app/api/routes/v1/notifications.py
app/api/routes/dashboard.py
app/api/routes/health.py
app/services/workflow_status.py
app/services/workflow_retry.py
app/services/notification.py
app/services/dashboard.py
app/services/health.py
app/services/quotation_pdf.py
app/repositories/dashboard.py
app/repositories/workflow_execution_state.py
app/models/workflow_execution_state.py
app/schemas/workflow.py
app/schemas/dashboard.py
app/schemas/notification.py
app/core/log_context.py
app/core/metrics.py
migrations/versions/003_add_workflow_execution_state.py
tests/integration/test_workflows_api.py
tests/integration/test_approvals_api.py
tests/integration/test_health_api.py
tests/integration/test_dashboard_api.py
tests/unit/test_notification_service.py
tests/unit/test_quotation_pdf.py
tests/unit/test_workflow_status.py
tests/unit/test_request_logging.py
```

---

## Production Readiness Checklist

| Check | Status |
|-------|--------|
| Backend starts | Pass |
| Migrations (run `alembic upgrade head`) | Required for retry tracking |
| All tests pass (102) | Pass |
| `/docs` loads | Pass |
| `/api/v1/leads` works | Pass |
| All agent endpoints execute | Pass (unchanged) |
| No MissingGreenlet | Pass (eager loading preserved) |
| No serialization errors | Pass |
| New workflow/dashboard/health APIs | Pass |

---

## Remaining Risks

1. **Migration 003** must be applied in production before retry tracking works.
2. **Email/SMS** channels require SMTP / provider configuration.
3. **Dashboard queries** may need indexes on high-volume tables at scale.
4. **PDF branding** uses settings defaults — customize via env vars.

---

## Deployment Notes

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Verify:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/ready
curl http://localhost:8000/metrics
```
