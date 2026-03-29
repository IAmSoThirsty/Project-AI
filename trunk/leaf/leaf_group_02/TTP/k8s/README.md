<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# TTP Kubernetes Manifests

Production-grade Kubernetes deployment configurations for the TTP application.

## Architecture

The Kubernetes deployment includes:
- API deployment with HorizontalPodAutoscaler
- Web frontend deployment
- ConfigMaps for configuration
- Secrets for sensitive data
- Services (ClusterIP and LoadBalancer)
- Ingress with TLS
- NetworkPolicies for security
- PodDisruptionBudgets for availability
- ServiceAccounts with RBAC

## Prerequisites

- Kubernetes cluster (EKS, GKE, or self-hosted) v1.28+
- kubectl configured to access the cluster
- Helm 3+ (for optional components)
- cert-manager for TLS certificates (optional)
- Istio service mesh (optional)

## Directory Structure

```
k8s/
├── base/              # Base manifests for all environments
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml.example  # Template (DO NOT commit actual secrets!)
│   ├── api/           # API deployment
│   ├── web/           # Web frontend deployment
│   └── ingress.yaml
├── overlays/          # Kustomize overlays per environment
│   ├── dev/
│   ├── staging/
│   └── prod/
└── README.md
```

## Deployment

### Using kubectl

```bash
# Create namespace
kubectl apply -f base/namespace.yaml

# Create secrets (see Secrets Management section below)
# DO NOT use secrets.yaml in production - use kubectl create secret instead

# Deploy application (ConfigMaps and Deployments)
kubectl apply -f base/configmap.yaml
kubectl apply -f base/api/
kubectl apply -f base/web/
kubectl apply -f base/ingress.yaml
kubectl apply -f base/networkpolicy.yaml

# Check deployment status
kubectl get pods -n ttp-prod
kubectl get svc -n ttp-prod
kubectl get ingress -n ttp-prod
```

### Using Kustomize

```bash
# Deploy to production
kubectl apply -k overlays/prod/

# Deploy to staging
kubectl apply -k overlays/staging/

# Deploy to development
kubectl apply -k overlays/dev/
```

## Configuration

### Secrets Management

⚠️ **SECURITY WARNING**: Never commit actual secrets to version control!

The repository includes `secrets.yaml.example` as a template. Actual secrets should be created using one of these methods:

#### Option 1: Create Secrets from Command Line (Recommended for Production)

```bash
# Generate a secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Create the secret
kubectl create secret generic ttp-secrets \
  --from-literal=DATABASE_URL="postgresql://username:password@your-rds-endpoint.region.rds.amazonaws.com:5432/ttp" \
  --from-literal=REDIS_URL="redis://your-elasticache-endpoint.region.cache.amazonaws.com:6379/0" \
  --from-literal=SECRET_KEY="$SECRET_KEY" \
  --from-literal=AWS_ACCESS_KEY_ID="your-access-key" \
  --from-literal=AWS_SECRET_ACCESS_KEY="your-secret-key" \
  --from-literal=OTEL_EXPORTER_OTLP_ENDPOINT="http://otel-collector:4317" \
  -n ttp-prod
```

#### Option 2: Use Secrets from File (Local Development Only)

```bash
# Copy the example template
cp base/secrets.yaml.example base/secrets.yaml

# Edit the file and replace all placeholder values
# NOTE: base/secrets.yaml is in .gitignore and will NOT be committed
vim base/secrets.yaml

# Apply the secrets
kubectl apply -f base/secrets.yaml
```

#### Option 3: Use External Secrets Management (Recommended for Production)

For production environments, use external secret management:
- **AWS Secrets Manager** with [External Secrets Operator](https://external-secrets.io/)
- **HashiCorp Vault** for centralized secret management
- **Sealed Secrets** for encrypted secrets in Git

Example with AWS Secrets Manager:
```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name ttp-prod-database \
  --secret-string '{"url":"postgresql://..."}' \
  --region us-east-1

# Use External Secrets Operator to sync to Kubernetes
# See: https://external-secrets.io/
```

### ConfigMap

Update `base/configmap.yaml` with environment-specific configuration.

## Scaling

### Manual Scaling

```bash
# Scale API deployment
kubectl scale deployment/ttp-api --replicas=5 -n ttp-prod

# Scale web deployment
kubectl scale deployment/ttp-web --replicas=3 -n ttp-prod
```

### Auto-scaling (HPA)

HorizontalPodAutoscaler is configured for the API deployment:
- Min replicas: 2
- Max replicas: 10
- Target CPU: 70%
- Target Memory: 80%

## Monitoring

```bash
# Check pod status
kubectl get pods -n ttp-prod

# View logs
kubectl logs -f deployment/ttp-api -n ttp-prod
kubectl logs -f deployment/ttp-web -n ttp-prod

# Describe resources
kubectl describe deployment/ttp-api -n ttp-prod
kubectl describe hpa/ttp-api-hpa -n ttp-prod
```

## Troubleshooting

```bash
# Check pod events
kubectl describe pod <pod-name> -n ttp-prod

# Exec into pod
kubectl exec -it <pod-name> -n ttp-prod -- /bin/bash

# Port forward for local testing
kubectl port-forward svc/ttp-api 8000:8000 -n ttp-prod
kubectl port-forward svc/ttp-web 3000:3000 -n ttp-prod

# Check resource usage
kubectl top pods -n ttp-prod
kubectl top nodes
```

## Rollback

```bash
# View rollout history
kubectl rollout history deployment/ttp-api -n ttp-prod

# Rollback to previous version
kubectl rollout undo deployment/ttp-api -n ttp-prod

# Rollback to specific revision
kubectl rollout undo deployment/ttp-api --to-revision=2 -n ttp-prod
```

## Health Checks

Both API and web deployments have:
- Liveness probes (restart unhealthy pods)
- Readiness probes (remove from load balancing when not ready)
- Startup probes (allow time for slow starts)

## Security

- Pods run as non-root user
- Read-only root filesystem
- Security contexts defined
- NetworkPolicies restrict traffic
- RBAC for service accounts
- Secrets encrypted at rest

## High Availability

- Multiple replicas across nodes
- PodDisruptionBudgets prevent simultaneous downtime
- Anti-affinity rules distribute pods
- Rolling update strategy with zero downtime

## License

MIT License - See LICENSE file for details.
