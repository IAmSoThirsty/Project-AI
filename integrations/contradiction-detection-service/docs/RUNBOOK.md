# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: contradiction-detection-service / RUNBOOK.md
# ============================================================================ #
# Runbook

## Contradiction Detection Service - Operational Procedures

### Common Operations

#### Check Service Health
```bash
curl https://Contradiction Detection Service.example.com/health
```

#### View Logs
```bash
kubectl logs -f deployment/Contradiction Detection Service -n production
```

#### Check Metrics
```bash
curl https://Contradiction Detection Service.example.com/metrics
```

#### Scale Service
```bash
kubectl scale deployment/Contradiction Detection Service --replicas=5 -n production
```

### Troubleshooting

#### Service Not Starting

1. Check logs:
```bash
kubectl logs deployment/Contradiction Detection Service -n production --tail=100
```

2. Check configuration:
```bash
kubectl get configmap Contradiction Detection Service-config -o yaml
kubectl get secret Contradiction Detection Service-secrets -o yaml
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
kubectl rollout undo deployment/Contradiction Detection Service -n production
```

#### Drain Traffic from Pod
```bash
kubectl cordon <node-name>
kubectl drain <node-name> --ignore-daemonsets
```

#### Emergency Scale Down
```bash
kubectl scale deployment/Contradiction Detection Service --replicas=0 -n production
```
