FROM ghcr.io/astral-sh/uv:0.11.22 AS uv

FROM dhi.io/python:3.12-debian12-dev AS base
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy
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
COPY --from=builder /app/.venv /app/.venv
# Copy application code
COPY README.md LICENSE ./
COPY packages ./packages
COPY apps/desktop ./apps/desktop
COPY apps/services ./apps/services
COPY docs/reference/DOI_REGISTRY.md ./docs/reference/DOI_REGISTRY.md
RUN mkdir -p /data && chown -R 10001:10001 /app /data
USER 10001:10001
HEALTHCHECK --interval=5s --timeout=3s --retries=12 --start-period=5s \
  CMD curl -f http://127.0.0.1:8000/health/live || exit 1
EXPOSE 8000
CMD ["uvicorn", "project_ai_api.app:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
