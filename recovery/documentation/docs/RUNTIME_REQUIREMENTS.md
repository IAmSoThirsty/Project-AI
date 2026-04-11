# Runtime Requirements Specification

**Document Status**: Production Standard  
**Last Updated**: 2026-04-09  
**Scope**: Complete runtime environment specification for Project-AI Sovereign Governance Substrate

---

## Executive Summary

This document specifies exact runtime requirements, version constraints, and configuration for the Project-AI platform. All production deployments MUST meet these requirements.

---

## 1. Core Runtime Environments

### 1.1 Python Runtime

**Required Version**: Python 3.11+  
**Recommended**: Python 3.12  
**Specified in**: `.python-version`, `pyproject.toml`, `Dockerfile`

**Version Constraints**:

- ✅ **Production**: Python 3.12 (current `.python-version`)
- ✅ **Acceptable**: Python 3.11 (minimum requirement)
- ⚠️ **Deprecated**: Python 3.10 (legacy support only)
- ❌ **Unsupported**: Python 3.9 and below

**Rationale**:

- Uses `match`/`case` statements (requires 3.10+)
- Type hints with `|` syntax (requires 3.10+)
- Performance improvements in 3.11+
- Improved error messages in 3.11+

**Configuration**:
```bash

# Environment variables

export PYTHONUNBUFFERED=1
export PYTHONPATH=/app/src
export PYTHONOPTIMIZE=0  # Development: 0, Production: 1 or 2
```

**Optimization Levels**:

- `PYTHONOPTIMIZE=0`: No optimization (development, debugging)
- `PYTHONOPTIMIZE=1`: Remove assert statements, `__debug__` = False
- `PYTHONOPTIMIZE=2`: Level 1 + remove docstrings (not recommended)

**Interpreter Flags**:
```bash

# Development

python -u  # Unbuffered output

# Production

python -O  # Optimize (equivalent to PYTHONOPTIMIZE=1)
python -OO # Maximum optimization (not recommended - removes docstrings)
```

### 1.2 Node.js Runtime

**Required Version**: Node.js 18.0.0+  
**Recommended**: Node.js 20 LTS  
**Specified in**: `package.json` (`engines.node`)

**Version Constraints**:

- ✅ **Production**: Node.js 20 LTS
- ✅ **Acceptable**: Node.js 18 LTS (minimum)
- ⚠️ **Deprecated**: Node.js 16 (EOL April 2024)
- ❌ **Unsupported**: Node.js < 16

**Configuration**:
```bash

# V8 heap size (adjust based on available memory)

export NODE_OPTIONS="--max-old-space-size=4096"

# Production flags

export NODE_ENV=production
```

**Performance Tuning**:
```bash

# Enable V8 optimizations

node --optimize-for-size  # Reduce memory footprint
node --max-old-space-size=8192  # Increase heap for large apps
```

---

## 2. Python Dependencies

### 2.1 Core Application Dependencies

**Source**: `requirements.txt`

| Package | Version | Purpose |
|---------|---------|---------|
| **fastapi** | ≥0.112.2 | Web framework |
| **uvicorn[standard]** | =0.27.0 | ASGI server |
| **pydantic** | ≥2.9.0 | Data validation |
| **sqlalchemy** | =2.0.25 | Database ORM |
| **cryptography** | ≥43.0.0 | Security primitives |
| **PyQt6** | =6.4.2 | GUI framework |
| **flask** | ≥3.0.3 | Miniature Office server |
| **gunicorn** | ≥22.0.0 | Production WSGI server |
| **temporalio** | ≥1.5.0 | Workflow orchestration |

**Security-Critical Versions**:

- `gunicorn ≥22.0.0`: Patched against CVE-2024-1135
- `cryptography ≥43.0.0`: Latest security updates
- `starlette ≥0.40.0`: ReDoS mitigation

### 2.2 Optional Dependencies

**Source**: `requirements-optional.txt`

| Package | Purpose | Install When |
|---------|---------|--------------|
| **redis** | Redis client | Using Redis for caching/sessions |
| **opencv-python-headless** | Computer vision | Video processing features |
| **openai-whisper** | Audio transcription | Audio features |
| **torch** | ML framework | Local model inference |
| **transformers** | NLP models | Local LLM features |

### 2.3 Development Dependencies

**Source**: `requirements-dev.txt`, `pyproject.toml`

| Package | Version | Purpose |
|---------|---------|---------|
| **pytest** | =7.4.4 | Testing framework |
| **pytest-asyncio** | =0.23.3 | Async test support |
| **pytest-cov** | =4.1.0 | Coverage reporting |
| **ruff** | ≥0.1.0 | Fast linter |
| **black** | =24.1.1 | Code formatter |
| **mypy** | =1.8.0 | Type checker |

---

## 3. Node.js Dependencies

**Source**: `package.json`

### 3.1 Development Tools

| Package | Version | Purpose |
|---------|---------|---------|
| **eslint** | ^8.57.0 | JavaScript linter |
| **prettier** | ^3.2.5 | Code formatter |
| **markdownlint-cli** | ^0.47.0 | Markdown linter |

---

## 4. System Dependencies

### 4.1 Docker Runtime

**Required**: Docker 20.10+ or compatible runtime

**Images Used**:

- Python: `python:3.11-slim@sha256:0b23...` (pinned)
- PostgreSQL: `postgres:13`
- Prometheus: `prom/prometheus:latest`
- Grafana: `grafana/grafana:latest`
- Temporal: `temporalio/auto-setup:latest`

### 4.2 Database Runtime

**PostgreSQL**:

- **Version**: PostgreSQL 13+
- **Client**: `psycopg2` (via SQLAlchemy)
- **Connection Pool**: SQLAlchemy pool (default 5 connections)

**SQLite**:

- Built-in to Python standard library
- Used for development/testing

### 4.3 Redis Runtime (Optional)

**Version**: Redis 6.0+  
**Client**: `redis-py` from `requirements-optional.txt`

**Configuration**:
```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

**Connection Pooling**:
```python
from redis import ConnectionPool

pool = ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50,
    socket_timeout=5,
    socket_connect_timeout=5
)
```

### 4.4 Temporal Runtime (Optional)

**Version**: Temporal Server 1.20+  
**Client**: `temporalio` Python SDK

**Configuration**:
```bash
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
```

---

## 5. Environment Configuration

### 5.1 Required Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PYTHONPATH` | `/app/src` | Python module search path |
| `PYTHONUNBUFFERED` | `1` | Disable output buffering |
| `QT_API` | `pyqt6` | Qt API backend |

### 5.2 Optional Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API authentication |
| `DEEPSEEK_API_KEY` | - | DeepSeek API authentication |
| `DATABASE_URL` | - | Database connection string |
| `TEMPORAL_HOST` | `localhost:7233` | Temporal server address |
| `REDIS_HOST` | `localhost` | Redis server address |
| `REDIS_PORT` | `6379` | Redis server port |
| `API_HOST` | `0.0.0.0` | API bind address |
| `API_PORT` | `8001` | API bind port |
| `API_WORKERS` | `4` | Uvicorn worker count |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

### 5.3 Production Environment Variables

```bash

# Performance

export PYTHONOPTIMIZE=1
export NODE_ENV=production
export API_WORKERS=8

# Security

export SECRET_KEY="[REDACTED]"
export CORS_ORIGINS="https://app.example.com"

# Monitoring

export ENABLE_METRICS=true
export METRICS_PORT=8000
```

---

## 6. Performance Tuning

### 6.1 Python Optimization

**Startup Performance**:
```bash

# Precompile bytecode

python -m compileall src/

# Use .pyc files

export PYTHONDONTWRITEBYTECODE=0
```

**Memory Management**:
```bash

# Reduce memory fragmentation

export PYTHONMALLOC=malloc

# Profile memory

python -m memory_profiler script.py
```

### 6.2 Uvicorn/Gunicorn Configuration

**Production Deployment**:
```bash

# Uvicorn with multiple workers

uvicorn src.app.main:app \
  --host 0.0.0.0 \
  --port 8001 \
  --workers 4 \
  --loop uvloop \
  --http httptools

# Gunicorn with Uvicorn workers

gunicorn src.app.main:app \
  --bind 0.0.0.0:8001 \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --timeout 120 \
  --max-requests 1000 \
  --max-requests-jitter 100
```

**Worker Calculation**:
```
workers = (2 × CPU_cores) + 1
```

### 6.3 Database Connection Pooling

**SQLAlchemy Pool Configuration**:
```python
from sqlalchemy import create_engine

engine = create_engine(
    DATABASE_URL,
    pool_size=10,              # Number of permanent connections
    max_overflow=20,           # Additional connections during load
    pool_pre_ping=True,        # Verify connections before use
    pool_recycle=3600,         # Recycle connections after 1 hour
    echo=False                 # Disable SQL logging in production
)
```

---

## 7. Health Checks

### 7.1 Runtime Verification Script

**Location**: `runtime_health_check.py`

**Usage**:
```bash

# Full health check

python runtime_health_check.py

# Quick check (fast startup verification)

python runtime_health_check.py --quick

# JSON output (for automation)

python runtime_health_check.py --json
```

**Exit Codes**:

- `0`: All checks passed
- `1`: One or more checks failed

### 7.2 Docker Health Check

**Defined in**: `Dockerfile`

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1
```

### 7.3 Startup Smoke Tests

**Run on every deployment**:
```bash

# Verify Python imports

python -c "import fastapi, uvicorn, pydantic, sqlalchemy, cryptography"

# Verify application entry point

python -m src.app.main --help

# Run quick health check

python runtime_health_check.py --quick
```

---

## 8. Troubleshooting

### 8.1 Common Issues

**Issue**: `ModuleNotFoundError: No module named 'src'`  
**Solution**: Set `PYTHONPATH=/app/src` or run from repository root

**Issue**: `ImportError: PyQt6 not found`  
**Solution**: Install system dependencies for Qt6 (Linux: `libxcb-*`, macOS: none required)

**Issue**: `uvicorn: command not found`  
**Solution**: Ensure virtual environment is activated and dependencies installed

**Issue**: Node version mismatch  
**Solution**: Use `nvm` to install correct Node.js version

### 8.2 Dependency Resolution

**Conflict**: Multiple package versions  
**Solution**: Use `requirements.lock` for deterministic builds

```bash

# Generate lock file

pip-compile requirements.in

# Install from lock

pip-sync requirements.lock
```

### 8.3 Performance Issues

**Slow Startup**:

1. Precompile Python bytecode
2. Reduce worker count during testing
3. Use `--reload` only in development

**High Memory Usage**:

1. Reduce worker count
2. Implement connection pooling
3. Profile with `memory_profiler`

---

## 9. Version Upgrade Path

### 9.1 Python Upgrades

**Current**: Python 3.12  
**Next**: Python 3.13 (when stable)

**Migration Checklist**:

- [ ] Update `.python-version`
- [ ] Update `pyproject.toml` (`requires-python`)
- [ ] Update `Dockerfile` base image
- [ ] Run full test suite
- [ ] Update CI/CD workflows
- [ ] Verify all dependencies compatible

### 9.2 Node.js Upgrades

**Current**: Node.js 18+  
**Target**: Node.js 20 LTS

**Migration Checklist**:

- [ ] Update `package.json` (`engines.node`)
- [ ] Test all npm scripts
- [ ] Update `.nvmrc` if present
- [ ] Update CI/CD workflows

---

## 10. Deployment Verification

### 10.1 Pre-Deployment Checklist

- [ ] Python version verified (3.11+)
- [ ] Node version verified (18+)
- [ ] All core dependencies installed
- [ ] Environment variables configured
- [ ] Database connectivity tested
- [ ] Health check passes
- [ ] Performance benchmarks met

### 10.2 Post-Deployment Monitoring

**Metrics to Monitor**:

- Application startup time
- Memory usage (RSS)
- CPU usage
- Database connection pool utilization
- Request latency (p50, p95, p99)
- Error rate

**Tools**:

- Prometheus + Grafana (configured in `docker-compose.yml`)
- Application logs (structured JSON)
- Health check endpoints

---

## 11. References

- **Python**: https://docs.python.org/3/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Uvicorn**: https://www.uvicorn.org/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Docker**: https://docs.docker.com/
- **Temporal**: https://docs.temporal.io/

---

**Document Maintained By**: Runtime Dependency Architect  
**Review Frequency**: Quarterly or on major dependency updates
