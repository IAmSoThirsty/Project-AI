# 02: Docker System Relationships

**Document**: Docker Build and Container Relationships  
**System**: Docker Multi-Stage Builds, Health Checks, Image Registry  
**Related Systems**: Kubernetes, CI/CD, Security Scanning

---


## Navigation

**Location**: `relationships\deployment\02_docker_relationships.md`

**Parent**: [[relationships\deployment\README.md]]


## Docker Architecture

```
┌────────────────────────────────────────────────────────┐
│                  DOCKER ECOSYSTEM                       │
├────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐                                      │
│  │  Dockerfile  │                                      │
│  │  (Project    │                                      │
│  │   Root)      │                                      │
│  └──────┬───────┘                                      │
│         │                                               │
│         ↓                                               │
│  ┌─────────────────────────────────────┐               │
│  │    Stage 1: Builder                 │               │
│  │                                     │               │
│  │  FROM python:3.11-slim as builder  │               │
│  │  • Install build-essential         │               │
│  │  • Copy requirements.txt           │               │
│  │  • Build Python wheels             │               │
│  │  • Output: /build/wheels/          │               │
│  └─────────────┬───────────────────────┘               │
│                │                                        │
│                ↓                                        │
│  ┌─────────────────────────────────────┐               │
│  │    Stage 2: Runtime                 │               │
│  │                                     │               │
│  │  FROM python:3.11-slim              │               │
│  │  • Install runtime libs only       │               │
│  │  • Copy wheels from builder        │               │
│  │  • Install pre-built wheels        │               │
│  │  • Copy application code           │               │
│  │  • Set PYTHONPATH, ENV vars        │               │
│  │  • Configure HEALTHCHECK           │               │
│  └─────────────┬───────────────────────┘               │
│                │                                        │
│                ↓                                        │
│  ┌─────────────────────────────────────┐               │
│  │      Final Container Image          │               │
│  │                                     │               │
│  │  Size: ~300MB (vs 800MB single)    │               │
│  │  Layers: 12 (optimized)            │               │
│  │  Entry Point: python -m app.main   │               │
│  └─────────────┬───────────────────────┘               │
│                │                                        │
│                ├─────→ Docker Hub (public)              │
│                ├─────→ ACR (Azure)                      │
│                └─────→ ECR (AWS)                        │
│                                                         │
└────────────────────────────────────────────────────────┘
```

## Multi-Stage Build Relationships

### Stage Dependencies
```
Builder Stage:
  Input:
    - requirements.txt (Python deps)
    - build-essential (compiler)
    - libssl-dev, libffi-dev (crypto libs)
  
  Process:
    pip wheel --no-cache-dir --wheel-dir /build/wheels
  
  Output:
    - Pre-compiled Python wheels (.whl files)
    - No source code required in runtime
    - Faster installation, smaller image

Runtime Stage:
  Input:
    - Python wheels from builder
    - Application source (src/)
    - Data directory (data/)
  
  Process:
    pip install --no-cache /wheels/*
  
  Output:
    - Minimal runtime image
    - No build tools
    - Production-ready container
```

### Image Optimization Chain

```
Base Image Selection
    ↓
python:3.11-slim (140MB)
    ↓ vs
python:3.11 (900MB)
    ↓ chose slim
~760MB saved

Multi-Stage Build
    ↓
Builder: 450MB (discarded)
Runtime: 300MB (kept)
    ↓ vs
Single Stage: 800MB
    ↓ saved
500MB per image

Layer Caching
    ↓
COPY requirements.txt (before code)
    ↓ cache hit if unchanged
Skip pip install
    ↓ vs
COPY . (entire app first)
    ↓ cache miss every commit
Rebuild everything

Final Size: 300MB (optimized)
vs Single-Stage: 800MB
Reduction: 62.5%
```

## Docker Compose Relationships

### Development Stack
```yaml
# docker-compose.yml
services:
  cerberus:
    build: ../Cerberus-main
    image: projectai/cerberus:omega
    depends_on: []
    networks: [sovereign_net]
    volumes:
      - spine_data:/var/data/spine
    resources:
      limits:
        cpus: '2.00'
        memory: 4G

  monolith:
    image: projectai/monolith:latest
    depends_on: []
    networks: [sovereign_net]
    environment:
      - TARL_POLICY_PATH=/app/tarl_policies

networks:
  sovereign_net:
    driver: bridge
    internal: true  # No external internet

volumes:
  spine_data:
    driver: local
```

### Service Dependency Graph
```
Docker Compose Up
    ↓ creates
Network: sovereign_net
    ↓ isolated
Volume: spine_data
    ↓ mounts
Containers:
    ├─→ cerberus (orchestrator)
    └─→ monolith (guardian)
        ↓ communicate via
        Internal Network Only
```

## Health Check System

### Docker HEALTHCHECK Directive
```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1
```

### Health Check Relationships
```
Docker Engine
    ↓ every 30s
Execute Health Check
    ↓ 10s timeout
Python Import Test
    ├─→ Success (exit 0)
    │   ↓ container = healthy
    │   No action
    └─→ Failure (exit 1)
        ↓ retry (max 3)
        Still failing?
        ↓ mark
        Container = unhealthy
        ↓ triggers
        Restart Policy (if configured)
```

### Health Check Levels
```
Level 1: Basic Import
    CMD python -c "import sys; sys.exit(0)"
    Verifies: Python runtime functional

Level 2: Module Import
    CMD python -c "from app.main import main; sys.exit(0)"
    Verifies: Application importable

Level 3: Service Check
    CMD curl -f http://localhost:5000/health || exit 1
    Verifies: Service responding

Level 4: Deep Check
    CMD python healthcheck.py
    Verifies: Database, external APIs, cache
```

## Image Registry Relationships

### Push/Pull Flow
```
Local Build
    ↓ docker build -t projectai/backend:latest
Tagged Image
    ↓ docker login <registry>
Authenticated Session
    ↓ docker push projectai/backend:latest
Registry Storage
    ├─→ Docker Hub (public)
    ├─→ ACR (Azure Container Registry)
    └─→ ECR (AWS Elastic Container Registry)
        ↓ pulled by
        Kubernetes Deployment
        ↓ ImagePullPolicy: IfNotPresent
        Local Node Cache
        ↓ used by
        Pod Creation
```

### Image Tagging Strategy
```
Semantic Versioning:
  projectai/backend:1.0.0    (specific version)
  projectai/backend:1.0      (minor version)
  projectai/backend:1        (major version)
  projectai/backend:latest   (latest stable)

Environment Tags:
  projectai/backend:dev      (development)
  projectai/backend:staging  (staging)
  projectai/backend:prod     (production)

Commit Tags:
  projectai/backend:abc123   (git commit SHA)
  projectai/backend:pr-456   (pull request)

Build Tags:
  projectai/backend:build-789 (CI/CD build number)
```

## Dockerfile Relationships

### File Dependencies
```
Dockerfile
    ↓ depends on
requirements.txt
    ↓ lists
Python Packages
    ↓ installed via
pip
    ↓ creates
Virtual Environment
    ↓ isolated in
Container Filesystem

Dockerfile
    ↓ depends on
.dockerignore
    ↓ excludes
.git/, .venv/, __pycache__/
    ↓ reduces
Build Context Size
    ↓ speeds up
Docker Build
```

### Layer Optimization
```
Layer 1: FROM python:3.11-slim
  ↓ cached (rarely changes)
Layer 2: RUN apt-get update && apt-get install
  ↓ cached (rarely changes)
Layer 3: COPY requirements.txt
  ↓ cached (if requirements unchanged)
Layer 4: RUN pip install -r requirements.txt
  ↓ cached (if requirements unchanged)
Layer 5: COPY src/ /app/src/
  ↓ invalidated (every code change)
Layers 6-12: COPY data/, ENV, HEALTHCHECK, CMD
  ↓ built (on top of cached layers)

Cache Hit Rate: 60-80% (typical)
Build Time: 2-3 min (full) vs 30s (cached)
```

## Volume Mount Relationships

### Development Mounts
```
Host: ./data/
    ↓ mounted to
Container: /app/data/
    ↓ persists
User Data, AI Persona State

Host: ./logs/
    ↓ mounted to
Container: /app/logs/
    ↓ persists
Application Logs

Host: ./.env
    ↓ mounted to
Container: /app/.env
    ↓ provides
Environment Variables
```

### Production Volumes
```
Named Volume: spine_data
    ↓ managed by
Docker Volume Driver
    ↓ backed by
Host Filesystem (/var/lib/docker/volumes/)
    ↓ survives
Container Recreate
    ↓ ensures
Data Persistence
```

## Network Isolation

```
Host Network
    ⊗ not exposed
Internal Network: sovereign_net
    ├─→ cerberus (no external ports)
    └─→ monolith (no external ports)
        ↓ communicate via
        Service Discovery
            ↓ DNS resolution
            cerberus:8080 → 172.18.0.2:8080
            monolith:8081 → 172.18.0.3:8081

Security Benefit:
  - No internet access (internal: true)
  - No port exposure to host
  - Service-to-service only
```

## CI/CD Integration

### GitHub Actions Build
```yaml
- name: Build Docker Image
  run: |
    docker build -t projectai/backend:${{ github.sha }} .
    docker tag projectai/backend:${{ github.sha }} projectai/backend:latest

- name: Push to Registry
  run: |
    echo ${{ secrets.DOCKER_HUB_TOKEN }} | docker login -u ${{ secrets.DOCKER_HUB_USER }} --password-stdin
    docker push projectai/backend:${{ github.sha }}
    docker push projectai/backend:latest
```

### Build Flow
```
GitHub Actions Trigger
    ↓ checkout code
Repository Clone
    ↓ setup Docker buildx
Docker Builder
    ↓ build multi-platform
docker buildx build --platform linux/amd64,linux/arm64
    ↓ push
Registry (Docker Hub)
    ↓ notified
Kubernetes Cluster
    ↓ pulls
New Image
    ↓ rolls out
Updated Deployment
```

## Security Scanning Integration

```
Docker Image Built
    ↓ scanned by
Trivy Container Scanner
    ↓ checks
CVE Database
    ↓ reports
Vulnerabilities:
    ├─→ Critical (block build)
    ├─→ High (require review)
    ├─→ Medium (log warning)
    └─→ Low (informational)
        ↓ output
        SARIF Report
        ↓ uploaded to
        GitHub Security Tab
```

### Trivy Integration
```bash
# Scan image
trivy image projectai/backend:latest \
  --severity CRITICAL,HIGH \
  --exit-code 1  # Fail on critical/high

# Output formats
trivy image projectai/backend:latest --format json > trivy-report.json
trivy image projectai/backend:latest --format sarif > trivy-report.sarif
```

## Related Systems

### Docker → Kubernetes
```
Docker Image
    ↓ referenced in
K8s Deployment YAML
    ↓ pulled by
kubelet
    ↓ creates
Container (via containerd)
    ↓ managed by
Pod Lifecycle
```

### Docker → CI/CD
```
Code Commit
    ↓ triggers
GitHub Actions
    ↓ executes
Docker Build
    ↓ produces
Tagged Image
    ↓ pushes to
Registry
    ↓ deployed via
K8s Helm Chart
```

## Best Practices

### Image Size Optimization
- ✅ Use slim base images (python:3.11-slim)
- ✅ Multi-stage builds (builder + runtime)
- ✅ Minimize layers (combine RUN commands)
- ✅ .dockerignore to exclude unnecessary files
- ✅ Clean up cache (`rm -rf /var/lib/apt/lists/*`)

### Security Hardening
- ✅ Non-root user (USER appuser)
- ✅ Read-only root filesystem
- ✅ No secrets in environment variables
- ✅ Scan images regularly (Trivy)
- ✅ Sign images (Cosign)

### Performance
- ✅ Layer caching strategy
- ✅ Copy requirements before code
- ✅ Use BuildKit for parallel builds
- ✅ Multi-platform builds for ARM/x86

---

**Status**: ✅ Complete  
**Systems Covered**: Docker, Docker Compose, Health Checks, Image Registry  
**Related Docs**: `03_kubernetes_orchestration.md`, `05_cicd_pipelines.md`
