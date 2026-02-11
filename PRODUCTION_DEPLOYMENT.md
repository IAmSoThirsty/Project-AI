# 🏗️ Production Deployment Guide

## Quick Start

### Prerequisites

```bash
# Install required tools
brew install kubectl helm k6  # macOS
# OR
apt-get install kubectl helm  # Ubuntu/Debian

# Verify installations
kubectl version --client
helm version
k6 version
```

### Deploy to Kubernetes

```bash
# Using Kustomize (dev environment)
kubectl apply -k k8s/overlays/dev

# Using Helm (production environment)
helm install project-ai ./helm/project-ai \
  --namespace project-ai \
  --create-namespace \
  --values helm/project-ai/values-production.yaml

# Using deployment script
cd k8s
./deploy.sh production deploy
```

### Verify Deployment

```bash
# Check deployment status
kubectl get all -n project-ai

# Check pod health
kubectl get pods -n project-ai -o wide

# Check logs
kubectl logs -f -l app.kubernetes.io/name=project-ai -n project-ai

# Run smoke tests
cd k8s && ./deploy.sh production test
```

## Architecture Overview

Project-AI is now production-ready with:

✅ **Kubernetes-native deployment** (14 manifests + Helm chart)  
✅ **Multi-environment support** (dev/staging/production)  
✅ **Auto-scaling** (3-10 pods based on CPU/memory)  
✅ **High availability** (Pod anti-affinity, PDB)  
✅ **Security hardening** (Rate limiting, request validation, WAF)  
✅ **Observability** (OpenTelemetry tracing, Prometheus metrics)  
✅ **Circuit breakers** (Automatic failure detection & recovery)  
✅ **Health checks** (Liveness, readiness, startup probes)  
✅ **Comprehensive testing** (E2E, load testing with k6/Locust)  
✅ **Production CI/CD** (Automated deployment with rollback)

See [PRODUCTION_ARCHITECTURE.md](docs/PRODUCTION_ARCHITECTURE.md) for detailed architecture.

## Security Features

### Rate Limiting
```python
# Configured per environment
# Development: No limits
# Staging: 120 requests/minute
# Production: 60 requests/minute
```

### Request Validation
- SQL injection prevention
- XSS pattern detection  
- Command injection blocking
- Path traversal protection
- Input sanitization

### Security Headers
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Content-Security-Policy: default-src 'self'
```

## Testing

### Run E2E Tests
```bash
pytest tests/e2e/test_production_readiness.py -v
```

### Run Load Tests

**Using k6:**
```bash
k6 run tests/load/k6-load-test.js --vus 50 --duration 5m
```

**Using Locust:**
```bash
locust -f tests/load/locust_load_test.py \
  --host=http://localhost:5000 \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m
```

### Performance Targets
- Response Time (p95): < 500ms
- Error Rate: < 5%
- Throughput: > 200 RPS

## Monitoring

### Access Dashboards

**Prometheus Metrics:**
```bash
kubectl port-forward -n project-ai svc/prometheus 9090:9090
open http://localhost:9090
```

**Grafana (if installed):**
```bash
kubectl port-forward -n project-ai svc/grafana 3000:3000
open http://localhost:3000
```

### Key Metrics
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `http_requests_failed` - Failed requests
- `app_connections_active` - Active connections

## Troubleshooting

### Pods Not Starting
```bash
# Check pod status
kubectl describe pod <pod-name> -n project-ai

# Check events
kubectl get events -n project-ai --sort-by='.lastTimestamp'

# Check logs
kubectl logs <pod-name> -n project-ai --previous
```

### High Memory Usage
```bash
# Check resource usage
kubectl top pods -n project-ai

# Adjust resource limits in values.yaml
resources:
  limits:
    memory: "3Gi"  # Increase if needed
```

### Database Connection Issues
```bash
# Check PostgreSQL status
kubectl exec -it postgres-0 -n project-ai -- psql -U projectai -c "SELECT 1"

# Restart PostgreSQL
kubectl rollout restart statefulset/postgres -n project-ai
```

## Rollback

```bash
# Automatic rollback (on deployment failure)
# Handled by CI/CD pipeline

# Manual rollback
kubectl rollout undo deployment/project-ai-app -n project-ai

# Rollback to specific revision
kubectl rollout history deployment/project-ai-app -n project-ai
kubectl rollout undo deployment/project-ai-app -n project-ai --to-revision=3
```

## Scaling

### Manual Scaling
```bash
# Scale to 5 replicas
kubectl scale deployment/project-ai-app -n project-ai --replicas=5
```

### Auto-Scaling (HPA)
```yaml
# Configured in k8s/base/hpa.yaml
minReplicas: 3
maxReplicas: 10
targetCPUUtilizationPercentage: 70
targetMemoryUtilizationPercentage: 80
```

## CI/CD Pipeline

### Deployment Flow
```
1. Push to main → Lint & Test
2. Security Scan (Trivy, OWASP)
3. Build Docker Image (multi-arch)
4. Push to Registry (GHCR)
5. Deploy to Staging
6. Run Smoke Tests
7. Load Testing
8. Deploy to Production (manual approval)
9. Monitoring & Alerts
10. Auto-rollback (on failure)
```

### Trigger Deployment
```bash
# Tag for production release
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions will automatically:
# 1. Build and test
# 2. Deploy to staging
# 3. Wait for approval
# 4. Deploy to production
```

## Environment Variables

### Required Secrets
```bash
# Create from .env file
kubectl create secret generic project-ai-secrets \
  --from-env-file=.env \
  -n project-ai

# Or use Sealed Secrets / Vault
```

### Configuration
```yaml
# See k8s/base/configmap.yaml
APP_ENV: "production"
LOG_LEVEL: "INFO"
API_PORT: "5000"
ENABLE_RATE_LIMITING: "true"
RATE_LIMIT_PER_MINUTE: "60"
```

## Cost Optimization

### Estimated Monthly Costs
- Kubernetes cluster (3-10 nodes): $200-500
- Storage (DB + logs): $10-30
- Networking (LB + egress): $50-100
- Monitoring: $50
- **Total**: $310-680/month

### Optimization Tips
1. Use spot instances for non-critical workloads
2. Enable cluster autoscaler
3. Set resource requests/limits accurately
4. Use PVC lifecycle policies
5. Implement caching (Redis)

## Support

### Documentation
- [Production Architecture](docs/PRODUCTION_ARCHITECTURE.md)
- [Kubernetes README](k8s/README.md)
- [Load Testing Guide](tests/load/README.md)
- [API Documentation](api/README.md)

### Getting Help
- GitHub Issues: https://github.com/IAmSoThirsty/Project-AI/issues
- Slack: #project-ai-production
- Email: devops@project-ai.example.com

### On-Call
- PagerDuty: https://project-ai.pagerduty.com
- Runbooks: docs/runbooks/
- Status Page: https://status.project-ai.example.com

## License

MIT License - see [LICENSE](LICENSE) file

---

**Project-AI** - Production-Ready AI Platform with Civilization-Tier Architecture
