# ===========================================================
# Iron Ridge Intelligent Sales Workflow — Dockerfile
# Multi-stage build for minimal production image
# ===========================================================

# --- Stage 1: Builder ---
FROM python:3.12-slim AS builder

WORKDIR /build

# Install build dependencies for asyncpg (C extension)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install into a separate directory
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt && \
    pip install --no-cache-dir --prefix=/install "aiohttp==3.13.2" && \
    PYTHONPATH=/install/lib/python3.12/site-packages \
    python -c "import aiohttp; from slack_sdk.web.async_client import AsyncWebClient"


# --- Stage 2: Production ---
FROM python:3.12-slim AS production

WORKDIR /app

# Install only runtime system libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini .

# Fail the image build if slack async dependencies are missing
RUN python -c "import aiohttp; from slack_sdk.web.async_client import AsyncWebClient"

# Non-root user for security
RUN addgroup --system ironridge && adduser --system --group ironridge
USER ironridge

# Railway and other hosts inject PORT at runtime (default 8000 for local Docker)
ENV PORT=8000
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; port=os.environ.get('PORT','8000'); r=urllib.request.urlopen(f'http://localhost:{port}/health', timeout=5); exit(0 if r.status==200 else 1)"

# Run with Uvicorn — shell form so $PORT expands on Railway
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
