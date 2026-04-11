# Kubernetes Operations Runbook

## Purpose

Comprehensive operational procedures for managing the Sovereign Governance Substrate platform on Kubernetes, including service scaling, updates, rollbacks, monitoring, and troubleshooting.

## Prerequisites

### Required Tools

- kubectl 1.24+
- kustomize 4.5+
- helm 3.x
- jq
- yq (optional)

### Required Access

- Kubernetes cluster admin or namespace admin
- kubectl configured with appropriate context
- Access to container registry

### Environment Variables

```bash
export NAMESPACE="project-ai-production"
export KUBECONFIG="/path/to/kubeconfig"
```

---

## Service Scaling

### Manual Scaling

#### Scale Main Application

```bash

# Scale to specific replica count

kubectl scale deployment/project-ai-app \
  --replicas=5 \
  -n ${NAMESPACE}

# Verify scaling

kubectl get deployment project-ai-app -n ${NAMESPACE}
kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=project-ai
```

#### Scale Microservices

```bash

# Scale individual microservice

kubectl scale deployment/mutation-firewall \
  --replicas=3 \
  -n ${NAMESPACE}

# Scale multiple services

for service in mutation-firewall incident-reflex trust-graph data-vault; do
  echo "Scaling ${service}..."
  kubectl scale deployment/${service} --replicas=3 -n ${NAMESPACE}
done

# Verify all microservices

kubectl get deployments -n ${NAMESPACE} -l tier=governance
```

#### Scale Database Replicas

```bash

# Scale PostgreSQL read replicas

kubectl scale statefulset/postgres-read-replica \
  --replicas=2 \
  -n ${NAMESPACE}

# Verify database replicas

kubectl get statefulset -n ${NAMESPACE}
kubectl get pods -n ${NAMESPACE} -l app=postgres
```

### Horizontal Pod Autoscaling (HPA)

#### View Current HPA Status

```bash

# List all HPAs

kubectl get hpa -n ${NAMESPACE}

# Describe HPA for details

kubectl describe hpa project-ai -n ${NAMESPACE}

# Watch HPA in real-time

kubectl get hpa project-ai -n ${NAMESPACE} --watch
```

#### Modify HPA Settings

```bash

# Update min/max replicas

kubectl patch hpa project-ai -n ${NAMESPACE} --patch '
spec:
  minReplicas: 5
  maxReplicas: 20
'

# Update target CPU utilization

kubectl patch hpa project-ai -n ${NAMESPACE} --patch '
spec:
  metrics:

  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60

'

# Verify changes

kubectl get hpa project-ai -n ${NAMESPACE} -o yaml
```

#### Disable/Enable HPA

```bash

# Disable HPA (delete it)

kubectl delete hpa project-ai -n ${NAMESPACE}

# Re-enable HPA (apply from manifest)

kubectl apply -f k8s/base/hpa.yaml -n ${NAMESPACE}
```

### Vertical Pod Autoscaling (VPA)

#### Check VPA Recommendations

```bash

# View VPA status

kubectl get vpa -n ${NAMESPACE}

# Get detailed recommendations

kubectl describe vpa project-ai-vpa -n ${NAMESPACE}

# View recommendations as JSON

kubectl get vpa project-ai-vpa -n ${NAMESPACE} -o json | \
  jq '.status.recommendation'
```

#### Apply VPA Recommendations

```bash

# Edit deployment with recommended resources

kubectl edit deployment project-ai-app -n ${NAMESPACE}

# Or patch directly

kubectl patch deployment project-ai-app -n ${NAMESPACE} --patch '
spec:
  template:
    spec:
      containers:

      - name: project-ai
        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"

'
```

---

## Rolling Updates

### Standard Rolling Update

#### Update Application Image

```bash

# Update to new image tag

kubectl set image deployment/project-ai-app \
  project-ai=project-ai:v2.0.0 \
  -n ${NAMESPACE}

# Alternative: Patch deployment

kubectl patch deployment project-ai-app -n ${NAMESPACE} --patch '
spec:
  template:
    spec:
      containers:

      - name: project-ai
        image: project-ai:v2.0.0

'

# Monitor rollout progress

kubectl rollout status deployment/project-ai-app -n ${NAMESPACE}
```

#### Update All Microservices

```bash

# Update all governance microservices to new version

VERSION="v2.0.0"

for service in mutation-firewall incident-reflex trust-graph data-vault \
               negotiation-agent compliance-engine verifiable-reality; do
  echo "Updating ${service} to ${VERSION}..."
  kubectl set image deployment/${service} \
    ${service}=${service}:${VERSION} \
    -n ${NAMESPACE}
done

# Monitor all rollouts

kubectl get deployments -n ${NAMESPACE} -l tier=governance --watch
```

#### Update Configuration

```bash

# Update ConfigMap

kubectl edit configmap project-ai-config -n ${NAMESPACE}

# Restart pods to pick up new config

kubectl rollout restart deployment/project-ai-app -n ${NAMESPACE}

# Update Secret

kubectl edit secret project-ai-secrets -n ${NAMESPACE}

# Restart all deployments using the secret

kubectl rollout restart deployment -n ${NAMESPACE} -l app.kubernetes.io/name=project-ai
```

### Rollout Control

#### Pause Rollout

```bash

# Pause ongoing rollout

kubectl rollout pause deployment/project-ai-app -n ${NAMESPACE}

# Verify status

kubectl rollout status deployment/project-ai-app -n ${NAMESPACE}
```

#### Resume Rollout

```bash

# Resume paused rollout

kubectl rollout resume deployment/project-ai-app -n ${NAMESPACE}

# Monitor completion

kubectl rollout status deployment/project-ai-app -n ${NAMESPACE}
```

#### View Rollout History

```bash

# Show rollout history

kubectl rollout history deployment/project-ai-app -n ${NAMESPACE}

# View specific revision details

kubectl rollout history deployment/project-ai-app \
  -n ${NAMESPACE} \
  --revision=5
```

---

## Rollback Procedures

### Quick Rollback

```bash

# Rollback to previous version

kubectl rollout undo deployment/project-ai-app -n ${NAMESPACE}

# Monitor rollback

kubectl rollout status deployment/project-ai-app -n ${NAMESPACE}
```

### Rollback to Specific Revision

```bash

# View revision history

kubectl rollout history deployment/project-ai-app -n ${NAMESPACE}

# Rollback to specific revision

kubectl rollout undo deployment/project-ai-app \
  -n ${NAMESPACE} \
  --to-revision=3

# Verify rollback

kubectl get deployment project-ai-app -n ${NAMESPACE} -o yaml | grep image:
```

### Automated Rollback

```bash

# Use rollback script (includes database rollback)

./rollback.sh production

# Rollback to specific revision

./rollback.sh production --to-revision=5

# Skip database rollback

./rollback.sh production --skip-database

# Force rollback without confirmation

./rollback.sh production --force
```

### Rollback All Microservices

```bash

# Rollback all governance tier services

for service in mutation-firewall incident-reflex trust-graph data-vault \
               negotiation-agent compliance-engine verifiable-reality; do
  echo "Rolling back ${service}..."
  kubectl rollout undo deployment/${service} -n ${NAMESPACE}
done

# Verify all rollbacks

kubectl get deployments -n ${NAMESPACE} -l tier=governance
```

---

## Health Checks and Monitoring

### Pod Health Status

#### Check Pod Status

```bash

# List all pods

kubectl get pods -n ${NAMESPACE}

# Get detailed pod information

kubectl get pods -n ${NAMESPACE} -o wide

# Watch pod status in real-time

kubectl get pods -n ${NAMESPACE} --watch

# Filter by labels

kubectl get pods -n ${NAMESPACE} -l app.kubernetes.io/name=project-ai
kubectl get pods -n ${NAMESPACE} -l tier=governance
```

#### Check Pod Health

```bash

# Describe pod for events

kubectl describe pod <pod-name> -n ${NAMESPACE}

# Check readiness and liveness probes

kubectl get pod <pod-name> -n ${NAMESPACE} -o json | \
  jq '.status.conditions'

# Check container statuses

kubectl get pod <pod-name> -n ${NAMESPACE} -o json | \
  jq '.status.containerStatuses'
```

#### View Pod Logs

```bash

# View current logs

kubectl logs <pod-name> -n ${NAMESPACE}

# Follow logs in real-time

kubectl logs -f <pod-name> -n ${NAMESPACE}

# View logs from previous container (after crash)

kubectl logs <pod-name> -n ${NAMESPACE} --previous

# View logs from specific container in multi-container pod

kubectl logs <pod-name> -c project-ai -n ${NAMESPACE}

# Tail last 100 lines

kubectl logs <pod-name> -n ${NAMESPACE} --tail=100

# View logs from all pods in deployment

kubectl logs -l app.kubernetes.io/name=project-ai -n ${NAMESPACE} --tail=50
```

### Service Health

#### Test Service Endpoints

```bash

# List services

kubectl get svc -n ${NAMESPACE}

# Describe service

kubectl describe svc project-ai -n ${NAMESPACE}

# Test service from within cluster

kubectl run -it --rm debug \
  --image=curlimages/curl \
  --restart=Never \
  -n ${NAMESPACE} -- \
  curl http://project-ai.${NAMESPACE}.svc.cluster.local:8000/health

# Port-forward to test locally

kubectl port-forward svc/project-ai 8000:8000 -n ${NAMESPACE}

# Then: curl http://localhost:8000/health

```

#### Test Microservices Health

```bash

# Test all microservices

services=(
  "mutation-firewall:8000"
  "incident-reflex:8000"
  "trust-graph:8000"
  "data-vault:8000"
  "negotiation-agent:8000"
  "compliance-engine:8000"
  "verifiable-reality:8000"
)

for service_port in "${services[@]}"; do
  IFS=':' read -r service port <<< "$service_port"
  echo "Testing ${service}..."
  kubectl run -it --rm test-${service} \
    --image=curlimages/curl \
    --restart=Never \
    -n ${NAMESPACE} -- \
    curl -s http://${service}.${NAMESPACE}.svc.cluster.local:${port}/api/v1/health/liveness
done
```

### Resource Monitoring

#### Check Resource Usage

```bash

# Node resource usage

kubectl top nodes

# Pod resource usage

kubectl top pods -n ${NAMESPACE}

# Sort by CPU

kubectl top pods -n ${NAMESPACE} --sort-by=cpu

# Sort by memory

kubectl top pods -n ${NAMESPACE} --sort-by=memory

# Specific pod usage

kubectl top pod <pod-name> -n ${NAMESPACE}
```

#### Check Resource Quotas

```bash

# View resource quotas

kubectl get resourcequota -n ${NAMESPACE}

# Describe quota details

kubectl describe resourcequota -n ${NAMESPACE}

# Check limit ranges

kubectl get limitrange -n ${NAMESPACE}
kubectl describe limitrange -n ${NAMESPACE}
```

#### Monitor Metrics

```bash

# Access Prometheus (port-forward)

kubectl port-forward -n ${NAMESPACE} svc/prometheus 9090:9090

# Access Grafana (port-forward)

kubectl port-forward -n ${NAMESPACE} svc/grafana 3000:3000

# Query metrics via Prometheus API

curl "http://localhost:9090/api/v1/query?query=up"

# Check all Prometheus targets

curl "http://localhost:9090/api/v1/targets" | jq .
```

---

## Configuration Management

### ConfigMap Operations

#### View ConfigMaps

```bash

# List all ConfigMaps

kubectl get configmap -n ${NAMESPACE}

# View ConfigMap content

kubectl get configmap project-ai-config -n ${NAMESPACE} -o yaml

# Get specific key

kubectl get configmap project-ai-config -n ${NAMESPACE} \
  -o jsonpath='{.data.LOG_LEVEL}'
```

#### Update ConfigMap

```bash

# Edit interactively

kubectl edit configmap project-ai-config -n ${NAMESPACE}

# Update from file

kubectl create configmap project-ai-config \
  --from-file=config/ \
  --dry-run=client -o yaml | \
  kubectl apply -n ${NAMESPACE} -f -

# Patch specific key

kubectl patch configmap project-ai-config -n ${NAMESPACE} --patch '
data:
  LOG_LEVEL: "DEBUG"
'

# Restart pods to pick up changes

kubectl rollout restart deployment/project-ai-app -n ${NAMESPACE}
```

### Secret Management

#### View Secrets (without exposing values)

```bash

# List secrets

kubectl get secrets -n ${NAMESPACE}

# Describe secret (doesn't show values)

kubectl describe secret project-ai-secrets -n ${NAMESPACE}

# Get secret keys only

kubectl get secret project-ai-secrets -n ${NAMESPACE} -o jsonpath='{.data}' | jq 'keys'
```

#### Update Secrets

```bash

# Create secret from environment file

kubectl create secret generic project-ai-secrets \
  --from-env-file=.env.production \
  --dry-run=client -o yaml | \
  kubectl apply -n ${NAMESPACE} -f -

# Update specific secret value

kubectl patch secret project-ai-secrets -n ${NAMESPACE} --patch "
data:
  API_KEY: $(echo -n 'new-secret-value' | base64)
"

# Rotate all secrets (use emergency script)

./emergency-rotate-secrets.sh
```

#### Decode Secret Values (with caution)

```bash

# View decoded secret (use with caution!)

kubectl get secret project-ai-secrets -n ${NAMESPACE} -o json | \
  jq '.data | map_values(@base64d)'

# Get specific key decoded

kubectl get secret project-ai-secrets -n ${NAMESPACE} \
  -o jsonpath='{.data.API_KEY}' | base64 -d
```

---

## Database Operations

### PostgreSQL Management

#### Check Database Pods

```bash

# Get database pods

kubectl get pods -n ${NAMESPACE} -l app=postgres

# Check database logs

kubectl logs -l app=postgres -n ${NAMESPACE} --tail=100

# Describe database pod

kubectl describe pod -l app=postgres -n ${NAMESPACE}
```

#### Connect to Database

```bash

# Connect to primary database

kubectl exec -it -n ${NAMESPACE} \
  $(kubectl get pod -n ${NAMESPACE} -l app=postgres,role=primary -o jsonpath='{.items[0].metadata.name}') \
  -- psql -U temporal -d temporal

# Connect to read replica

kubectl exec -it -n ${NAMESPACE} \
  $(kubectl get pod -n ${NAMESPACE} -l app=postgres,role=replica -o jsonpath='{.items[0].metadata.name}') \
  -- psql -U temporal -d temporal
```

#### Database Migrations

```bash

# Run migrations

kubectl exec -it deployment/project-ai-app -n ${NAMESPACE} -- \
  python -m alembic upgrade head

# Check current migration version

kubectl exec -it deployment/project-ai-app -n ${NAMESPACE} -- \
  python -m alembic current

# View migration history

kubectl exec -it deployment/project-ai-app -n ${NAMESPACE} -- \
  python -m alembic history

# Rollback one migration

kubectl exec -it deployment/project-ai-app -n ${NAMESPACE} -- \
  python -m alembic downgrade -1
```

#### Database Backups

```bash

# Trigger manual backup

kubectl create job --from=cronjob/postgres-backup backup-manual -n ${NAMESPACE}

# Check backup status

kubectl get job backup-manual -n ${NAMESPACE}
kubectl logs job/backup-manual -n ${NAMESPACE}

# List backup CronJobs

kubectl get cronjob -n ${NAMESPACE}

# View backup schedule

kubectl describe cronjob postgres-backup -n ${NAMESPACE}
```

### Redis Management

#### Check Redis Status

```bash

# Get Redis pods

kubectl get pods -n ${NAMESPACE} -l app=redis

# Check Redis master

kubectl exec -it -n ${NAMESPACE} \
  $(kubectl get pod -n ${NAMESPACE} -l app=redis,role=master -o jsonpath='{.items[0].metadata.name}') \
  -- redis-cli INFO replication

# Check Redis Sentinel

kubectl get pods -n ${NAMESPACE} -l app=redis-sentinel
kubectl logs -l app=redis-sentinel -n ${NAMESPACE}
```

#### Redis Operations

```bash

# Connect to Redis CLI

kubectl exec -it -n ${NAMESPACE} \
  $(kubectl get pod -n ${NAMESPACE} -l app=redis,role=master -o jsonpath='{.items[0].metadata.name}') \
  -- redis-cli

# Test Redis connectivity

kubectl run -it --rm redis-test \
  --image=redis:7 \
  --restart=Never \
  -n ${NAMESPACE} -- \
  redis-cli -h redis.${NAMESPACE}.svc.cluster.local PING
```

---

## Network Operations

### Ingress Management

#### Check Ingress Status

```bash

# List ingresses

kubectl get ingress -n ${NAMESPACE}

# Describe ingress

kubectl describe ingress project-ai-ingress -n ${NAMESPACE}

# Get ingress external IP/hostname

kubectl get ingress project-ai-ingress -n ${NAMESPACE} \
  -o jsonpath='{.status.loadBalancer.ingress[0].hostname}'
```

#### Update Ingress

```bash

# Edit ingress rules

kubectl edit ingress project-ai-ingress -n ${NAMESPACE}

# Add TLS certificate

kubectl patch ingress project-ai-ingress -n ${NAMESPACE} --patch '
spec:
  tls:

  - hosts:
    - api.project-ai.com
    secretName: tls-secret

'
```

### Network Policies

#### View Network Policies

```bash

# List network policies

kubectl get networkpolicy -n ${NAMESPACE}

# Describe policy

kubectl describe networkpolicy allow-ingress -n ${NAMESPACE}
```

#### Test Network Connectivity

```bash

# Test pod-to-pod connectivity

kubectl run -it --rm nettest \
  --image=nicolaka/netshoot \
  --restart=Never \
  -n ${NAMESPACE} -- \
  curl http://incident-reflex.${NAMESPACE}.svc.cluster.local:8000/health

# Test external connectivity

kubectl run -it --rm nettest \
  --image=nicolaka/netshoot \
  --restart=Never \
  -n ${NAMESPACE} -- \
  curl https://api.openai.com/v1/models
```

---

## Troubleshooting

### Pod Issues

#### Pod Stuck in Pending

```bash

# Check pod events

kubectl describe pod <pod-name> -n ${NAMESPACE}

# Common causes:

# 1. Insufficient resources

kubectl describe nodes | grep -A 5 "Allocated resources"

# 2. PVC not bound

kubectl get pvc -n ${NAMESPACE}

# 3. Image pull errors

kubectl get events -n ${NAMESPACE} | grep "Failed to pull image"

# 4. Node selector/affinity issues

kubectl get pod <pod-name> -n ${NAMESPACE} -o yaml | grep -A 5 nodeSelector
```

#### Pod CrashLoopBackOff

```bash

# View pod logs

kubectl logs <pod-name> -n ${NAMESPACE} --previous

# Check container exit code

kubectl get pod <pod-name> -n ${NAMESPACE} -o jsonpath='{.status.containerStatuses[0].lastState.terminated}'

# Common causes:

# - Application startup errors

# - Missing environment variables

# - Failed health checks

# - OOM kills

# Check OOM kills

kubectl describe pod <pod-name> -n ${NAMESPACE} | grep -i "OOMKilled"
```

#### ImagePullBackOff

```bash

# Check image pull status

kubectl describe pod <pod-name> -n ${NAMESPACE} | grep -A 10 "Events"

# Verify image exists

docker manifest inspect <image>:<tag>

# Check image pull secrets

kubectl get secrets -n ${NAMESPACE} | grep regcred
kubectl describe secret regcred -n ${NAMESPACE}

# Test image pull

kubectl run test-pull --image=<image>:<tag> -n ${NAMESPACE}
```

### Service Discovery Issues

#### Service Not Accessible

```bash

# Verify service exists

kubectl get svc <service-name> -n ${NAMESPACE}

# Check service endpoints

kubectl get endpoints <service-name> -n ${NAMESPACE}

# If endpoints are empty, check pod labels

kubectl get pods -n ${NAMESPACE} --show-labels
kubectl get svc <service-name> -n ${NAMESPACE} -o jsonpath='{.spec.selector}'

# Test DNS resolution

kubectl run -it --rm dnstest \
  --image=busybox \
  --restart=Never \
  -n ${NAMESPACE} -- \
  nslookup <service-name>.${NAMESPACE}.svc.cluster.local
```

### Performance Issues

#### High CPU/Memory Usage

```bash

# Check resource usage

kubectl top pods -n ${NAMESPACE} --sort-by=cpu
kubectl top pods -n ${NAMESPACE} --sort-by=memory

# Check if pods are being OOM killed

kubectl get events -n ${NAMESPACE} | grep "OOMKilled"

# Increase resource limits

kubectl edit deployment/<deployment-name> -n ${NAMESPACE}

# Update resources.limits.memory and resources.limits.cpu

# Enable VPA for recommendations

kubectl apply -f k8s/base/vpa.yaml -n ${NAMESPACE}
```

#### Slow Response Times

```bash

# Check if HPA is scaling

kubectl get hpa -n ${NAMESPACE}

# Check pod readiness

kubectl get pods -n ${NAMESPACE} -o wide

# Check application metrics

kubectl port-forward svc/prometheus 9090:9090 -n ${NAMESPACE}

# Query: rate(http_request_duration_seconds_sum[5m])

# Check database connection pool

kubectl exec -it deployment/project-ai-app -n ${NAMESPACE} -- \
  curl localhost:8000/metrics | grep db_pool
```

---

## Maintenance Tasks

### Cluster Maintenance

#### Drain Node for Maintenance

```bash

# Cordon node (mark unschedulable)

kubectl cordon <node-name>

# Drain node (evict pods)

kubectl drain <node-name> \
  --ignore-daemonsets \
  --delete-emptydir-data \
  --grace-period=300

# Perform maintenance...

# Uncordon node

kubectl uncordon <node-name>
```

#### Clean Up Resources

```bash

# Delete completed jobs

kubectl delete job -n ${NAMESPACE} --field-selector status.successful=1

# Delete evicted pods

kubectl delete pod -n ${NAMESPACE} --field-selector status.phase=Failed

# Delete old ReplicaSets

kubectl delete replicaset -n ${NAMESPACE} \
  $(kubectl get rs -n ${NAMESPACE} -o json | \
    jq -r '.items[] | select(.spec.replicas==0 and .status.replicas==0) | .metadata.name')
```

### Certificate Rotation

#### Rotate TLS Certificates

```bash

# Update TLS secret

kubectl create secret tls tls-secret \
  --cert=path/to/tls.crt \
  --key=path/to/tls.key \
  --dry-run=client -o yaml | \
  kubectl apply -n ${NAMESPACE} -f -

# Restart ingress controller

kubectl rollout restart deployment/nginx-ingress-controller -n ingress-nginx
```

---

## Emergency Procedures

### Complete Service Restart

```bash

# Restart all deployments

kubectl rollout restart deployment -n ${NAMESPACE}

# Wait for all to be ready

kubectl wait --for=condition=available --timeout=600s \
  deployment --all -n ${NAMESPACE}
```

### Emergency Rollback

```bash

# Quick rollback all services

./rollback.sh production --force

# Or manual rollback

for deploy in $(kubectl get deployments -n ${NAMESPACE} -o name); do
  kubectl rollout undo ${deploy} -n ${NAMESPACE}
done
```

### Disaster Recovery

```bash

# 1. Restore from backup

# 2. Restore database

# 3. Redeploy application

kustomize build k8s/overlays/production | kubectl apply -f -

# 4. Verify health

kubectl get pods -n ${NAMESPACE}
./k8s/deploy.sh production test
```

---

**Last Updated**: 2026-04-09  
**Maintained By**: SRE Team  
**Review Frequency**: Quarterly
