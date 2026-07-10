# Quick Deploy: Kubernetes Secret Integration

## 3 Ways to Deploy with Secrets

### Method 1: Simple (Development/Testing)

```bash
# Get token (example sources)
export API_TOKEN="my-secret-token-here"

# Deploy
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set-string secrets.api.token="${API_TOKEN}" \
  -n project-ai-prod --create-namespace

# Verify
kubectl get secret -n project-ai-prod
kubectl get pods -n project-ai-prod
```

### Method 2: Secure (Recommended for Production)

**Step 1: Create Secret**
```bash
export API_TOKEN="my-secret-token-here"

kubectl create secret generic project-ai-api-secrets \
  --from-literal=PROJECT_AI_API_TOKEN="${API_TOKEN}" \
  -n project-ai-prod --dry-run=client -o yaml | kubectl apply -f -
```

**Step 2: Deploy Helm**
```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set secrets.create=false \
  -n project-ai-prod --create-namespace
```

### Method 3: Enterprise (Vault/AWS Secrets Manager)

**Install External Secrets:**
```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  -n external-secrets-system --create-namespace
```

**Create Secret from Vault (example):**
```bash
cat <<EOF | kubectl apply -f -
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
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: project-ai-api-secrets-sync
  namespace: project-ai-prod
spec:
  refreshInterval: 1h
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
EOF
```

**Deploy Helm:**
```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set secrets.create=false \
  -n project-ai-prod --create-namespace
```

## Verify Deployment

```bash
# Check Secret exists
kubectl get secret project-ai-api-secrets -n project-ai-prod

# Check API pod is running
kubectl get pods -n project-ai-prod

# Verify token was injected (exec into pod)
kubectl exec -n project-ai-prod $(kubectl get pods -n project-ai-prod -l app.kubernetes.io/component=api -o jsonpath='{.items[0].metadata.name}') -- env | grep PROJECT_AI_API_TOKEN

# Check app health
kubectl port-forward -n project-ai-prod svc/project-ai-api 8000:8000 &
curl http://localhost:8000/health/live && echo "OK"
kill %1
```

## Update Token

```bash
# Method 1: Helm CLI
helm upgrade project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set-string secrets.api.token="new-token-here" \
  -n project-ai-prod

# Method 2: Direct Secret update
kubectl patch secret project-ai-api-secrets -n project-ai-prod \
  -p "{\"data\":{\"PROJECT_AI_API_TOKEN\":\"$(echo -n 'new-token-here' | base64)\"} }"

# Monitor pod restart
kubectl rollout status deployment/project-ai-api -n project-ai-prod
```

## Rollback

```bash
# List release history
helm history project-ai -n project-ai-prod

# Rollback to previous version
helm rollback project-ai -n project-ai-prod

# Or rollback to specific revision
helm rollback project-ai 1 -n project-ai-prod
```

## Troubleshoot

```bash
# Pod not starting?
kubectl describe pod -n project-ai-prod $(kubectl get pods -n project-ai-prod -l app.kubernetes.io/component=api -o jsonpath='{.items[0].metadata.name}')

# Secret missing?
kubectl get secret project-ai-api-secrets -n project-ai-prod

# Create missing Secret
kubectl create secret generic project-ai-api-secrets \
  --from-literal=PROJECT_AI_API_TOKEN="token" \
  -n project-ai-prod --dry-run=client -o yaml | kubectl apply -f -

# Check pod logs
kubectl logs -n project-ai-prod -l app.kubernetes.io/component=api -c api
```
