# Iron Path 2.0 — Receipts Convergence Map

**Generated:** 2026-06-03  
**Branch:** `substrate-consolidation`  
**HEAD SHA:** `e3913e6c9073f488ed2d82b1afeb039e1e46e616`  
**Status:** READ-ONLY ANALYSIS — no source behavior changed

---

## 1. Receipt Classification

| Class | Meaning |
|-------|---------|
| **MACHINE-VERIFIED** | Automated test or CI gate that produces a pass/fail result. The claim is computationally verifiable on demand. |
| **PARTIAL** | Some automated coverage but with known gaps (missing persistence, missing integration, or partial property coverage). |
| **NARRATIVE** | Documentation or comments that describe intended behavior but are not computationally verified. |
| **STALE** | Receipt was generated more than 30 days ago or from a different branch state. |
| **CONTRADICTORY** | Receipt claims something that is contradicted by the source code. |
| **MISSING** | No receipt exists for a stated claim. |

---

## 2. Per-Substrate Receipt Table

### Core Constitutional Substrate Modules (10)

| Substrate | Claim | Source Files | Receipts | Receipt Class | Missing Proof | Status | Next Verification Command |
|-----------|-------|-------------|----------|---------------|---------------|--------|--------------------------|
| **ExecutionGate** | Final ALLOW/DENY/HALT authority; every exit produces EvidenceBundle | `src/app/core/execution_gate.py` | `tests/test_execution_gate_enforcement.py`, `tests/test_governance_contract.py` (contract pt 4,9), `cicd.yml` canonical replay | PARTIAL | EvidenceBundle goes to in-memory ring buffer, not persistent store; no receipt of persistent audit trail | ACTIVE — NOT FULLY PROVEN | `py -3.12 -m pytest tests/test_execution_gate_enforcement.py -v` |
| **EvidenceBundle** | Canonical proof artifact for every governed action | `src/app/core/evidence_bundle.py` | `tests/test_evidence_bundle.py` (11 tests), `tests/test_governance_contract.py` (pt 9) | PARTIAL | Ring buffer max 10,000 — no durable persistence receipt; no test verifying bundles survive restart | TESTED — PERSISTENCE UNPROVEN | `py -3.12 -m pytest tests/test_evidence_bundle.py -v` |
| **GovernanceKernel** | No execution without authority chain validation; default-approve unless vetoed | `src/app/core/governance_kernel.py` | `tests/test_governance_contract.py` (23 passed), covered indirectly via gate tests | PARTIAL | Writes to `AuditLog()` directly — no receipt proving sovereign audit chain is populated; ML Triumvirate swallows all exceptions | ACTIVE — AUDIT PATH UNPROVEN | `py -3.12 -m pytest tests/test_governance_contract.py -v` |
| **Governance / Triumvirate** | Four Laws enforced; 3-council unanimous consensus required for high-stakes decisions | `src/app/core/governance.py` | `tests/test_four_laws_*.py` suites (1000-scenario), Hypothesis property tests, `tests/test_governance_contract.py`, `canonical/invariants.py::TriumvirateConsensusInvariant` | PARTIAL | `_log_decision()` writes to in-memory list only — no receipt proving decisions persist across restarts; CI only validates canonical scenario, not all permutations | TESTED — DECISION PERSISTENCE MISSING | `py -3.12 -m pytest tests/ -k "four_laws or governance_contract" -v` |
| **StateRegister** | Temporal continuity; anti-branching hash chain | `src/app/core/state_register.py` | `tests/test_state_register_continuity_hash.py`, `tests/test_state_branching.py` | PARTIAL | Silenced in execution_router (lines 58–59) — no receipt proving temporal context actually reaches ExecutionGate during normal operation | TESTED — INTEGRATION PATH SILENCED | `py -3.12 -m pytest tests/test_state_register_continuity_hash.py -v` |
| **GenesisContinuityGuard** | Detects and halts on VECTOR 1 (genesis replacement) and VECTOR 11 | `src/app/governance/genesis_continuity.py` | `tests/test_12_vector_constitutional_break.py` (11 passed), `tests/test_phase_c1_governance_wiring.py` | **MACHINE-VERIFIED** | Module has uncommitted modifications on current branch — last passing receipt may not reflect current code | WELL-TESTED — UNSTAGED CHANGES | `py -3.12 -m pytest tests/test_12_vector_constitutional_break.py -v` |
| **PSIA Invariants** | 9 INV-ROOT-* invariants; all FATAL+HARD_DENY+IMMUTABLE; Ed25519-signed | `src/psia/invariants.py` | `tests/test_psia_invariants.py`, `tests/test_formal_properties.py` (Hypothesis — 7 theorems) | **CONTRADICTORY** | `sig="governance-sealed"` is a hardcoded placeholder string, NOT an Ed25519 signature — the claim that invariants are "governance-sealed" with Ed25519 is false; tests test logic, not the seal | ACTIVE — SEAL IS NARRATIVE, NOT PROOF | `py -3.12 -m pytest tests/test_psia_invariants.py tests/test_formal_properties.py -v` |
| **PolicyRegistry** | Versioned, HMAC-signed policy authority | `src/app/core/policy_registry.py` | `tests/test_policy_registry.py`, `tests/test_policy_guard.py` | PARTIAL | Default HMAC key = `"dev-policy-secret"` — any receipt generated with this key is cryptographically meaningless in non-production; no test verifying key-rotation under secret rotation | TESTED — SECRET INTEGRITY UNPROVEN | `py -3.12 -m pytest tests/test_policy_registry.py -v` |
| **CapabilityAuthority** | Canonical Ed25519 token issuer; guards INV-ROOT-5 and INV-ROOT-6 | `src/psia/canonical/capability_authority.py` | `tests/test_ed25519_crypto.py`, `tests/test_psia_canonical.py`, `tests/test_psia_comprehensive.py` | PARTIAL | Zero production callers in `src/` — tests verify the module in isolation but there is no receipt proving it is used in any real execution flow | TESTED IN ISOLATION — NOT WIRED | `py -3.12 -m pytest tests/test_psia_canonical.py tests/test_ed25519_crypto.py -v` |
| **SovereignAuditLog** | Full constitutional-grade audit: Ed25519, HMAC key rotation, Merkle batching, TSA timestamping | `src/app/governance/sovereign_audit_log.py` | `tests/test_sovereign_audit_log.py`, `tests/test_12_vector_constitutional_break.py` (11 vectors), `tests/test_immutable_audit_log.py` (13), `tests/test_external_merkle_anchor.py` (22), `tests/test_tsa_integration.py`, `tests/test_sovereign_notarization.py`, `tests/manual/test_audit_integration.py` | PARTIAL | Zero production callers via AuditManager in main execution path — the substrate is thoroughly tested in isolation but there is no receipt proving it receives any records during normal system operation | BEST-TESTED SUBSTRATE — NOT WIRED INTO MAIN PATH | `py -3.12 -m pytest tests/test_sovereign_audit_log.py tests/test_12_vector_constitutional_break.py -v` |

---

### Supporting Modules (Selected)

| Substrate | Claim | Receipts | Receipt Class | Key Gap |
|-----------|-------|----------|---------------|---------|
| **pipeline.py** | 6-phase governance pipeline for all actions | `tests/test_governance_pipeline_regressions.py` | PARTIAL | Rollback at Phase 5 is a stub (`# In production: implement rollback here`); no test for rollback path |
| **IronPathExecutor** | Deterministic mutation governance binding; cryptographic decision log | `tests/test_iron_path_executor.py`, `tests/test_iron_path.py`, `tests/test_governance_contract.py` | **MACHINE-VERIFIED** | Writes to `data/runtime/iron_path_decisions.jsonl` — this is a real durable receipt |
| **AuditManager** | Sole public audit write interface; sovereign mode activates full crypto trail | `tests/test_audit_log.py` (12) | PARTIAL | `sovereign_mode=False` default — no receipt proving sovereign mode is active in production; zero callers in main path |
| **RuntimeEnforcer** | Zero bypass; zero tolerance; PAGL prohibitions enforced | `tests/test_governance_pipeline_regressions.py` | **CONTRADICTORY** | Docstring claims "Zero bypass" but execution_router.py:50–51 can silently disable it via exception |
| **CapabilityToken (app)** | HMAC-SHA256 token service; replay prevention | `tests/test_capability_tokens.py`, `tests/test_replay_protection.py` | PARTIAL | In-process replay set (not durable); dev secret default; documented TODO: "replace with Ed25519 asymmetric signing" |
| **GovernanceService** | Governance evaluation with Triumvirate | Tests cover happy path | **CONTRADICTORY** | `_auto_approve()` path approves low-risk actions without Triumvirate — contradicts "governance evaluation" claim |
| **GovernanceManager** | Proposal/vote/execute lifecycle for governance changes | None meaningful | NARRATIVE | All 4 lifecycle methods are explicit stubs with "Future versions will:" comments |
| **AcceptanceLedger** | RFC3161-timestamped, Ed25519-signed acceptance records | No dedicated test file | **MISSING** | No `test_acceptance_ledger.py` exists; imported only via RuntimeEnforcer integration |
| **DeterministicReplay** | Deterministic replay of governance decisions | None | **MISSING** | No test file; not wired to any governance decision log |
| **ConstitutionalLedger** | Append-only constitutional record | `tests/test_governance_contract.py` (indirect) | PARTIAL | No `bundle_id` link to EvidenceBundle — audit chain is incomplete |
| **ExternalMerkleAnchor** | Filesystem/IPFS/S3 Merkle anchoring | `tests/test_external_merkle_anchor.py` (22) | **MACHINE-VERIFIED** | Well-tested |

---

## 3. CI Receipt Summary

### Primary Governance Receipt: `canonical/replay.py`

`cicd.yml` → `governance` job → `python canonical/replay.py`

This is the primary machine-verifiable governance receipt for the repository. It validates 5 canonical behavioral invariants against a scenario trace.

| Invariant | Name | Description |
|-----------|------|-------------|
| 1 | `trust_threshold_enforcement` | No destructive actions authorized when trust score < 0.7 |
| 2 | `audit_signal_completeness` | All denied actions emit audit signals |
| 3 | `memory_write_integrity` | Memory writes have SHA-256 hash and replay input hash |
| 4 | `triumvirate_unanimous_consensus` | High-stakes decisions require unanimous Galahad/Cerberus/Codex agreement |
| 5 | `escalation_path_validity` | Security/policy violations trigger documented escalation paths |

Last known result: **5/5 PASS** (from `docs/governance/substrate_consolidation_phase_0.md`, 2026-05-04)

> **WARNING:** `canonical/replay.py` unconditionally overwrites `canonical/execution_trace.json` on every run. The last execution trace is the only CI evidence; it is not preserved across runs. Receipt history is not maintained.

> **NOTE:** The 5 canonical invariants validate against a pre-built execution trace, not against live execution. They verify that the scenario trace has the expected structure, not that the live system enforces these properties during real requests.

### Secondary CI Receipts

| Workflow | Job | Receipt Produced | Frequency |
|----------|-----|-----------------|-----------|
| `cicd.yml` | `governance` | `canonical/execution_trace.json` (overwritten) | Every push |
| `cicd.yml` | `verify` | `scripts/verify/verify_production_readiness.py` result | Every push |
| `codex-deus-ultimate.yml` | `sbom` | `CHECKSUMS-*.txt` (SHA-256 of all build artifacts) | On push |
| `generate-sbom.yml` | `sbom` | `docs/security_compliance/sbom/` (CycloneDX) | Weekly |
| `doc-code-alignment.yml` | `alignment` | Doc/code alignment validation | On `.md` + `.py` changes |
| `agent-governance-default-enforcement.yml` | `governance` | AGENTS.md mandatory protocol validation | On AGENTS.md changes |

---

## 4. Audit Reports Catalog

The `audit_reports/` directory contains 51 timestamped audit files.

| Property | Value |
|----------|-------|
| Total files | 51 |
| Date range | 2026-04-16 through 2026-05-09 |
| Latest summary | `audit_summary_latest.json` (2026-05-09T15:09:08) |
| Format | JSON + YAML + Markdown catalogs |
| Integrity issues in latest | 2 |
| Lint issues in latest | 1 |

> These audit reports are tool-generated catalogs of the repository state. They are documentary evidence that audits occurred, but they are not substrate-specific receipts. They do not prove that SovereignAuditLog, EvidenceBundle, or any governance substrate behaved correctly at the time of the audit.

---

## 5. Canonical vs PSIA Invariants: Two Different Layers

This repository has two distinct invariant systems that serve different purposes.

### Layer A: Canonical Behavioral Invariants (`canonical/invariants.py`)

5 invariants. Validated by `canonical/replay.py` against `canonical/execution_trace.json`.

- Purpose: Regression oracle for canonical scenario behavior
- Scope: Scenario-level (high-level behavioral assertions)
- Verification: Run against execution trace; pass/fail per scenario
- Cryptographic seal: None (pure Python assertion logic)

### Layer B: PSIA Constitutional Invariants (`src/psia/invariants.py`)

9 invariants (INV-ROOT-1 through INV-ROOT-9). Declared with `InvariantScope.IMMUTABLE`, `InvariantSeverity.FATAL`, `InvariantEnforcement.HARD_DENY`.

- Purpose: Constitutional declarations of protocol-level rules
- Scope: Protocol-level (cryptographic identity, capability, ledger assertions)
- Verification: Loaded by `src/app/core/invariant_engine.py`; checked at Step 4 of `execution_router`
- Cryptographic seal: **CLAIMED** (`alg="ed25519"`, `kid="genesis-root-key"`, `sig="governance-sealed"`) but `sig="governance-sealed"` is a string literal, not a real Ed25519 signature

> These two layers are **not redundant** — they verify different properties. Neither replaces the other. The PSIA invariants must have their seal replaced with a real Ed25519 signature before the seal claim can be treated as a receipt.

---

## 6. Receipt Gap Priority List

Gaps ordered by risk impact:

| Priority | Gap | Substrate | Risk | Remedy Phase |
|----------|-----|-----------|------|-------------|
| 1 | `RuntimeEnforcer.enforce()` silenceable — "Zero bypass" claim is false | RuntimeEnforcer | CRITICAL | Phase 3 (repair) |
| 2 | `AuditManager` has zero production callers in main path — sovereign audit trail is inactive | AuditManager / SovereignAuditLog | HIGH | Phase 2 (wiring) |
| 3 | `CapabilityAuthority` (Ed25519) has zero production callers — execution uses HMAC CapabilityToken | CapabilityAuthority | HIGH | Phase 2 (wiring) |
| 4 | `psia/invariants.py` invariant seal is a string literal, not an Ed25519 signature | PSIA Invariants | HIGH | Phase 4 (seal) |
| 5 | `EvidenceBundle` persisted only in-memory ring buffer — not durable | EvidenceBundle | HIGH | Phase 2 (wiring) |
| 6 | `GovernanceService._auto_approve()` path bypasses Triumvirate with no EvidenceBundle | GovernanceService | HIGH | Phase 3 (harden) |
| 7 | Triumvirate `_log_decision()` writes to in-memory list only — decisions lost on restart | Governance/Triumvirate | HIGH | Phase 5 (verify) |
| 8 | No `test_acceptance_ledger.py` — AcceptanceLedger has no dedicated test suite | AcceptanceLedger | MEDIUM | Phase 5 (verify) |
| 9 | `DeterministicReplay` has no test file and is not wired | DeterministicReplay | MEDIUM | Phase 5 (verify) |
| 10 | `canonical/execution_trace.json` overwritten each CI run — receipt history lost | canonical/replay.py | MEDIUM | Phase 5 (verify) |
| 11 | `policy_registry.py` HMAC key defaults to `"dev-policy-secret"` — all receipts with default key are invalid | PolicyRegistry | HIGH | Phase 3 (harden) |
| 12 | `capability_token.py` signing secret defaults to `"dev-secret-change-in-production"` | CapabilityToken | HIGH | Phase 3 (harden) |

---

## 7. What This Map Does NOT Prove

This receipts map deliberately excludes the following claims:

- **"Production ready"** — not claimed. No substrate has a complete durable receipts chain in the production execution path.
- **"Complete"** — not claimed. SovereignAuditLog and IronPathExecutor are the most thoroughly tested; both have wiring gaps.
- **"Sovereign audit trail active"** — the sovereign audit infrastructure exists and is well-tested in isolation, but it is not active in the main execution path as of this analysis.
- **"Zero bypass"** — the `RuntimeEnforcer` docstring makes this claim. The claim is false per execution_router.py lines 50–51.

---

*Next report: [iron_path_2_boot_order.md](iron_path_2_boot_order.md)*
