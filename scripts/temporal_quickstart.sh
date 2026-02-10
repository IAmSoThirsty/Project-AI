#!/bin/bash
# Quick Start Script for Temporal.io Integration
# 
# This script provides a one-command setup for Temporal.io in Project-AI

set -e

echo "=================================="
echo "Temporal.io Quick Start"
echo "=================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✓ Docker is running"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✓ Docker Compose is available"
echo ""

# Initialize configuration
echo "Initializing Temporal configuration..."
python3 scripts/setup_temporal.py init

echo ""
echo "Starting Temporal services..."
echo "  - Temporal Server (localhost:7233)"
echo "  - PostgreSQL Database"
echo "  - Temporal Web UI (http://localhost:8233)"
echo "  - Temporal Worker"
echo ""

# Start services
docker-compose up -d temporal temporal-postgresql temporal-worker

echo ""
echo "Waiting for services to be ready..."
sleep 10

# Check status
echo ""
echo "Service Status:"
docker-compose ps | grep temporal

echo ""
echo "=================================="
echo "✓ Temporal.io is ready!"
echo "=================================="
echo ""
echo "Next steps:"
echo "  1. Open Web UI: http://localhost:8233"
echo "  2. Run examples:"
echo "     cd examples/temporal"
echo "     PYTHONPATH=../../src python learning_workflow_example.py"
echo ""
echo "  3. Check logs:"
echo "     docker-compose logs -f temporal-worker"
echo ""
echo "  4. Stop services:"
echo "     docker-compose stop temporal temporal-postgresql temporal-worker"
echo ""
echo "Documentation: docs/TEMPORAL_SETUP.md"
echo "=================================="
