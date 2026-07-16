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
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.exception_handlers import register_exception_handlers
from app.api.middleware.rate_limit import RateLimitMiddleware
from app.api.middleware.request_logging import RequestLoggingMiddleware
from app.api.routes import (
    agents,
    approvals,
    audit,
    auth,
    consultations,
    customers,
    dashboard,
    deals,
    health,
    orders,
    quotations,
    requirements,
    webhooks,
)
from app.api.routes.v1 import leads as v1_leads
from app.api.routes.v1 import notifications as v1_notifications
from app.api.routes.v1 import workflows as v1_workflows
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

    # Verify database connectivity at startup (non-fatal — app serves /health and /docs degraded)
    db_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
        logger.info("Database connectivity verified at startup.")
    except Exception as exc:
        logger.warning(
            "Database not reachable at startup; running in degraded mode. "
            "Use Supabase pooler URL (port 6543) with SSL on Render/Railway.",
            extra={"error": str(exc)},
            exc_info=True,
        )

    # Bootstrap admin user only when database is reachable
    if db_ok:
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
    docs_url="/docs" if settings.enable_api_docs else None,
    redoc_url="/redoc" if settings.enable_api_docs else None,
    openapi_url="/openapi.json" if settings.enable_api_docs else None,
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
app.add_middleware(RateLimitMiddleware)
app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

# ---------------------------------------------------------------------------
# System routes (health, readiness, metrics)
# ---------------------------------------------------------------------------

@app.get("/", tags=["System"])
async def root():
    """Root endpoint verifying application status and metadata."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "docs_url": "/docs"
    }


app.include_router(health.router, tags=["System"])

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
app.include_router(v1_leads.router, prefix="/api/v1/leads", tags=["Lead Intake"])
app.include_router(v1_workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])
app.include_router(v1_notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(consultations.router, prefix="/api/v1/consultations", tags=["Consultations"])
