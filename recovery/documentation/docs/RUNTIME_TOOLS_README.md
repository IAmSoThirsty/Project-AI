# Runtime Dependency Tools - Quick Reference

**Created by**: Runtime Dependency Architect  
**Date**: 2026-04-09  
**Status**: ✅ Production Ready

---

## Overview

This directory contains comprehensive runtime dependency verification, documentation, and optimization tools for the Sovereign Governance Substrate.

---

## 📋 Quick Start

### Check Runtime Health

```bash

# Quick health check (< 1 second)

python runtime_health_check.py --quick

# Full health check (3-5 seconds)

python runtime_health_check.py

# JSON output for CI/CD

python runtime_health_check.py --json
```

### Run Full Verification Suite

```bash

# Test all components

python verify_runtime_setup.py
```

### Start Production Server

```bash

# Uvicorn mode (recommended)

./start_production.sh uvicorn

# Gunicorn mode

./start_production.sh gunicorn

# Custom worker count

API_WORKERS=8 ./start_production.sh uvicorn
```

---

## 📚 Documentation

### Core Documentation

1. **RUNTIME_REQUIREMENTS.md** (12 KB)
   - Complete runtime specification
   - Python 3.11+, Node.js 18+ requirements
   - Environment variables reference
   - Database and service configuration
   - Performance tuning settings

2. **RUNTIME_DEPENDENCIES_REPORT.md** (18 KB)
   - Comprehensive dependency analysis
   - Security audit (CVE status)
   - Library verification
   - Performance benchmarks
   - Deployment readiness checklist

3. **RUNTIME_OPTIMIZATION_GUIDE.md** (15 KB)
   - Python optimization techniques
   - ASGI server tuning
   - Database connection pooling
   - Caching strategies
   - Production deployment guide

4. **EXECUTIVE_SUMMARY.md** (10 KB)
   - High-level overview
   - Mission accomplishment summary
   - Key findings and recommendations
   - Quick reference guide

---

## 🔧 Tools

### runtime_health_check.py

**Purpose**: Automated runtime environment verification

**Features**:

- ✅ Python version check (3.11+ required)
- ✅ Node.js version check (18+ required)
- ✅ Dependency import validation
- ✅ Environment variable verification
- ✅ Service connectivity tests
- ✅ JSON output for automation

**Usage**:
```bash

# Quick check (fast startup verification)

python runtime_health_check.py --quick

# Full check (comprehensive)

python runtime_health_check.py

# JSON output

python runtime_health_check.py --json

# Quiet mode

python runtime_health_check.py --quiet
```

**Exit Codes**:

- `0`: All checks passed
- `1`: One or more checks failed

**Integration**:
```dockerfile

# Dockerfile

HEALTHCHECK CMD python runtime_health_check.py --quick

# entrypoint.sh

if [[ "${RUNTIME_HEALTH_CHECK:-1}" == "1" ]]; then
  python runtime_health_check.py --quick || exit 1
fi
```

### verify_runtime_setup.py

**Purpose**: Complete verification test suite

**Features**:

- ✅ Runs all health checks
- ✅ Verifies documentation exists
- ✅ Checks configuration files
- ✅ Tests Python imports
- ✅ Validates production readiness

**Usage**:
```bash

# Run full verification suite

python verify_runtime_setup.py
```

**Output**:
```
Total Tests: 16
✓ Passed:    15
✗ Failed:    0
⚠ Warnings:  1
```

### start_production.sh

**Purpose**: Production server startup with optimal configuration

**Features**:

- ✅ Uvicorn and Gunicorn support
- ✅ Auto-calculated worker count
- ✅ Integrated health checks
- ✅ Production optimization flags

**Usage**:
```bash

# Default (Uvicorn)

./start_production.sh

# Explicit mode

./start_production.sh uvicorn
./start_production.sh gunicorn

# Custom configuration

API_WORKERS=8 API_PORT=8000 ./start_production.sh uvicorn

# Skip health check

SKIP_HEALTH_CHECK=1 ./start_production.sh uvicorn
```

---

## ⚙️ Configuration Files

### .nvmrc

**Purpose**: Lock Node.js version for team consistency

**Content**: `20` (Node.js 20 LTS)

**Usage with nvm**:
```bash

# Install specified version

nvm install

# Use specified version

nvm use
```

### .env.production.example

**Purpose**: Production environment template

**Features**:

- Complete variable documentation
- Security key generation examples
- Resource limit configuration
- Monitoring setup
- Performance tuning

**Usage**:
```bash

# Copy and customize

cp .env.production.example .env

# Generate secret keys

python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate Fernet key

python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

---

## 🚀 Deployment Workflow

### 1. Pre-Deployment Verification

```bash

# Run health checks

python runtime_health_check.py

# Run full verification

python verify_runtime_setup.py

# Check dependencies

pip check

# Run tests

pytest tests/ -v
```

### 2. Docker Deployment

```bash

# Build image

docker build -t project-ai:latest .

# Test image health check

docker run --rm project-ai:latest python runtime_health_check.py --quick

# Deploy with resource limits

docker run -d \
  --name project-ai \
  --cpus=2.0 \
  --memory=2g \
  -p 8001:8001 \
  --env-file .env.production \
  project-ai:latest

# Verify health

docker inspect --format='{{.State.Health.Status}}' project-ai
```

### 3. Production Server

```bash

# Set production mode

export PRODUCTION=1

# Start server

./start_production.sh uvicorn

# Or with docker-compose

docker-compose up -d
```

### 4. Post-Deployment Verification

```bash

# Check container logs

docker logs -f project-ai

# Test health endpoint

curl http://localhost:8001/health

# Check metrics

curl http://localhost:8000/metrics
```

---

## 📊 Performance Targets

### Application Metrics

```
Startup Time (cold):    < 5 seconds
Startup Time (hot):     < 2 seconds
Health Check:           < 1 second
API Response (p50):     < 100ms
API Response (p95):     < 500ms
API Response (p99):     < 1000ms
```

### Resource Usage

```
Memory per worker:      < 512MB
CPU usage (average):    < 50%
CPU usage (peak):       < 80%
Database connections:   10-30
```

---

## 🔍 Troubleshooting

### Health Check Fails

```bash

# Run with verbose output

python runtime_health_check.py

# Check specific component

python -c "import fastapi, uvicorn, pydantic"

# Verify environment

echo $PYTHONPATH
```

### Import Errors

```bash

# Verify dependencies installed

pip list | grep -E 'fastapi|uvicorn|pydantic'

# Reinstall requirements

pip install -r requirements.txt

# Check for conflicts

pip check
```

### Performance Issues

```bash

# Profile application

py-spy top --pid <PID>

# Check database connections

# (See RUNTIME_OPTIMIZATION_GUIDE.md)

# Reduce workers

API_WORKERS=2 ./start_production.sh uvicorn
```

---

## 🔐 Security Checklist

- ✅ Python 3.11+ (security updates)
- ✅ All CVEs patched (gunicorn, cryptography, starlette)
- ✅ Non-root Docker user
- ✅ Pinned base images (SHA256)
- ✅ Minimal runtime dependencies
- ✅ No secrets in code
- ✅ Environment variable isolation

---

## 📝 Maintenance

### Regular Tasks

**Weekly**:

- Run `python verify_runtime_setup.py`
- Check for dependency updates
- Review performance metrics

**Monthly**:

- Update dependencies (if security patches available)
- Review and update documentation
- Performance benchmarking

**Quarterly**:

- Major dependency upgrades
- Python/Node.js version review
- Architecture optimization review

### Update Workflow

```bash

# Check for updates

pip list --outdated

# Update specific package

pip install --upgrade <package>

# Verify after update

python verify_runtime_setup.py
pytest tests/ -v
```

---

## 📞 Support

### Getting Help

1. **Check Documentation**:
   - `RUNTIME_REQUIREMENTS.md` - Specifications
   - `RUNTIME_DEPENDENCIES_REPORT.md` - Analysis
   - `RUNTIME_OPTIMIZATION_GUIDE.md` - Tuning

2. **Run Diagnostics**:
   ```bash
   python runtime_health_check.py --json > diagnostics.json
   python verify_runtime_setup.py
   ```

3. **Review Logs**:
   ```bash
   docker logs project-ai
   tail -f logs/audit.log
   ```

### Common Issues

| Issue | Solution |
|-------|----------|
| Import errors | Check PYTHONPATH, reinstall dependencies |
| Health check fails | Run `python runtime_health_check.py` for details |
| Slow startup | Check for large imports, reduce workers |
| High memory | Reduce worker count, check connection pools |
| Connection errors | Verify DATABASE_URL, REDIS_HOST settings |

---

## 📈 Metrics and Monitoring

### Prometheus Metrics

```bash

# View metrics

curl http://localhost:8000/metrics

# Check specific metric

curl http://localhost:8000/metrics | grep app_requests_total
```

### Grafana Dashboards

```bash

# Access Grafana

http://localhost:3000

# Default credentials (change in production)

Username: admin
Password: admin
```

---

## ✅ Production Readiness Checklist

Before deploying to production:

- [ ] `python runtime_health_check.py` passes
- [ ] `python verify_runtime_setup.py` passes
- [ ] `.env.production` configured with real values
- [ ] Secret keys generated and secure
- [ ] Database connection tested
- [ ] Resource limits configured
- [ ] Monitoring enabled (Prometheus + Grafana)
- [ ] Health checks functional
- [ ] Backup strategy in place
- [ ] Rollback plan documented

---

## 📖 Additional Resources

- **Python Performance**: https://wiki.python.org/moin/PythonSpeed
- **Uvicorn Deployment**: https://www.uvicorn.org/deployment/
- **Gunicorn Settings**: https://docs.gunicorn.org/en/stable/settings.html
- **FastAPI Production**: https://fastapi.tiangolo.com/deployment/
- **SQLAlchemy Pooling**: https://docs.sqlalchemy.org/en/20/core/pooling.html

---

**Maintained By**: Runtime Dependency Architect  
**Last Updated**: 2026-04-09  
**Review Schedule**: Quarterly or on dependency updates

---

## License

This documentation and tooling is part of the Sovereign Governance Substrate project, licensed under the MIT License.
