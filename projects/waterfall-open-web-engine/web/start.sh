#!/bin/bash
# Thirsty's Waterfall Web Interface Startup Script
# ================================================

set -e

echo "Starting Thirsty's Waterfall Web Interface..."

# Change to web directory
cd /app/web

# Add current directory to PYTHONPATH
export PYTHONPATH=/app/web:$PYTHONPATH

# Set environment variables
export WEB_HOST=${WEB_HOST:-"0.0.0.0"}
export WEB_PORT=${WEB_PORT:-"8080"}
export DEBUG=${DEBUG:-"False"}

echo "Starting web server on ${WEB_HOST}:${WEB_PORT}..."
echo "Python path: $PYTHONPATH"

# Production: Use Gunicorn WSGI server
# Using sync workers for now (simpler, will add gevent later for WebSockets)
exec python -m gunicorn \
    --bind "${WEB_HOST}:${WEB_PORT}" \
    --workers "${WORKERS:-4}" \
    --timeout 120 \
    --graceful-timeout 30 \
    --keep-alive 5 \
    --log-level "${LOG_LEVEL:-info}" \
    --access-logfile - \
    --error-logfile - \
    app:app
