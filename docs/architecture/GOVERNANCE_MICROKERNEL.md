# Governance Microkernel Architecture

**Version:** 1.0.0  
**Branch:** 05-09-26-Structural-upgrades  
**Status:** Active  

---

## Overview

The Governance Microkernel is the minimal, trusted core that every governed execution must pass through. It enforces the invariant: **no action executes without an authorized, audited, evidence-bound decision.**

The kernel's job is narrow by design — it does not implement policy logic, it does not evaluate business rules. It enforces the structural contract that policy evaluation happened, was authorized, is cryptographically bound, and has been logged.

---

## Kernel Responsibilities

The kernel owns exactly five responsibilities:

1. **Admissibility check** — Is this action type even evaluable by the current governance configuration?
2. **Invariant enforcement** — Are all system invariants intact before proceeding?
3. **Continuity proof** — Is the governance state chain unbroken?
4. **Authorization binding** — Is the specific execution instance authorized by a valid, scoped capability token?
5. **Evidence emission** — Has an evidence bundle been written for this outcome?

Everything else — risk classification, policy lookup, semantic analysis, threat scoring — happens in the outer pipeline and feeds into the kernel as pre-computed inputs.

---

## Pipeline Architecture

```
Ingress Request
      │
      ▼
┌─────────────────────────────────────────────────────┐
│                  ExecutionGate                       │
│  Stage 1: Kernel evaluation (admissibility/invars)  │
│  Stage 2: SafeAllowCalibration (risk scoring)       │
│  Stage 3: PolicyDecision (type-level permit)        │
│  Stage 4: PolicyRegistry binding verify             │
│  Stage 5: Sovereign runtime check                   │
│  Stage 6: CapabilityToken verify (instance auth)    │
│  Stage 7: SemanticCollision detection               │
│  Stage 8: InvariantSeverity final check             │
│  Stage 9: Execute + emit EvidenceBundle             │
└─────────────────────────────────────────────────────┘
      │
      ▼
GovernanceResult(outcome, reason, metadata, hash)
```

---

## Kernel Boundary

The kernel boundary is the set of modules that operate at HALT or ESCALATE severity — modules whose failure must stop execution unconditionally:

| Module | Kernel Role | Failure Outcome |
|--------|------------|-----------------|
| `invariant_severity.py` | Invariant enforcement | HALT or ESCALATE depending on severity |
| `state_register.py` (StateBranchingProtector) | Continuity proof | BranchConflictError → HALT |
| `evidence_bundle.py` | Evidence emission | EvidenceBundle required for all outcomes |
| `policy_registry.py` | Policy binding | Deny-default if registry unavailable |
| `execution_authorization.py` | Instance authorization | Deny on any guard failure |

Modules outside the kernel boundary (risk scoring, threat register, semantic collision) produce signals that feed into kernel decisions but cannot bypass the kernel's structural checks.

---

## Governance Modes

```python
class GovernanceMode(str, Enum):
    SOVEREIGN   = "SOVEREIGN"    # Full kernel active, all guards enforced
    DEGRADED    = "DEGRADED"     # Read-only permitted; mutating → HUMAN_APPROVAL_REQUIRED
    DISTRIBUTED = "DISTRIBUTED"  # Not yet implemented — see below
    BFT         = "BFT"          # Not yet implemented — see below
```

### SOVEREIGN (Default)
All 9 pipeline stages active. This is the only mode where mutating actions are authorized. High-impact actions require explicit human confirmation regardless of risk score.

### DEGRADED
Entered when the governance kernel detects partial failure (e.g., TSA unavailable, invariant at WARN, registry degraded). Read-classified actions proceed with `DEGRADED_READ_ONLY` outcome. Mutating actions require `HUMAN_APPROVAL_REQUIRED`. The `LiaraFallbackAuthority` operates at `AUTHORITY_LEVEL = "REDUCED"` — it cannot authorize actions beyond its reduced scope.

### DISTRIBUTED (Roadmap)
**Not implemented.** Reserved for multi-node governance consensus where policy decisions require quorum across N governance nodes. Calling `set_governance_mode(GovernanceMode.DISTRIBUTED)` raises `NotImplementedError` with reference to this document.

Design requirements for future implementation:
- Byzantine fault tolerance for up to `f` faulty nodes in a `3f+1` quorum
- Signed vote aggregation per policy decision
- Cross-node evidence bundle synchronization
- Split-brain detection and automatic HALT on quorum loss

### BFT (Roadmap)
**Not implemented.** Byzantine Fault Tolerant governance — extends DISTRIBUTED with active adversary tolerance. Requires cryptographic leader election and view-change protocol. Raises `NotImplementedError`.

---

## Invariant Registry

The kernel maintains five built-in invariants evaluated at execution time:

| Invariant | Severity | Condition |
|-----------|----------|-----------|
| `optional_metadata` | WARN | Metadata fields present but not required |
| `continuity_proof_fresh` | BLOCK | Continuity proof must be < 300s old |
| `no_forged_continuity` | HALT | Predecessor hash must match chain head |
| `signing_key_match` | ESCALATE | Active signing key must match registered key |
| `invariant_registry_integrity` | ESCALATE | Invariant registry itself must not be tampered |

Severity ordering: `INFO < WARN < BLOCK < HALT < ESCALATE`

BLOCK and above prevent execution. HALT mandates immediate stop. ESCALATE mandates human/council review before any further execution.

---

## Deny-Default Posture

The kernel operates deny-default at every layer:

- PolicyRegistry unavailable → DENY (not ALLOW)
- CapabilityToken missing → DENY
- InvariantSeverity evaluation error → treated as ESCALATE
- TimeTrust TSA unavailable → DEGRADED_READ_ONLY (not silent success)
- StateBranchingProtector lock failure → BranchConflictError (not silent proceed)
- Evidence bundle write failure → logged; outcome still recorded as attempted

No positive authorization is assumed. Every ALLOW must be earned through the full pipeline.

---

## Extension Points

The kernel is intentionally minimal. Extend governance behavior through:

1. **New invariants** — Register in `InvariantRegistry`; assign appropriate severity
2. **New outcome types** — Add to `GovernanceOutcome` enum; update `is_executable()`
3. **New pipeline stages** — Insert into `ExecutionGate._run_pipeline()` between stages 1-8; stage 9 (evidence emit) must always be last
4. **New violation types** — Add to `ViolationType` in `octoreflex.py`

Do not add business logic to the kernel. Business logic belongs in the outer pipeline stages (SafeAllowCalibration, PolicyDecision, ConversationThreatRegister).
