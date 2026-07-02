"""
app/core/logging.py

Structured JSON logging configuration for Iron Ridge backend.

Design decisions:
    1. JSON output — log lines are machine-readable and ingestible by
       Datadog, CloudWatch, Loki, or any log aggregator without extra parsing.

    2. Standard library `logging` is used (not structlog) — compatible with
       SQLAlchemy, Uvicorn, FastAPI, and all third-party libraries that use
       the standard `logging` module under the hood.

    3. `configure_logging()` is called ONCE at application startup in main.py.
       Never call it per-request.

    4. Log level comes from settings — INFO in production, DEBUG in development.
"""

import json
import logging
import sys
from datetime import datetime, timezone

from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """
    Formats log records as single-line JSON objects.

    Each log line contains:
        - timestamp   : ISO 8601 UTC timestamp
        - level       : log level name (INFO, WARNING, ERROR, etc.)
        - logger      : logger name (module path)
        - message     : the log message
        - extra fields: any extra dict passed to logger.info(..., extra={...})

    Example output:
        {"timestamp": "2025-01-01T00:00:00Z", "level": "INFO",
         "logger": "app.database.session", "message": "Session committed"}
    """

    def format(self, record: logging.LogRecord) -> str:
        """Serialize a LogRecord to a JSON string."""
        log_entry: dict = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Attach extra fields if provided
        # These come from: logger.info("msg", extra={"deal_id": "123"})
        reserved_attrs = {
            "msg", "args", "asctime", "created", "exc_info", "exc_text",
            "filename", "funcName", "id", "levelname", "levelno", "lineno",
            "module", "msecs", "message", "name", "pathname", "process",
            "processName", "relativeCreated", "stack_info", "thread",
            "threadName", "taskName",
        }
        for key, value in record.__dict__.items():
            if key not in reserved_attrs:
                log_entry[key] = value

        # Attach exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


def configure_logging() -> None:
    """
    Configure root logger with JSON formatting.

    Called once at application startup (in main.py lifespan).

    Sets:
        - Root logger level to settings.log_level
        - All handlers to use JSONFormatter
        - Uvicorn and SQLAlchemy loggers to respect the configured level
    """
    log_level = getattr(logging, settings.log_level.upper(), logging.INFO)

    # Remove existing handlers to avoid duplicate logs
    root_logger = logging.getLogger()
    root_logger.handlers.clear()

    # Console handler (stdout) with JSON formatter
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    console_handler.setLevel(log_level)

    root_logger.addHandler(console_handler)
    root_logger.setLevel(log_level)

    # Tune third-party library log levels
    # SQLAlchemy engine logs SQL queries only when db_echo=True in config
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.db_echo else logging.WARNING
    )
    # Suppress noisy asyncpg connection lifecycle logs in production
    logging.getLogger("asyncpg").setLevel(logging.WARNING)
    # Keep uvicorn access logs visible
    logging.getLogger("uvicorn.access").setLevel(log_level)

    root_logger.info(
        "Logging configured",
        extra={
            "log_level": settings.log_level,
            "app_env": settings.app_env,
            "app_version": settings.app_version,
        },
    )
