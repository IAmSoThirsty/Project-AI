# Database Configuration Guide

**Sovereign Governance Substrate - Complete Database Setup**

---

## Overview

This guide provides complete database connection strings, configuration, and setup instructions for all databases in the Sovereign Governance Substrate.

---

## 1. PostgreSQL - Primary Database

### 1.1 Connection Strings

**Production (Docker Compose):**
```bash

# Orchestrator

DATABASE_URL=postgresql://project_ai:[REDACTED]@postgres:5432/project_ai

# MCP Gateway

MCP_DB_URL=postgresql://project_ai:[REDACTED]@postgres:5432/project_ai
```

**Local Development:**
```bash
DATABASE_URL=postgresql://project_ai:[REDACTED]@localhost:5432/project_ai
```

**Connection with Connection Pool:**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

DATABASE_URL = "postgresql://project_ai:[REDACTED]@postgres:5432/project_ai"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,           # DB_POOL_SIZE
    max_overflow=10,        # DB_MAX_OVERFLOW
    pool_pre_ping=True,     # Verify connections before using
    pool_recycle=3600,      # Recycle connections after 1 hour
    echo=False              # Set to True for SQL logging
)
```

### 1.2 Environment Variables

Add to `.env` file:
```bash

# PostgreSQL Configuration

POSTGRES_DB=project_ai
POSTGRES_USER=project_ai
POSTGRES_PASSWORD=<GENERATE_SECURE_PASSWORD>

# Performance Tuning

POSTGRES_SHARED_BUFFERS=256MB
POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
POSTGRES_MAX_CONNECTIONS=200

# pgvector Configuration

PGVECTOR_DIMENSIONS=1536

# Connection Pooling

DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
```

### 1.3 Generating Secure Password

```bash

# Generate a secure password

python -c "import secrets; print(secrets.token_urlsafe(32))"

# Or use OpenSSL

openssl rand -base64 32
```

### 1.4 Database Initialization

**First-Time Setup:**
```bash

# 1. Start PostgreSQL container

docker-compose -f deploy/single-node-core/docker-compose.yml up -d postgres

# 2. Wait for health check to pass

docker-compose -f deploy/single-node-core/docker-compose.yml ps postgres

# 3. Verify extensions installed

docker exec -it project-ai-postgres psql -U project_ai -d project_ai -c "\dx"

# 4. Check schema migrations

docker exec -it project-ai-postgres psql -U project_ai -d project_ai -c "SELECT * FROM schema_migrations;"
```

### 1.5 Manual Connection (psql)

```bash

# Connect from host

docker exec -it project-ai-postgres psql -U project_ai -d project_ai

# Connect from another container

docker exec -it project-ai-orchestrator psql -h postgres -U project_ai -d project_ai

# Run SQL file

docker exec -i project-ai-postgres psql -U project_ai -d project_ai < schema.sql
```

### 1.6 SQLAlchemy ORM Example

```python
from sqlalchemy import create_engine, Column, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Database URL from environment

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine

engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# Create session factory

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models

Base = declarative_base()

# Example model

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default="now()")

# Usage

def get_user(user_id: uuid.UUID):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()
```

---

## 2. Redis - Cache and Queue

### 2.1 Connection Strings

**Production (Docker Compose):**
```bash

# Orchestrator (Database 0)

REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# MCP Gateway (Database 1)

MCP_REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/1
```

**Local Development:**
```bash
REDIS_URL=redis://:your_password@localhost:6379/0
```

### 2.2 Environment Variables

Add to `.env` file:
```bash

# Redis Configuration

REDIS_PASSWORD=<GENERATE_SECURE_PASSWORD>
REDIS_HOST=localhost              # For local dev
REDIS_PORT=6379
REDIS_DB=0

# Performance Tuning

REDIS_MAX_MEMORY=512mb
REDIS_MAXMEMORY_POLICY=allkeys-lru
REDIS_MAX_CONNECTIONS=50
```

### 2.3 Python Redis Client

```python
import redis
from redis.connection import ConnectionPool
import os

# Connection URL

REDIS_URL = os.getenv("REDIS_URL")

# Create connection pool

pool = ConnectionPool.from_url(
    REDIS_URL,
    max_connections=50,
    decode_responses=True  # Auto-decode bytes to strings
)

# Create Redis client

redis_client = redis.Redis(connection_pool=pool)

# Usage examples

def cache_set(key: str, value: str, ttl: int = 3600):
    """Set cache with TTL"""
    redis_client.setex(key, ttl, value)

def cache_get(key: str) -> str:
    """Get cached value"""
    return redis_client.get(key)

def queue_push(queue_name: str, item: str):
    """Push item to queue"""
    redis_client.lpush(queue_name, item)

def queue_pop(queue_name: str, timeout: int = 5):
    """Pop item from queue (blocking)"""
    result = redis_client.brpop(queue_name, timeout)
    return result[1] if result else None

def pubsub_publish(channel: str, message: str):
    """Publish message to channel"""
    redis_client.publish(channel, message)

def pubsub_subscribe(channel: str):
    """Subscribe to channel"""
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel)
    return pubsub
```

### 2.4 Redis CLI Access

```bash

# Connect from host

docker exec -it project-ai-redis redis-cli -a ${REDIS_PASSWORD}

# Connect from container

docker exec -it project-ai-orchestrator redis-cli -h redis -a ${REDIS_PASSWORD}

# Common commands

127.0.0.1:6379> INFO
127.0.0.1:6379> DBSIZE
127.0.0.1:6379> KEYS *
127.0.0.1:6379> GET key_name
127.0.0.1:6379> SET key_name value
127.0.0.1:6379> DEL key_name
```

---

## 3. SQLite - Embedded Databases

### 3.1 Connection Strings

**Secure Database:**
```python
db_path = "data/secure.db"

# or

db_path = os.path.join(os.getenv("DATA_DIR", "data"), "secure.db")
```

**Learning Requests Database:**
```python
db_path = "data/learning_requests/requests.db"
```

### 3.2 Python SQLite Example

```python
import sqlite3
from contextlib import contextmanager
from pathlib import Path

class SecureDatabaseManager:
    def __init__(self, db_path: str = "data/secure.db"):
        self.db_path = db_path

        # Ensure directory exists

        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dict-like objects
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()):
        """Execute a parameterized query"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_update(self, query: str, params: tuple = ()):
        """Execute an UPDATE/INSERT/DELETE query"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount

# Usage

db = SecureDatabaseManager("data/secure.db")

# Insert with parameters (prevents SQL injection)

db.execute_update(
    "INSERT INTO users (username, email) VALUES (?, ?)",
    ("alice", "alice@example.com")
)

# Query with parameters

users = db.execute_query(
    "SELECT * FROM users WHERE username = ?",
    ("alice",)
)
```

### 3.3 Migration to PostgreSQL

If you need to migrate from SQLite to PostgreSQL:

```python
import sqlite3
import psycopg2
from psycopg2.extras import execute_values

def migrate_sqlite_to_postgres(
    sqlite_path: str,
    postgres_url: str,
    table_name: str
):

    # Connect to SQLite

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    
    # Connect to PostgreSQL

    pg_conn = psycopg2.connect(postgres_url)
    
    try:

        # Read from SQLite

        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute(f"SELECT * FROM {table_name}")
        rows = sqlite_cursor.fetchall()
        
        # Insert into PostgreSQL

        pg_cursor = pg_conn.cursor()
        columns = rows[0].keys()
        values = [tuple(row) for row in rows]
        
        query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s"
        execute_values(pg_cursor, query, values)
        
        pg_conn.commit()
        print(f"Migrated {len(rows)} rows from {table_name}")
    
    finally:
        sqlite_conn.close()
        pg_conn.close()
```

---

## 4. Temporal Database

### 4.1 Connection String

**Production:**
```bash
TEMPORAL_DB_URL=postgresql://temporal:[REDACTED]@temporal-postgresql:5432/temporal
```

### 4.2 Environment Variables

```bash

# Temporal Configuration

TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
TEMPORAL_DB_USER=temporal
TEMPORAL_DB_PASSWORD=temporal
TEMPORAL_DB_NAME=temporal
```

---

## 5. Connection Testing

### 5.1 Test Script

Create `scripts/test_connections.py`:

```python
#!/usr/bin/env python3
"""Test all database connections"""

import os
import sys
from sqlalchemy import create_engine, text
import redis
import sqlite3

def test_postgresql():
    """Test PostgreSQL connection"""
    try:
        url = os.getenv("DATABASE_URL")
        engine = create_engine(url)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✓ PostgreSQL connected: {version[:50]}...")
            return True
    except Exception as e:
        print(f"✗ PostgreSQL failed: {e}")
        return False

def test_redis():
    """Test Redis connection"""
    try:
        url = os.getenv("REDIS_URL")
        r = redis.from_url(url)
        r.ping()
        info = r.info()
        print(f"✓ Redis connected: version {info['redis_version']}")
        return True
    except Exception as e:
        print(f"✗ Redis failed: {e}")
        return False

def test_sqlite():
    """Test SQLite connection"""
    try:
        db_path = "data/secure.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version()")
        version = cursor.fetchone()[0]
        conn.close()
        print(f"✓ SQLite connected: version {version}")
        return True
    except Exception as e:
        print(f"✗ SQLite failed: {e}")
        return False

def main():
    print("Testing database connections...\n")
    
    results = {
        "PostgreSQL": test_postgresql(),
        "Redis": test_redis(),
        "SQLite": test_sqlite()
    }
    
    print(f"\nResults: {sum(results.values())}/{len(results)} passed")
    
    if not all(results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()
```

Run the test:
```bash
python scripts/test_connections.py
```

---

## 6. Backup and Recovery

### 6.1 PostgreSQL Backup

**Automated backup script:**
```bash
#!/bin/bash

# scripts/backup_postgres.sh

BACKUP_DIR="data/backups/postgres"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/project_ai_${DATE}.dump"

mkdir -p "$BACKUP_DIR"

docker exec project-ai-postgres pg_dump \
    -U project_ai \
    -Fc \
    -f "/tmp/backup.dump" \
    project_ai

docker cp project-ai-postgres:/tmp/backup.dump "$BACKUP_FILE"

echo "Backup created: $BACKUP_FILE"

# Compress and cleanup old backups (keep last 7 days)

gzip "$BACKUP_FILE"
find "$BACKUP_DIR" -name "*.dump.gz" -mtime +7 -delete
```

**Restore from backup:**
```bash
#!/bin/bash

# scripts/restore_postgres.sh

BACKUP_FILE="$1"

if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

gunzip -c "$BACKUP_FILE" > /tmp/restore.dump

docker cp /tmp/restore.dump project-ai-postgres:/tmp/restore.dump

docker exec project-ai-postgres pg_restore \
    -U project_ai \
    -d project_ai \
    -c \
    /tmp/restore.dump

rm /tmp/restore.dump

echo "Database restored from: $BACKUP_FILE"
```

### 6.2 Redis Backup

```bash
#!/bin/bash

# scripts/backup_redis.sh

BACKUP_DIR="data/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Trigger background save

docker exec project-ai-redis redis-cli -a "$REDIS_PASSWORD" BGSAVE

# Wait for save to complete

sleep 5

# Copy RDB file

docker cp project-ai-redis:/data/dump.rdb "${BACKUP_DIR}/dump_${DATE}.rdb"

# Copy AOF file

docker cp project-ai-redis:/data/appendonly.aof "${BACKUP_DIR}/appendonly_${DATE}.aof"

echo "Redis backup created: ${BACKUP_DIR}"
```

---

## 7. Troubleshooting

### 7.1 PostgreSQL Issues

**Connection refused:**
```bash

# Check if PostgreSQL is running

docker ps | grep postgres

# Check logs

docker logs project-ai-postgres

# Verify network

docker network inspect project-ai-core-network
```

**Authentication failed:**
```bash

# Verify password

echo $POSTGRES_PASSWORD

# Reset password

docker exec -it project-ai-postgres psql -U postgres
ALTER USER project_ai WITH PASSWORD 'new_password';
```

### 7.2 Redis Issues

**Connection timeout:**
```bash

# Check Redis status

docker exec -it project-ai-redis redis-cli -a "$REDIS_PASSWORD" PING

# Check memory

docker exec -it project-ai-redis redis-cli -a "$REDIS_PASSWORD" INFO memory

# Check slow log

docker exec -it project-ai-redis redis-cli -a "$REDIS_PASSWORD" SLOWLOG GET 10
```

### 7.3 SQLite Issues

**Database locked:**
```python

# Use WAL mode to prevent locking

import sqlite3
conn = sqlite3.connect("data/secure.db")
conn.execute("PRAGMA journal_mode=WAL")
conn.close()
```

---

## 8. Security Best Practices

1. **Never commit passwords to git**
   - Use `.env` file (in `.gitignore`)
   - Use secrets management (Docker secrets, Vault, etc.)

2. **Use strong passwords**
   ```bash
   # Generate secure password
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

3. **Enable SSL/TLS for production**
   - PostgreSQL: `sslmode=require`
   - Redis: `--tls` flag

4. **Limit database user permissions**
   ```sql
   -- PostgreSQL: Create read-only user
   CREATE USER readonly WITH PASSWORD 'password';
   GRANT CONNECT ON DATABASE project_ai TO readonly;
   GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
   ```

5. **Regular backups**
   - Automated daily backups
   - Test restore procedures
   - Off-site backup storage

---

**END OF DATABASE CONFIGURATION GUIDE**
