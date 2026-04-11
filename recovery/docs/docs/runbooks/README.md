# Operational Runbooks Index

## Overview

This directory contains comprehensive operational runbooks for the Sovereign Governance Substrate platform. All runbooks are derived from actual infrastructure configurations and deployment artifacts.

## Quick Navigation

### Core Runbooks

- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Complete deployment procedures for all environments
- **[K8S_OPERATIONS.md](K8S_OPERATIONS.md)** - Kubernetes operational procedures
- **[DOCKER_OPERATIONS.md](DOCKER_OPERATIONS.md)** - Docker and Docker Compose operations
- **[MICROSERVICES_RUNBOOK.md](MICROSERVICES_RUNBOOK.md)** - Operations for 8 governance microservices
- **[INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md)** - Incident response and recovery procedures

### Service-Specific Runbooks

- **[services/ai-mutation-governance-firewall/](services/ai-mutation-governance-firewall/)** - Mutation Firewall operations
- **[services/autonomous-incident-reflex-system/](services/autonomous-incident-reflex-system/)** - Incident Reflex operations
- **[services/trust-graph-engine/](services/trust-graph-engine/)** - Trust Graph operations
- **[services/sovereign-data-vault/](services/sovereign-data-vault/)** - Data Vault operations
- **[services/autonomous-negotiation-agent/](services/autonomous-negotiation-agent/)** - Negotiation Agent operations
- **[services/autonomous-compliance/](services/autonomous-compliance/)** - Compliance Engine operations
- **[services/verifiable-reality/](services/verifiable-reality/)** - Verifiable Reality operations

### Existing P0 Runbooks

- **[../../P0_RUNBOOKS/k8s-secrets-encryption-guide.md](../../P0_RUNBOOKS/k8s-secrets-encryption-guide.md)** - Kubernetes secrets management
- **[../../P0_RUNBOOKS/keypair-rotation-procedure.md](../../P0_RUNBOOKS/keypair-rotation-procedure.md)** - Cryptographic key rotation
- **[../../P0_RUNBOOKS/postgresql-wal-backup-setup.md](../../P0_RUNBOOKS/postgresql-wal-backup-setup.md)** - Database backup procedures

## Runbook Categories

### 1. Deployment Operations

**Purpose**: Procedures for deploying the platform across environments

**Key Procedures**:

- Docker Compose deployment (development/local)
- Kubernetes deployment with Kustomize (staging/production)
- Helm deployment (alternative)
- Environment configuration
- Pre-deployment validation
- Post-deployment verification
- Rollback procedures

**Target Audience**: DevOps Engineers, SRE Team

**Related Files**:

- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- [../../deploy.sh](../../deploy.sh)
- [../../k8s/deploy.sh](../../k8s/deploy.sh)
- [../../rollback.sh](../../rollback.sh)

---

### 2. Kubernetes Operations

**Purpose**: Day-to-day Kubernetes cluster operations

**Key Procedures**:

- Service scaling (manual and auto)
- Rolling updates and rollbacks
- Configuration management (ConfigMaps, Secrets)
- Database operations (PostgreSQL, Redis)
- Network troubleshooting
- Resource monitoring
- Health checks
- Maintenance tasks

**Target Audience**: SRE Team, Platform Engineers

**Related Files**:

- [K8S_OPERATIONS.md](K8S_OPERATIONS.md)
- [../../k8s/base/](../../k8s/base/)
- [../../k8s/overlays/](../../k8s/overlays/)

---

### 3. Docker Operations

**Purpose**: Container management and Docker Compose operations

**Key Procedures**:

- Container lifecycle management (start/stop/restart)
- Build operations and optimization
- Registry operations (push/pull)
- Volume management and backups
- Network troubleshooting
- Resource monitoring
- Security scanning
- Performance optimization

**Target Audience**: Developers, DevOps Engineers

**Related Files**:

- [DOCKER_OPERATIONS.md](DOCKER_OPERATIONS.md)
- [../../docker-compose.yml](../../docker-compose.yml)
- [../../Dockerfile](../../Dockerfile)
- [../../Dockerfile.production](../../Dockerfile.production)

---

### 4. Microservices Operations

**Purpose**: Operations for the 8 governance microservices

**Services Covered**:

1. AI Mutation Firewall (port 8011)
2. Incident Reflex System (port 8012)
3. Trust Graph Engine (port 8013)
4. Sovereign Data Vault (port 8014)
5. Negotiation Agent (port 8015)
6. Compliance Engine (port 8016)
7. Verifiable Reality (port 8017)
8. I Believe In You (port 8018)

**Key Procedures**:

- Service start/stop procedures
- Health check monitoring
- Log aggregation and analysis
- Inter-service communication
- Scaling operations
- Performance troubleshooting
- Configuration management

**Target Audience**: SRE Team, Backend Engineers

**Related Files**:

- [MICROSERVICES_RUNBOOK.md](MICROSERVICES_RUNBOOK.md)
- [../../emergent-microservices/](../../emergent-microservices/)
- [../../API_SPECIFICATIONS/](../../API_SPECIFICATIONS/)

---

### 5. Incident Response

**Purpose**: Procedures for detecting, responding to, and recovering from incidents

**Severity Levels**:

- P0 - Critical (RTO: 15 min)
- P1 - High (RTO: 1 hour)
- P2 - Medium (RTO: 4 hours)
- P3 - Low (RTO: 1 day)

**Incident Types**:

- Infrastructure failures
- Application errors
- Performance degradation
- Security incidents
- Data integrity issues
- External dependency failures
- Configuration errors

**Key Procedures**:

- Incident detection and reporting
- Escalation procedures
- Containment strategies
- Root cause analysis
- Recovery playbooks
- Post-incident activities

**Target Audience**: On-call Engineers, SRE Team, Security Team

**Related Files**:

- [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md)
- [../../API_SPECIFICATIONS/autonomous-incident-reflex-system-api.yaml](../../API_SPECIFICATIONS/autonomous-incident-reflex-system-api.yaml)

---

## Infrastructure Components

### Docker Compose Stack

```yaml
Services:

  - project-ai (main application)
  - temporal (workflow engine)
  - temporal-worker
  - prometheus (metrics)
  - alertmanager (alerting)
  - grafana (dashboards)
  - postgres (database)
  - 8 microservices (governance tier)
  - monitoring exporters (node, cadvisor, postgres)

```

### Kubernetes Resources

```
Deployments:

  - project-ai-app (3+ replicas)
  - microservices (1-3 replicas each)
  - monitoring stack

StatefulSets:

  - postgres (primary + replicas)
  - redis-sentinel

Services:

  - LoadBalancer/NodePort/ClusterIP
  
Ingress:

  - HTTP/HTTPS routing
  - TLS termination

Autoscaling:

  - HPA (horizontal pod autoscaling)
  - VPA (vertical pod autoscaling)
  - Cluster autoscaler

```

### Monitoring Stack

- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert routing and notification
- **Exporters**: Node, cAdvisor, PostgreSQL metrics

---

## Common Procedures

### Quick Health Check

```bash

# All services health check

./recovery/runbooks/scripts/health_check_all.sh

# Or manual:

curl http://localhost:8000/health
for port in {8011..8018}; do curl http://localhost:$port/api/v1/health/liveness; done
```

### Emergency Rollback

```bash

# Automated rollback with all checks

./rollback.sh production

# Quick manual rollback (K8s)

kubectl rollout undo deployment/project-ai-app -n production

# Quick manual rollback (Docker)

git checkout v1.0.0 && docker-compose up -d --build
```

### View Aggregated Logs

```bash

# Docker Compose

docker-compose logs -f

# Kubernetes

kubectl logs -l app.kubernetes.io/name=project-ai -n production --tail=100 -f
```

### Check System Health

```bash

# Docker

docker-compose ps
docker stats

# Kubernetes  

kubectl get pods -n production
kubectl top nodes
kubectl top pods -n production
```

---

## Troubleshooting Quick Reference

### Service Not Starting

1. Check logs: `docker-compose logs <service>` or `kubectl logs <pod>`
2. Verify configuration: `docker-compose config` or `kubectl describe pod <pod>`
3. Check dependencies: Database, Redis, network connectivity
4. Review resource limits: CPU, memory, disk

### High Error Rate

1. Check recent deployments: `kubectl rollout history`
2. View error logs: Filter by ERROR level
3. Check metrics: Prometheus error rate queries
4. Consider rollback if persistent

### Performance Issues

1. Check resource usage: `docker stats` or `kubectl top`
2. Review metrics: Response times, throughput
3. Scale up: Increase replicas or resources
4. Investigate slow queries: Database logs

### Database Issues

1. Check connection: `pg_isready` or connection test
2. Verify pool size: Should be ≥ workers * 3
3. Check for long-running queries
4. Consider read replica failover

---

## Maintenance Schedule

### Daily

- Review error logs
- Check system health
- Verify backup completion
- Monitor resource usage

### Weekly

- Review performance metrics
- Check for security updates
- Verify monitoring alerts
- Update runbooks if needed

### Monthly

- Rotate secrets
- Review and clean up old logs
- Update dependencies
- Conduct disaster recovery drill

### Quarterly

- Review all runbooks
- Update contact information
- Audit access controls
- Capacity planning review

---

## Contact Information

### On-Call Rotation

- Primary: Check PagerDuty/Opsgenie
- Secondary: Check PagerDuty/Opsgenie
- Escalation: See [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md)

### Key Personnel

- SRE Team Lead: [Slack: #sre-team]
- Platform Engineering Lead: [Slack: #platform-eng]
- Security Team: [Slack: #security]

### Communication Channels

- **Incidents**: #incidents (Slack)
- **Deployments**: #deployments (Slack)
- **On-Call**: PagerDuty
- **Status Page**: https://status.example.com

---

## Document Maintenance

**Last Updated**: 2026-04-09  
**Maintained By**: SRE Team  
**Review Schedule**: Quarterly  
**Next Review**: 2026-07-09

**Change Log**:

- 2026-04-09: Initial runbook creation from infrastructure salvage
- Future updates tracked in git history

---

## Related Documentation

### Internal Documentation

- [Install Guide](../../INSTALL.md)
- [Quick Start Guide](../../QUICKSTART.md)
- [Contributing Guide](../../CONTRIBUTING.md)
- [Security Policy](../../SECURITY.md)

### External Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

---

## Feedback and Improvements

Found an issue or have a suggestion? 

- Open an issue: [GitHub Issues](../../.github/ISSUE_TEMPLATE/)
- Submit a PR: [Contributing Guide](../../CONTRIBUTING.md)
- Contact SRE Team: #sre-team (Slack)
