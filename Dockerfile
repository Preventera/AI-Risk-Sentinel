# =============================================================================
# AI Risk Sentinel - Multi-stage Dockerfile
# =============================================================================

# -----------------------------------------------------------------------------
# Base stage with Python dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml ./
RUN pip install --upgrade pip && \
    pip install -e ".[dev]"

# -----------------------------------------------------------------------------
# Development stage
# -----------------------------------------------------------------------------
FROM base as dev

COPY . .

CMD ["uvicorn", "ai_risk_sentinel.api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# -----------------------------------------------------------------------------
# API production stage
# -----------------------------------------------------------------------------
FROM base as api

COPY src/ ./src/
COPY data/ ./data/

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "ai_risk_sentinel.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# -----------------------------------------------------------------------------
# Celery worker stage
# -----------------------------------------------------------------------------
FROM base as worker

COPY src/ ./src/
COPY data/ ./data/

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

CMD ["celery", "-A", "ai_risk_sentinel.tasks", "worker", "--loglevel=info", "--concurrency=4"]

# -----------------------------------------------------------------------------
# Celery scheduler stage
# -----------------------------------------------------------------------------
FROM base as scheduler

COPY src/ ./src/
COPY data/ ./data/

# Create non-root user
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

CMD ["celery", "-A", "ai_risk_sentinel.tasks", "beat", "--loglevel=info"]
