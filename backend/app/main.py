"""
app/main.py

FastAPI application factory for Iron Ridge Intelligent Sales Workflow.

This is the entry point for the application. It:
    1. Configures logging
    2. Creates the FastAPI instance with metadata
    3. Registers middleware (CORS)
    4. Registers all API routers
    5. Defines the /health endpoint (database connectivity check)
    6. Manages async lifespan (startup / shutdown events)

Architecture note:
    This file is intentionally thin. No business logic here.
    Routing is delegated to app/api/routes/*.py
    Business logic lives in app/services/*.py
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.exception_handlers import register_exception_handlers
from app.api.middleware.request_logging import RequestLoggingMiddleware
from app.api.routes import (
    agents,
    approvals,
    audit,
    auth,
    customers,
    deals,
    orders,
    quotations,
    requirements,
    webhooks,
)
from app.core.config import settings
from app.core.logging import configure_logging
from app.database.database import engine
from app.database.session import AsyncSessionFactory
from app.repositories.user import UserRepository
from app.services.auth import AuthService

# Configure structured JSON logging BEFORE anything else logs
configure_logging()

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — replaces deprecated @app.on_event("startup")
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application startup and shutdown.

    Startup:
        - Log startup with version and environment info
        - Verify database connectivity (fail fast on misconfiguration)

    Shutdown:
        - Dispose engine (closes all pooled connections gracefully)
    """
    # --- Startup ---
    logger.info(
        "Iron Ridge backend starting up",
        extra={
            "app_name": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
        },
    )

    # Verify database connectivity at startup
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("Database connectivity verified at startup.")
    except Exception as exc:
        logger.critical(
            "STARTUP FAILED: Cannot connect to database. Check DATABASE_URL.",
            extra={"error": str(exc)},
            exc_info=True,
        )
        raise

    # Bootstrap admin user if not exists
    try:
        async with AsyncSessionFactory() as session:
            auth_service = AuthService(UserRepository(session))
            await auth_service.ensure_admin_exists(settings.admin_email, settings.admin_password)
            await session.commit()
        logger.info("Admin user bootstrap complete.")
    except Exception as exc:
        logger.warning("Admin bootstrap skipped", extra={"error": str(exc)})

    yield  # Application runs here

    # --- Shutdown ---
    logger.info("Iron Ridge backend shutting down. Disposing database engine.")
    await engine.dispose()
    logger.info("Database engine disposed. Shutdown complete.")


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Enterprise Multi-Agent AI Sales Operating System for Iron Ridge Fire Apparatus. "
        "Powers six AI agents (Marty, Lisa, Neil, Paul, Sally, Adam) and one human principal (Victor). "
        "All agents are orchestrated externally by n8n workflows."
    ),
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

# ---------------------------------------------------------------------------
# Health Check Endpoint
# ---------------------------------------------------------------------------

@app.get(
    "/health",
    tags=["System"],
    summary="Health check with database connectivity verification",
    description=(
        "Returns application status and verifies live database connectivity "
        "by executing a SELECT 1 query against Supabase PostgreSQL. "
        "n8n workflows should poll this before invoking agents."
    ),
    response_description="System health status with database ping latency.",
)
async def health_check() -> JSONResponse:
    """
    Health check endpoint.

    Performs a lightweight SELECT 1 to verify the database is reachable.
    Reports latency in milliseconds so infrastructure teams can detect
    slow connection pool saturation.

    Returns:
        200 OK    — Application healthy, database connected
        503 Error — Database unreachable (connection failure)
    """
    start_time = time.perf_counter()

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        db_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.debug("Health check passed.", extra={"db_latency_ms": db_latency_ms})

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "app": settings.app_name,
                "version": settings.app_version,
                "environment": settings.app_env,
                "database": {
                    "status": "connected",
                    "latency_ms": db_latency_ms,
                },
            },
        )

    except Exception as exc:
        db_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        logger.error(
            "Health check FAILED — database unreachable.",
            extra={"error": str(exc), "db_latency_ms": db_latency_ms},
            exc_info=True,
        )

        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "app": settings.app_name,
                "version": settings.app_version,
                "environment": settings.app_env,
                "database": {
                    "status": "unreachable",
                    "error": str(exc),
                    "latency_ms": db_latency_ms,
                },
            },
        )


# ---------------------------------------------------------------------------
# API Routers
# ---------------------------------------------------------------------------

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(customers.router, prefix="/customers", tags=["Customers"])
app.include_router(deals.router, prefix="/deals", tags=["Deals"])
app.include_router(requirements.router, prefix="/requirements", tags=["Requirements"])
app.include_router(quotations.router, prefix="/quotations", tags=["Quotations"])
app.include_router(approvals.router, prefix="/approvals", tags=["Approvals"])
app.include_router(orders.router, prefix="/orders", tags=["Orders"])
app.include_router(audit.router, prefix="/audit", tags=["Audit"])
app.include_router(agents.router, prefix="/agents", tags=["AI Agents"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
