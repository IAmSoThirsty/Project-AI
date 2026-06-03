# Constitutional Substrate Consolidation — Phase 0 Report
> Branch: substrate-consolidation  
> Date: 2026-06-03  
> Status: Complete — no behavior changed

---

## Baseline Test Status

**Constitutional substrate test suite: 118 passed, 0 failed, 1 warning**

Tests run:
- `tests/test_governance_contract.py` — 23 passed
- `tests/test_execution_gate_enforcement.py` — 3 passed
- `tests/test_evidence_bundle.py` — 11 passed
- `tests/test_audit_log.py` — 12 passed
- `tests/test_immutable_audit_log.py` — 13 passed
- `tests/test_governance_server.py` — 23 passed
- `tests/test_12_vector_constitutional_break.py` — 11 passed
- `tests/test_external_merkle_anchor.py` — 22 passed

Full test collection: 41 collection errors in unrelated modules (temporal, gradle_evolution, robotic, memory_optimization, etc.). These pre-exist on master and are unrelated to constitutional substrate work.

---

## Caller Map

### audit_log.py (`src/app/governance/audit_log.py`)
**Direct callers (production):**
- `src/app/cli.py:117` — `AuditLog()` constructed on demand
- `src/app/core/governance_kernel.py:139,141` — `AuditLog().log_event()` in `_approve()`
- `src/app/core/governance_kernel.py:188,190` — `AuditLog().log_event()` in `_reject()`
- `src/app/health/report.py:41,96` — `AuditLog()` stored on HealthReport instance

**Critical finding:** `governance_kernel.py` bypasses `audit_manager.py` entirely. The kernel — the canonical authority chain coordinator — writes directly to the lower-level `AuditLog`. Every kernel approval and rejection is not going through the sovereign audit path.

**Migration order:** `governance_kernel.py` first (highest authority), then `health/report.py`, then `cli.py`.

---

### immutable_audit_log.py (`src/app/security/immutable_audit_log.py`)
**Direct callers (production):** None.

Only `tests/test_immutable_audit_log.py` imports it. Safe to convert to shim in Phase 2 without touching any production path.

---

### sovereign_audit_log.py (`src/app/governance/sovereign_audit_log.py`)
**Direct callers (production):**
- `src/app/governance/audit_manager.py:15,59` — only caller; correctly routes through the public interface

The canonical chain is already partially correct. No direct production bypass of sovereign_audit_log.

---

### audit_manager.py (`src/app/governance/audit_manager.py`)
**Direct callers (production):** None.

`audit_manager.py` exists and is structurally correct. It calls `sovereign_audit_log.py`. But nothing calls it. Phase 2 is wiring production code to it, not building it.

---

### capability_token.py (`src/app/core/capability_token.py`)
**Direct callers (production):**
- `src/app/core/execution_gate.py:191` — imports `CapabilityTokenService` and validates tokens at Stage 6

**Name collision:** `CapabilityToken` class also exists in `src/psia/schemas/capability.py` (Pydantic, Ed25519 schema). `src/app/core/capability_token.py` uses HMAC-SHA256. Two incompatible token representations coexist under the same name.

`src/psia/canonical/capability_authority.py:111` constructs its own `CapabilityToken` using the Pydantic schema.

---

### capability_authority.py (`src/psia/canonical/capability_authority.py`)
**Direct callers (production):** None.

The canonical Ed25519 token issuer is fully tested and isolated. It has zero wiring to `execution_gate.py`. Phase 3 connects them.

---

### execution_gate.py (`src/app/core/execution_gate.py`)
**Direct callers (production):**
- `src/app/core/execution_router.py:9` — imports `get_execution_gate`
- `src/app/core/octoreflex.py:372` — imports `get_execution_gate` (conditional/inline)

`execution_gate.py` already emits `EvidenceBundle` on every DENY path. Gap: bundles go to the observability collector, not through `audit_manager.py`. Addressed in Phase 2.

---

### governance_kernel.py (`src/app/core/governance_kernel.py`)
**Direct callers (production):**
- `src/app/core/execution_gate.py:22` — imports `get_kernel`; kernel is called by gate

Call direction confirmed: **execution_gate → governance_kernel** (not the reverse).

Kernel calls `get_ledger().attest(record)` (constitutional_ledger) and `AuditLog().log_event()` (direct audit bypass). Both are addressed in Phase 2.

---

### pipeline.py (`src/app/core/governance/pipeline.py`)
**Direct callers (production):**
- `src/app/runtime/router.py` — parallel execution entry point that does NOT route through `execution_gate.py`

`pipeline.py` contains `_enforce_mutation_governance_binding()` which calls `IronPathExecutor` directly — a documented bypass of the canonical lifecycle. Phase 1 documents this; Phase 4 addresses it.

---

### runtime_enforcer.py (`src/app/governance/runtime_enforcer.py`)
**Direct callers (production):**
- `src/app/core/execution_router.py:39,47` — called at step 2.5, **before** `ExecutionGate`

`RuntimeEnforcer.enforce()` can produce DENY/WARN. A DENY at this point produces no `EvidenceBundle` and writes nothing to `audit_manager`. This is the highest-priority Phase 4 fix: a parallel final authority that produces unaudited denials.

---

### policy_registry.py (`src/app/core/policy_registry.py`)
**Direct callers (production):**
- `src/app/core/evidence_bundle.py:120` — calls `get_policy_registry()`
- `src/app/core/execution_authorization.py:155` — calls `get_policy_registry()`
- `src/app/core/policy_decision.py:77` — calls `get_policy_registry()`

Clean. The registry is correctly consulted. Gap: `src/cognition/adapters/policy_engine.py` and `src/cognition/cerberus/engine.py` run their own `PolicyEngine` without consulting `policy_registry`. Addressed in Phase 5.

---

### policy_decision.py (`src/app/core/policy_decision.py`)
**Direct callers (production):** Called by `execution_gate` Stage 2. Correctly consults `policy_registry`. Clean.

---

### governance_service.py (`src/app/core/services/governance_service.py`)
**Direct callers (production):**
- `src/app/core/services/__init__.py:17` — exported from services package

Used by the 11-agent fleet as a CognitionKernel-layer advisory service. Does not call `ExecutionGate` or `audit_manager`. Advisory layer only — not a final DENY authority. Not a competitor to `GovernanceManager`.

---

### governance_manager.py (`src/app/governance/governance_manager.py`)
**Direct callers (production):** None.

Stub proposal/voting system. No callers in src/. Not a competitor to `GovernanceService`. Phase 7 will determine whether it has any intended role.

---

### constitutional_ledger.py (`src/app/core/constitutional_ledger.py`)
**Direct callers (production):**
- `src/app/core/governance_kernel.py:11,135,184` — calls `get_ledger().attest(record)` in `_approve` and `_reject`

Creates independent governance records (`LedgerEntry`) without referencing an `EvidenceBundle` `bundle_id`. Addressed in Phase 2: ledger records should attach to the bundle, not be independent artifacts.

---

## Duplicate Authority Table

| Risk | Duplicate pair | Problem |
|---|---|---|
| CRITICAL | `runtime_enforcer.py` vs `execution_gate.py` | Two final DENY authorities; RuntimeEnforcer denials produce no EvidenceBundle |
| HIGH | `capability_token.py` (HMAC-SHA256) vs `capability_authority.py` (Ed25519) | Two token issuers with incompatible signature schemes |
| HIGH | `audit_log.py` + `immutable_audit_log.py` vs `sovereign_audit_log.py` via `audit_manager.py` | Three audit write paths; kernel uses the lowest-tier one directly |
| MEDIUM | `cognition/adapters/policy_engine.py` vs `policy_registry.py` | Independent policy evaluation bypasses versioned registry |
| MEDIUM | `governance_service.py` vs `governance_manager.py` | Two orchestration modules; manager has zero callers |
| MEDIUM | `constitutional_ledger.py` vs `evidence_bundle.py` | Both record governance decisions independently |

---

## Risky Files (Do Not Touch Until Noted)

These files are safe to read but require a tested shim path before any behavioral change:

- `src/app/core/governance_kernel.py` — authority chain coordinator; direct audit write bypass must be fixed carefully
- `src/app/core/execution_router.py` — calls RuntimeEnforcer before ExecutionGate; change requires full execution contract tests
- `src/app/core/execution_gate.py` — final DENY authority; any change requires 118-test suite passing before and after
- `src/psia/canonical/capability_authority.py` — Ed25519 issuer; signature scheme changes are irreversible
- `src/app/governance/sovereign_audit_log.py` — cryptographic anchor; do not modify unless all 12-vector tests prove integrity maintained

---

## Files Not Safe to Touch Yet

| File | Reason |
|---|---|
| `src/app/governance/audit_log.py` | 3 production callers; must shim first, then migrate callers |
| `src/app/security/immutable_audit_log.py` | Only test callers; can shim in Phase 2 |
| `src/app/core/capability_token.py` | Wired to execution_gate Stage 6; signature migration requires transitional tests first |
| `src/app/governance/runtime_enforcer.py` | Wired before ExecutionGate in execution_router; must add EvidenceBundle path before moving |
| `src/app/core/constitutional_ledger.py` | Must align with EvidenceBundle schema before changing |

---

## Proposed Migration Order

### Phase 2 — Audit consolidation
1. `src/app/security/immutable_audit_log.py` → shim (no production callers)
2. `src/app/governance/audit_log.py` → shim (3 callers)
3. `src/app/health/report.py` → migrate to `audit_manager.py`
4. `src/app/cli.py` → migrate to `audit_manager.py`
5. `src/app/core/governance_kernel.py` → migrate to `audit_manager.py` (most critical; fix both `_approve` and `_reject`)
6. `src/app/core/constitutional_ledger.py` → attach `bundle_id` from `EvidenceBundle`

### Phase 3 — Capability consolidation
1. Wire `execution_gate.py` Stage 6 to accept `psia/schemas/capability.CapabilityToken` (Ed25519)
2. Add compatibility validation for legacy HMAC tokens (fail-closed)
3. Add transitional tests
4. Convert `capability_token.py` from issuer to compatibility wrapper

### Phase 4 — Enforcement consolidation
1. Read `execution_router.py` step 2.5 behavior
2. Move RuntimeEnforcer check inside ExecutionGate
3. Ensure every RuntimeEnforcer DENY produces EvidenceBundle
4. Write to audit_manager

### Phase 5 — Policy consolidation
1. Load `atlas/config/safety.yaml` into `PolicyRegistry` at startup
2. Load `.antigravity/security.yaml` into `PolicyRegistry` at startup
3. Wire `cognition/cerberus/engine.py` PolicyEngine to call `policy_decision.py`

---

## Phase 0 Acceptance Criteria

- [x] No source behavior changed
- [x] Baseline test status recorded: 118 passed, 0 failed
- [x] Caller map exists for all 16 target files
- [x] Migration order documented
- [x] Risky files identified
- [x] Files not safe to touch yet listed
