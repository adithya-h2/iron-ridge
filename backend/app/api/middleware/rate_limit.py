"""Optional rate limiting middleware (Redis-backed when configured)."""

import logging
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.config import settings

logger = logging.getLogger(__name__)

# In-memory fallback for development (per-process, not distributed)
_memory_buckets: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT = 120  # requests per window
_WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if settings.is_development and not settings.redis_url:
            return await call_next(request)

        client_key = request.client.host if request.client else "unknown"
        now = time.time()

        if settings.redis_url:
            try:
                import redis.asyncio as aioredis

                redis_client = aioredis.from_url(settings.redis_url)
                key = f"rate:{client_key}:{request.url.path}"
                count = await redis_client.incr(key)
                if count == 1:
                    await redis_client.expire(key, _WINDOW_SECONDS)
                await redis_client.aclose()
                if count > _RATE_LIMIT:
                    return self._too_many_requests(request)
            except Exception as exc:
                logger.warning("Rate limit Redis unavailable, allowing request", extra={"error": str(exc)})
                return await call_next(request)
        else:
            bucket = _memory_buckets[client_key]
            _memory_buckets[client_key] = [t for t in bucket if now - t < _WINDOW_SECONDS]
            if len(_memory_buckets[client_key]) >= _RATE_LIMIT:
                return self._too_many_requests(request)
            _memory_buckets[client_key].append(now)

        return await call_next(request)

    def _too_many_requests(self, request: Request) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=429,
            content={
                "success": False,
                "data": None,
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Too many requests. Please retry later.",
                    "details": {},
                },
                "request_id": request_id,
            },
            headers={"Retry-After": str(_WINDOW_SECONDS)},
        )
