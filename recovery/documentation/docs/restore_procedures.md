# Restore Procedures

**Project-AI Sovereign Governance Substrate**  
**Quick Reference Guide for Recovery Operations**  
**Version**: 1.0  

---

## 🚨 Emergency Quick Start

**If you're in an emergency**, skip to the scenario that matches your situation:

- **[Database Down](#1-database-recovery)** → 30-60 minute restore
- **[Everything Down](#2-full-system-restore)** → 2-4 hour restore
- **[Ransomware](#3-ransomware-recovery)** → 6+ hour restore
- **[Need Old Data](#4-point-in-time-recovery)** → 1-2 hour restore

---

## Prerequisites

### Required Access

- [ ] SSH access to backup server
- [ ] Docker/Docker Compose access
- [ ] Backup encryption key (`.backup-encryption-key`)
- [ ] Database credentials
- [ ] Redis credentials

### Required Tools

```bash

# Verify required tools are installed

docker --version
docker compose version
openssl version
gunzip --version
```

### Environment Variables

```bash

# Set these before starting

export BACKUP_DIR="./backups"
export ENCRYPTION_KEY_FILE="./.backup-encryption-key"
export POSTGRES_USER="project_ai"
export POSTGRES_PASSWORD="[REDACTED]"
export REDIS_PASSWORD="[REDACTED]"
```

---

## 1. Database Recovery

**Use When**: PostgreSQL database is corrupted, lost, or inaccessible  
**Estimated Time**: 30-60 minutes  
**Data Loss**: Up to 24 hours (depends on backup age)  

### Step 1: Stop Dependent Services (2 minutes)

```bash
cd deploy/single-node-core

# Stop services that depend on database

docker compose stop project-ai-orchestrator mcp-gateway

# Verify they're stopped

docker compose ps
```

### Step 2: Find Latest Backup (1 minute)

```bash

# List available PostgreSQL backups

cd scripts
./restore.sh list postgres

# Output will show:

# PostgreSQL Backups:

#   - 20260108_020000: full_backup.dump.gz.enc (5.2G)

#   - 20260107_020000: full_backup.dump.gz.enc (5.1G)

# Note the timestamp of the backup you want (usually latest)

BACKUP_TIMESTAMP="20260108_020000"
```

### Step 3: Verify Backup Integrity (2 minutes)

```bash

# Verify backup file exists and checksums match

BACKUP_FILE="/path/to/backups/postgres/${BACKUP_TIMESTAMP}/full_backup.dump.gz.enc"

# Check checksum

sha256sum -c "${BACKUP_FILE}.sha256"

# Should output:

# full_backup.dump.gz.enc: OK

```

### Step 4: Execute Restore (30-50 minutes)

```bash

# Run restore (will prompt for confirmation)

./restore.sh postgres "$BACKUP_FILE" true

# You will see:

# "Are you sure you want to proceed? (yes/no):"

# Type: yes

# Restore process:

# - Decryption: 1-2 minutes

# - Decompression: 2-3 minutes

# - Database restore: 25-45 minutes

# - Verification: 2-3 minutes

```

### Step 5: Verify Restoration (5 minutes)

```bash

# Check database is accessible

docker compose exec postgres pg_isready -U project_ai

# Count tables

docker compose exec postgres psql -U project_ai -c "
  SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public';
"

# Sample query to verify data

docker compose exec postgres psql -U project_ai -c "
  SELECT * FROM [your_critical_table] LIMIT 5;
"
```

### Step 6: Restart Services (3 minutes)

```bash

# Start dependent services

docker compose start project-ai-orchestrator mcp-gateway

# Wait for services to be ready

sleep 30

# Check health

curl -f http://localhost:8000/health
```

### Step 7: Validate Application (5 minutes)

```bash

# Run smoke tests

docker compose exec project-ai-orchestrator pytest tests/smoke/ -v

# Monitor logs for errors

docker compose logs -f --since 5m | grep -i error
```

---

## 2. Full System Restore

**Use When**: Complete infrastructure failure, disaster recovery  
**Estimated Time**: 2-4 hours  
**Data Loss**: Up to 24 hours  

### Step 1: Find Complete Backup Set (5 minutes)

```bash
cd scripts

# List all backups to find matching timestamp

./restore.sh list all

# Find a timestamp where all components backed up:

# - PostgreSQL

# - Redis

# - Application data

# Example output:

# PostgreSQL Backups:

#   - 20260108_020000: full_backup.dump.gz.enc (5.2G)

# Redis Backups:

#   - 20260108_020000: redis_backup.tar.gz.enc (500M)

# Application Backups:

#   - 20260108_020000: app_backup.tar.gz.enc (1.2G)

RESTORE_TIMESTAMP="20260108_020000"
```

### Step 2: Verify Infrastructure (10 minutes)

```bash

# Ensure Docker is running

sudo systemctl status docker

# Check disk space (need 20+ GB free)

df -h /var/lib/docker

# Verify network connectivity

ping -c 3 8.8.8.8
```

### Step 3: Execute Full Restore (120-180 minutes)

```bash

# Run full system restore

./restore.sh full $RESTORE_TIMESTAMP

# You will be prompted:

# "Type 'RESTORE' to confirm:"

# Type: RESTORE (all caps)

# Restore process (automated):

# 1. PostgreSQL restore: 60-90 minutes

# 2. Redis restore: 5-10 minutes

# 3. Application data restore: 10-20 minutes

# 4. Service startup: 5-10 minutes

```

### Step 4: Comprehensive Validation (20 minutes)

```bash

# Check all containers

docker compose ps

# Should see all services "Up" and "healthy"

# Verify database

docker compose exec postgres psql -U project_ai -c "SELECT version();"

# Verify Redis

docker compose exec redis redis-cli -a "$REDIS_PASSWORD" PING

# Verify application

curl -f http://localhost:8000/health
curl -f http://localhost:8001/health
```

### Step 5: Run Integration Tests (15 minutes)

```bash

# Full test suite

docker compose exec project-ai-orchestrator pytest tests/integration/ -v

# Check critical workflows:

# - User authentication

# - Data CRUD operations

# - Audit logging

# - MCP gateway connectivity

```

---

## 3. Ransomware Recovery

**Use When**: Files encrypted by ransomware  
**Estimated Time**: 6+ hours  
**Data Loss**: Depends on when attack started (typically 24-48 hours)  

### ⚠️ CRITICAL FIRST STEPS

```bash

# 1. IMMEDIATELY DISCONNECT NETWORK

sudo ip link set eth0 down

# 2. DO NOT SHUTDOWN (preserves forensic evidence)

# 3. Notify security team IMMEDIATELY

# 4. Preserve infected state

docker commit project-ai-postgres postgres-infected-$(date +%Y%m%d)
docker commit project-ai-redis redis-infected-$(date +%Y%m%d)
docker commit project-ai-orchestrator orchestrator-infected-$(date +%Y%m%d)
```

### Step 1: Forensic Preservation (30 minutes)

```bash

# Create incident directory

INCIDENT_DIR="/root/ransomware_incident_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$INCIDENT_DIR"

# Capture system state

date > "$INCIDENT_DIR/timestamp.txt"
ps aux > "$INCIDENT_DIR/processes.txt"
netstat -tuln > "$INCIDENT_DIR/network.txt"
ls -laR /path/to/project > "$INCIDENT_DIR/files.txt"
docker ps -a > "$INCIDENT_DIR/containers.txt"

# Create forensic archive

tar -czf /root/forensics_$(date +%Y%m%d_%H%M%S).tar.gz \
  /var/log \
  /path/to/project/logs \
  "$INCIDENT_DIR"
```

### Step 2: Determine Last Known Good Backup (30 minutes)

```bash
cd scripts

# List all backups with dates

find /path/to/backups -name "full_backup.dump.gz*" -printf "%T@ %p\n" | sort -n

# Identify backup BEFORE infection

# Review timestamps against known incident timeline

# Example: If ransomware detected 2026-01-08 at 14:00,

# use backup from 2026-01-07 or earlier

SAFE_BACKUP="20260107_020000"
```

### Step 3: Nuclear Option - Complete Rebuild (60 minutes)

```bash

# DESTROY compromised environment

cd /path/to/project
docker compose down -v  # Remove all volumes
docker system prune -a --volumes -f  # Remove all images

# Verify clean slate

docker ps -a  # Should be empty
docker images  # Should be empty
docker volume ls  # Should be empty

# Pull fresh images from registry

docker compose pull

# Start clean infrastructure

docker compose up -d postgres redis
```

### Step 4: Restore from Clean Backup (90 minutes)

```bash

# Restore PostgreSQL

BACKUP_FILE="/path/to/backups/postgres/${SAFE_BACKUP}/full_backup.dump.gz.enc"
./restore.sh postgres "$BACKUP_FILE" true

# Restore Redis

BACKUP_FILE="/path/to/backups/redis/${SAFE_BACKUP}/redis_backup.tar.gz.enc"
./restore.sh redis "$BACKUP_FILE" true

# Restore Application Data

BACKUP_FILE="/path/to/backups/app/${SAFE_BACKUP}/app_backup.tar.gz.enc"
./restore.sh app "$BACKUP_FILE"
```

### Step 5: Security Hardening (60 minutes)

```bash

# Before bringing system online:

# 1. Rotate ALL credentials

# Generate new passwords for:

# - Database users

# - Redis

# - Application secrets

# - API keys

# 2. Scan for malware

docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image project-ai:latest

# 3. Update all packages

apt update && apt upgrade -y

# 4. Patch vulnerabilities

# - Review CVE reports

# - Apply security patches

# - Update base images

# 5. Enable additional security

# - MFA for admin access

# - IP whitelisting

# - Enhanced logging

```

### Step 6: Controlled Restart & Monitoring (30 minutes)

```bash

# Start services one at a time

docker compose up -d postgres
sleep 60  # Monitor for 1 minute

docker compose up -d redis
sleep 30

docker compose up -d project-ai-orchestrator
sleep 30

# Monitor continuously for suspicious activity

docker compose logs -f | tee /var/log/recovery_monitor.log
```

---

## 4. Point-in-Time Recovery

**Use When**: Need to restore data to specific point in time  
**Estimated Time**: 1-2 hours  
**Data Loss**: Controlled (select specific date/time)  

### Step 1: Identify Target Time

```bash

# Determine what timestamp you need

# Example: Restore to before accidental data deletion

TARGET_DATE="2026-01-05"  # Date of desired state
```

### Step 2: Find Appropriate Backup

```bash

# List backups around target date

ls -la /path/to/backups/postgres/ | grep "20260105"

# Find closest backup BEFORE target time

# Example output:

# 20260105_020000  # 2:00 AM backup

# 20260106_020000  # 2:00 AM backup (next day)

BACKUP_TIMESTAMP="20260105_020000"
```

### Step 3: Restore to Temporary Database

```bash

# Create temporary database for verification

docker compose exec postgres psql -U postgres -c "
  CREATE DATABASE project_ai_temp OWNER project_ai;
"

# Restore to temp database

BACKUP_FILE="/path/to/backups/postgres/${BACKUP_TIMESTAMP}/full_backup.dump.gz.enc"

# Decrypt

openssl enc -aes-256-cbc -d -pbkdf2 \
  -in "$BACKUP_FILE" \
  -out backup.dump.gz \
  -pass file:.backup-encryption-key

# Decompress

gunzip backup.dump.gz

# Restore to temp DB

docker compose cp backup.dump postgres:/tmp/restore.dump
docker compose exec postgres pg_restore \
  -U project_ai \
  -d project_ai_temp \
  --clean \
  --if-exists \
  /tmp/restore.dump
```

### Step 4: Verify and Extract Needed Data

```bash

# Connect to temp database

docker compose exec postgres psql -U project_ai -d project_ai_temp

# Verify data

SELECT * FROM [table] WHERE [condition] LIMIT 10;

# Export specific data

\copy (SELECT * FROM [table] WHERE [condition]) TO '/tmp/recovered_data.csv' CSV HEADER;
```

### Step 5: Import to Production

```bash

# Import recovered data to production

docker compose exec postgres psql -U project_ai -d project_ai -c "
  \copy [table] FROM '/tmp/recovered_data.csv' CSV HEADER;
"

# Clean up temp database

docker compose exec postgres psql -U postgres -c "
  DROP DATABASE project_ai_temp;
"
```

---

## 5. Audit Log Recovery

**Use When**: Need historical audit data for compliance/investigation  
**Estimated Time**: 30 minutes  
**Retention**: 7 years (2,555 days)  

### Step 1: Identify Required Date Range

```bash

# Determine date range needed

START_DATE="2025-06-01"
END_DATE="2025-06-30"
```

### Step 2: Find Audit Backups

```bash

# List audit backups

ls -la /path/to/backups/audit/ | grep "202506"

# Example output:

# audit_20250601_020000.log

# audit_20250602_020000.log

# ...

# audit_20250630_020000.log

```

### Step 3: Extract and Search

```bash

# Decompress if needed

gunzip < /path/to/backups/audit/audit_20250615_020000.log.gz > audit_temp.log

# Search for specific events

grep "event_type: user_login" audit_temp.log

# Search by actor

grep "actor: john.doe" audit_temp.log

# Search by date range

awk '/2025-06-15T10:00/,/2025-06-15T14:00/' audit_temp.log

# Count events

grep -c "event_type: authentication_failed" audit_temp.log
```

### Step 4: Verify Chain Integrity

```bash

# Verify audit log has not been tampered with

python3 scripts/verify_audit_chain.py audit_temp.log

# Expected output:

# ✓ Audit chain verified: 1,234 events

# ✓ No hash chain breaks detected

# ✓ All timestamps sequential

```

### Step 5: Export for Legal/Compliance

```bash

# Create tamper-proof archive

tar -czf audit_export_$(date +%Y%m%d).tar.gz audit_temp.log

# Generate checksum

sha256sum audit_export_*.tar.gz > audit_export_*.tar.gz.sha256

# Encrypt for transport

openssl enc -aes-256-cbc -salt -pbkdf2 \
  -in audit_export_*.tar.gz \
  -out audit_export_*.tar.gz.enc \
  -pass file:.backup-encryption-key
```

---

## 6. Configuration Rollback

**Use When**: Configuration change broke system  
**Estimated Time**: 15 minutes  
**Data Loss**: None  

### Step 1: Identify Corrupted Config

```bash

# Test configuration

docker compose config

# Error will indicate which file has issues

```

### Step 2: Restore from Git

```bash

# View recent commits

git log --oneline -10

# Restore specific file from previous commit

git checkout HEAD~1 -- docker-compose.yml

# Or restore from specific commit

git checkout abc1234 -- mcp/config.yaml
```

### Step 3: Alternative - Restore from Backup

```bash

# Extract config from latest backup

BACKUP_FILE="/path/to/backups/app/latest/app_backup.tar.gz.enc"

# Decrypt

openssl enc -aes-256-cbc -d -pbkdf2 \
  -in "$BACKUP_FILE" \
  -out app_backup.tar.gz \
  -pass file:.backup-encryption-key

# Extract

tar -xzf app_backup.tar.gz config.tar.gz
tar -xzf config.tar.gz -C ./restored_config/

# Review and copy needed configs

cp ./restored_config/mcp/config.yaml ./mcp/config.yaml
```

### Step 4: Validate and Restart

```bash

# Validate configuration

docker compose config -q

# If valid, restart services

docker compose restart
```

---

## Troubleshooting

### Backup File is Corrupted

```bash

# Try previous backup

BACKUP_FILE="/path/to/backups/postgres/20260107_020000/full_backup.dump.gz.enc"
./restore.sh postgres "$BACKUP_FILE" true
```

### Decryption Fails

```bash

# Verify encryption key exists

test -f .backup-encryption-key && echo "Key found" || echo "Key missing"

# Check key permissions

ls -la .backup-encryption-key

# Try manual decryption

openssl enc -aes-256-cbc -d -pbkdf2 \
  -in backup.enc \
  -out backup.decrypted \
  -pass file:.backup-encryption-key
```

### Insufficient Disk Space

```bash

# Check space

df -h

# Clean up old Docker resources

docker system prune -a --volumes

# Move backups to larger volume

rsync -av --progress /path/to/backups /mnt/large_volume/
```

### Database Won't Accept Connections

```bash

# Check PostgreSQL logs

docker compose logs postgres --tail 100

# Verify PostgreSQL is running

docker compose exec postgres pg_isready

# Check port binding

netstat -tuln | grep 5432
```

### Restore Takes Too Long

```bash

# Monitor restore progress

docker compose exec postgres psql -U project_ai -c "
  SELECT datname, pg_size_pretty(pg_database_size(datname))
  FROM pg_database;
"

# Check system resources

htop  # CPU/Memory usage
iostat -x 5  # Disk I/O
```

---

## Post-Recovery Checklist

### Immediate (Within 1 hour)

- [ ] All services running
- [ ] Database accessible
- [ ] Cache functional
- [ ] Monitoring active
- [ ] No error logs
- [ ] Critical workflows tested

### Short-Term (Within 24 hours)

- [ ] Full integration tests passed
- [ ] User access verified
- [ ] Data integrity confirmed
- [ ] Audit logs continuous
- [ ] Backup schedule resumed
- [ ] Incident documented

### Follow-Up (Within 1 week)

- [ ] Root cause analysis completed
- [ ] Preventive measures implemented
- [ ] DR playbook updated
- [ ] Team debrief conducted
- [ ] Compliance notification (if required)
- [ ] Management briefing

---

## Emergency Contacts

| Role | Primary | Phone | Email |
|------|---------|-------|-------|
| DR Coordinator | [NAME] | [PHONE] | [EMAIL] |
| Database Admin | [NAME] | [PHONE] | [EMAIL] |
| Infra Lead | [NAME] | [PHONE] | [EMAIL] |
| Security Lead | [NAME] | [PHONE] | [EMAIL] |

**24/7 Hotline**: [PHONE NUMBER]  
**Escalation Email**: dr-team@project-ai.local  

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-08  
**Next Review**: 2026-04-08  
**Classification**: RESTRICTED
