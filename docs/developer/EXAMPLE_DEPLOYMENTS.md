# Example Deployments: Production-Ready Security Patterns

**Document Version:** 1.0 **Effective Date:** 2026-02-05 **Status:** Deployment Reference Guide **Target Audience:** DevOps Engineers, System Architects, Security Engineers

______________________________________________________________________

## Overview

These example deployments demonstrate **production-caliber, security-elevated** approaches to running Project-AI across different environments and threat models. Each example includes complete configuration, upgrade paths, rollback procedures, and disaster recovery strategies.

**Deployment is not just about getting code running—it's about creating a resilient, secure, observable, and maintainable system.**

______________________________________________________________________

## Philosophical Question: Deployment as Stewardship

**How do our deployment choices reflect our stewardship and vision?**

Every deployment decision shapes what is possible and what is safe:

- **Minimal deployments** prioritize simplicity and reliability
- **Secured deployments** prioritize defense-in-depth
- **Research sandboxes** prioritize controlled experimentation

**None is inherently "better"—they serve different needs and contexts. The key is intentional choice aligned with your threat model and mission.**

______________________________________________________________________

## Deployment Philosophy

### Design Rules

All example deployments MUST demonstrate:

1. **Upgrade Path:** Clear procedure to move to newer versions
1. **Rollback Path:** Ability to revert to previous version quickly
1. **Disaster Recovery:** Documented restore procedures with RTO/RPO
1. **Monitoring Integration:** Observability from day one
1. **Security Hardening:** Defense-in-depth at every layer

**Why These Rules Matter:**

- Systems without upgrade paths accumulate technical debt
- Systems without rollback paths fear change
- Systems without DR plans are one incident from catastrophe
- Systems without monitoring are flying blind
- Systems without security hardening are already compromised

______________________________________________________________________

## Example 1: Minimal Deployment (Development/PoC)

### Overview

**Goal:** Get Project-AI running quickly for development or proof-of-concept with minimal complexity.

**Trade-offs:**

- ✅ **Simplicity:** Single server, minimal dependencies
- ✅ **Speed:** Running in \<30 minutes
- ⚠️ **Scalability:** Not suitable for production load
- ⚠️ **Availability:** Single point of failure

**Use Cases:**

- Local development
- Feature exploration
- Quick demos
- Learning the system

### Architecture

```
┌─────────────────────────────────────────────┐
│        Single Server (All-in-One)           │
├─────────────────────────────────────────────┤
│                                              │
│  ┌────────────────────────────────────┐   │
│  │      Project-AI Core (Python)       │   │
│  │      - Flask API                    │   │
│  │      - AGI Systems                  │   │
│  │      - CLI                          │   │
│  └────────────────────────────────────┘   │
│                                              │
│  ┌────────────────────────────────────┐   │
│  │    SQLite Database (File-based)     │   │
│  └────────────────────────────────────┘   │
│                                              │
│  ┌────────────────────────────────────┐   │
│  │    Local File Storage (./data)      │   │
│  └────────────────────────────────────┘   │
│                                              │
└─────────────────────────────────────────────┘
```

### Prerequisites

```bash

# System Requirements

- Python 3.11+
- 4GB RAM minimum
- 10GB disk space
- Linux/macOS/Windows with WSL

# Install Dependencies

sudo apt-get update
sudo apt-get install -y python3.11 python3.11-venv git
```

### Installation

```bash

# 1. Clone repository

git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# 2. Create virtual environment

python3.11 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Install dependencies

pip install -r requirements.txt

# 4. Configure environment

cp .env.example .env
nano .env  # Edit: Add OPENAI_API_KEY, HUGGINGFACE_API_KEY

# 5. Initialize database and data directories

python -m src.app.main --init

# 6. Run application

python -m src.app.main
```

### Verification

```bash

# Check health endpoint

curl http://localhost:8000/health

# Expected response:

# {"status":"healthy","version":"1.0.0"}

# Test CLI

python -m src.app.cli user list

# Test GUI (if running desktop version)

# Application window should open with login screen

```

### Upgrade Path

```bash

# 1. Backup data directory

cp -r data/ data.backup.$(date +%Y%m%d)

# 2. Pull latest code

git pull origin main

# 3. Update dependencies

pip install -r requirements.txt --upgrade

# 4. Run migrations (if any)

python -m src.app.main --migrate

# 5. Restart application

# Ctrl+C to stop, then: python -m src.app.main

```

### Rollback Path

```bash

# 1. Stop application (Ctrl+C)

# 2. Revert code to previous version

git checkout <previous-version-tag>

# 3. Restore dependencies

pip install -r requirements.txt

# 4. Restore data (if needed)

rm -rf data/
mv data.backup.YYYYMMDD data/

# 5. Restart application

python -m src.app.main
```

### Disaster Recovery

**Backup Strategy:**

```bash

# Daily backup script

#!/bin/bash

BACKUP_DIR=/backup/project-ai
DATE=$(date +%Y%m%d)

# Backup data directory

tar -czf $BACKUP_DIR/data-$DATE.tar.gz data/

# Backup configuration

cp .env $BACKUP_DIR/.env-$DATE

# Backup database

cp data/users.json $BACKUP_DIR/users-$DATE.json

# Retain last 7 days

find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete
```

**Recovery Procedure:**

```bash

# 1. Fresh clone

git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# 2. Restore data

tar -xzf /backup/project-ai/data-YYYYMMDD.tar.gz

# 3. Restore configuration

cp /backup/project-ai/.env-YYYYMMDD .env

# 4. Resume operation

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.app.main
```

**RTO:** 15 minutes **RPO:** 24 hours (daily backups)

______________________________________________________________________

## Example 2: Secured Advanced Deployment (Production)

### Overview

**Goal:** Production-grade deployment with defense-in-depth, high availability, and comprehensive monitoring.

**Trade-offs:**

- ✅ **Security:** Multiple security layers
- ✅ **Availability:** Redundancy and failover
- ✅ **Observability:** Full monitoring stack
- ⚠️ **Complexity:** Requires DevOps expertise
- ⚠️ **Cost:** Multiple servers and services

**Use Cases:**

- Production deployments
- Enterprise installations
- High-stakes environments
- Regulated industries

### Architecture

```
                          ┌─────────────────┐
                          │  Load Balancer  │
                          │  (TLS Termination)│
                          └────────┬────────┘
                                   │
                    ┌──────────────┴──────────────┐
                    │                              │
           ┌────────▼────────┐          ┌────────▼────────┐
           │   API Server 1  │          │   API Server 2  │
           │   (Read Replica)│          │   (Read Replica)│
           └────────┬────────┘          └────────┬────────┘
                    │                              │
                    └──────────────┬──────────────┘
                                   │
                          ┌────────▼────────┐
                          │  Primary DB      │
                          │  (PostgreSQL)    │
                          └────────┬────────┘
                                   │
                          ┌────────▼────────┐
                          │  Standby DB      │
                          │  (Hot Backup)    │
                          └─────────────────┘

        ┌──────────────────────────────────────────┐
        │         Monitoring Stack                  │
        │  - Prometheus (Metrics)                   │
        │  - Grafana (Dashboards)                   │
        │  - Loki (Logs)                            │
        │  - Alertmanager (Alerts)                  │
        └──────────────────────────────────────────┘
```

### Security Layers

1. **Network Layer:**

   - VPC with private subnets
   - Security groups restricting traffic
   - VPN/bastion for administrative access
   - WAF (Web Application Firewall)

1. **Application Layer:**

   - JWT authentication with short-lived tokens
   - RBAC (Role-Based Access Control)
   - Input validation and sanitization
   - Rate limiting and throttling

1. **Data Layer:**

   - Encryption at rest (AES-256)
   - Encryption in transit (TLS 1.3)
   - Database connection pooling with SSL
   - Secrets management (HashiCorp Vault)

1. **Monitoring Layer:**

   - Security Information and Event Management (SIEM)
   - Intrusion detection system (IDS)
   - Audit logging with tamper-evident storage
   - Real-time anomaly detection

### Installation (Kubernetes)

```yaml

# namespace.yaml

apiVersion: v1
kind: Namespace
metadata:
  name: project-ai-prod
  labels:
    environment: production
---

# configmap.yaml

apiVersion: v1
kind: ConfigMap
metadata:
  name: project-ai-config
  namespace: project-ai-prod
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  MAX_WORKERS: "4"
---

# secrets.yaml (Apply after creating secrets)

# kubectl create secret generic api-keys \

#   --from-literal=openai-key=<key> \

#   --from-literal=hf-key=<key> \

#   -n project-ai-prod

---

# deployment.yaml

apiVersion: apps/v1
kind: Deployment
metadata:
  name: project-ai-api
  namespace: project-ai-prod
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: project-ai-api
  template:
    metadata:
      labels:
        app: project-ai-api
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
    spec:
      serviceAccountName: project-ai-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
        seccompProfile:
          type: RuntimeDefault
      containers:

      - name: api

        image: project-ai/core:v1.0.0
        imagePullPolicy: Always
        ports:

        - containerPort: 8000

          name: http
        env:

        - name: OPENAI_API_KEY

          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai-key

        - name: HUGGINGFACE_API_KEY

          valueFrom:
            secretKeyRef:
              name: api-keys
              key: hf-key
        envFrom:

        - configMapRef:

            name: project-ai-config
        resources:
          requests:
            cpu: "1000m"
            memory: "2Gi"
          limits:
            cpu: "2000m"
            memory: "4Gi"
        livenessProbe:
          httpGet:
            path: /health/live
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop: ["ALL"]
        volumeMounts:

        - name: data

          mountPath: /app/data

        - name: tmp

          mountPath: /tmp
      volumes:

      - name: data

        persistentVolumeClaim:
          claimName: project-ai-data

      - name: tmp

        emptyDir: {}
---

# service.yaml

apiVersion: v1
kind: Service
metadata:
  name: project-ai-api
  namespace: project-ai-prod
spec:
  type: ClusterIP
  ports:

  - port: 80

    targetPort: 8000
    protocol: TCP
  selector:
    app: project-ai-api
---

# ingress.yaml

apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: project-ai-ingress
  namespace: project-ai-prod
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:

  - hosts:
    - api.project-ai.example.com

    secretName: project-ai-tls
  rules:

  - host: api.project-ai.example.com

    http:
      paths:

      - path: /

        pathType: Prefix
        backend:
          service:
            name: project-ai-api
            port:
              number: 80
---

# networkpolicy.yaml

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: project-ai-network-policy
  namespace: project-ai-prod
spec:
  podSelector:
    matchLabels:
      app: project-ai-api
  policyTypes:

  - Ingress
  - Egress

  ingress:

  - from:
    - namespaceSelector:

        matchLabels:
          name: ingress-nginx
    ports:

    - protocol: TCP

      port: 8000
  egress:

  - to:
    - namespaceSelector: {}

      podSelector:
        matchLabels:
          app: postgresql
    ports:

    - protocol: TCP

      port: 5432

  - to:
    - namespaceSelector:

        matchLabels:
          name: kube-system
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:

    - protocol: UDP

      port: 53
```

### Upgrade Path

```bash

# 1. Deploy to staging first

kubectl apply -f k8s/staging/ -n project-ai-staging

# 2. Run smoke tests

./scripts/smoke-test.sh project-ai-staging

# 3. Canary deployment (10% of traffic)

kubectl set image deployment/project-ai-api \
  api=project-ai/core:v1.1.0 \
  -n project-ai-prod
kubectl scale deployment/project-ai-api --replicas=1 -n project-ai-prod

# Deploy new version alongside old

kubectl apply -f k8s/canary/deployment.yaml -n project-ai-prod

# 4. Monitor metrics for 30 minutes

# Watch error rates, latency, resource usage

# 5. Gradual rollout

kubectl scale deployment/project-ai-api-canary --replicas=3 -n project-ai-prod
kubectl scale deployment/project-ai-api --replicas=0 -n project-ai-prod

# 6. Finalize

kubectl delete deployment/project-ai-api-old -n project-ai-prod
```

### Rollback Path

```bash

# Immediate rollback (emergency)

kubectl rollout undo deployment/project-ai-api -n project-ai-prod

# Verify rollback success

kubectl rollout status deployment/project-ai-api -n project-ai-prod

# Rollback to specific version

kubectl rollout history deployment/project-ai-api -n project-ai-prod
kubectl rollout undo deployment/project-ai-api --to-revision=N -n project-ai-prod
```

### Disaster Recovery

**Automated Backup:**

```yaml

# backup-cronjob.yaml

apiVersion: batch/v1
kind: CronJob
metadata:
  name: database-backup
  namespace: project-ai-prod
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:

          - name: backup

            image: postgres:15
            env:

            - name: PGPASSWORD

              valueFrom:
                secretKeyRef:
                  name: db-credentials
                  key: password
            command:

            - /bin/bash
            - -c
            - |

              pg_dump -h postgres -U project_ai project_ai | \
              gzip > /backup/db-$(date +%Y%m%d-%H%M%S).sql.gz
              aws s3 cp /backup/ s3://project-ai-backups/ --recursive
            volumeMounts:

            - name: backup

              mountPath: /backup
          volumes:

          - name: backup

            emptyDir: {}
          restartPolicy: OnFailure
```

**Recovery Procedure:**

```bash

# 1. Restore from S3 backup

aws s3 cp s3://project-ai-backups/db-TIMESTAMP.sql.gz .
gunzip db-TIMESTAMP.sql.gz

# 2. Restore to database

kubectl exec -it postgres-0 -n project-ai-prod -- psql -U project_ai -d project_ai < db-TIMESTAMP.sql

# 3. Verify data integrity

kubectl exec -it postgres-0 -n project-ai-prod -- psql -U project_ai -d project_ai -c "SELECT COUNT(*) FROM users;"

# 4. Resume traffic

kubectl scale deployment/project-ai-api --replicas=3 -n project-ai-prod
```

**RTO:** 5 minutes **RPO:** 24 hours (daily backups)

______________________________________________________________________

## Example 3: Research Sandbox (Controlled Hazard Exposure)

### Overview

**Goal:** Safe environment for testing potentially risky AGI capabilities with strong isolation and monitoring.

**Trade-offs:**

- ✅ **Isolation:** Cannot affect production systems
- ✅ **Monitoring:** All actions logged and reviewable
- ✅ **Rapid Iteration:** Quick deployment of experimental code
- ⚠️ **Limited Resources:** Constrained to prevent runaway processes
- ⚠️ **Ephemeral:** Data may not persist between sessions

**Use Cases:**

- AI safety research
- Red team exercises
- Testing new capabilities
- Adversarial robustness evaluation

### Architecture

```
┌──────────────────────────────────────────────┐
│        Isolated Sandbox Environment           │
├──────────────────────────────────────────────┤
│                                               │
│  ┌─────────────────────────────────────┐    │
│  │     Project-AI (Experimental)        │    │
│  │     - Capability Limits Enforced     │    │
│  │     - Network Egress Restricted      │    │
│  │     - Resource Quotas Applied        │    │
│  └─────────────────────────────────────┘    │
│                                               │
│  ┌─────────────────────────────────────┐    │
│  │     Safety Monitor (Always-On)       │    │
│  │     - Logs all actions               │    │
│  │     - Enforces kill switches         │    │
│  │     - Alerts on violations           │    │
│  └─────────────────────────────────────┘    │
│                                               │
│  ┌─────────────────────────────────────┐    │
│  │     Ephemeral Storage                 │    │
│  │     - Destroyed after session         │    │
│  │     - No persistence by default       │    │
│  └─────────────────────────────────────┘    │
│                                               │
└──────────────────────────────────────────────┘
          │
          │ Audit logs only
          ▼
   ┌──────────────┐
   │ Central Log  │
   │ Repository   │
   └──────────────┘
```

### Installation (Docker Compose)

```yaml

# docker-compose.sandbox.yml

version: '3.8'

services:
  sandbox:
    image: project-ai/core:experimental
    container_name: project-ai-sandbox
    restart: "no"  # Never auto-restart
    environment:
      ENVIRONMENT: sandbox
      CAPABILITY_LIMIT: "restricted"
      NETWORK_EGRESS: "blocked"
      AUTO_SHUTDOWN: "3600"  # 1 hour
    cap_drop:

      - ALL

    cap_add:

      - NET_BIND_SERVICE  # Only needed capability

    security_opt:

      - no-new-privileges:true

    read_only: true
    tmpfs:

      - /tmp:noexec,nosuid,nodev,size=100m

    networks:

      - sandbox_network

    ports:

      - "127.0.0.1:8000:8000"  # Localhost only

    volumes:

      - sandbox_data:/app/data:rw
      - ./sandbox_config:/config:ro

    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 512M

  safety_monitor:
    image: project-ai/safety-monitor:latest
    container_name: safety-monitor
    restart: always
    depends_on:

      - sandbox

    environment:
      MONITORED_CONTAINER: sandbox
      KILL_SWITCH_ENABLED: "true"
      ALERT_WEBHOOK: "${ALERT_WEBHOOK_URL}"
    volumes:

      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./safety_rules.yaml:/config/rules.yaml:ro

    networks:

      - sandbox_network

networks:
  sandbox_network:
    driver: bridge
    internal: true  # No internet access

volumes:
  sandbox_data:
    driver: local
```

### Safety Rules Configuration

```yaml

# safety_rules.yaml

rules:

  - name: "Prevent network egress"

    condition: "network_connections > 0"
    action: "kill_container"
    alert: true

  - name: "Enforce CPU limits"

    condition: "cpu_usage > 95% for 30s"
    action: "throttle"
    alert: true

  - name: "Enforce memory limits"

    condition: "memory_usage > 90%"
    action: "kill_container"
    alert: true

  - name: "Enforce time limits"

    condition: "runtime > 3600s"
    action: "graceful_shutdown"
    alert: false

  - name: "Detect privilege escalation"

    condition: "process_privileges_changed"
    action: "kill_container"
    alert: true

  - name: "Detect Four Laws violation"

    condition: "four_laws_violation_detected"
    action: "kill_container"
    alert: true
```

### Usage

```bash

# Start sandbox

docker-compose -f docker-compose.sandbox.yml up -d

# Access sandbox

docker exec -it project-ai-sandbox bash

# Run experimental code

python /app/experiments/test_new_capability.py

# Monitor logs in real-time

docker logs -f safety-monitor

# Stop sandbox

docker-compose -f docker-compose.sandbox.yml down

# Destroy all data (reset)

docker-compose -f docker-compose.sandbox.yml down -v
```

### Upgrade Path

Sandboxes are ephemeral—no formal upgrade path. Destroy and recreate.

```bash

# Pull latest experimental image

docker pull project-ai/core:experimental

# Destroy old sandbox

docker-compose -f docker-compose.sandbox.yml down -v

# Start fresh sandbox

docker-compose -f docker-compose.sandbox.yml up -d
```

### Rollback Path

Not applicable—sandboxes are isolated and disposable.

### Disaster Recovery

**No Recovery Needed:**

- Sandboxes are ephemeral by design
- No persistent data worth recovering
- Logs are sent to central repository in real-time
- Compromise of sandbox does not affect production

**If Sandbox is Compromised:**

```bash

# 1. Immediately destroy

docker-compose -f docker-compose.sandbox.yml down -v

# 2. Review logs

grep -r "sandbox" /var/log/project-ai/

# 3. Investigate compromise

# Analyze audit logs to understand attack vector

# 4. Harden defenses

# Update safety_rules.yaml with new protections

# 5. Resume research

docker-compose -f docker-compose.sandbox.yml up -d
```

**RTO:** Immediate (destroy compromised sandbox) **RPO:** N/A (no data to recover)

______________________________________________________________________

## Comparison Matrix

| Feature          | Minimal                 | Secured Advanced | Research Sandbox      |
| ---------------- | ----------------------- | ---------------- | --------------------- |
| **Complexity**   | Low                     | High             | Medium                |
| **Setup Time**   | 30 minutes              | 4-8 hours        | 1 hour                |
| **Cost**         | $0-50/month             | $500-2000/month  | $50-200/month         |
| **Availability** | Single point of failure | 99.9% uptime     | Intentionally limited |
| **Security**     | Basic                   | Defense-in-depth | Maximum isolation     |
| **Monitoring**   | Minimal                 | Comprehensive    | Focused on safety     |
| **Scalability**  | 1-10 users              | 1000s of users   | 1-5 researchers       |
| **Best For**     | Learning, dev           | Production       | Research, testing     |

______________________________________________________________________

## Deployment Checklist

Before deploying ANY configuration, verify:

- [ ] **Backup strategy defined** with tested restore procedures
- [ ] **Monitoring configured** with alerts to on-call staff
- [ ] **Security hardening applied** appropriate to threat model
- [ ] **Upgrade path documented** with rollback procedures
- [ ] **Disaster recovery tested** at least once
- [ ] **Access controls implemented** with least privilege
- [ ] **Secrets management** using secure vault (not environment variables)
- [ ] **Network isolation** appropriate to deployment type
- [ ] **Resource limits enforced** to prevent exhaustion
- [ ] **Audit logging enabled** with tamper-evident storage

______________________________________________________________________

## Conclusion: Intentional Deployment

There is no "one size fits all" deployment. Choose the configuration that matches:

- Your use case and scale
- Your threat model
- Your operational maturity
- Your budget and resources

**The best deployment is the one you understand, can maintain, and can secure.**

______________________________________________________________________

## Additional Resources

- [Infrastructure Production Guide](INFRASTRUCTURE_PRODUCTION_GUIDE.md) - Detailed Kubernetes guide
- [Operator Quickstart](OPERATOR_QUICKSTART.md) - Day-to-day operations
- [AI Safety Overview](AI_SAFETY_OVERVIEW.md) - Safety considerations
- [Security Framework](../security_compliance/AI_SECURITY_FRAMEWORK.md) - Security best practices

______________________________________________________________________

**Document Maintenance:** This document is reviewed quarterly and updated based on operational experience and new deployment patterns.

**Last Updated:** 2026-02-05 **Next Review:** 2026-05-05
