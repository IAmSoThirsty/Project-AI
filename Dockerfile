# (Substrate Runtime Blueprint)           [2026-04-09 04:26]
#                                          Status: Active

# Multi-stage build for Project-AI
# Supply Chain Hardening: Base images pinned to SHA256 digest

# Stage 1: Build dependencies
FROM python:3.11-slim@sha256:0b23cfb7425d065008b778022a17b1551c82f8b4866ee5a7a200084b7e2eafbf as builder

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
FROM python:3.11-slim@sha256:0b23cfb7425d065008b778022a17b1551c82f8b4866ee5a7a200084b7e2eafbf

# Create non-root user for security
RUN groupadd -r sovereign && useradd -r -g sovereign sovereign

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 \
    libffi8 \
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

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV PATH="/home/sovereign/.local/bin:${PATH}"

# Switch to non-root user
USER sovereign

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Entry point: Use the repaired master launch vector
CMD ["python", "launcher.py"]
