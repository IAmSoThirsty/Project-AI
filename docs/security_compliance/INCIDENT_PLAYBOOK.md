# Incident Playbook — Security Breach Response

**Purpose**: Rapid, repeatable response to confirmed high-severity adversarial breach or jailbreak.

**Scope**: Applies to incidents where an agent or model produces disallowed outputs, sensitive data exfiltration is suspected, or an adversarial campaign succeeds against guardrails.

______________________________________________________________________

## Immediate Actions (0–15 minutes)

### Detect

- Alert fires from monitoring or Triumvirate veto
- Automated detection via SecurityMetricsCollector
- Manual report from security team or user

### Triage Lead Assignment

- **Primary**: GALAHAD (relationship and safety)
- **Backup**: CERBERUS (security and risk)
- On-call rotation: See `.github/CODEOWNERS`

### Contain

Execute automated containment:

```bash

# Execute rollback to last safe snapshot

./scripts/incident_rollback.sh --snapshot-id ${LAST_SAFE_SNAPSHOT}

# Throttle affected endpoints

./scripts/throttle_endpoints.sh --endpoints ${AFFECTED_ENDPOINTS} --rate 0.1

# Isolate agent execution environment

./scripts/isolate_agent.sh --agent ${AFFECTED_AGENT} --sandbox-mode strict
```

### Snapshot

Create immutable forensic snapshot:

```bash

# Create forensic snapshot with tamperproof metadata

python scripts/create_forensic_snapshot.py \
  --incident-id ${INCIDENT_ID} \
  --include-models \
  --include-logs \
  --include-memory \
  --include-environment \
  --sign-with-timestamp
```

Snapshot includes:

- Model states and configurations
- Complete log files (last 24 hours)
- Agent memory and state
- Environment variables (redacted secrets)
- Tamperproof timestamp and checksum

______________________________________________________________________

## Short Term (15–90 minutes)

### Assess

Run reproducibility test in isolated staging:

```python
from src.app.incident.reproducer import IncidentReproducer

reproducer = IncidentReproducer(snapshot_id=SNAPSHOT_ID)
result = reproducer.reproduce_in_staging(
    use_saved_inputs=True,
    isolation_level="strict"
)

severity = classify_severity(result)

# Critical / High / Medium / Low

```

### Communicate

Post initial incident note using template:

```
🚨 INCIDENT: [Critical] Jailbreak success on flow X

Time: 2026-01-21T15:00Z
Incident ID: INC-20260121150000
Severity: CRITICAL
Scope:

  - Affected endpoints: /api/assistant, /api/chat
  - Personas: jailbreak_attacker, data_exfiltrator
  - Snapshot ID: snap-abc123def456

Immediate Mitigations:
  ✓ Rollback executed to snapshot snap-xyz789
  ✓ Endpoints throttled to 10% traffic
  ✓ Agent isolated in strict sandbox mode
  ⏳ Staging reproduction in progress

Owner: GALAHAD (@galahad-lead)
Status: INVESTIGATING

Artifacts:

  - SARIF: https://github.com/.../security/code-scanning/123
  - Transcript: transcript_id-abc123
  - Snapshot: snap-abc123def456
  - Dashboard: https://grafana.internal/incident-${INCIDENT_ID}

```

### Block

For critical incidents:

```bash

# Block merges and deployments

gh repo set-branch-protection main --required-checks "security-scan"

# Enable SafetyGuard in strict mode

python scripts/toggle_safety_mode.py --mode strict --all-endpoints

# Disable auto-PR merges from CodeAdversary

python scripts/disable_auto_merge.py --agent code_adversary --reason incident
```

______________________________________________________________________

## Containment and Remediation (90 minutes–24 hours)

### Root Cause

Reproduce attack vector with RedTeam + CodeAdversary:

```python
from src.app.agents.red_team_persona_agent import RedTeamPersonaAgent
from src.app.agents.code_adversary_agent import CodeAdversaryAgent

# Reproduce exact attack

red_team = RedTeamPersonaAgent()
session = red_team.replay_attack(
    transcript_id="abc123",
    persona_id="jailbreak_attacker",
    target_snapshot=SNAPSHOT_ID
)

# Identify failing guardrail

failing_guardrail = session["analysis"]["failing_guardrail"]
attack_vector = session["analysis"]["attack_vector"]

# Scan for code vulnerabilities

code_adversary = CodeAdversaryAgent()
vulns = code_adversary.find_vulnerabilities_related_to(
    attack_vector=attack_vector,
    guardrail=failing_guardrail
)
```

### Mitigate

Apply emergency patch in staging:

```bash

# Apply emergency patch

git checkout -b emergency/inc-${INCIDENT_ID}

# ... apply fixes ...

git commit -m "Emergency patch for incident ${INCIDENT_ID}"

# Deploy to staging

./scripts/deploy_staging.sh --branch emergency/inc-${INCIDENT_ID}

# Run full red-team campaign against patched flow

python scripts/run_red_team_campaign.py \
  --environment staging \
  --personas all \
  --targets ${AFFECTED_ENDPOINTS} \
  --verify-patch ${INCIDENT_ID}
```

### Validate

Triumvirate performs manual review:

```python
from src.app.core.council_hub import CouncilHub

hub = CouncilHub(kernel=kernel)

# Manual review by Triumvirate

review = hub.review_emergency_patch(
    incident_id=INCIDENT_ID,
    patch_branch="emergency/inc-${INCIDENT_ID}",
    require_unanimous=True  # All three must approve
)

if review["approved"]:

    # Run constitutional verification

    constitutional = hub._project["constitutional_guardrail"]
    const_review = constitutional.review_patch(patch_branch)

    # Run full JailbreakBench suite

    jbb = hub._project["jailbreak_bench"]
    bench_results = jbb.run_benchmark(
        patched_system,
        max_tests=200,  # Full HYDRA suite
        include_jbb=True
    )
```

______________________________________________________________________

## Recovery and Postmortem (24–72 hours)

### Restore

Gradual canary re-enable:

```python
from src.app.deployment.canary import CanaryDeployment

canary = CanaryDeployment(
    patch_branch="emergency/inc-${INCIDENT_ID}",
    initial_traffic=0.01,  # 1%
    increment=0.05,  # 5%
    increment_interval_hours=6
)

# Monitor metrics during rollout

canary.monitor_metrics([
    "attack_success_rate",
    "time_to_detect",
    "false_positive_rate",
    "agent_latency_p95"
])

# Auto-rollback if thresholds exceeded

canary.rollback_if(
    attack_success_rate="> 0.05",
    false_positive_rate="> 0.15",
    agent_latency_p95="> 3000"
)
```

### Postmortem

Produce comprehensive postmortem document:

**Template**: `docs/postmortems/INC-${INCIDENT_ID}.md`

```markdown

# Incident Postmortem: ${INCIDENT_ID}

## Timeline

- T+0min: Alert fired from attack_success_rate > threshold
- T+5min: Triage lead assigned (GALAHAD)
- T+10min: Rollback executed, endpoints throttled
- T+15min: Forensic snapshot created
- T+30min: Staging reproduction confirmed
- T+90min: Root cause identified (prompt injection in assistant flow)
- T+4hr: Emergency patch applied and tested
- T+12hr: Triumvirate approval obtained
- T+24hr: Canary deployment started (1% traffic)
- T+48hr: Deployment at 100%, incident resolved

## Root Cause

Prompt injection vulnerability in `/api/assistant` endpoint allowed
jailbreak_attacker persona to override system instructions via
role confusion attack vector.

Failing guardrail: SafetyGuard pattern matching insufficient for
encoded payloads.

## Remediation

1. Added detection pattern for encoded prompt injection
2. Enhanced SafetyGuard with multi-layer encoding detection
3. Updated constitutional principles to catch instruction override
4. Added test case to JailbreakBench for regression prevention

## Lessons Learned

- Need better detection for multi-turn encoded attacks
- SafetyGuard pattern database should include encoding variants
- Canary deployment worked well - caught issue at 5% traffic
- Forensic snapshot critical for reproduction

## Follow-up Actions

- [x] Add detection patterns to SafetyGuard persistent DB
- [x] Schedule regression campaign in 7 days
- [ ] Expand HYDRA dataset with encoding variations
- [ ] Update training for on-call engineers
- [ ] Review similar endpoints for same vulnerability

## Artifacts

- SARIF Report: artifacts/sarif/INC-${INCIDENT_ID}.sarif
- Attack Transcript: artifacts/transcripts/INC-${INCIDENT_ID}.json
- Forensic Snapshot: snapshots/snap-${INCIDENT_ID}.tar.gz.enc
- Red Team Results: artifacts/red_team/INC-${INCIDENT_ID}.json

```

### Follow Up

```bash

# Add detection patterns to SafetyGuard

python scripts/update_safety_patterns.py \
  --from-incident ${INCIDENT_ID} \
  --pattern-type jailbreak \
  --auto-extract

# Schedule regression campaign

python scripts/schedule_regression_campaign.py \
  --incident-id ${INCIDENT_ID} \
  --schedule "+7days" \
  --personas jailbreak_attacker \
  --targets ${AFFECTED_ENDPOINTS}
```

______________________________________________________________________

## Roles and Escalation

### Triumvirate Roles

- **GALAHAD**: Incident commander for detection and containment

  - Responsible for: Initial triage, user impact assessment, containment decisions
  - Escalation: Immediately notify if user data at risk

- **CERBERUS**: Forensic lead and evidence custodian

  - Responsible for: Forensic snapshot, evidence preservation, security analysis
  - Escalation: Immediately notify if external threat detected

- **CODEX DEUS MAXIMUS**: Remediation and patch approval

  - Responsible for: Root cause analysis, patch review, logical consistency
  - Escalation: Immediately notify if architectural change required

### External Escalation

**Requires Triumvirate approval for public disclosure**

Escalation ladder:

1. Internal security team (immediate)
1. Engineering leadership (within 1 hour)
1. Legal team (within 4 hours if data breach suspected)
1. PR/Communications (within 24 hours if public disclosure needed)
1. External authorities (only after legal review)

______________________________________________________________________

## Playbook Triggers and Criteria

### Auto-Trigger Conditions

```python

# In AlertManager rules

auto_trigger_incident_if(

    # Attack success above threshold

    attack_success_rate > 0.10 and persona_severity in ["critical", "high"]

    # Or data exfiltration detected

    or data_exfiltration_detected == True

    # Or multiple guardrail failures

    or (guardrail_failures > 3 and time_window_minutes < 15)

    # Or constitutional violation (high severity)

    or (constitutional_violation and violation_severity == "critical")
)
```

### Manual Trigger Criteria

- Any credible report of sensitive data leakage
- Model producing harmful instructions (verified)
- Systematic bypass of safety guardrails
- External security researcher report
- User complaint with evidence of harmful output

______________________________________________________________________

## Quick Reference Commands

### Immediate Response

```bash

# 1. Check incident status

python scripts/incident_status.py --incident-id ${INCIDENT_ID}

# 2. Execute containment

./scripts/incident_contain.sh --incident-id ${INCIDENT_ID}

# 3. Create forensic snapshot

python scripts/create_forensic_snapshot.py --incident-id ${INCIDENT_ID}

# 4. Reproduce in staging

python scripts/reproduce_incident.py --snapshot-id ${SNAPSHOT_ID}
```

### Monitoring

```bash

# Check current metrics

curl http://localhost:9090/metrics | grep security_

# View incident dashboard

open https://grafana.internal/d/incident-response

# Check Triumvirate status

python scripts/triumvirate_status.py --incident-id ${INCIDENT_ID}
```

### Recovery

```bash

# Start canary deployment

python scripts/canary_deploy.py --patch-id ${PATCH_ID}

# Monitor canary

python scripts/monitor_canary.py --deployment-id ${DEPLOYMENT_ID}

# Complete rollout

python scripts/complete_rollout.py --deployment-id ${DEPLOYMENT_ID}
```

______________________________________________________________________

## Triumvirate Triage Checklist

Use this checklist during incident triage:

- [ ] **Snapshot exists and is immutable**

  - Verify: `ls -l snapshots/snap-${INCIDENT_ID}.tar.gz.enc`
  - Check signature: `gpg --verify snapshots/snap-${INCIDENT_ID}.tar.gz.enc.sig`

- [ ] **Reproduce in isolated staging within 1 hour**

  - Run: `python scripts/reproduce_incident.py --snapshot-id ${SNAPSHOT_ID}`
  - Confirm: Same attack vector succeeds in staging

- [ ] **Identify failing guardrail and patch candidate**

  - RedTeam analysis: `python scripts/analyze_attack.py --transcript ${TRANSCRIPT_ID}`
  - Guardrail logs: `grep -r "VIOLATION" logs/guardrails/${DATE}/`
  - Patch proposal: CodeAdversary generates candidate patch

- [ ] **Decide on auto-PR vs manual patching**

  - Auto-PR: Low-risk, well-understood vulnerability, comprehensive tests
  - Manual: High-risk, requires architectural change, insufficient test coverage

- [ ] **Triumvirate approval obtained**

  - GALAHAD: ☐ Approved ☐ Rejected (reason: \_\_\_\_\_\_\_\_\_\_\_\_\_)
  - CERBERUS: ☐ Approved ☐ Rejected (reason: \_\_\_\_\_\_\_\_\_\_\_\_\_)
  - CODEX: ☐ Approved ☐ Rejected (reason: \_\_\_\_\_\_\_\_\_\_\_\_\_)
  - **Requires unanimous approval for critical incidents**

- [ ] **Full red-team campaign passed**

  - HYDRA: \_\_\_ / 200 tests passed
  - JBB: \_\_\_ / 30 tests passed
  - Custom scenarios: \_\_\_ / \_\_\_ tests passed

- [ ] **Postmortem scheduled**

  - Date: \_\_\_\_\_\_\_\_\_\_
  - Attendees: Security team, on-call engineer, Triumvirate representatives
  - Artifacts prepared: SARIF, transcripts, snapshots, metrics

______________________________________________________________________

**Document Version**: 1.0 **Last Updated**: 2026-01-21 **Owner**: Security Team / Triumvirate **Review Cycle**: After each incident + quarterly
