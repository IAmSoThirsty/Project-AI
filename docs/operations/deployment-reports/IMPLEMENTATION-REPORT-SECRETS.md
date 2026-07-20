# Kubernetes Secret Integration - Implementation Report

> **Current release boundary (2026-07-19):** This is a historical or
> implementation-reference artifact, not current production evidence or
> deployment approval. The v0.0.3 successor remains fail-closed until the
> [pre-deployment checklist](../../deployment/PRE_DEPLOYMENT_CHECKLIST.md) and
> [CAB evidence bundle](../cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md)
> pass. Commands here are examples; this document does not prove deployment.

## Overview

Implemented **production-grade Kubernetes Secret integration** for Project-AI. Sensitive credentials (API tokens, authentication strings) are now injected via Kubernetes Secrets rather than stored in plain text in Helm values or environment variables.

## Files Created

### 1. `helm/project-ai/templates/secrets.yaml` (NEW)
- **Purpose:** Kubernetes Secret resource definitions
- **Content:**
  - Creates API authentication secrets during Helm deployment
  - Conditional creation (controlled by `secrets.create` flag)
  - Supports external secret management (when `secrets.create=false`)
  - Labeled for tracking (component labels)

## Files Modified

### 1. `helm/project-ai/templates/api.yaml` (MODIFIED)
- **Changed:** Environment variable injection method
- **From:** `value: {{ .Values.api.env.PROJECT_AI_API_TOKEN }}`
- **To:** `valueFrom.secretKeyRef` (references Secret)
- **Benefit:** Token never appears in pod/deployment YAML
- **Fallback:** Optional reference (works with pre-existing Secrets)

### 2. `helm/project-ai/values.yaml` (MODIFIED)
- **Added:** `secrets` section (development defaults)
- `secrets.create: false` (development uses plain env vars)
- `secrets.api.token: ""` (placeholder, not used in dev)

### 3. `helm/values.prod.yaml` (MODIFIED)
- **Added:** `secrets` section (production defaults)
- `secrets.create: true` (create Secrets via Helm)
- `secrets.api.token: ""` (MUST be overridden at deploy time)
- **Warning:** Tokens must be provided via CLI or external tools

### 4. `helm/project-ai/templates/_helpers.tpl` (MODIFIED)
- **Added:** `project-ai.secretName` template helper
- Purpose: Consistent Secret naming across templates
- Usage: `include "project-ai.secretName" (dict "root" . "component" "api")`

## Architecture

### Three-Layer Secret Management

```
Layer 1: Secret Sources
├── Via Helm CLI: --set-string secrets.api.token="..."
├── Via External Tools: sops, sealed-secrets, vault-inject
└── Via Pre-created Secrets: --set secrets.create=false

Layer 2: Kubernetes Secret Resource (secrets.yaml)
├── Creates opaque Secret during helm install/upgrade
├── Stores base64-encoded values
└── Versioned with Helm release

Layer 3: Pod Environment Injection (api.yaml)
├── Pod reads from Secret via valueFrom.secretKeyRef
├── Application receives via env var
└── Secret value never appears in Pod spec
```

### Secret Lifecycle

```
1. User deploys with secret value: helm install ... --set-string secrets.api.token="abc123"
2. Helm templates secrets.yaml with token
3. kubectl applies Secret to cluster
4. API Deployment references Secret
5. Kubelet injects secret value into container
6. Application reads from environment
7. Secret stored in etcd (encrypted at rest with --encryption-provider-config)
```

## Security Considerations

### 1. Secret Storage

**Kubernetes etcd:**
- Secrets stored base64-encoded (NOT encrypted by default)
- **Mitigation:** Enable etcd encryption
  ```bash
  kube-apiserver --encryption-provider-config=/etc/kubernetes/pki/encryption.yaml
  ```

**Best Practice Alternatives:**
- HashiCorp Vault: `helm install ... --set secrets.create=false`
  - Vault Agent injects secrets at pod startup
  - Secrets never stored in etcd
  - Centralized rotation and audit

- AWS Secrets Manager: Use with IRSA (IAM Roles for Service Accounts)
  - External Secrets Operator reads from AWS
  - Pods authenticate via IRSA

- Sealed Secrets: Encrypt secrets in git
  - `kubeseal` encrypts values
  - Only cluster can decrypt
  - Safe to commit encrypted values to git

### 2. Secret Injection Methods

**Current Implementation (secretKeyRef):**
```yaml
env:
  - name: PROJECT_AI_API_TOKEN
    valueFrom:
      secretKeyRef:
        name: project-ai-api-secrets
        key: PROJECT_AI_API_TOKEN
        optional: false  # Pod won't start if Secret missing
```

**Advantages:**
- Simple, native Kubernetes
- No external tooling required
- Works with any Secret provider

**Disadvantages:**
- Secrets in etcd (unencrypted by default)
- No automatic rotation
- Manual lifecycle management

### 3. Secret Exposure Prevention

**✓ Implemented:**
- Secrets NOT passed as command-line args (avoid process listing)
- Secrets NOT stored in Helm values files (avoid git exposure)
- Secrets NOT baked into container images
- Secrets injected at runtime only
- Read-only root filesystem (container can't write secrets to disk)

**✗ Not Yet Implemented (Future):**
- etcd encryption at rest
- Automatic Secret rotation
- Secret audit logging
- Pod security policies (PSP → Pod Security Standards)
- Network policies (restrict Secret access)

### 4. Audit Trail

**What's Auditable:**
```
kubectl describe secret project-ai-api-secrets
  Shows: creation time, last update, labels, resource version

kubectl get events -A | grep Secret
  Shows: Secret creation/update events

audit.log entries
  Shows: Secret access via API (if audit enabled)
```

**Gap:** Secret VALUE is not logged (by design, sensitive data)

## Configuration Options

### Option 1: Helm-Managed Secrets (Recommended for Simple Deployments)

**Deploy Command:**
```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set-string secrets.api.token="your-token-here" \
  --namespace project-ai-prod \
  --create-namespace
```

**Advantages:**
- Simple CLI deployment
- No external tools
- Single source of truth (Helm release)

**Disadvantages:**
- Requires passing token in CLI args (history exposure risk)
- Token readable in helm history
- Manual secret updates

**Mitigation:**
```bash
# Better: Use environment variable
export API_TOKEN=$(vault read -field=token secret/project-ai/api)
helm install project-ai ... --set-string secrets.api.token="${API_TOKEN}"
```

### Option 2: Pre-Created Secrets (Recommended for Long-Running Clusters)

**Pre-Create Secret:**
```bash
kubectl create secret generic project-ai-api-secrets \
  --from-literal=PROJECT_AI_API_TOKEN="your-token-here" \
  -n project-ai-prod
```

**Deploy Command:**
```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set secrets.create=false \
  --namespace project-ai-prod
```

**Advantages:**
- Secrets never passed to helm command
- Supports pre-created Secret from any source
- Token history not exposed in helm

**Disadvantages:**
- Requires manual Secret creation step
- Secret lifecycle separate from Helm

### Option 3: External Secrets Operator (Most Secure)

**Install External Secrets Operator:**
```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  -n external-secrets-system --create-namespace
```

**Create SecretStore (vault example):**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: project-ai-prod
spec:
  provider:
    vault:
      server: "https://vault.example.com"
      path: "secret"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "project-ai"
```

**Create ExternalSecret:**
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: project-ai-api-secrets
  namespace: project-ai-prod
spec:
  refreshInterval: 15m
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: project-ai-api-secrets
    creationPolicy: Owner
  data:
    - secretKey: PROJECT_AI_API_TOKEN
      remoteRef:
        key: project-ai/api
        property: token
```

**Deploy with Helm:**
```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set secrets.create=false \
  --namespace project-ai-prod
```

**Advantages:**
- Secrets never stored in cluster etcd
- Automatic refresh every 15m
- Centralized secret management
- Full audit trail in Vault
- No manual CLI exposure

**Disadvantages:**
- Requires external system (Vault)
- Additional operator to manage
- Network dependency on Vault

## Deployment Guide

### Step 1: Determine Secret Source

Choose one of three options:
- **Simple:** Helm CLI (for development/testing)
- **Secure:** Pre-created Secret (for production with manual management)
- **Enterprise:** External Secrets Operator (for production with Vault/Secrets Manager)

### Step 2: Obtain API Token

From your organization's secret management system:
```bash
# Example: Vault
export API_TOKEN=$(vault kv get -field=token secret/project-ai/api)

# Example: AWS Secrets Manager
export API_TOKEN=$(aws secretsmanager get-secret-value --secret-id project-ai/api --query SecretString --output text | jq -r .token)

# Example: Local file (development only)
export API_TOKEN=$(cat .secrets/api-token.txt)
```

### Step 3: Deploy

**Option A: Helm CLI (Simple)**
```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set-string secrets.api.token="${API_TOKEN}" \
  --namespace project-ai-prod \
  --create-namespace
```

**Option B: Pre-Created Secret (Recommended)**
```bash
# Step 1: Create Secret
kubectl create secret generic project-ai-api-secrets \
  --from-literal=PROJECT_AI_API_TOKEN="${API_TOKEN}" \
  -n project-ai-prod

# Step 2: Deploy Helm without creating Secret
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set secrets.create=false \
  --namespace project-ai-prod \
  --create-namespace
```

**Option C: External Secrets (Enterprise)**
```bash
# Step 1: Create SecretStore (Vault credentials)
kubectl apply -f helm/secretstore-vault.yaml -n project-ai-prod

# Step 2: Create ExternalSecret (references Vault)
kubectl apply -f helm/externalsecret.yaml -n project-ai-prod

# Step 3: Deploy Helm without creating Secret
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set secrets.create=false \
  --namespace project-ai-prod \
  --create-namespace

# Step 4: Wait for Secret to be created by operator
kubectl wait --for=condition=SecretSynced externalsecret/project-ai-api-secrets \
  -n project-ai-prod --timeout=60s
```

### Step 4: Verify Deployment

```bash
# Check if API pod is running
kubectl get pods -n project-ai-prod -l app.kubernetes.io/component=api

# Verify Secret exists
kubectl get secret project-ai-api-secrets -n project-ai-prod

# Verify API pod has correct environment
kubectl exec -n project-ai-prod <pod-name> -- env | grep PROJECT_AI_API_TOKEN

# Check pod logs for startup errors
kubectl logs -n project-ai-prod <pod-name> -c api

# Verify application received token (health check)
kubectl port-forward -n project-ai-prod svc/project-ai-api 8000:8000
curl http://localhost:8000/health/live
```

## Secret Rotation

### Manual Rotation (Helm CLI)

**Generate new token:**
```bash
export NEW_TOKEN=$(openssl rand -hex 32)
```

**Update Secret in cluster:**
```bash
helm upgrade project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set-string secrets.api.token="${NEW_TOKEN}" \
  --namespace project-ai-prod
```

**Pods will be recreated with new Secret:**
```bash
# Monitor rollout
kubectl rollout status deployment/project-ai-api -n project-ai-prod
```

### Automatic Rotation (External Secrets)

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: project-ai-api-secrets
spec:
  refreshInterval: 1h  # Check Vault every hour
  # ... rest of config
```

External Secrets will automatically sync new tokens from Vault, triggering pod restart if value changed.

## Rollback Strategy

### Rollback to Previous Secret Version

**Via Helm:**
```bash
# List previous releases
helm history project-ai -n project-ai-prod

# Rollback to previous version
helm rollback project-ai 1 -n project-ai-prod
```

**What happens:**
- Previous Secret values restored
- Pods restarted with old Secret
- Application uses old token

**Verification:**
```bash
kubectl get secret project-ai-api-secrets -n project-ai-prod -o yaml
# Check timestamp, verify old token present (if not secret, can't verify value)
```

### Emergency Rollback (Bypass Secret)

**If Secret system fails:**
```bash
# Set token via plain env var (temporary, non-production)
helm upgrade project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set secrets.create=false \
  --set api.env.PROJECT_AI_API_TOKEN="fallback-token" \
  --namespace project-ai-prod
```

**Note:** This uses plain environment variable (less secure), only for emergency recovery.

## Validation Commands

### 1. Verify Secret Template Renders

```bash
helm template project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set-string secrets.api.token="test-token-xyz" \
  -n project-ai-prod | grep -A 20 "kind: Secret"
```

**Expected Output:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: project-ai-api-secrets
  namespace: project-ai-prod
  labels:
    ...
type: Opaque
stringData:
  PROJECT_AI_API_TOKEN: test-token-xyz
```

### 2. Verify Deployment References Secret

```bash
helm template project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  -n project-ai-prod | grep -A 5 "valueFrom"
```

**Expected Output:**
```yaml
env:
  - name: PROJECT_AI_API_TOKEN
    valueFrom:
      secretKeyRef:
        name: project-ai-api-secrets
        key: PROJECT_AI_API_TOKEN
        optional: false
```

### 3. Verify Helm Linting

```bash
helm lint helm/project-ai --strict
```

**Expected:** No errors

### 4. Test Secret Injection (Development)

```bash
# Dry-run deployment with test values
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set-string secrets.api.token="test-token" \
  --dry-run \
  --debug \
  -n project-ai-prod | grep -A 5 "SECRET"
```

## Production Checklist

- [ ] Choose Secret management strategy (Helm CLI, Pre-created, or External Secrets)
- [ ] Obtain API token from secure source (Vault, AWS Secrets Manager, etc.)
- [ ] If using Helm CLI: Store token securely, don't expose in shell history
  - [ ] Use `export TOKEN=$(...)` pattern instead of CLI arg
  - [ ] Or use `.envrc` with `direnv` for automatic env loading
- [ ] If using Pre-created Secret: Create Secret via kubectl before Helm deployment
- [ ] If using External Secrets: Deploy operator, create SecretStore, create ExternalSecret
- [ ] Deploy: `helm install project-ai ... --set-string secrets.api.token="${TOKEN}"`
- [ ] Verify: Pod running, Secret exists, application receives token
- [ ] Document Secret rotation procedure for your organization
- [ ] Test rollback: Deploy new token, verify pods restart, rollback to old token
- [ ] Set up audit logging for Secret access
- [ ] Enable etcd encryption at rest (kube-apiserver --encryption-provider-config)

## Monitoring & Alerting

### Alerts to Configure

1. **Secret update failures:**
   ```
   Alert: SecretUpdateFailed
   Condition: helm upgrade returns error
   Action: Page oncall, investigate token issues
   ```

2. **Secret sync failures (External Secrets):**
   ```
   Alert: ExternalSecretSyncFailed
   Condition: ExternalSecret.status.conditions.Ready=false
   Action: Check Vault connectivity, IRSA permissions
   ```

3. **Pod startup failures due to missing Secret:**
   ```
   Alert: PodFailedSecretMissing
   Condition: Pod pending > 5min with "SecretNotFound" event
   Action: Check Secret exists, verify deployment references correct Secret name
   ```

## Future Enhancements

- [ ] Multi-service Secret support (swr, atlas, arbiter-rlp, genesis)
- [ ] Database credentials (when persistence layer added)
- [ ] TLS certificates (when ingress added)
- [ ] API key rotation automation
- [ ] Secret audit logging dashboard
- [ ] Secret versioning (track token changes over time)

## References

- Kubernetes Secrets: https://kubernetes.io/docs/concepts/configuration/secret/
- External Secrets Operator: https://external-secrets.io/
- HashiCorp Vault: https://www.vaultproject.io/
- Sealed Secrets: https://github.com/bitnami-labs/sealed-secrets
- etcd Encryption: https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/
