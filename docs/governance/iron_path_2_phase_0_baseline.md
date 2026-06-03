# Iron Path 2.0 — Phase 0: Freeze, Baseline, and Caller Map

**Generated:** 2026-06-03  
**Branch:** `substrate-consolidation`  
**HEAD SHA:** `e3913e6c9073f488ed2d82b1afeb039e1e46e616`  
**Status:** READ-ONLY ANALYSIS — no source behavior changed  
**Analyst:** Iron Path 2.0 static analysis pass

---

## 1. Git Freeze

| Property | Value |
|----------|-------|
| Branch | `substrate-consolidation` |
| HEAD SHA | `e3913e6c9073f488ed2d82b1afeb039e1e46e616` |
| Commit message | `galahad/charter.html: add two-invariant-set distinction section` |
| Analysis date | 2026-06-03 |

### Recent commits (last 5)

```
e3913e6c galahad/charter.html: add two-invariant-set distinction section
8b6790eb Proof Portal makeover — institutional rebuild of all 20 Project-AI library pages
71312ece feat(web): build Project-AI walk-in library — 20 pages across 3 governance wings
a3fb7ec1 Fix LFS check hook crash on transiently-deleted files
cc70ec81 Fix 15 pre-existing test failures and deprecation warnings
```

### Dirty/Untracked Files at Freeze

The working tree is not clean. The following files have uncommitted changes as of the freeze point.

**Modified (M) — tracked, changed but not staged:**

| File | Note |
|------|------|
| `.github/copilot-instructions.md` | Governance instructions |
| `.github/instructions/GOVERNANCE_INSTRUCTIONS_INDEX.md` | Instructions index |
| `.github/instructions/refactor-engineer.agent.md` | Agent instructions |
| `.gitignore` | Ignore rules |
| `AGENTS.md` | Agent manifest |
| `Dockerfile` | Container definition |
| `Project-Ai/.obsidian/*.json` | Vault settings |
| `Project-Ai/Welcome.md` | Vault welcome |
| `README.md` | Project readme |
| `docker-compose.yml`, `docker-compose.override.yml` | Deployment |
| `docs/reports/ROOT_CLEANUP_KNOWN_PROBLEMS.md` | Known problems doc |
| `pyproject.toml`, `requirements.txt` | Python project metadata |
| `src/app/governance/genesis_continuity.py` | **CORE SUBSTRATE** — modified |
| `src/psia/crypto/threshold.py` | PSIA threshold crypto |
| `tests/conftest.py` | Test configuration |
| `web/site/projects/project-ai/**/*.html` | Web library (22 HTML files) |

**Added (A) — staged, not yet committed:**

| File | Note |
|------|------|
| `docs/governance/substrate_consolidation_phase_0.md` | Phase 0 baseline from prior session |

**Deleted (D) — removed from index:**

| File | Note |
|------|------|
| `.github/instructions/obsidian-vault-write-boundary.instructions.md` | Vault boundary instructions deleted |

**Untracked (??) — new files not yet tracked:**

Notable untracked files include: `DOCKER-DEPLOYMENT-GUIDE.md`, `IMAGE-VERSIONING-STRATEGY.md`, `OPERATIONS-RUNBOOK.md`, `OPTION-A-COMPLETION-REPORT.txt`, `OPTION-B-COMPLETION-REPORT.md`, `PROJECT-COMPLETE.md`, `config/prometheus.yml`, `config/alertmanager.yml`, `config/grafana-*.yml`, `.github/workflows/cicd.yml`, `Project_ai_index/`.

> **CRITICAL NOTE:** `src/app/governance/genesis_continuity.py` (a core substrate module) has uncommitted modifications. Its current on-disk state differs from the last committed state. This baseline reflects the working-tree version, not the HEAD version. This module must not be considered stable until the change is committed and tested.

---

## 2. Substrate Inventory

### 2A. Core Constitutional Substrate Modules (10)

| # | Module | Path | Lines | Role | Status |
|---|--------|------|-------|------|--------|
| 1 | ExecutionGate | `src/app/core/execution_gate.py` | 387 | Final ALLOW/DENY/HALT authority | Active |
| 2 | EvidenceBundle | `src/app/core/evidence_bundle.py` | 287 | Canonical proof artifact producer | Active |
| 3 | GovernanceKernel | `src/app/core/governance_kernel.py` | 219 | Two-layer Triumvirate evaluator | Active |
| 4 | Governance/Triumvirate | `src/app/core/governance.py` | 671 | Four Laws + 3-council votes | Active |
| 5 | StateRegister | `src/app/core/state_register.py` | 687 | Temporal continuity + anti-branching | Active |
| 6 | GenesisContinuityGuard | `src/app/governance/genesis_continuity.py` | 192 | Genesis identity pinning, VECTOR 1/11 | Active — MODIFIED |
| 7 | PSIA Invariants | `src/psia/invariants.py` | 124 | 9 INV-ROOT-* declarations (FATAL/HARD_DENY) | Active — SEAL GAP |
| 8 | PolicyRegistry | `src/app/core/policy_registry.py` | 237 | Versioned, HMAC-signed policy authority | Active — DEV SECRET |
| 9 | CapabilityAuthority | `src/psia/canonical/capability_authority.py` | 172 | Ed25519 token issuer/revoker | Active — NOT WIRED |
| 10 | SovereignAuditLog | `src/app/governance/sovereign_audit_log.py` | 561 | Cryptographic audit log (Ed25519+Merkle+TSA) | Active — NO PRODUCTION CALLERS |

### 2B. Supporting Interface/Entry Modules (11)

| Module | Path | Lines | Role | Status |
|--------|------|-------|------|--------|
| pipeline.py | `src/app/core/governance/pipeline.py` | 1,611 | 6-phase governance pipeline | Active — rollback TODO |
| IronPathExecutor | `src/app/core/governance/iron_path_executor.py` | 938 | Mutation binding + decision log | Active |
| AuditManager | `src/app/governance/audit_manager.py` | 136 | Sovereign audit facade | Active — DEFAULT NON-SOVEREIGN |
| PolicyDecision | `src/app/core/policy_decision.py` | 107 | Policy evaluation result DTO | Active |
| RuntimeEnforcer | `src/app/governance/runtime_enforcer.py` | 453 | PAGL + tier enforcement | Active — SILENCEABLE |
| CapabilitySchema | `src/psia/schemas/capability.py` | 66 | Canonical capability token schema | Active |
| CapabilityToken (app) | `src/app/core/capability_token.py` | 202 | HMAC-SHA256 token service | Active — DEV SECRET / DUAL AUTHORITY |
| GovernanceService | `src/app/core/services/governance_service.py` | 467 | Governance evaluation service | Active — AUTO-APPROVE GAP |
| GovernanceManager | `src/app/governance/governance_manager.py` | 333 | Proposal/vote lifecycle | FULLY STUBBED |
| ExecutionRouter | `src/app/core/execution_router.py` | 113 | "The ONLY legal execution path" | Active — 3 SILENT BYPASSES |
| ConstitutionalLedger | `src/app/core/constitutional_ledger.py` | 172 | JSONL append-only ledger | Active — NO BUNDLE_ID LINK |

### 2C. Additional Substrate Files

| File | Lines | Role | Status |
|------|-------|------|--------|
| `src/app/governance/acceptance_ledger.py` | 663 | RFC3161 + Ed25519 + SQLite acceptance log | Active — NO DEDICATED TESTS |
| `src/app/core/deterministic_replay.py` | 415 | Deterministic replay tool | Active — NOT WIRED |
| `src/app/governance/external_merkle_anchor.py` | 621 | Filesystem/IPFS/S3 Merkle anchor | Active — tested |
| `canonical/replay.py` | 672 | Canonical governance replay (CI receipt) | Active — writes execution_trace.json |
| `canonical/invariants.py` | 554 | 5 canonical behavioral invariants | Active — CI gate |
| `src/psia/invariants.py` | 124 | 9 PSIA constitutional invariants | Active — placeholder sig |

---

## 3. Caller / Import Map

For each core module: who imports it, how, and at what level.

### 3.1 ExecutionGate (`src/app/core/execution_gate.py`)

| Caller File | Import Type | Notes |
|-------------|-------------|-------|
| `src/app/core/execution_router.py` | Module-level import | Primary intended caller — `get_execution_gate()` |
| `src/app/core/octoreflex.py` | Module-level import | **DIRECT CALLER** — bypasses execution_router |
| `src/app/core/execution_gate.py` | Self (internal) | — |

> ExecutionGate is called directly by `octoreflex.py`, bypassing the `execution_router.execute()` wrapper. This means the waterfall/liara/runtime_enforcer/state_register/trust_scoring steps in execution_router are skipped when OctoReflex calls the gate directly.

### 3.2 EvidenceBundle (`src/app/core/evidence_bundle.py`)

| Caller File | Import Type | Notes |
|-------------|-------------|-------|
| `src/app/core/execution_gate.py` | Lazy import (Stage 9) | Produces pre/post bundles on every gate exit |
| `src/app/core/evidence_bundle.py` | Self (internal) | — |

> EvidenceBundle has only 2 Python callers in `src/`. The ring buffer (`_EVIDENCE_STORE`) is populated by ExecutionGate only. Nothing outside `execution_gate.py` calls `EvidenceBundleWriter` in the production path.

### 3.3 GovernanceKernel (`src/app/core/governance_kernel.py`)

| Caller File | Import Type | Notes |
|-------------|-------------|-------|
| `src/app/core/execution_gate.py` | Module-level import | `get_kernel()` at init; `kernel.evaluate_action()` at Stage 0 |

> GovernanceKernel has exactly 1 production caller: ExecutionGate.

### 3.4 Governance/Triumvirate (`src/app/core/governance.py`)

| Caller File | Import Type | Notes |
|-------------|-------------|-------|
| `src/app/core/governance_kernel.py` | Module-level import | `GovernanceContext`, `Triumvirate` used in evaluate_action() |
| `src/app/core/execution_gate.py` | Module-level import (via kernel) | Indirect |

> The Triumvirate is used only through GovernanceKernel. `governance.py` itself has no outbound calls — it is self-contained.

### 3.5 StateRegister (`src/app/core/state_register.py`)

| Caller File | Import Type | Notes |
|-------------|-------------|-------|
| `src/app/core/execution_router.py` | Module-level import | `get_state_register().get_temporal_context()` — SILENCEABLE |
| `src/app/core/validate_constitution.py` | Import | Constitutional validation |
| `src/app/core/genesis_reanchor.py` | Import | Re-anchoring tool |
| `src/app/core/constitutional_model.py` | Import | Constitutional model |
| `src/app/core/advanced_boot.py` | Import | Boot sequence |

> StateRegister is imported by 5 files but silenced in execution_router (lines 54–59, `except Exception: pass`). The other callers are utility/boot modules, not runtime execution paths.

### 3.6 GenesisContinuityGuard (`src/app/governance/genesis_continuity.py`)

| Caller File | Import Type | Notes |
|-------------|-------------|-------|
| `src/app/governance/sovereign_audit_log.py` | Module-level import | `check_or_pin()` called at SovereignAuditLog init |
| Self-contained | — | No other production callers identified |

> **WARNING:** This module has uncommitted modifications on the current branch. The on-disk state differs from HEAD.

### 3.7 PSIA Invariants (`src/psia/invariants.py`)

| Caller File | Import Type | Notes |
|-------------|-------------|-------|
| `src/app/core/invariant_engine.py` | Import | Loads `ROOT_INVARIANTS` dict |
| `canonical/sovereign_proof.py` | Import | Sovereign proof runner |

### 3.8 PolicyRegistry (`src/app/core/policy_registry.py`)

| Caller File | Import Type | Notes |
|-------------|-------------|-------|
| `src/app/core/evidence_bundle.py` | Lazy import | Auto-populates `policy_version`/`policy_hash` fields |
| `src/app/core/policy_decision.py` | Lazy import | `get_policy_registry()` in `evaluate()` |
| `src/app/core/execution_authorization.py` | Import | Authorization uses policy registry |
| `src/app/core/policy_registry.py` | Self | — |

### 3.9 CapabilityAuthority (`src/psia/canonical/capability_authority.py`)

| Caller File | Import Type | Notes |
|-------------|-------------|-------|
| `tests/test_psia_canonical.py` | Test import | Test-only; no production caller in `src/` |
| `tests/test_psia_comprehensive.py` | Test import | Test-only |

> **CapabilityAuthority has zero production callers in `src/`.** It is a real, complete Ed25519 token authority that is not wired into the execution path. ExecutionGate Stage 6 calls `CapabilityTokenService` (HMAC-SHA256, `src/app/core/capability_token.py`) instead.

### 3.10 SovereignAuditLog (`src/app/governance/sovereign_audit_log.py`)

| Caller File | Import Type | Notes |
|-------------|-------------|-------|
| `src/app/governance/audit_manager.py` | Module-level import | Instantiated inside `AuditManager.__init__` when `sovereign_mode=True` |

> **SovereignAuditLog has exactly 1 Python caller in `src/`: AuditManager.** And AuditManager itself has exactly 1 production caller: `src/app/core/shadow_execution_plane.py`. The main execution path (execution_gate → governance_kernel) does NOT reach SovereignAuditLog.

### AuditManager — Direct Callers

| Caller File | Import Type | Notes |
|-------------|-------------|-------|
| `src/app/governance/audit_manager.py` | Self | — |
| `src/app/core/shadow_execution_plane.py` | Import | Shadow plane only |

> **AuditManager is not used in the primary governance execution path.** governance_kernel.py calls `app.governance.audit_log.AuditLog().log_event()` directly — a lower-tier, non-sovereign logging path.

### ExecutionRouter — Direct Callers (10 domain modules + cognition_kernel)

`src/app/core/execution_router.execute()` is called by:

| Caller | Notes |
|--------|-------|
| `src/app/domains/agi_safeguards.py` | Domain module |
| `src/app/domains/biomedical_defense.py` | Domain module |
| `src/app/domains/command_control.py` | Domain module |
| `src/app/domains/continuous_improvement.py` | Domain module |
| `src/app/domains/deep_expansion.py` | Domain module |
| `src/app/domains/ethics_governance.py` | Domain module |
| `src/app/domains/situational_awareness.py` | Domain module |
| `src/app/domains/survivor_support.py` | Domain module |
| `src/app/domains/supply_logistics.py` | Domain module |
| `src/app/domains/tactical_edge_ai.py` | Domain module |
| `src/app/core/cognition_kernel.py` | Core kernel — also calls governance directly |

---

## 4. Test Baseline

From `docs/governance/substrate_consolidation_phase_0.md` (last recorded passing baseline):

| Metric | Value |
|--------|-------|
| Tests passed | 118 |
| Tests failed | 0 |
| Date recorded | 2026-05-04 |
| Run command | `PYTHONPATH=src py -3.12 -m pytest tests/ -x` |

> This baseline is 30 days old. The current working tree has uncommitted changes including modifications to `src/app/governance/genesis_continuity.py` and `tests/conftest.py`. The test baseline should be re-verified before implementation begins.

**Key test suites covering constitutional substrates:**

| Test File | Substrate Covered | Last Known Status |
|-----------|------------------|-------------------|
| `tests/test_sovereign_audit_log.py` | SovereignAuditLog | Passing |
| `tests/test_12_vector_constitutional_break.py` | SovereignAuditLog, GenesisContinuityGuard | Passing |
| `tests/test_external_merkle_anchor.py` | ExternalMerkleAnchor + SAL | Passing (22) |
| `tests/test_tsa_integration.py` | TSAAnchorManager + RFC3161 | Passing |
| `tests/test_evidence_bundle.py` | EvidenceBundle | Passing (11) |
| `tests/test_governance_contract.py` | 10 contract points across substrates | Passing (23) |
| `tests/test_execution_gate_enforcement.py` | ExecutionGate | Passing |
| `tests/test_iron_path_executor.py` | IronPathExecutor | Passing |
| `tests/test_psia_invariants.py` | INV-ROOT-1 through INV-ROOT-9 | Passing |
| `tests/test_formal_properties.py` | 7 formal theorems (Hypothesis) | Passing |
| `tests/test_state_register_continuity_hash.py` | StateRegister continuity_hash | Passing |
| `tests/test_ed25519_crypto.py` | Ed25519Provider / CapabilityAuthority | Passing |

---

## 5. Known Conflict Table

Eight critical architectural conflicts identified in this analysis:

| # | Conflict | Files Involved | Risk |
|---|----------|---------------|------|
| C-1 | 3 silent `except Exception: pass` blocks disable RuntimeEnforcer, StateRegister, TrustScoring | `execution_router.py:50,58,74` | CRITICAL |
| C-2 | `_auto_approve()` is an active parallel authority when no Triumvirate injected | `governance_service.py:344–386` | CRITICAL |
| C-3 | GovernanceKernel writes to `AuditLog()` directly, bypassing AuditManager and SovereignAuditLog | `governance_kernel.py:~139–200` | HIGH |
| C-4 | `capability_token.py` (HMAC-SHA256, dev secret) and `capability_authority.py` (Ed25519) are dual, independent token issuers | `capability_token.py`, `capability_authority.py` | HIGH |
| C-5 | AuditManager `sovereign_mode=False` default — no cryptographic audit trail unless opted in | `audit_manager.py:__init__` | HIGH |
| C-6 | `psia/invariants.py` invariant seal is `sig="governance-sealed"` — not a real Ed25519 signature | `invariants.py:14` | HIGH |
| C-7 | `governance.py` Triumvirate `_log_decision()` writes only to in-memory list — decisions lost on restart | `governance.py` | HIGH |
| C-8 | `governance_manager.py` proposal/vote/execute lifecycle is fully stubbed; no production callers | `governance_manager.py` | MEDIUM |

---

## 6. Files Flagged for Special Handling

| File | Flag | Reason |
|------|------|--------|
| `src/app/governance/genesis_continuity.py` | MODIFIED_UNSTAGED | Core substrate with uncommitted changes |
| `src/app/core/capability_token.py` | DEV_SECRET_DEFAULT | Default HMAC key = "dev-secret-change-in-production" |
| `src/app/core/policy_registry.py` | DEV_SECRET_DEFAULT | Default HMAC key = "dev-policy-secret" |
| `src/psia/invariants.py` | PLACEHOLDER_SEAL | `sig="governance-sealed"` is not a real cryptographic signature |
| `src/app/governance/governance_manager.py` | FULLY_STUBBED | All 4 lifecycle methods are explicit stubs |
| `src/app/core/deterministic_replay.py` | NOT_WIRED | No test file; not wired to decision log |
| `src/app/governance/acceptance_ledger.py` | NO_DEDICATED_TESTS | No `test_acceptance_ledger.py` exists |
| `canonical/replay.py` | WRITES_ARTIFACT | Writes `canonical/execution_trace.json` on every run — do not run in analysis-only mode |

---

## 7. Proposed Safe Migration Order

Based on the caller map and dependency graph (detailed in `iron_path_2_boot_order.md`):

1. Annotate only (no behavior change): execution_router silent passes, _auto_approve(), invariant seal placeholder
2. Wire AuditManager into governance_kernel (closes C-3)
3. Enable sovereign_mode=True in production callers
4. Fix execution_router silent passes to emit bypass EvidenceBundles
5. Rotate dev secrets (policy_registry, capability_token) via environment variable enforcement
6. Dual-verify capability tokens (HMAC + Ed25519) in ExecutionGate Stage 6
7. Replace invariant seal with real Ed25519 signature
8. Link EvidenceBundle IDs to ConstitutionalLedger entries
9. Resolve governance_manager stub or deprecate with notice

---

## 8. Snapshot Attestation

| Property | Value |
|----------|-------|
| Analysis type | Static read-only |
| Source modified | None |
| SHA frozen | `e3913e6c9073f488ed2d82b1afeb039e1e46e616` |
| Analysis date | 2026-06-03 |
| Branch | `substrate-consolidation` |
| Status | FROZEN — baseline established |

> **This document is a point-in-time snapshot. It does not claim production readiness. It establishes the baseline for Iron Path 2.0 implementation.**

---

*Next report: [iron_path_2_actual_execution_lifecycle.md](iron_path_2_actual_execution_lifecycle.md)*
