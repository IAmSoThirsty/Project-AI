# Disaster Recovery Playbook

**Project-AI Sovereign Governance Substrate**  
**Version**: 1.0  
**Last Updated**: 2026-01-08  
**Classification**: RESTRICTED - FOR AUTHORIZED PERSONNEL ONLY

---

## 🚨 Emergency Contacts

### Incident Response Team

| Role | Primary Contact | Backup Contact | Phone | Email |
|------|----------------|----------------|-------|-------|
| **DR Coordinator** | [NAME] | [NAME] | [PHONE] | [EMAIL] |
| **Database Lead** | [NAME] | [NAME] | [PHONE] | [EMAIL] |
| **Infrastructure Lead** | [NAME] | [NAME] | [PHONE] | [EMAIL] |
| **Security Lead** | [NAME] | [NAME] | [PHONE] | [EMAIL] |
| **Compliance Officer** | [NAME] | [NAME] | [PHONE] | [EMAIL] |

### Escalation Path

1. **Tier 1**: On-call engineer (15 min response)
2. **Tier 2**: DR Coordinator (30 min response)
3. **Tier 3**: Infrastructure Lead (1 hour response)
4. **Tier 4**: Executive Leadership (2 hour response)

---

## 📋 Pre-Incident Checklist

### Daily Verification (Automated)

- [ ] Backup completion verified (check cron logs)
- [ ] Backup checksums validated
- [ ] Backup upload to S3 confirmed
- [ ] Monitoring alerts reviewed
- [ ] No critical system alerts

### Weekly Verification (Manual)

- [ ] Review backup retention policy compliance
- [ ] Verify backup storage capacity (< 80%)
- [ ] Test backup file decryption
- [ ] Review disaster recovery documentation
- [ ] Validate access to encryption keys

### Monthly Verification (Scheduled)

- [ ] Perform restore test to staging environment
- [ ] Measure and document RTO/RPO
- [ ] Review and update contact information
- [ ] Test failover procedures (if applicable)
- [ ] Audit backup access logs

---

## 🔥 Disaster Scenarios & Response

### Scenario 1: Database Corruption/Loss

**Severity**: 🔴 CRITICAL  
**RTO Target**: 2 hours  
**RPO Target**: 1 hour  

#### Detection

```bash

# Symptoms

- PostgreSQL connection failures
- Database integrity errors
- Application errors referencing DB
- Monitoring alerts: "PostgreSQL Down"

```

#### Immediate Actions

```bash

# 1. Verify the incident

cd /path/to/project/deploy/single-node-core
docker compose ps postgres
docker compose logs postgres --tail 100

# 2. Attempt service recovery (if corruption is minor)

docker compose restart postgres

# 3. If restart fails, declare database incident

# Notify DR Coordinator immediately

```

#### Recovery Procedure

**Step 1: Assess Damage**
```bash

# Check database accessibility

docker compose exec postgres pg_isready -U project_ai

# If accessible, check for corruption

docker compose exec postgres psql -U project_ai -d project_ai -c "
  SELECT tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
  FROM pg_tables WHERE schemaname = 'public';
"
```

**Step 2: Stop Dependent Services**
```bash

# Prevent data inconsistency during recovery

docker compose stop project-ai-orchestrator mcp-gateway
```

**Step 3: List Available Backups**
```bash
cd scripts
./restore.sh list postgres

# Expected output:

# PostgreSQL Backups:

#   - 20260108_020000: full_backup.dump.gz.enc (5.2G)

#   - 20260107_020000: full_backup.dump.gz.enc (5.1G)

#   - 20260106_020000: full_backup.dump.gz.enc (5.0G)

```

**Step 4: Select and Verify Backup**
```bash

# Find latest valid backup

BACKUP_FILE="/path/to/backups/postgres/20260108_020000/full_backup.dump.gz.enc"

# Verify backup integrity

./backup.sh verify "$BACKUP_FILE"

# Expected output:

# [SUCCESS] Checksum verified

# [SUCCESS] PostgreSQL backup is valid

```

**Step 5: Execute Restoration**
```bash

# CRITICAL: This will DROP existing database

./restore.sh postgres "$BACKUP_FILE" true

# You will be prompted:

# "Are you sure you want to proceed? (yes/no):"

# Type: yes

# Restoration will take 30-60 minutes for large databases

# Monitor progress in real-time

```

**Step 6: Verify Data Integrity**
```bash

# Check table counts

docker compose exec postgres psql -U project_ai -d project_ai -c "
  SELECT schemaname, COUNT(*) FROM pg_tables 
  WHERE schemaname = 'public' GROUP BY schemaname;
"

# Run application-specific data validation

docker compose exec project-ai-orchestrator python -c "
  from app.database import verify_schema
  verify_schema()
"
```

**Step 7: Restart Services**
```bash

# Start dependent services

docker compose start project-ai-orchestrator mcp-gateway

# Wait for health checks

sleep 30

# Verify service health

docker compose ps
curl -f http://localhost:8000/health
```

**Step 8: Post-Recovery Validation**
```bash

# Run smoke tests

docker compose exec project-ai-orchestrator pytest tests/smoke/

# Check application functionality

# - User authentication

# - Data retrieval

# - Critical workflows

# Monitor error logs for 1 hour

docker compose logs -f --since 1h
```

**Step 9: Incident Documentation**
```bash

# Document in incident log

cat >> incident_log.md <<EOF
---
Date: $(date)
Incident: Database Recovery
Backup Used: $BACKUP_FILE
RPO Achieved: [CALCULATE]
RTO Achieved: [CALCULATE]
Data Loss: [YES/NO]
Root Cause: [TO BE DETERMINED]
---
EOF
```

#### Rollback Plan

If restoration fails:
```bash

# 1. Preserve failed state for forensics

docker compose exec postgres pg_dumpall > failed_state_dump.sql

# 2. Try previous backup

BACKUP_FILE="/path/to/backups/postgres/20260107_020000/full_backup.dump.gz.enc"
./restore.sh postgres "$BACKUP_FILE" true

# 3. If multiple backups fail, escalate to Tier 3

```

---

### Scenario 2: Redis Cache Failure

**Severity**: 🟡 HIGH  
**RTO Target**: 30 minutes  
**RPO Target**: 24 hours (cache can be rebuilt)  

#### Detection

```bash

# Symptoms

- Redis connection timeouts
- Application performance degradation
- Monitoring alerts: "Redis Down"

```

#### Recovery Procedure

**Step 1: Assess Impact**
```bash

# Check Redis status

docker compose ps redis
docker compose logs redis --tail 50

# Attempt connection

docker compose exec redis redis-cli -a "$REDIS_PASSWORD" ping
```

**Step 2: Quick Recovery Attempt**
```bash

# Try service restart

docker compose restart redis

# Wait 10 seconds

sleep 10

# Test connectivity

docker compose exec redis redis-cli -a "$REDIS_PASSWORD" DBSIZE
```

**Step 3: Restore from Backup (if restart fails)**
```bash
cd scripts

# List available backups

./restore.sh list redis

# Select latest backup

BACKUP_FILE="/path/to/backups/redis/20260108_020000/redis_backup.tar.gz.enc"

# Restore (will flush existing data)

./restore.sh redis "$BACKUP_FILE" true
```

**Step 4: Validate Cache**
```bash

# Check key count

docker compose exec redis redis-cli -a "$REDIS_PASSWORD" DBSIZE

# Check memory usage

docker compose exec redis redis-cli -a "$REDIS_PASSWORD" INFO memory

# Run cache warmup if needed

docker compose exec project-ai-orchestrator python -m app.cache.warmup
```

**Alternative: Cache Rebuild**
```bash

# If backup restore fails, rebuild cache from database

docker compose exec project-ai-orchestrator python -c "
  from app.cache import rebuild_cache
  rebuild_cache()
"

# This may take 10-30 minutes depending on data volume

```

---

### Scenario 3: Complete System Failure

**Severity**: 🔴 CRITICAL  
**RTO Target**: 4 hours  
**RPO Target**: 1 hour  

#### Detection

```bash

# Symptoms

- All services down
- Infrastructure unavailable
- Multiple monitoring alerts
- User-reported outage

```

#### Recovery Procedure

**Step 1: Incident Declaration**
```bash

# Notify all stakeholders

# Activate DR team

# Start incident timer

echo "INCIDENT DECLARED: $(date)" > dr_incident.log
```

**Step 2: Infrastructure Assessment**
```bash

# Check Docker host

systemctl status docker

# Check disk space

df -h

# Check network connectivity

ping -c 3 8.8.8.8

# Check DNS resolution

nslookup postgres
```

**Step 3: List Available Backups**
```bash
cd /path/to/project/deploy/single-node-core/scripts

# Find latest complete backup set

./restore.sh list all

# Identify timestamp for full restore

# Example: 20260108_020000

RESTORE_TIMESTAMP="20260108_020000"
```

**Step 4: Full System Restoration**
```bash

# Execute full restore

./restore.sh full $RESTORE_TIMESTAMP

# You will be prompted multiple times

# Type: RESTORE (all caps) to confirm

# Restoration will take 2-4 hours

# Components restored:

# 1. PostgreSQL database (60 min)

# 2. Redis cache (10 min)

# 3. Application data (20 min)

# 4. Service startup (10 min)

```

**Step 5: Service Verification**
```bash

# Check all services

docker compose ps

# Expected output: All services "Up" and healthy

# Verify database

docker compose exec postgres psql -U project_ai -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname='public';"

# Verify Redis

docker compose exec redis redis-cli -a "$REDIS_PASSWORD" DBSIZE

# Verify application

curl -f http://localhost:8000/health
```

**Step 6: End-to-End Testing**
```bash

# Run integration tests

docker compose exec project-ai-orchestrator pytest tests/integration/

# Test critical user workflows

# - User login

# - Data retrieval

# - Audit log writing

# - MCP gateway connectivity

```

**Step 7: Service Handoff**
```bash

# Monitor for stability (1 hour minimum)

watch -n 30 'docker compose ps'

# Review logs for errors

docker compose logs --since 1h | grep -i error

# Once stable, notify stakeholders of recovery completion

```

---

### Scenario 4: Ransomware Attack

**Severity**: 🔴 CRITICAL  
**RTO Target**: 6 hours  
**RPO Target**: Up to 24 hours (restore from immutable backup)  

#### Detection

```bash

# Symptoms

- File encryption notices
- Unusual file extensions (.encrypted, .locked)
- Ransom notes in directories
- Suspicious process activity

```

#### Immediate Actions

**Step 1: ISOLATE IMMEDIATELY**
```bash

# CRITICAL: Prevent spread

# Disconnect network (DO NOT SHUTDOWN - preserves forensic evidence)

# Docker: Stop all external ports

docker compose down

# Host: Disable network interfaces (if host is infected)

sudo ip link set eth0 down

# NOTIFY SECURITY TEAM IMMEDIATELY

```

**Step 2: Forensic Preservation**
```bash

# Capture system state

date > /root/ransomware_incident_$(date +%Y%m%d_%H%M%S).log
ps aux >> /root/ransomware_incident_*.log
netstat -tuln >> /root/ransomware_incident_*.log
ls -laR /path/to/project >> /root/ransomware_incident_*.log

# Preserve infected containers (DO NOT DELETE)

docker commit project-ai-postgres postgres-infected-$(date +%Y%m%d)
docker commit project-ai-redis redis-infected-$(date +%Y%m%d)
```

**Step 3: Assess Damage**
```bash

# Check file integrity

find /path/to/project -type f -mtime -1 | head -50

# Check for encryption

file /path/to/project/data/* | grep -i encrypted

# Check backup integrity

ls -la /path/to/backups/postgres/
sha256sum -c /path/to/backups/postgres/latest/*.sha256
```

**Step 4: Determine Last Known Good Backup**
```bash

# Find backup BEFORE infection

# Review backup timestamps

ls -lt /path/to/backups/postgres/

# Verify backup is not encrypted

cd /path/to/backups/postgres/20260107_020000
file full_backup.dump.gz.enc

# Should output: "openssl enc'd data with salted password"

```

**Step 5: Clean Slate Recovery**
```bash

# NUCLEAR OPTION: Wipe and rebuild from backup

# 1. Backup forensic evidence

tar -czf /root/forensics_$(date +%Y%m%d_%H%M%S).tar.gz \
  /var/log \
  /path/to/project/logs \
  /root/ransomware_incident_*.log

# 2. Destroy compromised environment

docker compose down -v  # Remove all volumes
docker system prune -a --volumes -f

# 3. Rebuild infrastructure from clean images

docker compose pull  # Fresh images from registry
docker compose up -d postgres redis

# 4. Restore from last known good backup

cd scripts
BACKUP_FILE="/path/to/backups/postgres/20260107_020000/full_backup.dump.gz.enc"
./restore.sh postgres "$BACKUP_FILE" true

BACKUP_FILE="/path/to/backups/redis/20260107_020000/redis_backup.tar.gz.enc"
./restore.sh redis "$BACKUP_FILE" true

# 5. Restore application data

BACKUP_FILE="/path/to/backups/app/20260107_020000/app_backup.tar.gz.enc"
./restore.sh app "$BACKUP_FILE"
```

**Step 6: Security Hardening**
```bash

# Before bringing system online:

# 1. Rotate all credentials

# 2. Update all passwords

# 3. Review access controls

# 4. Scan for malware

# 5. Patch all systems

# 6. Enable MFA

# Scan rebuilt system

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image project-ai:latest
```

**Step 7: Controlled Restart**
```bash

# Start services one by one

docker compose up -d postgres
sleep 60
docker compose up -d redis
sleep 30
docker compose up -d project-ai-orchestrator

# Monitor for suspicious activity

docker compose logs -f
```

**Step 8: Post-Incident Review**
```bash

# Required actions:

# 1. Root cause analysis

# 2. Security audit

# 3. Patch vulnerabilities

# 4. Update incident response procedures

# 5. Notify affected parties (if required by regulation)

# 6. File incident report with management

```

#### Data Loss Expectations

- **Best Case**: Up to 24 hours of data lost
- **Worst Case**: Up to 30 days (if recent backups compromised)
- **Audit Logs**: ZERO LOSS (7-year immutable backups)

---

### Scenario 5: Audit Log Investigation

**Severity**: 🟢 LOW  
**RTO Target**: N/A (read-only operation)  
**RPO Target**: N/A  

#### Use Cases

- Security incident investigation
- Compliance audit
- Legal discovery request
- Fraud detection
- User activity analysis

#### Query Procedures

**Step 1: Locate Audit Logs**
```bash

# Current audit log

cat audit.log

# Backup audit logs

ls -la backups/audit/

# Example:

# audit_20260108_020000.log

# audit_20260107_020000.log

# audit_20260106_020000.log

```

**Step 2: Search by Event Type**
```bash

# Find specific event types

grep "event_type: user_login" audit.log

# Find security events

grep -E "event_type: (unauthorized_access|permission_denied|authentication_failed)" audit.log

# Count events by type

grep -oP 'event_type: \K\w+' audit.log | sort | uniq -c | sort -rn
```

**Step 3: Search by Time Range**
```bash

# Events from specific date

grep "timestamp: '2026-01-08" audit.log

# Events in date range

awk '/2026-01-07/,/2026-01-08/' audit.log
```

**Step 4: Search by Actor**
```bash

# Find actions by specific user

grep "actor: john.doe" audit.log

# Find system actions

grep "actor: system" audit.log
```

**Step 5: Verify Audit Chain Integrity**
```bash

# Verify hash chain (no tampering)

python3 scripts/verify_audit_chain.py audit.log

# Expected output:

# ✓ Audit chain verified: 1,234 events

# ✓ No hash chain breaks detected

# ✓ All timestamps sequential

```

**Step 6: Export for Legal Discovery**
```bash

# Export specific time range

awk '/2026-01-01/,/2026-01-31/' audit.log > audit_jan2026.log

# Create tamper-proof archive

tar -czf audit_jan2026.tar.gz audit_jan2026.log
sha256sum audit_jan2026.tar.gz > audit_jan2026.tar.gz.sha256

# Encrypt for transport

openssl enc -aes-256-cbc -salt -pbkdf2 \
  -in audit_jan2026.tar.gz \
  -out audit_jan2026.tar.gz.enc \
  -pass file:.backup-encryption-key
```

**Step 7: Long-Term Audit Retrieval (7-Year Retention)**
```bash

# List all audit backups (sorted by date)

ls -lt backups/audit/ | head -20

# Restore old audit log

AUDIT_DATE="20230108"
gunzip < backups/audit/audit_${AUDIT_DATE}_020000.log.gz > audit_${AUDIT_DATE}.log

# Query restored log

grep "event_type: compliance_check" audit_${AUDIT_DATE}.log
```

---

### Scenario 6: Configuration Corruption

**Severity**: 🟡 HIGH  
**RTO Target**: 1 hour  
**RPO Target**: Depends on Git commit history  

#### Detection

```bash

# Symptoms

- Service startup failures
- Configuration validation errors
- Unexpected application behavior

```

#### Recovery Procedure

**Step 1: Identify Corrupted Configuration**
```bash

# Check which config is causing issues

docker compose config

# Validate individual configs

yamllint docker-compose.yml
yamllint mcp/config.yaml
```

**Step 2: Restore from Git**
```bash

# View recent changes

git log --oneline --all --decorate --graph -20

# Restore specific file

git checkout HEAD~1 -- mcp/config.yaml

# Or restore to specific commit

git checkout abc1234 -- docker-compose.yml
```

**Step 3: Restore from Backup**
```bash

# Extract config from latest backup

cd scripts
BACKUP_FILE="/path/to/backups/app/20260108_020000/app_backup.tar.gz.enc"

# Decrypt and extract

openssl enc -aes-256-cbc -d -pbkdf2 \
  -in "$BACKUP_FILE" \
  -out app_backup.tar.gz \
  -pass file:../.backup-encryption-key

tar -xzf app_backup.tar.gz config.tar.gz
tar -xzf config.tar.gz -C /restore/
```

**Step 4: Validate and Apply**
```bash

# Validate configuration

docker compose config -q

# If valid, restart services

docker compose restart
```

---

## 🔄 Failover Procedures

### Manual Failover (Primary to Secondary Region)

**Prerequisites**:

- Secondary region infrastructure deployed
- Database replication configured
- DNS failover capability

**Step 1: Assess Primary Region**
```bash

# Confirm primary is truly down

ping primary-db.region1.example.com
curl -f https://primary-api.region1.example.com/health
```

**Step 2: Verify Secondary Region Readiness**
```bash

# Check replication lag

ssh secondary-region
docker compose exec postgres psql -U project_ai -c "
  SELECT NOW() - pg_last_xact_replay_timestamp() AS replication_lag;
"

# Acceptable lag: < 15 minutes

```

**Step 3: Promote Secondary Database**
```bash

# Promote standby to primary

docker compose exec postgres pg_ctl promote -D /var/lib/postgresql/data
```

**Step 4: Update DNS**
```bash

# Update DNS records to point to secondary region

# This is typically done via cloud provider console or API

# Example with AWS Route53:

aws route53 change-resource-record-sets \
  --hosted-zone-id Z123456 \
  --change-batch file://dns-failover.json
```

**Step 5: Verify Failover**
```bash

# Test application access

curl -f https://api.example.com/health

# Monitor service health

docker compose ps
docker compose logs -f --since 10m
```

**Step 6: Notify Stakeholders**
```bash

# Send notification (automated)

# - Incident status: FAILOVER COMPLETE

# - Region: us-west-2 (secondary)

# - Data loss: [ESTIMATE RPO]

# - Expected recovery of primary: [ESTIMATE]

```

---

## 📊 Recovery Metrics & Reporting

### RTO/RPO Tracking

**After Each Recovery Event**:
```bash
cat >> recovery_metrics.csv <<EOF
Date,Scenario,Backup_Used,RPO_Minutes,RTO_Minutes,Data_Loss,Success
$(date),Database Restore,20260108_020000,45,120,No,Yes
EOF
```

### Monthly DR Report Template

```markdown

# DR Monthly Report - [MONTH YEAR]

## Executive Summary

- Backup Success Rate: [X]%
- Average Backup Size: [X] GB
- Restore Tests Performed: [X]
- Average RTO: [X] minutes
- Average RPO: [X] minutes

## Backup Statistics

- PostgreSQL: [X] backups, [X] GB total
- Redis: [X] backups, [X] GB total
- Audit Logs: [X] backups, [X] GB total
- Storage Used: [X] GB / [X] GB ([X]%)

## Incidents

- Total Incidents: [X]
- Critical: [X]
- High: [X]
- Medium: [X]
- Low: [X]

## Recovery Tests

- [Date]: [Scenario] - [Success/Failure]
- [Date]: [Scenario] - [Success/Failure]

## Recommendations

1. [Recommendation 1]
2. [Recommendation 2]

```

---

## 🛡️ Security & Compliance

### Encryption Key Management

**Key Rotation (Quarterly)**:
```bash

# Generate new encryption key

openssl rand -base64 32 > .backup-encryption-key.new

# Re-encrypt recent backups with new key

# (Keep old key for historical backups)

# Update backup script to use new key

mv .backup-encryption-key .backup-encryption-key.old
mv .backup-encryption-key.new .backup-encryption-key
chmod 600 .backup-encryption-key
```

### Access Audit

**Monthly Access Review**:
```bash

# List who has accessed backup directory

sudo ausearch -f /path/to/backups -ts this-month

# Review SSH access to backup servers

sudo last -F | grep backup-server
```

### Compliance Verification

**Quarterly Compliance Check**:
```bash

# Verify 7-year audit retention

OLDEST_AUDIT=$(ls -t backups/audit/ | tail -1)
AGE_DAYS=$(( ($(date +%s) - $(stat -c %Y backups/audit/$OLDEST_AUDIT)) / 86400 ))

if [ $AGE_DAYS -lt 2555 ]; then
  echo "✓ Audit retention policy compliant (oldest: $AGE_DAYS days)"
else
  echo "⚠ Audit retention exceeds 7 years (oldest: $AGE_DAYS days)"
fi
```

---

## 📞 Communication Templates

### Incident Notification

**Subject**: [SEVERITY] Disaster Recovery Incident - [BRIEF DESCRIPTION]

```
INCIDENT ALERT
==============

Severity: [CRITICAL/HIGH/MEDIUM/LOW]
Component: [Database/Redis/Full System/etc.]
Incident Start: [TIMESTAMP]
Estimated RTO: [X hours]
Estimated RPO: [X hours]

Status: [INVESTIGATING/RESTORING/MONITORING]

Impact:

- [Service/Feature affected]
- [User impact]

Actions Taken:

1. [Action 1]
2. [Action 2]

Next Update: [TIMESTAMP]

DR Coordinator: [NAME]
Contact: [PHONE/EMAIL]
```

### Recovery Completion

**Subject**: [RESOLVED] Disaster Recovery Complete - [BRIEF DESCRIPTION]

```
RECOVERY COMPLETE
=================

Incident: [DESCRIPTION]
Recovery Time: [X hours Y minutes]
Data Loss: [YES/NO - X hours RPO]

Components Restored:
✓ PostgreSQL Database
✓ Redis Cache
✓ Application Data
✓ Service Configurations

Verification:
✓ Data integrity validated
✓ All services operational
✓ Monitoring alerts cleared

Post-Incident Actions:

- Root cause analysis: [SCHEDULED DATE]
- Incident report: [DUE DATE]
- Process improvements: [ASSIGNED TO]

Incident Closed: [TIMESTAMP]
DR Coordinator: [NAME]
```

---

## 🔧 Maintenance & Testing

### Monthly Restore Test

**Procedure**:
```bash

# Create isolated test environment

export COMPOSE_PROJECT_NAME=dr_test

# Start test infrastructure

docker compose -f docker-compose.test.yml up -d postgres redis

# Restore latest backup

cd scripts
./restore.sh postgres /path/to/latest/backup.dump.gz.enc true

# Run validation tests

docker compose exec postgres psql -U project_ai -c "SELECT COUNT(*) FROM pg_tables;"

# Document RTO

echo "Restore Test $(date): RTO = [X] minutes" >> restore_test_log.txt

# Cleanup

docker compose -f docker-compose.test.yml down -v
```

### Quarterly DR Drill

**Full Disaster Simulation**:
```bash

# Schedule: First Saturday of quarter, 2:00 AM

# Duration: 4 hours

# Participants: All DR team members

# 1. Simulate primary region failure

# 2. Execute full restore procedure

# 3. Verify all services

# 4. Measure RTO/RPO

# 5. Document lessons learned

# 6. Update playbook with improvements

```

---

## 📚 Appendix

### A. Environment Variables

```bash

# Required environment variables for DR operations

export BACKUP_DIR="/path/to/backups"
export ENCRYPTION_KEY_FILE="/path/to/.backup-encryption-key"
export POSTGRES_USER="project_ai"
export POSTGRES_PASSWORD="[REDACTED]"
export POSTGRES_DB="project_ai"
export REDIS_PASSWORD="[REDACTED]"
export S3_BUCKET="project-ai-backups"
export S3_PREFIX="production/backups"
export SLACK_WEBHOOK="https://hooks.slack.com/services/XXX"
```

### B. Directory Structure

```
/path/to/project/
├── backups/
│   ├── postgres/
│   │   ├── 20260108_020000/
│   │   │   ├── full_backup.dump.gz.enc
│   │   │   ├── schema.sql
│   │   │   ├── globals.sql
│   │   │   └── table_sizes.txt
│   │   └── 20260107_020000/
│   ├── redis/
│   │   └── 20260108_020000/
│   │       └── redis_backup.tar.gz.enc
│   ├── app/
│   │   └── 20260108_020000/
│   │       └── app_backup.tar.gz.enc
│   └── audit/
│       ├── audit_20260108_020000.log
│       └── audit_20260107_020000.log
├── scripts/
│   ├── backup.sh
│   ├── restore.sh
│   └── verify_audit_chain.py
└── .backup-encryption-key
```

### C. Useful Commands

```bash

# Check backup health

find /path/to/backups -name "*.enc" -mtime -1

# Calculate total backup size

du -sh /path/to/backups/*

# Find largest backups

find /path/to/backups -type f -exec du -h {} + | sort -rh | head -10

# Verify all checksums

find /path/to/backups -name "*.sha256" -exec sha256sum -c {} \;

# List backups older than 30 days

find /path/to/backups/postgres -type d -mtime +30

# Estimate restore time

ls -lh /path/to/backups/postgres/latest/full_backup.dump.gz.enc

# Rule of thumb: 1 GB = ~10 minutes restore time

```

### D. Backup Script Cron Schedule

```cron

# Daily backups at 2:00 AM

0 2 * * * /path/to/project/deploy/single-node-core/scripts/backup.sh full >> /var/log/backup.log 2>&1

# Weekly backup verification at 3:00 AM Sunday

0 3 * * 0 /path/to/project/deploy/single-node-core/scripts/backup.sh verify >> /var/log/backup_verify.log 2>&1

# Monthly cleanup at 4:00 AM on 1st of month

0 4 1 * * /path/to/project/deploy/single-node-core/scripts/backup.sh cleanup >> /var/log/backup_cleanup.log 2>&1
```

---

## 📝 Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-08 | DR Architect | Initial playbook creation |
| | | | - Added 6 disaster scenarios |
| | | | - Documented recovery procedures |
| | | | - Created communication templates |

---

## ✅ Playbook Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **DR Coordinator** | _____________ | _____________ | ______ |
| **Infrastructure Lead** | _____________ | _____________ | ______ |
| **Security Lead** | _____________ | _____________ | ______ |
| **Compliance Officer** | _____________ | _____________ | ______ |

---

**CLASSIFIED: RESTRICTED**  
This document contains sensitive operational procedures. Distribution is limited to authorized DR team members only.

**Last Tested**: [DATE]  
**Next Review**: [DATE + 90 days]  
**Next Drill**: [DATE + 90 days]
