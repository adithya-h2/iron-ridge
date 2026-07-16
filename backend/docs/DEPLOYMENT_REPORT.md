# Iron Ridge Backend — Deployment Report

**Date:** 2026-07-16  
**Target platforms:** Render (Docker), Railway (Nixpacks/Docker), local Docker Compose

---

## Root cause

### Error 1: `ModuleNotFoundError: aiohttp`

- **Cause:** `slack-sdk` async client (`AsyncWebClient`) requires `aiohttp`, which is not a guaranteed transitive install.
- **Fix:** Pin `aiohttp==3.13.2` in `requirements.txt`; verify in `Dockerfile` and `nixpacks.toml` build steps.

### Error 2: `Application startup failed` / `OSError: [Errno 101] Network is unreachable`

- **Primary cause:** `app/main.py` lifespan **re-raised** on database connection failure, aborting Uvicorn startup entirely.
- **Contributing cause:** Supabase **direct** host (`db.*.supabase.co:5432`) is often unreachable from Render/Railway (IPv6/routing). Use the **Transaction pooler** (`*.pooler.supabase.com:6543`) with **SSL**.
- **Fix:** Non-fatal DB check at startup; `/health` liveness always HTTP 200; `DATABASE_SSL=true` for asyncpg; document pooler URL in `.env.example`.

---

## Files modified

| File | Change |
|------|--------|
| `app/main.py` | DB startup check is non-fatal; admin bootstrap only when DB reachable |
| `app/database/database.py` | Supabase SSL via `DATABASE_SSL`; fixed connect_args |
| `app/core/config.py` | Added `database_ssl` setting |
| `app/services/health.py` | Liveness status `degraded` when DB down |
| `app/api/routes/health.py` | `/health` always returns HTTP 200 |
| `requirements.txt` | Production-only deps; explicit `aiohttp` |
| `requirements-dev.txt` | **New** — pytest deps |
| `.env.example` | Pooler URL guidance, `DATABASE_SSL` |
| `tests/conftest.py` | `DATABASE_SSL=false` for local tests |
| `tests/integration/test_health_api.py` | Expect `/health` 200 + `degraded` |
| `docker-compose.yml` | Healthcheck uses stdlib urllib |
| `render.yaml` | **New** — Render Docker web service blueprint |

---

## Deployment checklist

### Render

1. Create **Web Service** → **Docker**; set **Root Directory** to `backend`
2. Set environment variables (see below)
3. Use Supabase **Transaction pooler** `DATABASE_URL` (port **6543**)
4. Set `DATABASE_SSL=true`
5. Deploy; verify `GET /health` → 200, `GET /docs` → Swagger UI
6. Verify `GET /ready` → 200 only when DB (and optional Redis) are reachable

### Railway

1. Service **root directory** = `backend`
2. `railway.toml` start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Same env vars as Render
4. Nixpacks uses `nixpacks.toml` to verify `aiohttp` at build time

### Required environment variables (production)

| Variable | Required | Notes |
|----------|----------|-------|
| `DATABASE_URL` | **Yes** | Pooler URL recommended; `postgres://` auto-converted |
| `DATABASE_SSL` | Recommended | `true` for Supabase cloud |
| `SECRET_KEY` | **Yes** (prod) | ≥ 32 chars when `APP_ENV=production` |
| `AGENT_API_KEY` | **Yes** (prod) | Agent route auth |
| `ADMIN_PASSWORD` | **Yes** (prod) | Not default `changeme` |
| `APP_ENV` | Recommended | `production` |
| `ALLOWED_ORIGINS` | Recommended | Include Vercel frontend URL |
| `ENABLE_API_DOCS` | Optional | `true` for `/docs` on Render |

### Optional (graceful if missing)

`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `SLACK_*`, `REDIS_URL`, `N8N_*`, `SMTP_*`, `SUPABASE_URL`, `SUPABASE_KEY`

---

## Health endpoints

| Path | Behavior when DB offline |
|------|--------------------------|
| `/health` | **HTTP 200**, `"status": "degraded"`, database block shows unreachable |
| `/ready` | **HTTP 503**, `"ready": false` |
| `/docs` | **Available** (if `ENABLE_API_DOCS=true`) |
| `/openapi.json` | **Available** (if `ENABLE_API_DOCS=true`) |
| API routes using DB | Fail at request time with appropriate errors |

---

## Remaining risks

1. **Wrong `DATABASE_URL`** — app starts degraded but API/data routes fail until pooler URL is correct.
2. **`APP_ENV=production`** without secure secrets — Settings validation fails at import (intentional).
3. **Redis configured but unreachable** — `/ready` returns 503; app still runs.
4. **Migrations** — not run automatically on deploy; run `alembic upgrade head` separately.

---

## Local development

```bash
cd backend
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
docker compose up --build
```
