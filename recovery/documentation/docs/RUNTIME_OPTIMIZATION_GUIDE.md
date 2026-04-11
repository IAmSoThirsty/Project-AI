# Runtime Optimization Guide

**Document Version**: 1.0  
**Target Audience**: DevOps Engineers, Platform Engineers, Production Deployment Teams  
**Last Updated**: 2026-04-09

---

## Table of Contents

1. [Python Runtime Optimization](#1-python-runtime-optimization)
2. [ASGI Server Optimization](#2-asgi-server-optimization)
3. [Database Performance Tuning](#3-database-performance-tuning)
4. [Caching Strategies](#4-caching-strategies)
5. [Resource Limits](#5-resource-limits)
6. [Monitoring and Profiling](#6-monitoring-and-profiling)
7. [Production Deployment](#7-production-deployment)

---

## 1. Python Runtime Optimization

### 1.1 Interpreter Flags

**Development**:
```bash

# Unbuffered output for real-time logging

python -u src/app/main.py

# Or set environment variable

export PYTHONUNBUFFERED=1
python src/app/main.py
```

**Production**:
```bash

# Enable optimizations (removes assert, sets __debug__=False)

python -O src/app/main.py

# Or set environment variable

export PYTHONOPTIMIZE=1
python src/app/main.py
```

**⚠️ Warning**: Do NOT use `-OO` (double optimization) as it removes docstrings, which breaks many libraries including FastAPI/Pydantic.

### 1.2 Bytecode Compilation

**Pre-compile Python files** for faster startup:
```bash

# Compile all Python files to .pyc

python -m compileall src/

# Verify compilation

find src/ -name "*.pyc" | wc -l
```

**Docker optimization**:
```dockerfile

# In Dockerfile after COPY

RUN python -m compileall src/
```

### 1.3 Import Optimization

**Lazy imports** for optional features:
```python

# Bad: Import at module level

import torch
import transformers

# Good: Import only when needed

def load_model():
    import torch
    import transformers

    # ...

```

**Use `importlib` for conditional imports**:
```python
from importlib import import_module

def get_backend(backend_name):
    return import_module(f'backends.{backend_name}')
```

### 1.4 Memory Management

**Configure memory allocator**:
```bash

# Use system malloc (faster, less fragmentation)

export PYTHONMALLOC=malloc
```

**Memory profiling**:
```bash

# Install memory_profiler

pip install memory-profiler

# Profile function

python -m memory_profiler script.py

# Decorator-based profiling

@profile
def my_function():

    # ...

```

---

## 2. ASGI Server Optimization

### 2.1 Uvicorn Configuration

**Production setup** (recommended):
```bash
uvicorn src.app.main:app \
  --host 0.0.0.0 \
  --port 8001 \
  --workers 4 \
  --loop uvloop \
  --http httptools \
  --log-level warning \
  --no-access-log \
  --proxy-headers \
  --forwarded-allow-ips='*' \
  --timeout-keep-alive 5
```

**Worker calculation**:
```python
import os
workers = (2 * os.cpu_count()) + 1
```

**Performance flags explained**:

- `--loop uvloop`: Use high-performance event loop (up to 2-4x faster)
- `--http httptools`: Use optimized HTTP parser (written in C)
- `--no-access-log`: Reduce I/O overhead (use reverse proxy logs instead)
- `--timeout-keep-alive 5`: Recycle connections faster

### 2.2 Gunicorn Configuration

**Production setup** (alternative to Uvicorn):
```bash
gunicorn src.app.main:app \
  --bind 0.0.0.0:8001 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 120 \
  --max-requests 1000 \
  --max-requests-jitter 100 \
  --graceful-timeout 30 \
  --keep-alive 5 \
  --log-level warning \
  --access-logfile - \
  --error-logfile -
```

**Worker recycling** (`--max-requests`):

- Prevents memory leaks from accumulating
- Recommended: 1000-5000 requests per worker

**Graceful shutdown** (`--graceful-timeout`):

- Allows in-flight requests to complete
- Recommended: 30-60 seconds

### 2.3 Startup Scripts

**Use provided production script**:
```bash

# Uvicorn mode (recommended)

./start_production.sh uvicorn

# Gunicorn mode

./start_production.sh gunicorn

# Custom worker count

API_WORKERS=8 ./start_production.sh uvicorn
```

---

## 3. Database Performance Tuning

### 3.1 Connection Pooling

**SQLAlchemy configuration**:
```python
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://user:[REDACTED]@host:5432/dbname"

engine = create_engine(
    DATABASE_URL,
    
    # Core pool settings

    pool_size=10,              # Number of persistent connections
    max_overflow=20,           # Additional connections during load
    
    # Connection health

    pool_pre_ping=True,        # Verify connections before use
    pool_recycle=3600,         # Recycle connections after 1 hour
    
    # Timeouts

    connect_args={
        "connect_timeout": 10,
        "application_name": "project-ai"
    },
    
    # Performance

    echo=False,                # Disable SQL logging in production
    pool_timeout=30,           # Wait up to 30s for connection
)
```

**Pool sizing formula**:
```
pool_size = min(CPU_cores * 2, 10)
max_overflow = pool_size * 2
total_connections = pool_size + max_overflow
```

**Example**: 4 CPU cores

- pool_size = 8
- max_overflow = 16
- total = 24 connections

### 3.2 Query Optimization

**Use indexes**:
```python
from sqlalchemy import Index

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)  # Indexed
    
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),  # Composite
    )
```

**Lazy loading vs. eager loading**:
```python

# Bad: N+1 queries

users = session.query(User).all()
for user in users:
    print(user.posts)  # Separate query for each user

# Good: Single query with join

from sqlalchemy.orm import joinedload

users = session.query(User).options(joinedload(User.posts)).all()
for user in users:
    print(user.posts)  # Already loaded
```

### 3.3 PostgreSQL-Specific Tuning

**Connection parameters**:
```python
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "options": "-c statement_timeout=30000",  # 30s query timeout
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)
```

---

## 4. Caching Strategies

### 4.1 Application-Level Caching

**Using functools.lru_cache**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_user_permissions(user_id: int) -> list[str]:

    # Expensive database query

    return db.query(...).all()
```

**TTL-based caching** with cachetools:
```python
from cachetools import TTLCache, cached

cache = TTLCache(maxsize=100, ttl=300)  # 5 minutes

@cached(cache)
def get_config(key: str) -> dict:
    return expensive_operation()
```

### 4.2 Redis Caching

**Connection pool**:
```python
from redis import ConnectionPool, Redis

pool = ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50,
    socket_timeout=5,
    socket_connect_timeout=5,
    decode_responses=True
)

redis_client = Redis(connection_pool=pool)
```

**Caching pattern**:
```python
import json
from typing import Optional

def get_cached_data(key: str) -> Optional[dict]:
    """Get data from cache or database"""

    # Try cache first

    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    
    # Cache miss - query database

    data = query_database(key)
    
    # Store in cache (5 minute TTL)

    redis_client.setex(key, 300, json.dumps(data))
    
    return data
```

### 4.3 HTTP Response Caching

**FastAPI cache headers**:
```python
from fastapi import Response

@app.get("/api/public/data")
def get_public_data(response: Response):
    response.headers["Cache-Control"] = "public, max-age=300"
    return {"data": "..."}
```

---

## 5. Resource Limits

### 5.1 Docker Resource Limits

**docker-compose.yml**:
```yaml
services:
  project-ai:
    build: .
    deploy:
      resources:
        limits:
          cpus: '2.0'        # Maximum 2 CPU cores
          memory: 2G         # Maximum 2GB RAM
        reservations:
          cpus: '1.0'        # Guaranteed 1 CPU core
          memory: 512M       # Guaranteed 512MB RAM
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
```

### 5.2 Kubernetes Resource Limits

**k8s/deployment.yaml**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: project-ai
spec:
  template:
    spec:
      containers:

      - name: app
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"

```

### 5.3 Application-Level Limits

**Request timeout**:
```python
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio

class TimeoutMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await asyncio.wait_for(call_next(request), timeout=30.0)
        except asyncio.TimeoutError:
            return JSONResponse(
                status_code=504,
                content={"error": "Request timeout"}
            )

app = FastAPI()
app.add_middleware(TimeoutMiddleware)
```

---

## 6. Monitoring and Profiling

### 6.1 Prometheus Metrics

**FastAPI integration**:
```python
from prometheus_client import Counter, Histogram, generate_latest
from fastapi import FastAPI

app = FastAPI()

# Metrics

request_count = Counter('app_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('app_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def prometheus_middleware(request, call_next):
    with request_duration.time():
        response = await call_next(request)
    request_count.labels(method=request.method, endpoint=request.url.path).inc()
    return response

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type="text/plain")
```

### 6.2 Application Profiling

**Using py-spy** (production-safe):
```bash

# Install py-spy

pip install py-spy

# Profile running process

py-spy top --pid <PID>

# Generate flame graph

py-spy record -o profile.svg --pid <PID>
```

**Using cProfile**:
```bash

# Profile application startup

python -m cProfile -o profile.stats launcher.py

# Analyze results

python -m pstats profile.stats
```

### 6.3 Performance Benchmarks

**Using locust**:
```python

# locustfile.py

from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_health(self):
        self.client.get("/health")
    
    @task(3)
    def get_api(self):
        self.client.get("/api/v1/data")
```

**Run benchmark**:
```bash
locust -f locustfile.py --host=http://localhost:8001
```

---

## 7. Production Deployment

### 7.1 Pre-Deployment Checklist

**Runtime verification**:
```bash

# Run health check

python runtime_health_check.py

# Verify dependencies

pip check

# Run tests

pytest tests/ -v

# Lint code

ruff check src/
```

**Configuration verification**:
```bash

# Check environment variables

env | grep -E 'PYTHON|API|DATABASE'

# Verify production settings

grep -r "DEBUG.*=.*True" src/  # Should return nothing

# Check secret management

grep -r "password.*=.*['\"]" src/  # Should use env vars
```

### 7.2 Deployment Process

**1. Build optimized Docker image**:
```bash
docker build -t project-ai:$(git rev-parse --short HEAD) .
```

**2. Run health check on container**:
```bash
docker run --rm project-ai:latest python runtime_health_check.py --quick
```

**3. Deploy with resource limits**:
```bash
docker run -d \
  --name project-ai \
  --cpus=2.0 \
  --memory=2g \
  --memory-reservation=512m \
  -p 8001:8001 \
  --env-file .env.production \
  project-ai:latest
```

**4. Verify deployment**:
```bash

# Check container health

docker inspect --format='{{.State.Health.Status}}' project-ai

# Check logs

docker logs -f project-ai

# Test endpoints

curl http://localhost:8001/health
```

### 7.3 Rollback Procedure

```bash

# Stop current version

docker stop project-ai

# Start previous version

docker run -d \
  --name project-ai \
  --cpus=2.0 \
  --memory=2g \
  -p 8001:8001 \
  --env-file .env.production \
  project-ai:previous-tag
```

---

## 8. Performance Targets

### 8.1 Application Metrics

**Target Performance**:
```
Startup Time:        < 5 seconds (cold start)
                     < 2 seconds (hot start)
Health Check:        < 1 second
API Response (p50):  < 100ms
API Response (p95):  < 500ms
API Response (p99):  < 1000ms
```

**Resource Usage**:
```
Memory per worker:   < 512MB
CPU usage (avg):     < 50%
CPU usage (peak):    < 80%
Database connections: 10-30 (per app instance)
```

### 8.2 Monitoring Thresholds

**Alerts**:
```
Memory > 1.5GB:      WARNING
Memory > 1.8GB:      CRITICAL
CPU > 70% (5min):    WARNING
CPU > 90% (2min):    CRITICAL
Error rate > 1%:     WARNING
Error rate > 5%:     CRITICAL
Response time > 2s:  WARNING
```

---

## 9. Troubleshooting

### 9.1 High Memory Usage

**Diagnosis**:
```bash

# Check process memory

ps aux | grep python

# Profile memory

python -m memory_profiler launcher.py

# Check for memory leaks

py-spy dump --pid <PID>
```

**Solutions**:

- Reduce worker count
- Implement connection pooling
- Add caching layer
- Review ORM query patterns (N+1 queries)
- Enable query result streaming for large datasets

### 9.2 Slow Response Times

**Diagnosis**:
```bash

# Profile application

py-spy record -o profile.svg --pid <PID> --duration 60

# Check database queries

# Enable SQLAlchemy echo

engine = create_engine(DATABASE_URL, echo=True)

# Monitor database

EXPLAIN ANALYZE SELECT ...
```

**Solutions**:

- Add database indexes
- Implement caching
- Use async database drivers
- Optimize ORM queries
- Add CDN for static assets

### 9.3 Connection Pool Exhaustion

**Symptoms**:
```
sqlalchemy.exc.TimeoutError: QueuePool limit exceeded
```

**Solutions**:
```python

# Increase pool size

engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Increase from 10
    max_overflow=40,     # Increase from 20
)

# Or reduce worker count

WORKERS=2 ./start_production.sh
```

---

## 10. References

- **Python Performance**: https://wiki.python.org/moin/PythonSpeed/PerformanceTips
- **Uvicorn Deployment**: https://www.uvicorn.org/deployment/
- **Gunicorn Settings**: https://docs.gunicorn.org/en/stable/settings.html
- **SQLAlchemy Pooling**: https://docs.sqlalchemy.org/en/20/core/pooling.html
- **FastAPI Performance**: https://fastapi.tiangolo.com/deployment/

---

**Maintained By**: Runtime Dependency Architect  
**Review Schedule**: Quarterly or on performance degradation
