# RBAC Implementation Report

> **Current release boundary (2026-07-19):** This is a historical or
> implementation-reference artifact, not current production evidence or
> deployment approval. The v0.0.3 successor remains fail-closed until the
> [pre-deployment checklist](../../deployment/PRE_DEPLOYMENT_CHECKLIST.md) and
> [CAB evidence bundle](../cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md)
> pass. Commands here are examples; this document does not prove deployment.

## Overview

Implemented **Role-Based Access Control (RBAC)** for Project-AI. Each service now has a dedicated ServiceAccount with minimal permissions required to operate, following the principle of least privilege.

## Files Created

### 1. `helm/project-ai/templates/rbac.yaml` (NEW)
- **Purpose:** ServiceAccount, Role, and RoleBinding resource definitions
- **Content:**
  - 4 ServiceAccounts: api, portals, adapters, genesis
  - 4 Roles with minimal permissions per component
  - 4 RoleBindings linking ServiceAccounts to Roles
  - Conditional creation via `rbac.create` flag

## Files Modified

### 1. `helm/project-ai/templates/api.yaml` (MODIFIED)
- **Added:** `serviceAccountName` specification
- Conditional: Only when `rbac.create=true`

### 2. `helm/project-ai/templates/portals.yaml` (MODIFIED)
- **Added:** `serviceAccountName` specification for portal services

### 3. `helm/project-ai/templates/adapters.yaml` (MODIFIED)
- **Added:** `serviceAccountName` specification for adapter services

### 4. `helm/project-ai/templates/genesis.yaml` (MODIFIED)
- **Added:** `serviceAccountName` specification

### 5. `helm/project-ai/values.yaml` (MODIFIED)
- **Added:** `rbac` configuration section (development defaults)
- `rbac.create: false` (development uses default ServiceAccount)
- `rbac.api.watchPods: false`

### 6. `helm/values.prod.yaml` (MODIFIED)
- **Added:** `rbac` configuration section (production defaults)
- `rbac.create: true` (production creates dedicated ServiceAccounts)
- `rbac.api.watchPods: false`

## Architecture

### ServiceAccount Strategy

```
┌──────────────────────────────────────────────────────────┐
│ Pod (running with ServiceAccount)                         │
├──────────────────────────────────────────────────────────┤
│ • Kubelet mounts ServiceAccount token at /var/run/secrets │
│ • Client libraries use token for API calls               │
│ • API Server validates token against RBAC policies       │
└──────────────────┬──────────────────────────────────────┘
                   │ (authentication)
┌──────────────────▼──────────────────────────────────────┐
│ Role (defines allowed actions)                            │
├──────────────────────────────────────────────────────────┤
│ • get persistentvolumeclaims (for API service)           │
│ • get configmaps (for configuration)                     │
│ • (empty for portals, adapters, genesis)                │
└──────────────────┬──────────────────────────────────────┘
                   │ (authorization)
┌──────────────────▼──────────────────────────────────────┐
│ RoleBinding (connects ServiceAccount to Role)             │
├──────────────────────────────────────────────────────────┤
│ • Links ServiceAccount to Role in namespace              │
│ • Enables RBAC enforcement                               │
└──────────────────────────────────────────────────────────┘
```

### ServiceAccounts per Component

| Service | ServiceAccount | Permissions | Justification |
|---------|---|---|---|
| **API** | `{release}-api` | Read PVC, Read ConfigMap | Access audit data, read config |
| **Portals** (docs, proof) | `{release}-portals` | None (read-only UI) | No cluster API access needed |
| **Adapters** (swr, atlas, arbiter-rlp) | `{release}-adapters` | None (read-only) | No cluster API access needed |
| **Genesis** | `{release}-genesis` | None (read-only emitter) | No cluster API access needed |

## Roles & Permissions

### API Service Role

```yaml
rules:
  # Read audit data PVC
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    resourceNames: ["project-ai-audit-data-pvc", "project-ai-backup-pvc"]
    verbs: ["get"]

  # Read ConfigMap (for future config management)
  - apiGroups: [""]
    resources: ["configmaps"]
    resourceNames: ["project-ai-config"]
    verbs: ["get"]

  # Optional: Watch pods (for future service discovery)
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]  # (if rbac.api.watchPods=true)
```

**Least Privilege:**
- ✅ Only specific PVCs (by name)
- ✅ Only specific ConfigMaps (by name)
- ✅ Only read operations (get, watch)
- ✅ No create/update/delete permissions

### Portal & Adapter Roles

```yaml
rules: []  # Empty - no permissions needed
```

**Rationale:**
- Read-only services (static content, read-only APIs)
- No need to access cluster resources
- Portals: serve pre-built frontend, don't call Kubernetes API
- Adapters: read external services, don't call Kubernetes API
- Genesis: emit events locally, don't call Kubernetes API

## Deployment Modes

### Mode 1: Development (No RBAC)

```yaml
rbac:
  create: false  # Don't create ServiceAccounts/Roles
```

**Result:**
- Pods use default ServiceAccount
- No explicit Role/RoleBinding
- Easier for local testing
- Not suitable for production

**Deploy:**
```bash
helm install project-ai ./helm/project-ai \
  -f helm/project-ai/values.yaml
```

### Mode 2: Production (RBAC Enabled)

```yaml
rbac:
  create: true  # Create ServiceAccounts/Roles
  api:
    watchPods: false  # API doesn't need pod discovery
```

**Result:**
- Dedicated ServiceAccounts per component
- Least-privilege Roles
- RBAC enforcement enabled
- API can read PVCs, other services are restricted

**Deploy:**
```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml
```

## Security Properties

### ✅ Implemented

1. **Least Privilege:**
   - Each service gets only required permissions
   - Portals, adapters, genesis have zero permissions
   - API has read-only access to PVCs/ConfigMaps

2. **Namespace Isolation:**
   - Roles scoped to namespace
   - ServiceAccounts isolated by namespace
   - Cross-namespace access denied

3. **Token Security:**
   - ServiceAccount token mounted as file (not in env)
   - Token rotated on pod restart
   - Token revoked when ServiceAccount deleted

4. **Audit Trail:**
   - All API calls via ServiceAccount logged
   - RBAC denials logged (if audit enabled)
   - Can trace which service made which API call

### 🔶 Partially Implemented

- Pod Security Standards (enforced at pod level, not via RBAC)
- Network policies (separate from RBAC, planned for Task 5)
- Audit logging (requires kube-apiserver config)

## RBAC Matrix

```
Service         │ PVC.get │ CM.get │ Pod.get │ Pod.list │ Pod.watch
─────────────────┼─────────┼────────┼─────────┼──────────┼──────────
API              │   ✓     │   ✓    │    ✗    │    ✗     │    ✗
Portals          │   ✗     │   ✗    │    ✗    │    ✗     │    ✗
Adapters         │   ✗     │   ✗    │    ✗    │    ✗     │    ✗
Genesis          │   ✗     │   ✗    │    ✗    │    ✗     │    ✗
─────────────────┼─────────┼────────┼─────────┼──────────┼──────────

Legend:
  ✓ = Allowed
  ✗ = Denied
  • Pod.watch (optional, controlled by rbac.api.watchPods)
```

## Error Scenarios

### Scenario 1: Forbidden - Insufficient Permissions

**Error Message:**
```
Error from server (Forbidden): persistentvolumeclaims "wrong-pvc-name" is forbidden: User "system:serviceaccount:default:project-ai-api" cannot get resource "persistentvolumeclaims" in API group "" in the namespace "default"
```

**Cause:** Application trying to read PVC not in Role

**Resolution:**
```yaml
# Update Role to include the PVC name
rules:
  - apiGroups: [""]
    resources: ["persistentvolumeclaims"]
    resourceNames: ["project-ai-audit-data-pvc", "project-ai-backup-pvc", "new-pvc"]
    verbs: ["get"]
```

### Scenario 2: Pod Cannot Access API Server

**Error:**
```
dial tcp: lookup kubernetes.default.svc on ...: No such host
```

**Cause:** Usually DNS/network issue, not RBAC

**Debug:**
```bash
# Verify ServiceAccount mounted
kubectl exec <pod> -- ls -la /var/run/secrets/kubernetes.io/serviceaccount/

# Check token validity
kubectl exec <pod> -- cat /var/run/secrets/kubernetes.io/serviceaccount/token

# Try API call
kubectl exec <pod> -- curl -H "Authorization: Bearer $(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
  --cacert /var/run/secrets/kubernetes.io/serviceaccount/ca.crt \
  https://kubernetes.default.svc/api/v1/namespaces/default/pods
```

### Scenario 3: Service Discovery Failing (Future)

**If App Implements Pod Discovery:**

```yaml
# Enable pod watching for API
rbac:
  api:
    watchPods: true  # Allow pod discovery
```

**Updated Role:**
```yaml
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

## Verification Commands

### Pre-Deployment

```bash
# Verify RBAC template renders (production)
helm template test ./helm/project-ai \
  -f helm/values.prod.yaml | grep "kind: ServiceAccount"
# Expected: 4 ServiceAccounts

# Verify RBAC not created (development)
helm template test ./helm/project-ai \
  -f helm/project-ai/values.yaml | grep "kind: ServiceAccount"
# Expected: (empty - no ServiceAccounts)

# Verify Deployments reference ServiceAccount
helm template test ./helm/project-ai \
  -f helm/values.prod.yaml | grep "serviceAccountName"
# Expected: Multiple references
```

### Post-Deployment

```bash
# List ServiceAccounts
kubectl get serviceaccounts -n project-ai-prod

# List Roles
kubectl get roles -n project-ai-prod

# List RoleBindings
kubectl get rolebindings -n project-ai-prod

# Verify pod using correct ServiceAccount
kubectl get pod <pod-name> -n project-ai-prod \
  -o jsonpath='{.spec.serviceAccountName}'
# Expected: project-ai-prod-api (or appropriate SA)

# Check ServiceAccount token mounted
kubectl exec <pod-name> -n project-ai-prod -- \
  ls -la /var/run/secrets/kubernetes.io/serviceaccount/

# Test RBAC permissions (dry-run)
kubectl auth can-i get persistentvolumeclaims \
  --as=system:serviceaccount:project-ai-prod:project-ai-prod-api \
  -n project-ai-prod
# Expected: yes

# Test forbidden access (dry-run)
kubectl auth can-i create deployments \
  --as=system:serviceaccount:project-ai-prod:project-ai-prod-api \
  -n project-ai-prod
# Expected: no
```

## Production Checklist

Before deploying to production:

- [ ] Review RBAC matrix (this document)
- [ ] Verify `rbac.create: true` in values.prod.yaml
- [ ] Deploy with RBAC enabled
- [ ] List ServiceAccounts: `kubectl get sa -n <namespace>`
- [ ] List Roles: `kubectl get roles -n <namespace>`
- [ ] List RoleBindings: `kubectl get rolebindings -n <namespace>`
- [ ] Test RBAC permissions: `kubectl auth can-i ...`
- [ ] Verify pods have correct ServiceAccount
- [ ] Enable audit logging for RBAC decisions
- [ ] Monitor for RBAC denials in logs
- [ ] Document any custom Role modifications
- [ ] Train team on RBAC troubleshooting

## Future Enhancements

- [ ] ClusterRole for cross-namespace read access
- [ ] Service-to-service authentication (mTLS)
- [ ] Pod Security Standards enforcement
- [ ] Audit logging dashboard for RBAC events
- [ ] Automated RBAC policy generation
- [ ] Role aggregation for multi-service authorization

## References

- Kubernetes RBAC: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- ServiceAccounts: https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/
- Audit Logging: https://kubernetes.io/docs/tasks/debug-application-cluster/audit/
- Pod Security Standards: https://kubernetes.io/docs/concepts/security/pod-security-standards/
