# Production Image Publishing Pipeline - Implementation Report

## Overview

Implemented **production-grade image publishing pipeline** for Project-AI using GitHub Actions and GitHub Container Registry (ghcr.io).

## Files Modified

### 1. `.github/workflows/publish.yaml` (NEW)
- **Purpose:** CI/CD pipeline for building and publishing container images
- **Key Features:**
  - Automated builds on `main` branch and release tags
  - Manual trigger support via `workflow_dispatch`
  - Matrix strategy for parallel builds (web portals, service adapters)
  - Immutable image tagging with version metadata
  - Build provenance attestation (SBOM included)
  - Layer caching via registry push-through
  - 7 services: api, docs-portal, proof-portal, swr, atlas, arbiter-rlp, genesis

### 2. `helm/values.prod.yaml` (NEW)
- **Purpose:** Production Helm configuration values
- **Key Features:**
  - Registry configuration: `ghcr.io` with organization namespace
  - Resource limits tuned for production (2-4x dev)
  - Multi-replica deployments (api=2, portals=2, adapters=1)
  - Pod Disruption Budget placeholders
  - Persistent volume configuration for audit data (10Gi)
  - TLS/Ingress framework (disabled, ready for implementation)
  - Network policy placeholders

### 3. `helm/project-ai/templates/_helpers.tpl` (MODIFIED)
- Added: `project-ai.image` template helper
- Supports full image reference construction: `registry/owner/name:tag`
- Backward compatible with development mode (empty registry falls back to local images)

### 4. `helm/project-ai/values.yaml` (MODIFIED)
- Added: `image.owner` and `image.tag` fields for production support
- Maintains development defaults (empty registry, local image names)

### 5. `helm/project-ai/templates/*.yaml` (MODIFIED)
- Updated all 5 deployment templates (api, portals, adapters, genesis)
- Changed: image reference from `.Values.<component>.image` to `include "project-ai.image"`
- Changed: replicas from hardcoded `1` to configurable `.Values.<component>.replicas`
- All templates now support both development and production modes

### 6. `.dockerignore` (VERIFIED)
- Existing optimization maintained
- Ensures lean production images

## Rationale

### Image Publishing Architecture

The workflow implements a **fan-out/fan-in pattern**:

1. **image-metadata job** determines version tag based on:
   - Semantic versioning for `v*` tags
   - Manual input for `workflow_dispatch`
   - Timestamped main branch builds
   - Timestamped dev branch builds

2. **Parallel build jobs** (build-api, build-web, build-adapters, build-genesis):
   - Each service built independently
   - Shared metadata output for consistency
   - Matrix strategy for web portals (docs, proof) and adapters (swr, atlas, arbiter-rlp)
   - Docker Buildx for multi-stage optimization

3. **Verification job** pulls all images post-build to verify:
   - Registry availability
   - Image manifest integrity
   - Architecture/OS metadata

4. **Release notes job** creates GitHub Release with:
   - Image reference list
   - Deployment instructions
   - Verification guidance

### Image Tagging Strategy

**Immutable by design:**

- Release tags: `v0.1.0`, `v0.1.0-rc1` → `ghcr.io/org/project-ai-api:v0.1.0`
- Main branch: `main-20250501-abc1234` (date + short SHA)
- Development branches: `dev-20250501-abc1234`
- Latest tag: Always points to most recent build

**Multi-tag support:**
- Semantic version tags (stable)
- Short SHA tags (traceable to commit)
- `latest` convenience tag (for development)

### Registry Authentication

- Uses `GITHUB_TOKEN` (automatic per GitHub Actions)
- Scoped permissions: `contents: read`, `packages: write`
- No manual token management required
- Seamless `ghcr.io` integration

### Build Optimization

- **Layer caching:** Via registry push-through (`type=registry`)
- **SBOM generation:** Automatic with `sbom: true`
- **Provenance attestation:** Recorded with `provenance: mode=max`
- **Multi-architecture support:** Ready for ARM64 via Buildx

## Security Considerations

### Image Identity & Provenance

1. **Build Provenance:**
   - Each image includes SLSA build attestation
   - Verifiable via `cosign verify-attestation <image>`
   - Traces to GitHub Actions job + commit SHA

2. **SBOM Attestation:**
   - Software Bill of Materials generated per image
   - CycloneDX format compatible with vulnerability scanners
   - Enables supply chain security scanning

3. **Image Signing:**
   - Provenance attestations provide cryptographic proof
   - Future implementation: `cosign sign` for additional key-based signatures
   - Deployment can enforce signature verification

### Access Control

1. **Registry Permissions:**
   - Scoped to GitHub Actions runner
   - `${{ secrets.GITHUB_TOKEN }}` automatically rotated
   - No hardcoded credentials in repository

2. **Registry ACLs:**
   - Private container registry (requires GitHub org membership)
   - Image visibility: `private` by default (configure per organization policy)

3. **Tag Immutability:**
   - Semantic version tags (v0.1.0) are immutable
   - Branch/timestamp tags are immutable (SHA-based)
   - Prevents accidental image overwrites

### Runtime Security (Helm)

1. **Image Pull Policy:**
   - Production: `IfNotPresent` (after pull verification)
   - Prevents unexpected image updates
   - Can be set to `Always` for rolling security patches

2. **Container Security:**
   - Non-root user (UID 10001)
   - Read-only root filesystem
   - Dropped ALL capabilities
   - seccomp: RuntimeDefault

3. **Secrets Management:**
   - Placeholders in values.prod.yaml (e.g., `PROJECT_AI_API_TOKEN`)
   - Injected via Kubernetes Secret references (next phase)
   - Never baked into images

## Rollback Strategy

### Immediate Rollback (Production Image Issue)

```bash
# 1. Identify last stable image
STABLE_IMAGE="ghcr.io/org/project-ai-api:v0.1.0"

# 2. Rollback deployment
helm upgrade project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set image.tag=v0.1.0 \
  --reuse-values

# 3. Verify pods are running
kubectl rollout status deployment/project-ai-api -n default
```

### Rollback via Git

```bash
# 1. Revert problematic commit
git revert <commit-sha>
git push origin main

# 2. Previous images already published
# GitHub Actions automatically builds from main

# 3. After build completes
helm upgrade project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set image.tag=main-20250501-def5678
```

### CI/CD Rollback Safeguards

1. **Concurrency control:** `cancel-in-progress: false`
   - Prevents concurrent builds from overwriting each other

2. **Build verification job:**
   - Ensures all images pulled successfully before release notes
   - Workflow fails if any image unavailable

3. **Manual approval option:**
   - Edit `.github/workflows/publish.yaml` to add `environment: production`
   - Requires manual approval before publishing to ghcr.io
   - Implement after next component deployment

## Validation Commands

### 1. Verify Helm Chart Syntax

```bash
helm lint helm/project-ai --strict
```

**Expected Output:**
```
==> Linting helm/project-ai
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

### 2. Render Helm Templates (Development Mode)

```bash
helm template project-ai-dev helm/project-ai \
  -f helm/project-ai/values.yaml
```

**Verify Output Contains:**
```
image: project-ai-development-api
image: project-ai-development-docs-portal
image: project-ai-development-proof-portal
image: project-ai-development-swr
image: project-ai-development-atlas
image: project-ai-development-arbiter-rlp
image: project-ai-development-genesis
```

### 3. Render Helm Templates (Production Mode)

```bash
helm template project-ai-prod helm/project-ai \
  -f helm/values.prod.yaml \
  --set image.owner=myorg \
  --set image.tag=v0.1.0
```

**Verify Output Contains:**
```
image: ghcr.io/myorg/project-ai-api:v0.1.0
image: ghcr.io/myorg/project-ai-docs-portal:v0.1.0
image: ghcr.io/myorg/project-ai-proof-portal:v0.1.0
image: ghcr.io/myorg/project-ai-swr:v0.1.0
image: ghcr.io/myorg/project-ai-atlas:v0.1.0
image: ghcr.io/myorg/project-ai-arbiter-rlp:v0.1.0
image: ghcr.io/myorg/project-ai-genesis:v0.1.0
```

### 4. Verify Workflow File Syntax

```bash
cat .github/workflows/publish.yaml | grep -E '^name:|^on:|^  [a-z-]+:$|    runs-on:|    permissions:'
```

**Expected Output:**
- Top-level `name:` (Publish)
- Top-level `on:` (push/workflow_dispatch)
- Multiple job names (image-metadata, build-api, build-web, etc.)
- Each job has `runs-on: ubuntu-latest`
- Build jobs have `permissions:` section

### 5. Test Version Extraction Logic

```bash
# Main branch build
export GITHUB_REF=refs/heads/main
export GITHUB_SHA=abc1234567890
VERSION="main-$(date +%Y%m%d)-$(echo $GITHUB_SHA | cut -c1-7)"
echo $VERSION  # main-20250501-abc1234

# Release tag build
export GITHUB_REF=refs/tags/v0.1.0
VERSION="${GITHUB_REF##*/}"
echo $VERSION  # v0.1.0
```

### 6. Validate Production Values Schema

```bash
helm template test-release helm/project-ai \
  -f helm/values.prod.yaml \
  --set image.owner=test \
  --set image.tag=test \
  --dry-run=client \
  --validate
```

**Expected:** No errors, valid Kubernetes manifests

## Deployment Verification Commands

### 1. Verify Images Are Published

```bash
# After workflow completes, check ghcr.io
docker login ghcr.io
docker pull ghcr.io/myorg/project-ai-api:v0.1.0
docker pull ghcr.io/myorg/project-ai-genesis:v0.1.0
# ... repeat for all 7 services
```

### 2. Verify Image Manifests

```bash
# Check image metadata
docker inspect ghcr.io/myorg/project-ai-api:v0.1.0 | jq '.[] | {Architecture, Os, Created, Size}'
```

### 3. List Published Tags

```bash
# Via ghcr.io API or docker CLI
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
  https://ghcr.io/v2/myorg/project-ai-api/tags/list

# Or use gh CLI
gh api repos/myorg/project-ai/packages --paginate | jq '.[] | select(.package_type=="container")'
```

### 4. Deploy via Helm (Production)

```bash
helm upgrade --install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set image.owner=myorg \
  --set image.tag=v0.1.0 \
  --namespace project-ai-prod \
  --create-namespace
```

### 5. Verify Kubernetes Deployment

```bash
kubectl get deployments -n project-ai-prod
kubectl get pods -n project-ai-prod
kubectl describe pod -n project-ai-prod <pod-name>
kubectl logs -n project-ai-prod <pod-name> -c <container-name>
```

### 6. Verify Image References in Running Pods

```bash
kubectl get pods -n project-ai-prod \
  -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}'
```

### 7. Check Image Pull Success

```bash
kubectl describe pod -n project-ai-prod <pod-name> | grep -A 5 "Pull"
```

### 8. Verify BuildKit Attestations (Optional)

```bash
# Requires cosign installation: https://github.com/sigstore/cosign/releases
cosign verify-attestation \
  --certificate-identity "https://github.com/.../project-ai/.github/workflows/publish.yaml" \
  ghcr.io/myorg/project-ai-api:v0.1.0
```

## Production Deployment Checklist

Before deploying to production:

- [ ] Update `.github/workflows/publish.yaml` with your GitHub organization
- [ ] Create GitHub release tag: `git tag v0.1.0 && git push --tags`
- [ ] Wait for GitHub Actions `Publish` workflow to complete
- [ ] Verify images appear in ghcr.io (Settings > Packages & Registries)
- [ ] Pull and inspect images locally: `docker pull ghcr.io/myorg/project-ai-api:v0.1.0`
- [ ] Update `helm/values.prod.yaml`:
  - [ ] Set `image.owner: myorg`
  - [ ] Set `image.tag: v0.1.0`
  - [ ] Set `persistence.storageClass` to your cluster's storage class
  - [ ] Set `ingress.hosts[0].host` to your domain
- [ ] Deploy: `helm upgrade --install project-ai ./helm/project-ai -f helm/values.prod.yaml -n production --create-namespace`
- [ ] Verify pods are running: `kubectl get pods -n production`
- [ ] Verify readiness: `kubectl get endpoints -n production`

## Next Steps (Future Production Blockers)

This implementation enables:

1. **Immutable Image Tagging** (already implemented via semantic versioning)
2. **Container Image Signing** (via `cosign sign` in workflow)
3. **Kubernetes Secret Integration** (placeholders in values.prod.yaml)
4. **Production Helm Values** (completed with helm/values.prod.yaml)
5. **Ingress & TLS** (framework in place, awaiting cert-manager integration)

## References

- GitHub Actions Documentation: https://docs.github.com/en/actions
- GitHub Container Registry: https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry
- Helm Values Documentation: https://helm.sh/docs/chart_best_practices/values/
- SLSA Build Provenance: https://slsa.dev/spec/
- CycloneDX SBOM: https://cyclonedx.org/
