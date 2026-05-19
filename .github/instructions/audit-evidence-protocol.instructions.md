---
description: "Audit and evidence protocol: generating, validating, and maintaining tamper-evident audit trails."
applyTo: "**/*.py"
tags: [audit, evidence, logging, compliance, RFC3161]
created: 2026-05-13
status: mandatory
---

# Audit and Evidence Protocol

All meaningful actions must generate tamper-evident audit trails.

## Core Audit Principles

### 1. Evidence Over Logs
- **Logs** are for debugging (can be verbose, unstructured)
- **Evidence** is for compliance (must be structured, immutable, timestamped)
- Every governed action produces **evidence**, not just logs

### 2. Tamper Evidence
All evidence bundles should:
- Be timestamped (RFC 3161 TSA when available)
- Include request hash (SHA-256)
- Include context hash (reproducibility)
- Include policy version and hash
- Be append-only (no modifications)

### 3. Evidence Completeness
Evidence bundles must capture:
- What was requested (request_hash)
- Who requested it (user_id, session_id)
- When it was requested (timestamp)
- What governance decided (outcome: ALLOW/DENY/ESCALATE/TERMINATE)
- Why governance decided it (reason, policy_version)
- What risk was assessed (risk_score)
- What capabilities were checked (capability_domain)

## Evidence Bundle Structure

### Minimal Evidence Bundle
```json
{
  "request_hash": "sha256_of_request_text_truncated_to_32_chars",
  "context_hash": "sha256_of_sorted_context_dict",
  "timestamp": "2026-05-13T18:49:57.584-06:00",
  "session_id": "uuid_or_session_identifier",
  "domain": "agent.knowledge",
  "action": "update_knowledge_base",
  "outcome": "ALLOW",
  "policy_version": "v1.2.3",
  "policy_hash": "sha256_of_policy_file",
  "risk_score": 0.35,
  "user_id": "user_identifier",
  "duration_ms": 123
}
```

### Full Evidence Bundle
```json
{
  "request_hash": "a1b2c3d4e5f6...",
  "context_hash": "f6e5d4c3b2a1...",
  "timestamp": "2026-05-13T18:49:57.584-06:00",
  "timestamp_rfc3161": "base64_encoded_tsa_response",
  "session_id": "3c1aa4f6-5ca7-4070-90c2-c00beaa960b6",
  "user_id": "user_123",
  "domain": "agent.knowledge",
  "action": "update_knowledge_base",
  "request_text": "Update knowledge base with new entry about X",
  "context": {
    "user_id": "user_123",
    "session_id": "3c1aa4f6-5ca7-4070-90c2-c00beaa960b6",
    "request_text": "Update knowledge base with new entry about X"
  },
  "outcome": "ALLOW",
  "outcome_reason": "Policy permits knowledge updates for authenticated users",
  "policy_version": "v1.2.3",
  "policy_hash": "abc123def456",
  "risk_score": 0.35,
  "capability_domain": "knowledge.write",
  "capability_granted": true,
  "invariants_checked": [
    "escalation_requires_severity",
    "no_bypass_on_high_risk",
    "audit_all_denials"
  ],
  "invariants_passed": true,
  "duration_ms": 123,
  "safe_allow_calibration": {
    "risk_score": 0.35,
    "outcome": "ALLOW",
    "reason": "Below risk threshold"
  },
  "policy_decision": {
    "permitted": true,
    "policy_version": "v1.2.3",
    "policy_hash": "abc123def456"
  },
  "execution_authorization": {
    "approved": true,
    "reason": "User has write permission"
  },
  "evidence_chain_link": {
    "previous_hash": "previous_evidence_bundle_hash",
    "current_hash": "this_evidence_bundle_hash"
  }
}
```

## Generating Evidence

### Pattern 1: Via ExecutionGate
```python
from app.core.execution_gate import ExecutionGate

gate = ExecutionGate()

approved, result = gate.execute(
    domain="my_domain",
    action="my_action",
    context={
        "session_id": session_id,
        "user_id": user_id,
        "request_text": "Human-readable description of what was requested",
    },
    executor_fn=lambda ctx: perform_action(ctx),
)

# Evidence bundle automatically generated at:
# data/evidence/{session_id}-{timestamp}-{request_hash}.json
```

### Pattern 2: Manual Evidence Creation
```python
import hashlib
import json
import time
from datetime import datetime, timezone
from pathlib import Path

def create_evidence_bundle(
    domain: str,
    action: str,
    context: dict,
    outcome: str,
    outcome_reason: str,
    risk_score: float = 0.0,
) -> Path:
    """Create evidence bundle for an action.
    
    Args:
        domain: Action domain (e.g., 'agent.knowledge')
        action: Action name (e.g., 'update_knowledge_base')
        context: Context dict with session_id, user_id, request_text
        outcome: ALLOW|DENY|ESCALATE|TERMINATE
        outcome_reason: Human-readable reason for outcome
        risk_score: Assessed risk (0.0-1.0)
    
    Returns:
        Path to created evidence bundle.
    """
    request_text = context.get("request_text", f"{domain}.{action}")
    request_hash = hashlib.sha256(request_text.encode()).hexdigest()[:32]
    
    # Sort context for deterministic hash
    context_items = sorted(context.items())
    context_str = json.dumps(context_items, sort_keys=True)
    context_hash = hashlib.sha256(context_str.encode()).hexdigest()[:32]
    
    timestamp = datetime.now(timezone.utc).isoformat()
    session_id = context.get("session_id", "unknown")
    
    evidence = {
        "request_hash": request_hash,
        "context_hash": context_hash,
        "timestamp": timestamp,
        "session_id": session_id,
        "user_id": context.get("user_id", "unknown"),
        "domain": domain,
        "action": action,
        "request_text": request_text,
        "context": context,
        "outcome": outcome,
        "outcome_reason": outcome_reason,
        "risk_score": risk_score,
    }
    
    # Add RFC 3161 timestamp if available
    try:
        from app.core.acceptance_ledger import AcceptanceLedger
        ledger = AcceptanceLedger()
        tsa_response = ledger.get_rfc3161_timestamp(json.dumps(evidence, sort_keys=True))
        if tsa_response:
            evidence["timestamp_rfc3161"] = tsa_response
    except Exception:
        pass  # Graceful degradation
    
    # Write evidence
    evidence_dir = Path(os.getenv("EVIDENCE_DIR", "data/evidence"))
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    evidence_file = evidence_dir / f"{session_id}-{int(time.time())}-{request_hash}.json"
    
    with open(evidence_file, "w") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)
    
    return evidence_file
```

## Audit Trail Validation

### Validating Evidence Integrity
```python
import hashlib
import json
from pathlib import Path

def validate_evidence_bundle(evidence_path: Path) -> tuple[bool, str]:
    """Validate evidence bundle integrity.
    
    Args:
        evidence_path: Path to evidence bundle JSON.
    
    Returns:
        (is_valid, reason) tuple.
    """
    try:
        with open(evidence_path) as f:
            evidence = json.load(f)
    except Exception as e:
        return False, f"Failed to load evidence: {e}"
    
    # Required fields
    required = [
        "request_hash", "context_hash", "timestamp",
        "domain", "action", "outcome",
    ]
    
    missing = [field for field in required if field not in evidence]
    if missing:
        return False, f"Missing required fields: {missing}"
    
    # Validate request hash
    request_text = evidence.get("request_text", "")
    expected_hash = hashlib.sha256(request_text.encode()).hexdigest()[:32]
    if evidence["request_hash"] != expected_hash:
        return False, "Request hash mismatch"
    
    # Validate context hash
    context = evidence.get("context", {})
    context_items = sorted(context.items())
    context_str = json.dumps(context_items, sort_keys=True)
    expected_context_hash = hashlib.sha256(context_str.encode()).hexdigest()[:32]
    if evidence["context_hash"] != expected_context_hash:
        return False, "Context hash mismatch"
    
    # Validate RFC 3161 timestamp if present
    if "timestamp_rfc3161" in evidence:
        try:
            from app.core.acceptance_ledger import AcceptanceLedger
            ledger = AcceptanceLedger()
            evidence_without_tsa = {k: v for k, v in evidence.items() if k != "timestamp_rfc3161"}
            is_valid = ledger.verify_rfc3161_timestamp(
                json.dumps(evidence_without_tsa, sort_keys=True),
                evidence["timestamp_rfc3161"]
            )
            if not is_valid:
                return False, "RFC 3161 timestamp verification failed"
        except Exception as e:
            # Graceful degradation
            pass
    
    return True, "Evidence bundle valid"
```

### Validating Evidence Chain
```python
def validate_evidence_chain(evidence_dir: Path) -> tuple[bool, list[str]]:
    """Validate chronological evidence chain.
    
    Args:
        evidence_dir: Directory containing evidence bundles.
    
    Returns:
        (is_valid, list_of_issues) tuple.
    """
    evidence_files = sorted(evidence_dir.glob("*.json"))
    
    if not evidence_files:
        return True, []  # Empty chain is valid
    
    issues = []
    prev_timestamp = None
    
    for evidence_file in evidence_files:
        with open(evidence_file) as f:
            evidence = json.load(f)
        
        timestamp = evidence.get("timestamp")
        if not timestamp:
            issues.append(f"{evidence_file.name}: Missing timestamp")
            continue
        
        if prev_timestamp and timestamp < prev_timestamp:
            issues.append(
                f"{evidence_file.name}: Timestamp {timestamp} is before previous {prev_timestamp}"
            )
        
        prev_timestamp = timestamp
        
        # Validate individual bundle
        is_valid, reason = validate_evidence_bundle(evidence_file)
        if not is_valid:
            issues.append(f"{evidence_file.name}: {reason}")
    
    return len(issues) == 0, issues
```

## Audit Logging vs Evidence

### When to Use Audit Logging
- Debugging and troubleshooting
- Development and testing
- Verbose operational details
- Non-governance actions

### When to Generate Evidence
- Governed actions (REQUIRED)
- Security decisions (REQUIRED)
- Denials and escalations (REQUIRED)
- Policy enforcement (REQUIRED)
- Capability grants (REQUIRED)

### Combined Pattern
```python
import logging
from app.core.execution_gate import ExecutionGate

logger = logging.getLogger(__name__)

def perform_governed_action(user_id: str, action_params: dict) -> dict:
    """Perform action with both logging and evidence."""
    gate = ExecutionGate()
    
    # Audit log (for debugging)
    logger.info(
        f"User {user_id} requesting action with params: {action_params}"
    )
    
    # Evidence generation (for compliance)
    approved, result = gate.execute(
        domain="my_domain",
        action="my_action",
        context={
            "user_id": user_id,
            "session_id": get_session_id(),
            "request_text": f"Perform action with {action_params}",
        },
        executor_fn=lambda ctx: execute_action(action_params),
    )
    
    # Audit log outcome
    if approved:
        logger.info(f"Action approved and executed: {result}")
    else:
        logger.warning(f"Action denied: {result}")
    
    return result
```

## Evidence Retention

### Retention Policy
- **Evidence bundles**: Retain indefinitely (tamper-evident audit trail)
- **Audit logs**: Retain for 90 days (debugging)
- **Denial evidence**: Retain indefinitely (compliance)
- **Escalation evidence**: Retain indefinitely (incident response)

### Archive Pattern
```python
import shutil
from datetime import datetime, timedelta
from pathlib import Path

def archive_old_audit_logs(audit_dir: Path, retention_days: int = 90):
    """Archive audit logs older than retention period.
    
    Evidence bundles are never archived (retained indefinitely).
    """
    cutoff = datetime.now() - timedelta(days=retention_days)
    archive_dir = audit_dir / "archive"
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    for log_file in audit_dir.glob("*.log"):
        if log_file.stat().st_mtime < cutoff.timestamp():
            shutil.move(str(log_file), str(archive_dir / log_file.name))
```

## Evidence Query Patterns

### Find Denials
```python
import json
from pathlib import Path

def find_denials(evidence_dir: Path, since_days: int = 7) -> list[dict]:
    """Find all denied actions in recent evidence."""
    from datetime import datetime, timedelta
    
    cutoff = datetime.now() - timedelta(days=since_days)
    denials = []
    
    for evidence_file in evidence_dir.glob("*.json"):
        with open(evidence_file) as f:
            evidence = json.load(f)
        
        if evidence.get("outcome") == "DENY":
            timestamp = datetime.fromisoformat(evidence["timestamp"])
            if timestamp >= cutoff:
                denials.append(evidence)
    
    return denials
```

### Find High-Risk Actions
```python
def find_high_risk_actions(evidence_dir: Path, threshold: float = 0.7) -> list[dict]:
    """Find actions with high risk scores."""
    high_risk = []
    
    for evidence_file in evidence_dir.glob("*.json"):
        with open(evidence_file) as f:
            evidence = json.load(f)
        
        if evidence.get("risk_score", 0.0) >= threshold:
            high_risk.append(evidence)
    
    return high_risk
```

## Related Files

- `src/app/core/execution_gate.py` — Evidence generation
- `src/app/core/acceptance_ledger.py` — RFC 3161 timestamping
- `src/app/core/invariant_engine.py` — Invariant validation
- `data/evidence/` — Evidence bundle storage
- `data/acceptance_ledger/` — Acceptance ledger storage
