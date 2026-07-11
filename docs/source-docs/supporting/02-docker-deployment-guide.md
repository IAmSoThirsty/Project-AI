# Docker Deployment Guide

**Document Type:** Operations Guide
**Component:** Docker Infrastructure
**Status:** Production
**Version:** 2.0.0
**Last Updated:** 2025-01-26
**Author:** AGENT-046
**Audience:** DevOps Engineers, System Administrators, Platform Engineers
**Scope:** Docker containerization, multi-stage builds, Docker Compose, production deployment
**Related Docs:**
- `01-web-backend-architecture.md`
- `03-ci-cd-pipelines.md`
- `06-deployment-strategies.md`

---

## Table of Contents

1. [Docker Strategy Overview](#docker-strategy-overview)
2. [Multi-Stage Build Architecture](#multi-stage-build-architecture)
3. [Dockerfile Deep Dive](#dockerfile-deep-dive)
4. [Docker Compose Configuration](#docker-compose-configuration)
5. [Container Orchestration](#container-orchestration)
6. [Image Optimization](#image-optimization)
7. [Production Deployment](#production-deployment)
8. [Health Checks & Monitoring](#health-checks--monitoring)
9. [Networking & Security](#networking--security)
10. [Volume Management](#volume-management)
11. [Troubleshooting](#troubleshooting)
12. [Best Practices](#best-practices)

---

## Docker Strategy Overview

### Containerization Philosophy

Project-AI uses Docker to achieve:

1. **Reproducible Environments**: Same container runs identically everywhere
2. **Dependency Isolation**: Python, system libraries, and data isolated per container
3. **Resource Control**: CPU, memory, and I/O limits enforced
4. **Scalability**: Horizontal scaling through container replication
5. **Security**: Process isolation, read-only filesystems, non-root users

**NOT a Microservices Architecture** (Yet):
- Current: Monolithic application in a single container
- Future: Cerberus orchestrator + service containers (planned)

### Container Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                   PROJECT-AI CONTAINERS                      │
├──────────────────┬──────────────────┬──────────────────────┤
│  Desktop App     │  Web Backend     │  Cerberus (Future)   │
│  (PyQt6)         │  (Flask)         │  (Orchestrator)      │
│                  │                  │                      │
│  Base: py3.11    │  Base: py3.11    │  Base: py3.11       │
│  Size: 800MB     │  Size: 400MB     │  Size: 600MB        │
│  Purpose: GUI    │  Purpose: API    │  Purpose: Control   │
└──────────────────┴──────────────────┴──────────────────────┘
```

**Current State:**
- ✅ Desktop app containerization (Dockerfile)
- ✅ Web backend containerization (Dockerfile.web)
- ✅ Docker Compose for local development
- ⏳ Cerberus orchestrator integration (in progress)

---

## Multi-Stage Build Architecture

### Why Multi-Stage Builds?

**Traditional Single-Stage Build Problems:**
- 800MB+ final image (includes build tools)
- Slow build times (rebuilds all dependencies)
- Security risks (unnecessary packages in production)

**Multi-Stage Solution:**
```dockerfile
# Stage 1: Builder (build-essential, gcc, etc.)
FROM python:3.11-slim as builder
# ... build wheels ...

# Stage 2: Runtime (only what's needed to run)
FROM python:3.11-slim
COPY --from=builder /build/wheels /wheels
# ... install wheels only ...
```

**Benefits:**
- ✅ 50% smaller final images
- ✅ Faster subsequent builds (cached layers)
- ✅ No build tools in production
- ✅ Reduced attack surface

### Build Stage Responsibilities

#### Stage 1: Builder

**Purpose:** Compile Python packages and create wheels.

```dockerfile
FROM python:3.11-slim as builder

WORKDIR /build

# Install ONLY build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \     # gcc, g++, make
    libssl-dev \          # OpenSSL headers
    libffi-dev \          # Foreign function interface
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Build wheels (no cache, no deps, wheel dir)
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt
```

**What Happens:**
1. Install system build tools (gcc, make, headers)
2. Copy requirements.txt
3. Build all Python packages into `.whl` files
4. Store wheels in `/build/wheels`

**Why Wheels:**
- Pre-compiled binaries (no recompilation needed)
- Faster installation in runtime stage
- Portable across same platform

#### Stage 2: Runtime

**Purpose:** Run the application with minimal dependencies.

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install ONLY runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 \             # OpenSSL library (not headers)
    libffi8 \             # FFI library (not headers)
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /build/wheels /wheels

# Install wheels
COPY requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy application
COPY src/ /app/src/
COPY data/ /app/data/

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src

# Entry point
CMD ["python", "-m", "app.main"]
```

**What Happens:**
1. Install only runtime libraries (no headers, no compilers)
2. Copy pre-built wheels from builder stage
3. Install wheels (fast, no compilation)
4. Copy application code
5. Set Python environment variables
6. Define entry point

**Key Optimization:**
- `apt-get install --no-install-recommends`: Minimal packages
- `rm -rf /var/lib/apt/lists/*`: Clean up package lists (saves 20MB)
- `pip install --no-cache`: Don't store pip cache (saves 50MB)

---

## Dockerfile Deep Dive

### Complete Annotated Dockerfile

```dockerfile
# ==============================================================================
# STAGE 1: BUILDER - Compile dependencies
# ==============================================================================
FROM python:3.11-slim as builder

WORKDIR /build

# Install system dependencies for building Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Core build tools
    build-essential \      # gcc, g++, make, libc-dev
    # Library headers for Python packages
    libssl-dev \           # cryptography package needs OpenSSL headers
    libffi-dev \           # cffi package needs FFI headers
    # Clean up to reduce layer size
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Build wheels for all dependencies
# --no-cache-dir: Don't store pip cache (saves space)
# --no-deps: Don't install dependencies of dependencies (just build)
# --wheel-dir: Output directory for .whl files
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements.txt

# ==============================================================================
# STAGE 2: RUNTIME - Production environment
# ==============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install ONLY runtime libraries (not headers or build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Runtime libraries (no -dev packages)
    libssl3 \              # OpenSSL library (cryptography needs this)
    libffi8 \              # FFI library (cffi needs this)
    # Clean up
    && rm -rf /var/lib/apt/lists/*

# Copy pre-built wheels from builder stage
COPY --from=builder /build/wheels /wheels

# Copy requirements to know what to install
COPY requirements.txt .

# Install wheels (fast because they're pre-built)
RUN pip install --no-cache /wheels/*

# Copy application code
COPY src/ /app/src/
COPY data/ /app/data/

# Set Python environment variables
ENV PYTHONUNBUFFERED=1      # Force stdout/stderr to be unbuffered (real-time logs)
ENV PYTHONPATH=/app/src     # Add src to Python path for imports

# Health check (runs every 30 seconds)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Entry point
CMD ["python", "-m", "app.main"]
```

### Dockerfile Variants

#### Desktop Application (Dockerfile)

**Purpose:** Run PyQt6 GUI in container with X11 forwarding.

```dockerfile
# ... multi-stage build ...

# Additional: X11 and GUI dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxcb1 \              # X11 client library
    libxkbcommon-x11-0 \   # Keyboard handling
    libgl1-mesa-glx \      # OpenGL support
    libdbus-1-3 \          # D-Bus for IPC
    && rm -rf /var/lib/apt/lists/*

# Entry point for desktop
CMD ["python", "-m", "app.main"]
```

**Usage:**
```bash
# Allow X11 forwarding
xhost +local:docker

# Run with X11 socket mounted
docker run -it \
  -e DISPLAY=$DISPLAY \
  -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
  projectai/desktop:latest
```

#### Web Backend (Dockerfile.web)

**Purpose:** Run Flask API server with Gunicorn.

```dockerfile
# ... multi-stage build ...

# Install Gunicorn for production server
RUN pip install gunicorn

# Expose port
EXPOSE 5000

# Entry point: Gunicorn with 4 workers
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--worker-class", "sync", \
     "--timeout", "120", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "web.backend.app:app"]
```

---

## Docker Compose Configuration

### Local Development Stack

**File:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  # ===========================================================================
  # Cerberus Orchestrator (Omega Configuration)
  # ===========================================================================
  cerberus:
    build:
      context: ../Cerberus-main
      dockerfile: Dockerfile
    image: projectai/cerberus:omega
    container_name: cerberus_omega
    restart: unless-stopped

    # Volume for persistent data
    volumes:
      - spine_data:/var/data/spine

    # Internal network (no internet access)
    networks:
      - sovereign_net

    # Resource limits (prevent runaway processes)
    deploy:
      resources:
        limits:
          cpus: '2.00'       # 2 CPU cores max
          memory: 4G         # 4GB RAM max

  # ===========================================================================
  # Thirsty Monolith (Guardian)
  # ===========================================================================
  monolith:
    image: projectai/monolith:latest
    container_name: thirsty_monolith

    networks:
      - sovereign_net

    environment:
      - TARL_POLICY_PATH=/app/tarl_policies

    # No ports exposed (internal only)

  # ===========================================================================
  # Web Backend (API Server)
  # ===========================================================================
  web-backend:
    build:
      context: .
      dockerfile: Dockerfile.web
    image: projectai/web-backend:latest
    container_name: web_backend
    restart: unless-stopped

    ports:
      - "5000:5000"

    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - ENVIRONMENT=development
      - CORS_ORIGINS=http://localhost:3000
      - LOG_LEVEL=INFO

    volumes:
      - ./data:/app/data
      - ./logs:/app/logs

    networks:
      - sovereign_net
      - external_net

    depends_on:
      - redis
      - cerberus

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  # ===========================================================================
  # Redis (Rate Limiting & Caching)
  # ===========================================================================
  redis:
    image: redis:7-alpine
    container_name: redis_cache
    restart: unless-stopped

    ports:
      - "6379:6379"

    volumes:
      - redis_data:/data

    networks:
      - sovereign_net

    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  # ===========================================================================
  # PostgreSQL (Future: Structured Data)
  # ===========================================================================
  postgres:
    image: postgres:16-alpine
    container_name: postgres_db
    restart: unless-stopped

    environment:
      - POSTGRES_DB=projectai
      - POSTGRES_USER=projectai
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}

    volumes:
      - postgres_data:/var/lib/postgresql/data

    networks:
      - sovereign_net

    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U projectai"]
      interval: 10s
      timeout: 5s
      retries: 5

# =============================================================================
# NETWORKS
# =============================================================================
networks:
  # Internal network: No external internet access
  sovereign_net:
    driver: bridge
    internal: true  # Critical: Blocks internet access for Cerberus

  # External network: Internet access for web backend and frontend
  external_net:
    driver: bridge

# =============================================================================
# VOLUMES (Persistent Data)
# =============================================================================
volumes:
  # Cerberus spine data (decision history, policies)
  spine_data:
    driver: local

  # Redis persistence
  redis_data:
    driver: local

  # PostgreSQL database
  postgres_data:
    driver: local
```

### Service Responsibilities

| Service | Purpose | Internet Access | Persistent Data |
|---------|---------|-----------------|-----------------|
| `cerberus` | AI orchestration, governance | ❌ No | spine_data |
| `monolith` | Policy enforcement, TARL | ❌ No | None |
| `web-backend` | HTTP API server | ✅ Yes | data/, logs/ |
| `redis` | Rate limiting, caching | ❌ No | redis_data |
| `postgres` | Structured data (future) | ❌ No | postgres_data |

### Development vs Production Compose

#### Development (`docker-compose.yml`)

**Characteristics:**
- Hot reloading enabled
- Debug logging
- Source code mounted as volumes
- All ports exposed
- Internet access for all services

```yaml
services:
  web-backend:
    build:
      context: .
      dockerfile: Dockerfile.web
    volumes:
      - ./src:/app/src:ro  # Mount source code read-only
      - ./data:/app/data
    environment:
      - FLASK_DEBUG=1
      - LOG_LEVEL=DEBUG
    command: flask run --host=0.0.0.0 --reload
```

#### Production (`docker-compose.prod.yml`)

**Characteristics:**
- No source code mounts
- Production servers (Gunicorn, not Flask dev)
- Minimal ports exposed
- Secrets from environment or vault
- Resource limits enforced

```yaml
services:
  web-backend:
    image: projectai/web-backend:v1.0.0  # Specific version tag
    restart: always
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=WARNING
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
      replicas: 3
    command: gunicorn --bind 0.0.0.0:5000 --workers 4 web.backend.app:app
```

---

## Container Orchestration

### Docker Compose Commands

**Start Services:**
```bash
# Start all services in background
docker-compose up -d

# Start specific service
docker-compose up -d web-backend

# Start with build (rebuild images)
docker-compose up -d --build

# View logs
docker-compose logs -f web-backend

# View all service status
docker-compose ps
```

**Stop Services:**
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (DATA LOSS!)
docker-compose down -v

# Stop specific service
docker-compose stop web-backend
```

**Service Management:**
```bash
# Restart service
docker-compose restart web-backend

# Scale service (horizontal scaling)
docker-compose up -d --scale web-backend=3

# Execute command in running container
docker-compose exec web-backend python -c "print('Hello')"

# View service logs
docker-compose logs -f --tail=100 web-backend
```

### Kubernetes Deployment

**Production-Grade Kubernetes Manifests:**

#### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-backend
  namespace: projectai
  labels:
    app: web-backend
    version: v1.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: web-backend
  template:
    metadata:
      labels:
        app: web-backend
        version: v1.0.0
    spec:
      # Security context
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

      containers:
      - name: web-backend
        image: projectai/web-backend:v1.0.0
        imagePullPolicy: IfNotPresent

        ports:
        - containerPort: 5000
          name: http
          protocol: TCP

        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: ai-secrets
              key: openai-api-key
        - name: ENVIRONMENT
          value: "production"
        - name: CORS_ORIGINS
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: cors-origins
        - name: RATE_LIMIT_STORAGE_URI
          value: "redis://redis-service:6379"

        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"

        livenessProbe:
          httpGet:
            path: /api/status
            port: 5000
          initialDelaySeconds: 10
          periodSeconds: 30
          timeoutSeconds: 5
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /api/status
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs

      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: web-backend-data
      - name: logs
        emptyDir: {}
```

#### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-backend-service
  namespace: projectai
  labels:
    app: web-backend
spec:
  type: LoadBalancer
  selector:
    app: web-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
    name: http
  sessionAffinity: None
```

#### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-backend-hpa
  namespace: projectai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
```

---

## Image Optimization

### Size Reduction Strategies

**Base Image Selection:**

| Base Image | Size | Use Case |
|------------|------|----------|
| `python:3.11` | 900MB | Not recommended |
| `python:3.11-slim` | 200MB | ✅ **Recommended** |
| `python:3.11-alpine` | 50MB | ⚠️ Compilation issues |

**Why Slim, Not Alpine:**
- Alpine uses musl libc (not glibc), causing compatibility issues
- Many Python packages expect glibc
- Compilation errors with cryptography, numpy, etc.
- Slim is a good balance: small size, broad compatibility

**Layer Optimization:**

```dockerfile
# ❌ BAD: Multiple layers
RUN apt-get update
RUN apt-get install -y build-essential
RUN apt-get install -y libssl-dev
RUN rm -rf /var/lib/apt/lists/*

# ✅ GOOD: Single layer with cleanup
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*
```

**Cache Invalidation Prevention:**

```dockerfile
# ❌ BAD: Copies everything, invalidates cache on any change
COPY . /app

# ✅ GOOD: Copy dependencies first, then code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ /app/src/  # Only invalidates this layer on code change
```

### Build Cache Optimization

**Use BuildKit:**
```bash
# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Build with cache from registry
docker build \
  --cache-from projectai/web-backend:latest \
  --tag projectai/web-backend:v1.0.1 \
  .
```

**Multi-Platform Builds:**
```bash
# Build for multiple architectures
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --tag projectai/web-backend:v1.0.0 \
  --push \
  .
```

---

## Production Deployment

### Pre-Deployment Checklist

✅ **Security:**
- [ ] Secrets stored in vault (not environment variables)
- [ ] Non-root user in container
- [ ] Read-only root filesystem
- [ ] Security scanning passed (Trivy, Clair)
- [ ] HTTPS/TLS configured

✅ **Reliability:**
- [ ] Health checks configured
- [ ] Resource limits set
- [ ] Liveness and readiness probes tested
- [ ] Persistent volumes configured
- [ ] Backup strategy in place

✅ **Observability:**
- [ ] Logging to stdout/stderr
- [ ] Metrics endpoint exposed
- [ ] Distributed tracing enabled
- [ ] Error tracking configured (Sentry)

✅ **Performance:**
- [ ] Image size optimized (<500MB)
- [ ] Build time <5 minutes
- [ ] Startup time <30 seconds
- [ ] Connection pooling enabled

### Deployment Strategies

#### Blue-Green Deployment

```bash
# Deploy green version
kubectl apply -f deployment-green.yaml

# Wait for health checks
kubectl rollout status deployment/web-backend-green

# Switch traffic to green
kubectl patch service web-backend-service -p '{"spec":{"selector":{"version":"green"}}}'

# Verify traffic
curl https://api.example.com/api/status

# Delete blue version
kubectl delete deployment web-backend-blue
```

#### Canary Deployment

```yaml
# 90% traffic to stable, 10% to canary
apiVersion: v1
kind: Service
metadata:
  name: web-backend-service
spec:
  selector:
    app: web-backend
  ports:
  - port: 80
    targetPort: 5000
---
apiVersion: networking.istio.io/v1alpha3
kind: VirtualService
metadata:
  name: web-backend
spec:
  hosts:
  - web-backend-service
  http:
  - match:
    - headers:
        canary:
          exact: "true"
    route:
    - destination:
        host: web-backend-service
        subset: canary
  - route:
    - destination:
        host: web-backend-service
        subset: stable
      weight: 90
    - destination:
        host: web-backend-service
        subset: canary
      weight: 10
```

---

## Health Checks & Monitoring

### Docker Health Checks

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1
```

**Parameters:**
- `--interval`: Run check every 30 seconds
- `--timeout`: Fail if check takes >10 seconds
- `--start-period`: Grace period before first check (5 seconds)
- `--retries`: Mark unhealthy after 3 consecutive failures

**Advanced Health Check:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/api/status || exit 1
```

### Container Metrics

**Prometheus Exporter:**
```yaml
services:
  web-backend:
    # ... other config ...
    labels:
      - "prometheus.io/scrape=true"
      - "prometheus.io/port=5000"
      - "prometheus.io/path=/metrics"
```

**cAdvisor (Container Advisor):**
```yaml
services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
    ports:
      - "8080:8080"
```

---

## Networking & Security

### Network Isolation

**Internal Network (sovereign_net):**
- Purpose: Isolate Cerberus and Monolith from internet
- Configuration: `internal: true`
- Access: Only containers in same network

**External Network (external_net):**
- Purpose: Allow web backend internet access
- Configuration: Default bridge network
- Access: Internet and other containers

**Multi-Network Container:**
```yaml
services:
  web-backend:
    networks:
      - sovereign_net  # Talk to Cerberus
      - external_net   # Talk to internet (OpenAI API)
```

### Security Best Practices

**Non-Root User:**
```dockerfile
# Create non-root user
RUN addgroup --system --gid 1000 appuser && \
    adduser --system --uid 1000 --ingroup appuser appuser

# Change ownership
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser
```

**Read-Only Root Filesystem:**
```yaml
services:
  web-backend:
    read_only: true
    tmpfs:
      - /tmp
      - /app/logs
```

**Security Options:**
```yaml
services:
  web-backend:
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # Only if binding to port <1024
```

---

## Volume Management

### Persistent Volumes

**Named Volumes:**
```yaml
volumes:
  data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /mnt/data/projectai
```

**Bind Mounts:**
```yaml
services:
  web-backend:
    volumes:
      - ./data:/app/data:rw  # Read-write
      - ./src:/app/src:ro    # Read-only
```

**Backup Strategy:**
```bash
# Backup named volume
docker run --rm \
  -v spine_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/spine_data_$(date +%Y%m%d).tar.gz -C /data .

# Restore named volume
docker run --rm \
  -v spine_data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/spine_data_20250126.tar.gz -C /data
```

---

## Troubleshooting

### Common Issues

#### 1. Container Won't Start

**Symptom:** `docker-compose up` shows immediate exit.

**Diagnosis:**
```bash
# View exit code and error
docker-compose logs web-backend

# Check container status
docker ps -a | grep web-backend
```

**Solutions:**
- Check logs for Python import errors
- Verify environment variables
- Ensure required files exist in image

#### 2. Health Check Failing

**Symptom:** Container marked unhealthy.

**Diagnosis:**
```bash
# View health check logs
docker inspect web-backend | jq '.[0].State.Health'

# Test health check manually
docker exec web-backend curl -f http://localhost:5000/api/status
```

**Solutions:**
- Increase `start_period` if app takes longer to start
- Check if port 5000 is actually bound
- Verify health endpoint returns 200 OK

#### 3. Volume Permission Denied

**Symptom:** `PermissionError: [Errno 13] Permission denied: '/app/data/users.json'`

**Diagnosis:**
```bash
# Check file ownership in container
docker exec web-backend ls -la /app/data

# Check user container runs as
docker exec web-backend whoami
```

**Solutions:**
```bash
# Fix ownership on host
sudo chown -R 1000:1000 ./data

# Or run container as root (not recommended)
docker-compose run --user root web-backend bash
```

#### 4. Out of Memory

**Symptom:** Container killed with exit code 137.

**Diagnosis:**
```bash
# Check memory usage
docker stats web-backend

# View OOM events
docker inspect web-backend | jq '.[0].State.OOMKilled'
```

**Solutions:**
```yaml
# Increase memory limit
services:
  web-backend:
    deploy:
      resources:
        limits:
          memory: 2G  # Increase from 1G
```

---

## Best Practices

### 1. Image Tagging

✅ **DO:**
- Use semantic versioning: `v1.0.0`, `v1.0.1`
- Tag production images: `projectai/web-backend:v1.0.0`
- Use `latest` only for development
- Include git commit SHA: `projectai/web-backend:v1.0.0-abc123`

❌ **DON'T:**
- Use `latest` in production
- Omit tags (defaults to `latest`)
- Use mutable tags in Kubernetes

### 2. Environment Variables

✅ **DO:**
- Use `.env` file for local development
- Use Kubernetes Secrets for production
- Validate required variables on startup
- Document all variables in `.env.example`

❌ **DON'T:**
- Commit `.env` to version control
- Hard-code secrets in Dockerfile
- Use default values for secrets

### 3. Resource Limits

✅ **DO:**
- Set memory limits to prevent OOM
- Set CPU limits to ensure fair sharing
- Use requests and limits in Kubernetes
- Monitor actual usage and adjust

❌ **DON'T:**
- Run without resource limits
- Set limits too low (causes throttling)
- Ignore memory leaks

---

## Summary

**Docker Strategy:**
- ✅ Multi-stage builds for 50% smaller images
- ✅ Docker Compose for local development
- ✅ Kubernetes for production orchestration
- ✅ Network isolation for security
- ✅ Health checks and monitoring

**Key Files:**
- `Dockerfile` - Desktop application
- `Dockerfile.web` - Web backend
- `docker-compose.yml` - Local development stack
- `docker-compose.prod.yml` - Production configuration

**Production Readiness:**
- Container images <500MB
- Startup time <30 seconds
- Health checks passing
- Resource limits configured
- Secrets in vault

**Next Steps:**
- Review `03-ci-cd-pipelines.md` for automated builds
- See `06-deployment-strategies.md` for rollout strategies
- Check `../monitoring/prometheus-setup.md` for metrics

---

**Document Metadata:**
- **Word Count:** 4,892 words
- **Code Examples:** 35
- **Configuration Files:** 12
- **Diagrams:** 2
- **Last Reviewed:** 2025-01-26
- **Next Review:** 2025-04-26

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
