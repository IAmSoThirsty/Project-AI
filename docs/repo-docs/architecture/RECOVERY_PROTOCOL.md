# Genesis Re-Anchoring: Sovereign Recovery Protocol

**Version:** 1.0.0
**Branch:** 05-09-26-Structural-upgrades
**Status:** Active — Guarded Stub
**Classification:** CRITICAL OPERATIONAL PROCEDURE

---

## What This Is

Genesis Re-Anchoring is the last-resort recovery operation for catastrophic continuity loss. It creates a new genesis anchor — a temporal root with no predecessor — resetting the governance state chain from a known-good point.

This operation exists because the alternative is worse: a system with a corrupted or unverifiable continuity chain that continues operating as if nothing happened. That is not acceptable.

**This is not a routine operation. If you are reading this for the first time during an incident, stop. Get a human governance authority on the call before proceeding.**

---

## When This Is Warranted

Genesis Re-Anchoring is warranted only when ALL of the following are true:

1. The governance state chain is verifiably corrupted or unrecoverable
2. Normal continuity recovery (re-replaying from last valid ancestor) has been attempted and failed
3. The system cannot safely operate in DEGRADED mode with the current chain state
4. A human governance authority has reviewed the incident and authorized recovery

It is NOT warranted for:
- Routine key rotation (use PolicyRegistry mutation with signing key update)
- TSA unavailability (system enters DEGRADED_READ_ONLY automatically)
- Single-node state divergence (use StateBranchingProtector adjudication)
- Policy version drift (use PolicyRegistry re-registration)

---

## Prerequisites

Before invoking genesis re-anchoring, the following must be in place:

### Environment Configuration
```bash
# Must be set out-of-band — NOT in the application's normal config:
export GENESIS_ROOT_AUTHORITY_TOKEN="<root-authority-token>"
```

This token is NOT the same as the application's signing key. It is a separate credential held by governance authorities, not by the application runtime. It must be set in a separate shell session, not sourced from the application's `.env`.

### Blocked Callers
The following system components are permanently blocked from invoking genesis re-anchoring, regardless of token:

- `ExecutionGate`
- `IronPathExecutor`
- `PolicyDecisionEvaluator`
- `ExecutionAuthorizationEvaluator`
- `CapabilityTokenService`

Any attempt from these components raises `GenesisReanchorDenied` immediately. This is enforced in `_NORMAL_RUNTIME_SENTINELS` and is not configurable at runtime.

---

## Invocation

```python
from app.core.genesis_reanchor import (
    invoke_genesis_reanchor,
    GenesisReanchorRequest,
    GenesisReanchorDenied,
)

request = GenesisReanchorRequest(
    requested_by="governance-authority-name",
    root_authority_token="<GENESIS_ROOT_AUTHORITY_TOKEN value>",
    reason="<non-empty human-readable reason — will be audited>",
    evidence={
        "incident_id": "INC-XXXX",
        "incident_summary": "...",
        "chain_corruption_proof": "...",
        "recovery_attempt_log": "...",
    },
    human_confirmation_id="<HCI from human authority sign-off>",
    requesting_caller="OutOfBandRecoveryTool",  # Must not be a sentinel
)

try:
    result = invoke_genesis_reanchor(request)
    print(f"New anchor: {result.new_anchor_id}")
    print(f"Anchor hash: {result.new_anchor_hash}")
    print(f"Audit entry: {result.audit_entry}")
except GenesisReanchorDenied as e:
    print(f"DENIED: {e}")
    # Do not retry without re-establishing prerequisites
```

---

## Guard Sequence

The invocation passes through five guards in order. All must pass:

```
Guard 1: GENESIS_ROOT_AUTHORITY_TOKEN configured in environment
         └── Fail → GenesisReanchorDenied("not configured")

Guard 2: request.root_authority_token matches env var
         (constant-time comparison via hmac.compare_digest)
         └── Fail → CRITICAL audit log + GenesisReanchorDenied("token mismatch")

Guard 3: requesting_caller NOT in _NORMAL_RUNTIME_SENTINELS
         └── Fail → CRITICAL audit log + GenesisReanchorDenied("normal_runtime_invocation_blocked")

Guard 4: reason, evidence, human_confirmation_id all non-empty
         └── Fail → GenesisReanchorDenied with specific missing field

Guard 5: (implicit) All above passed
         └── Success → New TemporalAnchor created, CRITICAL audit log written
```

---

## What Happens on Success

1. A new `TemporalAnchor` is created with `anchor_id = "GENESIS_<uuid>"` and no predecessor
2. The anchor hash is computed from the anchor contents
3. A CRITICAL-severity audit entry is written containing:
   - `requested_by`
   - `reason`
   - `evidence` dict
   - `human_confirmation_id`
   - `new_anchor_id`
   - `new_anchor_hash`
   - `severity: "CRITICAL"`
4. The audit entry is logged at CRITICAL level
5. A `GenesisReanchorResult` is returned with the above fields

The new anchor becomes the new chain head. All subsequent `StateBranchingProtector.advance()` calls must use the new anchor hash as their first predecessor.

---

## Post-Recovery Steps

After a successful genesis re-anchoring:

1. **Verify the new anchor** — Confirm `new_anchor_id` starts with `"GENESIS_"` and `new_anchor_hash` is non-empty
2. **Re-register policies** — The new chain has no policy history; re-register all active policies in `PolicyRegistry` with fresh signatures
3. **Re-issue capability tokens** — All existing tokens are invalidated by the chain reset; issue fresh tokens
4. **Re-run governance liveness tests** — `tests/test_governance_liveness.py` must pass before resuming production traffic
5. **Preserve audit entry** — The `audit_entry` from `GenesisReanchorResult` must be stored in your incident management system
6. **Human sign-off on resumption** — A governance authority must confirm the system is in a known-good state before resuming mutating operations

---

## Security Constraints

- **Never store** `GENESIS_ROOT_AUTHORITY_TOKEN` in source code, `.env` files, or application config
- **Never log** the token value — only log whether the operation succeeded or failed
- **Rotate** the token after any use (denied or approved)
- **The `human_confirmation_id`** should be a ticket, Zoom call recording ID, or other durable reference to the human authorization decision — not a self-issued identifier
- **The `requesting_caller`** field is audited — use a descriptive, specific name for your recovery tooling

---

## Implementation Notes

The current implementation is a **guarded stub**. The guard logic, audit trail, and result structure are production-grade. The actual continuity chain integration (wiring the new anchor into the live `StateBranchingProtector`) requires operational tooling specific to your deployment. The stub's output (`GenesisReanchorResult`) is the authoritative handoff point for that tooling.

Source: `src/app/core/genesis_reanchor.py`
Tests: `tests/test_genesis_reanchor.py` — 7/7 passing
