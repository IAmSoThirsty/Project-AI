# Docker Build Reproducibility Guide

This repository implements reproducible Docker builds using SOURCE_COMMIT_SHA and SOURCE_DATE_EPOCH for supply chain security and build transparency.

## Overview

All Dockerfiles in this repository have been enhanced with:

1. **Build Arguments** - Capture build metadata
2. **OCI Labels** - Store metadata in container images
3. **Environment Variables** - Make metadata available at runtime

## Build Arguments

Every Dockerfile accepts these build arguments:

```dockerfile
ARG SOURCE_COMMIT_SHA="unknown"      # Git commit SHA
ARG BUILD_VERSION="dev"              # Git tag or version
ARG SOURCE_DATE_EPOCH="0"            # Unix timestamp from git commit
ARG BUILD_TIMESTAMP="unknown"        # ISO 8601 build timestamp
```

## OCI Labels

Images include standardized OCI labels:

```dockerfile
LABEL org.opencontainers.image.revision="${SOURCE_COMMIT_SHA}"
LABEL org.opencontainers.image.version="${BUILD_VERSION}"
LABEL org.opencontainers.image.created="${BUILD_TIMESTAMP}"
LABEL org.opencontainers.image.source="https://github.com/IAmSoThirsty/Sovereign-Governance-Substrate"
```

## Environment Variables

The `SOURCE_DATE_EPOCH` is set as an environment variable for runtime use:

```dockerfile
ENV SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH}
```

## Building Images

### Automated Build Script

Use the provided build scripts that automatically capture git metadata:

**Linux/Mac:**
```bash
./scripts/build_docker_images.sh
```

**Windows:**
```powershell
.\scripts\build_docker_images.ps1
```

### Manual Build

Build a single image with reproducibility metadata:

```bash
docker build \
  --build-arg SOURCE_COMMIT_SHA=$(git rev-parse HEAD) \
  --build-arg BUILD_VERSION=$(git describe --tags --always) \
  --build-arg SOURCE_DATE_EPOCH=$(git log -1 --format=%ct) \
  --build-arg BUILD_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  -f Dockerfile.production \
  -t project-ai:production .
```

### With BuildKit Cache

For faster builds with caching:

```bash
DOCKER_BUILDKIT=1 docker build \
  --build-arg SOURCE_COMMIT_SHA=$(git rev-parse HEAD) \
  --build-arg BUILD_VERSION=$(git describe --tags --always) \
  --build-arg SOURCE_DATE_EPOCH=$(git log -1 --format=%ct) \
  --build-arg BUILD_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  --cache-from type=registry,ref=yourregistry/project-ai:cache \
  --build-arg BUILDKIT_INLINE_CACHE=1 \
  -f Dockerfile.production \
  -t project-ai:production .
```

## Verification

### Inspect Image Labels

View all OCI labels on a built image:

```bash
docker inspect project-ai:production | jq '.[0].Config.Labels'
```

Example output:
```json
{
  "org.opencontainers.image.revision": "abc123def456...",
  "org.opencontainers.image.version": "v1.0.0-5-gabc123d",
  "org.opencontainers.image.created": "2024-01-15T10:30:45Z",
  "org.opencontainers.image.source": "https://github.com/IAmSoThirsty/Sovereign-Governance-Substrate"
}
```

### Check Environment Variables

Verify SOURCE_DATE_EPOCH is set:

```bash
docker run --rm project-ai:production env | grep SOURCE_DATE_EPOCH
```

### PowerShell Verification

```powershell
docker inspect project-ai:production | ConvertFrom-Json | 
  Select-Object -ExpandProperty Config | 
  Select-Object -ExpandProperty Labels
```

## Benefits

1. **Traceability** - Every image can be traced back to its exact source code commit
2. **Reproducibility** - Builds from the same commit produce verifiable outputs
3. **Auditability** - Security teams can verify image provenance
4. **Compliance** - Meets supply chain security requirements (SLSA, SBOM)
5. **Debugging** - Easily identify which code version is running in production

## Updated Files

All Dockerfiles have been updated:

### Root Level

- `Dockerfile`
- `Dockerfile.production`
- `Dockerfile.optimized`
- `Dockerfile.test`
- `Dockerfile.sovereign`

### Services

- `api/Dockerfile`
- `web/Dockerfile`
- `web/backend/Dockerfile`

### Microservices

- `emergent-microservices/trust-graph-engine/Dockerfile`
- `emergent-microservices/sovereign-data-vault/Dockerfile`
- `emergent-microservices/autonomous-negotiation-agent/Dockerfile`
- `emergent-microservices/verifiable-reality/Dockerfile`
- `emergent-microservices/autonomous-compliance/Dockerfile`
- `emergent-microservices/autonomous-incident-reflex-system/Dockerfile`
- `emergent-microservices/ai-mutation-governance-firewall/Dockerfile`

### External Projects

- `external/Thirstys-Waterfall/Dockerfile`
- `external/Thirsty-Lang/Dockerfile`
- `external/Thirstys-Monolith/Dockerfile`
- `src/thirsty_lang/Dockerfile`
- `demos/thirstys_security_demo/Dockerfile`

## CI/CD Integration

Update your CI/CD pipeline to pass build arguments:

### GitHub Actions Example

```yaml

- name: Build Docker Image
  run: |
    docker build \
      --build-arg SOURCE_COMMIT_SHA=${{ github.sha }} \
      --build-arg BUILD_VERSION=${{ github.ref_name }} \
      --build-arg SOURCE_DATE_EPOCH=$(git log -1 --format=%ct) \
      --build-arg BUILD_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
      -f Dockerfile.production \
      -t project-ai:production .

```

### GitLab CI Example

```yaml
build:
  script:

    - export SOURCE_COMMIT_SHA=$CI_COMMIT_SHA
    - export BUILD_VERSION=$CI_COMMIT_TAG
    - export SOURCE_DATE_EPOCH=$(git log -1 --format=%ct)
    - export BUILD_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    - docker build 
        --build-arg SOURCE_COMMIT_SHA=$SOURCE_COMMIT_SHA
        --build-arg BUILD_VERSION=$BUILD_VERSION
        --build-arg SOURCE_DATE_EPOCH=$SOURCE_DATE_EPOCH
        --build-arg BUILD_TIMESTAMP=$BUILD_TIMESTAMP
        -f Dockerfile.production
        -t project-ai:production .

```

## References

- [SOURCE_DATE_EPOCH Specification](https://reproducible-builds.org/docs/source-date-epoch/)
- [OCI Image Spec - Annotations](https://github.com/opencontainers/image-spec/blob/main/annotations.md)
- [Reproducible Builds Project](https://reproducible-builds.org/)
- [SLSA Framework](https://slsa.dev/)
