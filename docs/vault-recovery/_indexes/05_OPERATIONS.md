---
type: moc
area: operations
priority: P0
status: active
version: "1.0.0"
created: 2025-01-23
updated: 2025-01-23
maintainer: AGENT-019
total_documents: 160+
schema_version: "1.0"
tags:
  - operations
  - deployment
  - monitoring
  - infrastructure
  - moc
aliases:
  - Operations MOC
  - Ops Index
  - DevOps Map
related_mocs:
  - "[[01_ARCHITECTURE]]"
  - "[[02_SECURITY]]"
  - "[[04_DEVELOPMENT]]"
---

# 05 - Operations & Infrastructure MOC

**Purpose:** Comprehensive operational documentation mapping deployment procedures, monitoring systems, incident response, infrastructure management, backup/recovery, scaling strategies, and operational runbooks for Project-AI desktop and web platforms.

**Scope:** Desktop deployment (Docker, launch scripts), web deployment (Vercel, Railway, Heroku, Docker Compose), monitoring & alerting (health checks, log aggregation), incident response (security incidents, system failures), database management (JSON persistence, future PostgreSQL), backup & recovery procedures, and infrastructure as code.

**Audience:** DevOps engineers, site reliability engineers (SREs), system administrators, on-call engineers, infrastructure managers, and anyone deploying or maintaining Project-AI systems.

---

## 🚀 Deployment

### Desktop Deployment

#### Local Deployment (Development)
**Quick Launch Scripts:**
- `launch-desktop.bat` - Windows batch script for quick launch
- `launch-desktop.ps1` - PowerShell script with environment validation
- `python -m src.app.main` - Manual Python module execution

**Prerequisites:**
- Python 3.11+ installed
- Virtual environment activated
- `.env` configured with API keys
- Dependencies installed (`pip install -r requirements.txt`)

**Documents:**
- `deployment-desktop-local.md` - Local desktop deployment [P0, Active]
- `deployment-launch-scripts.md` - Launch script documentation [P1, Active]

#### Docker Deployment (Production)
**Dockerfile:** Multi-stage build for optimized image size
```dockerfile
# Builder stage: Install dependencies
FROM python:3.11-slim as builder
...
# Runtime stage: Minimal production image
FROM python:3.11-slim
COPY --from=builder /app/.venv ./.venv
```

**Docker Compose:**
```yaml
services:
  desktop-app:
    build: .
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    healthcheck:
      test: ["CMD", "python", "-c", "import sys; sys.exit(0)"]
      interval: 30s
```

**Running:**
```bash
# Build and run
docker-compose up --build

# Detached mode
docker-compose up -d

# View logs
docker-compose logs -f desktop-app

# Stop
docker-compose down
```

**Documents:**
- `deployment-docker-desktop.md` - Docker desktop deployment [P1, Active]
- `deployment-docker-compose.md` - Docker Compose configuration [P1, Active]

### Web Deployment

#### Development Deployment
**Backend (Flask):**
```bash
cd web/backend
FLASK_ENV=development flask run --reload  # Port 5000
```

**Frontend (React + Vite):**
```bash
cd web/frontend
npm run dev  # Port 3000
```

**Documents:**
- `deployment-web-development.md` - Web development deployment [P1, Active]

#### Production Deployment

**Docker Compose (Self-Hosted):**
```yaml
services:
  backend:
    build: ./web/backend
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/projectai
    depends_on:
      - db
  frontend:
    build: ./web/frontend
    ports:
      - "80:80"
  db:
    image: postgres:15
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

**Cloud Deployment Options:**
- **Vercel:** Frontend deployment (React app)
- **Railway:** Backend deployment (Flask API + PostgreSQL)
- **Heroku:** Full stack deployment (Backend + Frontend)
- **AWS/GCP/Azure:** Self-managed infrastructure

**Documents:**
- `deployment-web-production.md` - Web production deployment [P1, In-Progress]
- `deployment-docker-compose-web.md` - Web Docker Compose setup [P1, Active]
- `deployment-vercel.md` - Vercel frontend deployment [P2, Planned]
- `deployment-railway.md` - Railway backend deployment [P2, Planned]
- `deployment-heroku.md` - Heroku full stack deployment [P2, Planned]
- `web/DEPLOYMENT.md` - Comprehensive web deployment guide [P1, Active]

### Deployment Workflows

#### Continuous Deployment (CD)
**File:** `.github/workflows/deploy.yml` (planned)

**Deployment Pipeline:**
1. **Build:** Docker image build
2. **Test:** Run integration tests against built image
3. **Push:** Push image to container registry (Docker Hub, GitHub Container Registry)
4. **Deploy:** Deploy to staging environment
5. **Smoke Test:** Run smoke tests against staging
6. **Promote:** Promote to production (manual approval)

**Documents:**
- `deployment-cd-pipeline.md` - CD pipeline configuration [P1, Planned]
- `deployment-staging.md` - Staging environment setup [P1, Planned]
- `deployment-production.md` - Production deployment procedures [P1, Planned]

#### Rollback Procedures
**Strategy:** Blue-green deployment with instant rollback capability

**Rollback Steps:**
1. Detect deployment failure (automated or manual)
2. Route traffic back to previous version (blue environment)
3. Investigate root cause in green environment
4. Fix issue and redeploy
5. Gradually shift traffic to fixed green environment

**Documents:**
- `deployment-rollback.md` - Rollback procedures [P1, Active]
- `deployment-blue-green.md` - Blue-green deployment strategy [P2, Planned]

---

## 📊 Monitoring & Observability

### Health Checks

#### Application Health
**Desktop Health Check:**
- Verify core systems initialized (FourLaws, Persona, Memory)
- Check API connectivity (OpenAI, Hugging Face)
- Validate data directory permissions
- Test database file access (JSON persistence)

**Web Health Check:**
- `/health` endpoint returns HTTP 200
- Database connection pool healthy
- Redis cache responding (if configured)
- External API availability

**Docker Health Check:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Documents:**
- `monitoring-health-checks.md` - Health check implementation [P1, Active]
- `monitoring-health-endpoints.md` - Health endpoint specifications [P1, Planned]

### Logging

#### Log Aggregation
**Current:** File-based logging to `logs/` directory
- `logs/app.log` - Application logs (INFO, WARNING, ERROR, CRITICAL)
- `logs/security.log` - Security audit logs (auth, override, incidents)
- `logs/error.log` - Error logs only (ERROR, CRITICAL)

**Planned:** Centralized log aggregation
- **ELK Stack:** Elasticsearch + Logstash + Kibana
- **Grafana Loki:** Lightweight log aggregation
- **CloudWatch Logs:** AWS-native log management

**Log Format:**
```
2025-01-23 14:32:15,123 - src.app.core.user_manager - INFO - User 'admin' logged in successfully
2025-01-23 14:32:20,456 - src.app.core.ai_systems - WARNING - Learning request denied: inappropriate content
```

**Documents:**
- `monitoring-logging.md` - Logging strategy and configuration [P1, Active]
- `monitoring-log-aggregation.md` - Log aggregation setup [P2, Planned]
- `monitoring-log-retention.md` - Log retention policies [P2, Active]

#### Log Levels
- **DEBUG:** Detailed diagnostic (development only, disabled in production)
- **INFO:** General operational events (login, actions, state changes)
- **WARNING:** Potential issues (failed validations, deprecated usage)
- **ERROR:** Error conditions (handled exceptions, failed operations)
- **CRITICAL:** System failures (unrecoverable errors, security breaches)

**Documents:**
- `monitoring-log-levels.md` - Log level guidelines [P1, Active]

### Metrics & Alerting

#### Key Metrics (Planned)
**Application Metrics:**
- Request rate (requests/second)
- Response time (p50, p95, p99)
- Error rate (errors/total requests)
- AI response latency (OpenAI API calls)
- Image generation time (Stable Diffusion, DALL-E)

**System Metrics:**
- CPU utilization
- Memory usage
- Disk I/O
- Network throughput

**Business Metrics:**
- Active users (daily, monthly)
- AI interactions per user
- Learning requests (approved, denied, Black Vault additions)
- Image generations per day

**Documents:**
- `monitoring-metrics.md` - Metrics collection and tracking [P1, Planned]
- `monitoring-key-metrics.md` - Key performance indicators [P1, Planned]

#### Alerting (Planned)
**Alert Channels:**
- Email notifications
- Slack webhooks
- PagerDuty integration (on-call)
- SMS alerts (critical only)

**Alert Rules:**
- **Critical:** System down, security breach, data loss
- **High:** High error rate (>5%), API failures, database connection loss
- **Medium:** Elevated latency, warning log spikes, low disk space
- **Low:** Informational alerts, usage trends

**Documents:**
- `monitoring-alerting.md` - Alerting strategy and configuration [P1, Planned]
- `monitoring-alert-rules.md` - Alert rule definitions [P1, Planned]
- `monitoring-on-call.md` - On-call procedures and escalation [P2, Planned]

### Tracing & Performance

#### Application Performance Monitoring (APM) (Planned)
**Tools:**
- **New Relic:** Full-stack APM
- **Datadog:** Infrastructure + APM monitoring
- **OpenTelemetry:** Vendor-neutral observability

**Tracing:**
- Request tracing (end-to-end)
- Database query performance
- External API call latency
- AI model inference time

**Documents:**
- `monitoring-apm.md` - APM setup and configuration [P2, Planned]
- `monitoring-tracing.md` - Distributed tracing [P2, Planned]

---

## 🚨 Incident Response

### Incident Management

#### Incident Response Workflow
1. **Detection:** Alert triggered or manual report
2. **Triage:** Assess severity (P0-Critical, P1-High, P2-Medium, P3-Low)
3. **Notification:** Notify on-call engineer and stakeholders
4. **Investigation:** Diagnose root cause, gather evidence
5. **Mitigation:** Implement temporary fix, restore service
6. **Resolution:** Permanent fix deployed, service validated
7. **Post-Mortem:** Document incident, identify improvements
8. **Follow-Up:** Implement preventive measures

**Documents:**
- `runbook-incident-response.md` - Incident response procedures [P0, Active]
- `runbook-incident-workflow.md` - Incident management workflow [P1, Active]
- `runbook-severity-matrix.md` - Incident severity criteria [P1, Active]

### Incident Runbooks

#### Security Incidents
- `runbook-security-incident.md` - Security incident response [P0, Active]
- `runbook-data-breach.md` - Data breach procedures [P0, Active]
- `runbook-unauthorized-access.md` - Unauthorized access response [P0, Active]

#### System Failures
- `runbook-database-failure.md` - Database failure recovery [P0, Active]
- `runbook-api-outage.md` - API service outage response [P1, Active]
- `runbook-disk-full.md` - Disk space emergency procedures [P1, Active]

#### Emergency Procedures
- `runbook-emergency-shutdown.md` - Emergency system shutdown [P0, Active]
- `runbook-credential-rotation.md` - Emergency credential rotation [P0, Active]
- `runbook-backup-restoration.md` - Emergency backup restore [P1, Active]

### Post-Mortem Process

**Post-Mortem Template:**
1. **Incident Summary:** What happened, when, impact
2. **Timeline:** Chronological event sequence
3. **Root Cause:** Why it happened, contributing factors
4. **Resolution:** How it was fixed
5. **Impact:** Users affected, downtime duration, data loss
6. **Lessons Learned:** What went well, what went poorly
7. **Action Items:** Preventive measures, process improvements

**Documents:**
- `runbook-post-mortem.md` - Post-mortem template and process [P1, Active]
- `runbook-action-items.md` - Post-mortem action item tracking [P2, Active]

---

## 💾 Data Management

### Backup & Recovery

#### Backup Strategy
**Desktop Application:**
- **Data Directory:** `data/` (users, AI state, configurations)
  - Backup frequency: Daily incremental, weekly full
  - Retention: 30 daily, 12 weekly, 12 monthly
- **Logs Directory:** `logs/` (application and security logs)
  - Backup frequency: Weekly
  - Retention: 90 days

**Web Application (Planned):**
- **PostgreSQL Database:** Full backup + WAL archiving
  - Backup frequency: Hourly incremental, daily full
  - Retention: 7 daily, 4 weekly, 12 monthly
- **User Uploads:** S3/object storage with versioning
- **Application Logs:** CloudWatch Logs with 90-day retention

**Backup Locations:**
- **Local:** External drive or NAS
- **Cloud:** AWS S3, Google Cloud Storage, Azure Blob Storage

**Documents:**
- `backup-strategy.md` - Backup strategy and policies [P0, Active]
- `backup-desktop.md` - Desktop backup procedures [P0, Active]
- `backup-web.md` - Web platform backup procedures [P1, Planned]

#### Recovery Procedures
**Recovery Time Objective (RTO):** 4 hours (maximum acceptable downtime)  
**Recovery Point Objective (RPO):** 1 hour (maximum acceptable data loss)

**Recovery Steps:**
1. Verify backup integrity
2. Stop affected services
3. Restore data from backup
4. Validate restored data completeness
5. Restart services
6. Run smoke tests
7. Monitor for issues

**Documents:**
- `recovery-procedures.md` - Data recovery procedures [P0, Active]
- `recovery-testing.md` - Backup recovery testing [P1, Active]

### Database Management

#### JSON Persistence (Current)
**Files:**
- `data/users.json` - User profiles, bcrypt hashes
- `data/ai_persona/state.json` - Personality, mood, interaction counts
- `data/memory/knowledge.json` - 6-category knowledge base
- `data/learning_requests/requests.json` - Learning requests with status
- `data/command_override_config.json` - Override states, audit logs

**Maintenance:**
- File permissions: Owner-only (600)
- Atomic writes: Write to temp file, rename on success
- Schema validation: Validate JSON structure on load
- Corruption detection: Checksum verification (planned)

**Documents:**
- `database-json-persistence.md` - JSON persistence architecture [P1, Active]
- `database-json-maintenance.md` - JSON file maintenance [P1, Active]

#### PostgreSQL Migration (Planned)
**Migration Strategy:**
- Dual-write period: Write to JSON + PostgreSQL
- Gradual read migration: Validate PostgreSQL data consistency
- Cutover: Switch to PostgreSQL-only
- JSON deprecation: Archive JSON files after successful migration

**Documents:**
- `database-postgresql-migration.md` - PostgreSQL migration plan [P2, Planned]
- `database-postgresql-setup.md` - PostgreSQL setup and configuration [P2, Planned]

---

## 🏗️ Infrastructure

### Infrastructure as Code (IaC)

#### Docker Infrastructure
**Files:**
- `Dockerfile` - Multi-stage Python application image
- `docker-compose.yml` - Desktop application services
- `web/docker-compose.yml` - Web platform services (backend, frontend, PostgreSQL)

**Docker Best Practices:**
- Multi-stage builds for minimal image size
- Non-root user execution
- Health checks for container orchestration
- Volume mounts for data persistence
- Environment variable configuration

**Documents:**
- `infrastructure-docker.md` - Docker infrastructure [P1, Active]
- `infrastructure-docker-best-practices.md` - Docker best practices [P1, Active]

#### Kubernetes (Planned)
**Resources:**
- Deployments: Application pods with replica sets
- Services: Load balancing and service discovery
- ConfigMaps: Non-sensitive configuration
- Secrets: Sensitive configuration (API keys, passwords)
- Ingress: External traffic routing

**Documents:**
- `infrastructure-kubernetes.md` - Kubernetes deployment [P2, Planned]
- `infrastructure-helm-charts.md` - Helm chart development [P2, Planned]

### Scaling

#### Horizontal Scaling (Web Platform)
**Strategy:** Scale out with load balancing

**Components:**
- **Load Balancer:** Nginx or cloud-native LB
- **Application Servers:** Multiple Flask instances
- **Session Store:** Redis for shared session state
- **Database:** PostgreSQL with read replicas

**Documents:**
- `scaling-horizontal.md` - Horizontal scaling strategy [P2, Planned]
- `scaling-load-balancing.md` - Load balancer configuration [P2, Planned]

#### Vertical Scaling (Desktop)
**Strategy:** Increase resource limits

**Resources:**
- CPU: Increase cores for parallel processing
- Memory: Increase RAM for larger models/datasets
- Disk: Increase storage for data growth

**Documents:**
- `scaling-vertical.md` - Vertical scaling guidelines [P2, Planned]

---

## 📚 Cross-References

### Related MOCs
- [[01_ARCHITECTURE]] - Infrastructure architecture, deployment design
- [[02_SECURITY]] - Security incident response, backup encryption
- [[04_DEVELOPMENT]] - Development deployment, local testing

### Related Indexes
- `by-type/runbook-type-index.md` - All operational runbooks
- `by-priority/p0-critical-priority-index.md` - Critical operational docs
- `cross-reference/operations-dependencies-index.md` - Operations dependencies

---

## 🔍 Quick Reference

### Deployment Checklist (Production)
1. [ ] Environment variables configured
2. [ ] Secrets securely stored (not hardcoded)
3. [ ] Database backups configured and tested
4. [ ] Health checks implemented and tested
5. [ ] Monitoring and alerting configured
6. [ ] Logging configured with appropriate retention
7. [ ] Security scans passed (no critical/high issues)
8. [ ] Load testing completed (expected traffic + 2x)
9. [ ] Rollback plan documented and tested
10. [ ] On-call rotation scheduled

### Incident Response Checklist
1. [ ] Incident detected and severity assessed
2. [ ] On-call engineer notified
3. [ ] Incident channel created (Slack, Teams)
4. [ ] Root cause investigation started
5. [ ] Mitigation implemented (temporary fix)
6. [ ] Service restored and validated
7. [ ] Permanent fix deployed
8. [ ] Post-mortem scheduled within 48 hours
9. [ ] Action items created and assigned
10. [ ] Stakeholders notified of resolution

### Backup Verification Checklist
1. [ ] Backup completed successfully (check logs)
2. [ ] Backup file size reasonable (not 0 bytes)
3. [ ] Backup integrity verified (checksum)
4. [ ] Backup restore tested (sample restoration)
5. [ ] Restored data validated (schema, completeness)
6. [ ] Backup retention policy enforced (old backups deleted)
7. [ ] Backup location secure (encrypted, access-controlled)
8. [ ] Backup documentation updated (location, credentials)

---

## 📊 Statistics

- **Total Operations Documents:** 160+ documents
- **Deployment Targets:** 2 platforms (desktop, web) × 3 environments (dev, staging, prod)
- **Runbooks:** 15+ operational runbooks (security, system, emergency)
- **Backup Strategy:** Daily incremental + weekly full (30-day retention)
- **RTO:** 4 hours (maximum acceptable downtime)
- **RPO:** 1 hour (maximum acceptable data loss)
- **Health Check Interval:** 30 seconds (Docker), 60 seconds (application)
- **Log Retention:** 90 days (application logs), 365 days (security logs)

---

## 🛡️ Governance

**Maintainer:** AGENT-019 (MOC Constructor)  
**Operations Lead:** TBD (assign DevOps team lead)  
**Update Frequency:** Event-driven (deployments, incidents) + monthly review  
**Incident SLA:** P0 (4h), P1 (24h), P2 (7d), P3 (30d)  
**Backup Testing:** Monthly disaster recovery drills  
**Quality Gate:** All runbooks must be tested in non-production environment

---

**Version:** 1.0.0  
**Last Updated:** 2025-01-23  
**Schema Compliance:** ✅ 100%  
**Operational Maturity:** 🟡 Developing (production-ready desktop, web in progress)

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

