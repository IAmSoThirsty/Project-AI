<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!--                                         [2026-03-03 13:45] -->
<!--                                        Productivity: Active -->
# Project-AI Single-Node Core Stack Deployment

## 🚀 Overview

This directory contains a complete, production-ready deployment recipe for Project-AI's single-node core stack. It provides a turnkey, fully-integrated AI infrastructure with robust architecture, security boundaries, and extensibility.

### Architecture Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Project-AI Core Stack                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Orchestrator │◄─┤ MCP Gateway  │◄─┤   Agents &   │          │
│  │    (Core)    │  │              │  │    Tools     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────────────┘          │
│         │                 │                                      │
│         ▼                 ▼                                      │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │  PostgreSQL  │  │    Redis     │                            │
│  │  (pgvector)  │  │ (Queue/Bus)  │                            │
│  └──────────────┘  └──────────────┘                            │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### What's Included

- ✅ **Docker Compose Stack**: Fully-wired services with health checks and networking
- ✅ **PostgreSQL with pgvector**: Vector database for AI embeddings and memory
- ✅ **Redis**: Message queue, cache, and pub/sub bus
- ✅ **MCP Gateway**: Model Context Protocol gateway for agent communication
- ✅ **Core Orchestrator**: Project-AI main application
- ✅ **Production Configuration**: Environment files, secrets management, monitoring
- ✅ **Extensibility**: Ready for worker processes and horizontal scaling
- ✅ **Security**: Authentication, encryption, audit logging
- ✅ **Health Monitoring**: Comprehensive health checks and observability

## 📋 Prerequisites

### System Requirements

- **OS**: Linux (Ubuntu 20.04+), macOS, Windows with WSL2
- **Docker**: 20.10+ with Docker Compose v2
- **CPU**: 4+ cores recommended
- **RAM**: 8GB minimum, 16GB recommended
- **Disk**: 20GB+ available space

### Software Dependencies

```bash

# Install Docker and Docker Compose

curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Verify installation

docker --version
docker compose version
```

## 🔧 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI/deploy/single-node-core
```

### 2. Configure Environment

```bash

# Copy and edit environment file

cp env/project-ai-core.env env/.env
nano env/.env

# Generate required secrets

python3 << 'EOF'
import secrets
from cryptography.fernet import Fernet

print("SECRET_KEY=" + secrets.token_urlsafe(32))
print("FERNET_KEY=" + Fernet.generate_key().decode())
print("POSTGRES_PASSWORD=" + secrets.token_urlsafe(24))
print("REDIS_PASSWORD=" + secrets.token_urlsafe(24))
print("MCP_API_KEY=" + secrets.token_hex(32))
EOF

# Add API keys to .env

# - OPENAI_API_KEY

# - HUGGINGFACE_API_KEY (optional)

# - Other service keys as needed

```

### 3. Configure MCP Secrets

```bash

# Copy and edit MCP secrets

cp mcp/secrets.env mcp/.secrets.env
nano mcp/.secrets.env

# Generate additional secrets for MCP

openssl rand -hex 32  # MCP_API_KEY
openssl rand -hex 32  # MCP_ADMIN_API_KEY
openssl rand -hex 64  # MCP_JWT_SECRET
```

### 4. Launch Stack

```bash

# Start all services

docker compose up -d

# View logs

docker compose logs -f

# Check service health

docker compose ps
```

### 5. Verify Deployment

```bash

# Check PostgreSQL

docker compose exec postgres psql -U project_ai -c "SELECT extname, extversion FROM pg_extension WHERE extname IN ('vector', 'pg_trgm');"

# Check Redis

docker compose exec redis redis-cli -a "${REDIS_PASSWORD}" ping

# Check orchestrator health

curl http://localhost:8000/health

# Check MCP gateway

curl http://localhost:9000/health
```

## 📁 Directory Structure

```
deploy/single-node-core/
├── docker-compose.yml           # Main compose file
├── README.md                    # This file
│
├── env/
│   ├── project-ai-core.env     # Main environment configuration
│   └── .env                    # Local overrides (gitignored)
│
├── mcp/
│   ├── config.yaml             # MCP gateway configuration
│   ├── registry.yaml           # MCP server registry
│   ├── secrets.env             # MCP credentials template
│   ├── .secrets.env            # Actual secrets (gitignored)
│   └── catalogs/
│       └── project-ai.yaml     # Project-AI tool catalog
│
├── postgres/
│   ├── init/
│   │   └── 01_extensions.sql  # Database initialization
│   └── postgresql.conf         # Custom postgres config (optional)
│
├── redis/
│   └── redis.conf              # Redis configuration
│
└── logs/                        # Application logs (gitignored)
```

## 🔐 Security Configuration

### Secrets Management

**Development**:

- Store secrets in `.env` files (not committed)
- Use strong passwords (20+ characters)
- Rotate credentials quarterly

**Production**:

- Use external secrets managers:
  - HashiCorp Vault
  - AWS Secrets Manager
  - Azure Key Vault
  - Google Secret Manager
- Enable audit logging for all secret access
- Implement automated rotation

### Network Security

```yaml

# All services on isolated bridge network

networks:
  project-ai-core:
    driver: bridge
    internal: false  # Set to true for full isolation
```

### File Permissions

```bash

# Secure sensitive files

chmod 600 env/.env
chmod 600 mcp/.secrets.env
chown $USER:$USER env/.env mcp/.secrets.env
```

### Firewall Configuration

```bash

# Only expose necessary ports

# Orchestrator: 5000, 8000, 8001

# PostgreSQL: 5432 (only if external access needed)

# Redis: 6379 (only if external access needed)

# MCP Gateway: 9000, 9001

# Example UFW rules

sudo ufw allow 5000/tcp
sudo ufw allow 8000:8001/tcp
sudo ufw deny 5432/tcp  # Block external DB access
sudo ufw deny 6379/tcp  # Block external Redis access
```

## 📊 Monitoring and Observability

### Health Checks

All services include comprehensive health checks:

```bash

# View service health status

docker compose ps

# Check individual service health

docker inspect project-ai-orchestrator | jq '.[0].State.Health'
```

### Logs

```bash

# All services

docker compose logs -f

# Specific service

docker compose logs -f project-ai-orchestrator

# With timestamps

docker compose logs -f --timestamps

# Last 100 lines

docker compose logs --tail=100
```

### Metrics

Access Prometheus metrics:

- Orchestrator: `http://localhost:8001/metrics`
- MCP Gateway: `http://localhost:9001/metrics`

### Database Monitoring

```bash

# PostgreSQL stats

docker compose exec postgres psql -U project_ai -c "
SELECT
    datname,
    numbackends as connections,
    xact_commit as commits,
    xact_rollback as rollbacks,
    blks_read as disk_reads,
    blks_hit as cache_hits
FROM pg_stat_database
WHERE datname = 'project_ai';
"

# Redis info

docker compose exec redis redis-cli -a "${REDIS_PASSWORD}" info stats
```

## 🔄 Operational Procedures

### Starting and Stopping

```bash

# Start all services

docker compose up -d

# Stop all services

docker compose down

# Stop and remove volumes (⚠️ destroys data)

docker compose down -v

# Restart specific service

docker compose restart project-ai-orchestrator
```

### Scaling Workers

```bash

# Add worker processes

docker compose up -d --scale worker=3

# Or edit docker-compose.yml to add explicit worker services

```

### Backups

#### PostgreSQL Backup

```bash

# Manual backup

docker compose exec postgres pg_dump -U project_ai project_ai > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup

docker compose exec -T postgres psql -U project_ai project_ai < backup_20240101_120000.sql

# Automated backup script

cat > backup.sh << 'EOF'

#!/bin/bash

BACKUP_DIR="./backups/postgres"
mkdir -p "$BACKUP_DIR"
docker compose exec -T postgres pg_dump -U project_ai project_ai | gzip > "$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql.gz"
find "$BACKUP_DIR" -mtime +30 -delete  # Keep 30 days
EOF
chmod +x backup.sh

# Add to cron

crontab -e

# Add: 0 2 * * * /path/to/backup.sh

```

#### Redis Backup

```bash

# Manual backup (AOF + RDB)

docker compose exec redis redis-cli -a "${REDIS_PASSWORD}" BGSAVE
docker compose cp redis:/data/dump.rdb ./backups/redis/dump.rdb
docker compose cp redis:/data/appendonly.aof ./backups/redis/appendonly.aof

# Restore

docker compose down
cp ./backups/redis/* ./volumes/redis-data/
docker compose up -d redis
```

### Database Migrations

```bash

# Run migrations

docker compose exec project-ai-orchestrator alembic upgrade head

# Create new migration

docker compose exec project-ai-orchestrator alembic revision --autogenerate -m "description"

# Rollback migration

docker compose exec project-ai-orchestrator alembic downgrade -1
```

### Log Rotation

```bash

# Configure Docker log rotation

cat > /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

sudo systemctl restart docker
```

## 🧪 Testing

### Smoke Tests

```bash

# Test PostgreSQL connection

docker compose exec postgres psql -U project_ai -c "SELECT 1;"

# Test Redis connection

docker compose exec redis redis-cli -a "${REDIS_PASSWORD}" ping

# Test orchestrator API

curl -f http://localhost:8000/health || echo "Health check failed"

# Test MCP gateway

curl -f http://localhost:9000/health || echo "MCP health check failed"
```

### Integration Tests

```bash

# Run integration tests

docker compose exec project-ai-orchestrator pytest tests/integration/

# Test MCP tool execution

docker compose exec project-ai-orchestrator python -c "
from app.core.mcp_server import ProjectAIMCPServer
server = ProjectAIMCPServer()
print('MCP Server initialized successfully')
"
```

## 🚀 Performance Tuning

### PostgreSQL Optimization

Edit `postgres/postgresql.conf`:
```ini

# Increase based on available RAM

shared_buffers = 512MB
effective_cache_size = 2GB
work_mem = 16MB
maintenance_work_mem = 128MB

# Connection pooling

max_connections = 200

# Query planning

random_page_cost = 1.1  # For SSD
effective_io_concurrency = 200
```

### Redis Optimization

Edit `redis/redis.conf`:
```ini

# Enable threaded I/O for high throughput

io-threads 4
io-threads-do-reads yes

# Increase maxmemory

maxmemory 1gb

# Tune eviction

maxmemory-policy allkeys-lfu
```

### Docker Resource Limits

Edit `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 4G
    reservations:
      cpus: '2'
      memory: 2G
```

## 🔧 Troubleshooting

### Common Issues

#### Services Won't Start

```bash

# Check logs

docker compose logs

# Check disk space

df -h

# Check Docker daemon

sudo systemctl status docker

# Rebuild images

docker compose build --no-cache
```

#### PostgreSQL Connection Errors

```bash

# Check PostgreSQL logs

docker compose logs postgres

# Verify credentials

echo $POSTGRES_PASSWORD

# Test connection

docker compose exec postgres psql -U project_ai -c "\l"

# Check extensions

docker compose exec postgres psql -U project_ai -c "SELECT * FROM pg_extension;"
```

#### Redis Connection Errors

```bash

# Check Redis logs

docker compose logs redis

# Test authentication

docker compose exec redis redis-cli -a "${REDIS_PASSWORD}" ping

# Check memory usage

docker compose exec redis redis-cli -a "${REDIS_PASSWORD}" info memory
```

#### Out of Memory

```bash

# Check container memory

docker stats

# Increase Docker memory limit (Docker Desktop)

# Settings > Resources > Memory

# Add swap for Linux

sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

### Getting Help

- **Documentation**: `docs/` directory
- **Issues**: https://github.com/IAmSoThirsty/Project-AI/issues
- **Discussions**: https://github.com/IAmSoThirsty/Project-AI/discussions

## 📚 Additional Resources

### Documentation

- [PRODUCTION_DEPLOYMENT.md](../../PRODUCTION_DEPLOYMENT.md) - Production deployment guide
- [DEVELOPER_QUICK_REFERENCE.md](../../DEVELOPER_QUICK_REFERENCE.md) - Developer reference
- [AI_PERSONA_IMPLEMENTATION.md](../../docs/AI_PERSONA_IMPLEMENTATION.md) - AI persona details
- [LEARNING_REQUEST_IMPLEMENTATION.md](../../docs/LEARNING_REQUEST_IMPLEMENTATION.md) - Learning system

### External Documentation

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [Redis Documentation](https://redis.io/documentation)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## 📝 License

MIT License - see [LICENSE](../../LICENSE) file

---

**Project-AI** - Production-Ready AI Platform with Civilization-Tier Architecture
