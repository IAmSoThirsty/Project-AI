# (Substrate Runtime Blueprint)           [2026-04-09 04:26]
#                                          Status: Active

# Multi-stage build for Project-AI
# Supply Chain Hardening: Base images pinned to SHA256 digest

# Build arguments for reproducibility
ARG SOURCE_COMMIT_SHA="unknown"
ARG BUILD_VERSION="dev"
ARG SOURCE_DATE_EPOCH="0"
ARG BUILD_TIMESTAMP="unknown"

# Stage 1: Build dependencies
FROM python:3.11-slim@sha256:0b23cfb7425d065008b778022a17b1551c82f8b4866ee5a7a200084b7e2eafbf as builder

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    pkg-config \
    libssl-dev \
    libffi-dev \
    # Database support (if psycopg2 used)
    libpq-dev \
    # Image processing (for Pillow - Miniature Office)
    libjpeg-dev \
    zlib1g-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Build wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt


# Stage 2: Runtime
FROM python:3.11-slim@sha256:0b23cfb7425d065008b778022a17b1551c82f8b4866ee5a7a200084b7e2eafbf

# OCI labels for reproducibility
LABEL org.opencontainers.image.revision="${SOURCE_COMMIT_SHA}"
LABEL org.opencontainers.image.version="${BUILD_VERSION}"
LABEL org.opencontainers.image.created="${BUILD_TIMESTAMP}"
LABEL org.opencontainers.image.source="https://github.com/IAmSoThirsty/Sovereign-Governance-Substrate"
LABEL org.opencontainers.image.title="Project-AI Sovereign Governance"
LABEL org.opencontainers.image.description="Constitutionally governed AI platform"

# Create non-root user for security
RUN groupadd -r sovereign && useradd -r -g sovereign sovereign

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core SSL/TLS
    libssl3 \
    libffi8 \
    # Database runtime (if psycopg2 used)
    libpq5 \
    # Image processing runtime (for Pillow - Miniature Office)
    libjpeg62 \
    zlib1g \
    libtiff5 \
    libfreetype6 \
    liblcms2-2 \
    libwebp7 \
    # Utilities
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /build/wheels /wheels

# Install wheels
COPY requirements.txt .
RUN pip install --no-cache-dir /wheels/*

# Copy application with correct ownership
COPY --chown=sovereign:sovereign src/ /app/src/
COPY --chown=sovereign:sovereign data/ /app/data/
COPY --chown=sovereign:sovereign launcher.py /app/
COPY --chown=sovereign:sovereign runtime_health_check.py /app/
COPY --chown=sovereign:sovereign entrypoint.sh /app/

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV PATH="/home/sovereign/.local/bin:${PATH}"
ENV RUNTIME_HEALTH_CHECK=1
ENV SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}

# Switch to non-root user
USER sovereign

# Enhanced health check using runtime verification script
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python runtime_health_check.py --quick || exit 1

# Entry point: Use the repaired master launch vector
CMD ["python", "launcher.py"]
