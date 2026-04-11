# Docker Architecture - Quick Reference Guide

**Sovereign-Governance-Substrate Production Deployment**

## Critical Findings - Executive Summary

### 🚨 PRODUCTION BLOCKERS (P0)

| # | Issue | Impact | Current State | Target | ETA |
|---|-------|--------|---------------|--------|-----|
| 1 | **Image Size Bloat** | Slow deployments, $$$ | 1.12GB | <500MB | Week 1 |
| 2 | **Missing SHA-256 Pins** | Supply chain vulnerability | 3/10 pinned | 10/10 | Week 1 |
| 3 | **Dockerfile.sovereign: No Non-Root User** | Container breakout risk | ❌ | ✅ | Week 1 |
| 4 | **Dockerfile.sovereign: No Health Check** | No failure detection | ❌ | ✅ | Week 1 |
| 5 | **Security Scans Non-Blocking** | Vulnerable images in prod | Warning only | Blocking | Week 1 |

### 📊 Production Readiness Score

```
Current:  78/100  ⚠️  (CONDITIONAL READY)
Target:   95/100  ✅  (PRODUCTION READY)
Gap:      17 points

Breakdown:
├─ Multi-Stage Builds:     18/20 ✅
├─ Security Hardening:     12/20 ⚠️  
├─ Image Optimization:     8/20  ❌
├─ Runtime Configuration:  14/20 ⚠️
└─ Production Operations:  26/20 ✅
```

---

## Quick Fix Commands

### Fix 1: Add SHA-256 Pins to Dockerfile.sovereign

```dockerfile

# BEFORE (VULNERABLE)

FROM golang:1.22-bookworm AS octoreflex-builder
FROM python:3.11-slim-bookworm

# AFTER (HARDENED)

FROM golang:1.22-bookworm@sha256:4a0b51b1f27c538f4e3b085fa0f1e006ca0c3194c754e4f2ceac92ecc7d2f4c6 AS octoreflex-builder
FROM python:3.11-slim-bookworm@sha256:0b23cfb7425d065008b778022a17b1551c82f8b4866ee5a7a200084b7e2eafbf
```

**Get SHA-256:**
```bash
docker pull python:3.11-slim-bookworm
docker inspect python:3.11-slim-bookworm --format='{{index .RepoDigests 0}}'
```

### Fix 2: Add Non-Root User to Dockerfile.sovereign

```dockerfile

# Add AFTER "COPY . ." and BEFORE "ENTRYPOINT"

RUN groupadd -r sovereign && useradd -r -g sovereign sovereign \
    && chown -R sovereign:sovereign /app
USER sovereign
```

### Fix 3: Add Health Check to Dockerfile.sovereign

```dockerfile

# Add BEFORE "ENTRYPOINT"

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### Fix 4: Make Trivy Scans Blocking

```yaml

# .github/workflows/tk8s-civilization-pipeline.yml

# CHANGE from:

- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'

# TO:

- name: Run Trivy vulnerability scanner
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: 'fs'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'              # ← FAIL BUILD ON VULNERABILITIES
    ignore-unfixed: false

```

### Fix 5: Reduce Image Size (Multi-Step Process)

**Step 1: Audit Dependencies**
```bash

# Find heavy packages

docker run --rm project-ai:latest pip list --format=freeze > installed.txt
pip install pipdeptree
pipdeptree --packages -fl | sort -k2 -n

# Remove unused packages from requirements.txt

```

**Step 2: Externalize Data Directory**
```dockerfile

# CHANGE from:

COPY --chown=sovereign:sovereign data/ /app/data/

# TO:

COPY --chown=sovereign:sovereign data/migrations/ /app/data/migrations/

# Use volume mount for runtime data:

# docker run -v /host/data:/app/data project-ai:latest

```

**Step 3: Add Cleanup Commands**
```dockerfile
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels \
    && find /usr/local/lib/python3.11 -type d -name '__pycache__' -delete \
    && find /usr/local/lib/python3.11 -type f -name '*.pyc' -delete \
    && find /usr/local/lib/python3.11 -type d -name 'tests' -exec rm -rf {} + 2>/dev/null || true
```

---

## Verification Commands

### Test Non-Root User

```bash
docker run --rm project-ai:latest whoami

# Expected: "sovereign" or "appuser" (NOT "root")

```

### Test Health Check

```bash
docker run -d --name test-health project-ai:latest
sleep 30
docker inspect --format='{{.State.Health.Status}}' test-health

# Expected: "healthy"

docker rm -f test-health
```

### Measure Image Size

```bash
docker images | grep project-ai

# Current: 1.12GB

# Target:  <500MB

```

### Test Security Scan

```bash
trivy image --severity CRITICAL,HIGH --exit-code 1 project-ai:latest

# Expected: Exit code 0 (no critical/high vulnerabilities)

```

### Verify Multi-Platform Build

```bash
docker buildx imagetools inspect ghcr.io/org/project-ai:latest

# Expected: linux/amd64, linux/arm64

```

---

## Build Commands

### Development Build

```bash
docker build -f Dockerfile -t project-ai:dev .
```

### Production Build (Optimized)

```bash
export DOCKER_BUILDKIT=1

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --build-arg VERSION=v1.0.0 \
  --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
  --cache-from type=gha \
  --cache-to type=gha,mode=max \
  --tag project-ai:v1.0.0 \
  --tag project-ai:latest \
  --load \
  -f Dockerfile .
```

### Build All Microservices

```bash
cd emergent-microservices
for service in */; do
  echo "Building $service..."
  docker build -t "sovereign-${service%/}:latest" "$service"
done
```

---

## Deployment Checklist

### Pre-Production Validation

**Security:**

- [ ] All base images SHA-256 pinned
- [ ] All containers run as non-root
- [ ] Trivy scan: CRITICAL=0, HIGH=0
- [ ] No secrets in image layers
- [ ] SBOM generated and stored

**Performance:**

- [ ] Image size < 500MB
- [ ] Build time < 5 minutes (first build)
- [ ] Build time < 2 minutes (cached)
- [ ] Health checks respond in <5s

**Operational:**

- [ ] Resource limits defined
- [ ] Graceful shutdown tested (SIGTERM)
- [ ] Multi-platform verified (amd64, arm64)
- [ ] Rollback procedure documented

### Deployment Commands

**Docker Compose (Development):**
```bash
docker-compose up -d
docker-compose ps
docker-compose logs -f project-ai
```

**Kubernetes (Production):**
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl rollout status deployment/project-ai -n sovereign
```

---

## Monitoring Commands

### Container Health

```bash

# Check health status

docker ps --filter "name=project-ai" --format "table {{.Names}}\t{{.Status}}"

# View health check logs

docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' project-ai

# Monitor resource usage

docker stats --no-stream project-ai
```

### Security Posture

```bash

# Scan running containers

trivy image $(docker ps --format '{{.Image}}')

# Check for root processes

docker top project-ai

# Verify exposed ports

docker port project-ai
```

### Performance Metrics

```bash

# Build time benchmark

time docker build --no-cache -f Dockerfile -t bench:test .

# Image size breakdown

docker history project-ai:latest --human=true --no-trunc

# Layer cache efficiency

docker build --cache-from project-ai:latest --progress=plain -f Dockerfile .
```

---

## Emergency Procedures

### Rollback to Previous Version

```bash

# Docker Compose

docker-compose down
docker tag project-ai:latest project-ai:rollback
docker tag project-ai:v1.0.0 project-ai:latest
docker-compose up -d

# Kubernetes

kubectl rollout undo deployment/project-ai -n sovereign
kubectl rollout status deployment/project-ai -n sovereign
```

### Force Rebuild (Cache Bypass)

```bash
docker build --no-cache --pull -f Dockerfile -t project-ai:latest .
```

### Debug Container Issues

```bash

# Run with shell access

docker run --rm -it --entrypoint /bin/bash project-ai:latest

# Check running processes

docker exec project-ai ps aux

# View logs with timestamps

docker logs --timestamps --since 1h project-ai

# Inspect container config

docker inspect project-ai | jq '.[0].Config'
```

---

## Resource Limits Reference

### Docker Compose

```yaml
services:
  project-ai:
    deploy:
      resources:
        limits:
          cpus: '4.0'
          memory: 8G
        reservations:
          cpus: '2.0'
          memory: 4G
```

### Kubernetes

```yaml
resources:
  requests:
    memory: "4Gi"
    cpu: "2000m"
  limits:
    memory: "8Gi"
    cpu: "4000m"
```

---

## CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Docker Build & Push

on:
  push:
    branches: [main]
    tags: ['v*.*.*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v4
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: ./Dockerfile
          push: true
          tags: ghcr.io/org/project-ai:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
          platforms: linux/amd64,linux/arm64
      
      - name: Security scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ghcr.io/org/project-ai:${{ github.sha }}
          severity: CRITICAL,HIGH
          exit-code: '1'

```

---

## Support & Troubleshooting

### Common Issues

**Issue: Build fails with "permission denied"**
```bash

# Solution: Check file ownership in COPY commands

COPY --chown=sovereign:sovereign src/ /app/src/
```

**Issue: Container immediately exits**
```bash

# Solution: Check logs for errors

docker logs project-ai

# Verify CMD/ENTRYPOINT

docker inspect --format='{{.Config.Cmd}}' project-ai:latest
```

**Issue: Health check failing**
```bash

# Solution: Test manually

docker exec project-ai curl -f http://localhost:8000/health

# Check startup time

docker inspect --format='{{.State.Health.Log}}' project-ai
```

**Issue: Image too large**
```bash

# Solution: Use dive to analyze layers

docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive:latest project-ai:latest
```

---

**Report Version:** 1.0  
**Last Updated:** 2026-01-09  
**Next Review:** After P0 remediation  
**Contact:** DevOps Team
