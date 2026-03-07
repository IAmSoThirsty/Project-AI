# Multi-stage build for Project-AI
# Supply Chain Hardening: Base images pinned to specific version

# Stage 1: Build dependencies
FROM python:3.12-slim AS builder

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Build wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt


# Stage 2: Runtime
FROM python:3.12-slim

# Create non-root user
RUN groupadd -r projectai && useradd -r -g projectai -d /app -s /sbin/nologin projectai

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 \
    libffi8 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /build/wheels /wheels

# Install wheels
COPY requirements.txt .
RUN pip install --no-cache /wheels/* && rm -rf /wheels

# Copy application (NOT source-mounted — immutable image)
COPY src/ /app/src/
COPY api/ /app/api/
COPY config/ /app/config/

# Create data and log directories owned by non-root user
RUN mkdir -p /app/data /app/logs && chown -R projectai:projectai /app

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src:/app
ENV AUDIT_LOG_PATH=/app/logs/audit.log

# Health check — actually hits the API endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -sf http://localhost:8001/health || exit 1

# Run as non-root
USER projectai

# Expose API port
EXPOSE 8001

# Entry point
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]
