# 03: Kubernetes Orchestration Relationships

**Document**: Kubernetes Deployment and Service Relationships  
**System**: K8s Deployments, Helm Charts, Auto-Scaling, Service Mesh  
**Related Systems**: Docker, Monitoring, Health Checks, Rollback Procedures

---


## Navigation

**Location**: `relationships\deployment\03_kubernetes_orchestration.md`

**Parent**: [[relationships\deployment\README.md]]


## Kubernetes Architecture

```
┌──────────────────────────────────────────────────────────┐
│              KUBERNETES ORCHESTRATION                     │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────────────────────────────────────┐         │
│  │         Helm Chart (project-ai)             │         │
│  │                                             │         │
│  │  • Chart.yaml (metadata)                   │         │
│  │  • values.yaml (configuration)             │         │
│  │  • templates/ (K8s manifests)              │         │
│  └────────────┬────────────────────────────────┘         │
│               │                                           │
│               ↓                                           │
│  ┌─────────────────────────────────────────────┐         │
│  │         helm install project-ai             │         │
│  └────────────┬────────────────────────────────┘         │
│               │                                           │
│               ↓                                           │
│  ┌─────────────────────────────────────────────┐         │
│  │       Kubernetes Resources Created          │         │
│  │                                             │         │
│  │  ┌──────────────┐  ┌──────────────┐        │         │
│  │  │ Deployment   │  │ StatefulSet  │        │         │
│  │  │ (Stateless)  │  │ (Stateful)   │        │         │
│  │  └──────┬───────┘  └──────┬───────┘        │         │
│  │         │                 │                 │         │
│  │         ↓                 ↓                 │         │
│  │  ┌──────────────┐  ┌──────────────┐        │         │
│  │  │ ReplicaSet   │  │ PVC          │        │         │
│  │  └──────┬───────┘  └──────┬───────┘        │         │
│  │         │                 │                 │         │
│  │         ↓                 ↓                 │         │
│  │  ┌──────────────────────────────┐          │         │
│  │  │        Pods (3 replicas)     │          │         │
│  │  │                              │          │         │
│  │  │  ┌───────┐  ┌───────┐  ┌───┐│          │         │
│  │  │  │ Pod 1 │  │ Pod 2 │  │Pod││          │         │
│  │  │  │       │  │       │  │ 3 ││          │         │
│  │  │  └───────┘  └───────┘  └───┘│          │         │
│  │  └──────────────┬───────────────┘          │         │
│  │                 │                           │         │
│  │                 ↓                           │         │
│  │  ┌──────────────────────────────┐          │         │
│  │  │         Service              │          │         │
│  │  │  (ClusterIP / LoadBalancer)  │          │         │
│  │  └──────────────┬───────────────┘          │         │
│  │                 │                           │         │
│  │                 ↓                           │         │
│  │  ┌──────────────────────────────┐          │         │
│  │  │         Ingress              │          │         │
│  │  │  (TLS + Routing)             │          │         │
│  │  └──────────────┬───────────────┘          │         │
│  └─────────────────┼─────────────────────────┘          │
│                    │                                     │
│                    ↓                                     │
│              External Traffic                            │
│                                                           │
└──────────────────────────────────────────────────────────┘
```

## Resource Dependency Chain

### Deployment → Pod Creation
```
Helm Chart Installation
    ↓ generates
Deployment Manifest
    ↓ creates
ReplicaSet (hash-based)
    ↓ spawns
Pods (desired: 3)
    ├─→ Pod 1 (node-1)
    ├─→ Pod 2 (node-2)
    └─→ Pod 3 (node-3)
        ↓ pull
        Container Image
        ↓ mount
        ConfigMap + Secret
        ↓ start
        Application Container
        ↓ expose
        Port 8000 (containerPort)
```

### Service Discovery
```
Service Definition
    ↓ selector: app=project-ai
Matches Pods
    ↓ creates
Endpoints Object
    ├─→ 10.0.1.5:8000 (Pod 1)
    ├─→ 10.0.1.6:8000 (Pod 2)
    └─→ 10.0.1.7:8000 (Pod 3)
        ↓ load balances
        Round-Robin / Least Connections
        ↓ provides
        ClusterIP: 10.96.0.10:80
        ↓ DNS: project-ai.default.svc.cluster.local
```

## Helm Chart Relationships

### Chart Structure
```
helm/project-ai/
├── Chart.yaml
│   ├─ name: project-ai
│   ├─ version: 1.0.0
│   └─ dependencies:
│       └─ postgresql: 12.0.0
├── values.yaml
│   ├─ replicaCount: 3
│   ├─ image:
│   │   ├─ repository: projectai/backend
│   │   └─ tag: "1.0.0"
│   ├─ resources:
│   │   ├─ requests: {cpu: 100m, memory: 128Mi}
│   │   └─ limits: {cpu: 500m, memory: 512Mi}
│   └─ autoscaling:
│       ├─ enabled: true
│       ├─ minReplicas: 3
│       └─ maxReplicas: 10
└── templates/
    ├── deployment.yaml
    ├── service.yaml
    ├── ingress.yaml
    ├── configmap.yaml
    ├── secret.yaml
    ├── hpa.yaml
    ├── pdb.yaml
    └── _helpers.tpl
```

### Values Override Cascade
```
Chart defaults (values.yaml)
    ↓ override
Environment-specific (values-prod.yaml)
    ↓ override
Command-line (--set image.tag=1.0.1)
    ↓ final
Rendered Manifest
    ↓ applied
Kubernetes Cluster
```

## Auto-Scaling Relationships

### Horizontal Pod Autoscaler (HPA)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: project-ai-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: project-ai
  minReplicas: 3
  maxReplicas: 10
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
```

### HPA Decision Flow
```
Metrics Server
    ↓ scrapes every 15s
Pod Resource Usage
    ↓ aggregates
Average CPU: 75% (target: 70%)
    ↓ triggers
HPA Controller
    ↓ calculates
Desired Replicas = ceil(3 * 75/70) = 4
    ↓ updates
Deployment.spec.replicas = 4
    ↓ creates
New Pod (Pod 4)
    ↓ waits
Stabilization Window (5 min)
    ↓ if still high
Scale Again (Pod 5)
```

### Vertical Pod Autoscaler (VPA)
```
VPA Controller
    ↓ analyzes
Historical Resource Usage
    ↓ recommends
CPU: 200m → 300m
Memory: 256Mi → 384Mi
    ↓ applies (if updateMode: Auto)
Pod Restart with New Limits
    ↓ monitors
New Performance
    ↓ adjusts
Recommendations
```

### Cluster Autoscaler
```
HPA scales to maxReplicas
    ↓ pending pods
Insufficient Node Capacity
    ↓ triggers
Cluster Autoscaler
    ↓ requests
Cloud Provider API (AWS/Azure/GCP)
    ↓ provisions
New Node
    ↓ joins
Kubernetes Cluster
    ↓ schedules
Pending Pods
```

## ConfigMap and Secret Management

### Configuration Propagation
```
Configuration Source
    ├─→ .env files (development)
    ├─→ CI/CD secrets (GitHub)
    └─→ HashiCorp Vault (production)
        ↓ converted to
        K8s ConfigMap/Secret
        ↓ mounted as
        Pod Volume (/etc/config)
        ↓ or injected as
        Environment Variables
        ↓ read by
        Application Code
```

### ConfigMap Example
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: project-ai-config
data:
  APP_ENV: "production"
  LOG_LEVEL: "info"
  DATABASE_HOST: "postgresql.default.svc.cluster.local"
  DATABASE_PORT: "5432"
  REDIS_URL: "redis://redis:6379/0"
```

### Secret Example (Opaque)
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: project-ai-secrets
type: Opaque
data:
  DATABASE_PASSWORD: <base64-encoded>
  OPENAI_API_KEY: <base64-encoded>
  FERNET_KEY: <base64-encoded>
  JWT_SECRET_KEY: <base64-encoded>
```

### Volume Mount Relationship
```yaml
# In Deployment spec:
spec:
  containers:
  - name: backend
    volumeMounts:
    - name: config
      mountPath: /etc/config
      readOnly: true
    - name: secrets
      mountPath: /etc/secrets
      readOnly: true
  volumes:
  - name: config
    configMap:
      name: project-ai-config
  - name: secrets
    secret:
      secretName: project-ai-secrets
```

## Service Mesh Integration

### Istio Relationships
```
Istio Control Plane (istiod)
    ↓ injects
Envoy Sidecar Proxy
    ↓ intercepts
Pod Network Traffic
    ├─→ Inbound (from other services)
    └─→ Outbound (to other services)
        ↓ applies
        Traffic Policies:
        ├─ mTLS Encryption
        ├─ Circuit Breaking
        ├─ Retries (3x)
        └─ Timeout (10s)
            ↓ reports
            Metrics to Prometheus
```

### VirtualService (Traffic Routing)
```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: project-ai-routing
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
      weight: 90
    - destination:
        host: project-ai
        subset: canary
      weight: 10
```

## Pod Disruption Budget (PDB)

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: project-ai-pdb
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: project-ai
```

### PDB Protection Flow
```
Node Maintenance Initiated
    ↓ kubelet drains node
Eviction API Called
    ↓ PDB checks
Available Pods: 3
MinAvailable: 2
    ├─→ Can evict 1 pod (3 - 1 >= 2)
    │   ↓ evicts
    │   Pod 3
    │   ↓ reschedules
    │   New Pod on different node
    └─→ Cannot evict (would violate PDB)
        ↓ blocks
        Eviction Request
        ↓ retries
        After Pod Rescheduled
```

## Ingress and TLS

### Ingress Relationships
```
External Request (HTTPS)
    ↓ DNS resolves
    project-ai.example.com → LoadBalancer IP
    ↓ routes to
    Ingress Controller (Nginx)
    ↓ TLS termination
    Certificate from cert-manager
    ↓ matches
    Ingress Rule (host + path)
    ↓ forwards to
    Service: project-ai:80
    ↓ load balances to
    Pod Endpoints:8000
```

### cert-manager Integration
```
Ingress with TLS annotation
    ↓ triggers
cert-manager
    ↓ creates
Certificate Request
    ↓ ACME challenge
Let's Encrypt
    ↓ validates
Domain Ownership
    ↓ issues
TLS Certificate
    ↓ stores in
Secret: project-ai-tls
    ↓ mounted by
Ingress Controller
    ↓ serves
HTTPS Traffic
```

## StatefulSet for Stateful Services

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgresql
spec:
  serviceName: postgresql
  replicas: 3
  selector:
    matchLabels:
      app: postgresql
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```

### StatefulSet Pod Identity
```
StatefulSet: postgresql
    ↓ creates
Pods with Stable Identity:
    ├─→ postgresql-0 (PVC: data-postgresql-0)
    ├─→ postgresql-1 (PVC: data-postgresql-1)
    └─→ postgresql-2 (PVC: data-postgresql-2)
        ↓ DNS records
        postgresql-0.postgresql.default.svc.cluster.local
        postgresql-1.postgresql.default.svc.cluster.local
        postgresql-2.postgresql.default.svc.cluster.local
            ↓ survives
            Pod Rescheduling (identity preserved)
```

## Rolling Update Strategy

```yaml
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
```

### Rolling Update Flow
```
Desired State: image: v1.0.1 (current: v1.0.0)
    ↓ calculates
Replicas: 3
MaxUnavailable: 1 (min available: 2)
MaxSurge: 1 (max total: 4)

Step 1: Create new Pod (v1.0.1)
  Total: 4 (3 old + 1 new)
  Available: 3 old
  ↓ wait for ready
Step 2: Terminate 1 old Pod
  Total: 3 (2 old + 1 new)
  Available: 3
  ↓ repeat
Step 3-4: Create new, terminate old
  ↓ until
All Pods running v1.0.1
  Total: 3 (all new)
  Available: 3
```

## Node Affinity and Taints

### Node Selection
```yaml
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: kubernetes.io/arch
            operator: In
            values:
            - amd64
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        preference:
          matchExpressions:
          - key: node-type
            operator: In
            values:
            - high-memory
```

### Scheduling Flow
```
Pod Created
    ↓ evaluates
Node Affinity Rules
    ↓ filters nodes
Required: arch=amd64
    ↓ available nodes
    [node-1, node-2, node-3]
    ↓ scores
Preferred: node-type=high-memory
    ↓ weights
    node-1: 100 (has high-memory)
    node-2: 0
    node-3: 0
    ↓ selects
    node-1 (highest score)
    ↓ schedules
    Pod on node-1
```

## Monitoring Integration

### Prometheus ServiceMonitor
```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: project-ai-metrics
spec:
  selector:
    matchLabels:
      app: project-ai
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

### Metrics Scraping Flow
```
Prometheus Operator
    ↓ discovers
ServiceMonitor CRD
    ↓ configures
Prometheus to scrape
    ↓ every 30s
Service Endpoint: project-ai:9090/metrics
    ↓ queries
Pod Metrics Endpoint
    ↓ returns
Prometheus Metrics:
    - http_requests_total
    - http_request_duration_seconds
    - pod_cpu_usage_seconds_total
    ↓ stores in
Prometheus TSDB
    ↓ visualized in
Grafana Dashboard
```

## Related Systems

- `02_docker_relationships.md` - Container images
- `07_health_monitoring_hooks.md` - K8s probes
- `08_rollback_procedures.md` - K8s rollout undo
- `10_deployment_pipeline_maps.md` - Full deployment flow

---

**Status**: ✅ Complete  
**Coverage**: Deployments, Helm, Auto-Scaling, Service Mesh, Ingress
