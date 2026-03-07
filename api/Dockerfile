FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r projectai && useradd -r -g projectai -d /app -s /sbin/nologin projectai

# Install curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY api/ ./api/
COPY src/ ./src/

# Set environment
ENV PYTHONPATH=/app/src:/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -sf http://localhost:8001/health || exit 1

# Run as non-root
RUN chown -R projectai:projectai /app
USER projectai

# Expose port
EXPOSE 8001

# Run with uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]
