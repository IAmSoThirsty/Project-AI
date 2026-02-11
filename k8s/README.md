# Kubernetes Deployment Guide

## Overview

This directory contains production-ready Kubernetes manifests and Helm charts for deploying Project-AI in a cloud-native environment.

## Architecture

- **Multi-environment support**: dev, staging, production
- **Zero-downtime deployments**: Rolling updates with readiness probes
- **Auto-scaling**: HPA based on CPU/memory metrics
- **High availability**: Pod anti-affinity, PodDisruptionBudgets
- **Security**: Network policies, RBAC, security contexts
- **Observability**: Prometheus metrics, distributed tracing

## Quick Start

### Using Kustomize

```bash
# Deploy to development
./k8s/deploy.sh dev deploy

# Deploy to staging
./k8s/deploy.sh staging deploy

# Deploy to production
./k8s/deploy.sh production deploy
```

### Using Helm

```bash
# Install Helm chart
./k8s/deploy.sh production helm

# Or manually
helm install project-ai ./helm/project-ai \
  --namespace project-ai \
  --create-namespace \
  --values helm/project-ai/values-production.yaml
```

## Directory Structure

```
k8s/
├── base/                    # Base Kubernetes resources
│   ├── namespace.yaml       # Namespace definition
│   ├── configmap.yaml       # Application configuration
│   ├── secret.yaml          # Secrets (use external secrets in production)
│   ├── deployment.yaml      # Main application deployment
│   ├── service.yaml         # Service definitions
│   ├── ingress.yaml         # Ingress configuration
│   ├── pvc.yaml            # Persistent volume claims
│   ├── rbac.yaml           # RBAC roles and bindings
│   ├── hpa.yaml            # Horizontal Pod Autoscaler
│   ├── pdb.yaml            # Pod Disruption Budget
│   ├── networkpolicy.yaml  # Network policies
│   ├── postgres.yaml       # PostgreSQL StatefulSet
│   ├── redis.yaml          # Redis StatefulSet
│   ├── monitoring.yaml     # Prometheus setup
│   └── kustomization.yaml  # Kustomize base config
├── overlays/               # Environment-specific overlays
│   ├── dev/               # Development environment
│   ├── staging/           # Staging environment
│   └── production/        # Production environment
└── deploy.sh              # Deployment script

helm/
└── project-ai/            # Helm chart
    ├── Chart.yaml         # Chart metadata
    ├── values.yaml        # Default values
    ├── templates/         # Kubernetes manifests
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   ├── ingress.yaml
    │   ├── configmap.yaml
    │   ├── secret.yaml
    │   ├── hpa.yaml
    │   ├── pvc.yaml
    │   └── _helpers.tpl
    └── values-*.yaml      # Environment-specific values
```

## Prerequisites

### Required Tools

- kubectl (v1.25+)
- kustomize (v4.5+) or helm (v3.10+)
- Access to a Kubernetes cluster (EKS, GKE, AKS, etc.)

### Install kubectl

```bash
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# macOS
brew install kubectl
```

### Install kustomize

```bash
curl -s "https://raw.githubusercontent.com/kubernetes-sigs/kustomize/master/hack/install_kustomize.sh" | bash
sudo mv kustomize /usr/local/bin/
```

### Install Helm

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

## Configuration

### Environment Variables

Configure secrets using External Secrets Operator or update the secret.yaml:

```yaml
# Required secrets
OPENAI_API_KEY: "<your-openai-key>"
HUGGINGFACE_API_KEY: "<your-huggingface-key>"
FERNET_KEY: "<your-fernet-key>"
JWT_SECRET_KEY: "<your-jwt-secret>"
DB_PASSWORD: "<your-db-password>"
```

### External Secrets (Recommended)

For production, use External Secrets Operator:

```bash
# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets \
  external-secrets/external-secrets \
  -n external-secrets-system \
  --create-namespace

# Configure Vault backend
kubectl apply -f - <<EOF
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: "http://vault.vault.svc.cluster.local:8200"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "project-ai"
EOF
```

### Ingress Configuration

Update ingress hosts in `k8s/base/ingress.yaml` or Helm values:

```yaml
ingress:
  hosts:
    - host: project-ai.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: project-ai-tls
      hosts:
        - project-ai.yourdomain.com
```

### TLS Certificates

Install cert-manager for automatic TLS:

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

## Deployment Strategies

### Blue-Green Deployment

```bash
# Deploy new version (green)
kubectl apply -k k8s/overlays/production

# Test green deployment
./k8s/deploy.sh production test

# Switch traffic (update ingress)
kubectl patch ingress project-ai -n project-ai \
  -p '{"spec":{"rules":[{"host":"project-ai.example.com","http":{"paths":[{"path":"/","pathType":"Prefix","backend":{"service":{"name":"project-ai-green","port":{"number":80}}}}]}}]}}'

# Remove old deployment (blue)
kubectl delete deployment project-ai-blue -n project-ai
```

### Canary Deployment

```bash
# Deploy canary with 10% traffic
kubectl apply -f - <<EOF
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: project-ai
  namespace: project-ai
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: project-ai
  service:
    port: 80
  analysis:
    interval: 1m
    threshold: 10
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
EOF
```

## Monitoring

### Prometheus Queries

Access Prometheus at `http://prometheus.project-ai.svc.cluster.local:9090`

Useful queries:
```promql
# Request rate
rate(http_requests_total[5m])

# Error rate
rate(http_requests_total{status=~"5.."}[5m])

# Memory usage
container_memory_usage_bytes{pod=~"project-ai.*"}

# CPU usage
rate(container_cpu_usage_seconds_total{pod=~"project-ai.*"}[5m])
```

### Grafana Dashboards

Access Grafana at `http://grafana.project-ai.svc.cluster.local:3000`

Import dashboards:
- Kubernetes Cluster Monitoring (ID: 315)
- Kubernetes Pods (ID: 6417)
- Prometheus Stats (ID: 2)

## Scaling

### Manual Scaling

```bash
# Scale replicas
kubectl scale deployment project-ai-app -n project-ai --replicas=5

# Scale database
kubectl scale statefulset postgres -n project-ai --replicas=3
```

### Auto-scaling

HPA is configured for CPU/memory-based autoscaling:

```bash
# View HPA status
kubectl get hpa -n project-ai

# Edit HPA
kubectl edit hpa project-ai -n project-ai
```

## Backup and Restore

### Backup Data

```bash
# Backup PostgreSQL
kubectl exec -n project-ai postgres-0 -- pg_dump -U projectai projectai > backup.sql

# Backup persistent data
kubectl cp project-ai/project-ai-app-0:/app/data ./data-backup
```

### Restore Data

```bash
# Restore PostgreSQL
kubectl exec -i -n project-ai postgres-0 -- psql -U projectai projectai < backup.sql

# Restore persistent data
kubectl cp ./data-backup project-ai/project-ai-app-0:/app/data
```

## Troubleshooting

### View Logs

```bash
# View application logs
kubectl logs -f -n project-ai -l app.kubernetes.io/name=project-ai

# View logs from all pods
kubectl logs -f -n project-ai --all-containers=true -l app.kubernetes.io/name=project-ai

# View previous logs (if pod crashed)
kubectl logs -p -n project-ai <pod-name>
```

### Debug Pod Issues

```bash
# Describe pod
kubectl describe pod -n project-ai <pod-name>

# Get events
kubectl get events -n project-ai --sort-by='.lastTimestamp'

# Execute commands in pod
kubectl exec -it -n project-ai <pod-name> -- /bin/sh

# Debug with ephemeral container
kubectl debug -it -n project-ai <pod-name> --image=busybox --target=project-ai
```

### Network Issues

```bash
# Test connectivity
kubectl run -it --rm debug --image=nicolaka/netshoot -n project-ai -- /bin/bash

# Inside debug pod
curl http://project-ai.project-ai.svc.cluster.local
nslookup postgres.project-ai.svc.cluster.local
ping redis.project-ai.svc.cluster.local
```

### Database Issues

```bash
# Connect to PostgreSQL
kubectl exec -it -n project-ai postgres-0 -- psql -U projectai

# Check Redis
kubectl exec -it -n project-ai redis-0 -- redis-cli ping
```

## Security Best Practices

1. **Use External Secrets Operator** for secrets management
2. **Enable Network Policies** to restrict pod-to-pod communication
3. **Use Security Contexts** to run containers as non-root
4. **Enable Pod Security Standards** in the namespace
5. **Regular security scanning** with tools like Trivy
6. **Rotate secrets regularly** (every 90 days)
7. **Use RBAC** to limit permissions
8. **Enable audit logging** in Kubernetes

## Performance Tuning

### Resource Optimization

```yaml
# Adjust resource requests/limits
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Database Optimization

```yaml
# PostgreSQL tuning
env:
- name: POSTGRES_MAX_CONNECTIONS
  value: "200"
- name: POSTGRES_SHARED_BUFFERS
  value: "256MB"
- name: POSTGRES_EFFECTIVE_CACHE_SIZE
  value: "1GB"
```

### Redis Optimization

```yaml
# Redis tuning
command:
- redis-server
- --maxmemory 512mb
- --maxmemory-policy allkeys-lru
- --save ""  # Disable RDB snapshots for performance
```

## Maintenance

### Update Application

```bash
# Update image tag
kubectl set image deployment/project-ai-app \
  project-ai=ghcr.io/iamsothirsty/project-ai:v1.1.0 \
  -n project-ai

# Watch rollout
kubectl rollout status deployment/project-ai-app -n project-ai
```

### Rollback

```bash
# Rollback to previous version
./k8s/deploy.sh production rollback

# Rollback to specific revision
kubectl rollout undo deployment/project-ai-app -n project-ai --to-revision=2
```

### Database Migration

```bash
# Run migrations
kubectl exec -n project-ai <pod-name> -- python -m alembic upgrade head
```

## Cloud Provider Specific

### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster \
  --name project-ai \
  --region us-west-2 \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 3 \
  --nodes-min 2 \
  --nodes-max 10 \
  --managed

# Use EBS CSI driver for persistent volumes
kubectl apply -k "github.com/kubernetes-sigs/aws-ebs-csi-driver/deploy/kubernetes/overlays/stable/?ref=master"
```

### GCP GKE

```bash
# Create GKE cluster
gcloud container clusters create project-ai \
  --region us-central1 \
  --num-nodes 3 \
  --machine-type n1-standard-2 \
  --enable-autoscaling \
  --min-nodes 2 \
  --max-nodes 10
```

### Azure AKS

```bash
# Create AKS cluster
az aks create \
  --resource-group project-ai \
  --name project-ai \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/IAmSoThirsty/Project-AI/issues
- Documentation: https://project-ai.example.com/docs
- Email: support@project-ai.example.com
