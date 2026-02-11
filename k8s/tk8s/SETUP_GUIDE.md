# TK8S Quick Setup Guide

This guide will help you deploy TK8S (Thirsty's Kubernetes) to your cluster.

## Prerequisites

### Required Tools
- `kubectl` v1.29+ configured and authenticated
- `helm` v3.x (for ArgoCD installation)
- `cosign` (for image signing)
- `syft` (for SBOM generation)
- Docker or Podman (for building images)

### Required Access
- Kubernetes cluster admin access
- GitHub Container Registry write access
- GitHub repository write access

## Step-by-Step Deployment

### 1. Install ArgoCD

```bash
# Create ArgoCD namespace
kubectl create namespace argocd

# Install ArgoCD
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ArgoCD to be ready
kubectl wait --for=condition=available --timeout=300s deployment/argocd-server -n argocd

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### 2. Install Kyverno

```bash
# Add Kyverno Helm repo
helm repo add kyverno https://kyverno.github.io/kyverno/
helm repo update

# Install Kyverno
helm install kyverno kyverno/kyverno -n kyverno --create-namespace

# Wait for Kyverno to be ready
kubectl wait --for=condition=available --timeout=300s deployment/kyverno -n kyverno
```

### 3. Generate Cosign Key Pair

```bash
# Generate signing key pair
cosign generate-key-pair

# This creates:
# - cosign.key (private key - KEEP SECRET)
# - cosign.pub (public key - embed in Kyverno policy)

# Store private key in GitHub Secrets
# Name: COSIGN_PRIVATE_KEY
# Value: Contents of cosign.key

# Store password in GitHub Secrets
# Name: COSIGN_PASSWORD
# Value: Password you set during generation
```

### 4. Update Kyverno Policy with Public Key

Edit `k8s/tk8s/security/kyverno-policies.yaml` and replace the placeholder public key:

```yaml
# Find this section:
attestors:
- count: 1
  entries:
  - keys:
      publicKeys: |-
        -----BEGIN PUBLIC KEY-----
        # TODO: Replace with actual Cosign public key
        -----END PUBLIC KEY-----
```

Replace with your actual public key from `cosign.pub`.

### 5. Deploy TK8S Namespaces

```bash
cd k8s/tk8s

# Apply namespaces first
kubectl apply -f namespaces/tk8s-namespaces.yaml

# Verify namespaces
kubectl get namespaces | grep project-ai
```

### 6. Deploy RBAC

```bash
# Apply RBAC policies
kubectl apply -f rbac/tk8s-rbac.yaml

# Verify service accounts
kubectl get serviceaccounts -n project-ai-core
kubectl get serviceaccounts -n project-ai-eca
```

### 7. Deploy Network Policies

```bash
# Apply network policies
kubectl apply -f network-policies/tk8s-network-policies.yaml

# Verify policies
kubectl get networkpolicies -A | grep project-ai
```

### 8. Deploy Kyverno Policies

```bash
# Apply Kyverno cluster policies
kubectl apply -f security/kyverno-policies.yaml

# Verify policies
kubectl get clusterpolicies
```

### 9. Deploy ArgoCD Applications

```bash
# Apply ArgoCD applications
kubectl apply -f argocd/applications.yaml

# Verify applications
kubectl get applications -n argocd
```

### 10. Configure GitHub Secrets

Add these secrets to your GitHub repository:

```bash
# Repository Settings > Secrets and variables > Actions

COSIGN_PRIVATE_KEY    # Contents of cosign.key
COSIGN_PASSWORD       # Password for cosign.key
GITHUB_TOKEN          # Automatically provided by GitHub
```

### 11. Build and Push Initial Images

```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u $GITHUB_USERNAME --password-stdin

# Build core image
docker build -t ghcr.io/iamsothirsty/project-ai-core:v1.0.0 .

# Build ECA image
docker build -f Dockerfile.eca -t ghcr.io/iamsothirsty/project-ai-eca:v1.0.0 .

# Generate SBOMs
syft ghcr.io/iamsothirsty/project-ai-core:v1.0.0 -o spdx-json > sbom-core.json
syft ghcr.io/iamsothirsty/project-ai-eca:v1.0.0 -o spdx-json > sbom-eca.json

# Sign images
cosign sign --key cosign.key ghcr.io/iamsothirsty/project-ai-core:v1.0.0
cosign sign --key cosign.key ghcr.io/iamsothirsty/project-ai-eca:v1.0.0

# Push images
docker push ghcr.io/iamsothirsty/project-ai-core:v1.0.0
docker push ghcr.io/iamsothirsty/project-ai-eca:v1.0.0
```

### 12. Deploy Applications

```bash
# Sync ArgoCD applications
argocd app sync project-ai-core
argocd app sync project-ai-eca

# Or wait for auto-sync (default: 3 minutes)
```

### 13. Verify Deployment

```bash
# Check all pods
kubectl get pods -A | grep project-ai

# Check core pods
kubectl get pods -n project-ai-core

# Check ECA pods
kubectl get pods -n project-ai-eca

# Check pod security
kubectl get pod <pod-name> -n project-ai-core -o jsonpath='{.spec.securityContext}'

# Check network policies are enforced
kubectl get networkpolicies -A
```

### 14. Deploy Monitoring (Optional)

```bash
# Apply monitoring configuration
kubectl apply -f monitoring/prometheus-config.yaml

# Install Prometheus stack with Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack -n project-ai-monitoring

# Install Loki
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack -n project-ai-monitoring

# Install Tempo
helm install tempo grafana/tempo -n project-ai-monitoring
```

## Verification Checklist

- [ ] All namespaces created
- [ ] All service accounts created
- [ ] Network policies applied
- [ ] RBAC policies applied
- [ ] Kyverno policies applied and enforcing
- [ ] ArgoCD applications synced
- [ ] Core pods running (3 replicas)
- [ ] ECA pods running (2 replicas)
- [ ] All pods passing health checks
- [ ] Network policies blocking unauthorized traffic
- [ ] Image signatures verified
- [ ] SBOM annotations present
- [ ] Monitoring stack deployed (if enabled)
- [ ] CI/CD pipeline triggered successfully

## Troubleshooting

### Issue: Kyverno blocking deployments

**Symptom:** Pods fail to create with admission error

**Solution:**
```bash
# Check policy violations
kubectl get events -n project-ai-core | grep kyverno

# Temporarily disable policy (TESTING ONLY)
kubectl annotate clusterpolicy <policy-name> policies.kyverno.io/scored=false

# Fix the issue and re-enable
kubectl annotate clusterpolicy <policy-name> policies.kyverno.io/scored=true
```

### Issue: Network policy blocking traffic

**Symptom:** Pods cannot communicate

**Solution:**
```bash
# Check network policies
kubectl get networkpolicies -n <namespace>

# Describe to see rules
kubectl describe networkpolicy <name> -n <namespace>

# Check pod labels match selectors
kubectl get pod <pod-name> -n <namespace> --show-labels
```

### Issue: ArgoCD sync failing

**Symptom:** ArgoCD shows "OutOfSync" status

**Solution:**
```bash
# Check application status
kubectl get application project-ai-core -n argocd -o yaml

# View sync status
argocd app get project-ai-core

# Force sync
argocd app sync project-ai-core --force

# Check for resource errors
kubectl describe application project-ai-core -n argocd
```

## Next Steps

1. **Configure Secrets:** Replace placeholder secrets with actual values using SealedSecrets or Vault
2. **Enable Monitoring:** Deploy the full observability stack
3. **Configure Alerting:** Set up PagerDuty, Slack, or email alerts
4. **Run CI/CD Pipeline:** Trigger the civilization pipeline
5. **Production Deployment:** Follow the promotion workflow in TK8S_DOCTRINE.md

## Support

- Documentation: `docs/TK8S_DOCTRINE.md`
- Timeline: `docs/CIVILIZATION_TIMELINE.md`
- Issues: https://github.com/IAmSoThirsty/Project-AI/issues

## Security Considerations

⚠️ **IMPORTANT:**
- Never commit `cosign.key` to Git
- Store all secrets in GitHub Secrets or Vault
- Review network policies before production
- Test rollback procedures
- Keep SBOM records for compliance
- Rotate signing keys periodically
- Monitor Kyverno policy violations
- Review audit logs regularly

---

**Status:** Ready for Deployment  
**Version:** 1.0.0  
**Last Updated:** 2026-02-11
