# Deployment Guide - Sovereign Governance Substrate

## Purpose

Complete deployment procedures for the Sovereign Governance Substrate platform across all environments (development, staging, production). This guide covers Docker Compose, Kubernetes, and manual deployment methods.

## Prerequisites

### Required Tools

- Docker Engine 20.10+
- Docker Compose 2.x
- kubectl 1.24+
- kustomize 4.5+
- Helm 3.x (optional)
- Python 3.11+
- git
- jq

### Required Access

- Kubernetes cluster access (for K8s deployments)
- Container registry credentials
- Environment-specific secrets (FERNET_KEY, SECRET_KEY, JWT_SECRET)
- Database credentials
- API keys (OpenAI, DeepSeek, HuggingFace)

### Pre-Deployment Checklist

- [ ] All secrets are configured in environment files
- [ ] Database is provisioned and accessible
- [ ] Container images are built and pushed to registry
- [ ] DNS records are configured
- [ ] SSL certificates are provisioned
- [ ] Monitoring stack is ready (Prometheus, Grafana)
- [ ] Backup strategy is in place

---

## Deployment Methods

### Method 1: Docker Compose (Development/Local)

#### Quick Start

```bash

# 1. Clone repository

git clone <repository-url>
cd Sovereign-Governance-Substrate

# 2. Configure environment

cp .env.example .env

# Edit .env with your values

# 3. Build and start services

docker-compose up -d

# 4. Verify deployment

docker-compose ps
curl http://localhost:8000/health
```

#### Full Deployment Steps

**Step 1: Environment Configuration**
```bash

# Copy and configure environment file

cp .env.example .env

# Generate required secrets

python -c "from cryptography.fernet import Fernet; print('FERNET_KEY=' + Fernet.generate_key().decode())" >> .env
python -c "import secrets; print('SECRET_KEY='[REDACTED]" >> .env
python -c "import secrets; print('JWT_SECRET='[REDACTED]" >> .env

# Edit .env and set:

# - OPENAI_API_KEY

# - ENVIRONMENT=development

# - DATABASE_URL (if using external DB)

# - CORS_ORIGINS

```

**Step 2: Build Images**
```bash

# Build main application

docker-compose build project-ai

# Build all microservices

docker-compose build \
  mutation-firewall \
  incident-reflex \
  trust-graph \
  data-vault \
  negotiation-agent \
  compliance-engine \
  verifiable-reality \
  i-believe-in-you

# View built images

docker images | grep project-ai
```

**Step 3: Start Infrastructure Services**
```bash

# Start databases first

docker-compose up -d temporal-postgresql

# Wait for database to be ready

docker-compose exec temporal-postgresql pg_isready -U temporal

# Start Temporal

docker-compose up -d temporal

# Start monitoring stack

docker-compose up -d prometheus alertmanager grafana
```

**Step 4: Start Application Services**
```bash

# Start main application

docker-compose up -d project-ai

# Start Temporal worker

docker-compose up -d temporal-worker

# Start all microservices

docker-compose up -d \
  mutation-firewall \
  incident-reflex \
  trust-graph \
  data-vault \
  negotiation-agent \
  compliance-engine \
  verifiable-reality \
  i-believe-in-you

# Start monitoring exporters

docker-compose up -d \
  node-exporter \
  cadvisor \
  postgres-exporter
```

**Step 5: Verify Deployment**
```bash

# Check all services are running

docker-compose ps

# View logs

docker-compose logs -f project-ai

# Test health endpoints

curl http://localhost:8000/health
curl http://localhost:8011/api/v1/health/liveness  # mutation-firewall
curl http://localhost:8012/api/v1/health/liveness  # incident-reflex
curl http://localhost:8013/api/v1/health/liveness  # trust-graph
curl http://localhost:8014/api/v1/health/liveness  # data-vault
curl http://localhost:8015/api/v1/health/liveness  # negotiation-agent
curl http://localhost:8016/api/v1/health/liveness  # compliance-engine
curl http://localhost:8017/api/v1/health/liveness  # verifiable-reality
curl http://localhost:8018/api/v1/health/liveness  # i-believe-in-you

# Access monitoring

# Prometheus: http://localhost:9090

# Grafana: http://localhost:3000 (admin/admin)

# Alertmanager: http://localhost:9093

```

---

### Method 2: Kubernetes with Kustomize (Production)

#### Quick Deploy

```bash

# Deploy to production

./k8s/deploy.sh production deploy

# Check status

./k8s/deploy.sh production status
```

#### Full Kubernetes Deployment

**Step 1: Prepare Environment**
```bash

# Set target environment

export ENVIRONMENT=production  # or staging, dev
export NAMESPACE="project-ai-${ENVIRONMENT}"

# Verify cluster connection

kubectl cluster-info
kubectl get nodes
```

**Step 2: Create Namespace and Secrets**
```bash

# Create namespace

kubectl create namespace ${NAMESPACE}

# Create secrets from .env file

kubectl create secret generic project-ai-secrets \
  --from-env-file=.env.production \
  --namespace=${NAMESPACE}

# Create image pull secrets (if using private registry)

kubectl create secret docker-registry regcred \
  --docker-server=<registry-url> \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email> \
  --namespace=${NAMESPACE}

# Verify secrets

kubectl get secrets -n ${NAMESPACE}
```

**Step 3: Configure Kustomization**
```bash

# Edit overlay for environment

cd k8s/overlays/${ENVIRONMENT}

# Update kustomization.yaml with:

# - Correct image tags

# - Resource limits

# - Replica counts

# - Environment-specific configs

# Review changes

kustomize build . | less
```

**Step 4: Deploy Base Infrastructure**
```bash

# Deploy PostgreSQL

kubectl apply -f k8s/base/postgres.yaml -n ${NAMESPACE}

# Wait for PostgreSQL to be ready

kubectl wait --for=condition=ready pod -l app=postgres -n ${NAMESPACE} --timeout=300s

# Deploy Redis

kubectl apply -f k8s/base/redis.yaml -n ${NAMESPACE}
kubectl apply -f k8s/base/redis-sentinel.yaml -n ${NAMESPACE}

# Wait for Redis to be ready

kubectl wait --for=condition=ready pod -l app=redis -n ${NAMESPACE} --timeout=300s
```

**Step 5: Deploy Application**
```bash

# Apply kustomization

kustomize build k8s/overlays/${ENVIRONMENT} | kubectl apply -f -

# Alternative: Use deploy script

./k8s/deploy.sh ${ENVIRONMENT} deploy

# Monitor rollout

kubectl rollout status deployment/project-ai-app -n ${NAMESPACE}
```

**Step 6: Deploy Microservices**
```bash

# Deploy each microservice

kubectl apply -k k8s/emergent-services/${ENVIRONMENT}

# Verify deployments

kubectl get deployments -n ${NAMESPACE}
kubectl get pods -n ${NAMESPACE} -l tier=governance
```

**Step 7: Deploy Monitoring**
```bash

# Apply monitoring resources

kubectl apply -f k8s/base/monitoring.yaml -n ${NAMESPACE}

# Deploy Grafana dashboards

kubectl apply -f k8s/grafana-dashboards.yaml -n ${NAMESPACE}

# Verify monitoring stack

kubectl get pods -n ${NAMESPACE} -l component=monitoring
```

**Step 8: Configure Ingress**
```bash

# Apply ingress

kubectl apply -f k8s/base/ingress.yaml -n ${NAMESPACE}

# Get ingress IP/hostname

kubectl get ingress -n ${NAMESPACE}

# Test external access

INGRESS_HOST=$(kubectl get ingress project-ai-ingress -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
curl https://${INGRESS_HOST}/health
```

**Step 9: Enable Autoscaling**
```bash

# Deploy HPA

kubectl apply -f k8s/base/hpa.yaml -n ${NAMESPACE}

# Deploy VPA (optional)

kubectl apply -f k8s/base/vpa.yaml -n ${NAMESPACE}

# Deploy Cluster Autoscaler (if supported)

kubectl apply -f k8s/base/cluster-autoscaler.yaml

# Verify autoscaling

kubectl get hpa -n ${NAMESPACE}
kubectl get vpa -n ${NAMESPACE}
```

---

### Method 3: Helm Deployment (Alternative)

```bash

# Add Helm repository (if published)

helm repo add project-ai <repository-url>
helm repo update

# Install with Helm

helm install project-ai-${ENVIRONMENT} project-ai/project-ai \
  --namespace ${NAMESPACE} \
  --create-namespace \
  --values helm/project-ai/values-${ENVIRONMENT}.yaml \
  --timeout 10m \
  --wait

# Alternative: Install from local chart

helm upgrade --install project-ai-${ENVIRONMENT} ./helm/project-ai \
  --namespace ${NAMESPACE} \
  --values helm/project-ai/values-${ENVIRONMENT}.yaml \
  --timeout 10m \
  --wait

# Verify installation

helm list -n ${NAMESPACE}
helm status project-ai-${ENVIRONMENT} -n ${NAMESPACE}
```

---

## Verification

### Health Checks

```bash

# Application health

curl http://localhost:8000/health/live
curl http://localhost:8000/health/ready

# Microservices health

for port in {8011..8018}; do
  echo "Checking port $port..."
  curl -s http://localhost:$port/api/v1/health/liveness || echo "Failed"
done

# Kubernetes health

kubectl get pods -n ${NAMESPACE}
kubectl describe pod <pod-name> -n ${NAMESPACE}
kubectl logs <pod-name> -n ${NAMESPACE}
```

### Smoke Tests

```bash

# Run smoke tests

./k8s/deploy.sh ${ENVIRONMENT} test

# Manual API tests

# Test authentication

curl -X POST http://localhost:8001/api/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"test"}'

# Test microservices integration

curl -X GET http://localhost:8011/api/v1/policies \
  -H "X-API-Key: ${API_KEY}"
```

### Metrics Verification

```bash

# Check Prometheus targets

curl http://localhost:9090/api/v1/targets | jq .

# View metrics

curl http://localhost:8000/metrics

# Grafana dashboards

# Access: http://localhost:3000

# Login: admin/admin (change immediately)

# Import dashboards from k8s/grafana-dashboards.yaml

```

---

## Rollback

### Docker Compose Rollback

```bash

# Stop current deployment

docker-compose down

# Restore previous version

git checkout <previous-tag>

# Rebuild and redeploy

docker-compose build
docker-compose up -d

# Verify

docker-compose ps
```

### Kubernetes Rollback

```bash

# Quick rollback to previous version

kubectl rollout undo deployment/project-ai-app -n ${NAMESPACE}

# Rollback to specific revision

kubectl rollout history deployment/project-ai-app -n ${NAMESPACE}
kubectl rollout undo deployment/project-ai-app -n ${NAMESPACE} --to-revision=3

# Monitor rollback

kubectl rollout status deployment/project-ai-app -n ${NAMESPACE}

# Automated rollback using script

./rollback.sh ${ENVIRONMENT}
```

### Database Rollback

```bash

# Rollback migrations (if Alembic)

# In Kubernetes

kubectl exec -it deployment/project-ai-app -n ${NAMESPACE} -- \
  python -m alembic downgrade -1

# In Docker Compose

docker-compose exec project-ai python -m alembic downgrade -1

# Verify migration version

kubectl exec -it deployment/project-ai-app -n ${NAMESPACE} -- \
  python -m alembic current
```

---

## Troubleshooting

### Common Issues

**Issue: Container fails to start**
```bash

# Check logs

docker-compose logs project-ai
kubectl logs <pod-name> -n ${NAMESPACE}

# Check events

kubectl describe pod <pod-name> -n ${NAMESPACE}

# Common causes:

# - Missing environment variables

# - Database connection failure

# - Image pull errors

# - Resource constraints

```

**Issue: Health checks failing**
```bash

# Test health endpoint directly

kubectl port-forward pod/<pod-name> 8000:8000 -n ${NAMESPACE}
curl http://localhost:8000/health

# Check application logs

kubectl logs <pod-name> -n ${NAMESPACE} --tail=100

# Check resource usage

kubectl top pod <pod-name> -n ${NAMESPACE}
```

**Issue: Database connection failures**
```bash

# Test database connectivity

kubectl run -it --rm debug --image=postgres:13 --restart=Never -n ${NAMESPACE} -- \
  psql -h postgres.${NAMESPACE}.svc.cluster.local -U temporal -d temporal

# Check database pod

kubectl logs -l app=postgres -n ${NAMESPACE}
kubectl describe pod -l app=postgres -n ${NAMESPACE}
```

**Issue: Microservice communication failures**
```bash

# Test service DNS

kubectl run -it --rm debug --image=busybox --restart=Never -n ${NAMESPACE} -- \
  nslookup incident-reflex.${NAMESPACE}.svc.cluster.local

# Test service connectivity

kubectl run -it --rm debug --image=curlimages/curl --restart=Never -n ${NAMESPACE} -- \
  curl http://incident-reflex.${NAMESPACE}.svc.cluster.local:8000/api/v1/health/liveness

# Check network policies

kubectl get networkpolicies -n ${NAMESPACE}
```

**Issue: Insufficient resources**
```bash

# Check resource quotas

kubectl describe resourcequota -n ${NAMESPACE}

# Check node resources

kubectl top nodes

# Adjust resource requests/limits in deployment YAML

```

---

## Post-Deployment Tasks

### 1. Verify All Services

```bash

# Run comprehensive health check

python runtime_health_check.py --full

# Verify microservices

./verify_runtime_setup.py
```

### 2. Configure Monitoring Alerts

```bash

# Apply alerting rules

kubectl apply -f config/prometheus/alerts.yml

# Configure Alertmanager

kubectl apply -f config/alertmanager/alertmanager.yml

# Test alert firing

curl -X POST http://localhost:9093/api/v1/alerts -d '[...]'
```

### 3. Set Up Log Aggregation

```bash

# Deploy logging stack (if not using existing)

kubectl apply -f k8s/logging/

# Configure log retention

# Edit configmap and restart services

```

### 4. Enable Backup Automation

```bash

# Configure database backups

kubectl apply -f backup_automation/k8s/

# Test backup

kubectl create job --from=cronjob/postgres-backup backup-test -n ${NAMESPACE}
kubectl logs job/backup-test -n ${NAMESPACE}
```

### 5. Security Hardening

```bash

# Rotate secrets (do this immediately after deployment)

./emergency-rotate-secrets.sh

# Enable network policies

kubectl apply -f k8s/base/networkpolicy.yaml -n ${NAMESPACE}

# Configure RBAC

kubectl apply -f k8s/base/rbac.yaml -n ${NAMESPACE}

# Scan for vulnerabilities

docker scan project-ai:latest
```

---

## Environment-Specific Notes

### Development

- Single replica deployments acceptable
- API docs enabled (`ENABLE_API_DOCS=true`)
- Verbose logging (`LOG_LEVEL=DEBUG`)
- CORS allowed from localhost

### Staging

- Minimum 2 replicas for HA testing
- Matches production configuration
- Blue-green deployment testing
- Load testing recommended

### Production

- Minimum 3 replicas
- API docs disabled (`ENABLE_API_DOCS=false`)
- Restrictive CORS
- All secrets from vault (not .env)
- Auto-scaling enabled
- Multi-zone deployment
- Automated backups
- 24/7 monitoring

---

## References

- [Kubernetes Operations Runbook](K8S_OPERATIONS.md)
- [Docker Operations Runbook](DOCKER_OPERATIONS.md)
- [Microservices Runbook](MICROSERVICES_RUNBOOK.md)
- [Incident Response Playbook](INCIDENT_RESPONSE.md)
- [Install Guide](../../INSTALL.md)
- [Quick Start](../../QUICKSTART.md)

---

**Last Updated**: 2026-04-09  
**Maintained By**: SRE Team  
**Review Frequency**: Quarterly
