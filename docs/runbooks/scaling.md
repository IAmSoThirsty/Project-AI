# Scaling Runbook

## Overview
Procedures for scaling the Sovereign Governance Substrate system to handle increased load or optimize resource usage.

## Scaling Strategies

### Horizontal Pod Autoscaling (HPA)

#### Configure HPA for Workers
```bash
# Create HPA based on CPU utilization
kubectl autoscale deployment temporal-worker \
  --min=3 \
  --max=50 \
  --cpu-percent=70 \
  -n sovereign-governance

# Verify HPA
kubectl get hpa -n sovereign-governance

# View HPA details
kubectl describe hpa temporal-worker -n sovereign-governance
```

#### Configure HPA based on Custom Metrics
```yaml
# hpa-custom-metrics.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: temporal-worker-hpa
  namespace: sovereign-governance
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: temporal-worker
  minReplicas: 3
  maxReplicas: 50
  metrics:
    # CPU-based scaling
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    
    # Memory-based scaling
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
    
    # Custom metric: pending workflows
    - type: Pods
      pods:
        metric:
          name: temporal_pending_workflows
        target:
          type: AverageValue
          averageValue: "10"
    
    # Custom metric: workflow latency
    - type: Pods
      pods:
        metric:
          name: temporal_workflow_latency_p95
        target:
          type: AverageValue
          averageValue: "2000"  # 2 seconds
  
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300  # Wait 5 min before scaling down
      policies:
        - type: Percent
          value: 50  # Scale down max 50% of current replicas
          periodSeconds: 60
        - type: Pods
          value: 2  # Scale down max 2 pods
          periodSeconds: 60
      selectPolicy: Min  # Choose most conservative policy
    
    scaleUp:
      stabilizationWindowSeconds: 0  # Scale up immediately
      policies:
        - type: Percent
          value: 100  # Scale up max 100% of current replicas
          periodSeconds: 15
        - type: Pods
          value: 10  # Scale up max 10 pods
          periodSeconds: 15
      selectPolicy: Max  # Choose most aggressive policy
```

Apply configuration:
```bash
kubectl apply -f hpa-custom-metrics.yaml
```

### Vertical Pod Autoscaling (VPA)

#### Install VPA
```bash
# Install VPA CRDs and components
git clone https://github.com/kubernetes/autoscaler.git
cd autoscaler/vertical-pod-autoscaler
./hack/vpa-up.sh
```

#### Configure VPA
```yaml
# vpa-temporal-worker.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: temporal-worker-vpa
  namespace: sovereign-governance
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: temporal-worker
  
  updatePolicy:
    updateMode: "Auto"  # Auto, Initial, or Off
  
  resourcePolicy:
    containerPolicies:
      - containerName: worker
        minAllowed:
          cpu: 500m
          memory: 512Mi
        maxAllowed:
          cpu: 4
          memory: 8Gi
        controlledResources:
          - cpu
          - memory
```

Apply configuration:
```bash
kubectl apply -f vpa-temporal-worker.yaml

# View VPA recommendations
kubectl describe vpa temporal-worker-vpa -n sovereign-governance
```

### Cluster Autoscaling

#### Configure Cluster Autoscaler (AWS EKS)
```bash
# Deploy cluster autoscaler
kubectl apply -f https://raw.githubusercontent.com/kubernetes/autoscaler/master/cluster-autoscaler/cloudprovider/aws/examples/cluster-autoscaler-autodiscover.yaml

# Configure for your cluster
kubectl -n kube-system edit deployment cluster-autoscaler

# Add these flags:
# --balance-similar-node-groups
# --skip-nodes-with-system-pods=false
# --node-group-auto-discovery=asg:tag=k8s.io/cluster-autoscaler/enabled,k8s.io/cluster-autoscaler/<cluster-name>
```

#### Configure Node Groups
```yaml
# node-group-workers.yaml (AWS example)
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: sovereign-cluster
  region: us-east-1

nodeGroups:
  - name: temporal-workers
    instanceType: m5.2xlarge
    desiredCapacity: 3
    minSize: 3
    maxSize: 20
    
    labels:
      workload: temporal-worker
    
    taints:
      - key: workload
        value: temporal-worker
        effect: NoSchedule
    
    tags:
      k8s.io/cluster-autoscaler/enabled: "true"
      k8s.io/cluster-autoscaler/sovereign-cluster: "owned"
    
    iam:
      withAddonPolicies:
        autoScaler: true
```

## Manual Scaling

### Scale Workers
```bash
# Scale to specific number of replicas
kubectl scale deployment temporal-worker --replicas=10 -n sovereign-governance

# Scale based on current load
CURRENT_LOAD=$(kubectl top pods -n sovereign-governance -l app=temporal-worker | awk '{sum+=$3} END {print int(sum/70)}')
kubectl scale deployment temporal-worker --replicas=$CURRENT_LOAD -n sovereign-governance

# Scale to zero (maintenance mode)
kubectl scale deployment temporal-worker --replicas=0 -n sovereign-governance
```

### Scale Temporal Server
```bash
# Scale frontend service
kubectl scale deployment temporal-frontend --replicas=5 -n temporal

# Scale matching service
kubectl scale deployment temporal-matching --replicas=3 -n temporal

# Scale history service
kubectl scale deployment temporal-history --replicas=5 -n temporal

# Scale worker service
kubectl scale deployment temporal-worker-service --replicas=3 -n temporal
```

### Scale Database

#### Cassandra Scaling
```bash
# Scale Cassandra StatefulSet
kubectl scale statefulset cassandra --replicas=5 -n temporal

# Wait for new nodes to join
kubectl rollout status statefulset/cassandra -n temporal

# Verify cluster status
kubectl exec -it -n temporal cassandra-0 -- nodetool status

# Rebalance data
kubectl exec -it -n temporal cassandra-0 -- nodetool cleanup
```

#### PostgreSQL Scaling (if using)
```bash
# Scale read replicas
kubectl scale statefulset postgres-replica --replicas=3 -n temporal

# Promote replica to primary (failover)
kubectl exec -it -n temporal postgres-replica-0 -- \
  pg_ctl promote -D /var/lib/postgresql/data
```

## Scaling Scenarios

### Scenario 1: Anticipated Traffic Spike

**Preparation (1-2 hours before):**
```bash
# 1. Scale workers proactively
kubectl scale deployment temporal-worker --replicas=20 -n sovereign-governance

# 2. Scale Temporal services
kubectl scale deployment temporal-frontend --replicas=10 -n temporal
kubectl scale deployment temporal-history --replicas=10 -n temporal

# 3. Verify cluster capacity
kubectl top nodes
kubectl describe nodes | grep -A 5 "Allocated resources"

# 4. Add cluster nodes if needed (AWS)
eksctl scale nodegroup --cluster=sovereign-cluster \
  --name=temporal-workers --nodes=10

# 5. Verify scaling
kubectl get pods -n sovereign-governance -o wide
kubectl get nodes -o wide

# 6. Monitor during event
watch -n 5 'kubectl top pods -n sovereign-governance'
```

**Post-event (after traffic normalizes):**
```bash
# Scale back down gradually
kubectl scale deployment temporal-worker --replicas=10 -n sovereign-governance
sleep 300  # Wait 5 minutes
kubectl scale deployment temporal-worker --replicas=5 -n sovereign-governance

# Remove extra nodes
eksctl scale nodegroup --cluster=sovereign-cluster \
  --name=temporal-workers --nodes=5
```

### Scenario 2: Gradual Load Increase

**Monitor and scale incrementally:**
```bash
# Check current utilization
kubectl top pods -n sovereign-governance
kubectl top nodes

# Calculate needed replicas based on CPU
CURRENT_REPLICAS=$(kubectl get deployment temporal-worker -n sovereign-governance -o jsonpath='{.spec.replicas}')
AVG_CPU=$(kubectl top pods -n sovereign-governance -l app=temporal-worker | awk 'NR>1 {sum+=$3; count++} END {print int(sum/count)}')
TARGET_CPU=70
NEEDED_REPLICAS=$(echo "scale=0; $CURRENT_REPLICAS * $AVG_CPU / $TARGET_CPU" | bc)

echo "Current: $CURRENT_REPLICAS, Needed: $NEEDED_REPLICAS"

# Scale to calculated replicas
kubectl scale deployment temporal-worker --replicas=$NEEDED_REPLICAS -n sovereign-governance
```

### Scenario 3: Resource Optimization (Cost Reduction)

**Identify over-provisioned resources:**
```bash
# Install and use kubectl-resource-capacity
kubectl resource-capacity --pods --util

# Analyze VPA recommendations
kubectl get vpa temporal-worker-vpa -n sovereign-governance -o yaml

# Check actual vs requested resources
kubectl top pods -n sovereign-governance
kubectl describe deployment temporal-worker -n sovereign-governance | grep -A 5 resources:

# Right-size based on data
kubectl set resources deployment temporal-worker -n sovereign-governance \
  --limits=cpu=2,memory=4Gi \
  --requests=cpu=1,memory=2Gi
```

### Scenario 4: Emergency Scale-down

**When cluster resources are critically low:**
```bash
# 1. Identify non-critical workloads
kubectl get deployments -A --sort-by=.metadata.creationTimestamp

# 2. Scale down non-critical services
kubectl scale deployment <non-critical-app> --replicas=1 -n <namespace>

# 3. Drain specific nodes for maintenance
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# 4. Cordon nodes to prevent new pods
kubectl cordon <node-name>

# 5. After recovery, uncordon
kubectl uncordon <node-name>
```

## Monitoring Scaling Operations

### Key Metrics to Watch

```bash
# Watch HPA status
watch -n 5 'kubectl get hpa -A'

# Watch pod scaling
watch -n 5 'kubectl get pods -n sovereign-governance -l app=temporal-worker'

# Monitor resource usage
watch -n 5 'kubectl top pods -n sovereign-governance'
watch -n 5 'kubectl top nodes'

# Check for pending pods (need more capacity)
kubectl get pods -A --field-selector=status.phase=Pending

# Check for evicted pods (resource pressure)
kubectl get pods -A --field-selector=status.phase=Failed | grep Evicted
```

### Prometheus Queries for Scaling

```promql
# Pod count over time
count(kube_pod_info{namespace="sovereign-governance"})

# CPU utilization
avg(rate(container_cpu_usage_seconds_total{namespace="sovereign-governance"}[5m]))

# Memory utilization
avg(container_memory_working_set_bytes{namespace="sovereign-governance"})

# Pending workflows
temporal_pending_workflows{namespace="default"}

# Workflow execution rate
rate(temporal_workflow_completed_total[5m])

# Queue depth
temporal_task_queue_depth{task_queue="default"}
```

### Grafana Dashboard Queries

Create dashboard with these panels:
1. Worker pod count (last 24h)
2. CPU/Memory utilization
3. Workflow execution rate
4. Queue depth
5. P95/P99 latency
6. Error rate

## Scaling Best Practices

### Do's
✅ **Scale gradually**: Increase/decrease by 20-50% increments
✅ **Monitor after scaling**: Watch for 15-30 minutes
✅ **Use HPA for predictable patterns**: Let automation handle it
✅ **Document capacity planning**: Track peak loads and scaling needs
✅ **Test scaling procedures**: Regular drills in staging
✅ **Set resource limits**: Prevent runaway consumption

### Don'ts
❌ **Don't scale too aggressively**: Can cause instability
❌ **Don't ignore pending pods**: Indicates insufficient capacity
❌ **Don't forget to scale database**: Application scaling is useless without it
❌ **Don't scale during incidents**: Unless directly related to capacity
❌ **Don't forget cost implications**: Monitor cloud spending

## Capacity Planning

### Calculate Required Capacity

```python
# capacity_calculator.py
def calculate_worker_capacity(
    workflows_per_second: float,
    avg_workflow_duration_sec: float,
    workflows_per_worker: int = 10,
    overhead_factor: float = 1.5  # 50% overhead
):
    concurrent_workflows = workflows_per_second * avg_workflow_duration_sec
    required_workers = (concurrent_workflows / workflows_per_worker) * overhead_factor
    return int(required_workers) + 1  # Round up

# Example
wps = 100  # 100 workflows/sec
duration = 5  # 5 seconds average
workers_needed = calculate_worker_capacity(wps, duration)
print(f"Workers needed: {workers_needed}")
```

### Sizing Guidelines

| Load Level | Workflows/sec | Workers | Frontend | History | Database |
|------------|---------------|---------|----------|---------|----------|
| Low        | < 10          | 3       | 2        | 2       | 3        |
| Medium     | 10-100        | 10      | 5        | 5       | 5        |
| High       | 100-1000      | 50      | 10       | 10      | 9        |
| Very High  | 1000+         | 100+    | 20       | 20      | 15       |

## Troubleshooting Scaling Issues

### HPA Not Scaling

```bash
# Check metrics availability
kubectl get apiservice v1beta1.metrics.k8s.io -o yaml

# Verify metrics server
kubectl get deployment metrics-server -n kube-system

# Check HPA events
kubectl describe hpa temporal-worker-hpa -n sovereign-governance

# View current metrics
kubectl get hpa temporal-worker-hpa -n sovereign-governance -o yaml
```

### Pods Pending After Scale-up

```bash
# Check why pods are pending
kubectl describe pod <pending-pod> -n sovereign-governance

# Common causes:
# 1. Insufficient node capacity
kubectl get nodes -o wide
kubectl describe nodes | grep -A 5 "Allocated resources"

# 2. Pod affinity/anti-affinity rules
kubectl get pod <pending-pod> -n sovereign-governance -o yaml | grep -A 10 affinity

# 3. Taints/tolerations
kubectl get nodes -o custom-columns=NAME:.metadata.name,TAINTS:.spec.taints

# Solution: Add more nodes or adjust pod requirements
```

## Revision History

- 2026-04-11: Initial version
