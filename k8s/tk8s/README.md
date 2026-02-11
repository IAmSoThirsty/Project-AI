# TK8S - Thirsty's Kubernetes
## Civilization-Grade Sovereign Orchestration Layer for Project-AI

> **No wrappers. No managed magic. No YAML sprawl chaos.**  
> **Everything constitutional. Everything deterministic.**

---

## Quick Start

### Prerequisites

- Kubernetes cluster 1.29+ (managed or self-hosted)
- kubectl configured and authenticated
- ArgoCD installed in cluster
- Cosign for image signing
- Syft for SBOM generation

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI/k8s/tk8s
```

2. **Apply namespaces:**
```bash
kubectl apply -f namespaces/tk8s-namespaces.yaml
```

3. **Deploy base infrastructure:**
```bash
kubectl apply -k .
```

4. **Install ArgoCD applications:**
```bash
kubectl apply -f argocd/applications.yaml
```

5. **Verify deployment:**
```bash
kubectl get pods -n project-ai-core
kubectl get pods -n project-ai-eca
kubectl get networkpolicies -A
```

---

## Architecture Overview

### Layering Model

```
┌─────────────────────────────────────────────┐
│  Layer 5: Observability + Audit            │
│  Prometheus, Grafana, Loki, Tempo          │
├─────────────────────────────────────────────┤
│  Layer 4: External Amplifiers              │
│  ECA / Ultra (Maximum Isolation)           │
├─────────────────────────────────────────────┤
│  Layer 3: Governance & Security            │
│  TARL, Cerberus, Kyverno, Falco, OPA      │
├─────────────────────────────────────────────┤
│  Layer 2: Sovereign Services               │
│  Project-AI Core, Memory Systems           │
├─────────────────────────────────────────────┤
│  Layer 1: Kubernetes Core                  │
│  etcd, API server, Controllers             │
├─────────────────────────────────────────────┤
│  Layer 0: Hardware / Cloud Substrate       │
│  Compute, Storage, Network                 │
└─────────────────────────────────────────────┘
```

### Namespace Segmentation

| Namespace | Layer | Purpose | Isolation |
|-----------|-------|---------|-----------|
| `project-ai-core` | 2 | Core application services | Standard |
| `project-ai-security` | 3 | TARL, Cerberus, governance | High |
| `project-ai-memory` | 2 | PostgreSQL, Redis, knowledge base | Standard |
| `project-ai-eca` | 4 | External Cognition Amplifier | **Maximum** |
| `project-ai-monitoring` | 5 | Prometheus, Grafana, Loki, Tempo | Standard |
| `project-ai-system` | 1 | Vault, cert-manager, system services | High |

---

## Core Principles

### 1. Single Monorepo Authority
All infrastructure as code lives in this repository. Git is the single source of truth.

### 2. Signed Images Only
Every container image must be signed with Cosign. Kyverno admission controller enforces this.

```bash
# Sign an image
cosign sign --key cosign.key ghcr.io/iamsothirsty/project-ai-core:v1.0.0

# Verify signature
cosign verify --key cosign.pub ghcr.io/iamsothirsty/project-ai-core:v1.0.0
```

### 3. SBOM Mandatory
Software Bill of Materials required for every image.

```bash
# Generate SBOM
syft ghcr.io/iamsothirsty/project-ai-core:v1.0.0 -o spdx-json > sbom.json
```

### 4. No Mutable Containers
- `latest` tag forbidden
- Read-only root filesystem enforced
- No in-place modifications

### 5. No Shell Access in Production
- No `kubectl exec` into production pods
- Debug containers blocked via Kyverno
- All debugging via logs and traces only

---

## CI/CD Pipeline

The TK8S Civilization Pipeline (`tk8s-civilization-pipeline.yml`) implements:

```
┌──────────────────────────────────────────────────┐
│  1. Static Analysis (Ruff, Bandit)              │
│  2. Unit Tests (pytest with coverage)           │
│  3. E2E Tests                                    │
│  4. Canonical Invariants                        │
│  5. Red Team Simulation                         │
│  6. Docker Build (multi-arch)                   │
│  7. Trivy Container Scan                        │
│  8. SBOM Generation (Syft)                      │
│  9. Image Signing (Cosign)                      │
│ 10. Push to Registry                            │
│ 11. ArgoCD Sync to Staging                      │
│ 12. Regression Replay                           │
│ 13. Manual Constitutional Approval              │
│ 14. Production Promotion                        │
│ 15. CIVILIZATION LOCK                           │
└──────────────────────────────────────────────────┘
```

### Triggering the Pipeline

```bash
# Push to main branch (auto-deploys to staging)
git push origin main

# Create a release tag (triggers production pipeline)
git tag -s v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

---

## Security Layer

### Kyverno Policies

TK8S uses Kyverno for admission control:

- ✅ Image signature verification
- ✅ SBOM annotation enforcement
- ✅ No mutable containers
- ✅ No shell access
- ✅ Read-only root filesystem
- ✅ ECA isolation enforcement
- ✅ Resource limits required

### Network Policies

Default-deny with explicit allow rules:

```yaml
# ECA namespace: Default deny all
- Ingress: Blocked
- Egress: DNS + HTTPS only (no internal cluster communication)

# Core namespace: Standard isolation
- Ingress: From ingress controller + monitoring
- Egress: To memory namespace + external APIs

# Security namespace: High isolation
- Ingress: From monitoring only
- Egress: Read-only access to all namespaces
```

### RBAC

Least privilege access control:

- Service accounts per component
- No cluster-admin in production
- Monitoring has read-only cluster role
- ECA has minimal permissions

---

## Observability

### Metrics Tracked

1. **Policy Enforcement:**
   - Policy rejection rate
   - Image signature validation failures
   - SBOM annotation missing count

2. **Canonical Invariants:**
   - Invariant failure count
   - Replay scenario success rate
   - Four Laws compliance rate

3. **Security:**
   - Falco runtime violations
   - Trivy CVE detections
   - ECA isolation breach attempts

4. **Performance:**
   - Pod restart rate
   - Memory/CPU utilization
   - Token spend rate

### Dashboards

Grafana dashboards available at `/k8s/tk8s/monitoring/`:

- TK8S Civilization Overview
- Policy Compliance
- Security Alerts
- Canonical Invariant Status
- Resource Utilization

---

## Deployment Workflows

### Staging Deployment (Automatic)

```bash
# Push to main branch
git push origin main

# ArgoCD auto-syncs to staging
# Regression tests run automatically
# Results available in CI/CD logs
```

### Production Deployment (Manual Approval)

```bash
# After successful staging deployment
# Obtain constitutional approval from:
# - Technical Lead
# - Security Officer
# - Product Owner

# Create signed release tag
git tag -s v1.0.0 -m "Production release v1.0.0"
git push origin v1.0.0

# Pipeline promotes to production
# CIVILIZATION LOCK applied
# Timeline updated automatically
```

### Rollback

```bash
# Via ArgoCD (instant)
argocd app rollback project-ai-core

# Via Git (if ArgoCD unavailable)
git revert HEAD
git push origin main
```

---

## Release Strategy

### Versioning

```
v{major}.{minor}.{patch}-{component}

Examples:
  v1.0.0-core      # Core application
  v1.0.0-eca       # External Cognition Amplifier
  v1.0.0-tk8s      # TK8S infrastructure
```

### Promotion Levels

1. **DEV:** Fast iteration, optional security
2. **STAGING:** Full security, regression testing
3. **PRODUCTION:** Manual approval, full audit
4. **CIVILIZATION LOCK:** Immutable, permanent record

---

## Troubleshooting

### Common Issues

**1. Image signature verification failed**
```bash
# Check if image is signed
cosign verify --key cosign.pub <image>

# Re-sign image if needed
cosign sign --key cosign.key <image>
```

**2. SBOM annotation missing**
```bash
# Generate SBOM
syft <image> -o spdx-json > sbom.json

# Calculate SHA256
sha256sum sbom.json

# Add annotation to deployment
kubectl annotate deployment/<name> \
  tk8s.io/sbom-sha256=<hash> \
  -n <namespace>
```

**3. Network policy blocking traffic**
```bash
# Check current policies
kubectl get networkpolicies -A

# Describe specific policy
kubectl describe networkpolicy <name> -n <namespace>

# Temporarily allow all (testing only)
kubectl delete networkpolicy <name> -n <namespace>
```

**4. Pod failing to start**
```bash
# Check pod status
kubectl get pods -n <namespace>

# View pod events
kubectl describe pod <pod-name> -n <namespace>

# Check logs
kubectl logs <pod-name> -n <namespace>

# Check security context
kubectl get pod <pod-name> -n <namespace> -o yaml | grep -A 10 securityContext
```

---

## Development

### Local Testing

```bash
# Validate manifests
kubectl apply --dry-run=client -k .

# Check with kubeval
kubeval **/*.yaml

# Score with kube-score
kube-score score **/*.yaml
```

### Adding New Components

1. Create deployment manifest in `deployments/`
2. Add network policy in `network-policies/`
3. Add RBAC in `rbac/`
4. Update kustomization.yaml
5. Add Kyverno policies if needed
6. Update ArgoCD applications
7. Document in CIVILIZATION_TIMELINE.md

---

## Documentation

- **[TK8S_DOCTRINE.md](../../docs/TK8S_DOCTRINE.md)** - Complete doctrine and principles
- **[CIVILIZATION_TIMELINE.md](../../docs/CIVILIZATION_TIMELINE.md)** - Release history and tracking
- **[Workflow Architecture](../../.github/workflows/tk8s-civilization-pipeline.yml)** - CI/CD pipeline

---

## Support

- **Issues:** https://github.com/IAmSoThirsty/Project-AI/issues
- **Discussions:** https://github.com/IAmSoThirsty/Project-AI/discussions
- **Email:** tk8s@project-ai.example.com

---

## License

MIT License - See [LICENSE](../../LICENSE) for details

---

**Status:** Production Ready  
**Version:** 1.0.0  
**Last Updated:** 2026-02-11  
**Maintained By:** TK8S Core Team
