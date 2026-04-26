# Resource Limits Configuration
# Defines production resource constraints for Sovereign Governance Substrate

## Container Resource Limits

### Core Application (project-ai)
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

### Temporal Worker
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### PostgreSQL
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Prometheus
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "250m"
  limits:
    memory: "2Gi"
    cpu: "1000m"
```

### Grafana
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### Microservices (each)
```yaml
resources:
  requests:
    memory: "128Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

## Application Limits

### API Rate Limits
- **Authenticated Users:** 100 requests/minute
- **Anonymous Users:** 10 requests/minute
- **Admin Users:** 1000 requests/minute
- **Burst:** 150% of base limit

### Database Connections
- **Max Connections:** 100
- **Pool Size:** 20
- **Max Overflow:** 10
- **Pool Timeout:** 30s

### File Upload Limits
- **Max File Size:** 100MB
- **Max Request Size:** 110MB
- **Timeout:** 300s

### Memory Limits
- **Python Process:** 2GB heap
- **Request Processing:** 50MB per request
- **Cache Size:** 256MB

### Concurrency Limits
- **Worker Processes:** 4 (default)
- **Worker Threads:** 10 per process
- **Max Concurrent Requests:** 100
- **Queue Size:** 1000

### Temporal Workflow Limits
- **Max Workflow Execution Time:** 24 hours
- **Max Activity Execution Time:** 1 hour
- **Max Workflow History Size:** 50,000 events
- **Max Pending Activities:** 1000

## Network Limits

### Timeouts
- **Connection Timeout:** 10s
- **Read Timeout:** 30s
- **Write Timeout:** 30s
- **Keepalive Timeout:** 75s

### Connection Pools
- **HTTP Pool Size:** 100
- **Database Pool Size:** 20
- **Redis Pool Size:** 50

## Storage Limits

### Persistent Volumes
- **PostgreSQL Data:** 20Gi
- **Prometheus Data:** 50Gi
- **Grafana Data:** 10Gi
- **Application Logs:** 10Gi

### Retention Policies
- **Audit Logs:** 90 days
- **Application Logs:** 30 days
- **Metrics Data:** 15 days
- **Backup Retention:** 30 days

## Monitoring Thresholds

### CPU Alerts
- **Warning:** >70% for 5 minutes
- **Critical:** >90% for 2 minutes

### Memory Alerts
- **Warning:** >75% for 5 minutes
- **Critical:** >90% for 2 minutes

### Disk Alerts
- **Warning:** >75% usage
- **Critical:** >90% usage

### Response Time Alerts
- **Warning:** p95 > 500ms
- **Critical:** p95 > 1000ms

### Error Rate Alerts
- **Warning:** >1% error rate
- **Critical:** >5% error rate

## Auto-Scaling Configuration

### Horizontal Pod Autoscaler (HPA)
```yaml
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

### Vertical Pod Autoscaler (VPA)
```yaml
updateMode: "Auto"
resourcePolicy:
  containerPolicies:
    - containerName: "*"
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 2Gi
```

---

**Last Updated:** 2026-04-10  
**Reviewed By:** Production Qualification Process  
**Status:** APPROVED for production deployment
