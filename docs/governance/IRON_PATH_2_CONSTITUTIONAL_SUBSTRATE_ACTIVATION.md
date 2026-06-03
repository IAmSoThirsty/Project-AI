# Iron Path 2.0 — Constitutional Substrate Activation

**Branch:** `substrate-consolidation`  
**HEAD SHA:** `e3913e6c9073f488ed2d82b1afeb039e1e46e616`  
**Analysis Date:** 2026-06-03  
**Analyst:** Iron Path 2.0 static analysis — read-only pass  
**Source Modified:** None  

---

## Sub-Report Index

| Report | File | Status |
|--------|------|--------|
| Phase 0 Baseline | [iron_path_2_phase_0_baseline.md](iron_path_2_phase_0_baseline.md) | Complete |
| Actual Execution Lifecycle | [iron_path_2_actual_execution_lifecycle.md](iron_path_2_actual_execution_lifecycle.md) | Complete |
| Receipts Convergence Map | [iron_path_2_receipts_convergence_map.md](iron_path_2_receipts_convergence_map.md) | Complete |
| Boot Order | [iron_path_2_boot_order.md](iron_path_2_boot_order.md) | Complete |
| Repair Plan | [iron_path_2_repair_plan.md](iron_path_2_repair_plan.md) | Complete |

---

## 1. Executive Status

| Substrate | Status |
|-----------|--------|
| ExecutionGate | PARTIALLY PROVEN — logic tested; EvidenceBundle not persisted; OctoReflex bypasses execution_router |
| EvidenceBundle | PARTIALLY PROVEN — logic tested; ring buffer only; no durable persistence |
| GovernanceKernel | PARTIALLY PROVEN — Triumvirate logic tested; kernel writes audit to lower tier (not AuditManager) |
| Governance/Triumvirate | PARTIALLY PROVEN — Four Laws + 3-council logic tested; decisions not persisted |
| StateRegister | PARTIALLY PROVEN — tested; silenced in execution_router (lines 58–59) |
| GenesisContinuityGuard | PARTIALLY PROVEN — 12-vector break suite passes; module has unstaged modifications |
| PSIA Invariants (9) | PARTIALLY PROVEN — logic tested; seal is string placeholder, not real Ed25519 signature |
| PolicyRegistry | PARTIALLY PROVEN — tested; default HMAC key is "dev-policy-secret" |
| CapabilityAuthority | PARTIALLY PROVEN — Ed25519 logic tested; zero production callers |
| SovereignAuditLog | PARTIALLY PROVEN — best-tested substrate; zero production callers via AuditManager in main path |

**No substrate is FULLY PROVEN.** The primary gaps across all substrates are: (1) persistence of proof artifacts, (2) wiring of tested components into the actual execution path, and (3) cryptographic seal completeness.

---

## 2. Core Constitutional Substrate Map

### 1. ExecutionGate

| Property | Value |
|----------|-------|
| Role | Final ALLOW/DENY/HALT decision point for all governed actions |
| Authority Level | HIGHEST — only module that may produce a final outcome |
| Enforcement Role | 9-stage gate; stage 0 = Triumvirate; stage 9 = EvidenceBundle production |
| Source File | `src/app/core/execution_gate.py` (387 lines) |
| Callers | `execution_router.py` (primary), `octoreflex.py` (direct — bypasses execution_router wrapper) |
| Receipts | `tests/test_execution_gate_enforcement.py`, `tests/test_governance_contract.py` |
| Missing Receipts | No persistent EvidenceBundle store; no proof that Stage 9 bundles survive restart |
| Activation Status | ACTIVE — but OctoReflex direct caller bypasses waterfall/RuntimeEnforcer/StateRegister pre-checks |

### 2. EvidenceBundle

| Property | Value |
|----------|-------|
| Role | Canonical proof-carrying artifact for every governed action |
| Authority Level | Proof layer — not decision-making; documents decisions |
| Enforcement Role | EvidenceBundleWriter builds bundles; EvidenceBundleValidator checks structure |
| Source File | `src/app/core/evidence_bundle.py` (287 lines) |
| Callers | `execution_gate.py` (Stage 9 only) |
| Receipts | `tests/test_evidence_bundle.py` (11), `tests/test_governance_contract.py` |
| Missing Receipts | No durable persistence; ring buffer max 10,000; no receipt proving bundles written to disk or AuditManager |
| Activation Status | ACTIVE — but bundles are ephemeral |

### 3. GovernanceKernel

| Property | Value |
|----------|-------|
| Role | Two-layer Triumvirate evaluator; authority chain validator; default-approve semantics |
| Authority Level | HIGH — first substantive gate inside ExecutionGate |
| Enforcement Role | Rule-based Triumvirate + ML Triumvirate; event spine publication; constitutional ledger attestation |
| Source File | `src/app/core/governance_kernel.py` (219 lines) |
| Callers | `execution_gate.py` (Stage 0 only) |
| Receipts | Covered via `tests/test_governance_contract.py` |
| Missing Receipts | Writes to `AuditLog()` directly — no sovereign audit chain receipt for kernel decisions; ML Triumvirate swallows all exceptions silently |
| Activation Status | ACTIVE — audit path bypasses sovereign tier |

### 4. Governance / Triumvirate

| Property | Value |
|----------|-------|
| Role | Four Laws enforcement + 3-council votes (Galahad/Cerberus/Codex) |
| Authority Level | HIGH — unanimous consent required for approval |
| Enforcement Role | `_four_laws_check()` blocks on constitutional violations; council votes produce final GovernanceDecision |
| Source File | `src/app/core/governance.py` (671 lines) |
| Callers | `governance_kernel.py` |
| Receipts | `tests/test_four_laws_*.py` (1000-scenario + Hypothesis), `canonical/invariants.py::TriumvirateConsensusInvariant` |
| Missing Receipts | `_log_decision()` writes to in-memory list only — no durable receipt for every Triumvirate decision |
| Activation Status | ACTIVE — decisions not persisted |

### 5. StateRegister

| Property | Value |
|----------|-------|
| Role | Temporal continuity tracker; predecessor hash chain; anti-branching (StateBranchingProtector) |
| Authority Level | MEDIUM — informs execution context; does not make ALLOW/DENY decisions |
| Enforcement Role | Detects state-jumping attacks; injects temporal context for anti-gaslighting |
| Source File | `src/app/core/state_register.py` (687 lines) |
| Callers | `execution_router.py` (silenced), `advanced_boot.py`, `genesis_reanchor.py`, `validate_constitution.py` |
| Receipts | `tests/test_state_register_continuity_hash.py`, `tests/test_state_branching.py` |
| Missing Receipts | Silenced in `execution_router.py` lines 58–59 — no receipt that temporal context actually reaches ExecutionGate during runtime |
| Activation Status | ACTIVE in boot/validation utilities — SILENCEABLE in primary execution path |

### 6. GenesisContinuityGuard

| Property | Value |
|----------|-------|
| Role | Pins genesis identity per process; detects VECTOR 1 (genesis replacement) and VECTOR 11 |
| Authority Level | HIGH — FATAL exception on genesis discontinuity |
| Enforcement Role | `check_or_pin()` called at SovereignAuditLog init; `is_system_compromised()` boolean |
| Source File | `src/app/governance/genesis_continuity.py` (192 lines) — **MODIFIED/UNSTAGED** |
| Callers | `sovereign_audit_log.py` (module-level import) |
| Receipts | `tests/test_12_vector_constitutional_break.py` (11 vectors), `tests/test_phase_c1_governance_wiring.py` |
| Missing Receipts | Module has uncommitted changes — last passing tests may not reflect current code |
| Activation Status | ACTIVE — **but unstaged changes require review before implementation proceeds** |

### 7. PSIA Invariants (INV-ROOT-1 through INV-ROOT-9)

| Property | Value |
|----------|-------|
| Role | Constitutional declarations: authentication, authorization, ledger, key expiry, self-issuance, scope bounds, quorum, DID, ledger uniqueness |
| Authority Level | HIGH — FATAL+HARD_DENY+IMMUTABLE; checked by invariant_engine at Step 4 of execution_router |
| Enforcement Role | Loaded by `invariant_engine.py`; validated against context on every execution |
| Source File | `src/psia/invariants.py` (124 lines) |
| Callers | `src/app/core/invariant_engine.py`, `canonical/sovereign_proof.py` |
| Receipts | `tests/test_psia_invariants.py`, `tests/test_formal_properties.py` (7 Hypothesis theorems) |
| Missing Receipts | `sig="governance-sealed"` is a string literal — invariant seal is NOT cryptographically verifiable |
| Activation Status | ACTIVE — seal is narrative, not proof |

### 8. PolicyRegistry

| Property | Value |
|----------|-------|
| Role | Canonical policy authority; versioned, HMAC-signed policy store |
| Authority Level | MEDIUM — consulted at ExecutionGate Stage 2 via PolicyDecision |
| Enforcement Role | `is_action_permitted()` returns allow/deny; detects governance weakening |
| Source File | `src/app/core/policy_registry.py` (237 lines) |
| Callers | `evidence_bundle.py` (lazy), `policy_decision.py` (lazy), `execution_authorization.py` |
| Receipts | `tests/test_policy_registry.py`, `tests/test_policy_guard.py` |
| Missing Receipts | Default `POLICY_REGISTRY_SECRET="dev-policy-secret"` — HMAC receipts with this key are cryptographically invalid |
| Activation Status | ACTIVE — secret integrity unverified in non-production |

### 9. CapabilityAuthority

| Property | Value |
|----------|-------|
| Role | Canonical Ed25519 token issuer; issue/revoke/rotate lifecycle; guards INV-ROOT-5 and INV-ROOT-6 |
| Authority Level | HIGH (intended) — but zero production callers means it is currently inactive |
| Enforcement Role | `issue()` produces Ed25519-signed CapabilityToken; `is_valid()` + `is_revoked()` for verification |
| Source File | `src/psia/canonical/capability_authority.py` (172 lines) |
| Callers | Test files only — no `src/` callers |
| Receipts | `tests/test_psia_canonical.py`, `tests/test_ed25519_crypto.py`, `tests/test_psia_comprehensive.py` |
| Missing Receipts | No production execution path exercises CapabilityAuthority; ExecutionGate Stage 6 uses `capability_token.py` (HMAC) instead |
| Activation Status | TESTED IN ISOLATION — NOT WIRED into production path |

### 10. SovereignAuditLog

| Property | Value |
|----------|-------|
| Role | Full constitutional-grade audit: Ed25519 per-entry signing, HMAC key rotation, Merkle batching, TSA timestamping, genesis continuity |
| Authority Level | HIGH — the intended final cryptographic audit authority |
| Enforcement Role | `log_event()` → sign → hash chain → Merkle → optional TSA anchor; `generate_proof_bundle()` for legal admissibility |
| Source File | `src/app/governance/sovereign_audit_log.py` (561 lines) |
| Callers | `audit_manager.py` (sole caller in `src/`) — but AuditManager itself has only 1 production caller: `shadow_execution_plane.py` |
| Receipts | Best-tested substrate: 12-vector break suite, TSA integration, RFC3161, immutable log, external Merkle anchor tests |
| Missing Receipts | No production caller chain from main execution path; sovereign audit log receives no records during normal system operation |
| Activation Status | ACTIVE as an isolated substrate — NOT CONNECTED to the main execution path |

---

## 3. Actual vs Intended Execution Lifecycle

### Intended (per mission spec)

```
pipeline.py → governance_kernel → execution_gate
  → evidence_bundle [pre-exec proof]
  → audit_manager → sovereign_audit_log
  → iron_path_executor
  → execution_result
  → evidence_bundle [post-exec proof]
  → audit_manager → sovereign_audit_log
```

### Actual (discovered by static analysis)

**Primary path:**
```
execution_router.execute()                        [10 domain modules + cognition_kernel call this]
  [1] waterfall_filter.filter()                   HARD
  [2] liara_ttl_check()                           HARD
  [2.5] runtime_enforcer.enforce()                SILENCEABLE ← lines 50–51
  [3] state_register.get_temporal_context()       SILENCEABLE ← lines 58–59
  [3.5] TrustScoring + AdversarialPattern         SILENCEABLE ← lines 74–75
  [4] invariant_engine.validate()                 HARD
  [5] execution_gate.execute()                    HARD GATE
        Stage 0: governance_kernel.evaluate_action()
          [rule Triumvirate + ML Triumvirate]
          → constitutional_ledger.attest()
          → AuditLog().log_event()                ← BYPASS: not AuditManager
        Stage 1–8: policy, authorization, mutation, capability, invariants
        → executor_fn()
        Stage 9: evidence_bundle [in-memory ring buffer, NOT AuditManager]
  [6] nirl_forge                                  NON-FATAL
```

**Parallel path (bypasses execution_router entirely):**
```
runtime/router.py → pipeline.py::enforce_pipeline()
  Phase 3: iron_path_executor.bind_mutation()     ← DIRECT, bypasses ExecutionGate
```

**OctoReflex path (bypasses execution_router wrapper):**
```
octoreflex.py → execution_gate.execute()          ← DIRECT, bypasses steps 2.5/3/3.5
```

### Delta Summary

| Point | Intended | Actual |
|-------|----------|--------|
| Entry point | `pipeline.py` | `execution_router.py` (or octoreflex.py / runtime/router.py) |
| Audit path | `audit_manager → sovereign_audit_log` | `AuditLog()` directly from kernel |
| Evidence persistence | Durable | In-memory ring buffer only |
| Token authority | `capability_authority.py` (Ed25519) | `capability_token.py` (HMAC) |
| Triumvirate record | Persisted | In-memory list only |
| RuntimeEnforcer | Hard gate | Silenceable |
| pipeline.py → ExecutionGate | Through gate | Direct to IronPathExecutor (Phase 3 of pipeline) |

---

## 4. Authority Path Map

### Execution Authority

```
execution_router.execute()
  └─ execution_gate.execute()  [SOLE FINAL AUTHORITY — not bypassed by exception]
       └─ governance_kernel.evaluate_action()  [Triumvirate gate]
```

**Fragmentation:** `pipeline.py::enforce_pipeline()` Phase 3 calls `iron_path_executor.bind_mutation()` directly — a parallel execution authority path that bypasses ExecutionGate.

**Fragmentation:** `octoreflex.py` calls `execution_gate` directly without going through `execution_router` — skips waterfall/liara/runtime_enforcer/state_register/trust scoring.

### Audit Authority

```
INTENDED:
execution_gate → audit_manager → sovereign_audit_log

ACTUAL:
governance_kernel → AuditLog() [non-sovereign, non-cryptographic]
execution_gate Stage 9 → evidence_bundle [in-memory ring buffer]
shadow_execution_plane → audit_manager → sovereign_audit_log [shadow plane only]
```

**Fragmentation:** 3 separate audit write paths. None of them converge to SovereignAuditLog in the main execution flow.

### Capability / Token Authority

```
INTENDED:
capability_authority.py [Ed25519, psia/canonical]
  └─ ExecutionGate Stage 6

ACTUAL:
capability_token.py [HMAC-SHA256, dev default secret]
  └─ ExecutionGate Stage 6

capability_authority.py [Ed25519]
  └─ [no production callers — test files only]
```

**Fragmentation:** Two independent token issuers with incompatible signature schemes. Neither delegates to the other.

### Policy Authority

```
policy_registry.py [HMAC-signed, versioned]
  └─ policy_decision.py [lazy import]
       └─ ExecutionGate Stage 2

governance_manager.py [proposal/vote/execute lifecycle]
  └─ [FULLY STUBBED — no callers — no production enforcement]
```

**Fragmentation:** `governance_manager.py` declares a policy governance lifecycle but is not wired to `policy_registry.py`. Policy changes cannot go through a governed proposal/vote process as designed.

### Continuity Authority

```
genesis_continuity.py [process-level pin]
  └─ sovereign_audit_log.py [loaded at init]

state_register.py [session-level hash chain]
  └─ execution_router.py [SILENCEABLE — lines 58–59]
```

### Replay Authority

```
canonical/replay.py [scenario trace validation — 5 invariants]
  └─ canonical/execution_trace.json [overwritten each run]

src/app/core/deterministic_replay.py [deterministic replay tool]
  └─ [NOT WIRED — no callers — no tests]
```

**Fragmentation:** Two replay systems with no shared receipt format. `canonical/replay.py` validates a pre-built scenario trace. `deterministic_replay.py` has no callers and no tests.

### Legal / Admissibility Authority

```
acceptance_ledger.py [SQLite + Ed25519 + RFC3161]
  └─ runtime_enforcer.py [imported at top]
       └─ execution_router.py [SILENCEABLE — lines 50–51]

sovereign_audit_log.py [Ed25519 + TSA + Merkle + RFC3161]
  └─ audit_manager.py [sovereign_mode=False default]
       └─ shadow_execution_plane.py [not on main path]
```

**Fragmentation:** Legal admissibility infrastructure exists and is tested in isolation. It is not reachable from the main execution path under normal operating conditions.

---

## 5. Receipts Map (Summary)

Full receipts map is in [iron_path_2_receipts_convergence_map.md](iron_path_2_receipts_convergence_map.md).

| Substrate | Receipt Class | Key Receipt | Key Gap |
|-----------|--------------|-------------|---------|
| ExecutionGate | PARTIAL | `test_execution_gate_enforcement.py` | EvidenceBundle not persisted |
| EvidenceBundle | PARTIAL | `test_evidence_bundle.py` (11) | No durable store |
| GovernanceKernel | PARTIAL | `test_governance_contract.py` (23) | Audit writes to lower tier |
| Governance/Triumvirate | PARTIAL | 1000-scenario + Hypothesis tests | Decisions in-memory only |
| StateRegister | PARTIAL | `test_state_register_continuity_hash.py` | Silenced in execution path |
| GenesisContinuityGuard | PARTIAL | 12-vector break suite | Unstaged modifications |
| PSIA Invariants | CONTRADICTORY | `test_psia_invariants.py` | Seal is string literal, not Ed25519 |
| PolicyRegistry | PARTIAL | `test_policy_registry.py` | Dev secret default |
| CapabilityAuthority | PARTIAL | `test_psia_canonical.py` | Zero production callers |
| SovereignAuditLog | PARTIAL | 12-vector break suite, TSA, Merkle | Zero production callers via main path |
| AcceptanceLedger | MISSING | None | No dedicated test file |
| GovernanceManager | NARRATIVE | None | Fully stubbed |
| DeterministicReplay | MISSING | None | No test file; not wired |
| RuntimeEnforcer | CONTRADICTORY | `test_governance_pipeline_regressions.py` | "Zero bypass" claim false |

---

## 6. Missing Proof Map

Claims that lack machine-verifiable receipts:

| Claimed Capability | Where Claimed | Why Not Proven |
|-------------------|---------------|----------------|
| "Sovereign audit trail is active for all governed actions" | Architecture docs, CONSTITUTIONAL_AUDIT.md | AuditManager has zero callers in main execution path |
| "Zero bypass" (RuntimeEnforcer) | `runtime_enforcer.py` docstring | `execution_router.py:50–51` silences it |
| "PSIA invariants are Ed25519-signed by genesis root key" | `psia/invariants.py:14` | `sig="governance-sealed"` is a string literal |
| "All capability tokens are issued by canonical authority" | Mission spec | `capability_token.py` (HMAC) is active; `capability_authority.py` (Ed25519) is unused |
| "Every governed action produces pre/post EvidenceBundle in durable store" | Evidence bundle docstring | Ring buffer only; not persisted |
| "GovernanceManager governs policy changes" | `governance_manager.py` docstring | Fully stubbed; no callers |
| "production ready" | `PROJECT-COMPLETE.md` (untracked), `OPTION-*-COMPLETION-REPORT.txt` (untracked) | No substrate has a complete durable receipts chain in the production execution path |
| "Deterministic replay available for all governance decisions" | Mission spec | `deterministic_replay.py` is not wired; `canonical/replay.py` replays a scenario, not live decisions |

---

## 7. Boot Order (Summary)

Full boot order is in [iron_path_2_boot_order.md](iron_path_2_boot_order.md).

```
Tier 0: genesis_continuity, policy_registry, psia_invariants,
        capability_authority, evidence_bundle, iron_path_executor

Tier 1: constitutional_ledger, acceptance_ledger, governance/Triumvirate,
        state_register, capability_token

Tier 2: sovereign_audit_log, governance_kernel, runtime_enforcer, policy_decision

Tier 3: audit_manager, execution_gate

Tier 4: execution_router

Tier 5: domain modules, pipeline/runtime-router, cognition_kernel
```

**Critical ordering constraint:** `genesis_continuity` MUST boot before `sovereign_audit_log` (hard import). `data/legal/` directory MUST exist before `acceptance_ledger` boots, or RuntimeEnforcer init fails and is silently bypassed in execution_router.

---

## 8. Repair Plan (Summary)

Full repair plan is in [iron_path_2_repair_plan.md](iron_path_2_repair_plan.md).

| Phase | Tasks | Type | Earliest Start |
|-------|-------|------|----------------|
| Phase 1 — Annotations | 3 tasks | No behavior change | Immediately |
| Phase 2 — Wiring | 3 tasks | Connect existing infra | After Phase 1 |
| Phase 3 — Harden | 3 tasks | Close bypass windows | After Phase 2 |
| Phase 4 — Seal | 3 tasks | Cryptographic completeness | After Phase 3 |
| Phase 5 — Verify | 4 tasks | Receipt completeness | After Phase 4 |

---

## 9. Stop Conditions

The following stop conditions from the mission spec are currently **ACTIVE** (they block implementation):

| # | Stop Condition | Evidence |
|---|----------------|----------|
| S-1 | Any audit write bypasses audit_manager.py without justification | `governance_kernel.py` → `AuditLog()` directly |
| S-2 | Any old token issuer remains active without compatibility-only constraints | `capability_token.py` active with no compatibility annotation |
| S-3 | Any code path executes without canonical lifecycle | `GovernanceService._auto_approve()` produces no EvidenceBundle |
| S-4 | Any test artifact contradicts documentation | `runtime_enforcer.py` "Zero bypass" vs `execution_router.py:50–51` |
| S-5 | Core substrate with uncommitted modifications | `genesis_continuity.py` has unstaged changes |

The following stop conditions are **NOT triggered**:

| Stop Condition | Status |
|----------------|--------|
| ExecutionGate behavior ambiguous | NOT triggered — 9 stages, unambiguous ALLOW/DENY/HALT/ESCALATE |
| DENY path fails to produce EvidenceBundle | NOT triggered — Stage 9 covers all exit paths including DENY |
| HALT path fails to produce EvidenceBundle | NOT triggered |
| Schema change required before receipts complete | NOT triggered |
| Caller map incomplete | NOT triggered |

---

## 10. Final Recommendation

### May implementation proceed?

**Conditionally yes — Phase 1 only.**

Phase 1 (annotations, no behavior change) may proceed immediately. It has zero risk, produces no functional changes, and establishes the written record of known gaps required by the Iron Path standard before any implementation work begins.

**Phases 2–5 must not begin** until:

1. `src/app/governance/genesis_continuity.py` unstaged changes are committed, tested, and verified. This is a core substrate with uncommitted modifications. Any implementation that touches related code while this file is unstaged introduces uncontrolled state.

2. The active stop conditions S-1 through S-4 above are formally acknowledged and scoped. Each stop condition requires either a plan to fix it (already provided in the Repair Plan) or an explicit accepted-risk annotation approved by the project owner.

3. The test baseline is re-verified on the current working tree. The last recorded baseline (118 passed, 0 failed) is 30 days old. `tests/conftest.py` has been modified. Re-run before trusting the baseline.

### Which repair phase goes first?

**Phase 1, then Phase 2.1 (AuditManager wiring), then Phase 3.1 (silent bypass hardening).**

This ordering addresses the highest-risk findings first without requiring new infrastructure. All three phases use existing, tested substrates — they are wiring and annotation work, not new code.

### Which files are unsafe to touch?

| File | Reason |
|------|--------|
| `src/app/governance/genesis_continuity.py` | Unstaged modifications; core substrate |
| `src/psia/invariants.py` | Changing the seal without a working Ed25519 keypair registration will break invariant_engine |
| `canonical/replay.py` | Unconditionally writes `execution_trace.json`; do not run in analysis-only mode |
| `src/app/core/governance/pipeline.py` | 1,611 lines; caller migration for rollback stub requires full pipeline understanding |
| `src/psia/crypto/threshold.py` | Unstaged modifications |

### Which authority paths are currently fragmented?

1. **Audit authority** — 3 write paths (AuditLog direct, EvidenceBundle ring buffer, SovereignAuditLog via shadow plane only). None converge.

2. **Token / capability authority** — 2 independent issuers (HMAC CapabilityToken, Ed25519 CapabilityAuthority). Neither delegates to the other.

3. **Execution authority** — 3 entry paths (execution_router, pipeline.py via runtime/router, OctoReflex direct). Only execution_router passes through all pre-gate checks; pipeline.py bypasses ExecutionGate; OctoReflex bypasses execution_router wrapper.

4. **Policy authority** — PolicyRegistry enforces via ExecutionGate Stage 2; GovernanceManager (proposal/vote lifecycle) is fully stubbed and not connected to PolicyRegistry.

5. **Replay authority** — canonical/replay.py (scenario-level) and deterministic_replay.py (not wired) are disconnected.

### Final Statement

> This system has a correctly designed constitutional governance architecture with real, tested components. The substrate modules exist and function correctly in isolation. The governance enforcement infrastructure (SovereignAuditLog, CapabilityAuthority, AuditManager, GenesisContinuityGuard) is among the better-tested infrastructure in the codebase.
>
> The current gaps are wiring gaps, not design gaps. The right components exist but are not connected to the execution path that processes real requests.
>
> **This system is not production-ready.** The sovereign audit trail is not active. The canonical token authority is not wired. Three enforcement gates are silenceable by exception. The policy governance lifecycle is stubbed. The claim that this system provides constitutional-grade auditability of every governed action is not supported by the evidence.
>
> Implementation may proceed — one phase at a time, receipt before next phase, no big-bang migration, no deletion before caller migration.

---

*Iron Path 2.0 analysis complete. Receipts over claims. Deterministic over narrative.*
