---
type: operations-doc
tags: [bcdr, disaster-recovery, business-continuity, resilience, backup]
created: 2026-05-19
status: active
owner: Thirsty's Projects LLC
review_cycle: quarterly
related_systems: [save-points-api, git-version-control, governance-spine]
---

# Project-AI Business Continuity & Disaster Recovery Plan

**Version 1.0** — Thirsty's Projects LLC Production Infrastructure

---

## Executive Summary

Project-AI is the technical backbone of Thirsty's Projects LLC, a legitimate commercial software business. This BCDR plan defines how to protect, recover, and verify every critical component — from source code and governance state to audit logs and endpoint workstations.

**Recovery Philosophy**: BCDR is not "make backups." It means provable, trustworthy recovery with continuity guarantees for governance systems that must never lose their legitimacy.

---

## 1. What Do We Need to Protect?

### Asset Inventory

| Asset Category | Components | Criticality | Current Protection |
|----------------|------------|-------------|-------------------|
| **Source Code** | Git repos (Project-AI, Cerberus, OCEE, civic-attest) | CRITICAL | Git version control, GitHub remote |
| **Databases** | SQLite/JSON files (data/), Redis (temporal quotas) | CRITICAL | Save Points API (15-min auto), manual saves |
| **Configs/Secrets** | .env files, API keys, command_override_config.json | CRITICAL | Save Points API, excluded from git |
| **Audit Logs** | data/audit/*.jsonl, acceptance_ledger TSA timestamps | CRITICAL | Save Points API, append-only storage |
| **Governance State** | canonical/replay.py invariants, pipeline.py state | CRITICAL | Git + Save Points API |
| **Model Artifacts** | Trained models, embeddings, knowledge graphs | HIGH | Not yet implemented — future requirement |
| **Runtime Services** | FastAPI (port 8001), Cerberus container, Monolith | MEDIUM | Docker images, docker-compose.yml |
| **Developer Endpoints** | Jeremy's workstation, local dev environments | HIGH | Windows backup, git working directory |

### Data Loss Tolerance

- **Zero tolerance**: Audit logs, governance state, committed source code
- **15-minute tolerance**: Live operational state (users.json, ai_persona/state.json)
- **1-hour tolerance**: Development work (uncommitted changes)
- **24-hour tolerance**: Logs, metrics, monitoring data

---

## 2. What Can Break?

### Failure Scenarios

#### 2.1 Data Corruption
- **SQLite database corruption** (data/users.json, memory/knowledge.json)
- **Config file corruption** (.env, command_override_config.json)
- **Git repository corruption** (refs, objects, index)

#### 2.2 Infrastructure Failures
- **Workstation failure** (hardware death, ransomware, Windows corruption)
- **GitHub outage** (remote unavailable)
- **Docker container crash** (Cerberus, Monolith, FastAPI)
- **Network partition** (local dev ↔ GitHub)

#### 2.3 Human Error
- **Accidental deletion** (rm -rf, git reset --hard)
- **Bad commit** (breaks 5/5 invariants, introduces security hole)
- **Config error** (wrong API key, corrupt override config)
- **Malicious code injection** (supply chain attack, compromised dependency)

#### 2.4 Governance Continuity Breach
- **Acceptance ledger corruption** (lost TSA timestamps)
- **Invariant failure cascade** (canonical/replay.py 0/5 pass)
- **Jurisdiction config loss** (markdown parsers can't load rights/obligations)
- **Temporal quota reset** (Redis flush, lost crisis state)

#### 2.5 External Dependencies
- **DigiCert TSA outage** (can't timestamp new acceptance events)
- **Redis failure** (temporal quota enforcement breaks)
- **Docker Hub outage** (can't pull base images)

---

## 3. How Fast Must It Come Back?

### Recovery Time Objectives (RTO)

| Component | RTO | Justification |
|-----------|-----|---------------|
| **Source Code** | 0 (instant) | Already on GitHub, local clone = recovery |
| **Operational State** | 15 minutes | Last auto-save restore |
| **Governance Spine** | 5 minutes | Git checkout + invariant replay |
| **FastAPI Service** | 2 minutes | Docker restart or manual `python start_api.py` |
| **Cerberus/Monolith** | 5 minutes | Docker compose restart |
| **Developer Workstation** | 4 hours | Full OS reinstall + git clone + dependency setup |
| **Audit Logs** | 0 (instant) | Must never be lost — restore from last save point |
| **Redis Quotas** | 1 hour | Rebuild from crisis filesystem scan |

### Recovery Point Objectives (RPO)

| Data Type | RPO | Mechanism |
|-----------|-----|-----------|
| **Committed Source Code** | 0 (real-time) | Every commit is immediately on GitHub |
| **Operational State** | 15 minutes | Auto-save interval |
| **Manual Saves** | User-initiated | Explicit save before risky operations |
| **Audit Logs** | 15 minutes | Bundled in auto-saves |
| **Git Working Directory** | Uncommitted | User responsibility to commit frequently |
| **Redis State** | 1 hour | Rebuilt from crisis alerts or last snapshot |

---

## 4. How Much Data Can We Afford to Lose?

### Acceptable Data Loss

| Scenario | Acceptable Loss | Mitigation |
|----------|----------------|------------|
| **Workstation dies between auto-saves** | ≤15 minutes of uncommitted work | User creates manual save before risky operations |
| **GitHub remote unavailable** | 0 (local git remains authoritative) | Commit locally, push when available |
| **Redis flush** | ≤1 hour of quota state | Rebuild from crisis filesystem scan |
| **Bad commit pushed to master** | 0 (revert commit, restore from prior save point) | Git revert + save point restore |
| **Audit log corruption** | 0 (unacceptable) | TSA timestamps ensure non-repudiation |

### Unacceptable Data Loss

These scenarios require **immediate escalation** and **forensic investigation**:

- Loss of governance acceptance timestamps (TSA ledger)
- Loss of canonical invariant proofs (canonical/replay.py history)
- Loss of committed audit logs (data/audit/*.jsonl after commit)
- Loss of governance continuity (can't prove system's legal legitimacy)

---

## 5. Where Do We Restore It From?

### Backup Sources

#### 5.1 Primary: Git Version Control

```
Source:     master branch (GitHub remote + local clone)
Contains:   All source code, docs, config templates
Frequency:  Every commit (real-time)
Retention:  Infinite (Git history)
Access:     git clone https://github.com/IAmSoThirsty/Project-AI.git
```

**Recovery Procedure**:
```bash
# Fresh clone
git clone https://github.com/IAmSoThirsty/Project-AI.git
cd Project-AI

# Or repair existing clone
git fsck --full
git gc --prune=now
```

#### 5.2 Primary: Save Points API

```
Source:     data/savepoints/ directory
Contains:   Compressed .tar.gz of data/ + config/
Frequency:  Auto: 15 minutes | User: on-demand
Retention:  Auto: 7 days or 20 saves | User: unlimited
Access:     FastAPI endpoint or filesystem
```

**Auto-Save Naming**: `auto_YYYYMMDD_HHMMSS.tar.gz`  
**User-Save Naming**: `user_<name>_YYYYMMDD_HHMMSS.tar.gz`

**Recovery Procedure**:
```bash
# Via API
curl -X POST http://localhost:8001/api/savepoints/restore/auto_20260519_120000

# Or manual extraction
tar -xzf data/savepoints/auto_20260519_120000.tar.gz
```

#### 5.3 Secondary: Windows System Backup

```
Source:     Windows Backup & Restore
Contains:   Full workstation state (OS, apps, files)
Frequency:  Daily (recommended)
Retention:  30 days
Access:     Windows Recovery Environment
```

**Recovery Procedure**: Boot Windows Recovery → Restore from system image

#### 5.4 Tertiary: Docker Images

```
Source:     Local Docker registry, Docker Hub (if published)
Contains:   projectai/api:1.0.0, projectai/cerberus:omega, projectai/monolith:omega
Frequency:  On build
Retention:  Latest + previous stable
Access:     docker pull or docker load
```

**Recovery Procedure**:
```bash
# Rebuild from Dockerfile
docker-compose build

# Or pull from registry (if published)
docker pull projectai/api:1.0.0
```

---

## 6. Who Decides When Recovery Is Valid?

### Validation Authority

| Recovery Type | Validator | Validation Criteria |
|---------------|-----------|---------------------|
| **Source Code** | Git + Canonical Replay | 5/5 invariants pass in canonical/replay.py |
| **Operational State** | Save Points API | Extraction succeeds, critical files exist |
| **Governance State** | Jeremy (owner) | Acceptance ledger timestamps intact, jurisdictions load |
| **Audit Logs** | Acceptance Ledger | TSA signatures verify, no gaps in sequence |
| **Services** | Health Checks | `/health/live` returns 200, services respond |

### Validation Tests

#### Test 1: Source Code Integrity
```bash
# Must pass to confirm valid recovery
ALLOW_NON_VAULT_CHANGES=1 python canonical/replay.py

# Expected output:
# Invariant #1: ENFORCED (Governance Gate Authority)
# Invariant #2: ENFORCED (Universal Rights Adherence)
# Invariant #3: ENFORCED (Audit Immutability)
# Invariant #4: ENFORCED (Breach Incident Transparency)
# Invariant #5: ENFORCED (Reset/Purge Legitimacy)
# Verdict: 5/5 PASS
```

#### Test 2: Save Point Integrity
```bash
# List available save points
curl http://localhost:8001/api/savepoints/list

# Validate critical files exist after restore
test -f data/users.json && \
test -f data/ai_persona/state.json && \
test -f config/command_override_config.json && \
echo "PASS: Critical files present"
```

#### Test 3: Governance Continuity
```python
from src.app.governance.acceptance_ledger import verify_ledger_continuity

# Must return True to confirm no tampering
assert verify_ledger_continuity(), "Acceptance ledger broken"
```

#### Test 4: Service Health
```bash
# FastAPI
curl http://localhost:8001/health/live

# Cerberus (if running)
docker exec cerberus_omega /bin/sh -c 'echo alive'

# Expected: All return success
```

---

## 7. How Do We Prove the Restored System Is Trustworthy?

### Trustworthiness Verification

Recovery isn't complete until we can **prove** the system retains its governance legitimacy.

#### 7.1 Cryptographic Verification

**Acceptance Ledger TSA Timestamps**:
```bash
# Verify DigiCert TSA signatures on acceptance events
python -c "
from src.app.governance.acceptance_ledger import verify_all_timestamps
assert verify_all_timestamps(), 'TSA tampering detected'
"
```

**Git Commit Signatures** (future enhancement):
```bash
# Verify commits are signed by authorized committers
git log --show-signature
```

#### 7.2 Governance Invariant Replay

**Canonical Invariants Must Pass**:
```bash
# 5/5 pass required for production deployment
PYTHONPATH=src py -3.12 canonical/replay.py

# If any fail: restore from earlier save point, investigate
```

#### 7.3 Audit Log Continuity

**No Gaps in Sequence**:
```python
import json
from pathlib import Path

audit_files = sorted(Path("data/audit").glob("audit_*.jsonl"))
events = []
for f in audit_files:
    events.extend([json.loads(line) for line in f.read_text().splitlines()])

# Verify sequence numbers are contiguous
seq_nums = [e.get("sequence_number") for e in events if "sequence_number" in e]
assert seq_nums == list(range(1, len(seq_nums) + 1)), "Audit log gap detected"
```

#### 7.4 Jurisdiction Configuration Validity

**All Jurisdictions Load Without Error**:
```python
from src.app.governance.jurisdiction_loader import load_all_jurisdictions

jurisdictions = load_all_jurisdictions()
assert jurisdictions, "Jurisdiction loader failed"
assert all(j.get("rights") for j in jurisdictions), "Incomplete jurisdiction config"
```

#### 7.5 Restored State Matches Pre-Failure State

**Hash Verification** (future enhancement):
```json
{
  "save_point_metadata": {
    "id": "user_before-restore_20260519_120000",
    "sha256_checksums": {
      "data/users.json": "a3f8b9c2...",
      "data/ai_persona/state.json": "d4e5f6a7...",
      "config/command_override_config.json": "b8c9d0e1..."
    }
  }
}
```

---

## 8. Recovery Procedures by Component

### 8.1 Source Code Recovery

**Scenario**: Git repository corruption or workstation loss

**Procedure**:
1. Clone fresh from GitHub: `git clone https://github.com/IAmSoThirsty/Project-AI.git`
2. Verify canonical replay: `PYTHONPATH=src py -3.12 canonical/replay.py`
3. Expected: `Verdict: 5/5 PASS`
4. If fails: Contact repository owner, investigate commit history

**RTO**: 2 minutes (git clone on fast connection)  
**RPO**: 0 (all commits on GitHub)

---

### 8.2 Operational State Recovery

**Scenario**: Data corruption, accidental deletion, bad config change

**Procedure**:
1. **DO NOT skip this**: Create emergency backup before restore:
   ```bash
   curl -X POST http://localhost:8001/api/savepoints/create \
     -H "Content-Type: application/json" \
     -d '{"name": "emergency-pre-restore", "metadata": {}}'
   ```

2. List available save points:
   ```bash
   curl http://localhost:8001/api/savepoints/list | jq '.save_points[] | {id, timestamp, type}'
   ```

3. Restore from most recent known-good save point:
   ```bash
   curl -X POST http://localhost:8001/api/savepoints/restore/auto_20260519_120000
   ```

4. Verify critical files:
   ```bash
   test -f data/users.json && echo "users.json OK"
   test -f data/ai_persona/state.json && echo "state.json OK"
   ```

5. Restart services:
   ```bash
   python start_api.py  # or docker-compose restart
   ```

**RTO**: 5 minutes  
**RPO**: 15 minutes (last auto-save)

---

### 8.3 Governance State Recovery

**Scenario**: Acceptance ledger corruption, invariant failures, jurisdiction config loss

**Procedure**:
1. Verify git HEAD matches expected commit:
   ```bash
   git log -1 --oneline
   ```

2. Run canonical replay:
   ```bash
   ALLOW_NON_VAULT_CHANGES=1 PYTHONPATH=src py -3.12 canonical/replay.py
   ```

3. If any invariant fails:
   - Restore from last save point
   - Revert to last known-good commit: `git log --all --oneline | grep "merge("`
   - Contact owner immediately

4. Verify acceptance ledger:
   ```python
   from src.app.governance.acceptance_ledger import verify_ledger_continuity
   assert verify_ledger_continuity()
   ```

5. Verify jurisdictions load:
   ```python
   from src.app.governance.jurisdiction_loader import load_all_jurisdictions
   assert load_all_jurisdictions()
   ```

**RTO**: 10 minutes  
**RPO**: 0 (git) + 15 minutes (save points for runtime state)

---

### 8.4 Audit Log Recovery

**Scenario**: Audit log deletion, corruption, or tampering

**Procedure**:
1. **Stop all write operations** to prevent further corruption
2. Restore from most recent save point:
   ```bash
   curl -X POST http://localhost:8001/api/savepoints/restore/auto_20260519_120000
   ```

3. Verify audit log continuity:
   ```bash
   ls -lh data/audit/audit_*.jsonl
   # Check for gaps in dates
   ```

4. Verify TSA timestamps:
   ```python
   from src.app.governance.acceptance_ledger import verify_all_timestamps
   assert verify_all_timestamps(), "TSA signature verification failed"
   ```

5. **Forensic investigation required** if tampering suspected:
   - Examine git history: `git log -- data/audit/`
   - Check save point timestamps for suspicious restore attempts
   - Review Windows event logs for unauthorized access

**RTO**: 15 minutes  
**RPO**: 15 minutes (bundled in auto-saves)

**⚠️ CRITICAL**: Audit log loss triggers compliance investigation. Document timeline, root cause, and corrective actions.

---

### 8.5 Service Recovery

**Scenario**: FastAPI crash, Docker container failure, process hang

**Procedure**:

#### FastAPI (Port 8001)
```bash
# Check if running
curl http://localhost:8001/health/live

# If down, restart
python start_api.py

# Or via Docker
docker-compose restart api
```

#### Cerberus Container
```bash
# Check status
docker ps | grep cerberus_omega

# Restart
docker-compose restart cerberus
```

#### Monolith Container
```bash
# Restart
docker-compose restart monolith
```

#### Full Stack Restart
```bash
# Nuclear option: rebuild all containers
docker-compose down
docker-compose build
docker-compose up -d
```

**RTO**: 2-5 minutes  
**RPO**: N/A (stateless services; state in data/)

---

### 8.6 Developer Workstation Recovery

**Scenario**: Hardware failure, ransomware, Windows corruption

**Procedure**:

#### Phase 1: OS Reinstall (if necessary)
1. Boot Windows Recovery Environment
2. Restore from system image backup
3. Or: Clean Windows install → Windows Update → driver installation

#### Phase 2: Development Environment Setup
1. Install Python 3.12:
   ```powershell
   winget install Python.Python.3.12
   ```

2. Install Git:
   ```powershell
   winget install Git.Git
   ```

3. Clone Project-AI:
   ```bash
   git clone https://github.com/IAmSoThirsty/Project-AI.git
   cd Project-AI
   ```

4. Install dependencies:
   ```bash
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

5. Restore operational state from most recent save point:
   ```bash
   # Start API (will auto-create save_points/ if missing)
   python start_api.py

   # Restore from backup if available
   # (Copy .tar.gz files from external backup to data/savepoints/)
   curl -X POST http://localhost:8001/api/savepoints/restore/auto_20260519_120000
   ```

6. Verify canonical replay:
   ```bash
   ALLOW_NON_VAULT_CHANGES=1 PYTHONPATH=src py -3.12 canonical/replay.py
   ```

#### Phase 3: Secret Restoration
1. Restore `.env` files from secure backup (password manager, encrypted USB)
2. Regenerate API keys if compromise suspected
3. Update `.env` with new keys
4. Test services: `curl http://localhost:8001/health/live`

**RTO**: 4 hours (OS reinstall) + 30 minutes (dev setup)  
**RPO**: 15 minutes (save points) + uncommitted work lost

---

## 9. Backup Retention Policy

### Retention Schedule

| Backup Type | Retention | Storage Location | Purpose |
|-------------|-----------|------------------|---------|
| **Auto-saves** | 7 days or 20 saves (whichever first) | data/savepoints/ | Operational recovery |
| **User-saves** | Unlimited (manual deletion only) | data/savepoints/ | Pre-change checkpoints |
| **Git commits** | Infinite | .git/ + GitHub remote | Source code history |
| **Docker images** | Latest + 1 previous stable | Local Docker cache | Service rollback |
| **Windows backup** | 30 days (recommended) | External drive | Workstation recovery |
| **Audit logs** | Infinite (archived after 1 year) | data/audit/ + offsite | Compliance, forensics |

### Offsite Backup (Future Enhancement)

**Recommended**:
- Weekly full backup to external encrypted drive
- Monthly backup to cloud storage (encrypted at rest)
- Quarterly backup to offline media (air-gapped USB stored securely)

**Contents**:
- Full git clone (source code)
- All save points (.tar.gz files)
- Audit logs (data/audit/)
- Critical configs (redacted .env templates)
- Docker images (exported .tar files)

**Encryption**: AES-256, password in secure vault (not in git)

---

## 10. Testing & Validation

### Quarterly DR Tests

**Test 1: Save Point Restore**
```bash
# Create test save point
curl -X POST http://localhost:8001/api/savepoints/create \
  -H "Content-Type: application/json" \
  -d '{"name": "dr-test-q2-2026", "metadata": {"test": true}}'

# Make deliberate change
echo "test" > data/users.json

# Restore
curl -X POST http://localhost:8001/api/savepoints/restore/dr-test-q2-2026

# Verify restoration
test ! -f data/users.json || (echo "FAIL: test data not removed" && exit 1)
curl -X DELETE http://localhost:8001/api/savepoints/delete/dr-test-q2-2026
echo "PASS: Save point restore successful"
```

**Test 2: Git Clone & Replay**
```bash
# Clone to temp directory
cd /tmp
git clone https://github.com/IAmSoThirsty/Project-AI.git test-clone
cd test-clone

# Run canonical replay
ALLOW_NON_VAULT_CHANGES=1 PYTHONPATH=src py -3.12 canonical/replay.py

# Expected: 5/5 PASS
# Cleanup
cd /tmp && rm -rf test-clone
```

**Test 3: Service Restart**
```bash
# Stop all services
docker-compose down

# Restart
docker-compose up -d

# Verify health
sleep 10
curl http://localhost:8001/health/live || echo "FAIL: API did not restart"
docker ps | grep cerberus_omega || echo "FAIL: Cerberus did not restart"
```

**Test 4: Audit Log Continuity**
```python
# Run after any restore
from pathlib import Path
import json

audit_files = sorted(Path("data/audit").glob("audit_*.jsonl"))
all_events = []
for f in audit_files:
    all_events.extend([json.loads(line) for line in f.read_text().splitlines()])

# Verify no gaps (implementation depends on your sequence numbering)
print(f"Total audit events: {len(all_events)}")
print(f"Date range: {all_events[0]['timestamp']} → {all_events[-1]['timestamp']}")
```

### Annual Full DR Simulation

**Scenario**: Workstation destroyed, must recover from offsite backups

**Success Criteria**:
- New workstation operational within 8 hours
- Git clone succeeds
- Save point restore succeeds
- Canonical replay 5/5 pass
- All services start
- Audit log continuity verified
- No secrets leaked (new API keys generated)

**Documentation Required**:
- Test date and participants
- Total recovery time (actual vs. RTO)
- Issues encountered
- Corrective actions
- Lessons learned

---

## 11. Incident Response Integration

### DR Triggers

| Trigger | Response | Escalation |
|---------|----------|------------|
| **Invariant failure** | Immediate: git revert + save point restore | Owner notification |
| **Audit log corruption** | Stop writes, restore from save point, forensic investigation | Compliance team |
| **Workstation ransomware** | Disconnect network, restore from clean backup, regenerate secrets | Security team |
| **GitHub outage** | Continue work locally, push when available | Monitor GitHub status |
| **Save point corruption** | Restore from previous save point | Investigate root cause |
| **Docker Hub outage** | Use local images, rebuild from Dockerfile | No escalation |

### Communication Plan

**Immediate Notification** (within 15 minutes):
- Jeremy (owner) — primary contact
- LLC stakeholders (if business-impacting)

**Status Updates**:
- Every 30 minutes during active recovery
- Final update with timeline, root cause, corrective actions

**Post-Incident Review**:
- Document what broke, how it was fixed, how to prevent recurrence
- Update this BCDR plan if gaps discovered
- Commit findings to git: `docs/incidents/INCIDENT_YYYY-MM-DD.md`

---

## 12. Continuous Improvement

### BCDR Metrics

Track these metrics quarterly:

| Metric | Target | Current | Notes |
|--------|--------|---------|-------|
| **Mean Time to Recovery (MTTR)** | < RTO for each component | TBD | Measure during DR tests |
| **Save Point Success Rate** | 100% | TBD | Monitor auto-save failures |
| **Canonical Replay Pass Rate** | 100% | Current | Track in CI |
| **Audit Log Gaps** | 0 | 0 | Verify continuity monthly |
| **DR Test Compliance** | 4 per year (quarterly) | TBD | Schedule in calendar |

### Plan Maintenance

**Review Triggers**:
- Quarterly (scheduled)
- After any DR event (actual or test)
- After major architecture change (new critical system added)
- After security incident
- When RTO/RPO targets change

**Version Control**:
- This plan is versioned in git
- Changes require commit message: `docs(bcdr): <change description>`
- Owner approves all changes

---

## 13. Appendices

### Appendix A: Save Points API Reference

See [source-docs/api/03-SAVE-POINTS-API.md](../../source-docs/api/03-SAVE-POINTS-API.md) for complete API documentation.

**Quick Reference**:
```bash
# Create save point
curl -X POST http://localhost:8001/api/savepoints/create \
  -H "Content-Type: application/json" \
  -d '{"name": "my-checkpoint", "metadata": {}}'

# List save points
curl http://localhost:8001/api/savepoints/list

# Restore
curl -X POST http://localhost:8001/api/savepoints/restore/<save_id>

# Delete user save
curl -X DELETE http://localhost:8001/api/savepoints/delete/<save_id>

# Auto-save status
curl http://localhost:8001/api/savepoints/auto/status
```

### Appendix B: Emergency Contacts

| Role | Contact | Responsibility |
|------|---------|----------------|
| **Owner** | Jeremy Karrick | Final authority on recovery decisions |
| **LLC Representative** | Thirsty's Projects LLC | Business continuity decisions |
| **GitHub Support** | support@github.com | Git remote issues |
| **DigiCert TSA** | TSA support | Timestamp authority outages |

### Appendix C: Critical File Inventory

Files that **must** be in every save point:

```
data/
├── users.json                      # User accounts, roles
├── ai_persona/state.json           # AI operational state
├── memory/knowledge.json           # Knowledge graph
├── learning_requests/requests.json # Learning queue
├── audit/audit_YYYYMMDD.jsonl      # Audit events
└── savepoints/                     # Recursive backups

config/
└── command_override_config.json    # Governance overrides

.env                                # Secrets (not in git, must backup separately)
```

### Appendix D: Compliance Notes

**For Thirsty's Projects LLC**:

- Audit logs must be retained for 7 years (compliance requirement)
- TSA timestamps provide non-repudiation for governance events
- Acceptance ledger proves system legitimacy across restores
- No PII/HIPAA data currently stored (as of 2026-05-19)
- If PII added in future: encrypted backups required, compliance review needed

---

## 14. Document Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-19 | Claude (Project-AI) | Initial BCDR plan created per LLC requirements |

---

## 15. Approval & Sign-off

**Plan Owner**: Jeremy Karrick, Thirsty's Projects LLC  
**Next Review Date**: 2026-08-19 (quarterly)  
**Status**: Active  

**Approval**: This plan is version-controlled in git. Approval = commit to master branch.

---

**END OF PROJECT-AI BCDR PLAN v1.0**
