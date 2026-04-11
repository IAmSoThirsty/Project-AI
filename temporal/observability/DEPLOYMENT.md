# Observability Stack Deployment Guide

## Prerequisites

- Kubernetes cluster (v1.25+) with at least 3 nodes
- kubectl configured to access the cluster
- Helm (optional, for alternative deployment)
- Storage class for persistent volumes
- 100GB+ available storage

## Quick Start

### 1. Deploy with Kustomize (Recommended)

```bash
# Deploy entire observability stack
kubectl apply -k temporal/observability/

# Verify deployments
kubectl get pods -n observability

# Wait for all pods to be ready
kubectl wait --for=condition=ready pod --all -n observability --timeout=300s
```

### 2. Deploy with Docker Compose (Local Development)

```bash
cd temporal/observability
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## Access Services

### Port Forwarding (Kubernetes)

```bash
# Grafana
kubectl port-forward -n observability svc/grafana 3000:3000

# Prometheus
kubectl port-forward -n observability svc/prometheus 9090:9090

# Jaeger UI
kubectl port-forward -n observability svc/jaeger-query 16686:16686

# AlertManager
kubectl port-forward -n observability svc/alertmanager 9093:9093

# Loki
kubectl port-forward -n observability svc/loki 3100:3100
```

### Default Credentials

- **Grafana**: admin / admin (change on first login)
- Other services: No authentication by default (configure in production)

## Configuration

### 1. Update Prometheus Targets

Edit `prometheus/prometheus.yml` to add your agent endpoints:

```yaml
- job_name: 'agents'
  kubernetes_sd_configs:
    - role: pod
      namespaces:
        names:
          - agents  # Your agent namespace
```

### 2. Configure Alerting

Update `alertmanager/alertmanager.yml` with your notification channels:

```yaml
receivers:
  - name: 'critical-alerts'
    slack_configs:
      - channel: '#your-channel'
        api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    pagerduty_configs:
      - service_key: 'YOUR_PAGERDUTY_KEY'
```

### 3. Setup Thanos for Long-term Storage

Create S3 bucket and update `prometheus/thanos-bucket.yml`:

```yaml
config:
  bucket: "your-thanos-bucket"
  region: "your-region"
  access_key: "YOUR_ACCESS_KEY"
  secret_key: "YOUR_SECRET_KEY"
```

Apply as secret:

```bash
kubectl create secret generic thanos-objstore-config \
  --from-file=thanos-bucket.yml=prometheus/thanos-bucket.yml \
  -n observability
```

## Monitoring 1000+ Agents

### Resource Requirements

For 1000+ agents across multiple regions:

**Prometheus:**
- CPU: 4-8 cores
- Memory: 16-32GB
- Storage: 200GB (30 days retention)

**Thanos:**
- CPU: 2-4 cores per component
- Memory: 4-8GB per component
- Storage: S3 or equivalent (unlimited)

**Loki:**
- CPU: 2-4 cores
- Memory: 8-16GB
- Storage: 100GB (30 days retention)

**Jaeger:**
- CPU: 2-4 cores
- Memory: 4-8GB
- Storage: Elasticsearch cluster recommended

**Grafana:**
- CPU: 1-2 cores
- Memory: 2-4GB
- Storage: 10GB

### Scaling Prometheus

For multi-region monitoring, deploy Prometheus per region:

```bash
# US-East
kubectl apply -k temporal/observability/ --namespace observability-us-east

# EU-Central
kubectl apply -k temporal/observability/ --namespace observability-eu-central

# Configure federation in main Prometheus
```

### High Availability

Enable HA mode for critical components:

```bash
# Scale Prometheus
kubectl scale statefulset prometheus -n observability --replicas=2

# Scale AlertManager
kubectl scale statefulset alertmanager -n observability --replicas=3

# Scale Grafana
kubectl scale deployment grafana -n observability --replicas=2
```

## Dashboards

Three pre-configured dashboards are available:

1. **Agent Fleet Health** (`/d/agent-fleet-health`)
   - Agent availability and uptime
   - Error rates and latency
   - Resource usage
   - Regional distribution

2. **Workflow Performance** (`/d/workflow-performance`)
   - Workflow execution metrics
   - Task queue depth
   - Activity success rates
   - Worker utilization

3. **Resource Usage Overview** (`/d/resource-usage-overview`)
   - CPU, Memory, Disk usage
   - Network traffic
   - Container metrics
   - System load

Access at: http://localhost:3000

## Alerting Rules

Configured alert rules include:

### Critical Alerts (Immediate)
- Agent down (>5% of fleet)
- High error rates (>1%)
- Resource exhaustion (>95%)
- Workflow stuck (>30 minutes)

### Warning Alerts (15-minute threshold)
- High CPU/Memory (>85%)
- Slow performance (p95 >5s)
- High retry rates

## Troubleshooting

### Prometheus Not Scraping Targets

```bash
# Check Prometheus targets
kubectl port-forward -n observability svc/prometheus 9090:9090
# Visit http://localhost:9090/targets

# Check service discovery
kubectl get servicemonitors -n observability
```

### Grafana Not Showing Data

```bash
# Test datasource connection
kubectl exec -n observability deployment/grafana -- \
  curl http://prometheus:9090/api/v1/query?query=up

# Check Grafana logs
kubectl logs -n observability deployment/grafana
```

### Jaeger Not Receiving Traces

```bash
# Check Jaeger collector logs
kubectl logs -n observability deployment/jaeger-collector

# Verify agent configuration points to:
# jaeger-collector.observability.svc.cluster.local:14268
```

### AlertManager Not Sending Alerts

```bash
# Check AlertManager config
kubectl exec -n observability statefulset/alertmanager -- \
  amtool config show

# Test alert
kubectl exec -n observability statefulset/alertmanager -- \
  amtool alert add test severity=warning
```

### Loki Query Performance

```bash
# Check Loki metrics
kubectl port-forward -n observability svc/loki 3100:3100
# Visit http://localhost:3100/metrics

# Optimize queries with labels:
# {job="agents", region="us-east"} |= "error"
```

## Maintenance

### Backup Configuration

```bash
# Backup all configs
kubectl get configmaps -n observability -o yaml > observability-backup.yaml
kubectl get secrets -n observability -o yaml >> observability-backup.yaml
```

### Update Retention Policies

```bash
# Edit Prometheus retention
kubectl edit statefulset prometheus -n observability
# Update: --storage.tsdb.retention.time=60d

# Edit Loki retention
kubectl edit configmap loki-config -n observability
# Update retention_period
```

### Clean Up Old Data

```bash
# Prometheus
kubectl exec -n observability statefulset/prometheus-0 -- \
  promtool tsdb delete --start=-90d

# Loki compactor runs automatically
# Check compactor logs:
kubectl logs -n observability deployment/loki -c compactor
```

## Production Checklist

- [ ] Enable authentication on all services
- [ ] Configure TLS/mTLS for inter-service communication
- [ ] Set up proper RBAC for Kubernetes resources
- [ ] Configure backup for Grafana dashboards
- [ ] Set up long-term storage (Thanos)
- [ ] Configure notification channels in AlertManager
- [ ] Test alert routing and escalation
- [ ] Set up monitoring for the monitoring stack
- [ ] Configure resource quotas and limits
- [ ] Enable audit logging
- [ ] Set up disaster recovery procedures
- [ ] Document runbooks for common alerts
- [ ] Configure network policies for isolation
- [ ] Enable PodSecurityPolicies
- [ ] Set up cost monitoring for cloud resources

## Security

### Enable mTLS

```bash
# Generate certificates
./scripts/generate-certs.sh

# Apply certificates
kubectl create secret tls observability-tls \
  --cert=certs/tls.crt \
  --key=certs/tls.key \
  -n observability
```

### Configure RBAC

```bash
# Apply RBAC policies
kubectl apply -f rbac/

# Create service accounts
kubectl create serviceaccount grafana-sa -n observability
```

### Network Policies

```bash
# Apply network isolation
kubectl apply -f network-policies/
```

## Monitoring the Monitoring Stack

Create alerts for the observability platform itself:

- Prometheus storage usage
- Grafana availability
- AlertManager cluster status
- Loki ingestion rate
- Jaeger storage capacity

## Support

For issues:
1. Check component logs: `kubectl logs -n observability <pod-name>`
2. Verify network connectivity between components
3. Check resource utilization
4. Review Grafana datasource configurations
5. Validate Prometheus scrape configs
