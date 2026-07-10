# Iron Ridge Architecture Review Report

**Date:** 2026-07-10  
**Scope:** Full backend repository audit (Phases 1–4)  
**Sprint A status:** Implemented — see [`SPRINT_A_REPORT.md`](SPRINT_A_REPORT.md)

---

## Phase 1 — Repository Audit Summary

### HTTP layer: PASS

All 10 route files in `app/api/routes/` delegate to services only. No direct repository or SQLAlchemy usage in routes.

### Agent layer: PARTIAL (improved in Sprint A)

- **MartyAgent** — refactored to use `LeadIntakeService` (Sprint A)
- **LisaAgent / NeilAgent** — still access repositories directly (deferred to Sprint B)

### Infrastructure: PASS

| Area | Files | Verdict |
|------|-------|---------|
| Core | 6 | Production ready |
| Database | 3 | Production ready |
| Services | 18 (post Sprint A) | Production ready |
| Repositories | 20 | Thin stubs intentional |
| Models | 17 | Match Supabase schema |
| Tests | 18 | 78 tests passing |
| Migrations | 2 | Partial — business tables Supabase-managed |
| Docker | Dockerfile + compose | Dev/prod split OK |

### Files flagged for cleanup (non-blocking)

- Empty `app/api/middleware/__init__.py`, `tools/__init__.py`
- Dead `WorkflowEventResponse` in `schemas/common.py`
- Unused DI deps in `PricingService`, `SlackService`
- Duplicate `_rid()` in 7 route files
- `pytest.ini` `[tool:pytest]` section ignored

---

## Phase 2 — Code Quality

| Category | Status |
|----------|--------|
| TODO/FIXME | None in `app/` |
| Commented dead code | None |
| Magic strings | Minor (Sally, order service) |
| Duplicate tests | `test_pipeline.py` vs matrix — consolidate in Sprint B |
| Security | Webhook auth deferred to Sprint B |

---

## Phase 3 — Architecture Validation

| Rule | Status |
|------|--------|
| Routes → Services only | PASS |
| Services → Repos only | PASS |
| Repos → no business logic | MOSTLY PASS |
| Models → no API logic | PASS |
| Schemas → no business logic | PASS |

### Remaining violations

1. Lisa/Neil agents bypass service layer
2. `SlackService.handle_interaction` queries approval repo directly
3. `AgentMemoryRepository.upsert_execution` contains merge logic

---

## Phase 4 — Database Review

| Table | Lead Intake Ready |
|-------|-------------------|
| `customers` | YES |
| `deals` | YES (after migration 002) |
| `audit_logs` | YES |
| `agent_memory` | YES |
| `users` | YES |
| `lead_validation` | YES (post-intake, Lisa) |

### Migration 002

Adds `lead_source`, `workflow_id`, `submission_channel` to `deals`.

```bash
cd backend && alembic upgrade head
```

---

## Phase 5 — Sprint A Outcome

Universal Lead Intake Engine delivered:

- `POST /api/v1/leads` — primary public endpoint
- `LeadIntakeService` — single orchestrator for all channels
- `WorkflowService` stub — no direct n8n coupling
- Backward compatible Marty + n8n webhook paths

---

## Remaining Technical Debt

- Lisa/Neil service layer refactor
- Full route integration test matrix
- CI pipeline
- Alembic baseline for 16 Supabase tables
- Webhook authentication hardening

---

## Recommendations Before Sprint B

1. `N8nWorkflowService` implementing `WorkflowService`
2. `LeadValidationService` + Lisa refactor
3. Neil → `RequirementService`
4. GitHub Actions CI
5. Consolidate duplicate test fixtures and route helpers

---

*Generated as part of Architecture Review + Sprint A*
