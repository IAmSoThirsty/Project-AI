# 08: Rollback Procedures and Blue-Green Deployment

**Document**: Rollback Chains and Zero-Downtime Deployment Strategies  
**System**: K8s Rollbacks, Database Migration Rollback, Blue-Green, Canary  
**Related Systems**: Kubernetes, Health Checks, Monitoring

---


## Navigation

**Location**: `relationships\deployment\08_rollback_procedures.md`

**Parent**: [[relationships\deployment\README.md]]


## Rollback Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                  ROLLBACK & RECOVERY SYSTEM                   │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Production Issue Detected                                    │
│  ├─→ Health Check Failure                                    │
│  ├─→ Error Rate Spike (>5%)                                  │
│  ├─→ Latency Increase (p95 >1s)                             │
│  └─→ User Reports                                            │
│           ↓                                                   │
│  ┌────────────────────────────────────────┐                  │
│  │  Alert Triggered                       │                  │
│  │  • Prometheus AlertManager             │                  │
│  │  • PagerDuty notification              │                  │
│  │  • Slack #incidents channel            │                  │
│  └──────────────┬─────────────────────────┘                  │
│                 ↓                                             │
│  ┌────────────────────────────────────────┐                  │
│  │  Incident Commander Assessment         │                  │
│  │  • Severity: Critical / High / Medium  │                  │
│  │  • Impact: % of users affected         │                  │
│  │  • Decision: Rollback vs Hot-fix       │                  │
│  └──────────────┬─────────────────────────┘                  │
│                 │                                             │
│       ┌─────────┴─────────┐                                  │
│       ↓                   ↓                                  │
│  ┌──────────┐      ┌────────────┐                            │
│  │ Rollback │      │ Hot-fix    │                            │
│  │ (Fast)   │      │ (Forward)  │                            │
│  └────┬─────┘      └────────────┘                            │
│       │                                                       │
│       ↓                                                       │
│  ┌────────────────────────────────────────┐                  │
│  │  Rollback Execution                    │                  │
│  │  ┌──────────────────────────────────┐  │                  │
│  │  │  1. Kubernetes Rollout Undo      │  │                  │
│  │  │     kubectl rollout undo         │  │                  │
│  │  └──────────────────────────────────┘  │                  │
│  │  ┌──────────────────────────────────┐  │                  │
│  │  │  2. Database Migration Rollback  │  │                  │
│  │  │     alembic downgrade -1         │  │                  │
│  │  └──────────────────────────────────┘  │                  │
│  │  ┌──────────────────────────────────┐  │                  │
│  │  │  3. Configuration Revert         │  │                  │
│  │  │     kubectl rollout undo cm/cfg  │  │                  │
│  │  └──────────────────────────────────┘  │                  │
│  └──────────────┬─────────────────────────┘                  │
│                 ↓                                             │
│  ┌────────────────────────────────────────┐                  │
│  │  Post-Rollback Validation              │                  │
│  │  • Health checks passing               │                  │
│  │  • Error rate normal (<1%)             │                  │
│  │  • Latency acceptable (p95 <500ms)     │                  │
│  │  • User acceptance testing             │                  │
│  └────────────────────────────────────────┘                  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

## Kubernetes Rollout Undo

### Deployment History
```bash
# View rollout history
kubectl rollout history deployment/project-ai -n production

REVISION  CHANGE-CAUSE
1         Image update: projectai/backend:v1.0.0
2         Image update: projectai/backend:v1.0.1
3         Image update: projectai/backend:v1.0.2 (current - broken)
```

### Rollback to Previous Version
```bash
# Rollback to immediately previous revision
kubectl rollout undo deployment/project-ai -n production

# Rollback to specific revision
kubectl rollout undo deployment/project-ai --to-revision=2 -n production

# Check rollback status
kubectl rollout status deployment/project-ai -n production

# Verify pods are running old version
kubectl get pods -n production -o jsonpath='{.items[*].spec.containers[0].image}'
# Output: projectai/backend:v1.0.1
```

### Rollback Flow
```
Issue Detected (v1.0.2)
    ↓ execute
kubectl rollout undo deployment/project-ai
    ↓ updates
Deployment.spec.template.spec.containers[0].image
    ↓ from: projectai/backend:v1.0.2
    ↓ to:   projectai/backend:v1.0.1
    ↓ triggers
Rolling Update Strategy
    ├─ maxUnavailable: 1
    └─ maxSurge: 1
        ↓ steps
        1. Create new Pod (v1.0.1)
        2. Wait for ready
        3. Terminate old Pod (v1.0.2)
        4. Repeat until all Pods on v1.0.1
        ↓ result
All Pods Running v1.0.1
    ↓ validates
Health Checks Pass
    ↓ success
Service Restored
```

## Database Migration Rollback

### Alembic Downgrade
```bash
# Show current revision
alembic current
# Output: abc123 (head)

# Show migration history
alembic history
# Output:
# abc123 -> def456 (head), Add user_preferences table
# xyz789 -> abc123, Add email_verified column
# ...

# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade xyz789

# Rollback all migrations
alembic downgrade base
```

### Migration Rollback Script
```python
# alembic/versions/def456_add_user_preferences.py
def upgrade():
    """Add user_preferences table."""
    op.create_table(
        'user_preferences',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('preferences', sa.JSON),
    )

def downgrade():
    """Remove user_preferences table."""
    op.drop_table('user_preferences')
```

### Safe Migration Pattern
```python
# Backward-compatible migration (add column with default)
def upgrade():
    op.add_column('users', sa.Column('email_verified', sa.Boolean, default=False))

def downgrade():
    op.drop_column('users', 'email_verified')

# Dangerous migration (drop column - data loss!)
def upgrade():
    op.drop_column('users', 'old_field')  # ⚠️ Data loss!

def downgrade():
    # Cannot restore dropped data!
    op.add_column('users', sa.Column('old_field', sa.String))  # Empty values
```

## Blue-Green Deployment

### Environment Setup
```
Production Environment
    ├─→ Blue (current production)
    │   ├─ Deployment: project-ai-blue
    │   ├─ Pods: 3 replicas (v1.0.1)
    │   └─ Service: project-ai (selector: version=blue)
    │
    └─→ Green (new version)
        ├─ Deployment: project-ai-green
        ├─ Pods: 3 replicas (v1.0.2)
        └─ Service: project-ai (selector: version=green)
```

### Blue-Green Switch Flow
```
Current State: Blue serving traffic
    ↓ deploy
Green Environment (v1.0.2)
    ├─ helm install project-ai-green
    ├─ kubectl apply -f deployment-green.yaml
    └─ Wait for all Pods ready
        ↓ smoke test
Green Environment Health Check
    ├─ curl https://green.projectai.com/health
    ├─ Run smoke tests
    └─ Verify metrics
        ↓ if pass
Traffic Switch (instantaneous)
    ↓ patch service
    kubectl patch service project-ai \
        -p '{"spec":{"selector":{"version":"green"}}}'
    ↓ effect
    All traffic now routes to Green (v1.0.2)
    Blue (v1.0.1) still running but not receiving traffic
        ↓ monitor
Monitor Green for 10-15 minutes
    ├─→ Success
    │   ↓ cleanup
    │   kubectl delete deployment project-ai-blue
    │   ↓ done
    │   Green is now production
    │
    └─→ Failure
        ↓ instant rollback
        kubectl patch service project-ai \
            -p '{"spec":{"selector":{"version":"blue"}}}'
        ↓ effect
        Traffic back to Blue (v1.0.1)
        Zero downtime!
```

### Blue-Green Helm Chart
```yaml
# values.yaml
deployment:
  version: blue  # or green
  image:
    tag: v1.0.1

# Deployment template
metadata:
  name: project-ai-{{ .Values.deployment.version }}
  labels:
    app: project-ai
    version: {{ .Values.deployment.version }}
spec:
  selector:
    matchLabels:
      app: project-ai
      version: {{ .Values.deployment.version }}
  template:
    metadata:
      labels:
        app: project-ai
        version: {{ .Values.deployment.version }}
    spec:
      containers:
      - name: backend
        image: projectai/backend:{{ .Values.image.tag }}

# Service template (traffic routing)
apiVersion: v1
kind: Service
metadata:
  name: project-ai
spec:
  selector:
    app: project-ai
    version: {{ .Values.activeVersion }}  # blue or green
  ports:
  - port: 80
    targetPort: 8000
```

## Canary Deployment

### Canary Rollout Strategy
```
Initial State: Stable (v1.0.1) - 100% traffic
    ↓ deploy
Canary (v1.0.2) - 5% traffic
    ├─ 1 pod (v1.0.2)
    ├─ 19 pods (v1.0.1)
    └─ Service routes 5% to canary
        ↓ monitor
Canary Metrics (10 minutes)
    ├─→ Success (error rate < 1%)
    │   ↓ increase
    │   Canary: 25% traffic
    │       ↓ monitor
    │       Success
    │           ↓ increase
    │           Canary: 50% traffic
    │               ↓ monitor
    │               Success
    │                   ↓ complete
    │                   Canary: 100% traffic
    │                   ↓ cleanup
    │                   Delete stable (v1.0.1)
    │
    └─→ Failure (error rate > 1%)
        ↓ abort
        Delete Canary (v1.0.2)
        ↓ revert
        Stable: 100% traffic
```

### Istio VirtualService (Canary)
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: project-ai-canary
spec:
  hosts:
  - project-ai.example.com
  http:
  - match:
    - headers:
        x-canary:
          exact: "true"
    route:
    - destination:
        host: project-ai
        subset: canary
      weight: 100
  - route:
    - destination:
        host: project-ai
        subset: stable
      weight: 95
    - destination:
        host: project-ai
        subset: canary
      weight: 5
```

### Flagger Automated Canary
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: project-ai
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: project-ai
  service:
    port: 80
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
  webhooks:
    - name: load-test
      url: http://flagger-loadtester/
      timeout: 5s
      metadata:
        cmd: "hey -z 1m -q 10 -c 2 http://project-ai/"
```

## Configuration Rollback

### ConfigMap Versioning
```bash
# Create ConfigMap with version label
kubectl create configmap project-ai-config-v2 \
    --from-file=config.yaml \
    --dry-run=client -o yaml | \
    kubectl label --local -f - version=v2 -o yaml | \
    kubectl apply -f -

# Update Deployment to use new ConfigMap
kubectl set env deployment/project-ai \
    CONFIG_VERSION=v2

# Rollback to previous ConfigMap
kubectl set env deployment/project-ai \
    CONFIG_VERSION=v1
```

## Disaster Recovery

### Backup and Restore
```bash
# Backup Kubernetes resources
kubectl get all -n production -o yaml > backup-production.yaml

# Backup database
pg_dump projectai > backup-$(date +%Y%m%d).sql

# Restore database
psql projectai < backup-20260420.sql

# Restore Kubernetes resources
kubectl apply -f backup-production.yaml
```

### Snapshot Rollback (Cloud Providers)
```bash
# AWS EBS Snapshot
aws ec2 create-snapshot --volume-id vol-abc123 --description "Pre-deployment"

# Rollback: Restore from snapshot
aws ec2 create-volume --snapshot-id snap-xyz789 --availability-zone us-east-1a
```

## Related Systems

- `03_kubernetes_orchestration.md` - K8s deployment strategies
- `07_health_monitoring_hooks.md` - Health-triggered rollback
- `09_environment_flows.md` - Environment promotion

---

**Status**: ✅ Complete  
**Coverage**: K8s rollbacks, database migration rollback, blue-green, canary, disaster recovery
