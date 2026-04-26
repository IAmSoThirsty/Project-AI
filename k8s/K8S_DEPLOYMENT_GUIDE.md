# Kubernetes Deployment Guide for Project-AI

**Status:** Manifests created and validated  
**Cluster Requirement:** Kubernetes 1.24+  
**Tested:** Manifest validation only (cluster not available)

---

## 📋 Quick Start

### Prerequisites
- Docker Desktop with Kubernetes enabled, OR
- Minikube, OR
- Any Kubernetes cluster (local/cloud)
- kubectl configured

### Minimal Deployment (Development)

```bash
# 1. Ensure Docker image is available
docker images | grep project-ai

# 2. Apply minimal deployment
kubectl apply -f k8s/minimal-deploy.yaml

# 3. Verify deployment
kubectl get all -n project-ai

# 4. Check pod logs
kubectl logs -n project-ai -l app=project-ai

# 5. Port forward for local access (optional)
kubectl port-forward -n project-ai svc/project-ai 8080:80
```

---

## 📦 What's Deployed

### Minimal Deployment (k8s/minimal-deploy.yaml)
- **Namespace:** project-ai
- **Deployment:** 1 replica (auto-scales to 3)
- **Service:** ClusterIP on port 80
- **Resources:** 256Mi RAM, 0.1 CPU (burst to 512Mi, 0.5 CPU)
- **Security:** Non-root user (UID 1000)
- **Health Checks:** Liveness + Readiness probes

### Full Deployment (k8s/base/)
Complete production-ready manifests:
- ConfigMap (environment configuration)
- Deployment (with security context)
- Service (ClusterIP/LoadBalancer)
- Ingress (HTTPS routing)
- HPA (Horizontal Pod Autoscaler)
- PDB (Pod Disruption Budget)
- NetworkPolicy (network isolation)
- RBAC (service accounts)
- Monitoring (Prometheus integration)
- PostgreSQL StatefulSet
- Redis StatefulSet

---

## 🎯 Deployment Verification

### Check Deployment Status
```bash
# Namespace created
kubectl get namespace project-ai

# Pods running
kubectl get pods -n project-ai
# Expected: project-ai-xxxxxxxxxx-xxxxx  1/1  Running

# Service available
kubectl get svc -n project-ai
# Expected: project-ai  ClusterIP  10.x.x.x  <none>  80/TCP

# HPA configured
kubectl get hpa -n project-ai
# Expected: project-ai-hpa  Deployment/project-ai  <metrics>
```

### Check Pod Logs
```bash
kubectl logs -n project-ai -l app=project-ai --tail=50
```

Expected output:
```
[UI-CONSOLE] Initializing Sovereign Governance Substrate...
[UI-CONSOLE] Security Layers: [ACTIVE]
[UI-CONSOLE] Sovereign Substrate is now OPERATIONAL.
```

---

## 🔧 Configuration

### Environment Variables (ConfigMap)
- `PYTHONUNBUFFERED=1` - Real-time logging
- `ENVIRONMENT=development` - Deployment environment
- `LOG_LEVEL=INFO` - Logging verbosity

### Resource Limits
**Requests (guaranteed):**
- Memory: 256Mi
- CPU: 100m (0.1 cores)

**Limits (maximum):**
- Memory: 512Mi
- CPU: 500m (0.5 cores)

### Auto-Scaling (HPA)
- Min replicas: 1
- Max replicas: 3
- Scale trigger: CPU >70% or Memory >80%

---

## 🛠️ Troubleshooting

### Pod Not Starting
```bash
# Describe pod for events
kubectl describe pod -n project-ai -l app=project-ai

# Check image pull
kubectl get events -n project-ai --sort-by='.lastTimestamp'
```

Common issues:
- Image not found → Build Docker image first
- ImagePullBackOff → Use `imagePullPolicy: IfNotPresent` for local images
- CrashLoopBackOff → Check logs: `kubectl logs -n project-ai <pod-name>`

### Health Check Failing
```bash
# Check liveness probe
kubectl exec -n project-ai <pod-name> -- python -c "import sys; sys.exit(0)"

# Expected: Exit code 0 (success)
```

### Service Not Accessible
```bash
# Test from within cluster
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- \
  curl http://project-ai.project-ai.svc.cluster.local

# Port forward to localhost
kubectl port-forward -n project-ai svc/project-ai 8080:80
# Access: http://localhost:8080
```

---

## 🚀 Advanced Deployments

### Using Kustomize (Recommended)
```bash
# Development
kubectl apply -k k8s/overlays/dev

# Staging
kubectl apply -k k8s/overlays/staging

# Production
kubectl apply -k k8s/overlays/production
```

### Using Helm (Future)
```bash
helm install project-ai ./helm/project-ai \
  --namespace project-ai \
  --create-namespace \
  --values values-dev.yaml
```

### Using ArgoCD (GitOps)
```bash
kubectl apply -f k8s/tk8s/argocd/applications.yaml
```

---

## 📊 Monitoring

### Prometheus Metrics
If Prometheus is installed:
```bash
kubectl apply -f k8s/base/monitoring.yaml
```

### Grafana Dashboards
```bash
kubectl apply -f k8s/grafana-dashboards.yaml
```

### View Metrics
```bash
# CPU/Memory usage
kubectl top pod -n project-ai

# HPA status
kubectl get hpa -n project-ai -w
```

---

## 🔒 Security

### Network Policies
```bash
# Apply network isolation
kubectl apply -f k8s/base/networkpolicy.yaml
```

Restricts:
- Ingress: Only from ingress controller
- Egress: DNS, external APIs only

### Pod Security
- Non-root user (UID 1000, GID 1000)
- Read-only root filesystem (optional)
- No privilege escalation
- Capabilities dropped

### RBAC
```bash
kubectl apply -f k8s/base/rbac.yaml
```

Creates:
- ServiceAccount: project-ai-sa
- Role: project-ai-role
- RoleBinding: project-ai-rolebinding

---

## 🧹 Cleanup

```bash
# Delete minimal deployment
kubectl delete -f k8s/minimal-deploy.yaml

# Or delete namespace (removes everything)
kubectl delete namespace project-ai

# Verify cleanup
kubectl get all -n project-ai
# Expected: No resources found
```

---

## 📚 Manifest Structure

```
k8s/
├── minimal-deploy.yaml          # Quick start (this guide uses)
├── base/                        # Base manifests (production-ready)
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── hpa.yaml
│   ├── ingress.yaml
│   ├── networkpolicy.yaml
│   ├── pdb.yaml
│   ├── rbac.yaml
│   └── monitoring.yaml
├── overlays/                    # Environment-specific patches
│   ├── dev/
│   ├── staging/
│   └── production/
└── tk8s/                        # Advanced features
    ├── argocd/
    ├── security/
    └── monitoring/
```

---

## ✅ Validation Results

**Manifest Validation:**
```bash
# Dry-run validation (no cluster needed)
kubectl apply -f k8s/minimal-deploy.yaml --dry-run=client
# Result: All manifests valid ✅
```

**Docker Image:**
- Built: ✅
- Tagged: project-ai:test
- Size: 1.12GB
- Security: Non-root user ✅
- Health check: Configured ✅

**Deployment Readiness:**
- Manifests: Valid ✅
- Image: Available ✅
- Security: Configured ✅
- Monitoring: Ready ✅
- Auto-scaling: Configured ✅

---

## 🎯 Production Checklist

Before production deployment:

### Infrastructure
- [ ] Kubernetes cluster provisioned (1.24+)
- [ ] kubectl configured with access
- [ ] Image registry available (Docker Hub, GCR, ECR, etc.)
- [ ] Ingress controller installed (nginx, traefik, etc.)
- [ ] Certificate management (cert-manager recommended)

### Application
- [x] Docker image built and tested
- [x] Health checks configured
- [x] Resource limits set
- [x] Security context configured
- [ ] Secrets externalized (Vault, Sealed Secrets, etc.)
- [ ] Persistent storage configured (if needed)

### Observability
- [ ] Prometheus installed
- [ ] Grafana dashboards configured
- [ ] Log aggregation (ELK, Loki, etc.)
- [ ] Alerting rules defined

### Security
- [x] Network policies defined
- [x] RBAC configured
- [x] Non-root containers
- [ ] Image scanning in CI/CD
- [ ] Runtime security (Falco, etc.)
- [ ] Secret rotation strategy

---

## 📈 Next Steps

1. **Enable Kubernetes in Docker Desktop**
   - Docker Desktop → Settings → Kubernetes → Enable

2. **Apply Minimal Deployment**
   ```bash
   kubectl apply -f k8s/minimal-deploy.yaml
   ```

3. **Verify Deployment**
   ```bash
   kubectl get all -n project-ai
   kubectl logs -n project-ai -l app=project-ai
   ```

4. **Test Locally**
   ```bash
   kubectl port-forward -n project-ai svc/project-ai 8080:80
   curl http://localhost:8080
   ```

5. **Scale to Production**
   - Use k8s/overlays/production
   - Configure ingress with TLS
   - Set up monitoring
   - Deploy to cloud cluster

---

**Status:** K8s manifests validated and ready for deployment  
**Requirements:** Kubernetes cluster (local or cloud)  
**Recommendation:** Start with minimal-deploy.yaml for testing
