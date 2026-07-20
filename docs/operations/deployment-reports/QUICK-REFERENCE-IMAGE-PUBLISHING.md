# Quick Reference: Production Image Publishing Pipeline

> **Current release boundary (2026-07-19):** This is a historical or
> implementation-reference artifact, not current production evidence or
> deployment approval. The v0.0.3 successor remains fail-closed until the
> [pre-deployment checklist](../../deployment/PRE_DEPLOYMENT_CHECKLIST.md) and
> [CAB evidence bundle](../cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md)
> pass. Commands here are examples; this document does not prove deployment.

## Verify Implementation

### 1. Check Helm Chart
```bash
helm lint helm/project-ai --strict
```

### 2. Development Mode (local builds)
```bash
helm template project-ai-dev helm/project-ai -f helm/project-ai/values.yaml | grep "image:"
```

Expected output: `image: project-ai-development-*`

### 3. Production Mode (ghcr.io)
```bash
helm template project-ai-prod helm/project-ai \
  -f helm/values.prod.yaml \
  --set image.owner=myorg \
  --set image.tag=v0.1.0 | grep "image:"
```

Expected output: `image: ghcr.io/myorg/project-ai-*:v0.1.0`

## Deploy to Production

### Step 1: Create Release Tag
```bash
git tag v0.1.0
git push origin v0.1.0
```

### Step 2: Wait for GitHub Actions
- Monitor: https://github.com/YOUR-ORG/project-ai/actions/workflows/publish.yaml
- All 7 images must build successfully
- Check: ghcr.io → Your Organization → Packages

### Step 3: Deploy with Helm
```bash
helm upgrade --install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set image.owner=YOUR-ORG \
  --set image.tag=v0.1.0 \
  --namespace project-ai-prod \
  --create-namespace
```

### Step 4: Verify Deployment
```bash
kubectl get pods -n project-ai-prod
kubectl get pods -n project-ai-prod -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}'
```

## Rollback (If Needed)

### Immediate Rollback to Previous Version
```bash
helm upgrade project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set image.tag=v0.0.9 \
  --namespace project-ai-prod
```

### Git-Based Rollback
```bash
git revert <commit-sha>
git push origin main
# Wait for GitHub Actions to rebuild
# Then: helm upgrade --set image.tag=main-20250501-xyz789 ...
```

## Configuration

### Update Organization in Values
Edit `helm/values.prod.yaml`:
```yaml
image:
  registry: ghcr.io
  owner: YOUR-GITHUB-ORG-OR-USERNAME  # <- Change this
  tag: v0.1.0
```

### Update Storage Class
Edit `helm/values.prod.yaml`:
```yaml
persistence:
  storageClass: "standard"  # <- Set to your cluster's storage class
```

## Troubleshooting

### Image Pull Failed
```bash
kubectl describe pod -n project-ai-prod <pod-name>
# Check: ImagePullBackOff, Authentication errors
# Solution: Verify image exists in ghcr.io, registry credentials
```

### Pods Not Ready
```bash
kubectl logs -n project-ai-prod <pod-name> -c <container-name>
# Check: Application startup errors
```

### Check Published Images
```bash
docker login ghcr.io  # Use GitHub token as password
docker pull ghcr.io/YOUR-ORG/project-ai-api:v0.1.0
docker inspect ghcr.io/YOUR-ORG/project-ai-api:v0.1.0 | jq '.[] | {Architecture, Os, Created, Size}'
```

## Files Reference

| File | Purpose |
|------|---------|
| `.github/workflows/publish.yaml` | Automated image build and publish |
| `helm/values.prod.yaml` | Production Helm values |
| `helm/project-ai/templates/_helpers.tpl` | Image reference templating |
| `helm/project-ai/values.yaml` | Development Helm values (updated) |
| `helm/project-ai/templates/*.yaml` | Deployment manifests (updated) |

## Key Features

✓ **Immutable Tagging**: Semantic versioning (v0.1.0) + git SHA
✓ **Multi-Service**: 7 services built in parallel
✓ **Layer Caching**: Speeds up subsequent builds
✓ **Build Provenance**: SLSA attestations per image
✓ **SBOM**: CycloneDX software bill of materials
✓ **Automatic Verification**: Images tested post-build
✓ **Release Notes**: GitHub Release creation
✓ **No Credentials**: Uses GitHub Token (auto-rotated)

## Next Steps

1. Update `helm/values.prod.yaml` with your organization
2. Create first release tag
3. Monitor GitHub Actions workflow
4. Deploy with Helm
5. Verify pods are running
6. Check attestations: `cosign verify-attestation ghcr.io/myorg/project-ai-api:v0.1.0`

---

**Documentation**: See IMPLEMENTATION-REPORT-IMAGE-PUBLISHING.md for full details
