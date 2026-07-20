# Alerting Implementation Report

> **Current release boundary (2026-07-19):** This is a historical or
> implementation-reference artifact, not current production evidence or
> deployment approval. The v0.0.3 successor remains fail-closed until the
> [pre-deployment checklist](../../deployment/PRE_DEPLOYMENT_CHECKLIST.md) and
> [CAB evidence bundle](../cab/PROJECT_AI_V0.0.3_SUCCESSOR_CAB_REVIEW_PACK.md)
> pass. Commands here are examples; this document does not prove deployment.

## Overview

Implemented **alerting layer** via PrometheusRule. Alert rules trigger notifications on critical events: pod failures, high error rates, resource exhaustion.

## Files Created

### 1. `helm/project-ai/templates/prometheusrule.yaml` (NEW)
- 5 PrometheusRules for critical alerts
- Pod health, error rate, latency, storage, restart monitoring
- Conditional creation via `alerting.enabled` flag

## Alert Rules

### Critical Alerts

1. **ProjectAIPodDown** (5m threshold)
   - Triggers when pod not running for 5 minutes
   - Severity: CRITICAL
   - Action: Page oncall immediately

2. **ProjectAIHighErrorRate** (5% threshold)
   - Triggers on error rate > 5% for 5 minutes
   - Severity: WARNING
   - Action: Investigate API logs

3. **ProjectAIHighLatency** (1s p99 threshold)
   - Triggers on p99 latency > 1 second
   - Severity: WARNING
   - Action: Check node resources

4. **ProjectAIPVCAlmostFull** (80% threshold)
   - Triggers when storage > 80%
   - Severity: WARNING
   - Action: Expand PVC before full

5. **ProjectAIPodRestartingTooOften** (0.1/hour threshold)
   - Triggers on restart rate > 0.1/hour
   - Severity: WARNING
   - Action: Investigate pod crashes

## Notification Channels

Configure in Alertmanager:

```yaml
route:
  receiver: 'team-oncall'
  group_by: ['severity', 'component']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

receivers:
  - name: 'team-oncall'
    email_configs:
      - to: 'oncall@example.com'
    slack_configs:
      - api_url: 'https://hooks.slack.com/...'
        channel: '#alerts'
    pagerduty_configs:
      - service_key: '...'
```

## Deployment

**Prerequisites:**
```bash
# Install Prometheus operator with Alertmanager
helm install prometheus-operator prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace
```

**Deploy with Alerting:**
```bash
helm install project-ai ./helm/project-ai \
  -f helm/values.prod.yaml \
  --set alerting.enabled=true \
  -n project-ai-prod
```

## Verification

```bash
# Check PrometheusRule created
kubectl get prometheusrule -n project-ai-prod

# Test alert firing (simulate pod failure)
kubectl delete pod -n project-ai-prod <pod-name>

# Check Prometheus alerts
kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090
# Visit: http://localhost:9090/alerts
```

## References

- PrometheusRule: https://prometheus-operator.dev/docs/operator/api/#prometheusrule
- Alertmanager: https://prometheus.io/docs/alerting/latest/alertmanager/
