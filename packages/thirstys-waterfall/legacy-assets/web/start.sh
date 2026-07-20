#!/bin/bash
# Thirstys Waterfall Web Interface Startup Script
# Production-grade web server start script

set -e

# Configuration
PYTHON=${PYTHON:-python}
APP_DIR=${APP_DIR:-$(dirname "$0")}
LOG_DIR=${LOG_DIR:-${APP_DIR}/logs}
PID_FILE=${PID_FILE:-${LOG_DIR}/web.pid}

# Create log directory
mkdir -p "$LOG_DIR"

# Activate virtual environment if it exists
if [ -d "${APP_DIR}/.venv" ]; then
    source "${APP_DIR}/.venv/bin/activate"
fi

# Check if running Flask directly (development) or Gunicorn (production)
if [ "${WORKERS:-}" != "" ]; then
    # Production mode with Gunicorn
    echo "Starting Thirstys Waterfall Web Interface (production mode)..."
    echo "Workers: ${WORKERS:-4}"
    echo "Worker class: ${WORKER_CLASS:-sync}"
    echo "Port: ${WEB_PORT:-8080}"
    
    exec gunicorn \
        --workers="${WORKERS:-4}" \
        --worker-class="${WORKER_CLASS:-sync}" \
        --bind="${WEB_HOST:-0.0.0.0}:${WEB_PORT:-8080}" \
        --timeout=120 \
        --access-logfile="${LOG_DIR}/access.log" \
        --error-logfile="${LOG_DIR}/error.log" \
        --log-level="${LOG_LEVEL:-info}" \
        --pid="${PID_FILE}" \
        "app:create_app()"
else
    # Development mode with Flask
    echo "Starting Thirstys Waterfall Web Interface (development mode)..."
    echo "Host: ${WEB_HOST:-0.0.0.0}"
    echo "Port: ${WEB_PORT:-8080}"
    echo "Debug: ${DEBUG:-false}"
    
    exec ${PYTHON} -c "
from app import create_app
app = create_app()
app.run(
    host='${WEB_HOST:-0.0.0.0}',
    port=${WEB_PORT:-8080},
    debug=${DEBUG:-false}
)
"
fi
