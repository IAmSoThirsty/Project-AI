# Docker Reproducibility Quick Reference



## 🎯 Quick Start



### Build All Images (Recommended)

```bash

# Linux/Mac

./scripts/build_docker_images.sh



# Windows

.\scripts\build_docker_images.ps1
```



### Build Single Image

```bash
docker build \
  --build-arg SOURCE_COMMIT_SHA=$(git rev-parse HEAD) \
  --build-arg BUILD_VERSION=$(git describe --tags --always) \
  --build-arg SOURCE_DATE_EPOCH=$(git log -1 --format=%ct) \
  --build-arg BUILD_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
  -f Dockerfile.production \
  -t project-ai:production .
```



## 🔍 Verification



### Check Labels

```bash
docker inspect <image>:latest | jq '.[0].Config.Labels'
```



### Check Environment

```bash
docker run --rm <image>:latest env | grep SOURCE_DATE_EPOCH
```



## 📋 Build Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `SOURCE_COMMIT_SHA` | Git commit hash | `abc123def...` |
| `BUILD_VERSION` | Git tag or version | `v1.0.0-5-gabc123d` |
| `SOURCE_DATE_EPOCH` | Unix timestamp | `1705334445` |
| `BUILD_TIMESTAMP` | ISO 8601 timestamp | `2024-01-15T10:30:45Z` |



## 🏷️ OCI Labels

All images include these standard labels:

- `org.opencontainers.image.revision` - Git commit SHA
- `org.opencontainers.image.version` - Build version
- `org.opencontainers.image.created` - Build timestamp
- `org.opencontainers.image.source` - Repository URL



## 🔧 CI/CD Integration



### GitHub Actions

```yaml

- name: Build Image
  run: |
    docker build \
      --build-arg SOURCE_COMMIT_SHA=${{ github.sha }} \
      --build-arg BUILD_VERSION=${{ github.ref_name }} \
      --build-arg SOURCE_DATE_EPOCH=$(git log -1 --format=%ct) \
      --build-arg BUILD_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ") \
      -f Dockerfile.production \
      -t project-ai:production .

```



### GitLab CI

```yaml
build:
  script:

    - docker build 
        --build-arg SOURCE_COMMIT_SHA=$CI_COMMIT_SHA
        --build-arg BUILD_VERSION=$CI_COMMIT_TAG
        --build-arg SOURCE_DATE_EPOCH=$(git log -1 --format=%ct)
        --build-arg BUILD_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        -f Dockerfile.production
        -t project-ai:production .

```



## 📚 Documentation

- Full Guide: [`docs/DOCKER_REPRODUCIBILITY.md`](docs/DOCKER_REPRODUCIBILITY.md)
- Summary: [`DOCKER_REPRODUCIBILITY_SUMMARY.md`](DOCKER_REPRODUCIBILITY_SUMMARY.md)
- Build Scripts: [`scripts/build_docker_images.*`](scripts/)



## ✅ Benefits

- ✅ **Traceability** - Track every image to source code
- ✅ **Reproducibility** - Verify build outputs
- ✅ **Security** - Supply chain provenance
- ✅ **Compliance** - SLSA & SBOM requirements
- ✅ **Debugging** - Know exact version in production



## 🚀 Next Steps

1. Build images using automated scripts
2. Verify labels on built images
3. Update CI/CD pipelines with build args
4. Integrate into deployment workflows
