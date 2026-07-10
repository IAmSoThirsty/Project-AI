# Quick Deploy: RBAC

## Development (No RBAC)

```bash
helm install project-ai ./helm/project-ai \
  -f helm/project-ai/values.yaml
```

Uses default ServiceAccount. Fine for testing.

---

## Production (RBAC Enabled)

```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  -n project-ai-prod \
  --create-namespace
```

Creates dedicated ServiceAccounts with minimal permissions.

---

## Verify RBAC

```bash
# List ServiceAccounts
kubectl get serviceaccounts -n project-ai-prod

# List Roles
kubectl get roles -n project-ai-prod

# List RoleBindings
kubectl get rolebindings -n project-ai-prod

# Check pod's ServiceAccount
kubectl get pod <pod-name> -n project-ai-prod \
  -o jsonpath='{.spec.serviceAccountName}'

# Test permission (should succeed)
kubectl auth can-i get persistentvolumeclaims \
  --as=system:serviceaccount:project-ai-prod:project-ai-prod-api \
  -n project-ai-prod

# Test forbidden (should fail)
kubectl auth can-i delete deployments \
  --as=system:serviceaccount:project-ai-prod:project-ai-prod-api \
  -n project-ai-prod
```

---

## RBAC Matrix

| Service | PVC Read | ConfigMap Read | Pod Watch |
|---------|----------|---|---|
| API | ✓ | ✓ | ✗ |
| Portals | ✗ | ✗ | ✗ |
| Adapters | ✗ | ✗ | ✗ |
| Genesis | ✗ | ✗ | ✗ |

---

## Enable Pod Watching (Optional)

If API needs to discover pods:

```bash
helm upgrade project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set rbac.api.watchPods=true \
  -n project-ai-prod
```

---

## Troubleshoot

### Permission Denied Error

```bash
# Check if role grants permission
kubectl get role <role-name> -n project-ai-prod -o yaml

# Add permission if needed (edit role)
kubectl edit role <role-name> -n project-ai-prod
```

### Service Account Not Mounted

```bash
# Verify pod has serviceAccountName
kubectl get pod <pod-name> -n project-ai-prod \
  -o jsonpath='{.spec.serviceAccountName}'

# Verify token file exists in pod
kubectl exec <pod-name> -n project-ai-prod -- \
  ls /var/run/secrets/kubernetes.io/serviceaccount/
```

### RBAC Disabled Globally

```bash
# Check API server started with RBAC
kubectl get nodes -o jsonpath='{.items[0].metadata.annotations.kubeadm\.alpha\.kubernetes\.io/cri-socket}'

# Verify authorization-mode includes RBAC
kubectl get pod kube-apiserver-<node> -n kube-system -o yaml | grep authorization
```

---

## Disable RBAC (Not Recommended)

```bash
helm upgrade project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set rbac.create=false \
  -n project-ai-prod
```

Falls back to default ServiceAccount.

---

## Monitor RBAC Denials

```bash
# Check logs for RBAC errors
kubectl logs <pod-name> -n project-ai-prod -c <container>

# Look for "Forbidden" messages
kubectl logs -n project-ai-prod --all-containers=true -l app.kubernetes.io/component=api | grep -i forbidden
```
