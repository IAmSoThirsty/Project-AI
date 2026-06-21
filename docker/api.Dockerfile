FROM ghcr.io/astral-sh/uv:0.11.22 AS uv

FROM python:3.12.10-slim-bookworm AS runtime
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=uv /uv /usr/local/bin/uv
COPY pyproject.toml uv.lock README.md LICENSE .python-version ./
COPY packages ./packages
COPY apps/desktop ./apps/desktop
COPY apps/services ./apps/services
COPY docs/reference/DOI_REGISTRY.md ./docs/reference/DOI_REGISTRY.md
RUN uv sync --frozen --no-dev --package project-ai-api \
    && mkdir -p /data \
    && chown -R 10001:10001 /app /data
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "project_ai_api.app:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]

