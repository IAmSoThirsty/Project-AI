# 🏛️ Sovereign CI/CD - Quick Reference Card

## 🚀 One-Page Cheat Sheet

### Pipeline Trigger

```bash

# Automatic triggers

git push origin main              # Runs full pipeline + Docker push
git push origin feature-branch    # Runs validation only (PR)
git tag -s v1.2.3                 # Release pipeline with attestation
```

### Pipeline Phases (12 Total)

1. 🔐 **Source Trust** - Commit signature verification
1. 🐍 **Environment** - Hash-locked dependency install
1. 🔍 **Static Analysis** - Ruff linting
1. 🧪 **Unit Tests** - Pytest with coverage
1. ⚡ **TARL** - Runtime enforcement tests
1. 🎯 **Canonical** - 5 invariants (MUST PASS)
1. 🛡️ **Adversarial** - Red team evaluation
1. 📋 **SBOM** - Syft SPDX generation
1. 🐳 **Docker** - Multi-stage build + push
1. 🔏 **Attestation** - SLSA 3 provenance
1. 📦 **Artifacts** - Upload trace, SBOM, reports
1. 📊 **Summary** - Trust boundary report

### Critical Files

```
.github/workflows/project-ai-monolith.yml    # Main pipeline
Dockerfile                                    # Pinned to digest
requirements.lock                             # Hash-validated deps
canonical/replay.py                           # 5 invariants
docs/SUPPLY_CHAIN_SECURITY.md                # Threat coverage
docs/REPOSITORY_HARDENING.md                 # Config guide
scripts/verify-supply-chain.sh               # External verifier
```

### Trust Boundaries (7 Layers)

```
Source → Workflow → Dependency → Execution →
Artifact → Registry → Auditability
```

### Threat Coverage: 13/13 ✅

1. Dependency Substitution → Hash validation
1. Action Supply Chain → SHA pinning
1. Registry Impersonation → Hardcoded GHCR
1. Digest Mutation → Attestation signature
1. Replay Attack → Temporal metadata
1. Privilege Escalation → Minimal perms
1. Artifact Tampering → Immutable storage
1. Silent Failure → Explicit exits
1. Floating Tag Poison → Digest pinning
1. Build Drift → Canonical replay
1. Base Image Compromise → Digest pinning
1. Tool Injection → Official sources
1. Context Leakage → Secret masking

### Release Gates (All Required)

- [ ] Unit tests passed
- [ ] TARL integration passed
- [ ] Canonical 5/5 invariants passed
- [ ] Adversarial suite evaluated
- [ ] SBOM generated
- [ ] Attestation signed
- [ ] Digest stored
- [ ] Trace uploaded
- [ ] Branch protection satisfied

### Verification Commands

```bash

# Check workflow run

gh run view <RUN_ID>

# Verify supply chain

./scripts/verify-supply-chain.sh <RUN_ID>

# Verify image

IMAGE_DIGEST=$(docker inspect ghcr.io/iamsothirsty/project-ai:main \
  --format='{{index .RepoDigests 0}}' | cut -d@ -f2)
gh attestation verify \
  --repo IAmSoThirsty/Project-AI \
  ghcr.io/iamsothirsty/project-ai@${IMAGE_DIGEST}

# Download artifacts

gh run download <RUN_ID> -n sbom
gh run download <RUN_ID> -n canonical-execution-trace
```

### Repository Configuration

```bash

# Check current config

./scripts/configure-repository.sh --check-only

# Apply hardening

./scripts/configure-repository.sh
```

### Branch Protection Requirements

- **main** and **release** branches:
  - ✅ 2+ required approvals
  - ✅ Signed commits required
  - ✅ Linear history enforced
  - ✅ Status checks required
  - ✅ Dismiss stale reviews
  - ✅ Require conversation resolution

### Security Features Required

- ✅ Dependabot alerts enabled
- ✅ Dependabot security updates enabled
- ✅ CodeQL scanning enabled
- ✅ Secret scanning enabled
- ✅ Secret push protection enabled

### Artifacts Retention

- SBOM: **365 days** (compliance)
- Execution trace: **90 days** (audit)
- Adversarial reports: **90 days** (security)
- Coverage reports: **30 days** (quality)

### Action Versions (SHA Pinned)

```yaml
actions/checkout@v4.2.2
actions/setup-python@v5.3.0
actions/upload-artifact@v4.5.0
docker/login-action@v3.3.0
docker/build-push-action@v6.10.0
docker/setup-buildx-action@v3.7.1
docker/metadata-action@v5.6.1
actions/attest-build-provenance@v2.0.0
```

### Docker Base Image (Pinned)

```dockerfile
FROM python:3.11-slim@sha256:0b23cfb7425d065008b778022a17b1551c82f8b4866ee5a7a200084b7e2eafbf
```

### Environment Variables

```yaml
REGISTRY: ghcr.io
IMAGE_NAME: ${{ github.repository }}
PYTHON_VERSION: "3.11"
```

### Permissions (Minimal)

```yaml
contents: read          # Read repository
packages: write         # Push to GHCR
attestations: write     # Build provenance
id-token: write         # OIDC token
```

### Common Issues & Solutions

**Issue**: Hash validation failed

```bash

# Regenerate lock file

pip-compile --generate-hashes -o requirements.lock requirements.in
```

**Issue**: Canonical replay failed

```bash

# Run locally to debug

python canonical/replay.py --verbose
```

**Issue**: Commit not signed

```bash

# Configure GPG signing

git config --global commit.gpgsign true
git config --global user.signingkey YOUR_KEY_ID
```

**Issue**: Docker digest changed

```bash

# Get new digest

docker pull python:3.11-slim
docker inspect python:3.11-slim --format='{{index .RepoDigests 0}}'

# Update Dockerfile

```

### Compliance Status

- **SLSA Level**: 3 ✅
- **NIST SSDF**: Aligned ✅
- **Supply Chain**: 13/13 threats mitigated ✅
- **Trust Boundaries**: 7/7 enforced ✅

### Key Documentation

- Implementation: `docs/SOVEREIGN_CICD_IMPLEMENTATION.md`
- Security: `docs/SUPPLY_CHAIN_SECURITY.md`
- Hardening: `docs/REPOSITORY_HARDENING.md`
- Workflows: `.github/workflows/README.md`

### Emergency Contacts

- **Workflow Issues**: Check run logs with `gh run view`
- **Security Issues**: Review adversarial reports
- **Build Issues**: Check canonical trace
- **Config Issues**: Run `./scripts/configure-repository.sh --check-only`

______________________________________________________________________

**Version**: 1.0.0 | **Status**: ✅ Production | **Updated**: 2026-02-13

🏛️ **SOVEREIGN. SEALED. SUPREME.**
