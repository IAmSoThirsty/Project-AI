FROM ghcr.io/astral-sh/uv:0.11.22 AS uv

FROM dhi.io/python:3.12-debian12-dev AS base
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_INSTALL_DIR=/opt/uv-python
WORKDIR /app

FROM base AS builder
COPY --from=uv /uv /usr/local/bin/uv
# Cache dependency resolution: copy lock first
COPY uv.lock pyproject.toml .python-version ./
COPY packages ./packages
COPY apps/desktop ./apps/desktop
COPY apps/services ./apps/services
RUN uv sync --frozen --no-dev --package project-ai-api

FROM base AS runtime
# Copy venv from builder
COPY --from=builder --chown=10001:10001 /app/.venv /app/.venv
COPY --from=builder --chown=10001:10001 /opt/uv-python /opt/uv-python
# Copy application code
COPY --chown=10001:10001 README.md LICENSE ./
COPY --chown=10001:10001 packages ./packages
COPY --chown=10001:10001 apps/desktop ./apps/desktop
COPY --chown=10001:10001 apps/services ./apps/services
COPY --chown=10001:10001 docs/reference/DOI_REGISTRY.md ./docs/reference/DOI_REGISTRY.md
COPY --chown=10001:10001 docs/internal/frozen-history/PROJECT-AI_FROZEN_HISTORY.md ./docs/internal/frozen-history/PROJECT-AI_FROZEN_HISTORY.md
COPY --chown=10001:10001 tools/canonical_replay.py tools/verify_frozen_history.py tools/verify_security_relay.py ./tools/
RUN chmod 0755 /app/.venv/bin/uvicorn \
    && mkdir -p /data \
    && chown 10001:10001 /data
USER 10001:10001
HEALTHCHECK --interval=5s --timeout=3s --retries=12 --start-period=5s \
  CMD curl -f http://127.0.0.1:8000/health/live || exit 1
EXPOSE 8000
CMD ["uvicorn", "project_ai_api.app:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
