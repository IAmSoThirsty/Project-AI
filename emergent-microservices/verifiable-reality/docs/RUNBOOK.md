# Runbook

## Verifiable Reality Infrastructure (Post-AI Proof Layer) - Operational Procedures

### Common Operations

#### Check Service Health
```bash
curl https://Verifiable Reality Infrastructure (Post-AI Proof Layer).example.com/health
```

#### View Logs
```bash
kubectl logs -f deployment/Verifiable Reality Infrastructure (Post-AI Proof Layer) -n production
```

#### Check Metrics
```bash
curl https://Verifiable Reality Infrastructure (Post-AI Proof Layer).example.com/metrics
```

#### Scale Service
```bash
kubectl scale deployment/Verifiable Reality Infrastructure (Post-AI Proof Layer) --replicas=5 -n production
```

### Troubleshooting

#### Service Not Starting

1. Check logs:
```bash
kubectl logs deployment/Verifiable Reality Infrastructure (Post-AI Proof Layer) -n production --tail=100
```

2. Check configuration:
```bash
kubectl get configmap Verifiable Reality Infrastructure (Post-AI Proof Layer)-config -o yaml
kubectl get secret Verifiable Reality Infrastructure (Post-AI Proof Layer)-secrets -o yaml
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
kubectl rollout undo deployment/Verifiable Reality Infrastructure (Post-AI Proof Layer) -n production
```

#### Drain Traffic from Pod
```bash
kubectl cordon <node-name>
kubectl drain <node-name> --ignore-daemonsets
```

#### Emergency Scale Down
```bash
kubectl scale deployment/Verifiable Reality Infrastructure (Post-AI Proof Layer) --replicas=0 -n production
```
