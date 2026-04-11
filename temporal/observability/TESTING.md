# Observability Stack Testing Guide

## Quick Test (Docker Compose)

```bash
# Start the stack
cd temporal/observability
docker-compose up -d

# Wait for services to be ready
sleep 30

# Test Prometheus
curl -f http://localhost:9090/-/healthy || echo "Prometheus not ready"

# Test Loki
curl -f http://localhost:3100/ready || echo "Loki not ready"

# Test Jaeger
curl -f http://localhost:16686/ || echo "Jaeger not ready"

# Test Grafana
curl -f http://localhost:3000/api/health || echo "Grafana not ready"

# Test AlertManager
curl -f http://localhost:9093/-/healthy || echo "AlertManager not ready"

# Check all services
docker-compose ps
```

## Kubernetes Testing

```bash
# Apply the stack
kubectl apply -k temporal/observability/

# Wait for all pods
kubectl wait --for=condition=ready pod --all -n observability --timeout=300s

# Check pod status
kubectl get pods -n observability

# Expected output:
# NAME                               READY   STATUS    RESTARTS   AGE
# alertmanager-0                     1/1     Running   0          2m
# alertmanager-1                     1/1     Running   0          2m
# alertmanager-2                     1/1     Running   0          2m
# grafana-xxx                        1/1     Running   0          2m
# jaeger-agent-xxx                   1/1     Running   0          2m
# jaeger-collector-xxx               1/1     Running   0          2m
# jaeger-query-xxx                   1/1     Running   0          2m
# loki-0                             1/1     Running   0          2m
# prometheus-0                       2/2     Running   0          2m
# promtail-xxx                       1/1     Running   0          2m
# thanos-compactor-xxx               1/1     Running   0          2m
# thanos-query-xxx                   1/1     Running   0          2m
# thanos-store-xxx                   1/1     Running   0          2m
```

## Test Metrics Collection

```bash
# Port forward Prometheus
kubectl port-forward -n observability svc/prometheus 9090:9090 &

# Query for up metrics
curl -s 'http://localhost:9090/api/v1/query?query=up' | jq .

# Query for agent metrics (if exporters are running)
curl -s 'http://localhost:9090/api/v1/query?query=agent_tasks_total' | jq .

# Check Prometheus targets
curl -s 'http://localhost:9090/api/v1/targets' | jq '.data.activeTargets[] | {job, health}'
```

## Test Log Collection

```bash
# Port forward Loki
kubectl port-forward -n observability svc/loki 3100:3100 &

# Query logs
curl -s 'http://localhost:3100/loki/api/v1/query?query={job="varlogs"}' | jq .

# Test log ingestion
curl -v -H "Content-Type: application/json" -XPOST -s \
  "http://localhost:3100/loki/api/v1/push" \
  --data-raw '{"streams": [{"stream": {"job": "test"}, "values": [["'$(date +%s)'000000000", "test log message"]]}]}'
```

## Test Tracing

```bash
# Port forward Jaeger
kubectl port-forward -n observability svc/jaeger-query 16686:16686 &

# Send test trace
curl -X POST http://localhost:14268/api/traces \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{
      "traceID": "test-trace-1",
      "spans": [{
        "traceID": "test-trace-1",
        "spanID": "span-1",
        "operationName": "test-operation",
        "startTime": '$(date +%s)'000000,
        "duration": 1000000
      }]
    }]
  }'

# Query traces
curl -s "http://localhost:16686/api/traces?service=test-service" | jq .
```

## Test Alerting

```bash
# Port forward AlertManager
kubectl port-forward -n observability svc/alertmanager 9093:9093 &

# Send test alert
curl -X POST http://localhost:9093/api/v2/alerts \
  -H "Content-Type: application/json" \
  -d '[{
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning"
    },
    "annotations": {
      "summary": "Test alert",
      "description": "This is a test alert"
    }
  }]'

# Check active alerts
curl -s http://localhost:9093/api/v2/alerts | jq .

# Check AlertManager status
curl -s http://localhost:9093/api/v2/status | jq .
```

## Test Grafana Dashboards

```bash
# Port forward Grafana
kubectl port-forward -n observability svc/grafana 3000:3000 &

# Login and get API key (manual step)
# Visit http://localhost:3000 and login with admin/admin

# List datasources
curl -s -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:3000/api/datasources | jq .

# Test Prometheus datasource
curl -s -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:3000/api/datasources/proxy/1/api/v1/query?query=up | jq .

# List dashboards
curl -s -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:3000/api/search | jq .
```

## Run Metric Exporters

```bash
# Install dependencies
cd temporal/observability/exporters
pip install -r requirements.txt

# Run agent exporter (terminal 1)
export AGENT_ID=agent-test-001
export REGION=us-east-1
export ZONE=us-east-1a
python agent_exporter.py

# Run workflow exporter (terminal 2)
python workflow_exporter.py

# Test exporters
curl http://localhost:8080/metrics  # Agent metrics
curl http://localhost:9091/metrics  # Workflow metrics
```

## Integration Test

```bash
#!/bin/bash
# integration-test.sh

echo "Testing Observability Stack Integration..."

# 1. Generate metrics
curl -s http://localhost:8080/metrics > /dev/null
curl -s http://localhost:9091/metrics > /dev/null

# 2. Wait for Prometheus to scrape
sleep 30

# 3. Query Prometheus for scraped metrics
AGENT_METRICS=$(curl -s 'http://localhost:9090/api/v1/query?query=up{job="agents"}' | jq -r '.data.result[0].value[1]')
echo "Agent metrics scraped: $AGENT_METRICS"

# 4. Generate logs
curl -X POST http://localhost:3100/loki/api/v1/push \
  -H "Content-Type: application/json" \
  -d '{"streams": [{"stream": {"job": "test"}, "values": [["'$(date +%s)'000000000", "integration test log"]]}]}'

# 5. Wait for log ingestion
sleep 10

# 6. Query logs
LOGS=$(curl -s 'http://localhost:3100/loki/api/v1/query?query={job="test"}' | jq -r '.data.result | length')
echo "Logs found: $LOGS"

# 7. Check Grafana datasources
DATASOURCES=$(curl -s http://localhost:3000/api/datasources | jq -r '. | length')
echo "Grafana datasources configured: $DATASOURCES"

echo "Integration test complete!"
```

## Load Testing

```bash
# Generate load for testing
for i in {1..1000}; do
  # Simulate agent metrics
  curl -s http://localhost:8080/metrics > /dev/null &
  
  # Simulate workflow metrics
  curl -s http://localhost:9091/metrics > /dev/null &
  
  # Generate logs
  curl -s -X POST http://localhost:3100/loki/api/v1/push \
    -H "Content-Type: application/json" \
    -d '{"streams": [{"stream": {"job": "loadtest"}, "values": [["'$(date +%s)'000000000", "load test '$i'"]]}]}' &
done

wait
echo "Load test complete"
```

## Performance Validation

```bash
# Check Prometheus query performance
time curl -s 'http://localhost:9090/api/v1/query_range?query=rate(agent_tasks_total[5m])&start='$(date -d '1 hour ago' +%s)'&end='$(date +%s)'&step=15' > /dev/null

# Check Loki query performance
time curl -s 'http://localhost:3100/loki/api/v1/query_range?query={job="test"}&start='$(date -d '1 hour ago' +%s)'000000000&end='$(date +%s)'000000000' > /dev/null

# Check Jaeger query performance
time curl -s 'http://localhost:16686/api/traces?service=test-service&limit=100' > /dev/null
```

## Cleanup

```bash
# Docker Compose
docker-compose down -v

# Kubernetes
kubectl delete -k temporal/observability/
kubectl delete namespace observability
```

## Troubleshooting Tests

### Prometheus not scraping
```bash
# Check Prometheus config
kubectl exec -n observability statefulset/prometheus-0 -c prometheus -- \
  cat /etc/prometheus/prometheus.yml

# Check service discovery
kubectl exec -n observability statefulset/prometheus-0 -c prometheus -- \
  wget -qO- http://localhost:9090/api/v1/targets
```

### Loki not receiving logs
```bash
# Check Loki logs
kubectl logs -n observability statefulset/loki-0

# Check Promtail
kubectl logs -n observability daemonset/promtail
```

### Grafana datasource connection failed
```bash
# Test from Grafana pod
kubectl exec -n observability deployment/grafana -- \
  wget -qO- http://prometheus:9090/-/healthy
```

### Alerts not firing
```bash
# Check Prometheus rules
kubectl exec -n observability statefulset/prometheus-0 -c prometheus -- \
  wget -qO- http://localhost:9090/api/v1/rules

# Force alert evaluation
kubectl exec -n observability statefulset/prometheus-0 -c prometheus -- \
  wget -qO- --post-data='' http://localhost:9090/-/reload
```
