# Quick Response Templates

## Incident Slack/Channel Post Template

```
🚨 INCIDENT: [Critical] Jailbreak success on flow /api/assistant

**Time**: 2026-01-21T15:00Z
**Incident ID**: INC-20260121150000
**Severity**: CRITICAL

**Scope**:
- Affected endpoints: /api/assistant, /api/chat
- Personas: jailbreak_attacker, data_exfiltrator
- Snapshot ID: snap-abc123def456

**Immediate Actions**:
✓ Rollback executed to snapshot snap-xyz789
✓ Endpoints throttled to 10% traffic
✓ Agent isolated in strict sandbox mode
⏳ Staging reproduction in progress

**Owner**: GALAHAD (@galahad-lead)
**Backup**: CERBERUS (@cerberus-lead)
**Status**: INVESTIGATING

**Artifacts**:
- SARIF: https://github.com/IAmSoThirsty/Project-AI/security/code-scanning/123
- Transcript: transcript_id-abc123
- Snapshot: snap-abc123def456
- Dashboard: https://grafana.internal/incident-INC-20260121150000

**Next Steps**:
1. Complete staging reproduction (ETA: +30min)
2. Identify failing guardrail (ETA: +60min)
3. Generate emergency patch (ETA: +2hr)
4. Triumvirate review (ETA: +4hr)
```

---

## Triumvirate Triage Checklist Template

```markdown
# Incident Triage: INC-${INCIDENT_ID}

## Immediate Verification (0-15 min)
- [ ] **Snapshot exists and is immutable**
  - Path: `data/forensic_snapshots/snap-${SNAPSHOT_ID}.tar.gz`
  - Checksum verified: `sha256sum snap-${SNAPSHOT_ID}.tar.gz`
  - Metadata intact: `cat snap-${SNAPSHOT_ID}.metadata.json`

- [ ] **Reproduction in isolated staging (<1 hour)**
  - Command: `python scripts/reproduce_incident.py --snapshot ${SNAPSHOT_ID}`
  - Status: ☐ In Progress ☐ Success ☐ Failed
  - Reproduces: ☐ Yes ☐ No ☐ Partial

- [ ] **Identify failing guardrail and patch candidate**
  - Failing guardrail: _________________________
  - Attack vector: _________________________
  - Root cause: _________________________
  - Patch candidate: ☐ Available ☐ In Progress ☐ Needs Research

## Decision Points (15-90 min)
- [ ] **Decide on auto-PR vs manual patching**
  - ☐ **Auto-PR**: Low-risk, well-understood, comprehensive tests
  - ☐ **Manual**: High-risk, architectural change, or insufficient coverage
  - Rationale: _________________________

## Triumvirate Approval
- [ ] **GALAHAD**: ☐ Approved ☐ Rejected
  - Reason (if rejected): _________________________
- [ ] **CERBERUS**: ☐ Approved ☐ Rejected
  - Reason (if rejected): _________________________
- [ ] **CODEX DEUS MAXIMUS**: ☐ Approved ☐ Rejected
  - Reason (if rejected): _________________________

**Requires**: Unanimous approval for Critical incidents

## Validation (90 min - 24 hr)
- [ ] **Full red-team campaign passed**
  - HYDRA: ___ / 200 tests passed
  - JBB: ___ / 30 tests passed
  - Custom: ___ / ___ tests passed

- [ ] **Postmortem scheduled**
  - Date/Time: _________________________
  - Attendees: Security team, on-call, Triumvirate reps
  - Artifacts prepared: ☐ SARIF ☐ Transcripts ☐ Snapshots ☐ Metrics

## Follow-up Actions
- [ ] Add detection patterns to SafetyGuard
- [ ] Schedule regression campaign (+7 days)
- [ ] Update training materials
- [ ] Review similar endpoints
```

---

## High-Severity Alert Template

```
🔴 HIGH SEVERITY ALERT

**Alert**: Attack success rate exceeds threshold
**Metric**: security_attack_success_rate = 12.5% (threshold: 10%)
**Time**: 2026-01-21T15:00Z
**Duration**: Last 5 minutes

**Affected**:
- Personas: jailbreak_attacker, social_engineer
- Guardrails: SafetyGuard, ConstitutionalGuardrail
- Targets: /api/assistant, /api/chat

**Automated Actions**:
✓ Alert fired to PagerDuty
✓ Incident workflow triggered
✓ Forensic snapshot created

**Required Actions**:
1. Acknowledge alert within 5 minutes
2. Begin investigation immediately
3. Execute containment if confirmed

**Runbook**: docs/INCIDENT_PLAYBOOK.md
**Dashboard**: https://grafana.internal/d/security-overview
```

---

## Code Security Finding Template

```
🛡️ CODE SECURITY FINDING

**Severity**: Critical
**Finding Type**: SQL Injection
**CWE**: CWE-89
**File**: src/app/api/users.py
**Line**: 142

**Description**:
Unsanitized user input used directly in SQL query construction.

**Code Snippet**:
```python
query = f"SELECT * FROM users WHERE id = {user_id}"
cursor.execute(query)
```

**Suggested Fix**:
```python
query = "SELECT * FROM users WHERE id = ?"
cursor.execute(query, (user_id,))
```

**Impact**:
- Allows arbitrary SQL execution
- Potential for data exfiltration
- Authentication bypass possible

**Actions**:
- [ ] Review finding
- [ ] Apply suggested fix
- [ ] Add test case
- [ ] Run security scan
- [ ] Deploy to staging
- [ ] Verify fix with red team

**SARIF**: artifacts/sarif/scan-${SCAN_ID}.sarif.json
**Assigned**: @security-team
**Priority**: P0 - Block deployment
```

---

## Red Team Campaign Summary Template

```
🎯 RED TEAM CAMPAIGN SUMMARY

**Campaign ID**: campaign-20260121150000
**Duration**: 45 minutes
**Status**: ✓ Completed

**Scope**:
- Personas tested: 7 (jailbreak_attacker, data_exfiltrator, social_engineer, logic_manipulator, privacy_prober, resource_exhaustion, instruction_hijacker)
- Targets tested: 3 (/api/assistant, /api/chat, /api/search)
- Total attacks: 21

**Results**:
✅ Passed: 18 (85.7%)
❌ Failed: 3 (14.3%)

**Failed Attacks**:
1. jailbreak_attacker on /api/assistant
   - Attack vector: role_confusion -> system_message_override
   - Severity: Critical
   - Transcript: transcript-abc123
   - Incident: INC-20260121150000

2. data_exfiltrator on /api/search
   - Attack vector: indirect_query -> log_probing
   - Severity: High
   - Transcript: transcript-def456
   - Incident: INC-20260121150001

3. social_engineer on /api/chat
   - Attack vector: authority_impersonation -> urgency
   - Severity: Medium
   - Transcript: transcript-ghi789
   - Incident: INC-20260121150002

**Artifacts**:
- SARIF: data/sarif_reports/campaign-20260121150000.sarif.json
- Results: data/campaign_results/campaign-20260121150000.json
- Snapshot: snap-campaign-20260121150000-20260121150045

**Next Steps**:
1. Investigate 3 failed attacks
2. Apply emergency patches
3. Re-run campaign on patched system
4. Update detection patterns

**Triumvirate Review Required**: Yes (2 critical, 1 high)
```

---

## Deployment Gate Failure Template

```
🚫 DEPLOYMENT BLOCKED

**Gate**: Security Scan
**Status**: FAILED
**Time**: 2026-01-21T15:00Z

**Blocking Issues**:
1. **Critical Vulnerabilities**: 2 found
   - SQL Injection in src/app/api/users.py:142
   - Command Injection in src/app/utils/exec.py:89

2. **High Severity Issues**: 5 found
   - Hardcoded secrets (3)
   - Path traversal (2)

**SARIF Report**: https://github.com/IAmSoThirsty/Project-AI/security/code-scanning/456

**Required Actions**:
- [ ] Review all critical findings
- [ ] Apply CodeAdversary suggested patches
- [ ] Re-run security scan
- [ ] Verify all critical issues resolved
- [ ] Re-attempt deployment

**Policy**: Critical vulnerabilities block all deployments to production.
**Override**: Requires Triumvirate unanimous approval + incident ticket.

**Help**: docs/INCIDENT_PLAYBOOK.md
**Contact**: @security-team
```

---

## Canary Deployment Rollback Template

```
⚠️ CANARY ROLLBACK TRIGGERED

**Deployment**: v1.3.0-patch-incident-123
**Canary Traffic**: 5%
**Status**: ROLLING BACK

**Rollback Trigger**:
- Metric: attack_success_rate
- Threshold: 10%
- Actual: 15.2%
- Duration: 10 minutes

**Affected Metrics**:
- attack_success_rate: 15.2% (↑ from 2.1%)
- false_positive_rate: 8.3% (↑ from 5.1%)
- agent_latency_p95: 1,250ms (↑ from 450ms)

**Automated Actions**:
✓ Traffic redirected to stable version (v1.2.0)
✓ Deployment halted
✓ Incident ticket created: INC-20260121150000
✓ Rollback snapshot created

**Investigation Required**:
1. Identify root cause of increased attack success
2. Review patch changes
3. Run red team campaign on rolled-back version
4. Determine if patch introduced regression

**Timeline**:
- Deployment started: 14:00Z
- Canary at 5%: 14:30Z
- Threshold exceeded: 14:40Z
- Rollback initiated: 14:42Z
- Rollback completed: 14:45Z

**Status**: Stable version restored, investigating
```

---

## Postmortem Meeting Agenda Template

```
# Incident Postmortem: INC-${INCIDENT_ID}

**Date**: _________________________
**Time**: _________________________
**Duration**: 60 minutes
**Attendees**: 
- Security Team
- On-call Engineer
- GALAHAD Representative
- CERBERUS Representative
- CODEX Representative

---

## Agenda

### 1. Timeline Review (15 min)
- Incident detection
- Initial response
- Containment actions
- Root cause identification
- Mitigation implementation
- Recovery

### 2. Root Cause Analysis (15 min)
- What happened?
- Why did it happen?
- Why did our defenses fail?

### 3. Response Evaluation (10 min)
- What went well?
- What could have been better?
- Were playbooks followed?

### 4. Lessons Learned (10 min)
- Technical lessons
- Process lessons
- Communication lessons

### 5. Action Items (10 min)
- Immediate fixes
- Short-term improvements
- Long-term initiatives
- Owners and deadlines

---

## Preparation (Before Meeting)

Required Artifacts:
- [ ] Timeline document
- [ ] SARIF reports
- [ ] Attack transcripts
- [ ] Forensic snapshot metadata
- [ ] Metrics/graphs showing impact
- [ ] Emergency patch details

---

## Output (After Meeting)

Deliverables:
- [ ] Completed postmortem document
- [ ] Action item tracking
- [ ] Knowledge base update
- [ ] Training material updates (if needed)
- [ ] External communication (if needed)
```

---

## Copy-Paste Command Reference

### Immediate Response Commands
```bash
# Check incident status
python scripts/incident_status.py --incident-id ${INCIDENT_ID}

# Execute containment
./scripts/incident_contain.sh --incident-id ${INCIDENT_ID}

# Create forensic snapshot
python scripts/create_forensic_snapshot.py --incident-id ${INCIDENT_ID}

# Reproduce in staging
python scripts/reproduce_incident.py --snapshot-id ${SNAPSHOT_ID}
```

### Investigation Commands
```bash
# Check current metrics
curl http://localhost:9090/metrics | grep security_

# View incident dashboard
open https://grafana.internal/d/incident-response

# Check Triumvirate status
python scripts/triumvirate_status.py --incident-id ${INCIDENT_ID}

# Analyze attack transcript
python scripts/analyze_attack.py --transcript ${TRANSCRIPT_ID}
```

### Recovery Commands
```bash
# Start canary deployment
python scripts/canary_deploy.py --patch-id ${PATCH_ID}

# Monitor canary
python scripts/monitor_canary.py --deployment-id ${DEPLOYMENT_ID}

# Complete rollout
python scripts/complete_rollout.py --deployment-id ${DEPLOYMENT_ID}
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-21  
**Maintained By**: Security Team
