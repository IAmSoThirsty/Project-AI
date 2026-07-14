# Health Monitoring & SLO Dashboard Configuration

This Helm values configuration sets up Prometheus, Grafana, and custom dashboards for monitoring Project-AI governance and operational health.

```yaml
monitoring:
  enabled: true
  
  prometheus:
    enabled: true
    retention: 30d
    replicas: 2
    resources:
      requests:
        memory: "512Mi"
        cpu: "250m"
      limits:
        memory: "1Gi"
        cpu: "500m"
    
    alertRules:
      - alert: APIHighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        annotations:
          summary: "API error rate > 5%"
      
      - alert: VerdictLongLatency
        expr: histogram_quantile(0.95, governance_verdict_duration_seconds) > 5
        for: 10m
        annotations:
          summary: "Verdict processing latency > 5s (p95)"
      
      - alert: AuditChainBroken
        expr: increase(audit_chain_breaks_total[5m]) > 0
        for: 1m
        annotations:
          summary: "Audit chain integrity violation detected"
      
      - alert: ServiceDown
        expr: up{job=~"project-ai-.*"} == 0
        for: 2m
        annotations:
          summary: "Service {{ $labels.job }} is down"

  grafana:
    enabled: true
    replicas: 1
    adminPassword: ${GRAFANA_ADMIN_PASSWORD}
    datasources:
      - name: Prometheus
        type: prometheus
        url: http://prometheus:9090
        isDefault: true
      
      - name: Loki
        type: loki
        url: http://loki:3100
    
    dashboards:
      governance:
        title: "Constitutional Governance"
        panels:
          - title: "Verdicts per minute"
            targets:
              - expr: rate(governance_verdicts_total[1m])
          
          - title: "Verdict decisions (stacked)"
            targets:
              - expr: rate(governance_verdicts_total{status="ALLOW"}[5m])
                legend: "ALLOW"
              - expr: rate(governance_verdicts_total{status="DENY"}[5m])
                legend: "DENY"
              - expr: rate(governance_verdicts_total{status="ESCALATE"}[5m])
                legend: "ESCALATE"
          
          - title: "Triumvirate consensus time (p95)"
            targets:
              - expr: histogram_quantile(0.95, governance_verdict_duration_seconds)
          
          - title: "Policy violations (24h)"
            targets:
              - expr: increase(governance_policy_violations_total[24h])
      
      audit:
        title: "Audit Trail & Security"
        panels:
          - title: "Audit log size (GB)"
            targets:
              - expr: project_ai_audit_chain_size_bytes / 1e9
          
          - title: "Audit chain integrity checks (success rate)"
            targets:
              - expr: rate(audit_chain_verification_total{status="success"}[5m]) / rate(audit_chain_verification_total[5m])
          
          - title: "Recent audit events"
            targets:
              - expr: topk(10, increase(audit_events_total[5m]))
          
          - title: "Cryptographic signature verification failures (24h)"
            targets:
              - expr: increase(audit_signature_failures_total[24h])
      
      operational:
        title: "Operational Health"
        panels:
          - title: "API request rate"
            targets:
              - expr: rate(http_requests_total[1m])
          
          - title: "API latency (p50, p95, p99)"
            targets:
              - expr: histogram_quantile(0.50, http_request_duration_seconds)
                legend: "p50"
              - expr: histogram_quantile(0.95, http_request_duration_seconds)
                legend: "p95"
              - expr: histogram_quantile(0.99, http_request_duration_seconds)
                legend: "p99"
          
          - title: "HTTP status codes"
            targets:
              - expr: rate(http_requests_total[5m]) by (status)
          
          - title: "Service health (up/down)"
            targets:
              - expr: up{job=~"project-ai-.*"}
          
          - title: "Container resource usage"
            targets:
              - expr: container_memory_usage_bytes{pod=~"project-ai-.*"}
                legend: "Memory"
              - expr: rate(container_cpu_usage_seconds_total{pod=~"project-ai-.*"}[5m])
                legend: "CPU"
          
          - title: "Restart count (24h)"
            targets:
              - expr: increase(kube_pod_container_status_restarts_total{pod=~"project-ai-.*"}[24h])
      
      memory:
        title: "CCMA Memory System"
        panels:
          - title: "Memory domain sizes"
            targets:
              - expr: project_ai_memory_domain_size_bytes by (domain)
          
          - title: "Memory retrieval latency (p95)"
            targets:
              - expr: histogram_quantile(0.95, project_ai_memory_retrieval_duration_seconds)
          
          - title: "Memory garbage collection runs"
            targets:
              - expr: rate(project_ai_memory_gc_runs_total[5m])
          
          - title: "Active memory sessions"
            targets:
              - expr: project_ai_memory_active_sessions

  loki:
    enabled: true
    retention: 7d
    replicas: 1
    resources:
      requests:
        memory: "256Mi"
        cpu: "100m"

  slos:
    api_availability:
      target: 99.9
      window: 30d
      alert_threshold: 99.0
      metric: "up{job='project-ai-api'}"
    
    verdict_latency:
      target: p95 < 2s
      window: 30d
      alert_threshold: p95 > 3s
      metric: "histogram_quantile(0.95, governance_verdict_duration_seconds)"
    
    audit_chain_integrity:
      target: 100.0%
      window: 30d
      alert_threshold: "any failures"
      metric: "audit_chain_verification_total{status='failure'}"
    
    governance_policy_adherence:
      target: 100.0%
      window: 30d
      alert_threshold: "> 0 violations"
      metric: "increase(governance_policy_violations_total[24h])"
```

## Usage

### Enable in Deployment

```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.monitoring.yaml \
  --set monitoring.enabled=true \
  --set grafana.adminPassword=$(openssl rand -base64 16)
```

### View Dashboards

1. **Governance Dashboard**: http://grafana:3000/d/governance
   - Verdict rate, decision distribution, consensus time
   - Policy violations and Triumvirate performance

2. **Audit Dashboard**: http://grafana:3000/d/audit
   - Audit trail size, chain integrity, recent events
   - Signature verification failures

3. **Operational Dashboard**: http://grafana:3000/d/operational
   - API request rate and latency
   - Service health and restarts
   - Container resource usage

4. **Memory Dashboard**: http://grafana:3000/d/memory
   - CCMA memory domain sizes
   - Retrieval performance
   - Garbage collection activity

### SLO Tracking

All SLOs are tracked in Prometheus and visualized in the SLO dashboard. Error budgets are calculated as:

```
Error Budget = (1 - Target) × Time Window
```

Example: 99.9% target over 30 days = 0.1% × 30d = 43 minutes of downtime allowed

When error budget is consumed, automated alerts trigger for investigation and remediation.

### Alert Examples

- **API High Error Rate**: Error rate > 5% for 5 minutes
- **Verdict Long Latency**: p95 latency > 5 seconds for 10 minutes
- **Audit Chain Broken**: Any chain integrity violation
- **Service Down**: Any core service unreachable for 2+ minutes

Configure alert routing in `alertmanager.yaml` to send to your incident management system.
