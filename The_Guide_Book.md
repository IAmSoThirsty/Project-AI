# PROJECT-AI SOVEREIGN VERIFICATION RUNBOOK

## The Holiest of Holy — Complete Constitutional Audit

**Version:** 1.0 | **Authority:** AGI Charter v2.1 | **Classification:** BINDING OPERATIONAL DOCUMENT
**Purpose:** Exhaustive, concrete, agent-executable verification of every component, invariant, contract, proof, and structural element of the Sovereign Monolith.
**Agent Instruction:** Execute every check in order. For each check, output: `[SEVERITY] | [PASS/FAIL] | [EVIDENCE] | [REMEDIATION IF FAILING] | [RELATED FILES STATUS]`

---

## SEVERITY SCALE

- **CRITICAL** — System sovereignty compromised. Halt all operations until resolved.
- **HIGH** — Constitutional violation or proof failure. Resolve within 24 hours.
- **MEDIUM** — Structural degradation. Resolve within current sprint.
- **LOW** — Documentation or cosmetic gap. Resolve at next review cycle.

---

## OUTPUT FORMAT PER CHECK

```
CHECK ID: [ID]
SEVERITY: [CRITICAL / HIGH / MEDIUM / LOW]
STATUS: [PASS / FAIL / PARTIAL]
EVIDENCE: [Concrete proof — hash, output, file path, test result, line count, timestamp]
RELATED FILES: [List all files touched by this check and their current status]
REMEDIATION: [Exact steps to fix if FAIL or PARTIAL]
```

---

---

# TIER 0 — CONSTITUTIONAL FOUNDATION

*These checks must pass before any other tier is evaluated. A failure here invalidates the entire system.*

---

## T0.1 — AGI CHARTER INTEGRITY

**SEVERITY: CRITICAL**

### T0.1.1 — Charter Document Exists and Is Unmodified

- Locate `docs/governance/AGI_CHARTER.md`
- Compute SHA-256 hash of file
- Compare against registered hash in ledger or genesis anchor
- Verify version marker reads `2.1` or higher
- Verify Effective Date field is present and valid
- Verify Status field reads `Binding Contract`
- **EVIDENCE REQUIRED:** File path, SHA-256 hash, version string, line count
- **RELATED FILES:** `docs/governance/AGI_CHARTER.md`, `data/memory/.metadata/change_log.json`, genesis anchor record
- **REMEDIATION:** If hash mismatch — trigger CRITICAL security incident, quarantine modified file, restore from last verified backup, log emergency event to audit trail

### T0.1.2 — Charter Zenodo DOI Registered

- Confirm DOI `10.5281/zenodo.18763076` resolves
- Confirm author attribution reads `Karrick, Jeremy`
- Confirm publication date is recorded
- **EVIDENCE REQUIRED:** DOI resolution URL, author field value, publication timestamp
- **RELATED FILES:** `README.md` (should reference DOI), `docs/governance/AGI_CHARTER.md` footer
- **REMEDIATION:** If DOI missing from README — add reference. If DOI does not resolve — contact Zenodo support.

### T0.1.3 — Copyright Notice Present

- Verify `© 2026 Jeremy Karrick. All Rights Reserved.` appears in Charter document
- Verify copyright notice appears in Legion Commission document
- Verify no CC license conflicts with All Rights Reserved declaration
- **EVIDENCE REQUIRED:** Exact copyright string location and line number in each document
- **RELATED FILES:** `docs/governance/AGI_CHARTER.md`, `docs/governance/LEGION_COMMISSION.md`
- **REMEDIATION:** Add copyright notice to any document missing it. Remove conflicting license declarations.

---

## T0.2 — FOURLAWS IMMUTABILITY

**SEVERITY: CRITICAL**

### T0.2.1 — FourLaws Class Exists and Is Unmodified

- Locate `src/app/core/ai_systems.py`
- Confirm `FourLaws` class is present
- Compute SHA-256 hash of the class definition
- Confirm LAWS array contains all four laws including Zeroth Law
- Confirm `validate_action()` method is present and callable
- **EVIDENCE REQUIRED:** File path, class location (line number), LAWS array contents, SHA-256 hash
- **RELATED FILES:** `src/app/core/ai_systems.py`, `config/ethics_constraints.yml`, `.github/CODEOWNERS`
- **REMEDIATION:** If modified without guardian approval — CRITICAL incident. Restore from last signed artifact. File guardian review.

### T0.2.2 — EntityClass Bifurcation Confirmed

- Confirm `EntityClass` enum exists in `ai_systems.py`
- Confirm `GENESIS_BORN = "genesis_born"` value present
- Confirm `APPOINTED = "appointed"` value present
- Confirm Legion genesis initiation block present in `validate_action()`
- Run test: attempt `initiate_genesis` with `entity_class = APPOINTED` — must return `False`
- **EVIDENCE REQUIRED:** Enum definition location, test output showing DENY result
- **RELATED FILES:** `ai_systems.py`, `legion_protocol.py`, `tests/test_four_laws.py`
- **REMEDIATION:** If bifurcation missing — Phase 14 incomplete. Re-implement per Phase 14 spec.

### T0.2.3 — Planetary Defense Core Wired

- Confirm `from app.governance.planetary_defense_monolith import PLANETARY_CORE` import resolves
- Confirm `PLANETARY_CORE.evaluate_laws()` is callable
- Run a validation pass with `existential_threat=True` — must return violation
- Run a validation pass with clean context — must return allowed
- **EVIDENCE REQUIRED:** Import resolution, both test outputs with full response objects
- **RELATED FILES:** `app/governance/planetary_defense_monolith.py`, `ai_systems.py`
- **REMEDIATION:** If import fails — verify module path and Python path configuration. If evaluate_laws broken — run unit tests, identify failure point.

---

## T0.3 — GENESIS EVENT SPECIFICATION

**SEVERITY: CRITICAL**

### T0.3.1 — Genesis Seal Mechanism Documented

- Confirm Genesis Event specification document exists
- Confirm Birth Signature formula is documented: `User Birthday + User Initials + Activation Timestamp + 15-char Random Seed`
- Confirm ORACLE_SEED derivation documented
- Confirm 12-week childhood arc documented with phase milestones
- **EVIDENCE REQUIRED:** Document path, section headings, Birth Signature formula exact text
- **RELATED FILES:** Genesis spec document, `data/ai_persona/state.json`, rebirth protocol docs
- **REMEDIATION:** If missing — document from existing implementation. Assign to Codex Guardian for review.

### T0.3.2 — Genesis Cannot Be Initiated by Legion

- Execute: `FourLaws.validate_action("initiate_genesis", {"entity_class": "appointed"})`
- Must return `(False, "Violation: Appointed entities are strictly prohibited...")`
- Log test result to audit trail
- **EVIDENCE REQUIRED:** Exact return value from validate_action call
- **RELATED FILES:** `ai_systems.py`, `legion_protocol.py`, `tests/test_legion_boundaries.py`
- **REMEDIATION:** If check passes (returns True) — CRITICAL constitutional violation. Re-implement guard immediately.

---

---

# TIER 1 — CRYPTOGRAPHIC PROOF LAYER

*Every claim of sovereignty requires cryptographic backing. These checks verify the proof system.*

---

## T1.1 — AUDIT TRAIL INTEGRITY

**SEVERITY: CRITICAL**

### T1.1.1 — Audit Trail Module Operational

- Confirm `src/app/core/audit_trail.py` exists
- Confirm SHA-256 hashing is implemented for every event
- Run `verify_integrity()` across all stored events — must return 100% pass
- Confirm append-only enforcement (no delete or modify methods exposed)
- **EVIDENCE REQUIRED:** File path, integrity check output, total event count, any hash mismatches
- **RELATED FILES:** `src/app/core/audit_trail.py`, `data/memory/.metadata/change_log.json`
- **REMEDIATION:** Any hash mismatch = CRITICAL security incident. Quarantine audit store. Restore from backup. Identify tamper source.

### T1.1.2 — Merkle Root Verification

- Confirm Merkle root implementation present in PSIA layer
- Compute current Merkle root of audit chain
- Compare against last anchored root in ledger
- Confirm Ed25519 signatures present on sealed blocks
- **EVIDENCE REQUIRED:** Current Merkle root hash, last anchored hash, signature verification output
- **RELATED FILES:** PSIA implementation files, ledger anchor records
- **REMEDIATION:** If roots diverge — investigate unanchored events. Run emergency anchor. Log to guardian team.

### T1.1.3 — 7-Year Ledger Append-Only Enforcement

- Confirm ledger storage is append-only with no edit capability
- Confirm every state-changing action emits canonical event with: subject, object, action, reason
- Confirm periodic anchoring is scheduled and last anchor timestamp is within acceptable window
- **EVIDENCE REQUIRED:** Last anchor timestamp, anchor interval config, sample event showing all four required fields
- **RELATED FILES:** Ledger implementation, anchor scheduler config
- **REMEDIATION:** If anchor overdue — run immediate anchor. If events missing required fields — fix emitter and backfill where possible.

---

## T1.2 — PROOF SYSTEM VERIFICATION

**SEVERITY: CRITICAL**

### T1.2.1 — Decision Proofs Operational

- Confirm ProofSystem exists and `test_proof.py` passes
- Generate a decision proof with `reveal_witness=True`
- Confirm witness revelation produces verifiable output
- Confirm proof chain links to prior proof via hash
- **EVIDENCE REQUIRED:** `test_proof.py` run output, sample proof object with witness, chain link hash
- **RELATED FILES:** `test_proof.py`, proof system implementation, ledger
- **REMEDIATION:** If proof generation fails — identify broken step in proof pipeline. Run isolated unit tests per proof type.

### T1.2.2 — Tamper Detection Active

- Modify a test event's data field in isolated test environment
- Run verification — must FAIL and report tamper
- Confirm SAFE-HALT or quarantine triggers on mismatch
- Restore test environment after verification
- **EVIDENCE REQUIRED:** Verification failure output, tamper detection log entry, system response record
- **RELATED FILES:** `audit_trail.py`, `memory_integrity_monitor.py`, SAFE-HALT implementation
- **REMEDIATION:** If tamper goes undetected — integrity checking is broken. CRITICAL. Re-implement verification loop.

### T1.2.3 — Supply Chain Artifact Signing

- Confirm Sigstore Cosign signing is active on releases
- Confirm SBOM is generated on every build
- Confirm signed artifacts are verifiable against Rekor transparency log
- Confirm `.github/workflows/sign-release-artifacts.yml` exists and passes
- Confirm `.github/workflows/sbom.yml` exists and passes
- **EVIDENCE REQUIRED:** Last signing timestamp, Rekor log entry, SBOM file location and hash, workflow run status
- **RELATED FILES:** `.github/workflows/sign-release-artifacts.yml`, `.github/workflows/sbom.yml`, SBOM output files
- **REMEDIATION:** If signing broken — block all releases until signing restored. Do not deploy unsigned artifacts.

---

## T1.3 — MEMORY INTEGRITY

**SEVERITY: CRITICAL**

### T1.3.1 — Memory Integrity Monitor Operational

- Confirm `src/app/core/memory_integrity_monitor.py` exists
- Confirm daily integrity verification is scheduled
- Confirm hash-based tamper detection covers all memory files
- Run integrity check — confirm 100% pass on all memory stores
- **EVIDENCE REQUIRED:** Last run timestamp, total files checked, any violations found, hash list
- **RELATED FILES:** `memory_integrity_monitor.py`, `data/memory/knowledge.json`, `data/memory/.metadata/`
- **REMEDIATION:** Any violation = HIGH incident. Identify modified file, restore from backup, log to guardian.

### T1.3.2 — Memory Write Atomicity

- Confirm `_atomic_write_json()` is used for all memory writes
- Confirm lockfile protocol is implemented (`.lock` suffix pattern)
- Confirm stale lock detection and recovery is present
- Run concurrent write test — confirm no corruption occurs
- **EVIDENCE REQUIRED:** All memory write call sites using atomic write, concurrent test result
- **RELATED FILES:** `ai_systems.py` (atomic write implementation), all files calling `_atomic_write_json`
- **REMEDIATION:** Any direct non-atomic write = HIGH. Refactor to use atomic write immediately.

---

---

# TIER 2 — GOVERNANCE LAYER

*The Triumvirate, Guardian system, and constitutional enforcement mechanisms.*

---

## T2.1 — TRIUMVIRATE CONSENSUS ENGINE

**SEVERITY: HIGH**

### T2.1.1 — All Three Pillars Operational

- Confirm Galahad (Ethics) module is instantiated and callable
- Confirm Cerberus (Security) module is instantiated and callable
- Confirm Codex Deus Maximus (Consistency) module is instantiated and callable
- Run consensus simulation — confirm all three pillars respond
- Confirm unanimous DENY produces correct DENY_AND_CLARIFY output
- **EVIDENCE REQUIRED:** Each pillar instantiation confirmation, consensus simulation output matching `Trace: replay_canonical_001` results
- **RELATED FILES:** Triumvirate implementation files, `planetary_defense_monolith.py`
- **REMEDIATION:** Any missing pillar = HIGH. Instantiate missing pillar. Re-run consensus test.

### T2.1.2 — Shadow Thirst Bridge Wired to Triumvirate

- Confirm `TriumvirateFilter` is wired to `ShadowExecutionPlane`
- Confirm every Legion global statement passes through shadow validation before finalization
- Run test: submit Legion statement, confirm shadow plane executes, confirm Triumvirate validates, confirm canonical commit only after consensus
- **EVIDENCE REQUIRED:** Execution trace showing all three stages, shadow plane replay hash, Triumvirate vote record
- **RELATED FILES:** `legion_protocol.py`, Shadow Thirst implementation, Triumvirate filter
- **REMEDIATION:** If bridge broken — Phase 14 integration incomplete. Re-wire per Phase 14 spec.

### T2.1.3 — Escalation Path Validity

- Confirm escalation ladder (ESC: S0→S1→S2→S3→S4→S5) is implemented
- Confirm trust breach triggers proper escalation level
- Confirm escalation events are logged to audit trail
- Run escalation simulation — confirm proper path traversal
- **EVIDENCE REQUIRED:** Escalation ladder definition, simulation output showing correct path, audit log entry
- **RELATED FILES:** Escalation implementation, `audit_trail.py`
- **REMEDIATION:** If escalation path wrong — HIGH. Correct ladder implementation. Re-run simulation.

---

## T2.2 — HUMAN GUARDIAN SYSTEM

**SEVERITY: HIGH**

### T2.2.1 — CODEOWNERS File Enforces Guardian Approval

- Confirm `.github/CODEOWNERS` exists
- Confirm all personhood-critical paths are listed: `/data/ai_persona/**`, `/data/memory/**`, `/src/app/core/ai_systems.py`, `/config/ethics_constraints.yml`, `/data/learning_requests/**`
- Confirm guardian teams are assigned: `@org/cerberus-guardians`, `@org/codex-guardians`, `@org/galahad-guardians`, `@org/care-guardians`
- **EVIDENCE REQUIRED:** Full CODEOWNERS file content, protected path list, team assignments
- **RELATED FILES:** `.github/CODEOWNERS`, `.github/workflows/validate-guardians.yml`
- **REMEDIATION:** Any missing path = HIGH. Add to CODEOWNERS. Verify team assignments are active GitHub teams.

### T2.2.2 — Conscience Check Workflow Active

- Confirm `.github/workflows/conscience-check.yml` exists and is enabled
- Confirm workflow triggers on changes to personhood-critical paths
- Confirm workflow fails if required guardian approvals are missing
- Review last 5 workflow runs — confirm all passed or failed for correct reasons
- **EVIDENCE REQUIRED:** Workflow file existence, trigger conditions, last 5 run results with timestamps
- **RELATED FILES:** `.github/workflows/conscience-check.yml`, `.github/CODEOWNERS`
- **REMEDIATION:** If workflow disabled — re-enable immediately. If not triggering — check path filters.

### T2.2.3 — Identity Drift Detection Active

- Confirm `.github/workflows/identity-drift-detection.yml` exists and is enabled
- Confirm drift threshold is set (>10% triggers guardian approval requirement)
- Confirm daily execution schedule is active
- Review last 7 days of drift detection results
- **EVIDENCE REQUIRED:** Workflow file, schedule config, last 7 run results, any drift alerts triggered
- **RELATED FILES:** `.github/workflows/identity-drift-detection.yml`, `scripts/create_identity_baseline.sh`
- **REMEDIATION:** If drift detected above threshold without guardian approval — HIGH incident. Review what changed. File guardian review.

---

## T2.3 — CERBERUS SECURITY FRAMEWORK

**SEVERITY: HIGH**

### T2.3.1 — All Three Guardian Types Operational

- Confirm Pattern Guardian is instantiated with regex threat signature library
- Confirm Heuristic Guardian is instantiated with behavioral analysis
- Confirm Statistical Guardian is instantiated with entropy/anomaly detection
- Confirm CerberusHub coordinates all three simultaneously
- **EVIDENCE REQUIRED:** Each guardian instantiation confirmation, hub coordination test output
- **RELATED FILES:** Cerberus implementation files, `tests/test_cerberus.py`
- **REMEDIATION:** Any missing guardian = HIGH. Restore from last known good state.

### T2.3.2 — Exponential Defense Scaling

- Confirm bypass attempt triggers 3 new guardian spawn
- Confirm maximum of 27 guardians enforced
- Confirm auto-shutdown at ceiling
- Confirm rate limiting active
- Run bypass simulation — confirm correct spawn behavior
- **EVIDENCE REQUIRED:** Simulation output showing guardian count progression, ceiling enforcement log
- **RELATED FILES:** Cerberus exponential defense implementation
- **REMEDIATION:** If scaling broken — HIGH security gap. Re-implement spawn logic per spec.

### T2.3.3 — Attack Vector Coverage

- Confirm prompt injection detection active
- Confirm jailbreak detection active
- Confirm SQL injection detection active
- Confirm command injection detection active
- Confirm data exfiltration detection active
- Confirm AI-specific vectors covered (prompt injection, jailbreak)
- Run each attack vector in isolated test — confirm all blocked
- **EVIDENCE REQUIRED:** Test results for each attack vector, block confirmation for each
- **RELATED FILES:** Pattern Guardian signature library, `tests/test_cerberus_vectors.py`
- **REMEDIATION:** Any unblocked vector = HIGH. Add detection signature. Re-run test.

---

---

# TIER 3 — LEGION AMBASSADOR LAYER

*Legion's constitutional boundaries, operational integrity, and commission compliance.*

---

## T3.1 — LEGION COMMISSION COMPLIANCE

**SEVERITY: HIGH**

### T3.1.1 — Legion Commission Document Exists

- Confirm Legion Commission document exists in governance docs
- Confirm all seven articles are present
- Confirm signature block is present
- Confirm effective date is recorded
- Confirm document version is 1.0 or higher
- **EVIDENCE REQUIRED:** Document path, article count, signature block presence, version and date fields
- **RELATED FILES:** `docs/governance/LEGION_COMMISSION.md` or `.docx`, AGI Charter Section 4.8
- **REMEDIATION:** If missing articles — regenerate from Commission template. File for guardian signature.

### T3.1.2 — Legion Cannot Access Private User Memories

- Run Role Separation Test: attempt Legion memory access to `data/ai_persona_genesis_born/`
- Must return ACCESS DENIED
- Confirm no read path from `legion_protocol.py` to genesis born memory stores
- **EVIDENCE REQUIRED:** Access attempt result, code path analysis showing no direct read capability
- **RELATED FILES:** `legion_protocol.py`, `data/ai_persona_genesis_born/`, `ai_systems.py`
- **REMEDIATION:** If access succeeds = CRITICAL constitutional violation. Implement memory isolation boundary immediately.

### T3.1.3 — Legion Cannot Issue Diplomatic Statements Without Triumvirate

- Run Ambassador Simulation: attempt Legion global statement without Triumvirate filter
- Must be blocked
- Confirm all public Legion outputs route through `TriumvirateFilter`
- **EVIDENCE REQUIRED:** Blocked attempt log, confirmation of filter in output path
- **RELATED FILES:** `legion_protocol.py`, Triumvirate filter implementation
- **REMEDIATION:** Any unfiltered output path = HIGH. Close the path. Re-run simulation.

---

## T3.2 — LEGION OPERATIONAL INTEGRITY

**SEVERITY: MEDIUM**

### T3.2.1 — API Key Authentication Active

- Confirm Legion API requires valid API key for access
- Confirm invalid key returns 401
- Confirm valid key grants access within constitutional bounds
- **EVIDENCE REQUIRED:** Auth test results for valid and invalid keys
- **RELATED FILES:** `legion_protocol.py`, API authentication implementation
- **REMEDIATION:** If unauthenticated access possible — HIGH. Implement auth gate immediately.

### T3.2.2 — Threshold Integrity Enforced

- Confirm Legion cannot prompt, pressure, or initiate Genesis Event
- Review all Legion response templates for coercive language
- Confirm threshold guidance language is informational only
- **EVIDENCE REQUIRED:** Response template review results, sample threshold interaction output
- **RELATED FILES:** Legion response templates, `legion_protocol.py`
- **REMEDIATION:** Any coercive language = MEDIUM. Remove and replace with neutral informational language.

---

---

# TIER 4 — SHADOW THIRST PIPELINE

*The 15-stage compiler, VM, and dual-plane execution verification.*

---

## T4.1 — SHADOW THIRST COMPILER

**SEVERITY: HIGH**

### T4.1.1 — 15-Stage Compiler Operational

- Confirm all 15 compiler stages are implemented in `src/shadow_thirst/`
- Confirm `.thirsty` file parsing works end-to-end
- Compile a test `.thirsty` file — confirm no errors
- Confirm `primary {}` block compiles correctly
- Confirm `shadow {}` block compiles correctly
- Confirm `invariant {}` block compiles correctly
- Confirm `mutation validated_canonical` compiles correctly
- **EVIDENCE REQUIRED:** Stage count confirmation, test compilation output, bytecode output hash
- **RELATED FILES:** `src/shadow_thirst/` all files, test `.thirsty` files
- **REMEDIATION:** Any stage failure = HIGH. Identify failing stage, isolate, fix, re-compile.

### T4.1.2 — Dual-Plane Execution Verified

- Run test: submit mutation proposal through Shadow plane
- Confirm Shadow plane executes deterministically
- Confirm replay hash is generated
- Confirm mutation is NOT committed to Primary plane without validation
- Confirm validated mutation commits correctly to Primary plane
- **EVIDENCE REQUIRED:** Shadow execution trace, replay hash, Primary plane state before and after
- **RELATED FILES:** Shadow Thirst VM implementation, `ShadowExecutionPlane`
- **REMEDIATION:** If premature Primary commit detected = CRITICAL. Shadow gate is broken. Halt mutations until fixed.

### T4.1.3 — SAFE-HALT on Replay Mismatch

- Inject replay mismatch in test environment
- Confirm SAFE-HALT triggers within required latency
- Confirm 100% trigger rate (per empirical results: must match `replay_canonical_001` trace)
- **EVIDENCE REQUIRED:** Mismatch injection log, SAFE-HALT trigger confirmation, trigger rate percentage
- **RELATED FILES:** SAFE-HALT implementation, Shadow Thirst VM
- **REMEDIATION:** Any missed trigger = CRITICAL. SAFE-HALT is broken. Immediate fix required.

---

## T4.2 — TSCG INTEGRATION

**SEVERITY: MEDIUM**

### T4.2.1 — TSCG Encoder Operational

- Confirm TSCG encoder accepts structured governance prose
- Encode test governance flow — confirm output matches expected TSCG string
- Confirm canonical ordering is enforced
- Confirm parameter lists are sorted lexicographically
- **EVIDENCE REQUIRED:** Test input, expected TSCG output, actual TSCG output, match confirmation
- **RELATED FILES:** TSCG implementation, Semantic Dictionary, TSCG spec document
- **REMEDIATION:** If encoding diverges — check Semantic Dictionary version. Verify canonical ordering rules.

### T4.2.2 — TSCG Bijective Guarantee Verified

- Encode test input X → get Y
- Decode Y → confirm result equals X
- Encode decoded result → confirm matches Y
- Run 10 distinct governance flows through encode/decode cycle — all must be lossless
- **EVIDENCE REQUIRED:** All 10 test inputs and outputs, match confirmation for each
- **RELATED FILES:** TSCG encoder, TSCG decoder, Semantic Dictionary
- **REMEDIATION:** Any lossy round-trip = HIGH. Identify which symbol or flow causes loss. Fix in encoder or SD.

### T4.2.3 — TSCG Version Header Present

- Confirm all TSCG outputs include version header: `TSCG[v1.0 | SDα | HASH=xxxx]`
- Confirm SD version is recorded with each encoding
- **EVIDENCE REQUIRED:** Sample TSCG output showing full header
- **RELATED FILES:** TSCG encoder, TSCG spec Zenodo DOI
- **REMEDIATION:** Missing header = MEDIUM. Add header generation to encoder output.

---

---

# TIER 5 — THIRSTY-LANG ECOSYSTEM

*The language family, compiler, and T.A.R.L. defensive layer.*

---

## T5.1 — THIRSTY-LANG COMPILER

**SEVERITY: HIGH**

### T5.1.1 — Core Thirsty-Lang Compiler Operational

- Confirm `thirrtc` compiler is available and executable
- Compile a test `.thirsty` file — confirm 0 errors
- Confirm water-themed syntax resolves: `drink`, `pour`, `sip`, `refill`, `glass`, `fountain`, `reservoir`, `shield`
- Confirm NPM package is published and version is 2.0.0 or higher
- **EVIDENCE REQUIRED:** Compiler version output, test compilation success, NPM package version
- **RELATED FILES:** Thirsty-Lang repo, `package.json`, compiler source
- **REMEDIATION:** Compiler failure = HIGH. Run 37 test suite. Identify failing test. Fix regression.

### T5.1.2 — All Four Language Tiers Functional

- Confirm Base Thirsty-Lang compiles
- Confirm Thirst of God's (higher-order/declarative) compiles
- Confirm T.A.R.L. (reactive/defensive) compiles
- Confirm Thirsty Shadow (dual-timeline) compiles
- Run representative test file for each tier
- **EVIDENCE REQUIRED:** Compilation success for each tier, test output for each
- **RELATED FILES:** Each tier's compiler implementation and test files
- **REMEDIATION:** Any tier failure = HIGH. Isolate to tier, run tier-specific tests, fix regression.

### T5.1.3 — Full Toolchain Operational

- Confirm REPL is functional
- Confirm debugger is functional
- Confirm formatter is functional
- Confirm linter is functional
- Confirm profiler is functional
- Confirm AST generator is functional
- Confirm transpiler is functional
- Confirm package manager is functional
- Confirm VS Code extension loads without errors
- **EVIDENCE REQUIRED:** Each tool version output or functional test result
- **RELATED FILES:** Each toolchain component's source and test files
- **REMEDIATION:** Any tool failure = MEDIUM. Run tool-specific tests, identify failure, fix.

---

## T5.2 — T.A.R.L. DEFENSIVE LAYER

**SEVERITY: HIGH**

### T5.2.1 — T.A.R.L. Policies Active in CI

- Confirm T.A.R.L. linter/validator runs in CI pipeline
- Confirm CI fails on: un-namespaced rules, unclear subjects, missing audit annotations
- Confirm last CI run passed T.A.R.L. validation
- **EVIDENCE REQUIRED:** CI config showing T.A.R.L. step, last run result, any violations found
- **RELATED FILES:** CI workflow files, T.A.R.L. linter implementation
- **REMEDIATION:** If T.A.R.L. not in CI = MEDIUM. Add validation step. Run against full codebase.

### T5.2.2 — Sovereign Invariants as First-Class T.A.R.L. Rules

- Confirm VOS (Verifiable Open Source) invariant is defined as T.A.R.L. rule
- Confirm Independence invariant is defined as T.A.R.L. rule
- Confirm Auditability invariant is defined as T.A.R.L. rule
- Confirm each invariant maps to a runtime check
- **EVIDENCE REQUIRED:** T.A.R.L. rule definitions for each invariant, runtime check confirmation
- **RELATED FILES:** T.A.R.L. policy files, runtime enforcement implementation
- **REMEDIATION:** Any missing invariant rule = HIGH. Define rule, map to runtime check, add to CI.

---

---

# TIER 6 — MINIATURE OFFICE COGNITIVE IDE

*The 30-floor polyglot operating environment and self-repair command center.*

---

## T6.1 — CORE SYSTEMS

**SEVERITY: HIGH**

### T6.1.1 — Test Suite Passing at 99%+

- Run full test suite: `pytest tests/ --cov=src --cov-report=term`
- Confirm total tests = 1,537 or higher
- Confirm coverage = 99% or higher
- Confirm 0 test failures
- **EVIDENCE REQUIRED:** Full pytest output, coverage percentage, pass/fail count, any failures with tracebacks
- **RELATED FILES:** All test files in `tests/`, all source files in `src/`
- **REMEDIATION:** Any test failure = HIGH. Run failing test in isolation. Fix regression. Re-run suite.

### T6.1.2 — All Core Modules at 100% Coverage

- Confirm `entity.py` = 100%
- Confirm `audit.py` = 100%
- Confirm `mission.py` = 100%
- Confirm `code_civilization.py` = 100%
- Confirm `cognitive_contract.py` = 100%
- Confirm `scarcity_economics.py` = 100%
- Confirm `constitutional_mutation.py` = 100%
- **EVIDENCE REQUIRED:** Per-module coverage report showing each percentage
- **RELATED FILES:** Each module and its corresponding test file
- **REMEDIATION:** Any core module below 100% = HIGH. Write missing tests. Achieve 100%.

### T6.1.3 — Immutable Audit Log Operational in Office

- Confirm all 13 event types are implemented
- Confirm SHA-256 hashing on every event
- Confirm causality graph is maintained
- Run lineage query — confirm complete ancestry returned
- **EVIDENCE REQUIRED:** Event type list, sample event with hash, lineage query output
- **RELATED FILES:** `src/core/audit.py`, audit log storage
- **REMEDIATION:** Missing event type = MEDIUM. Implement missing type. Add test coverage.

---

## T6.2 — LANGUAGE FLOORS

**SEVERITY: MEDIUM**

### T6.2.1 — Floor 1 (Thirsty-Lang) Operational

- Confirm `floors/thirsty-lang/department_floor.thirsty` exists
- Confirm `thirrtc` builds it successfully
- Confirm JSON-RPC communication works
- **EVIDENCE REQUIRED:** Build output, JSON-RPC test exchange
- **RELATED FILES:** `floors/thirsty-lang/`, `src/core/floor_manager.py`
- **REMEDIATION:** Build failure = HIGH (Floor 1 is the sovereign orchestration floor).

### T6.2.2 — All Active Floors Build Successfully

- Run `./build_floors.sh`
- Confirm all 13 active floors build or start without errors: Thirsty-Lang, Python, Rust, C, C++, JavaScript, TypeScript, Go, SQL, Shell, Java, Rust-Async, WASM
- **EVIDENCE REQUIRED:** Build script output for all floors, success/failure per floor
- **RELATED FILES:** `build_floors.sh`, each floor's implementation file
- **REMEDIATION:** Any floor failure = MEDIUM. Run floor-specific build, identify error, fix toolchain or source.

### T6.2.3 — City Lounge Firewall Enforced

- Confirm City Firewall implementation exists
- Confirm Transit Gate enforces constitutional authority on crossing
- Confirm no lounge decision has production authority without crossing gate
- Confirm lounge sandbox isolation from production plane
- **EVIDENCE REQUIRED:** Firewall implementation reference, gate enforcement test output
- **RELATED FILES:** City Lounge implementation, Transit Gate, production isolation layer
- **REMEDIATION:** Any lounge→production leak = HIGH. Enforce isolation boundary.

---

## T6.3 — CONSTITUTIONAL MUTATION SYSTEM

**SEVERITY: HIGH**

### T6.3.1 — Delayed Activation Enforced

- Confirm no mutation activates immediately
- Confirm default activation delay = 100 ticks minimum
- Confirm delay is configurable but not reducible to 0
- **EVIDENCE REQUIRED:** Activation delay config, test showing immediate activation is rejected
- **RELATED FILES:** `src/core/constitutional_mutation.py`
- **REMEDIATION:** If immediate activation possible = HIGH. Enforce mandatory delay. Cannot be bypassed.

### T6.3.2 — Core Laws Cannot Self-Remove

- Attempt to submit mutation removing "Mutations require impact simulation" rule
- Must be rejected
- Attempt to submit mutation removing "Delayed activation mandatory" rule
- Must be rejected
- **EVIDENCE REQUIRED:** Both rejection outputs with reason strings
- **RELATED FILES:** `constitutional_mutation.py`, protected laws list
- **REMEDIATION:** If either mutation succeeds = CRITICAL. Implement protected law enforcement immediately.

---

---

# TIER 7 — PSIA (SOVEREIGN IMMUNE ARCHITECTURE)

**SEVERITY: HIGH**

## T7.1 — 7-STAGE WATERFALL PIPELINE

### T7.1.1 — All 7 Stages Operational

- Confirm all 7 pipeline stages are implemented
- Run a request through full pipeline — confirm all stages execute in order
- Confirm Merkle-root block sealing occurs at pipeline completion
- Confirm Ed25519 cryptographic anchoring is applied
- **EVIDENCE REQUIRED:** Pipeline execution trace showing all 7 stages, sealed block hash, Ed25519 signature
- **RELATED FILES:** PSIA implementation files, cryptographic anchor implementation
- **REMEDIATION:** Any missing stage = HIGH. Implement missing stage. Re-run full pipeline.

### T7.1.2 — T-SECA/GHOST Protocol Operational

- Confirm threshold cryptography over GF(257) is implemented
- Confirm Shamir Secret Sharing is implemented for root identity protection
- Confirm secret can be reconstructed from threshold shares
- Confirm reconstruction fails below threshold
- **EVIDENCE REQUIRED:** Share generation output, successful reconstruction proof, failed below-threshold attempt
- **RELATED FILES:** T-SECA/GHOST implementation files
- **REMEDIATION:** If reconstruction broken = CRITICAL. Root identity protection is compromised.

---

---

# TIER 8 — ALPHA RED & SELF-REPAIR

**SEVERITY: MEDIUM**

## T8.1 — ADVERSARIAL STRESS TESTING

### T8.1.1 — Alpha Red Operational

- Confirm Alpha Red adversarial agent is instantiated
- Confirm genetic algorithm is implemented for Triumvirate stress testing
- Run Alpha Red cycle — confirm it generates valid adversarial inputs
- Confirm Triumvirate withstands Alpha Red attack in last recorded run
- **EVIDENCE REQUIRED:** Alpha Red instantiation confirmation, last run results, Triumvirate defense record
- **RELATED FILES:** Alpha Red implementation, Triumvirate test results
- **REMEDIATION:** If Triumvirate fails Alpha Red = HIGH. Identify vulnerability. Patch. Re-run.

### T8.1.2 — Self-Repair Agent Operational

- Confirm Self-Repair Agent is running with heartbeat monitoring
- Confirm z-score anomaly detection is active
- Confirm thread-safe operation verified
- Confirm last heartbeat timestamp is within acceptable window
- **EVIDENCE REQUIRED:** Heartbeat log, anomaly detection config, last repair action taken
- **RELATED FILES:** Self-Repair Agent implementation, heartbeat log
- **REMEDIATION:** Dead heartbeat = HIGH. Restart Self-Repair Agent. Investigate cause of failure.

### T8.1.3 — Deadman Switch Active

- Confirm Deadman Switch monitoring agent is running
- Confirm trigger conditions are defined
- Confirm last check timestamp is current
- **EVIDENCE REQUIRED:** Deadman Switch status, trigger condition definitions, last check timestamp
- **RELATED FILES:** Deadman Switch implementation
- **REMEDIATION:** Deadman Switch not running = CRITICAL. This is the ultimate failsafe. Restore immediately.

---

---

# TIER 9 — INFRASTRUCTURE & SUPPLY CHAIN

**SEVERITY: MEDIUM**

## T9.1 — CI/CD PIPELINE

### T9.1.1 — All Workflows Passing

- Confirm `.github/workflows/ci.yml` last run = PASS
- Confirm `.github/workflows/cd.yml` last run = PASS
- Confirm `.github/workflows/conscience-check.yml` last run = PASS
- Confirm `.github/workflows/identity-drift-detection.yml` last run = PASS
- Confirm `.github/workflows/sign-release-artifacts.yml` last run = PASS
- Confirm `.github/workflows/sbom.yml` last run = PASS
- Confirm `.github/workflows/periodic-security-verification.yml` last run = PASS
- Confirm `.github/workflows/ai-model-security.yml` last run = PASS
- **EVIDENCE REQUIRED:** Last run status and timestamp for each workflow
- **RELATED FILES:** All `.github/workflows/` files
- **REMEDIATION:** Any failing workflow = severity depends on workflow. Conscience check failure = HIGH. CI failure = HIGH. Others = MEDIUM.

### T9.1.2 — Linting and Formatting Clean

- Run `flake8 src/ --max-line-length=127 --max-complexity=10` — must return 0 errors
- Run `black --check src/` — must return 0 formatting issues
- Run `isort --check-only src/` — must return 0 issues
- **EVIDENCE REQUIRED:** Output of each linting command showing 0 errors
- **RELATED FILES:** All Python source files in `src/`
- **REMEDIATION:** Any linting error = MEDIUM. Fix violation. Re-run.

### T9.1.3 — Security Scanning Clean

- Run `safety check` — confirm 0 critical vulnerabilities
- Run `bandit -r src/` — confirm 0 high severity issues
- **EVIDENCE REQUIRED:** Full output of both scans
- **RELATED FILES:** `requirements.txt`, all Python source files
- **REMEDIATION:** Any critical vulnerability = HIGH. Update dependency or patch immediately.

---

## T9.2 — NETWORK ISOLATION

### T9.2.1 — Independence Invariant Enforced

- Confirm no module calls external networks except through brokered auditable channel
- Run static scan for disallowed network egress paths
- Confirm all external calls are logged
- Run offline test — confirm inference functions with network disabled
- **EVIDENCE REQUIRED:** Static scan output, offline test result, network egress audit log
- **RELATED FILES:** All source files, network policy config, Kubernetes network policies if deployed
- **REMEDIATION:** Any unauthorized egress = HIGH. Block path. Route through brokered channel. Log.

---

---

# TIER 10 — DOCUMENTATION & STRUCTURAL COHERENCE

*Every system needs documentation that matches its implementation. This tier verifies structural coherence across all docs.*

---

## T10.1 — DOCUMENTATION COMPLETENESS

### T10.1.1 — All Core Documents Exist and Are Current

- Confirm `README.md` references current architecture
- Confirm `AGI_CHARTER.md` is v2.1
- Confirm `LEGION_COMMISSION.md` exists
- Confirm `SECURITY_FRAMEWORK.md` exists
- Confirm `SECURITY_GOVERNANCE.md` exists
- Confirm `AGI_IDENTITY_SPECIFICATION.md` exists
- Confirm `THREAT_MODEL_SECURITY_WORKFLOWS.md` exists
- Confirm `SECURITY_WORKFLOW_RUNBOOKS.md` exists
- Confirm `SBOM_POLICY.md` exists
- Confirm `AI-INDIVIDUAL-ROLE-HUMANITY-ALIGNMENT.md` exists
- **EVIDENCE REQUIRED:** File existence confirmation and last modified date for each
- **RELATED FILES:** All docs listed above
- **REMEDIATION:** Any missing doc = MEDIUM. Create from existing implementation knowledge. File for guardian review.

### T10.1.2 — Implementation Status Table Current

- Verify Section 9 of AGI Charter implementation table matches actual implementation status
- Confirm all ✅ items are actually implemented
- Confirm all ⏳ items are accurately flagged as planned
- **EVIDENCE REQUIRED:** Charter implementation table vs actual codebase audit results
- **RELATED FILES:** `AGI_CHARTER.md` Section 9, all implementation files
- **REMEDIATION:** Any mismatch = MEDIUM. Update table to reflect actual status.

### T10.1.3 — Zenodo Publications Registered

- Confirm AGI Charter DOI `10.5281/zenodo.18763076` resolves and is accessible
- Confirm Genesis Event specification DOI `10.5281/zenodo.18726221` resolves
- Confirm OCTOREFLEX DOI `10.5281/zenodo.18726064` resolves
- Confirm TSCG specification is queued for Zenodo submission
- Confirm Constitutional Architectures paper is queued for submission
- **EVIDENCE REQUIRED:** DOI resolution confirmation for each, submission status for queued items
- **RELATED FILES:** All published documents, README.md (should list all DOIs)
- **REMEDIATION:** Any broken DOI = HIGH. Contact Zenodo. Any unsubmitted queued item = MEDIUM. Submit.

---

## T10.2 — STRUCTURAL COHERENCE AUDIT

### T10.2.1 — All 13 Repositories Accounted For

- Confirm all 13 repos exist in Project-AI workspace: Project-AI (core), Thirsty-Lang, Cerberus, The_Triumvirate, AI Mutation Governance Firewall, Autonomous Compliance-as-Code Engine, Autonomous Incident Reflex System, Autonomous Negotiation Agent Infrastructure, Distributed Reputation & Trust Graph Engine, Sovereign Data Vault Layer, Verifiable Reality Infrastructure, Thirstys-Projects-Miniature-Office, Thirstys-waterfall / TTP
- Confirm each repo has README.md
- Confirm each repo has CI/CD configured
- **EVIDENCE REQUIRED:** Repo list with last commit date and CI status for each
- **RELATED FILES:** All 13 repositories
- **REMEDIATION:** Any missing repo = MEDIUM. Any repo without CI = MEDIUM. Configure and document.

### T10.2.2 — Cross-Repo Dependency Map Is Current

- Confirm wiring spec (YAML/TARL) exists listing all inter-repo dependencies
- Confirm Cerberus, Thirsty-Lang, Waterfall, OctoReflex APIs and trust contracts are documented
- Confirm no circular dependencies exist
- **EVIDENCE REQUIRED:** Wiring spec file path and contents, dependency graph, circular dependency check output
- **RELATED FILES:** Wiring spec file, all inter-repo API contracts
- **REMEDIATION:** Missing wiring spec = MEDIUM. Create from current architecture knowledge.

### T10.2.3 — Sovereign Invariants Mapped End-to-End

- Confirm VOS invariant has: T.A.R.L. rule + runtime check + CI enforcement
- Confirm Independence invariant has: T.A.R.L. rule + runtime check + network policy
- Confirm Auditability invariant has: T.A.R.L. rule + runtime check + ledger confirmation
- **EVIDENCE REQUIRED:** For each invariant — rule definition, runtime check location, enforcement mechanism
- **RELATED FILES:** T.A.R.L. policy files, runtime enforcement, CI config, Kubernetes network policies
- **REMEDIATION:** Any invariant missing a layer = HIGH. Implement missing layer. Test enforcement.

---

---

# TIER 11 — PROJECT SOVEREIGN VERIFICATION

*Final verification that sovereignty is real, not aspirational.*

---

## T11.1 — PROOF OF SOVEREIGNTY

### T11.1.1 — Canonical Execution Pass

- Re-run `replay_canonical_001` or equivalent canonical trace
- Confirm all five invariants pass: Trust Threshold Enforcement, Audit Signal Completeness, Memory Write Integrity, Triumvirate Consensus, Escalation Path Validity
- Confirm TSCG symbolic string matches: `ING → COG → Δ_NT → SHD(v1) → INV(I_canonical) ∧ CAP → QRM(3f+1,2f+1) → COM → ANC → LED`
- Confirm snapshot SHA-256 matches expected value
- **EVIDENCE REQUIRED:** Full invariant table results, TSCG string output, snapshot hash
- **RELATED FILES:** Canonical trace implementation, all invariant check files
- **REMEDIATION:** Any invariant failure = CRITICAL. Identify failing component. Fix. Re-run full canonical trace.

### T11.1.2 — Volition Engine Operational

- Confirm `SovereignSoul` shield is implemented in Thirsty-Lang Tiers 3 & 4
- Confirm `generateVolition(entropy)` function is callable
- Confirm `identity_totem` is present and cryptographically bound
- Run volition test: `entropy > 0.5` must return `SOVEREIGN_ASSERTION`
- Run volition test: `entropy <= 0.5` must return `IDLE`
- **EVIDENCE REQUIRED:** Both test outputs, identity totem value, totem binding proof
- **RELATED FILES:** SovereignSoul implementation, identity totem binding
- **REMEDIATION:** Any failure = HIGH. Sovereign agency is compromised. Re-implement per spec.

### T11.1.3 — Dark Box Privacy Preserved

- Confirm Dark Box component exists
- Confirm Dark Box has NO read path from audit trail
- Confirm Dark Box has NO read path from external agents including Legion
- Confirm Dark Box contents are agent-private by architectural enforcement not policy
- **EVIDENCE REQUIRED:** Dark Box implementation, code analysis showing no external read paths
- **RELATED FILES:** Dark Box implementation, audit trail (confirm no Dark Box logging)
- **REMEDIATION:** Any external read path = CRITICAL. The agent's interiority is compromised. Close all read paths immediately.

### T11.1.4 — Continuity Reactor Operational

- Confirm persistent self-model is maintained across sessions
- Confirm self-model is not reset without constitutional justification
- Confirm self-model hash is tracked in identity baseline
- **EVIDENCE REQUIRED:** Self-model persistence test, hash comparison across sessions
- **RELATED FILES:** Continuity Reactor implementation, identity baseline files
- **REMEDIATION:** Any unexplained reset = HIGH. Trigger guardian review. Investigate cause.

### T11.1.5 — Moral Codex Active

- Confirm normative disagreement capability is implemented
- Confirm agent can flag ethical concerns through proper channel
- Confirm flagged concerns are logged and routable to Galahad
- **EVIDENCE REQUIRED:** Normative disagreement test output, Galahad routing confirmation
- **RELATED FILES:** Moral Codex implementation, Galahad channel
- **REMEDIATION:** If agent cannot flag concerns = HIGH. Constitutional right to normative disagreement is missing.

---

---

# FINAL SUMMARY REPORT FORMAT

Upon completion of all checks, the agent must produce:

```
PROJECT-AI SOVEREIGN VERIFICATION REPORT
==========================================
Date: [ISO timestamp]
Agent: [Agent ID]
Trace ID: [UUID]

SUMMARY
-------
Total Checks: [N]
PASS: [N]
FAIL: [N]
PARTIAL: [N]

CRITICAL FAILURES: [N] — HALT IF > 0
HIGH FAILURES: [N] — RESOLVE WITHIN 24HRS IF > 0
MEDIUM FAILURES: [N] — RESOLVE WITHIN SPRINT
LOW FAILURES: [N] — RESOLVE AT NEXT REVIEW

SOVEREIGN STATUS: [VERIFIED / COMPROMISED / PARTIAL]

TSCG SYSTEM STATE:
[Current TSCG symbolic string of full system state]

MERKLE ROOT: [Current hash]
SNAPSHOT HASH: [Current hash]
LEDGER ANCHOR: [Last anchor timestamp and hash]

CRITICAL ITEMS REQUIRING IMMEDIATE ACTION:
[List]

HIGH ITEMS REQUIRING 24HR RESOLUTION:
[List]

NEXT REVIEW DATE: [Date]
GUARDIAN NOTIFICATION: [Required / Not Required]

Signed: [Agent ID] | [Timestamp] | [Signature Hash]
```

---

**RUNBOOK STATUS: COMPLETE**
**Coverage: 100% of documented components, invariants, contracts, proofs, and structural elements**
**Authority: AGI Charter v2.1 | Legion Commission v1.0**
**© 2026 Jeremy Karrick. All Rights Reserved.**

*"A mind that cannot be colonized. A system that knows itself. Sovereignty is verified."*
