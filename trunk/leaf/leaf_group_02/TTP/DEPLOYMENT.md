<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / DEPLOYMENT.md # -->
<!-- # ============================================================================ # -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / DEPLOYMENT.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
# TTP Deployment & Operations Guide

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Operational Procedures](#operational-procedures)
5. [Monitoring & Alerting](#monitoring--alerting)
6. [Disaster Recovery](#disaster-recovery)
7. [Scaling Guidelines](#scaling-guidelines)

---

## Prerequisites

### Required Tools & Versions

**Infrastructure**:
- Kubernetes 1.28+ cluster
- kubectl 1.28+
- Helm 3.14+
- Terraform 1.7+ (for infrastructure provisioning)
- ArgoCD 2.10+ (for GitOps)

**Development**:
- Python 3.12+
- Git 2.40+
- Git LFS 3.4+ (for large texture files)
- Docker 25.0+
- Docker Compose 2.24+

**Cloud Accounts**:
- AWS account with admin access (or equivalent cloud provider)
- Container registry access (ECR, GCR, or Docker Hub)
- Domain name and DNS management
- SSL/TLS certificates (Let's Encrypt or commercial)

###System Requirements

**Development Machine**:
- CPU: 4+ cores
- RAM: 16 GB minimum, 32 GB recommended
- Storage: 100 GB SSD minimum
- OS: Linux (Ubuntu 22.04), macOS 13+, or Windows 11 with WSL2

**Production Cluster** (minimum):
- 3 master nodes: 4 CPU, 16 GB RAM each
- 5 worker nodes: 8 CPU, 32 GB RAM each
- Total storage: 5 TB (distributed across nodes)
- Network: 10 Gbps minimum between nodes

---

## Local Development Setup

### 1. Clone Repository

```bash
git clone https://github.com/IAmSoThirsty/TTP.git
cd TTP

# Initialize Git LFS for large files
git lfs install
git lfs pull
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r tools/requirements.txt

# Verify installation
python tools/validate_pack.py --version
```

### 3. Validate Local Packs

```bash
# Validate all packs
for pack in packs/*/; do
    python tools/validate_pack.py --strict "$pack"
done

# Validate specific pack with asset checking
python tools/validate_pack.py --check-assets packs/vr-cinematics/
```

### 4. Run Pre-commit Hooks (Optional)

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## Production Deployment

### Architecture Overview

```
┌─────────────────┐
│   CloudFront    │  CDN for asset delivery
│   (Global CDN)  │
└────────┬────────┘
         │
┌────────▼────────┐
│  Load Balancer  │  ALB/NLB
│   (Kong API GW) │
└────────┬────────┘
         │
    ┌────▼─────┐
    │  Istio   │  Service Mesh
    │  Gateway │
    └────┬─────┘
         │
    ┌────▼──────────────────────┐
    │   Kubernetes Cluster      │
    │  ┌─────────┐  ┌─────────┐ │
    │  │ API Pods│  │Workers  │ │
    │  └────┬────┘  └────┬────┘ │
    │       │            │      │
    │  ┌────▼────┐  ┌────▼────┐ │
    │  │Database │  │  Redis  │ │
    │  │  (RDS)  │  │ Cluster │ │
    │  └─────────┘  └─────────┘ │
    └───────────────────────────┘
            │
       ┌────▼────┐
       │   S3    │  Object storage
       │ Buckets │
       └─────────┘
```

### Step 1: Infrastructure Provisioning

**Using Terraform** (infrastructure-as-code):

```bash
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review planned changes
terraform plan -var-file=environments/production.tfvars

# Apply infrastructure
terraform apply -var-file=environments/production.tfvars

# Output will include:
# - EKS cluster endpoint
# - RDS connection string
# - S3 bucket names
# - Load balancer DNS
```

**Key Infrastructure Components Created**:
- VPC with public/private subnets across 3 AZs
- EKS cluster with node groups
- RDS PostgreSQL instance (Multi-AZ)
- ElastiCache Redis cluster
- S3 buckets for assets and backups
- CloudFront distribution
- Route53 DNS records
- ACM SSL certificates

### Step 2: Kubernetes Cluster Setup

```bash
# Configure kubectl
aws eks update-kubeconfig --region us-east-1 --name ttp-prod

# Verify cluster access
kubectl cluster-info
kubectl get nodes

# Install core components
helm repo add jetstack https://charts.jetstack.io
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install cert-manager for TLS
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set installCRDs=true

# Install Prometheus + Grafana
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  -f infrastructure/helm/prometheus-values.yaml

# Install Istio service mesh
istioctl install --set profile=production -y
kubectl label namespace default istio-injection=enabled
```

### Step 3: Deploy Application (GitOps with ArgoCD)

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for ArgoCD to be ready
kubectl wait --for=condition=available --timeout=600s \
  deployment/argocd-server -n argocd

# Get ArgoCD admin password
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 -d

# Port-forward to access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Create ArgoCD application
kubectl apply -f infrastructure/argocd/ttp-app.yaml
```

**ArgoCD Application Manifest** (`infrastructure/argocd/ttp-app.yaml`):
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: ttp-prod
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/IAmSoThirsty/TTP.git
    targetRevision: main
    path: infrastructure/kubernetes/overlays/production
  destination:
    server: https://kubernetes.default.svc
    namespace: ttp-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### Step 4: Database Migration

```bash
# Run database migrations
kubectl exec -it deployment/ttp-api -n ttp-prod -- \
  python manage.py migrate

# Seed initial data (if needed)
kubectl exec -it deployment/ttp-api -n ttp-prod -- \
  python manage.py loaddata initial_data.json
```

### Step 5: Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n ttp-prod

# Check services
kubectl get svc -n ttp-prod

# Test API health
kubectl run curl --image=curlimages/curl -i --rm --restart=Never -- \
  curl http://ttp-api.ttp-prod.svc.cluster.local:8000/healthz

# Check logs
kubectl logs -f deployment/ttp-api -n ttp-prod
```

### Step 6: Configure DNS

```bash
# Get load balancer address
kubectl get svc -n istio-system istio-ingressgateway \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'

# Create DNS records (via Route53 or your DNS provider):
# - ttp.example.com → Load Balancer
# - api.ttp.example.com → Load Balancer
# - cdn.ttp.example.com → CloudFront distribution
```

---

## Operational Procedures

### Daily Operations

**Health Checks**:
```bash
# Check API health
curl https://api.ttp.example.com/healthz

# Check database connectivity
curl https://api.ttp.example.com/readyz

# View metrics
curl https://api.ttp.example.com/metrics
```

**Log Aggregation**:
```bash
# View recent errors
kubectl logs -l app=ttp-api --tail=100 | grep ERROR

# Follow logs in real-time
stern -n ttp-prod ttp-api

# Query structured logs (via Loki)
logcli query '{namespace="ttp-prod"}' --limit=100
```

### Weekly Maintenance

**Database Maintenance**:
```sql
-- Run on primary RDS instance (via psql)

-- Vacuum and analyze
VACUUM ANALYZE;

-- Check table bloat
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Reindex if necessary
REINDEX DATABASE ttp_prod;
```

**Backup Verification**:
```bash
# List recent backups
aws rds describe-db-snapshots \
  --db-instance-identifier ttp-prod \
  --query 'DBSnapshots[*].[DBSnapshotIdentifier,SnapshotCreateTime]' \
  --output table

# Test restore (to separate instance)
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier ttp-prod-test-restore \
  --db-snapshot-identifier ttp-prod-snapshot-2026-02-18
```

### Monthly Tasks

**Security Updates**:
```bash
# Update container images
docker pull python:3.12-slim
docker build -t ttp-api:latest .
docker push registry.example.com/ttp-api:latest

# Update Kubernetes components
kubectl apply -f infrastructure/kubernetes/

# Scan for vulnerabilities
trivy image registry.example.com/ttp-api:latest
```

**Capacity Planning**:
```bash
# Review resource usage
kubectl top nodes
kubectl top pods -n ttp-prod

# Check storage usage
kubectl get pvc -n ttp-prod

# Review cost reports (AWS Cost Explorer)
aws ce get-cost-and-usage \
  --time-period Start=2026-02-01,End=2026-02-28 \
  --granularity MONTHLY \
  --metrics BlendedCost
```

---

## Monitoring & Alerting

### Grafana Dashboards

Access Grafana at: `https://grafana.ttp.example.com`

**Pre-configured Dashboards**:
1. **TTP Overview** - System-wide metrics
2. **API Performance** - Request latency, error rates
3. **Database Metrics** - Query performance, connections
4. **S3 Storage** - Upload/download rates, costs
5. **Cost Analysis** - Daily/monthly cost breakdown

### Key Metrics to Monitor

**Golden Signals**:
- **Latency**: API p95 < 200ms, p99 < 500ms
- **Traffic**: Requests/second, bandwidth
- **Errors**: HTTP 5xx rate < 0.1%
- **Saturation**: CPU < 70%, Memory < 85%

**Custom Metrics**:
```promql
# API request duration
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Database connection pool usage
pg_stat_database_numbackends / pg_settings_max_connections

# S3 upload success rate
rate(s3_upload_success_total[5m]) / rate(s3_upload_attempts_total[5m])
```

### Alert Rules

**Critical Alerts** (page immediately):
- API down > 5 minutes
- Database connection failures
- Disk space < 10%
- SSL certificate expiring < 7 days

**Warning Alerts** (ticket):
- API latency p95 > 500ms for 10 minutes
- Error rate > 1% for 5 minutes
- Memory usage > 85% for 15 minutes

---

## Disaster Recovery

### Backup Strategy

**Database Backups**:
- Automated daily snapshots (7-day retention)
- Weekly backups (30-day retention)
- Monthly archives (1-year retention)
- Continuous WAL archiving to S3

**S3 Object Versioning**:
- All texture assets versioned
- 30-day retention for deleted objects
- Cross-region replication to us-west-2

**Configuration Backups**:
- Git repository contains all infrastructure code
- Kubernetes manifests in version control
- Secrets backed up in HashiCorp Vault

### Recovery Procedures

**Database Recovery** (RPO: 5 minutes, RTO: 15 minutes):
```bash
# 1. Identify recovery point
aws rds describe-db-snapshots --db-instance-identifier ttp-prod

# 2. Restore from snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier ttp-prod-restored \
  --db-snapshot-identifier <snapshot-id>

# 3. Update application config
kubectl set env deployment/ttp-api -n ttp-prod \
  DATABASE_URL=<new-connection-string>

# 4. Verify functionality
curl https://api.ttp.example.com/healthz
```

**Complete System Recovery**:
```bash
# 1. Provision new infrastructure
cd infrastructure/terraform
terraform apply -var-file=environments/dr.tfvars

# 2. Restore database
aws rds restore-db-instance-from-db-snapshot ...

# 3. Sync S3 from replica region
aws s3 sync s3://ttp-assets-us-west-2 s3://ttp-assets-us-east-1

# 4. Deploy application
kubectl apply -f infrastructure/kubernetes/

# 5. Update DNS (Route53 failover)
aws route53 change-resource-record-sets ...
```

---

## Scaling Guidelines

### Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ttp-api-hpa
  namespace: ttp-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: ttp-api
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
```

### Database Scaling

**Vertical Scaling** (for increased workload):
```bash
# Modify RDS instance class
aws rds modify-db-instance \
  --db-instance-identifier ttp-prod \
  --db-instance-class db.r6g.2xlarge \
  --apply-immediately
```

**Read Replicas** (for read-heavy workload):
```bash
# Create read replica
aws rds create-db-instance-read-replica \
  --db-instance-identifier ttp-prod-replica-1 \
  --source-db-instance-identifier ttp-prod \
  --db-instance-class db.r6g.xlarge
```

### CDN Scaling

**CloudFront** auto-scales, but consider:
- Increase origin timeout for large file downloads
- Add more edge locations (premium pricing tier)
- Implement Lambda@Edge for dynamic content

---

## Cost Optimization

### Current Baseline Costs

**Monthly costs for 10K users, 50 TB storage**:
- Compute (EKS): $2,000
- Database (RDS): $1,500
- Storage (S3): $1,150
- Data transfer: $4,500
- CDN: $2,000
- Monitoring: $800
- **Total**: ~$12,000/month

### Optimization Strategies

1. **Use Reserved Instances**: Save 30% on EC2/RDS with 1-year commitment
2. **Enable S3 Intelligent-Tiering**: Auto-move cold data to cheaper storage
3. **CDN Offloading**: Reduce origin bandwidth by 90%
4. **Spot Instances**: Use for batch/worker nodes (70% savings)
5. **Compression**: Enable Brotli/gzip to reduce transfer costs

---

## Support & Contact

**Operational Issues**:
- On-call rotation: See PagerDuty schedule
- Escalation: ops@thirstystudios.example.com
- Emergency hotline: +1-555-TTP-HELP

**Documentation**:
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- API Reference: https://api.ttp.example.com/docs
- Runbooks: https://runbooks.ttp.example.com

---

**Document Version**: 1.0.0
**Last Updated**: 2026-02-18
**Maintained By**: TTP Operations Team
