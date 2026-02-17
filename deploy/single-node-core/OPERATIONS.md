# Production Operations Runbook - Project-AI Core Stack

## Overview

This runbook provides operational procedures for the Project-AI single-node core stack deployment. All procedures are production-tested and ready for immediate use.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Deployment Procedures](#deployment-procedures)
3. [Monitoring and Alerting](#monitoring-and-alerting)
4. [Incident Response](#incident-response)
5. [Backup and Recovery](#backup-and-recovery)
6. [Scaling Procedures](#scaling-procedures)
7. [Security Operations](#security-operations)
8. [Performance Tuning](#performance-tuning)

---

## Quick Reference

### Critical Commands

```bash

# Deploy production stack

DEPLOYMENT_MODE=production ./scripts/deploy.sh

# Check service health

docker compose ps
docker compose logs -f

# Emergency stop

docker compose down

# Full backup

./scripts/backup.sh full

# Restore from backup

./scripts/restore.sh full <timestamp>

# View metrics

curl http://localhost:8001/metrics
```

### Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Orchestrator API | http://localhost:5000 | Main application |
| Health Check | http://localhost:8000/health | Service health |
| Metrics | http://localhost:8001/metrics | Prometheus metrics |
| MCP Gateway | http://localhost:9000 | Agent communication |
| Prometheus | http://localhost:9090 | Metrics database |
| Grafana | http://localhost:3000 | Dashboards |
| AlertManager | http://localhost:9093 | Alert management |

---

## Deployment Procedures

### Initial Deployment

```bash

# 1. Validate configuration

./validate.sh

# 2. Generate secrets

./quickstart.sh --generate-only

# 3. Deploy stack

DEPLOYMENT_MODE=production ./scripts/deploy.sh
```

### Updating Services

```bash

# 1. Backup current state

./scripts/backup.sh full

# 2. Pull latest images

docker compose pull

# 3. Deploy with zero downtime

./scripts/deploy.sh

# 4. Verify deployment

curl http://localhost:8000/health
```

### Rolling Back

```bash

# 1. List available backups

./scripts/restore.sh list

# 2. Stop current services

docker compose down

# 3. Restore from backup

./scripts/restore.sh full <timestamp>

# 4. Verify restoration

docker compose ps
curl http://localhost:8000/health
```

---

## Monitoring and Alerting

### Checking System Health

```bash

# Overall service status

docker compose ps

# Resource usage

docker stats

# Application logs

docker compose logs -f orchestrator

# Database status

docker compose exec postgres psql -U project_ai -c "
SELECT
    datname,
    numbackends as connections,
    xact_commit as commits,
    xact_rollback as rollbacks
FROM pg_stat_database
WHERE datname = 'project_ai';
"

# Redis status

docker compose exec redis redis-cli -a "${REDIS_PASSWORD}" INFO stats
```

### Alert Configuration

Edit `monitoring/alertmanager/alertmanager.yml`:

```yaml
receivers:

  - name: 'critical'

    email_configs:

      - to: 'oncall@example.com'

    slack_configs:

      - channel: '#critical-alerts'

        webhook_url: '${SLACK_WEBHOOK}'
```

Reload configuration:
```bash
docker compose kill -s HUP alertmanager
```

---

## Incident Response

### Service Down

**Symptoms**: Service health check failing, 502/503 errors

**Response**:
```bash

# 1. Check service status

docker compose ps

# 2. Check logs for errors

docker compose logs --tail=100 <service-name>

# 3. Restart service

docker compose restart <service-name>

# 4. If restart fails, check resources

docker stats
df -h
free -h

# 5. Escalate if not resolved in 5 minutes

```

### Database Connection Issues

**Symptoms**: Connection timeouts, "too many connections"

**Response**:
```bash

# 1. Check connection count

docker compose exec postgres psql -U project_ai -c "
SELECT COUNT(*) FROM pg_stat_activity;
"

# 2. Kill idle connections

docker compose exec postgres psql -U project_ai -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND query_start < NOW() - INTERVAL '1 hour';
"

# 3. Check for locks

docker compose exec postgres psql -U project_ai -c "
SELECT * FROM pg_locks WHERE NOT granted;
"

# 4. Restart if necessary

docker compose restart postgres
```

### High Memory Usage

**Symptoms**: OOM errors, slow performance

**Response**:
```bash

# 1. Check memory usage

docker stats --no-stream

# 2. Check container limits

docker inspect <container> | grep -A 10 Memory

# 3. Clear caches

docker compose exec redis redis-cli -a "${REDIS_PASSWORD}" FLUSHDB

# 4. Restart high-memory services

docker compose restart orchestrator

# 5. Increase limits if persistent

# Edit docker-compose.yml:

deploy:
  resources:
    limits:
      memory: 4G  # Increase as needed
```

### Disk Space Full

**Symptoms**: Write failures, service crashes

**Response**:
```bash

# 1. Check disk usage

df -h
du -sh /var/lib/docker/*

# 2. Clean up old Docker resources

docker system prune -a --volumes -f

# 3. Clean old logs

find ./logs -name "*.log" -mtime +7 -delete

# 4. Clean old backups

./scripts/backup.sh cleanup

# 5. Expand disk if needed

```

---

## Backup and Recovery

### Automated Backups

Setup cron job:
```bash

# Edit crontab

crontab -e

# Add daily backup at 2 AM

0 2 * * * cd /path/to/deploy/single-node-core && ./scripts/backup.sh full

# Add weekly verification at 3 AM Sunday

0 3 * * 0 cd /path/to/deploy/single-node-core && ./scripts/backup.sh verify $(ls -t backups/postgres | head -1)
```

### Manual Backup

```bash

# Full backup (all services)

./scripts/backup.sh full

# Individual services

./scripts/backup.sh postgres
./scripts/backup.sh redis
./scripts/backup.sh app

# Verify backup

./scripts/backup.sh verify /path/to/backup.dump.gz.enc
```

### Restore Procedures

```bash

# List available backups

./scripts/restore.sh list

# Full system restore

./scripts/restore.sh full <timestamp>

# Selective restore

./scripts/restore.sh postgres /path/to/backup.dump.gz.enc
./scripts/restore.sh redis /path/to/backup.tar.gz.enc

# Test restore (non-destructive)

# Create test environment and restore there

```

### Disaster Recovery

**Complete system loss recovery**:

```bash

# 1. Install dependencies

curl -fsSL https://get.docker.com | sh

# 2. Clone repository

git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI/deploy/single-node-core

# 3. Restore secrets

# Copy .backup-encryption-key from secure storage

# Copy env/.env from secure storage

# 4. Restore from backup

./scripts/restore.sh full <timestamp>

# 5. Verify restoration

docker compose ps
curl http://localhost:8000/health
```

---

## Scaling Procedures

### Vertical Scaling (More Resources)

```bash

# 1. Stop services

docker compose down

# 2. Edit docker-compose.yml

# Increase resource limits:

deploy:
  resources:
    limits:
      cpus: '8'      # Increase CPU
      memory: 16G    # Increase memory

# 3. Restart services

docker compose up -d

# 4. Verify performance

docker stats
```

### Horizontal Scaling (More Workers)

Add worker services to docker-compose.yml:

```yaml
worker-01:
  <<: *worker-template
  container_name: project-ai-worker-01
  environment:
    WORKER_ID: worker-01

worker-02:
  <<: *worker-template
  container_name: project-ai-worker-02
  environment:
    WORKER_ID: worker-02
```

Deploy:
```bash
docker compose up -d --scale worker=3
```

### Database Scaling

**Read replicas**:
```bash

# Add to docker-compose.yml

postgres-replica:
  image: pgvector/pgvector:pg16
  environment:
    POSTGRES_MASTER_HOST: postgres
    POSTGRES_REPLICATION_MODE: slave
```

**Connection pooling**:
```bash

# Add PgBouncer

pgbouncer:
  image: pgbouncer/pgbouncer
  environment:
    DATABASE_URL: postgres://project_ai:${POSTGRES_PASSWORD}@postgres:5432/project_ai
```

---

## Security Operations

### Rotating Secrets

```bash

# 1. Generate new secrets

python3 << 'EOF'
import secrets
print("NEW_SECRET=" + secrets.token_urlsafe(32))
EOF

# 2. Update env/.env

nano env/.env

# 3. Rolling restart services

docker compose up -d --force-recreate --no-deps orchestrator
docker compose up -d --force-recreate --no-deps mcp-gateway

# 4. Verify functionality

curl http://localhost:8000/health
```

### Security Auditing

```bash

# Check for security vulnerabilities

docker scout cves project-ai:latest

# Review audit logs

docker compose exec postgres psql -U project_ai -c "
SELECT * FROM audit_logs
WHERE severity = 'critical'
ORDER BY created_at DESC
LIMIT 100;
"

# Check failed login attempts

docker compose logs orchestrator | grep "authentication failed"
```

### Network Security

```bash

# Verify network isolation

docker network inspect project-ai-core-network

# Check open ports

netstat -tlnp | grep docker

# Configure firewall

ufw allow 5000/tcp
ufw allow 8000:8001/tcp
ufw deny 5432/tcp  # Block external DB access
ufw deny 6379/tcp  # Block external Redis access
```

---

## Performance Tuning

### Database Optimization

```bash

# Analyze query performance

docker compose exec postgres psql -U project_ai -c "
SELECT
    query,
    calls,
    mean_exec_time / 1000 as mean_seconds,
    total_exec_time / 1000 as total_seconds
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
"

# Vacuum database

docker compose exec postgres psql -U project_ai -c "VACUUM ANALYZE;"

# Rebuild indexes

docker compose exec postgres psql -U project_ai -c "REINDEX DATABASE project_ai;"

# Check cache hit ratio

docker compose exec postgres psql -U project_ai -c "
SELECT
    sum(blks_hit)::float / (sum(blks_hit) + sum(blks_read)) * 100 as cache_hit_ratio
FROM pg_stat_database;
"
```

### Redis Optimization

```bash

# Check memory usage

docker compose exec redis redis-cli -a "${REDIS_PASSWORD}" INFO memory

# Check slow log

docker compose exec redis redis-cli -a "${REDIS_PASSWORD}" SLOWLOG GET 10

# Optimize memory

docker compose exec redis redis-cli -a "${REDIS_PASSWORD}" CONFIG SET maxmemory-policy allkeys-lfu

# Clear unused keys

docker compose exec redis redis-cli -a "${REDIS_PASSWORD}" --scan --pattern "temp:*" | xargs redis-cli -a "${REDIS_PASSWORD}" DEL
```

### Application Tuning

```bash

# Check metrics

curl http://localhost:8001/metrics | grep http_request_duration

# Adjust worker concurrency

# Edit env/.env:

WORKER_CONCURRENCY=8
WORKER_PREFETCH_MULTIPLIER=8

# Restart services

docker compose restart orchestrator
```

---

## Troubleshooting

### Common Issues

#### Issue: Port Already in Use

```bash

# Find process using port

lsof -i :5000

# Kill process

kill -9 <PID>

# Or change port in docker-compose.yml

ports:

  - "5001:5000"  # Map to different host port

```

#### Issue: Permission Denied

```bash

# Fix volume permissions

sudo chown -R $USER:$USER ./data
sudo chmod -R 755 ./data

# Fix Docker socket permissions

sudo usermod -aG docker $USER
newgrp docker
```

#### Issue: Container Keeps Restarting

```bash

# Check logs

docker compose logs --tail=100 <service>

# Check resource limits

docker inspect <container> | grep -A 20 Resources

# Disable restart and debug

docker compose up --no-start
docker compose start <service>
docker compose logs -f <service>
```

---

## Support and Escalation

### Internal Support

1. Check this runbook
2. Review logs: `docker compose logs -f`
3. Check monitoring: http://localhost:3000

### External Support

- GitHub Issues: https://github.com/IAmSoThirsty/Project-AI/issues
- Documentation: `deploy/single-node-core/README.md`

### Emergency Contacts

- On-call engineer: (configure in AlertManager)
- Database admin: (configure in AlertManager)
- Security team: (configure in AlertManager)

---

## Maintenance Windows

### Planned Maintenance

**Schedule**: First Sunday of month, 2-6 AM UTC

**Procedure**:

1. Notify users 48 hours in advance
2. Create backup: `./scripts/backup.sh full`
3. Apply updates: `./scripts/deploy.sh`
4. Run tests: `./scripts/smoke-tests.sh`
5. Monitor for 24 hours
6. Document changes

### Emergency Maintenance

**Trigger**: Critical security patch, data corruption

**Procedure**:

1. Assess impact and urgency
2. Create emergency backup
3. Apply fix
4. Verify functionality
5. Monitor closely
6. Post-mortem within 24 hours

---

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2024-02-12 | Initial production deployment | Project-AI Team |

---

**Last Updated**: 2024-02-12
**Version**: 1.0.0
**Maintained by**: Project-AI Operations Team
