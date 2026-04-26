# Kubernetes Deployment and Orchestration

## Overview

Project-AI supports Kubernetes deployment for production-scale orchestration, auto-scaling, service mesh integration, and high availability. This document covers Helm charts, deployment manifests, scaling strategies, and production Kubernetes patterns.

## Kubernetes Architecture

### Cluster Architecture

```
Project-AI Kubernetes Cluster/
├── Namespaces
│   ├── project-ai-prod (production)
│   ├── project-ai-staging (staging)
│   └── project-ai-dev (development)
├── Control Plane
│   ├── API Server
│   ├── Scheduler
│   ├── Controller Manager
│   └── etcd (cluster state)
├── Worker Nodes
│   ├── Node 1 (CPU-optimized)
│   ├── Node 2 (Memory-optimized)
│   └── Node 3 (GPU-enabled, for image generation)
└── Add-ons
    ├── Ingress Controller (NGINX)
    ├── Service Mesh (Istio)
    ├── Monitoring (Prometheus + Grafana)
    ├── Logging (Fluentd + Elasticsearch)
    └── Cert-Manager (TLS automation)
```

### Resource Topology

```yaml
project-ai Deployment/
├── Deployments
│   ├── backend-deployment (Flask API)
│   ├── frontend-deployment (React)
│   ├── worker-deployment (Celery workers)
│   └── cerberus-deployment (AI orchestrator)
├── Services
│   ├── backend-service (ClusterIP)
│   ├── frontend-service (ClusterIP)
│   └── ingress (external access)
├── ConfigMaps
│   ├── app-config
│   └── ai-config
├── Secrets
│   ├── api-keys
│   ├── database-credentials
│   └── tls-certificates
├── PersistentVolumeClaims
│   ├── data-pvc (user data)
│   ├── models-pvc (AI models)
│   └── logs-pvc (application logs)
└── HorizontalPodAutoscalers
    ├── backend-hpa
    └── worker-hpa
```

## Base Manifests

### Namespace

**File**: `k8s/base/namespace.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: project-ai-prod
  labels:
    name: project-ai-prod
    environment: production
```

### Backend Deployment

**File**: `k8s/base/backend-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: project-ai-prod
  labels:
    app: project-ai
    component: backend
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: project-ai
      component: backend
  template:
    metadata:
      labels:
        app: project-ai
        component: backend
        version: v1.0.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: project-ai-backend
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault
      
      initContainers:
      - name: init-db
        image: busybox:1.35
        command: ['sh', '-c', 'until nc -z postgres-service 5432; do echo waiting for db; sleep 2; done']
      
      containers:
      - name: backend
        image: projectai/backend:v1.0.0
        imagePullPolicy: IfNotPresent
        
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        
        env:
        - name: APP_ENV
          value: "production"
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: app-config
              key: LOG_LEVEL
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
        - name: REDIS_URL
          value: "redis://redis-service:6379/0"
        
        envFrom:
        - configMapRef:
            name: app-config
        - secretRef:
            name: api-keys
        
        volumeMounts:
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
        - name: config
          mountPath: /app/config
          readOnly: true
        - name: tmp
          mountPath: /tmp
        
        resources:
          requests:
            cpu: 500m
            memory: 512Mi
          limits:
            cpu: 2000m
            memory: 2Gi
        
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
            - ALL
      
      volumes:
      - name: data
        persistentVolumeClaim:
          claimName: project-ai-data
      - name: logs
        persistentVolumeClaim:
          claimName: project-ai-logs
      - name: config
        configMap:
          name: app-config
      - name: tmp
        emptyDir: {}
      
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - project-ai
                - key: component
                  operator: In
                  values:
                  - backend
              topologyKey: kubernetes.io/hostname
```

### Backend Service

**File**: `k8s/base/backend-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: project-ai-prod
  labels:
    app: project-ai
    component: backend
spec:
  type: ClusterIP
  selector:
    app: project-ai
    component: backend
  ports:
  - name: http
    port: 80
    targetPort: 8000
    protocol: TCP
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 3600
```

### Frontend Deployment

**File**: `k8s/base/frontend-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: project-ai-prod
spec:
  replicas: 2
  selector:
    matchLabels:
      app: project-ai
      component: frontend
  template:
    metadata:
      labels:
        app: project-ai
        component: frontend
    spec:
      containers:
      - name: frontend
        image: projectai/frontend:v1.0.0
        ports:
        - containerPort: 80
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Frontend Service

**File**: `k8s/base/frontend-service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: project-ai-prod
spec:
  type: ClusterIP
  selector:
    app: project-ai
    component: frontend
  ports:
  - port: 80
    targetPort: 80
```

## Ingress and TLS

### Ingress Controller

**File**: `k8s/base/ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: project-ai-ingress
  namespace: project-ai-prod
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/limit-rps: "10"
    nginx.ingress.kubernetes.io/limit-connections: "20"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
spec:
  tls:
  - hosts:
    - projectai.com
    - www.projectai.com
    - api.projectai.com
    secretName: project-ai-tls
  rules:
  # Frontend
  - host: projectai.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
  - host: www.projectai.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
  # API
  - host: api.projectai.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 80
```

### Cert-Manager (TLS Automation)

**Cluster Issuer** (`k8s/base/cert-issuer.yaml`):

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@projectai.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

## ConfigMaps and Secrets

### Application ConfigMap

**File**: `k8s/base/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: project-ai-prod
data:
  # Application settings
  APP_NAME: "Project AI"
  APP_VERSION: "1.0.0"
  LOG_LEVEL: "INFO"
  
  # Feature flags
  ENABLE_IMAGE_GENERATION: "true"
  ENABLE_LEARNING_REQUESTS: "true"
  ENABLE_LOCATION_TRACKING: "false"
  
  # Rate limiting
  RATE_LIMIT_PER_MINUTE: "30"
  RATE_LIMIT_PER_HOUR: "500"
  
  # CORS
  CORS_ORIGINS: "https://projectai.com,https://www.projectai.com"
```

### Secrets

**File**: `k8s/base/secrets.yaml` (managed via sealed-secrets or external secrets operator)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
  namespace: project-ai-prod
type: Opaque
stringData:
  openai: "sk-..."
  huggingface: "hf_..."
  fernet-key: "..."
  secret-key: "..."
  jwt-secret: "..."

---
apiVersion: v1
kind: Secret
metadata:
  name: database-credentials
  namespace: project-ai-prod
type: Opaque
stringData:
  url: "postgresql://user:pass@postgres-service:5432/legion_web"
  username: "produser"
  password: "..."
```

**Using Sealed Secrets** (encrypted secrets in Git):

```bash
# Install sealed-secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# Seal a secret
kubeseal -f secrets.yaml -w sealed-secrets.yaml

# Apply sealed secret (safe to commit)
kubectl apply -f sealed-secrets.yaml
```

## Persistent Storage

### PersistentVolumeClaim

**File**: `k8s/base/pvc.yaml`

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: project-ai-data
  namespace: project-ai-prod
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 50Gi

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: project-ai-logs
  namespace: project-ai-prod
spec:
  accessModes:
  - ReadWriteMany
  storageClassName: nfs-client
  resources:
    requests:
      storage: 20Gi

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: project-ai-models
  namespace: project-ai-prod
spec:
  accessModes:
  - ReadOnlyMany
  storageClassName: fast-ssd
  resources:
    requests:
      storage: 100Gi
```

## Auto-Scaling

### Horizontal Pod Autoscaler

**File**: `k8s/base/hpa.yaml`

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: project-ai-prod
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 20
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
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
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
        periodSeconds: 15
      - type: Pods
        value: 4
        periodSeconds: 15
      selectPolicy: Max
```

### Vertical Pod Autoscaler (VPA)

**File**: `k8s/base/vpa.yaml`

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: backend-vpa
  namespace: project-ai-prod
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: backend
      minAllowed:
        cpu: 100m
        memory: 256Mi
      maxAllowed:
        cpu: 4000m
        memory: 8Gi
```

## Database Deployment

### PostgreSQL StatefulSet

**File**: `k8s/base/postgres-statefulset.yaml`

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: project-ai-prod
spec:
  serviceName: postgres-service
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_DB
          value: legion_web
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: username
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: database-credentials
              key: password
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - pg_isready
            - -U
            - postgres
          initialDelaySeconds: 5
          periodSeconds: 5
  volumeClaimTemplates:
  - metadata:
      name: postgres-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-ssd
      resources:
        requests:
          storage: 100Gi
```

### Redis Deployment

**File**: `k8s/base/redis-deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: project-ai-prod
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379
        command: ["redis-server", "--appendonly", "yes"]
        volumeMounts:
        - name: redis-storage
          mountPath: /data
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 1Gi
      volumes:
      - name: redis-storage
        persistentVolumeClaim:
          claimName: redis-data

---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
  namespace: project-ai-prod
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
```

## Helm Chart

### Chart Structure

```
helm/project-ai/
├── Chart.yaml
├── values.yaml
├── values-prod.yaml
├── values-staging.yaml
├── templates/
│   ├── _helpers.tpl
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── hpa.yaml
│   ├── pvc.yaml
│   └── serviceaccount.yaml
└── charts/  # Sub-charts (PostgreSQL, Redis)
```

### Chart.yaml

```yaml
apiVersion: v2
name: project-ai
description: Personal AI Assistant Helm Chart
type: application
version: 1.0.0
appVersion: "1.0.0"

dependencies:
- name: postgresql
  version: "12.5.0"
  repository: https://charts.bitnami.com/bitnami
  condition: postgresql.enabled
- name: redis
  version: "17.11.0"
  repository: https://charts.bitnami.com/bitnami
  condition: redis.enabled
```

### values.yaml

```yaml
# Global settings
replicaCount: 3
image:
  repository: projectai/backend
  tag: v1.0.0
  pullPolicy: IfNotPresent

resources:
  requests:
    cpu: 500m
    memory: 512Mi
  limits:
    cpu: 2000m
    memory: 2Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
  - host: projectai.com
    paths:
    - path: /
      pathType: Prefix
  tls:
  - secretName: project-ai-tls
    hosts:
    - projectai.com

postgresql:
  enabled: true
  auth:
    username: produser
    password: ""  # Set via --set or values file
    database: legion_web
  primary:
    persistence:
      size: 100Gi

redis:
  enabled: true
  architecture: standalone
  auth:
    enabled: false
  master:
    persistence:
      size: 10Gi
```

### Deploy with Helm

```bash
# Add Bitnami repo
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

# Install chart
helm install project-ai ./helm/project-ai \
  --namespace project-ai-prod \
  --create-namespace \
  -f helm/project-ai/values-prod.yaml \
  --set postgresql.auth.password=$DB_PASSWORD

# Upgrade
helm upgrade project-ai ./helm/project-ai \
  --namespace project-ai-prod \
  -f helm/project-ai/values-prod.yaml

# Rollback
helm rollback project-ai 1 --namespace project-ai-prod

# Uninstall
helm uninstall project-ai --namespace project-ai-prod
```

## Monitoring and Observability

### Prometheus ServiceMonitor

**File**: `k8s/monitoring/servicemonitor.yaml`

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: project-ai-backend
  namespace: project-ai-prod
  labels:
    app: project-ai
spec:
  selector:
    matchLabels:
      app: project-ai
      component: backend
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### Grafana Dashboard

**Import Dashboard ID**: 1860 (Node Exporter Full)

**Custom Metrics**:
- `http_request_duration_seconds` - Request latency
- `http_requests_total` - Request count
- `ai_chat_requests_total` - Chat requests
- `ai_image_generations_total` - Image generations
- `memory_expansion_entries_total` - Knowledge base size

## Deployment Workflows

### GitOps with ArgoCD

**Application Manifest** (`argocd/project-ai.yaml`):

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: project-ai
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/IAmSoThirsty/Project-AI
    targetRevision: main
    path: k8s/base
  destination:
    server: https://kubernetes.default.svc
    namespace: project-ai-prod
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

### CI/CD Pipeline (GitHub Actions)

**Workflow** (`.github/workflows/k8s-deploy.yml`):

```yaml
name: Deploy to Kubernetes

on:
  push:
    branches: [ main ]
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure kubectl
        uses: azure/k8s-set-context@v3
        with:
          method: kubeconfig
          kubeconfig: ${{ secrets.KUBECONFIG }}
      
      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/base/ -n project-ai-prod
          kubectl rollout status deployment/backend -n project-ai-prod
```

## Related Documentation

- `01_docker_architecture.md` - Container images
- `07_container_security.md` - Security hardening
- `10_cicd_docker_pipeline.md` - Automated deployments

## References

- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Helm**: https://helm.sh/docs/
- **ArgoCD**: https://argo-cd.readthedocs.io/
- **Cert-Manager**: https://cert-manager.io/docs/
