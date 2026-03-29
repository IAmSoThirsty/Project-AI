# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: dark-fiber-relay / RUNBOOK.md
# ============================================================================ #
# Runbook

## Dark-Fiber Relay - Operational Procedures

### Common Operations

#### Check Service Health
```bash
curl https://Dark-Fiber Relay.example.com/health
```

#### View Logs
```bash
kubectl logs -f deployment/Dark-Fiber Relay -n production
```

#### Check Metrics
```bash
curl https://Dark-Fiber Relay.example.com/metrics
```

#### Scale Service
```bash
kubectl scale deployment/Dark-Fiber Relay --replicas=5 -n production
```

### Troubleshooting

#### Service Not Starting

1. Check logs:
```bash
kubectl logs deployment/Dark-Fiber Relay -n production --tail=100
```

2. Check configuration:
```bash
kubectl get configmap Dark-Fiber Relay-config -o yaml
kubectl get secret Dark-Fiber Relay-secrets -o yaml
```

3. Check database connection

#### High Error Rate

1. Check error metrics in Grafana
2. Review recent deployments
3. Check database performance
4. Consider rollback if recent deployment

#### High Latency

1. Check CPU/memory usage
2. Review database query performance  
3. Check external API latency
4. Scale horizontally if needed

### Emergency Procedures

#### Rollback Deployment
```bash
kubectl rollout undo deployment/Dark-Fiber Relay -n production
```

#### Drain Traffic from Pod
```bash
kubectl cordon <node-name>
kubectl drain <node-name> --ignore-daemonsets
```

#### Emergency Scale Down
```bash
kubectl scale deployment/Dark-Fiber Relay --replicas=0 -n production
```
