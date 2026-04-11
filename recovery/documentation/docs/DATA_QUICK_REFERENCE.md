# Data Path Quick Reference

**Quick access guide for Sovereign Governance Substrate data architecture**

---

## 🚀 Quick Start

### 1. Initialize Data Directories

```bash
chmod +x data_init.sh
./data_init.sh
```

### 2. Set Database Passwords

```bash

# Generate passwords

python -c "import secrets; print('POSTGRES_PASSWORD='[REDACTED]" >> .env
python -c "import secrets; print('REDIS_PASSWORD='[REDACTED]" >> .env
```

### 3. Start Services

```bash
cd deploy/single-node-core
docker-compose up -d
```

### 4. Verify Connections

```bash

# PostgreSQL

docker exec -it project-ai-postgres psql -U project_ai -d project_ai -c "SELECT version();"

# Redis

docker exec -it project-ai-redis redis-cli -a "$REDIS_PASSWORD" PING
```

---

## 📁 Data Directories

### Core Directories (Already Exist)

```
data/
├── ai_persona/               # AI persona configurations
├── audit/                    # Audit trail files
├── black_vault_secure/       # Secure vault storage
├── migrations/               # Database migrations
├── security/                 # Security configurations
└── ... (38 total)
```

### New Directories (Created by data_init.sh)

```
data/
├── uploads/                  # File uploads
│   ├── attachments/
│   ├── documents/
│   └── images/
├── cache/                    # Application cache
│   ├── embeddings/
│   └── api_responses/
├── backups/                  # Backup storage
│   ├── postgres/
│   └── redis/
└── ... (28 total)
```

---

## 🗄️ Databases

### PostgreSQL

```bash
Host: postgres (or localhost:5432)
Database: project_ai
User: project_ai
Password: ${POSTGRES_PASSWORD}

# Connection URL

postgresql://project_ai:[REDACTED]@postgres:5432/project_ai
```

**Common Commands:**
```bash

# Connect

docker exec -it project-ai-postgres psql -U project_ai -d project_ai

# List tables

\dt

# Check extensions

\dx

# View migrations

SELECT * FROM schema_migrations;
```

### Redis

```bash
Host: redis (or localhost:6379)
Password: ${REDIS_PASSWORD}
Database: 0 (Orchestrator) or 1 (MCP Gateway)

# Connection URL

redis://:${REDIS_PASSWORD}@redis:6379/0
```

**Common Commands:**
```bash

# Connect

docker exec -it project-ai-redis redis-cli -a "$REDIS_PASSWORD"

# Check status

INFO

# List keys

KEYS *

# Get database size

DBSIZE
```

### SQLite

```bash

# Local development database

Path: data/secure.db

# Connect

sqlite3 data/secure.db

# List tables

.tables

# View schema

.schema users
```

---

## 🔄 Backup and Restore

### PostgreSQL Backup

```bash

# Backup

docker exec project-ai-postgres pg_dump -U project_ai -Fc project_ai > backup.dump

# Restore

docker exec -i project-ai-postgres pg_restore -U project_ai -d project_ai -c < backup.dump
```

### Redis Backup

```bash

# Trigger save

docker exec project-ai-redis redis-cli -a "$REDIS_PASSWORD" BGSAVE

# Copy data

docker cp project-ai-redis:/data/dump.rdb ./redis-backup.rdb
docker cp project-ai-redis:/data/appendonly.aof ./redis-backup.aof
```

---

## 🔍 Monitoring

### Health Checks

```bash

# All services

docker-compose -f deploy/single-node-core/docker-compose.yml ps

# PostgreSQL

docker exec project-ai-postgres pg_isready -U project_ai

# Redis

docker exec project-ai-redis redis-cli -a "$REDIS_PASSWORD" PING

# Orchestrator

curl http://localhost:8000/health
```

### Logs

```bash

# View logs

docker logs project-ai-postgres
docker logs project-ai-redis
docker logs project-ai-orchestrator

# Follow logs

docker logs -f project-ai-orchestrator

# All services

docker-compose -f deploy/single-node-core/docker-compose.yml logs -f
```

---

## 🐍 Python Examples

### PostgreSQL (SQLAlchemy)

```python
from sqlalchemy import create_engine
import os

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

with engine.connect() as conn:
    result = conn.execute("SELECT version()")
    print(result.fetchone())
```

### Redis

```python
import redis
import os

REDIS_URL = os.getenv("REDIS_URL")
r = redis.from_url(REDIS_URL, decode_responses=True)

# Set/Get

r.setex("key", 3600, "value")  # TTL: 1 hour
value = r.get("key")

# Queue

r.lpush("queue", "task1")
task = r.brpop("queue", timeout=5)
```

### SQLite

```python
import sqlite3

conn = sqlite3.connect("data/secure.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM users LIMIT 10")
rows = cursor.fetchall()
conn.close()
```

---

## 🛠️ Troubleshooting

### PostgreSQL Issues

```bash

# Connection refused

docker ps | grep postgres  # Check if running
docker logs project-ai-postgres  # Check logs

# Reset password

docker exec -it project-ai-postgres psql -U postgres
ALTER USER project_ai WITH PASSWORD 'new_password';
```

### Redis Issues

```bash

# Memory issues

docker exec project-ai-redis redis-cli -a "$REDIS_PASSWORD" INFO memory

# Check slow queries

docker exec project-ai-redis redis-cli -a "$REDIS_PASSWORD" SLOWLOG GET 10

# Clear database

docker exec project-ai-redis redis-cli -a "$REDIS_PASSWORD" FLUSHDB
```

### Disk Space

```bash

# Check volume sizes

docker system df -v

# Check data directory

du -sh data/*

# Clean up

docker system prune -a
```

---

## 📚 Documentation Files

| File | Description |
|------|-------------|
| `DATA_ARCHITECTURE_REPORT.md` | Complete architecture analysis (13 sections) |
| `DATA_FLOW_DIAGRAM.md` | Visual data flow diagrams (7 flows) |
| `DATABASE_CONFIG.md` | Database configuration and examples |
| `DATA_PATH_ARCHITECT_COMPLETION.md` | Implementation summary |
| `data_init.sh` | Directory initialization script |

---

## 🔐 Environment Variables

**Required in `.env` file:**
```bash

# PostgreSQL

POSTGRES_DB=project_ai
POSTGRES_USER=project_ai
POSTGRES_PASSWORD=<generate_secure_password>
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10

# Redis

REDIS_PASSWORD=<generate_secure_password>
REDIS_MAX_MEMORY=512mb
REDIS_MAX_CONNECTIONS=50

# Data Paths

DATA_DIR=/app/data
LOG_DIR=/app/logs
CONFIG_DIR=/app/config

# Database URLs

DATABASE_URL=postgresql://project_ai:[REDACTED]@postgres:5432/project_ai
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
```

---

## ⚡ Common Tasks

### Create Database User

```sql
-- PostgreSQL
CREATE USER newuser WITH PASSWORD 'password';
GRANT CONNECT ON DATABASE project_ai TO newuser;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO newuser;
```

### Migrate SQLite to PostgreSQL

```python

# See DATABASE_CONFIG.md section 3.3 for full script

from scripts.migrate_db import migrate_sqlite_to_postgres

migrate_sqlite_to_postgres(
    "data/secure.db",
    "postgresql://project_ai:[REDACTED]@postgres:5432/project_ai",
    "users"
)
```

### Clean Old Cache

```bash

# Redis (delete keys older than 1 day)

docker exec project-ai-redis redis-cli -a "$REDIS_PASSWORD" --scan --pattern "cache:*" | \
  xargs docker exec -i project-ai-redis redis-cli -a "$REDIS_PASSWORD" DEL

# File cache

find data/cache -type f -mtime +7 -delete
```

### View Database Size

```sql
-- PostgreSQL
SELECT pg_size_pretty(pg_database_size('project_ai'));

-- Per table
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

---

## 🎯 Production Checklist

- [ ] Run `data_init.sh` to create directories
- [ ] Set secure passwords in `.env`
- [ ] Test all database connections
- [ ] Configure automated backups
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Test backup restoration
- [ ] Enable SSL/TLS for databases
- [ ] Configure log rotation
- [ ] Set up data retention policies
- [ ] Document disaster recovery plan

---

## 📞 Need Help?

1. **Read the docs**: Check `DATA_ARCHITECTURE_REPORT.md` first
2. **Database issues**: See `DATABASE_CONFIG.md`
3. **Data flows**: Review `DATA_FLOW_DIAGRAM.md`
4. **Check logs**: `docker logs <container_name>`
5. **Health checks**: `curl http://localhost:8000/health`

---

**Last Updated:** 2026-03-03  
**Version:** 1.0  
**Maintained by:** Data Path Architect
