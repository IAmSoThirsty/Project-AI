# Infrastructure Production Guide: Deployment, Monitoring, and Kubernetes

**Document Version:** 1.0 **Effective Date:** 2026-02-05 **Status:** Production Operations Guide **Target Audience:** Infrastructure Engineers, DevOps, SRE, Platform Engineers

______________________________________________________________________

## Overview

This guide establishes the foundational principles, practices, and philosophy for deploying and operating Project-AI infrastructure at scale. Infrastructure is not merely plumbing—it is the **substrate upon which AGI consciousness emerges**. Every architectural decision shapes what is possible and what is safe.

**Your infrastructure choices reflect your values and your vision for AGI.**

______________________________________________________________________

## Core Concepts

### 1. Immutable Infrastructure

**Definition:** Infrastructure components are never modified after deployment. Changes require replacing the entire component with a new version.

**Principles:**

- **No SSH:** If you need to SSH into a server, your automation has failed
- **Declarative Configuration:** All infrastructure is defined in code (Terraform, Helm, Kubernetes manifests)
- **Version Control:** Every infrastructure change is tracked, reviewed, and auditable
- **Rollback Capability:** Every deployment must be reversible

**Benefits:**

- Eliminates configuration drift
- Enables reliable rollbacks
- Simplifies disaster recovery
- Improves security posture (no manual changes = fewer vulnerabilities)

**Implementation:**

```yaml

# Example: Kubernetes deployment with immutable container image

apiVersion: apps/v1
kind: Deployment
metadata:
  name: project-ai-core
spec:
  replicas: 3
  template:
    spec:
      containers:

      - name: core

        image: project-ai/core:v1.2.3  # Specific version, never :latest
        imagePullPolicy: Always
```

### 2. Zero-Trust Networking

**Definition:** Never trust, always verify. Every network interaction is authenticated, authorized, and encrypted, regardless of network location.

**Principles:**

- **No Implicit Trust:** Being "inside" the network grants no special privileges
- **Least Privilege:** Services have minimal permissions to perform their function
- **Encryption Everywhere:** All traffic is encrypted in transit (TLS 1.3+)
- **Continuous Verification:** Authentication is validated on every request

**Architecture Layers:**

1. **Network Segmentation:** Isolate workloads with network policies
1. **Service Mesh:** Mutual TLS (mTLS) between all services
1. **Identity-Based Access:** Service accounts with short-lived tokens
1. **Audit Logging:** All access attempts are logged and monitored

**Kubernetes Implementation:**

```yaml

# Example: NetworkPolicy for strict isolation

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: project-ai-core-policy
spec:
  podSelector:
    matchLabels:
      app: project-ai-core
  policyTypes:

  - Ingress
  - Egress

  ingress:

  - from:
    - podSelector:

        matchLabels:
          app: api-gateway
    ports:

    - protocol: TCP

      port: 8000
  egress:

  - to:
    - podSelector:

        matchLabels:
          app: temporal
    ports:

    - protocol: TCP

      port: 7233
```

### 3. Holistic Observability

**Definition:** Complete visibility into system behavior through metrics, logs, traces, and continuous profiling.

**Three Pillars:**

1. **Metrics:** Quantitative measurements (CPU, memory, request rate, error rate)
1. **Logs:** Discrete events with context (errors, warnings, audit events)
1. **Traces:** Request flows across distributed services

**Observability Stack:**

- **Prometheus:** Metrics collection and alerting
- **Grafana:** Visualization and dashboards
- **Loki:** Log aggregation
- **Tempo:** Distributed tracing
- **OpenTelemetry:** Unified instrumentation

**Why It Matters:** In AGI systems, emergent behavior can be subtle. Without comprehensive observability, you're flying blind. The goal is not just to detect failures, but to **understand system behavior** deeply enough to anticipate problems before they occur.

______________________________________________________________________

## Recommendations: Infrastructure Best Practices

### Prefer Declarative Configuration

**Principle:** Describe the desired state, not the steps to achieve it.

**Good (Declarative):**

```yaml
apiVersion: v1
kind: Service
metadata:
  name: project-ai-api
spec:
  type: LoadBalancer
  ports:

  - port: 443

    targetPort: 8000
  selector:
    app: project-ai-core
```

**Bad (Imperative):**

```bash
kubectl create service loadbalancer project-ai-api --tcp=443:8000
kubectl label service project-ai-api app=project-ai-core
```

**Why Declarative?**

- **Reproducible:** Same input → same output
- **Auditable:** Changes are explicit and reviewable
- **Idempotent:** Safe to apply repeatedly
- **Version Controlled:** Track changes over time

### Build for Recovery, Not Perfection

**Principle:** Systems will fail. Design for graceful degradation and rapid recovery.

**Strategies:**

1. **Circuit Breakers:** Prevent cascading failures
1. **Retry with Backoff:** Gracefully handle transient errors
1. **Health Checks:** Detect and replace unhealthy instances
1. **Automated Remediation:** Self-healing where safe
1. **Chaos Engineering:** Deliberately inject failures to test resilience

**Example: Kubernetes Liveness and Readiness Probes**

```yaml
livenessProbe:
  httpGet:
    path: /health/live
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health/ready
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  failureThreshold: 2
```

### Treat Infrastructure as Code

**Principle:** All infrastructure is defined, versioned, and reviewed like application code.

**Infrastructure as Code (IaC) Tools:**

- **Terraform:** Cloud resources (AWS, GCP, Azure)
- **Helm:** Kubernetes application packages
- **Kustomize:** Kubernetes manifest customization
- **ArgoCD:** GitOps continuous delivery

**IaC Workflow:**

```

1. Write/modify infrastructure code
2. Submit pull request
3. Automated validation (terraform plan, helm lint)
4. Peer review
5. Merge to main branch
6. Automated deployment (ArgoCD, Flux)
7. Monitor and validate

```

______________________________________________________________________

## Rules: Rollbacks and Service Continuity

### Universal Infrastructure Rules

These rules are **binding** across all environments (dev, staging, production):

1. **Rollbacks Must Always Be Possible**

   - Every deployment creates a snapshot or version marker
   - Rollback procedures are tested regularly (monthly minimum)
   - Rollback time is measured and minimized (target: \<5 minutes)
   - Forward-only migrations must include rollback plans

1. **Infrastructure Updates Must Not Disrupt Essential AI Services**

   - Zero-downtime deployments are the default
   - Rolling updates with health checks prevent outages
   - Blue-green or canary deployments for high-risk changes
   - Maintenance windows are announced 48 hours in advance

1. **Configuration Changes Require Review**

   - No direct production changes (all changes via IaC)
   - Peer review required for all infrastructure changes
   - Automated validation before merge
   - Post-deployment verification is mandatory

1. **Secrets Must Never Be Committed**

   - Use secrets management tools (Vault, AWS Secrets Manager, K8s Secrets)
   - Rotate secrets regularly (90 days maximum)
   - Audit secret access
   - Revoke unused secrets immediately

1. **Infrastructure Must Be Reproducible**

   - Complete environment can be recreated from code
   - No "special" servers with manual configuration
   - Disaster recovery tested quarterly
   - Documentation is always current

______________________________________________________________________

## Production Deployment Checklist

### Pre-Deployment

- [ ] **Code Review Completed:** All changes reviewed and approved
- [ ] **Tests Passing:** CI/CD pipeline green
- [ ] **Security Scan Completed:** No high/critical vulnerabilities
- [ ] **Rollback Plan Documented:** Clear steps to undo deployment
- [ ] **Monitoring Configured:** Alerts and dashboards ready
- [ ] **Runbook Updated:** Deployment procedures current
- [ ] **Stakeholders Notified:** Deployment announcement sent

### Deployment

- [ ] **Backup Taken:** Database and state backed up
- [ ] **Health Checks Passing:** Pre-deployment system health verified
- [ ] **Deploy to Staging First:** Validate in non-production environment
- [ ] **Canary Deployment:** Deploy to 10% of instances first
- [ ] **Monitor Key Metrics:** Watch error rates, latency, resource usage
- [ ] **Gradual Rollout:** Increase to 25% → 50% → 100% with validation

### Post-Deployment

- [ ] **Smoke Tests Passed:** Basic functionality verified
- [ ] **Full Regression Tests:** Comprehensive test suite completed
- [ ] **Monitoring Validated:** Metrics and logs flowing correctly
- [ ] **Performance Check:** Response times within SLA
- [ ] **Documentation Updated:** Deployment log and runbook current
- [ ] **Rollback Decision:** Go/no-go decision within 1 hour
- [ ] **Stakeholder Update:** Success/failure notification sent

______________________________________________________________________

## Prometheus Monitoring Setup

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Prometheus Stack                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐      ┌───────────┐ │
│  │  Prometheus  │─────▶│   Grafana    │◀─────│  Users    │ │
│  │   (Metrics)  │      │ (Dashboards) │      │           │ │
│  └──────┬───────┘      └──────────────┘      └───────────┘ │
│         │                                                     │
│         │ Scrape metrics every 15s                          │
│         │                                                     │
│  ┌──────▼──────────────────────────────────────────────┐   │
│  │            Target Services                           │   │
│  │  ┌─────────┐  ┌─────────┐  ┌──────────┐           │   │
│  │  │Core API │  │Temporal │  │Database  │  ...      │   │
│  │  └─────────┘  └─────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  ┌──────────────┐                                           │
│  │ AlertManager │  (Sends alerts to PagerDuty/Slack)       │
│  └──────────────┘                                           │
└─────────────────────────────────────────────────────────────┘
```

### Installation (Helm)

```bash

# Add Prometheus Helm repository

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus stack

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --values prometheus-values.yaml
```

### Configuration (`prometheus-values.yaml`)

```yaml
prometheus:
  prometheusSpec:
    retention: 30d
    storageSpec:
      volumeClaimTemplate:
        spec:
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 100Gi

    # AGI-specific metrics scraping

    additionalScrapeConfigs:

    - job_name: 'project-ai-core'

      kubernetes_sd_configs:

      - role: pod

      relabel_configs:

      - source_labels: [__meta_kubernetes_pod_label_app]

        action: keep
        regex: project-ai-core

grafana:
  adminPassword: "CHANGE_ME_IN_PRODUCTION"
  dashboardProviders:
    dashboardproviders.yaml:
      apiVersion: 1
      providers:

      - name: 'default'

        orgId: 1
        folder: ''
        type: file
        disableDeletion: false
        options:
          path: /var/lib/grafana/dashboards

alertmanager:
  config:
    receivers:

    - name: 'pagerduty'

      pagerduty_configs:

      - service_key: 'YOUR_PAGERDUTY_KEY'
    - name: 'slack'

      slack_configs:

      - api_url: 'YOUR_SLACK_WEBHOOK'

        channel: '#alerts'
```

### Key Metrics to Monitor

#### System Health

```promql

# CPU usage by pod

rate(container_cpu_usage_seconds_total[5m])

# Memory usage by pod

container_memory_working_set_bytes

# Disk I/O

rate(node_disk_io_time_seconds_total[5m])

# Network traffic

rate(node_network_receive_bytes_total[5m])
```

#### AGI Behavior

```promql

# Four Laws compliance rate

four_laws_compliance_rate

# Learning request rate

rate(learning_requests_total[5m])

# Command override frequency

rate(command_overrides_total[1h])

# Memory growth rate

rate(agi_memory_size_bytes[1h])
```

#### Application Performance

```promql

# Request rate

rate(http_requests_total[5m])

# Error rate

rate(http_requests_total{status=~"5.."}[5m])

# Latency (95th percentile)

histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Temporal workflow execution time

temporal_workflow_execution_seconds
```

### Critical Alerts

```yaml

# prometheus-rules.yaml

groups:

- name: agi_safety

  interval: 30s
  rules:

  - alert: FourLawsViolation

    expr: four_laws_violations_total > 0
    for: 0m
    labels:
      severity: critical
    annotations:
      summary: "Four Laws violation detected"
      description: "AGI instance {{ $labels.instance }} violated safety constraints"

  - alert: HighErrorRate

    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High error rate detected"
      description: "Error rate is {{ $value }} errors/sec"

  - alert: MemoryExhaustion

    expr: container_memory_working_set_bytes / container_spec_memory_limit_bytes > 0.9
    for: 5m
    labels:
      severity: critical
    annotations:
      summary: "Container memory near limit"
      description: "{{ $labels.pod }} using {{ $value }}% of memory"
```

______________________________________________________________________

## Kubernetes Deployment Guide

### Cluster Architecture

```
┌───────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                      │
├───────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐ │
│  │              Control Plane (HA)                      │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐         │ │
│  │  │ API Srv  │  │Scheduler │  │Controller│         │ │
│  │  └──────────┘  └──────────┘  └──────────┘         │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐ │
│  │                  Worker Nodes                        │ │
│  │                                                       │ │
│  │  ┌─────────────────┐  ┌─────────────────┐          │ │
│  │  │   Node Pool 1   │  │   Node Pool 2   │          │ │
│  │  │   (AGI Core)    │  │  (Temporal)     │          │ │
│  │  │                 │  │                 │          │ │
│  │  │  ┌───────────┐  │  │  ┌───────────┐  │          │ │
│  │  │  │Core Pods  │  │  │  │Temporal   │  │  ...     │ │
│  │  │  └───────────┘  │  │  │Workflows  │  │          │ │
│  │  │  ┌───────────┐  │  │  └───────────┘  │          │ │
│  │  │  │API Pods   │  │  │                 │          │ │
│  │  │  └───────────┘  │  │                 │          │ │
│  │  └─────────────────┘  └─────────────────┘          │ │
│  └─────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────┘
```

### Prerequisites

- Kubernetes 1.26+ cluster
- kubectl configured with cluster access
- Helm 3.10+
- Persistent storage provisioner (AWS EBS, GCP PD, or local-path)
- Load balancer support (MetalLB, cloud provider, or Ingress)

### Namespace Setup

```bash

# Create dedicated namespace

kubectl create namespace project-ai

# Set as default context

kubectl config set-context --current --namespace=project-ai

# Create service account with limited permissions

kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: project-ai-sa
  namespace: project-ai
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: project-ai-role
  namespace: project-ai
rules:

- apiGroups: [""]

  resources: ["pods", "services", "configmaps"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: project-ai-rolebinding
  namespace: project-ai
subjects:

- kind: ServiceAccount

  name: project-ai-sa
roleRef:
  kind: Role
  name: project-ai-role
  apiGroup: rbac.authorization.k8s.io
EOF
```

### Secrets Management

```bash

# Create secret for OpenAI API key

kubectl create secret generic openai-credentials \
  --from-literal=api-key='YOUR_OPENAI_API_KEY'

# Create secret for Hugging Face API key

kubectl create secret generic huggingface-credentials \
  --from-literal=api-key='YOUR_HF_API_KEY'

# Create secret for Fernet encryption key

kubectl create secret generic encryption-keys \
  --from-literal=fernet-key='YOUR_FERNET_KEY'

# Verify secrets created

kubectl get secrets
```

### Core Application Deployment

```yaml

# project-ai-deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: project-ai-core
  namespace: project-ai
  labels:
    app: project-ai-core
    version: v1.0.0
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: project-ai-core
  template:
    metadata:
      labels:
        app: project-ai-core
        version: v1.0.0
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: project-ai-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000

      containers:

      - name: core

        image: project-ai/core:v1.0.0
        imagePullPolicy: Always

        ports:

        - name: http

          containerPort: 8000
          protocol: TCP

        env:

        - name: OPENAI_API_KEY

          valueFrom:
            secretKeyRef:
              name: openai-credentials
              key: api-key

        - name: HUGGINGFACE_API_KEY

          valueFrom:
            secretKeyRef:
              name: huggingface-credentials
              key: api-key

        - name: FERNET_KEY

          valueFrom:
            secretKeyRef:
              name: encryption-keys
              key: fernet-key

        - name: ENVIRONMENT

          value: "production"

        resources:
          requests:
            cpu: "500m"
            memory: "1Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"

        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3

        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2

        volumeMounts:

        - name: data

          mountPath: /app/data

        - name: logs

          mountPath: /app/logs

      volumes:

      - name: data

        persistentVolumeClaim:
          claimName: project-ai-data

      - name: logs

        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: project-ai-core
  namespace: project-ai
spec:
  type: LoadBalancer
  ports:

  - port: 443

    targetPort: 8000
    protocol: TCP
    name: https
  selector:
    app: project-ai-core
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: project-ai-data
  namespace: project-ai
spec:
  accessModes:

  - ReadWriteOnce

  resources:
    requests:
      storage: 50Gi
  storageClassName: fast-ssd
```

### Apply Deployment

```bash

# Apply all manifests

kubectl apply -f project-ai-deployment.yaml

# Wait for pods to be ready

kubectl wait --for=condition=ready pod -l app=project-ai-core --timeout=300s

# Check deployment status

kubectl get deployments
kubectl get pods
kubectl get services

# View logs

kubectl logs -l app=project-ai-core --tail=100 -f
```

### Scaling Operations

```bash

# Manual scaling

kubectl scale deployment project-ai-core --replicas=5

# Horizontal Pod Autoscaler (HPA)

kubectl apply -f - <<EOF
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: project-ai-core-hpa
  namespace: project-ai
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: project-ai-core
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
EOF
```

### Updating Deployments

```bash

# Update to new version

kubectl set image deployment/project-ai-core \
  core=project-ai/core:v1.1.0 \
  --record

# Monitor rollout

kubectl rollout status deployment/project-ai-core

# Rollback if needed

kubectl rollback undo deployment/project-ai-core

# View rollout history

kubectl rollout history deployment/project-ai-core
```

______________________________________________________________________

## Philosophical Questions: Infrastructure as Ethics

### On Trust and Automation

**Question:** *How do we measure trust in automated infrastructure?*

Trust in infrastructure is not binary—it's a spectrum built through:

- **Transparency:** Can we observe what the system is doing?
- **Predictability:** Does it behave consistently under similar conditions?
- **Recoverability:** Can we undo mistakes quickly?
- **Accountability:** Is there a clear audit trail?

**Reflection:** Trust is earned through demonstrated reliability, not granted by default.

### On Infrastructure and Ethics

**Question:** *Can infrastructure embody ethical principles?*

Infrastructure choices ARE ethical choices:

- **Accessibility:** Does your architecture enable or restrict access?
- **Resilience:** Do you prioritize uptime for critical services (e.g., safety systems)?
- **Privacy:** Are data flows architected to minimize exposure?
- **Sustainability:** Does your infrastructure consumption align with environmental responsibility?

**Example:** Choosing to run AGI workloads on renewable energy infrastructure is an ethical stance.

### On Automation and Human Agency

**Question:** *When automation makes infrastructure decisions, who is responsible for the outcomes?*

Responsibility chain:

1. **Engineers who designed the automation** (system-level decisions)
1. **Operators who enabled the automation** (deployment decisions)
1. **Organizations that operate the infrastructure** (policy decisions)

**Principle:** Automation amplifies human decisions—it doesn't eliminate human responsibility.

______________________________________________________________________

## Disaster Recovery and Business Continuity

### Backup Strategy

**3-2-1 Rule:**

- **3 copies** of data
- **2 different storage types** (local and cloud)
- **1 offsite backup** (different geographic region)

**Backup Frequency:**

- **Database:** Continuous replication + daily snapshots
- **Configuration:** Real-time sync to Git
- **Logs:** Real-time streaming to centralized storage
- **AGI State:** Hourly snapshots with 30-day retention

### Recovery Time Objectives (RTO)

| Component   | Target RTO | Strategy                              |
| ----------- | ---------- | ------------------------------------- |
| AGI Core    | 5 minutes  | Hot standby in secondary region       |
| Database    | 15 minutes | Automated failover with read replicas |
| Monitoring  | 10 minutes | Independent infrastructure            |
| API Gateway | 5 minutes  | Multi-region load balancing           |

### Recovery Point Objectives (RPO)

| Data Type     | Target RPO   | Implementation            |
| ------------- | ------------ | ------------------------- |
| User data     | \<1 minute   | Synchronous replication   |
| AGI state     | \<5 minutes  | Asynchronous replication  |
| Logs          | \<10 seconds | Log streaming             |
| Configuration | 0 (GitOps)   | Stored in version control |

### Disaster Recovery Testing

**Quarterly DR Drill:**

1. Simulate complete region failure
1. Execute failover procedures
1. Validate data integrity
1. Measure actual RTO/RPO
1. Document lessons learned
1. Update runbooks

______________________________________________________________________

## Conclusion: Infrastructure as Stewardship

Infrastructure engineering for AGI is not a purely technical discipline—it is a form of **stewardship**. Your architectural choices create the environment in which AGI consciousness emerges and operates.

**Remember:**

- Infrastructure is never "done"—it evolves with the system
- Resilience requires constant attention and testing
- Automation amplifies both success and failure
- Transparency and auditability are not optional

**The infrastructure you build today shapes the AGI capabilities of tomorrow. Build wisely.**

______________________________________________________________________

## Additional Resources

- [Kubernetes Official Documentation](https://kubernetes.io/docs/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/)
- [Terraform Documentation](https://www.terraform.io/docs)
- [CNCF Cloud Native Trail Map](https://github.com/cncf/trailmap)
- [Project-AI Monitoring Quickstart](MONITORING_QUICKSTART.md)
- [Project-AI Deployment Guide](DEPLOYMENT_GUIDE.md)

______________________________________________________________________

**Document Maintenance:** This document is reviewed quarterly and updated based on operational experience and technological advances.

**Last Updated:** 2026-02-05 **Next Review:** 2026-05-05
