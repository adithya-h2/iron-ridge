"""Health and readiness checks."""

import time

from sqlalchemy import text

from app.core.config import settings
from app.core.metrics import get_metrics_snapshot, record_db_latency
from app.database.database import engine


class HealthService:
    async def check_database(self) -> dict:
        start = time.perf_counter()
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            latency = round((time.perf_counter() - start) * 1000, 2)
            record_db_latency(latency)
            return {"status": "connected", "latency_ms": latency}
        except Exception as exc:
            latency = round((time.perf_counter() - start) * 1000, 2)
            error = str(exc) if not settings.is_production else "Database connection failed"
            return {"status": "unreachable", "error": error, "latency_ms": latency}

    async def check_redis(self) -> dict:
        if not settings.redis_url:
            return {"status": "skipped", "configured": False}
        try:
            import redis.asyncio as aioredis

            client = aioredis.from_url(settings.redis_url, decode_responses=True)
            await client.ping()
            await client.aclose()
            return {"status": "connected", "configured": True}
        except Exception as exc:
            return {"status": "unreachable", "configured": True, "error": str(exc)}

    def check_llm(self) -> dict:
        if settings.ai_provider == "anthropic":
            configured = bool(settings.anthropic_api_key)
        else:
            configured = bool(settings.openai_api_key)
        return {"status": "configured" if configured else "not_configured", "provider": settings.ai_provider}

    def check_n8n(self) -> dict:
        configured = bool(settings.n8n_webhook_base_url)
        return {"status": "configured" if configured else "not_configured", "url_set": configured}

    def check_slack(self) -> dict:
        configured = bool(settings.slack_bot_token)
        return {"status": "configured" if configured else "not_configured"}

    async def get_health(self) -> dict:
        """Liveness payload — process is up; database may be degraded."""
        db = await self.check_database()
        status_label = "healthy" if db["status"] == "connected" else "degraded"
        return {
            "status": status_label,
            "app": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
            "database": db,
        }

    async def get_readiness(self) -> dict:
        db = await self.check_database()
        redis = await self.check_redis()
        ready = db["status"] == "connected" and redis["status"] in ("connected", "skipped")
        return {
            "ready": ready,
            "database": db,
            "redis": redis,
            "llm": self.check_llm(),
            "n8n": self.check_n8n(),
            "slack": self.check_slack(),
        }

    async def get_metrics(self) -> dict:
        snapshot = get_metrics_snapshot()
        db = await self.check_database()
        return {
            "uptime_seconds": snapshot.uptime_seconds,
            "requests": {
                "total": snapshot.request_count,
                "errors": snapshot.error_count,
                "avg_duration_ms": snapshot.avg_duration_ms,
            },
            "database": {"last_latency_ms": snapshot.last_db_latency_ms or db.get("latency_ms")},
            "dependencies": {
                "llm": self.check_llm(),
                "n8n": self.check_n8n(),
                "slack": self.check_slack(),
                "redis": await self.check_redis(),
            },
        }
