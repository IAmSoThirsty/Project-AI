#!/bin/bash
# Production deployment startup script
# Combines base services with logging and persistence layers

set -e

echo "🚀 Starting Project-AI Production Stack..."

# Create .env if not exists
if [ ! -f .env ]; then
    echo "⚠️  Creating .env with default passwords (CHANGE THESE IN PRODUCTION)"
    cat > .env <<EOF
PROJECT_AI_API_TOKEN=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)
GF_SECURITY_ADMIN_PASSWORD=$(openssl rand -hex 16)

POSTGRES_DATA_PATH=./.data/postgres
REDIS_DATA_PATH=./.data/redis
EOF
    chmod 600 .env
    echo "✅ Created .env - review and update passwords!"
fi

# Create data directories
mkdir -p .data/postgres .data/redis

# Load environment
source .env

# Validate compose files
echo "🔍 Validating compose files..."
docker compose -f compose.yaml -f compose.volumes.yaml -f compose.logging.yaml config --quiet

# Start services
echo "📦 Starting base services..."
docker compose up -d --wait --wait-timeout 240 -f compose.yaml

echo "💾 Starting persistence layer..."
docker compose -f compose.volumes.yaml up -d --wait --wait-timeout 120

echo "📊 Starting logging stack..."
docker compose -f compose.logging.yaml up -d --wait --wait-timeout 120

# Health checks
echo "🏥 Running health checks..."
docker compose ps

echo ""
echo "✅ Project-AI Production Stack Started"
echo ""
echo "Services Available:"
echo "  📍 API:           http://127.0.0.1:8000"
echo "  🌐 Docs Portal:   http://127.0.0.1:4173"
echo "  🔬 Proof Portal:  http://127.0.0.1:4174"
echo "  🐘 PostgreSQL:    postgres://project_ai@127.0.0.1:5432/project_ai_state"
echo "  🔴 Redis:         redis://127.0.0.1:6379"
echo "  📊 Grafana:       http://127.0.0.1:3000 (admin/${GF_SECURITY_ADMIN_PASSWORD})"
echo "  📝 Prometheus:    http://127.0.0.1:9090"
echo "  📋 Loki:          http://127.0.0.1:3100"
echo ""
echo "Next: Configure Grafana dashboards and set up log shipping"
