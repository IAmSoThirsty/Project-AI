# 09: Environment Flows

**Document**: Development → Staging → Production Promotion Flows  
**System**: Environment Promotion, Configuration Management, Validation Gates  
**Related Systems**: CI/CD, Kubernetes, Health Checks, Rollback Procedures

---


## Navigation

**Location**: `relationships\deployment\09_environment_flows.md`

**Parent**: [[relationships\deployment\README.md]]


## Environment Promotion Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                 ENVIRONMENT PROMOTION FLOW                    │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────────────────────────────────┐                 │
│  │  Development Environment                │                 │
│  │  • Local (Docker Compose)               │                 │
│  │  • SQLite / PostgreSQL                  │                 │
│  │  • Hot Reload Enabled                   │                 │
│  │  • Debug Mode                           │                 │
│  │  • .env.development                     │                 │
│  │  • Ports: 3000 (frontend), 5000 (API)   │                 │
│  └──────────────┬──────────────────────────┘                 │
│                 │                                             │
│                 ↓ git push origin develop                     │
│                 ↓ automated promotion                         │
│  ┌─────────────────────────────────────────┐                 │
│  │  Staging Environment                    │                 │
│  │  • Kubernetes Cluster (staging NS)     │                 │
│  │  • PostgreSQL (managed DB)             │                 │
│  │  • Full Stack Deployed                 │                 │
│  │  • Production-like Config              │                 │
│  │  • .env.staging / K8s Secrets          │                 │
│  │  • URL: https://staging.projectai.com  │                 │
│  └──────────────┬──────────────────────────┘                 │
│                 │                                             │
│                 ↓ manual approval + merge to main            │
│                 ↓ validation gates                            │
│  ┌─────────────────────────────────────────┐                 │
│  │  Production Environment                 │                 │
│  │  • Kubernetes Multi-Region             │                 │
│  │  • PostgreSQL (HA, replicated)         │                 │
│  │  • Blue-Green Deployment               │                 │
│  │  • Vault Secrets                       │                 │
│  │  • .env.production (immutable)         │                 │
│  │  • URL: https://projectai.com          │                 │
│  └─────────────────────────────────────────┘                 │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Development Environment

### Local Setup
```bash
# Clone repository
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate (Windows)

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env.development
# Edit .env.development with local API keys

# Run locally
python -m src.app.main  # Desktop app
# or
docker-compose up  # Web stack
```

### Development Configuration
```bash
# .env.development
APP_ENV=development
DEBUG=True
LOG_LEVEL=DEBUG

# Database (local)
DATABASE_URL=sqlite:///data/project-ai.db
# or
DATABASE_URL=postgresql://postgres:password@localhost:5432/projectai_dev

# External APIs (dev keys)
OPENAI_API_KEY=sk-dev-...
HUGGINGFACE_API_KEY=hf_dev_...

# Feature Flags
ENABLE_NEW_FEATURE=True
ENABLE_METRICS=False

# Hot Reload
FLASK_ENV=development
VITE_DEV_SERVER=True
```

### Development Workflow
```
Developer Workflow
    ↓ code changes
Local Testing
    ├─ python -m pytest tests/
    ├─ npm run test (frontend)
    └─ manual testing
        ↓ commit
Git Commit (develop branch)
    ↓ push
GitHub (develop branch)
    ↓ triggers
CI Pipeline
    ├─ Lint (ruff, mypy)
    ├─ Security (bandit, trivy)
    └─ Tests (pytest, jest)
        ↓ if pass
        Auto-deploy to Staging
```

## Staging Environment

### Staging Deployment
```bash
# Deployed via GitHub Actions
# .github/workflows/deploy-staging.yml

on:
  push:
    branches: [develop]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      
      - name: Build Docker Image
        run: |
          docker build -t projectai/backend:staging-${{ github.sha }} .
          docker push projectai/backend:staging-${{ github.sha }}
      
      - name: Deploy to K8s Staging
        run: |
          kubectl set image deployment/project-ai \
            backend=projectai/backend:staging-${{ github.sha }} \
            -n staging
          kubectl rollout status deployment/project-ai -n staging
```

### Staging Configuration
```yaml
# K8s ConfigMap (staging namespace)
apiVersion: v1
kind: ConfigMap
metadata:
  name: project-ai-config
  namespace: staging
data:
  APP_ENV: "staging"
  DEBUG: "False"
  LOG_LEVEL: "info"
  DATABASE_HOST: "postgresql-staging.default.svc.cluster.local"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "projectai_staging"
  REDIS_URL: "redis://redis-staging:6379/0"
  ENABLE_METRICS: "True"
  ENABLE_NEW_FEATURE: "True"  # Test new features

---
# K8s Secret (staging namespace)
apiVersion: v1
kind: Secret
metadata:
  name: project-ai-secrets
  namespace: staging
type: Opaque
data:
  DATABASE_PASSWORD: <base64-staging-password>
  OPENAI_API_KEY: <base64-staging-key>
  FERNET_KEY: <base64-staging-fernet>
  JWT_SECRET_KEY: <base64-staging-jwt>
```

### Staging Validation Gates
```
Staging Deployment Complete
    ↓ automated tests
Smoke Tests
    ├─ curl https://staging.projectai.com/health
    ├─ curl https://staging.projectai.com/api/version
    └─ pytest tests/e2e/test_smoke.py
        ↓ pass
Integration Tests
    ├─ pytest tests/integration/
    ├─ npm run test:e2e
    └─ API contract tests (Postman)
        ↓ pass
Performance Tests
    ├─ Load test (100 RPS for 5 min)
    ├─ Latency check (p95 < 500ms)
    └─ Memory usage < 80%
        ↓ pass
Security Scan
    ├─ OWASP ZAP scan
    ├─ Trivy container scan
    └─ Bandit code analysis
        ↓ all pass
Ready for Production Promotion
    ↓ manual approval
```

## Production Environment

### Production Promotion
```bash
# Manual promotion workflow
# 1. Create Pull Request (develop → main)
gh pr create --base main --head develop --title "Release v1.0.2"

# 2. PR Approval (requires 2 approvers)
gh pr review <PR_NUMBER> --approve

# 3. Merge to main
gh pr merge <PR_NUMBER> --squash

# 4. Automated production deployment triggered
# .github/workflows/deploy-production.yml triggers on push to main
```

### Production Deployment Workflow
```yaml
# .github/workflows/deploy-production.yml
on:
  push:
    branches: [main]

jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://projectai.com
    steps:
      - uses: actions/checkout@v4
      
      - name: Wait for Manual Approval
        # Configured in GitHub Environment settings
        # Requires approval from CODEOWNERS
      
      - name: Tag Release
        run: |
          git tag v${{ steps.version.outputs.version }}
          git push origin v${{ steps.version.outputs.version }}
      
      - name: Blue-Green Deploy
        run: |
          # Deploy to green environment
          helm upgrade project-ai ./helm/project-ai \
            --namespace production \
            --set image.tag=${{ github.sha }} \
            --set environment=green \
            --wait --timeout=10m
          
          # Smoke test green environment
          ./scripts/smoke-tests.sh production-green
          
          # Switch traffic to green (zero downtime)
          kubectl patch service project-ai \
            -p '{"spec":{"selector":{"version":"green"}}}' \
            -n production
          
          # Monitor for 10 minutes
          sleep 600
          
          # Verify health
          if ./scripts/health-check.sh production; then
            echo "Deployment successful"
            # Cleanup old blue environment
            kubectl delete deployment project-ai-blue -n production
          else
            echo "Deployment failed - rolling back"
            kubectl patch service project-ai \
              -p '{"spec":{"selector":{"version":"blue"}}}' \
              -n production
            exit 1
          fi
```

### Production Configuration
```yaml
# K8s ConfigMap (production namespace)
apiVersion: v1
kind: ConfigMap
metadata:
  name: project-ai-config
  namespace: production
data:
  APP_ENV: "production"
  DEBUG: "False"
  LOG_LEVEL: "warning"
  DATABASE_HOST: "postgresql-prod.default.svc.cluster.local"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "projectai"
  REDIS_URL: "redis://redis-prod:6379/0"
  ENABLE_METRICS: "True"
  ENABLE_NEW_FEATURE: "False"  # Disabled until validated in staging
  SENTRY_DSN: "https://..."
  PROMETHEUS_ENABLED: "True"

---
# K8s Secret (production namespace - from Vault)
apiVersion: v1
kind: Secret
metadata:
  name: project-ai-secrets
  namespace: production
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "project-ai"
    vault.hashicorp.com/agent-inject-secret-database: "secret/data/projectai/database"
type: Opaque
# Secrets injected by Vault Agent Sidecar
```

## Configuration Hierarchy

### Environment Variable Precedence
```
1. Hardcoded Defaults (in code)
    ↓ overridden by
2. .env.defaults (committed to repo)
    ↓ overridden by
3. .env (local, gitignored)
    ↓ overridden by
4. .env.{environment} (.env.staging, .env.production)
    ↓ overridden by
5. Environment Variables (OS-level)
    ↓ overridden by
6. K8s ConfigMap (for K8s deployments)
    ↓ overridden by
7. K8s Secret (for sensitive data)
    ↓ overridden by
8. Vault (production secrets)
```

### Environment Comparison Matrix

| Feature | Development | Staging | Production |
|---------|-------------|---------|------------|
| **Infrastructure** | Docker Compose | Kubernetes (1 region) | Kubernetes (multi-region) |
| **Database** | SQLite / Local PG | Managed PostgreSQL | Managed PG (HA, replicas) |
| **Cache** | In-memory | Redis (single instance) | Redis Cluster |
| **Secrets** | .env file | K8s Secrets | HashiCorp Vault |
| **Monitoring** | Console logs | Prometheus + Grafana | Full observability stack |
| **Scaling** | 1 instance | 3 pods (HPA: min 3, max 10) | 10 pods (HPA: min 10, max 50) |
| **Deployment** | Manual | Auto (on develop push) | Manual approval + auto |
| **Rollback** | N/A | kubectl rollout undo | Blue-green switch |
| **SSL/TLS** | Self-signed | Let's Encrypt (staging) | Commercial cert |
| **CDN** | None | None | CloudFlare |
| **Backups** | None | Daily snapshots | Hourly snapshots + PITR |
| **Debug Mode** | Enabled | Disabled | Disabled |
| **Log Level** | DEBUG | INFO | WARNING |
| **Feature Flags** | All enabled | Beta features | Stable only |
| **Downtime Tolerance** | High | Medium | Zero |

## Promotion Checklist

### Pre-Promotion (Staging → Production)
- [ ] All staging tests passing
- [ ] No critical/high security vulnerabilities
- [ ] Performance benchmarks met
- [ ] Database migrations tested
- [ ] Rollback plan documented
- [ ] Monitoring dashboards updated
- [ ] Alert rules configured
- [ ] On-call engineer identified
- [ ] Changelog updated
- [ ] Release notes drafted
- [ ] Stakeholders notified

### During Promotion
- [ ] Manual approval obtained
- [ ] Database backup created
- [ ] Blue environment deployed
- [ ] Smoke tests pass
- [ ] Traffic switched to green
- [ ] Monitoring confirms health
- [ ] Error rate within SLA (<1%)
- [ ] Latency within SLA (p95 <500ms)

### Post-Promotion
- [ ] All health checks passing
- [ ] User acceptance testing
- [ ] Error tracking reviewed (Sentry)
- [ ] Performance metrics normal
- [ ] Logs reviewed for anomalies
- [ ] Old blue environment cleaned up
- [ ] Git tag created
- [ ] GitHub Release published
- [ ] Documentation updated
- [ ] Post-mortem (if issues)

## Related Systems

- `05_cicd_pipelines.md` - Automated deployment workflows
- `03_kubernetes_orchestration.md` - K8s deployment strategies
- `08_rollback_procedures.md` - Rollback on promotion failure
- `07_health_monitoring_hooks.md` - Post-deployment validation

---

**Status**: ✅ Complete  
**Coverage**: Dev/staging/prod environments, promotion flows, validation gates, configuration management
