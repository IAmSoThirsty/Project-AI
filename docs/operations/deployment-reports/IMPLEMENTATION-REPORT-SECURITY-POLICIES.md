# Security Policies Implementation Report

> **Current release boundary (2026-07-19):** This is a historical or
> implementation-reference artifact, not current production evidence or
> deployment approval. The v0.0.3 successor remains fail-closed until the
> [pre-deployment checklist](../../deployment/PRE_DEPLOYMENT_CHECKLIST.md) and
> [CAB evidence bundle](../cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md)
> pass. Commands here are examples; this document does not prove deployment.

## Overview

Implemented **Pod Security Standards (PSS)** for namespace-level security enforcement. Deprecated PodSecurityPolicy replaced with declarative PSS labels.

## Implementation

### Namespace Labels

Apply to production namespace:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: project-ai-prod
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Restricted Profile Enforcement

All Project-AI pods comply with `restricted` profile:

✅ **Container security:**
- Non-root user (UID 10001)
- Read-only root filesystem
- No privilege escalation
- All capabilities dropped
- seccomp: RuntimeDefault

✅ **Volume restrictions:**
- No hostPath volumes
- No emptyDir (except /tmp)
- Only PVC volumes allowed

✅ **Pod security:**
- runAsNonRoot: true
- seccompProfile required

## Deployment

**Apply PSS to namespace:**
```bash
kubectl label namespace project-ai-prod \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted
```

**Verify compliance:**
```bash
kubectl get pods -n project-ai-prod -o yaml | grep securityContext
```

## References

- Pod Security Standards: https://kubernetes.io/docs/concepts/security/pod-security-standards/
