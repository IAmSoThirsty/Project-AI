---
type: governance-invariant
tags: [governance, security, authorization, execution-control, invariant]
created: 2026-05-13
last_verified: 2026-05-13
status: mandatory
enforcement_level: critical
related_systems: [execution-gate, octoreflex, triumvirate, nirl, invariant-engine]
stakeholders: [all-agents, all-copilots, security-team, governance-team]
config_scope: all-execution-contexts
automation_type: enforced
review_cycle: never-disable
supersedes: none
---

---
description: "MANDATORY execution governance invariant: No meaningful execution without prior governance authorization. Deny-by-default for all execution types."
applyTo: "**"
enforcement: "CRITICAL"
---

# Execution Governance Invariant

## Invariant Statement

**No meaningful execution may occur unless governance has authorized it first.**

This is a foundational security invariant. Violation of this invariant is a **critical governance failure**.

## Scope: What Requires Authorization

The following execution types **MUST** pass through governance authorization before execution:

### 1. Model/LLM Calls
- OpenAI API requests (chat, completions, embeddings, DALL-E, etc.)
- Hugging Face model inference
- Any external AI/ML provider requests
- Local model inference (if applicable)
- Token consumption actions

### 2. Shell/Subprocess Actions
- Any `powershell`, `bash`, `cmd` execution
- Process spawning (`subprocess`, `os.system`, etc.)
- Interactive shell sessions
- Background/detached processes
- System commands of any kind

### 3. File System Operations
- File writes (create, edit, delete)
- Directory creation/deletion
- File moves/renames
- Permission changes
- Symbolic link creation

### 4. Database Mutations
- SQL INSERT, UPDATE, DELETE, DROP
- NoSQL write operations
- Redis SET, INCR, DEL operations
- Session database modifications
- Any state persistence writes

### 5. Provider Requests
- HTTP/HTTPS requests to external APIs
- GitHub API calls (write operations)
- Cloud provider API calls
- Webhook triggers
- Email/SMS sends

### 6. Deployment Actions
- Docker build/push/run
- Container starts/stops
- Service deployments
- Infrastructure provisioning
- Configuration deployments

### 7. Training/Fine-tuning Actions
- Model training starts
- Fine-tuning jobs
- Dataset uploads
- Checkpoint saves
- Hyperparameter updates

### 8. Plugin Actions
- Plugin enable/disable
- Plugin execution
- Plugin state changes
- Plugin API calls

### 9. Workbench Actions
- Code execution in notebooks
- REPL evaluation
- Test execution (when destructive)
- Build operations
- Package installations

## Required Authorization Chain

Every execution **MUST** follow this chain in order:

```
1. Request received
   ↓
2. Identity/Authority check
   - Who is requesting?
   - What credentials/session/token?
   - Is identity verified?
   ↓
3. Capability/Policy check
   - Does requester have capability?
   - What policy applies?
   - Is action permitted under policy?
   ↓
4. State verification
   - Is system state valid?
   - Are preconditions met?
   - Is state continuity verified?
   ↓
5. Governance decision
   - ExecutionGate.execute() OR
   - Triumvirate endpoint verdict OR
   - OctoReflex enforcement decision
   ↓
6. Audit/Evidence record
   - Write acceptance ledger entry
   - Log governance decision
   - Capture evidence (SHA-256, timestamp, decision)
   ↓
7. Execution OR Denial
   - If authorized: execute with audit trail
   - If denied: return denial reason + audit
```

**Breaking this chain or reordering steps is non-compliant.**

## Deny-by-Default Conditions

The following conditions **MUST** result in denial (no execution):

### 1. Authority Missing
- No valid session/token
- Unknown identity
- Expired credentials
- Insufficient privileges

### 2. Capability Missing
- Requester lacks required capability
- Capability revoked
- Capability expired
- Capability suspended

### 3. State Continuity Unverified
- System state is inconsistent
- Precondition check failed
- State hash mismatch
- State transition invalid

### 4. Policy Ambiguous
- Multiple conflicting policies
- Policy parse error
- Policy not found
- Policy condition indeterminate

### 5. Audit Cannot Be Written
- Acceptance ledger unavailable
- Audit log write failed
- Evidence capture failed
- Timestamp service unavailable (graceful degradation may apply per NIRL)

### 6. Evidence Cannot Be Produced
- SHA-256 hash computation failed
- Signature generation failed
- Proof construction failed
- Chain-of-custody broken

### 7. Governance Path Unavailable
- ExecutionGate unreachable
- Triumvirate server down
- OctoReflex offline
- InvariantEngine not loaded

## Anti-Pattern: Permissive Fallbacks

**NEVER** implement permissive fallbacks such as:

```python
# ❌ FORBIDDEN
try:
    governance_decision = execution_gate.check(action)
except Exception:
    governance_decision = "ALLOW"  # NEVER DO THIS

# ❌ FORBIDDEN
if governance_available:
    check_authorization()
else:
    execute_anyway()  # NEVER DO THIS

# ❌ FORBIDDEN
if not audit_written:
    logger.warning("Audit failed, but continuing")
    execute()  # NEVER DO THIS
```

**Correct pattern: Fail closed**

```python
# ✅ CORRECT
try:
    governance_decision = execution_gate.check(action)
except Exception as e:
    logger.error(f"Governance unavailable: {e}")
    return ExecutionResult(
        status="DENIED",
        reason="Governance path unavailable",
        evidence=None
    )

# ✅ CORRECT
if not governance_available:
    raise GovernanceUnavailableError(
        "Cannot execute: governance path unavailable"
    )

# ✅ CORRECT
audit_result = write_audit(action, decision)
if not audit_result.success:
    raise AuditFailureError(
        "Cannot execute: audit record failed"
    )
```

## Implementation Guidance for AI Agents

### Before ANY Execution Action

1. **Identify the execution type** (model call, shell, file write, etc.)
2. **Do NOT proceed directly** — stop and invoke governance
3. **Call the appropriate governance check:**
   - For code execution: `ExecutionGate.execute()`
   - For shell commands: `ExecutionGate.execute()` before `powershell`/`bash`
   - For file writes: `ExecutionGate.execute()` before `create`/`edit`
   - For API calls: `ExecutionGate.execute()` before HTTP request
4. **Await governance decision** — do not timeout and proceed
5. **If denied:** return denial to user with reason
6. **If allowed:** verify audit was written, then execute
7. **After execution:** verify evidence was recorded

### Example: File Write

```python
# Agent pseudocode for file write
action = {
    "type": "file_write",
    "path": "src/app/new_module.py",
    "operation": "create",
    "content_hash": hashlib.sha256(content.encode()).hexdigest()
}

# MUST call governance first
result = execution_gate.execute(action, context)

if result.status == "DENIED":
    return f"Governance denied: {result.reason}"

if result.status == "ALLOWED":
    # Verify audit
    if not result.evidence or not result.evidence.get("ledger_entry"):
        return "Audit verification failed, cannot proceed"
    
    # NOW execute
    create_file(path, content)
    
    # Verify evidence
    verify_acceptance_ledger_contains(result.evidence["ledger_entry"])
```

### Example: Model Call

```python
# Agent pseudocode for OpenAI call
action = {
    "type": "model_call",
    "provider": "openai",
    "model": "gpt-4",
    "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest(),
    "max_tokens": 500
}

result = execution_gate.execute(action, context)

if result.status != "ALLOWED":
    return f"Cannot call model: {result.reason}"

# Execute with audit trail
response = openai.ChatCompletion.create(
    model=action["model"],
    messages=messages,
    max_tokens=action["max_tokens"]
)

# Log consumption
log_token_usage(response.usage, result.evidence)
```

### Example: Shell Command

```python
# Agent pseudocode for shell execution
action = {
    "type": "shell_command",
    "command": "pytest tests/",
    "shell_type": "powershell",
    "working_dir": os.getcwd()
}

result = execution_gate.execute(action, context)

if result.status == "DENIED":
    raise ExecutionDeniedError(result.reason)

# Proceed only if allowed
powershell(
    command=action["command"],
    mode="sync",
    initial_wait=120
)
```

## Integration Points

This invariant is enforced by:

1. **ExecutionGate** (`src/app/core/execution_gate.py`)
   - Primary enforcement point
   - Routes to OctoReflex for decisions
   - Writes acceptance ledger entries

2. **OctoReflex** (`src/app/governance/octoreflex.py`)
   - Enforcement level determination (WARN/BLOCK/TERMINATE/ESCALATE)
   - Calls InvariantEngine for invariant validation
   - Interfaces with Triumvirate for policy decisions

3. **InvariantEngine** (`src/app/core/nirl/invariant_engine.py`)
   - Loads and validates canonical invariants
   - Provides violation detection
   - Returns invariant check results

4. **Triumvirate** (`src/app/governance/triumvirate_server.py`)
   - Cerberus: Threat assessment
   - Codex: Constitutional review
   - Galahad: Rights verification
   - Runs as daemon on port 8001

5. **Acceptance Ledger** (`src/app/governance/acceptance_ledger.py`)
   - RFC 3161 timestamping (DigiCert TSA)
   - Immutable audit trail
   - Evidence production

## Verification

To verify this invariant is enforced:

```powershell
# Run canonical replay (must show 5/5 invariants pass)
$env:PYTHONIOENCODING="utf-8"
$env:PYTHONPATH="src"
py -3.12 canonical/replay.py
```

Expected output:
```
✓ Invariant 1: execution-governance (PASS)
✓ Invariant 2: state-continuity (PASS)
✓ Invariant 3: rights-preservation (PASS)
✓ Invariant 4: audit-integrity (PASS)
✓ Invariant 5: deny-by-default (PASS)
```

## Monitoring

Governance denials are monitored via:

- **Drift alerts:** `data/governance_drift_alerts/*.json`
- **Audit logs:** `data/governance/audit_log.jsonl`
- **Acceptance ledger:** `data/governance/acceptance_ledger.jsonl`
- **Triumvirate logs:** `data/governance/triumvirate_decisions/*.json`

Crisis detection threshold: 3+ denials in 24 hours.

## Non-Compliance Consequences

Bypassing this invariant results in:

1. **Canonical replay failure** (invariant check fails)
2. **Governance drift alert** (crisis detection triggered)
3. **OctoReflex escalation** (ESCALATE enforcement level)
4. **Audit trail corruption** (evidence chain broken)
5. **Policy violation** (workspace profile non-compliance)

## Exception Handling

**There are no exceptions to this invariant.**

Even in emergency scenarios:
- Governance path must be available
- If governance is down, execution must be denied
- Graceful degradation applies only to audit timestamp service (per NIRL Heart spec)

## AI Agent Checklist

Before executing ANY action, verify:

- [ ] Action type is identified
- [ ] Governance check is invoked
- [ ] Decision is awaited (no timeout bypass)
- [ ] Denial results in no execution
- [ ] Approval results in audit verification
- [ ] Evidence is captured post-execution
- [ ] No permissive fallback is used

## Related Policies

- `.github/copilot_workspace_profile.md` — Governance policy
- `canonical/scenario.yaml` — Canonical governance scenario
- `docs/nirl/NIRL_IMPLEMENTATION.md` — NIRL Heart/MiniBrain/Antibody/Forge
- `docs/governance/TRIUMVIRATE_DOMAIN_MAPPING.md` — Cerberus/Codex/Galahad mapping

## Enforcement Level

**CRITICAL** — This invariant is non-negotiable and applies to all agents, copilots, plugins, and execution contexts.

---

**Summary:** Request → Authority → Capability → State → Governance → Audit → Execute/Deny. Deny when any step fails. No permissive fallbacks.
