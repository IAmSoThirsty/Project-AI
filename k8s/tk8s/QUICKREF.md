# TK8S Quick Reference

## One-Line Deployment

```bash
./install-prerequisites.sh && ./generate-cosign-keys.sh && ./deploy-tk8s.sh
```

## Commands

### Installation

```bash
./install-prerequisites.sh    # Install ArgoCD, Kyverno, tools
./generate-cosign-keys.sh     # Generate signing keys
./deploy-tk8s.sh              # Deploy TK8S infrastructure
./verify-deployment.sh        # Validate deployment
python validate_tk8s.py       # Detailed validation
```

### Options

```bash
./deploy-tk8s.sh --dry-run           # Preview changes
./deploy-tk8s.sh --skip-validation   # Skip validation
```

### Verification

```bash
kubectl get namespaces | grep project-ai
kubectl get pods -A | grep project-ai
kubectl get networkpolicies -A
kubectl get clusterpolicies
kubectl get applications -n argocd
```

### ArgoCD Access

```bash

# Get password

kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Port-forward

kubectl port-forward svc/argocd-server -n argocd 8080:443

# Access: https://localhost:8080

# Username: admin

```

### Troubleshooting

```bash

# Check logs

kubectl logs -n argocd deployment/argocd-server
kubectl logs -n kyverno deployment/kyverno

# Check status

kubectl get all -n project-ai-core
kubectl describe pod <pod-name> -n <namespace>

# Rollback

kubectl delete namespace project-ai-*
```

## File Structure

```
k8s/tk8s/
├── install-prerequisites.sh   # Prerequisites installer
├── generate-cosign-keys.sh    # Key generator
├── deploy-tk8s.sh             # Main deployer
├── verify-deployment.sh       # Validator
├── validate_tk8s.py           # Python validation
├── SCRIPTS_README.md          # Detailed docs
├── SETUP_GUIDE.md             # Manual guide
├── README.md                  # Overview
├── namespaces/                # Namespace manifests
├── deployments/               # Deployment manifests
├── network-policies/          # NetworkPolicy manifests
├── rbac/                      # RBAC manifests
├── security/                  # Kyverno policies
├── argocd/                    # ArgoCD apps
└── monitoring/                # Observability config
```

## Documentation

- **Scripts:** `SCRIPTS_README.md`
- **Setup:** `SETUP_GUIDE.md`
- **Doctrine:** `../../docs/TK8S_DOCTRINE.md`
- **Timeline:** `../../docs/CIVILIZATION_TIMELINE.md`
