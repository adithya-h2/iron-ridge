"""Request logging middleware with request_id tracking."""

import logging
import re
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.log_context import get_log_context, set_log_context
from app.core.metrics import record_request

logger = logging.getLogger(__name__)

_UUID_PATH_RE = re.compile(
    r"/(?:deals|api/v1/workflows|quotations|orders|approvals)/([0-9a-fA-F-]{36})"
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        deal_id = getattr(request.state, "deal_id", None)
        if not deal_id:
            match = _UUID_PATH_RE.search(request.url.path)
            if match:
                deal_id = match.group(1)
                request.state.deal_id = deal_id

        agent = getattr(request.state, "agent_name", None)
        workflow_id = getattr(request.state, "workflow_id", None)
        set_log_context(
            request_id=request_id,
            deal_id=deal_id,
            workflow_id=workflow_id,
            agent=agent,
        )

        start = time.perf_counter()
        status_code = 500
        error_msg: str | None = None
        response: Response | None = None

        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            error_msg = str(exc)
            logger.exception(
                "Unhandled exception in request",
                extra={
                    **get_log_context(),
                    "method": request.method,
                    "path": request.url.path,
                },
            )
            raise
        finally:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            record_request(duration_ms, status_code)
            ctx = get_log_context()
            logger.info(
                "HTTP request completed",
                extra={
                    **ctx,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                    "execution_time_ms": duration_ms,
                    "status": status_code,
                    "user": getattr(request.state, "user_email", None),
                    "error": error_msg,
                },
            )
