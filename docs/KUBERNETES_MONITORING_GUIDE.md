# Kubernetes + Helm Deployment Guide for Project-AI Monitoring

## Overview

Deploy the complete Project-AI observability stack on Kubernetes in minutes using Helm. This includes:

- **Prometheus + Grafana**: Metrics collection and visualization
- **ELK Stack** (Elasticsearch, Logstash, Kibana): Log analytics at 1M+ events/sec
- **Netdata**: Real-time performance at 1000s FPS, zero-config
- **OpenTelemetry Collector**: Full-stack observability (Apache 2.0)
- **Cilium + Hubble**: eBPF kernel-level observability (packet, syscall, DNS)
- **Zabbix** (optional): Traditional monitoring

**Battle-tested at exabyte scale. All Apache/MIT licenses. Container-ready.**

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Deployment Options](#deployment-options)
4. [Component Details](#component-details)
5. [eBPF Observability with Cilium](#ebpf-observability-with-cilium)
6. [ELK Stack Configuration](#elk-stack-configuration)
7. [Netdata Setup](#netdata-setup)
8. [OpenTelemetry Integration](#opentelemetry-integration)
9. [Scaling](#scaling)
10. [Troubleshooting](#troubleshooting)
11. [Production Best Practices](#production-best-practices)

---

## Prerequisites

### Required

- **Kubernetes Cluster**: v1.24+ (supports 12,000+ nodes)
- **Helm**: v3.10+
- **kubectl**: Configured and connected to cluster
- **Storage Class**: Dynamic provisioning enabled
- **Resources**: Minimum 32 CPU cores, 64GB RAM for full stack

### Optional

- **Cert-Manager**: For automatic TLS certificate management
- **NGINX Ingress Controller**: For external access
- **External DNS**: For automatic DNS management

### Check Prerequisites

```bash
# Verify Kubernetes
kubectl version --short
kubectl get nodes

# Verify Helm
helm version

# Check storage classes
kubectl get storageclass

# Verify resources
kubectl top nodes
```

---

## Quick Start

### 1. Add Helm Repositories

```bash
# Prometheus community charts
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts

# Elastic charts
helm repo add elastic https://helm.elastic.co

# Netdata charts
helm repo add netdata https://netdata.github.io/helmchart/

# OpenTelemetry charts
helm repo add open-telemetry https://open-telemetry.github.io/opentelemetry-helm-charts

# Cilium charts
helm repo add cilium https://helm.cilium.io/

# Zabbix charts (optional)
helm repo add zabbix https://zabbix.github.io/helm-charts

# Update repositories
helm repo update
```

### 2. Install Complete Stack (One Command!)

```bash
# Install full observability stack
helm install project-ai-monitoring ./helm/project-ai-monitoring \
  --namespace monitoring \
  --create-namespace \
  --timeout 15m \
  --wait

# Watch deployment
kubectl get pods -n monitoring -w
```

**That's it!** The entire stack is now deploying. Typical deployment time: 3-5 minutes.

### 3. Access Services

Get access URLs:

```bash
# Get all services
kubectl get svc -n monitoring

# Port forward for local access
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090 &
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80 &
kubectl port-forward -n monitoring svc/kibana-kibana 5601:5601 &
kubectl port-forward -n monitoring svc/cilium-hubble-ui 8080:80 &
kubectl port-forward -n monitoring svc/netdata 19999:19999 &
```

Access:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Kibana**: http://localhost:5601
- **Hubble UI**: http://localhost:8080
- **Netdata**: http://localhost:19999

---

## Deployment Options

### Minimal Deployment (Prometheus + Grafana only)

For development or resource-constrained environments:

```bash
helm install project-ai-monitoring ./helm/project-ai-monitoring \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.enabled=true \
  --set elasticsearch.enabled=false \
  --set netdata.enabled=false \
  --set opentelemetry.enabled=false \
  --set cilium.enabled=false
```

### Production Deployment (Full Stack)

With custom values for production:

```bash
# Create custom values file
cat > prod-values.yaml <<EOF
global:
  environment: production
  storageClass: fast-ssd

prometheus:
  enabled: true

kube-prometheus-stack:
  prometheus:
    prometheusSpec:
      retention: 30d
      retentionSize: "100GB"
      storageSpec:
        volumeClaimTemplate:
          spec:
            resources:
              requests:
                storage: 100Gi
      resources:
        requests:
          cpu: 2000m
          memory: 8Gi
        limits:
          cpu: 4000m
          memory: 16Gi
  
  grafana:
    adminPassword: "super_secret_password_here"
    ingress:
      enabled: true
      ingressClassName: nginx
      hosts:
        - grafana.your-domain.com
      tls:
        - secretName: grafana-tls
          hosts:
            - grafana.your-domain.com

elasticsearch:
  enabled: true
  replicas: 5
  resources:
    requests:
      cpu: 4000m
      memory: 16Gi
    limits:
      cpu: 8000m
      memory: 32Gi
  volumeClaimTemplate:
    resources:
      requests:
        storage: 1Ti

netdata:
  enabled: true
  parent:
    claiming:
      enabled: true
      token: "YOUR_NETDATA_CLOUD_TOKEN"
      rooms: "YOUR_ROOM_ID"

cilium:
  enabled: true
  hubble:
    ui:
      ingress:
        enabled: true
        hosts:
          - hubble.your-domain.com
EOF

# Deploy with production values
helm install project-ai-monitoring ./helm/project-ai-monitoring \
  -f prod-values.yaml \
  --namespace monitoring \
  --create-namespace \
  --timeout 30m
```

### Hybrid Deployment (with Zabbix)

Enable Zabbix for hybrid monitoring:

```bash
helm install project-ai-monitoring ./helm/project-ai-monitoring \
  --namespace monitoring \
  --create-namespace \
  --set zabbix.enabled=true
```

---

## Component Details

### Prometheus + Grafana

**What it monitors:**
- AI system metrics (persona, Four Laws, memory)
- Security events (Cerberus, threats)
- Application performance (API latency, errors)
- Plugin execution
- Kubernetes cluster metrics

**Configuration:**

```yaml
# values.yaml
prometheus:
  enabled: true

kube-prometheus-stack:
  prometheus:
    prometheusSpec:
      # Scrape interval
      scrapeInterval: 15s
      # Retention period
      retention: 15d
      # Storage size
      retentionSize: "50GB"
```

**Access Grafana:**

```bash
# Get admin password
kubectl get secret -n monitoring prometheus-grafana \
  -o jsonpath="{.data.admin-password}" | base64 --decode

# Port forward
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80
```

Navigate to http://localhost:3000 and explore pre-configured dashboards.

### AlertManager

**Configure alerts:**

```bash
# Edit AlertManager config
kubectl edit secret -n monitoring alertmanager-prometheus-kube-prometheus-alertmanager

# Test alert delivery
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-alertmanager 9093:9093
```

---

## eBPF Observability with Cilium

**Cilium + Hubble provides kernel-level observability without agents:**

- Every packet, syscall, DNS query in real-time
- Replaces iptables for better performance (ToB scale)
- Zero overhead eBPF-based monitoring
- Network policy enforcement

### Features

- **Network Flow Monitoring**: See all L3/L4/L7 traffic
- **DNS Query Tracking**: Monitor all DNS requests
- **TCP/HTTP Metrics**: Application-level visibility
- **Service Map**: Auto-discover service dependencies
- **Packet Drop Analysis**: Identify network issues

### Installation

Cilium is installed automatically with the Helm chart. If you want standalone:

```bash
# Install Cilium CLI
CILIUM_CLI_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/cilium-cli/main/stable.txt)
curl -L --fail --remote-name-all https://github.com/cilium/cilium-cli/releases/download/${CILIUM_CLI_VERSION}/cilium-linux-amd64.tar.gz{,.sha256sum}
sha256sum --check cilium-linux-amd64.tar.gz.sha256sum
sudo tar xzvfC cilium-linux-amd64.tar.gz /usr/local/bin
rm cilium-linux-amd64.tar.gz{,.sha256sum}

# Check Cilium status
cilium status

# Enable Hubble observability
cilium hubble enable --ui
```

### Using Hubble CLI

```bash
# Install Hubble CLI
HUBBLE_VERSION=$(curl -s https://raw.githubusercontent.com/cilium/hubble/master/stable.txt)
curl -L --fail --remote-name-all https://github.com/cilium/hubble/releases/download/$HUBBLE_VERSION/hubble-linux-amd64.tar.gz{,.sha256sum}
sha256sum --check hubble-linux-amd64.tar.gz.sha256sum
sudo tar xzvfC hubble-linux-amd64.tar.gz /usr/local/bin
rm hubble-linux-amd64.tar.gz{,.sha256sum}

# Port forward to Hubble Relay
cilium hubble port-forward &

# Watch network flows in real-time
hubble observe

# Filter by namespace
hubble observe --namespace monitoring

# Watch DNS queries
hubble observe --type dns

# See HTTP requests
hubble observe --protocol http

# Monitor specific pod
hubble observe --pod project-ai-app

# See dropped packets
hubble observe --verdict DROPPED

# Get network statistics
hubble status
hubble observe --last 1000 | grep -E "TCP|UDP" | wc -l
```

### Hubble UI

Access visual service map:

```bash
kubectl port-forward -n monitoring svc/cilium-hubble-ui 8080:80
```

Navigate to http://localhost:8080 to see:
- Real-time service map
- Network flows visualization
- DNS query patterns
- HTTP request traces

### eBPF Programs

Cilium runs the following eBPF programs in the kernel:

- **XDP**: Packet processing at network driver level
- **TC (Traffic Control)**: L3/L4 policy enforcement
- **Socket**: L7 protocol parsing (HTTP, DNS, Kafka, etc.)
- **KProbes**: Kernel function tracing
- **Tracepoints**: Kernel event monitoring

**View loaded eBPF programs:**

```bash
# SSH into node
ssh node1

# List eBPF programs
sudo bpftool prog list | grep cilium

# View eBPF maps
sudo bpftool map list | grep cilium

# Inspect specific map
sudo bpftool map dump id <map-id>
```

---

## ELK Stack Configuration

**Elasticsearch + Logstash + Kibana for log analytics at 1M+ events/sec**

### Architecture

```
Application Logs → Filebeat/Fluentd → Logstash → Elasticsearch → Kibana
                                          ↓
                              OpenTelemetry Collector
```

### Sending Logs to ELK

#### Option 1: Direct Logging (Python Application)

```python
# In your Project-AI code
import logging
from pythonjsonlogger import jsonlogger

# Configure JSON logging
logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Logs will be collected by Logstash
logger.info("AI Persona mood updated", extra={
    "component": "ai-persona",
    "mood": "contentment",
    "value": 0.8
})
```

#### Option 2: Filebeat Sidecar

```yaml
# Add to deployment.yaml
- name: filebeat
  image: docker.elastic.co/beats/filebeat:8.5.1
  args: [
    "-c", "/etc/filebeat/filebeat.yml",
    "-e"
  ]
  volumeMounts:
  - name: config
    mountPath: /etc/filebeat
  - name: logs
    mountPath: /var/log/project-ai
```

#### Option 3: Fluentd

```yaml
# Deploy Fluentd DaemonSet
kubectl apply -f https://raw.githubusercontent.com/fluent/fluentd-kubernetes-daemonset/master/fluentd-daemonset-elasticsearch.yaml
```

### Kibana Setup

1. **Access Kibana:**

```bash
kubectl port-forward -n monitoring svc/kibana-kibana 5601:5601
```

2. **Create Index Pattern:**

- Navigate to http://localhost:5601
- Go to Management → Stack Management → Index Patterns
- Create pattern: `project-ai-*`
- Select `@timestamp` as time field

3. **Pre-configured Dashboards:**

The Logstash pipeline automatically creates indices:
- `project-ai-persona-*`: AI persona logs
- `project-ai-security-*`: Security events
- `project-ai-ethics-*`: Four Laws events
- `project-ai-logs-*`: General application logs

4. **Search Examples:**

```
# Find critical security events
component:security AND severity:critical

# AI persona mood changes
component:ai-persona AND mood:*

# Four Laws violations
component:four-laws AND result:denied

# High-latency API requests
api.duration:>1000 AND endpoint:*

# Error logs in last hour
level:ERROR AND @timestamp:[now-1h TO now]
```

### Performance Tuning

For 1M+ events/sec:

```yaml
# values.yaml
elasticsearch:
  replicas: 5  # Scale horizontally
  resources:
    requests:
      cpu: 4000m
      memory: 16Gi
    limits:
      cpu: 8000m
      memory: 32Gi
  
  esJavaOpts: "-Xms16g -Xmx16g"
  
  esConfig:
    elasticsearch.yml: |
      # Bulk indexing optimization
      indices.memory.index_buffer_size: 30%
      thread_pool.write.queue_size: 10000
      
      # Refresh interval (higher = better throughput)
      index.refresh_interval: 30s

logstash:
  replicas: 5  # Scale for throughput
  resources:
    requests:
      cpu: 2000m
      memory: 8Gi
  
  logstashConfig:
    pipeline.workers: 8
    pipeline.batch.size: 2000
    pipeline.batch.delay: 50
```

---

## Netdata Setup

**Real-time performance at 1000s FPS per core. Zero config. Monitors homelab to CERN racks.**

### Features

- **1000+ metrics per second per core**
- **Zero configuration** - auto-detects everything
- **Cloud sync** - access anywhere
- **1-second granularity** - see instant changes
- **ML-powered anomaly detection**
- **Low overhead** - <1% CPU, <100MB RAM

### Accessing Netdata

```bash
# Port forward to parent node
kubectl port-forward -n monitoring svc/netdata 19999:19999
```

Navigate to http://localhost:19999

### Netdata Cloud Integration

1. **Get token:**

Visit https://app.netdata.cloud and create workspace

2. **Update values:**

```yaml
# values.yaml
netdata:
  parent:
    claiming:
      enabled: true
      token: "YOUR_TOKEN_HERE"
      rooms: "YOUR_ROOM_ID"
```

3. **Upgrade release:**

```bash
helm upgrade project-ai-monitoring ./helm/project-ai-monitoring \
  -n monitoring \
  --set netdata.parent.claiming.token="YOUR_TOKEN" \
  --set netdata.parent.claiming.rooms="YOUR_ROOM"
```

### What Netdata Monitors

**Per-Node Metrics:**
- CPU (per core, per thread)
- Memory (RAM, swap, caches)
- Disk I/O (per disk, per partition)
- Network (per interface, per protocol)
- Processes (per process, per user)
- System calls
- Interrupts
- Context switches

**Application Metrics:**
- Docker containers
- Kubernetes pods
- Databases (MySQL, PostgreSQL, MongoDB)
- Web servers (Nginx, Apache)
- Message queues (RabbitMQ, Kafka)
- Caches (Redis, Memcached)

**Custom Metrics:**

```bash
# Custom Python plugin
cat > /etc/netdata/python.d/project_ai.conf <<EOF
project_ai:
  name: 'project_ai'
  update_every: 1
  priority: 90000
  
jobs:
  local:
    url: 'http://localhost:8000/metrics'
    metrics_path: 'metrics'
EOF

# Restart Netdata
systemctl restart netdata
```

---

## OpenTelemetry Integration

**Full-stack observability matching $1M/year enterprise suites. Apache 2.0 license.**

### What OpenTelemetry Provides

- **Unified Telemetry**: Single SDK for traces, metrics, logs
- **Vendor-Neutral**: Works with any backend
- **Auto-Instrumentation**: Zero-code instrumentation for popular frameworks
- **Sampling**: Intelligent sampling for high-volume systems
- **Context Propagation**: Distributed tracing across services

### Python SDK Integration

```python
# Install OpenTelemetry
pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp

# In your Project-AI code
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Configure tracer
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)
span_exporter = OTLPSpanExporter(
    endpoint="http://opentelemetry-collector:4317",
    insecure=True
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(span_exporter)
)

# Configure metrics
metric_reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(
        endpoint="http://opentelemetry-collector:4317",
        insecure=True
    )
)
metrics.set_meter_provider(MeterProvider(metric_readers=[metric_reader]))
meter = metrics.get_meter(__name__)

# Create custom metrics
persona_mood_counter = meter.create_counter(
    name="ai.persona.mood.changes",
    description="AI persona mood changes",
    unit="1"
)

# Use in code
with tracer.start_as_current_span("update_persona_mood"):
    # Your code here
    update_mood()
    persona_mood_counter.add(1, {"mood_type": "contentment"})
```

### Auto-Instrumentation (No Code Changes)

```bash
# Install auto-instrumentation
pip install opentelemetry-instrumentation

# Run with auto-instrumentation
opentelemetry-instrument \
  --traces_exporter otlp \
  --metrics_exporter otlp \
  --service_name project-ai \
  --exporter_otlp_endpoint http://opentelemetry-collector:4317 \
  python -m src.app.main
```

### Viewing Traces in Jaeger

```bash
# Port forward to Jaeger UI
kubectl port-forward -n monitoring svc/jaeger-query 16686:16686
```

Navigate to http://localhost:16686 and search for traces.

---

## Scaling

### Horizontal Scaling

Scale components based on load:

```bash
# Scale Prometheus
kubectl scale statefulset -n monitoring prometheus-kube-prometheus-prometheus --replicas=3

# Scale Elasticsearch
kubectl scale statefulset -n monitoring elasticsearch-master --replicas=5

# Scale Logstash
kubectl scale deployment -n monitoring logstash-logstash --replicas=5

# Scale OpenTelemetry Collector
kubectl scale deployment -n monitoring opentelemetry-collector --replicas=4
```

### Autoscaling

```yaml
# HPA for OpenTelemetry Collector
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: otel-collector-hpa
  namespace: monitoring
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: opentelemetry-collector
  minReplicas: 2
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

### Federation (Multi-Cluster)

For monitoring 12,000+ nodes across multiple clusters:

```yaml
# values.yaml - Enable Thanos for federation
kube-prometheus-stack:
  prometheus:
    prometheusSpec:
      thanos:
        image: quay.io/thanos/thanos:v0.32.0
        version: v0.32.0
        objectStorageConfig:
          key: thanos.yaml
          name: thanos-objstore-config
      
      externalLabels:
        cluster: us-east-1
        datacenter: dc1
```

Deploy Thanos query frontend:

```bash
helm install thanos bitnami/thanos \
  --namespace monitoring \
  --set query.enabled=true \
  --set query.stores={prometheus-operated:10901}
```

---

## Troubleshooting

### Pods Not Starting

```bash
# Check pod status
kubectl get pods -n monitoring

# Describe problematic pod
kubectl describe pod -n monitoring <pod-name>

# Check logs
kubectl logs -n monitoring <pod-name>

# Check events
kubectl get events -n monitoring --sort-by='.lastTimestamp'
```

### Storage Issues

```bash
# Check PVCs
kubectl get pvc -n monitoring

# Check storage class
kubectl get storageclass

# Increase storage (if using dynamic provisioning)
kubectl edit pvc -n monitoring <pvc-name>
```

### Network Issues

```bash
# Test connectivity between pods
kubectl run -it --rm debug --image=nicolaka/netshoot --restart=Never -n monitoring -- /bin/bash

# Inside debug pod
curl http://prometheus-kube-prometheus-prometheus:9090/-/healthy
curl http://elasticsearch-master:9200/_cluster/health
```

### Cilium Issues

```bash
# Check Cilium status
cilium status

# Test connectivity
cilium connectivity test

# View Cilium logs
kubectl logs -n kube-system -l k8s-app=cilium

# Restart Cilium
kubectl rollout restart daemonset/cilium -n kube-system
```

---

## Production Best Practices

### Security

1. **Enable TLS**:

```yaml
# values.yaml
kube-prometheus-stack:
  grafana:
    ingress:
      enabled: true
      tls:
        - secretName: grafana-tls
          hosts:
            - grafana.example.com
```

2. **Network Policies**:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: monitoring-netpol
  namespace: monitoring
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
```

3. **RBAC**:

```bash
# Create read-only user
kubectl create serviceaccount monitoring-readonly -n monitoring
kubectl create clusterrole monitoring-readonly --verb=get,list,watch --resource=*
kubectl create clusterrolebinding monitoring-readonly --clusterrole=monitoring-readonly --serviceaccount=monitoring:monitoring-readonly
```

### High Availability

```yaml
# values.yaml - Enable HA for all components
kube-prometheus-stack:
  prometheus:
    prometheusSpec:
      replicas: 3
  
  alertmanager:
    alertmanagerSpec:
      replicas: 3

elasticsearch:
  replicas: 5
  minimumMasterNodes: 3

logstash:
  replicas: 3

cilium:
  operator:
    replicas: 3
```

### Backup and Restore

```bash
# Backup Prometheus data
kubectl exec -n monitoring prometheus-kube-prometheus-prometheus-0 -- \
  tar czf /tmp/prometheus-backup.tar.gz /prometheus

kubectl cp monitoring/prometheus-kube-prometheus-prometheus-0:/tmp/prometheus-backup.tar.gz \
  ./prometheus-backup.tar.gz

# Backup Elasticsearch snapshots
kubectl exec -n monitoring elasticsearch-master-0 -- \
  curl -X PUT "localhost:9200/_snapshot/backup_repo/snapshot_1?wait_for_completion=true"
```

### Monitoring the Monitors

```yaml
# AlertManager alert for Prometheus down
- alert: PrometheusDown
  expr: up{job="prometheus"} == 0
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "Prometheus is down"

# Alert for Elasticsearch cluster health
- alert: ElasticsearchClusterRed
  expr: elasticsearch_cluster_health_status{color="red"} == 1
  for: 5m
  labels:
    severity: critical
```

---

## Support and Resources

- **Project-AI Issues**: https://github.com/IAmSoThirsty/Project-AI/issues
- **Prometheus**: https://prometheus.io/docs/
- **Elastic Stack**: https://www.elastic.co/guide/
- **Netdata**: https://learn.netdata.cloud/
- **OpenTelemetry**: https://opentelemetry.io/docs/
- **Cilium**: https://docs.cilium.io/

---

**Last Updated**: 2026-01-07  
**Version**: 1.0  
**License**: MIT (monitoring stack uses Apache 2.0 / MIT licenses)
