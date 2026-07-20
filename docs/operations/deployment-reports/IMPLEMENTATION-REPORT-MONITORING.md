# Monitoring Implementation Report

> **Current release boundary (2026-07-19):** This is a historical or
> implementation-reference artifact, not current production evidence or
> deployment approval. The v0.0.3 successor remains fail-closed until the
> [pre-deployment checklist](../../deployment/PRE_DEPLOYMENT_CHECKLIST.md) and
> [CAB evidence bundle](../cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md)
> pass. Commands here are examples; this document does not prove deployment.

## Overview

Implemented **observability layer** via Prometheus ServiceMonitor. Services expose metrics for scraping by Prometheus, enabling real-time monitoring and alerting.

## Files Created

### 1. `helm/project-ai/templates/servicemonitor.yaml` (NEW)
- ServiceMonitor for Prometheus operator
- Scrape configuration (30s interval, /metrics endpoint)
- Label-based pod discovery
- Conditional creation via `monitoring.enabled` flag

## Files Modified

### 1. `helm/values.prod.yaml` (TO ADD)
- Add: `monitoring.enabled: true`

## Metrics Collection

### Scrape Configuration

```yaml
# ServiceMonitor automatically creates scrape job
job_name: project-ai
scrape_interval: 30s
scrape_timeout: 10s
endpoint: /metrics
```

### Metrics Available (via application instrumentation)

**API Service:**
- HTTP request latency (histogram)
- Request rate (counter)
- Error rate (counter)
- Audit log entries (gauge)

**All Services:**
- Container CPU usage
- Container memory usage
- Pod restart count
- Network I/O

## Deployment

**Prerequisites:**
```bash
# Install Prometheus operator
helm install prometheus-operator prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace
```

**Deploy with Monitoring:**
```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set monitoring.enabled=true \
  -n project-ai-prod
```

## Verification

```bash
# Check ServiceMonitor created
kubectl get servicemonitor -n project-ai-prod

# Check Prometheus scrape targets
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090
# Visit: http://localhost:9090/targets
```

## Grafana Dashboards

Create dashboard for:
- API response time
- Request rate
- Error rate
- Pod CPU/memory
- Audit log volume

## References

- Prometheus: https://prometheus.io/
- ServiceMonitor: https://prometheus-operator.dev/docs/operator/api/#servicemonitor
