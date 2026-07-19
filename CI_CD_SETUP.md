# Project-AI CI/CD Setup Complete

## Current Status
✅ **CI/CD workflow exists**: `.github/workflows/docker-hub-publish.yaml`
✅ **Docker Compose verified**: All 7 services configured
✅ **Dockerfiles in place**: API, web portals, services, genesis
✅ **Local builds working**: Multi-stage optimized builds with DHI base images

## What's Already Set Up

### GitHub Actions Workflows
- **ci.yaml** — Runs on all branches:
  - Python (MyPy, Ruff, pytest, coverage >80%, canonical replay, frozen history)
  - Rust (fmt, clippy, tests)
  - Node (lint, test, build)
  - Android (unit tests, debug assembly)
  - Desktop (PyInstaller smoke test)
  - Windows installer (WiX build + smoke test)
  - Docker Compose (build, health checks, security verification)
  - Kubernetes (Helm lint + dry-run)
  - SBOM generation (CycloneDX)

- **docker-hub-publish.yaml** — Publishes on `main` branch and version tags:
  - API image
  - 3 web portals (docs, proof, operator-console)
  - 3 background services (swr, atlas, arbiter-rlp)
  - Genesis service
  - Uses registry caching for faster rebuilds
  - Auto-tags with `latest` + version number

### Docker Optimization
- Multi-stage builds: dependencies in builder layer, runtime only gets venv + code
- Layer caching: lock files copied first for dependency caching
- DHI (Docker Hardened Images): using `dhi.io/python:3.12-debian12-dev` for security
- Non-root user (UID 10001) in runtime stage
- Health checks on all services
- Read-only filesystems + `cap_drop: [ALL]`
- tmpfs for /tmp

### Image Tagging Strategy
**On `main` branch push (or manual `workflow_dispatch`):**
```
docker.io/iamsothirsty/project-ai-api:latest
```

**On version tag (e.g., `v1.2.3`):**
```
docker.io/iamsothirsty/project-ai-api:1.2.3
docker.io/iamsothirsty/project-ai-api:latest
```

## What You Need to Do in GitHub

### 1. Add Docker Hub Secret (if not already present)
Go to your repo **Settings → Secrets and variables → Actions** and add:

| Secret Name | Value |
|---|---|
| `PROJECT_AI` | Your Docker Hub Personal Access Token |

The Docker Hub username (`iamsothirsty`) is hardcoded in the workflow — it is public
information (it's the image namespace) and keeping it out of secrets avoids GitHub
masking image names in workflow logs.

**Get your Docker Hub PAT:**
1. Log in to [Docker Hub](https://hub.docker.com)
2. Go to **Account Settings → Security → Access Tokens**
3. Click **New Access Token**
4. Give it a descriptive name (e.g., "GitHub Actions Project-AI")
5. Select **Read, Write & Delete** permissions
6. Copy the token and paste into GitHub secret `PROJECT_AI`

### 2. Verify the Workflow
Push a test commit to `main`:
```bash
git add .
git commit -m "ci: enable docker hub publishing"
git push origin main
```

Go to **Actions** tab and watch the workflow run. Once the CI job completes green, the `docker-hub-publish` job will:
- Build all 7 images
- Push to Docker Hub
- Tag with commit SHA + `latest`

### 3. Create a Version Tag to Test Release Flow
```bash
git tag -a v0.0.1 -m "Initial development release"
git push origin v0.0.1
```

This triggers `docker-hub-publish` with version tagging:
```
project-ai-api:0.0.1
project-ai-api:latest
```

## Kubernetes Deployment

Your Helm chart is in `helm/project-ai/`. To deploy to a cluster:

```bash
# Validate locally first
helm lint helm/project-ai
helm template project-ai-dev helm/project-ai

# Deploy to cluster
helm install project-ai helm/project-ai \
  --namespace project-ai \
  --create-namespace \
  --set dockerImage.tag=latest \
  --set dockerImage.registry=docker.io \
  --set dockerImage.username=<your-docker-hub-username>
```

## Local Testing

### Build and run the full stack
```bash
docker compose up -d --build --wait
```

### Health check all services
```bash
curl http://localhost:8000/health/live        # API
curl http://localhost:4173/healthz            # Docs portal
curl http://localhost:4174/healthz            # Proof portal
curl http://localhost:4175/healthz            # Operator console
```

### View logs
```bash
docker compose logs -f api
docker compose logs -f postgres
```

### Stop everything
```bash
docker compose down
```

## What Happens on Each Git Event

| Event | Workflow | Triggered |
|---|---|---|
| Push to any branch | `ci.yaml` | All linting, tests, builds |
| Push to `main` | `docker-hub-publish.yaml` (after ci.yaml passes) | Publish all 7 images with `latest` tag |
| Push tag `v*` | `docker-hub-publish.yaml` (after ci.yaml passes) | Publish all 7 images with version tag |
| Weekly schedule | `nightly.yaml` | Vulnerability scans, SBOM generation |

## Next Steps

1. ✅ **Add GitHub Secret** (`PROJECT_AI` = Docker Hub PAT)
2. ✅ **Push a commit** to verify the workflow runs
3. ✅ **Create a release tag** (e.g., `v0.0.1`) to test version tagging
4. ✅ **Verify images on Docker Hub** — your username/project-ai-api, etc.
5. Deploy to Kubernetes or Docker Swarm using the published images

## Troubleshooting

**Workflow fails at Docker Hub login?**
- Check that `PROJECT_AI` is a **Personal Access Token**, not your password
- Ensure token has **Read, Write & Delete** permissions
- Verify the hardcoded username in the workflow matches your Docker Hub account

**Images not appearing on Docker Hub?**
- Check **Actions** tab for workflow logs
- Look for "Push to Docker Hub" step output
- Ensure the `ci.yaml` job completed successfully first (prerequisite for publish)

**Build times too long?**
- Registry cache is enabled in workflow (pulls cache from Docker Hub on rebuild)
- First build takes longer; subsequent builds reuse layers
- Consider using Docker Build Cloud for even faster builds

**Need to modify image names or tags?**
- Edit `.github/workflows/docker-hub-publish.yaml`
- Change the `tags:` section in each build step
- Follow pattern: `docker.io/{username}/project-ai-{service}:{version}`
