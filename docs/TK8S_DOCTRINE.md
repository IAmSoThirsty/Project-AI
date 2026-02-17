# TK8S DOCTRINE

## Thirsty's Kubernetes - Civilization-Grade Sovereign Orchestration Layer

> **No wrappers. No managed magic. No YAML sprawl chaos.** **Everything constitutional. Everything deterministic.**

______________________________________________________________________

## I. FOUNDATIONAL DOCTRINE

### Non-Negotiables

These are immutable principles that cannot be violated:

1. **Single Monorepo Authority**

   - All infrastructure as code lives in one repository
   - No scattered configurations across multiple repos
   - Git is the single source of truth for all deployments

1. **Git = Source of Truth**

   - All changes flow through Git
   - ArgoCD enforces Git-declared state
   - No manual kubectl changes in production
   - No configuration drift allowed

1. **Signed Images Only**

   - Every container image must be signed with Cosign
   - Kyverno admission controller enforces signatures
   - Unsigned images are rejected at admission time
   - Public key infrastructure managed via cert-manager

1. **SBOM Mandatory**

   - Software Bill of Materials required for every image
   - Generated automatically in CI/CD pipeline
   - Both SPDX and CycloneDX formats
   - SHA256 hash recorded in deployment annotation

1. **No Mutable Containers**

   - `latest` tag forbidden
   - All images must use immutable digests or semantic versions
   - Read-only root filesystem enforced
   - No in-place modifications allowed

1. **No Shell Access in Production**

   - Ephemeral containers forbidden via Kyverno policy
   - No `kubectl exec` into production pods
   - Debug containers blocked at admission
   - All debugging via logs and traces only

1. **All Secrets via Vault / SealedSecrets**

   - No plain-text secrets in Git
   - Vault integration for dynamic secrets
   - SealedSecrets for static secrets
   - Automatic rotation where possible

1. **All Deployments Must Pass Canonical Invariants**

   - Five canonical invariants verified before deployment
   - Replay scenario must succeed in staging
   - No bypass mechanism exists
   - Failures block promotion to production

1. **External Cognition (Ultra) Runs in Isolation Namespace**

   - ECA has its own namespace (`project-ai-eca`)
   - Maximum security isolation enforced
   - No cross-namespace writes permitted
   - Egress-only network policy

1. **Cerberus Monitors Cluster Integrity**

   - Security namespace monitors all clusters
   - Real-time policy violation detection
   - Automatic alerting on anomalies
   - Continuous compliance verification

______________________________________________________________________

## II. TK8S CLUSTER ARCHITECTURE

### Layering Model

```
┌─────────────────────────────────────────────┐
│  Layer 5: Observability + Audit            │
│  (Prometheus, Grafana, Loki, Tempo)        │
├─────────────────────────────────────────────┤
│  Layer 4: External Amplifiers              │
│  (ECA / Ultra - Maximum Isolation)         │
├─────────────────────────────────────────────┤
│  Layer 3: Governance & Security            │
│  (TARL, Cerberus, Kyverno, Falco, OPA)    │
├─────────────────────────────────────────────┤
│  Layer 2: Sovereign Services               │
│  (Project-AI Core, Memory Systems)         │
├─────────────────────────────────────────────┤
│  Layer 1: Kubernetes Core                  │
│  (etcd, API server, Controllers)           │
├─────────────────────────────────────────────┤
│  Layer 0: Hardware / Cloud Substrate       │
│  (Compute, Storage, Network)               │
└─────────────────────────────────────────────┘
```

### Design Principles

- **Separation of Concerns:** Each layer has distinct responsibilities
- **Defense in Depth:** Multiple security layers reinforce each other
- **Fail Secure:** Default-deny for all network and access policies
- **Least Privilege:** Minimum permissions required for each component
- **Immutable Infrastructure:** No configuration changes post-deployment
- **Observable:** Full tracing, logging, and metrics at every layer

______________________________________________________________________

## III. NAMESPACE SEGMENTATION

### Namespace Structure

```yaml
project-ai-core         # Layer 2: Core application services
project-ai-security     # Layer 3: TARL, Cerberus, governance
project-ai-memory       # Layer 2: PostgreSQL, Redis, knowledge base
project-ai-eca          # Layer 4: External Cognition Amplifier
project-ai-monitoring   # Layer 5: Prometheus, Grafana, Loki, Tempo
project-ai-system       # Layer 1: Vault, cert-manager, system services
```

### Cross-Namespace Communication Rules

1. **No cross-namespace writes without policy approval**

   - All cross-namespace communication must be explicitly allowed
   - Network policies enforce isolation by default
   - Write operations require elevated approval

1. **Monitoring namespace has read-only access**

   - Can scrape metrics from all namespaces
   - Cannot modify any resources
   - Alerts can trigger external actions only

1. **ECA namespace is fully isolated**

   - Cannot initiate connections to other namespaces
   - Egress-only to external APIs
   - No service account token mounted
   - Maximum security posture

1. **Security namespace monitors all**

   - Read-only access to all namespaces
   - Can query API server for compliance
   - Generates alerts but cannot auto-remediate
   - Human approval required for changes

______________________________________________________________________

## IV. SECURITY LAYER

### Mandatory Security Components

1. **Kyverno Policy Engine**

   - Admission control for all resources
   - Validates image signatures
   - Enforces SBOM annotations
   - Blocks mutable containers
   - Prevents shell access

1. **Falco Runtime Detection**

   - Monitors syscalls for anomalies
   - Detects privilege escalation attempts
   - Alerts on suspicious file access
   - Integrates with Prometheus for metrics

1. **OPA Gatekeeper**

   - Custom policy constraints
   - Resource quota enforcement
   - Label and annotation validation
   - Namespace isolation rules

1. **Trivy Admission Scanner**

   - Scans images at admission time
   - Blocks HIGH and CRITICAL vulnerabilities
   - Integrates with CI/CD pipeline
   - Generates alerts for new CVEs

1. **Cert-Manager (Internal PKI)**

   - Issues certificates for internal services
   - Automatic rotation
   - Mutual TLS between services
   - Integration with Vault

1. **Cosign Image Signing**

   - Keyless signing via GitHub OIDC
   - Signature verification at admission
   - Public key distribution via configmap
   - Signature stored in OCI registry

______________________________________________________________________

## V. CI/CD PIPELINE - CIVILIZATION GRADE

### Pipeline Philosophy

> **Every commit must survive the entire gauntlet. No bypass.**

### Pipeline Stages

```
Developer Push
    │
    ├─ Pre-commit Hooks (local validation)
    │
    ▼
GitHub Actions: Civilization Pipeline
    │
    ├─ 1. Static Analysis (Ruff, Bandit)
    ├─ 2. Unit Tests (pytest with coverage)
    ├─ 3. E2E Tests (full application scenarios)
    ├─ 4. Canonical Invariants (replay.py)
    ├─ 5. Red Team Simulation (adversarial testing)
    ├─ 6. Docker Build (multi-arch)
    ├─ 7. Trivy Scan (container vulnerabilities)
    ├─ 8. SBOM Generation (Syft)
    ├─ 9. Image Signing (Cosign)
    └─ 10. Push to Registry (ghcr.io)
           │
           ▼
ArgoCD Auto-Sync → Staging
           │
           ├─ Automated Regression Replay
           ├─ Monitoring Validation
           └─ Smoke Tests
           │
           ▼
Manual Constitutional Approval
    │
    ├─ Technical Lead Review
    ├─ Security Officer Review
    └─ Product Owner Review
           │
           ▼
Promote to Production
    │
    ├─ Blue-Green Deployment
    ├─ Canary Release (10% → 50% → 100%)
    └─ CIVILIZATION LOCK (immutable tag)
           │
           ▼
Update Timeline (docs/CIVILIZATION_TIMELINE.md)
```

### No Bypass Mechanisms

- Cannot skip tests (except emergency override requiring 3 approvals)
- Cannot deploy unsigned images
- Cannot skip SBOM generation
- Cannot bypass canonical invariants
- Cannot promote to production without approval
- Cannot modify production directly

______________________________________________________________________

## VI. RELEASE STRATEGY

### Versioning Scheme

```
v{major}.{minor}.{patch}-{component}

Examples:
  v1.0.0-core      # Core application
  v1.0.0-eca       # External Cognition Amplifier
  v1.0.0-tk8s      # TK8S infrastructure
```

### Promotion Levels

1. **DEV**

   - Branch: `develop`
   - Auto-deploy on push
   - Fast iteration
   - Optional security scanning

1. **STAGING**

   - Branch: `main`
   - Auto-deploy on push
   - Full security scanning required
   - Regression testing environment
   - SBOM and signing required

1. **PRODUCTION**

   - Manual promotion only
   - Constitutional approval required
   - Blue-green deployment
   - Full audit trail
   - CIVILIZATION LOCK applied

1. **CIVILIZATION LOCK**

   - Immutable tag created
   - Git tag with signature
   - Timeline updated
   - SBOM archived
   - Cannot be modified or deleted

### Rollback Strategy

- Blue-green deployment enables instant rollback
- ArgoCD can revert to previous Git commit
- Rollback requires 1 approval (faster than deploy)
- Post-mortem required for all rollbacks

______________________________________________________________________

## VII. OBSERVABILITY

### Metrics Tracked

1. **Policy Enforcement:**

   - Policy rejection rate
   - Image signature validation failures
   - SBOM annotation missing count
   - Mutable container attempts

1. **Canonical Invariants:**

   - Invariant failure count
   - Replay scenario success rate
   - Ethical violation detections
   - Four Laws compliance rate

1. **Security:**

   - Falco runtime violations
   - Trivy CVE detections
   - OPA constraint violations
   - ECA isolation breach attempts

1. **Performance:**

   - Pod restart rate
   - Memory/CPU utilization
   - Request latency (p50, p95, p99)
   - Token spend rate

1. **Operational:**

   - Deployment frequency
   - Lead time for changes
   - Mean time to recovery
   - Change failure rate

### Alerting Rules

- **Critical:** Page on-call immediately

  - Image signature validation failure
  - Canonical invariant failure
  - ECA isolation breach
  - Falco critical runtime violation

- **High:** Alert in Slack/PagerDuty

  - Policy rejection rate > 1%
  - Security alert (high severity)
  - Pod restart rate > 0.1 per 15min

- **Medium:** Email notification

  - High memory/CPU usage
  - Token spend rate exceeds budget

- **Low:** Dashboard only

  - General metrics
  - Informational events

______________________________________________________________________

## VIII. DISASTER RECOVERY

### Backup Strategy

1. **etcd Snapshots:**

   - Automated every 6 hours
   - Retained for 30 days
   - Stored in separate region
   - Encrypted at rest

1. **Application Data:**

   - PostgreSQL continuous archiving
   - Point-in-time recovery capability
   - Retained for 90 days
   - Encrypted backups

1. **Configuration:**

   - Git is authoritative
   - ArgoCD can rebuild cluster from Git
   - No configuration outside Git

### Recovery Procedures

1. **Pod Failure:**

   - Kubernetes automatic restart
   - Health checks detect failures
   - Replacement pod scheduled automatically

1. **Node Failure:**

   - Pods rescheduled to healthy nodes
   - Tolerations allow graceful handling
   - Auto-scaling adds capacity if needed

1. **Namespace Failure:**

   - ArgoCD re-syncs from Git
   - Resources recreated automatically
   - State restored from backups

1. **Cluster Failure:**

   - New cluster provisioned
   - ArgoCD deployed first
   - All applications synced from Git
   - Data restored from backups
   - DNS updated to new cluster

1. **Region Failure:**

   - Multi-region deployment strategy
   - Traffic failed over to secondary region
   - Data replicated cross-region
   - RPO < 5 minutes, RTO < 30 minutes

______________________________________________________________________

## IX. COMPLIANCE & AUDIT

### Audit Trail

All actions logged:

- Git commits (who, what, when)
- ArgoCD sync operations
- Admission controller decisions
- Falco runtime events
- Prometheus metrics
- Loki logs
- Tempo traces

### Compliance Reports

Generated monthly:

- Policy compliance rate
- Security scan results
- Canonical invariant status
- SBOM coverage
- Signature verification rate
- Backup verification

### Access Control

- All human access via OIDC
- No direct cluster access
- All changes via Git + ArgoCD
- kubectl access logged and audited
- Emergency access requires approval

______________________________________________________________________

## X. CIVILIZATION-GRADE GUARANTEES

If all TK8S doctrines are followed, you have:

✅ **Sovereignty:** Full control over infrastructure ✅ **Security:** Multiple layers of defense ✅ **Traceability:** Complete audit trail ✅ **Reproducibility:** Infrastructure from code ✅ **Immutability:** No configuration drift ✅ **Observability:** Full visibility ✅ **Reliability:** Automated recovery ✅ **Compliance:** Policy enforcement ✅ **Scalability:** Cloud-native architecture ✅ **Maintainability:** Declarative configuration

______________________________________________________________________

## FINAL STATE

You now have:

- ✅ Thirsty's Kubernetes (hard doctrine)
- ✅ Isolation of external cognition
- ✅ Civilization CI/CD
- ✅ Signed release chain
- ✅ Immutable timeline tracking
- ✅ Deterministic promotion flow
- ✅ Zero-trust network architecture
- ✅ Comprehensive observability
- ✅ Constitutional governance

**Welcome to civilization-grade infrastructure.**

______________________________________________________________________

**Document Version:** 1.0.0 **Last Updated:** 2026-02-11 **Status:** Living Document **Maintained By:** TK8S Core Team **Review Frequency:** Quarterly **Next Review:** 2026-05-11
