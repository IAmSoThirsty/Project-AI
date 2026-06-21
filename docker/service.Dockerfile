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
RUN uv sync --frozen --no-dev --package project-ai-service-host \
    && chown -R 10001:10001 /app
USER 10001:10001
EXPOSE 8000
CMD ["uvicorn", "project_ai_services.app:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]

