"""In-process request metrics for /metrics endpoint."""

import time
from dataclasses import dataclass, field

_start_time = time.time()
_request_count = 0
_error_count = 0
_total_duration_ms = 0.0
_last_db_latency_ms: float | None = None


@dataclass
class MetricsSnapshot:
    uptime_seconds: float
    request_count: int
    error_count: int
    avg_duration_ms: float
    last_db_latency_ms: float | None = field(default=None)


def record_request(duration_ms: float, status_code: int) -> None:
    global _request_count, _error_count, _total_duration_ms
    _request_count += 1
    _total_duration_ms += duration_ms
    if status_code >= 500:
        _error_count += 1


def record_db_latency(latency_ms: float) -> None:
    global _last_db_latency_ms
    _last_db_latency_ms = latency_ms


def get_metrics_snapshot() -> MetricsSnapshot:
    avg = _total_duration_ms / _request_count if _request_count else 0.0
    return MetricsSnapshot(
        uptime_seconds=round(time.time() - _start_time, 2),
        request_count=_request_count,
        error_count=_error_count,
        avg_duration_ms=round(avg, 2),
        last_db_latency_ms=_last_db_latency_ms,
    )
