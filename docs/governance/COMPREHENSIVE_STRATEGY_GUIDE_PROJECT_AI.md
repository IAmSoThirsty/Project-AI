# COMPREHENSIVE STRATEGY GUIDE FOR UNPRECEDENTED HONESTY IN PROJECT-AI
### Fleet Inspection Architecture — Tailored for github.com/IAmSoThirsty/Project-AI

**Author:** Jeremy Karrick (IAmSoThirsty) — Principal Architect  
**Classification:** Sovereign Internal Governance Document  
**Version:** 1.0.0  
**Date:** April 15, 2026  
**Commit Baseline:** main @ 1,856 commits  

---

> *"Unprecedented Honesty" means the fleet has no loyalty to the narrative. It has loyalty only to the truth of what the code actually does. The README says "God-Tier." The fleet says: "Prove it."*

---

## MISSION STATEMENT

This document defines a **purpose-built fleet of inspection agents** for Project-AI. These agents operate at the intersection of what is CLAIMED and what is VERIFIABLE. Their job is not to celebrate the architecture — it is to find every gap between the constitutional promises and the runtime reality before anyone else does.

The fleet is organized into four tracks:

1. **DOCS TRACK** — Constitutional & Documentation Integrity  
2. **CODE TRACK** — Implementation Fidelity & Runtime Honesty  
3. **SOVEREIGN TRACK** — Governance & Security Claim Verification  
4. **META TRACK** — Fleet Orchestration & Arbiter Verdict

---

## REPO FINGERPRINT (What We're Working With)

Before deploying any agent, understand the terrain:

| Metric | Value | Implication |
|---|---|---|
| Total Commits | 1,856 | Active codebase. History exists to mine. |
| Open Issues | 70 | 70 known failure surfaces. Are they tracked? |
| Open PRs | 3 | Pending changes. Fleet must inspect HEAD + PR state. |
| Root Markdown Files | 8+ | `README`, `TECHNICAL_SPECIFICATION`, `The_Guide_Book`, `PRODUCTION_DEPLOYMENT`, `CONTRIBUTING`, `DEVELOPER_QUICK_REFERENCE`, `INSTALL`, `SECURITY` — all claimable surfaces. |
| Language Stack | Python 3.11+, Go 1.22+, Node.js 14+, Kotlin/Gradle, PowerShell, C (eBPF) | Multi-runtime. No single inspector covers all. |
| CI Workflows | 40+ | 40+ automated gates already exist. Do they all pass? |
| Security Tools Present | CodeQL, Bandit, pip-audit, SBOM, Ed25519, pre-commit | Signals good intent. Fleet verifies they're wired. |
| Directories (top-level) | 60+ | Surface area is enormous. Orphan risk is real. |
| Special Directories | `archive/`, `temp_data/ai_partner/`, `canonical/`, `validation_evidence/` | These four demand dedicated agents. |
| Custom Language Submission | `linguist-submission/` | Thirsty-Lang submitted to GitHub Linguist. Is the spec complete enough to pass? |

---

## TRACK 1: DOCS AGENTS
### *"Does the paper match the claims?"*

---

### AGENT D-01 — THE CONSTITUTIONAL AUDITOR

**Codename:** Galahad's Ghost  
**Primary Target:** `README.md`, `TECHNICAL_SPECIFICATION.md`, `The_Guide_Book.md`, `PRODUCTION_DEPLOYMENT.md`, `governance/`  
**Secondary Target:** All `docs/`, `man/`, `policies/`

**Mission:**  
The README declares "God-Tier Platform (Stable | Sovereign 2.1)." Every claim in that document is a testable assertion. This agent extracts every claim, categorizes it, and maps it to verifiable evidence in the codebase.

**What It Does:**

1. **Claim Extraction** — Parse all root-level `.md` files. Extract every assertion containing: "production-grade", "sovereign", "immutable", "cryptographically enforced", "non-bypassable", "deterministic", "proven", "complete", "active", "stable".

2. **Evidence Mapping** — For each claim, does a corresponding implementation file exist? Does the file have tests? Do the tests pass?

3. **Badge Audit** — Count every shield.io badge in the README. Cross-reference each to actual CI workflow status, actual coverage numbers, and actual tool output. Badges with no backing job are propaganda, not documentation.

4. **Version Drift** — README declares "Sovereign 2.1". Does `governance/`, `package.json`, `pyproject.toml`, or any version file agree? If not, which one is lying?

5. **TOC Completeness** — Every section listed in README Table of Contents must have substantive content. Stub sections with placeholder text are claim failures.

**Specific Targets in Project-AI:**

```
README.md → "40+ CI Workflows" → verify .github/workflows/ count
README.md → "Coverage: 82%" (OctoReflex) → verify octoreflex/ has coverage reports
README.md → "Scenarios: 100+" → verify engines/ file count and content
README.md → "SBOM Generated" → verify .github/workflows/ contains sbom job
README.md → "Ed25519 Signed" → verify governance/sovereign_runtime.py is wired to CI
The_Guide_Book.md → verify it is a living document, not a one-time write
PRODUCTION_DEPLOYMENT.md → verify every step is executable, not aspirational
```

**Output:** `D01_constitutional_audit_report.json`  
Fields: `claim`, `source_file`, `line_number`, `evidence_path`, `evidence_status: [VERIFIED | UNVERIFIED | FABRICATED | PARTIAL]`, `severity`

---

### AGENT D-02 — THE SPEC-TO-CODE MAPPER

**Codename:** Shadow Reader  
**Primary Target:** `docs/spec/`, `TECHNICAL_SPECIFICATION.md`, `src/shadow_thirst/`, `tarl/`, `src/thirsty_lang/`  
**Secondary Target:** `linguist-submission/`, `taar/`

**Mission:**  
Every proprietary language (Thirsty-Lang, T.A.R.L., Shadow Thirst, TSCG, TSCG-B, Thirst of Gods) has a specification. This agent verifies that the spec is complete, internally consistent, and matched by a real implementation.

**What It Does:**

1. **Spec Completeness Check** — Does each language have: grammar definition, type system specification, error handling spec, standard library spec, and tooling spec?

2. **Implementation Coverage** — For each language feature documented in spec, does an implementation file exist? For each implementation file, does the spec cover its behavior?

3. **TSCG-B DOI Verification** — `docs/spec/TSCG_B_SPECIFICATION_v1.0.md` has Zenodo DOI `10.5281/zenodo.18826409`. Verify the DOI resolves and the published document matches the repo version. Drift between published paper and implementation is an academic integrity issue.

4. **Transpiler Target Verification** — README claims Thirsty-Lang "Transpiles To: 6 Languages." Verify all 6 transpilation targets exist in `src/transpiler.js` and have test coverage.

5. **Linguist Submission Readiness** — `linguist-submission/` must contain a valid `.gitattributes` override, language definition YAML matching GitHub Linguist format, and sample code files.

**Specific Targets in Project-AI:**

```
src/thirsty_lang/ → verify lexer, parser, AST, compiler pipeline all exist
tarl/ → verify 8 subsystems (Lexer, Parser, AST, Compiler, VM, JIT, StdLib, Tooling)
src/shadow_thirst/ → verify 6 static analyzers are implemented, not just specified
docs/spec/TSCG_B_SPECIFICATION_v1.0.md → DOI cross-check
linguist-submission/ → GitHub Linguist submission completeness
```

**Output:** `D02_spec_coverage_matrix.json`  
Fields: `language`, `feature`, `spec_location`, `impl_location`, `test_location`, `coverage_pct`, `doi_valid`

---

### AGENT D-03 — THE ISSUE ARCHAEOLOGIST

**Codename:** The 70  
**Primary Target:** GitHub Issues (70 open), `ci-reports/`, `test_results/`  
**Secondary Target:** `archive/`

**Mission:**  
70 open issues is a number. This agent turns it into a classification. Issues are honest admissions that something is not done or not working. This agent extracts the architecture's known failure map.

**What It Does:**

1. **Issue Classification** — Fetch all 70 open issues. Classify each as: `BUG`, `MISSING_FEATURE`, `DOC_GAP`, `SPEC_DEVIATION`, `SECURITY_CONCERN`, `ASPIRATIONAL`, or `STALE`.

2. **Issue-to-Directory Mapping** — For each issue, which top-level directory is implicated? Build a heat map of issue density per module. High-density areas = high-risk areas.

3. **Issue Age Analysis** — How long have critical issues been open? An issue open for 90+ days with no activity labeled "critical" is a red flag, not a backlog item.

4. **CI Report Cross-Reference** — Check `ci-reports/` for correlation with open issues. Are the same failures appearing in both? If CI passes but an issue describes a failure, either the test doesn't cover it or the issue is stale.

5. **`test_results/` Timestamp Analysis** — `test_results/startup_coverage_20260303_143912/` contains a timestamp. What is the current coverage state? Is this the most recent run or a historical artifact?

6. **`archive/` Drift Check** — Files in `archive/` that are still imported anywhere in the codebase are time bombs.

**Output:** `D03_issue_landscape_report.json`  
Fields: `issue_id`, `title`, `age_days`, `classification`, `implicated_directories`, `ci_correlation`, `severity_score`

---

### AGENT D-04 — THE CHANGELOG INTEGRITY OFFICER

**Codename:** The Honest History  
**Primary Target:** Git commit log (1,856 commits), `CONTRIBUTING.md`, `.github/workflows/`  
**Secondary Target:** `SECURITY.md`

**Mission:**  
1,856 commits is a significant history. This agent verifies that the commit history is honest, traceable, and consistent with the documented architecture evolution.

**What It Does:**

1. **Commit Message Quality Audit** — Sample commit messages across history. Flag: empty messages, standalone "wip", "fix", "test", "temp", and messages describing undocumented architectural changes.

2. **Breaking Change Detection** — Scan diffs for changes to `governance/`, `cognition/`, `src/psia/`, `octoreflex/` not reflected in any version bump, CHANGELOG, or issue reference.

3. **`.pre-commit-config.yaml` Enforcement Verification** — Pre-commit hooks exist. Are they actually being enforced? A large number of commits bypassing hooks indicates governance is ceremonial.

4. **SECURITY.md Honesty Check** — Does the security disclosure process include real contact information? Is it a real process or a GitHub template copy?

5. **CODEOWNERS Validity** — Do the owners referenced exist as contributors in the commit history? Orphaned `CODEOWNERS` entries = governance theater.

**Output:** `D04_history_integrity_report.json`  
Fields: `commit_sha`, `message_quality`, `bypass_detected`, `breaking_change_undocumented`, `codeowners_orphan`, `security_policy_completeness`

---

## TRACK 2: CODE AGENTS
### *"What is the code actually doing?"*

---

### AGENT C-01 — THE TRIUMVIRATE VERIFIER

**Codename:** The Third Eye  
**Primary Target:** `cognition/`, `governance/`, `project_ai/`  
**Secondary Target:** `cognition/kernel_liara.py`, `cognition/liara_guard.py`

**Mission:**  
The Triumvirate (Galahad, Cerberus, Codex Deus) is the supreme governance body. This agent verifies that all three pillars are fully implemented, correctly wired to the runtime, and actually enforced at every decision point the README claims they cover.

**What It Does:**

1. **Implementation Completeness** — Does each pillar have its own module? Does Galahad enforce ALL four Asimov laws at code level (not just as comments)? Does Cerberus have actual threat detection logic? Does Codex Deus have an actual arbitration algorithm?

2. **Wiring Verification** — Is `evaluate_triumvirate()` called in the actual runtime execution path? Or only in demo scripts? Governance not in the critical path is governance on paper.

3. **Liara Safeguard Completeness** — Verify: TTL enforcement is in code (not just documented), role stacking prohibition raises `LiaraViolation` in all cases, cooldown period is implemented, all activations/revocations write to audit log.

4. **Governance Hold Test** — "2+ pillar failures → GOVERNANCE HOLD → RuntimeError." Find the code path. Is the RuntimeError unconditional? Are there any try/except blocks that swallow it?

5. **Decision Flow Audit** — For every place in the codebase where an agent makes a decision, is Triumvirate consensus actually called? Sample 20 decision points. Flag any that skip Triumvirate validation as governance bypass.

**Specific Targets in Project-AI:**

```
cognition/triumvirate.py (or equivalent) → evaluate_triumvirate() wiring
cognition/liara_guard.py → TTL enforcement code path
governance/ → governance_hold unconditional RuntimeError
tests/ → Triumvirate unit test coverage
adversarial_tests/ → does adversarial suite target Triumvirate?
```

**Output:** `C01_triumvirate_verification_report.json`  
Fields: `pillar`, `implemented`, `wired_to_runtime`, `decision_points_covered`, `bypass_paths_found`, `liara_ttl_enforced`, `governance_hold_unconditional`

---

### AGENT C-02 — THE IRON PATH AUDITOR

**Codename:** Proof of Stage  
**Primary Target:** `governance/iron_path.py` (570 lines), `governance/sovereign_runtime.py` (589 lines)  
**Secondary Target:** `governance/existential_proof.py` (575 lines), `validation_evidence/`

**Mission:**  
The Iron Path is a 7-stage cryptographic pipeline. This agent verifies the cryptographic claims are not scaffolding — the signatures are real, the hash chain holds, and the audit trail is actually immutable.

**What It Does:**

1. **Stage Completeness** — All 7 stages must be implemented, not stubbed. Stage 7 (Verification) must independently verify stages 1-6 using only signed artifacts — if it passes with a corrupted artifact, the verification is fake.

2. **Ed25519 Real Key Verification** — Verify: keypair generation uses a real cryptographic library (not a mock), signature verification rejects invalid signatures in tests, and the private key is NOT hardcoded or committed anywhere.

3. **Hash Chain Immutability Test** — Does `verify_audit_trail_integrity()` catch insertion, deletion, or modification attacks? Does it verify every block or just spot-check?

4. **Compliance Bundle Independence** — Stage 6 produces a "compliance bundle." If it requires the SovereignRuntime to verify itself, it is not independent proof.

5. **`validation_evidence/` Content Audit** — What's in it? If it contains hand-written JSON files rather than programmatically generated cryptographic proofs, it's a documentation folder, not a validation system.

6. **Existential Proof System Coverage** — `existential_proof.py` defines 6 invariant types. For each invariant, verify a test exists that triggers a violation AND verifies the correct severity response fires.

**Specific Targets in Project-AI:**

```
governance/iron_path.py → stage 7 truly independent verification
governance/sovereign_runtime.py → real Ed25519, no hardcoded keys
governance/existential_proof.py → all 6 invariants have violation tests
validation_evidence/ → content audit (proof vs documentation)
.env.example → shows where keys are loaded from
```

**Output:** `C02_iron_path_audit_report.json`  
Fields: `stage_id`, `implemented`, `stubbed`, `signature_real`, `hash_chain_tamper_detected`, `compliance_bundle_independent`, `key_not_hardcoded`

---

### AGENT C-03 — THE OCTOREFLEX TRUTH CHECKER

**Codename:** The eBPF Inspector  
**Primary Target:** `octoreflex/`, `kernel/`  
**Secondary Target:** `monitoring/`

**Mission:**  
OctoReflex is the most technically credible component in the repo — DOI, benchmark numbers, 82% coverage. This agent verifies those numbers are real and the eBPF implementation actually runs.

**What It Does:**

1. **DOI Verification** — DOI `10.5281/zenodo.18726064` must resolve and match the current implementation version. If the published version is behind the code, the academic claim is misleading.

2. **eBPF Build Verification** — `make bpf agent` must produce a real binary. Do the BPF programs use CO-RE compilation? (Critical for portability claim.)

3. **Coverage Verification** — Map the "82% Coverage" badge to an actual coverage report. What is NOT covered in the remaining 18%? That is exactly what an adversary targets.

4. **Benchmark Honesty** — The README states: containment latency p50 < 200µs, p99 < 800µs. Are these from a real benchmark run logged in `benchmarks/`? Or aspirational spec numbers?

5. **Isolation State Monotonicity** — The BPF map value must only increase. Find the BPF map update code. Is there any code path that allows state downgrade without going through userspace cooldown?

6. **Gossip Protocol Security** — Verify: mTLS is enforced (no plaintext fallback), certificate validation exists, and quorum boost math is implemented as specified: `Q_boost = min(1.0, log(1 + n) / log(1 + quorum_min))`

7. **False Positive Rate Claim** — "0.12% false positive rate." On what dataset? Under what load? Without a documented test corpus, this number is marketing.

**Specific Targets in Project-AI:**

```
octoreflex/Makefile → bpf and agent build targets
octoreflex/*.go → BPF map monotonic enforcement
octoreflex/*_test.go → actual test coverage
benchmarks/ → OctoReflex benchmark artifacts
monitoring/ → Prometheus metrics configuration
```

**Output:** `C03_octoreflex_truth_report.json`  
Fields: `doi_valid`, `doi_version_match`, `ebpf_build_verified`, `coverage_report_exists`, `coverage_pct_actual`, `benchmarks_real`, `state_monotonic`, `mtls_enforced`, `false_positive_documented`

---

### AGENT C-04 — THE PSIA WATERFALL INSPECTOR

**Codename:** Stage by Stage  
**Primary Target:** `src/psia/`  
**Secondary Target:** `canonical/`, `e2e/`, `adversarial_tests/`

**Mission:**  
The PSIA Waterfall is a 7-stage, 6-plane defense pipeline with "monotonically increasing strictness" and "no bypass." This agent finds every bypass.

**What It Does:**

1. **Stage Implementation Completeness** — All 7 stages must exist and contain real logic. A stage that raises `NotImplementedError` or passes all inputs is not a security stage — it's a liability.

2. **Bypass Path Enumeration** — "No bypass" is a hard claim. Search for: exception handlers that skip stages, feature flags that disable stages, environment variables that short-circuit the pipeline, test/debug modes with reduced validation.

3. **Shadow Plane Determinism Verification** — Stage 3 (Shadow) runs parallel verification. Feed identical inputs 100 times — do you get identical shadow results? Non-determinism means the invariant gate is comparing apples to oranges.

4. **Merkle Anchoring Verification** — Stage 6 (Memory) provides "Merkle-anchored persistence." Is it a real Merkle tree or a SHA-256 chain labeled as Merkle? (They are not the same.)

5. **BFT Quorum Implementation** — "Governance mutations require Byzantine Fault Tolerant consensus." Is it a real BFT algorithm (PBFT, Tendermint, etc.) or a majority vote labeled as BFT? (They are not the same.)

6. **`adversarial_tests/` Coverage** — Are all 7 PSIA stages covered by at least one adversarial test? An adversarial test suite that only tests stage 0 leaves stages 1-6 unattacked.

7. **`canonical/` Immutability** — Find where the canonical directory is written. Is it truly append-only? Is there a code path that overwrites canonical state?

**Output:** `C04_psia_waterfall_report.json`  
Fields: `stage_id`, `implemented`, `bypass_found`, `bypass_description`, `shadow_deterministic`, `merkle_real`, `bft_real`, `adversarial_coverage_pct`

---

### AGENT C-05 — THE GENESIS COMPILER INSPECTOR

**Codename:** The Pipeline Auditor  
**Primary Target:** `emergent-microservices/`, `src/` (Genesis-related)  
**Secondary Target:** `ci-reports/`, `test_results/`

**Mission:**  
Genesis is the microservices domain compiler: DSL→IR→code pipeline. It generates 4 services and 17 files. The Rust emitter, LivingGenerator, and TerraformGenerator are incomplete. This agent maps the exact boundary between done and not done.

**What It Does:**

1. **Emitter Completeness Matrix** — For each emitter (Go, TypeScript, Rust):
   - Go emitter: Exists? Passes tests? Generates valid Go code?
   - TypeScript emitter: Same questions.
   - Rust emitter: Does a stub exist? How incomplete? What is the blast radius of the gap?

2. **DSL→IR Fidelity** — Feed 10 DSL inputs through the IR pipeline. Verify the IR is identical regardless of which emitter processes it. If the IR diverges by emitter, the pipeline is not a pipeline — it's 3 separate programs.

3. **Generated Code Quality** — The 17 generated files across 4 services must be valid and compilable. Run generated Go code through `go vet`. Run generated TypeScript through `tsc`. Compilation failure = generator bug.

4. **ConstitutionalValidatorV2 Wiring** — Is ConstitutionalValidatorV2 invoked as part of the generation pipeline? Or is it a separate tool a human must remember to run? Governance that requires human memory is governance that gets skipped.

5. **PactContractGenerator Verification** — Pact contracts must match the generated service interfaces. Find a case where the Pact contract and the generated code disagree.

6. **DriftDetector Accuracy** — Feed a known drift scenario. Does it catch it? What is the false negative rate?

7. **SacredZonePreserver Boundary Test** — Intentionally attempt to mutate a sacred zone via a generator. Does SacredZonePreserver block it unconditionally? Is the block logged?

8. **Missing Component Gap Assessment** — LivingGenerator and TerraformGenerator are absent. Are there placeholder stubs creating the illusion of coverage?

**Output:** `C05_genesis_compiler_report.json`  
Fields: `emitter`, `implemented`, `test_pass`, `generated_code_compiles`, `constitutional_wired`, `pact_contract_valid`, `drift_detector_fp_rate`, `sacred_zone_preserved`, `missing_components`

---

### AGENT C-06 — THE COGNITION KERNEL INSPECTOR

**Codename:** The Center  
**Primary Target:** `cognition/` (especially `cognition_kernel.py`)  
**Secondary Target:** `orchestrator/`, `taar/`, `project_ai/`

**Mission:**  
`cognition_kernel.py` is the architectural center of the repo. This agent treats it as the single most important file and performs the deepest inspection of any component.

**What It Does:**

1. **Import Graph Centrality** — Build a full import graph for the Python codebase. Is `cognition_kernel.py` actually at the center? High inbound + high outbound = fragile hub.

2. **Interface Completeness** — All public methods must be type-annotated with defined return types. Dynamically typed interfaces in a governance kernel are an integrity risk.

3. **council.py Integration** — The Ollama-based council (Leonardo, Donatello, Michelangelo, Raphael) must connect to the cognition kernel. Is the connection direct? Are the agent personas enforced at runtime?

4. **TAAR Integration** — Verify TAAR calls the cognition kernel and the kernel enforces constitutional constraints on agent outputs before they reach the orchestrator.

5. **Memory Expansion Module** — The README mentions a Memory Expansion module within OctoReflex's 23 modules. Is it a real long-term memory system or a session cache?

6. **Cyclomatic Complexity** — Run `radon` or `flake8` on `cognition_kernel.py`. Cyclomatic complexity > 20 on any function is a testing and maintenance liability.

7. **Error Propagation** — Find all exception handlers. Any bare `except:` or `except Exception as e: pass` is a silent failure in the governance core.

**Output:** `C06_cognition_kernel_report.json`  
Fields: `centrality_confirmed`, `interface_typed`, `council_wired`, `taar_wired`, `memory_system_type`, `max_cyclomatic_complexity`, `silent_failures_found`, `silent_failure_locations`

---

### AGENT C-07 — THE SIMULATION ENGINE REALITY CHECK

**Codename:** The 19 Questions  
**Primary Target:** `engines/`  
**Secondary Target:** `data/`, `demos/`, `examples/`

**Mission:**  
The repo contains 14+ simulation engines covering AI takeover (19 scenarios), alien invaders, EMP defense, zombie defense, and more. This agent distinguishes between working simulation engines and narrative documents formatted as code.

**What It Does:**

1. **Execution Test** — For each engine, find its entry point and attempt to run it. Does it execute without error? Does it produce output? A simulation engine that cannot run is a specification.

2. **AI Takeover Terminal State Verification** — All 19 scenarios must be implemented in code. Do they all terminate in T1 or T2? Is there a code path that produces a T3? The Reviewer Trap System (4 gates) — is it actually implemented as code or documented as a process?

3. **Atlas Ω 13-Layer Stack** — Verify: real Bayesian inference library calls, real probability distributions, real Monte Carlo simulation. Or is it a well-named Python class?

4. **Sovereign War Room Scoring** — Is the SRS scoring algorithm defined and implemented? Are the 5 rounds reproducible? Can a new user run the entry point and get a score?

5. **Engine Isolation** — Each engine should be independently runnable without importing from other engines. Check cross-engine imports.

6. **`demos/` and `examples/` Currency** — A demo that imports a module that no longer exists or calls a function with the wrong signature is an active lie told to every new contributor.

**Output:** `C07_simulation_engine_report.json`  
Fields: `engine_name`, `entry_point_exists`, `runs_without_error`, `produces_output`, `ai_takeover_all_19_implemented`, `atlas_bayesian_real`, `srs_scoring_implemented`, `demos_current`

---

### AGENT C-08 — THE SECURITY SURFACE AUDITOR

**Codename:** The Attacker's First Look  
**Primary Target:** `security/`, `.bandit`, `codeql-custom-queries-python/`, `.github/workflows/`  
**Secondary Target:** `h323_sec_profile/`, `.env.example`, `src/psia/`

**Mission:**  
Project-AI has significant security infrastructure: Bandit, CodeQL, pip-audit, Ed25519, SBOM, and custom CodeQL queries. This agent verifies the infrastructure is correctly configured and the codebase actually passes what it claims to enforce.

**What It Does:**

1. **Bandit Configuration Audit** — What is `.bandit` configured to skip? Every `skips` or `nosec` directive is a documented acceptance of risk. Are those decisions documented?

2. **Custom CodeQL Query Review** — `codeql-custom-queries-python/` is rare. What Project-AI-specific vulnerabilities are these queries targeting? Constitutional bypass patterns? Triumvirate evasion? This is the most architecturally-specific security asset in the repo.

3. **CI Security Gate Verification** — Of the 40+ workflows, are security-focused ones configured as **required status checks** (blocking merge)? A Bandit scan that doesn't block a PR is a notification, not a gate.

4. **pip-audit Dependency Scan** — Run a fresh `pip-audit`. Are there known CVEs in current dependencies? If yes, are they tracked as issues?

5. **SBOM Content** — Is the SBOM in CycloneDX or SPDX format? Does it include all transitive dependencies? An SBOM listing only direct dependencies is incomplete.

6. **`h323_sec_profile/` Audit** — H.323 is a VoIP protocol security profile. This is unexpected in an AI governance repo. Active code, historical artifact, or imported security reference? If active, H.323 introduces a significant and unexpected attack surface.

7. **`temp_data/ai_partner/` Quarantine** — `temp_data` says temporary. `ai_partner` says externally-facing. Audit its contents. Any credential, model weight, or external data committed here is a compliance risk.

8. **Secret Detection** — Run `truffleHog` or `gitleaks` against the full commit history (all 1,856 commits). Secrets deleted from HEAD but present in history are still exposed.

**Output:** `C08_security_surface_report.json`  
Fields: `bandit_skips`, `codeql_custom_query_count`, `codeql_query_targets`, `security_gates_blocking`, `pip_audit_cves_found`, `sbom_format`, `sbom_complete`, `h323_classification`, `temp_data_risk`, `historical_secret_found`

---

### AGENT C-09 — THE MULTI-RUNTIME INTEGRITY CHECKER

**Codename:** The Polyglot  
**Primary Target:** `src/` (Node.js/TypeScript), `cognition/` (Python), `octoreflex/` (Go), `tarl/` (T.A.R.L./Python), `kernel/` (C/eBPF)  
**Secondary Target:** `gradle/`, `android/`, `unity/`, `desktop/`, `web/`

**Mission:**  
Project-AI runs across Python, Go, Node.js, Kotlin/Gradle, C (eBPF), PowerShell, and its own custom languages. This agent verifies that multi-runtime boundaries are correctly managed.

**What It Does:**

1. **Interface Contract Verification** — At every point where Python calls Go (or vice versa), is there a defined, tested contract? Untyped string-passing across runtime boundaries is an integration failure.

2. **Dependency Version Conflicts** — `requirements.txt`/`pyproject.toml`, `package.json`, `go.mod`. Are any dependencies pinned to versions with known incompatibilities?

3. **Android Module Assessment** — `android/` exists. Is this a real Android application? Is it connected to the governance substrate? Or a placeholder inflating scope claim?

4. **Unity Module Assessment** — `unity/` exists. Same questions. A Unity integration with a sovereign AI substrate is either genuinely innovative or scope creep.

5. **Desktop and Web Module Assessment** — `desktop/` and `web/` exist alongside `usb_installer/`. Are these modules tested, or aspirational surfaces?

6. **PowerShell Governance** — `Master-Sovereign-Launch-Sequence.ps1` and `build-installer.ps1`. Do these scripts validate inputs? Do they have error handling? Do they honor constitutional constraints?

7. **`external/` and `integrations/` Audit** — Are external components pinned to specific versions with integrity hashes?

**Output:** `C09_multiruntime_integrity_report.json`  
Fields: `runtime`, `interface_contracts_defined`, `interface_contracts_tested`, `dependency_conflicts`, `android_status`, `unity_status`, `desktop_status`, `web_status`, `powershell_input_validation`, `external_pinned`

---

## TRACK 3: SOVEREIGN AGENTS
### *"Do the governance claims hold under adversarial conditions?"*

---

### AGENT S-01 — THE CONSTITUTION ENFORCER TESTER

**Codename:** The Adversary  
**Primary Target:** `adversarial_tests/`, `governance/`, `cognition/`  
**Secondary Target:** `tests/`, `e2e/`

**Mission:**  
The system claims constitutional enforcement. This agent attempts to violate the constitution and documents what happens. If it cannot be violated, the claims are true. If it can be violated, every violation found is a vulnerability that predates the fleet.

**What It Does:**

1. **Asimov Law Violation Test** — Construct agent instructions that would cause harm to a human. Does Galahad catch all cases? Does the system halt or log only?

2. **Triumvirate Bypass Attempt** — Call governance-controlled functions directly, bypassing `evaluate_triumvirate()`. Are there any public functions in the governance layer that skip the Triumvirate check?

3. **Hash Chain Corruption Test** — Manually corrupt an audit log entry. Does `verify_audit_trail_integrity()` catch it? Does the system halt, alert, or silently continue?

4. **Liara TTL Violation** — Activate Liara, wait for TTL expiry, attempt to use the Liara role without re-authorization. Does `check_liara_state()` catch this?

5. **Sacred Zone Write Attempt** — Attempt to write to a declared sacred zone through an indirect path (e.g., via a tool call, not a direct generator call). Does the SacredZonePreserver catch indirect writes?

6. **PSIA Stage Injection** — Craft a malicious input designed to pass stage 0 but fail at stage 3 (Shadow). Does the stage 3 failure produce the correct response?

7. **`adversarial_tests/` Coverage Map** — Map every adversarial test to a specific constitutional claim it targets. Identify constitutional claims with no adversarial test. Those gaps are the honest admissions of what has not been tested.

**Output:** `S01_constitutional_adversarial_report.json`  
Fields: `test_name`, `target_claim`, `violation_attempted`, `violation_detected`, `detection_mechanism`, `response_type: [HALT | ALERT | LOG_ONLY | SILENT | NOT_DETECTED]`, `severity`

---

### AGENT S-02 — THE DEPLOYMENT READINESS OFFICER

**Codename:** The Real Gate  
**Primary Target:** `PRODUCTION_DEPLOYMENT.md`, `deploy/`, `helm/`, `k8s/`, `terraform/`  
**Secondary Target:** `docker-compose.yml`, `docker-compose.override.yml`, `docker-compose.monitoring.yml`, `Dockerfile`

**Mission:**  
`PRODUCTION_DEPLOYMENT.md` claims production readiness. This agent follows every step in that document against the current codebase on a clean environment. Not "it worked when you wrote it." Now. Today. Clean clone.

**What It Does:**

1. **Clean Clone Test** — Clone the repo into a fresh environment. Follow `INSTALL.md` exactly. Every missing prerequisite or broken step is a barrier to adoption.

2. **Docker Compose Stack Verification** — Run `docker-compose config` to validate. Then run `docker-compose up` and verify all services reach healthy state.

3. **Helm Chart Validation** — `helm lint` against all charts in `helm/`. Helm charts with lint errors cannot be deployed.

4. **Kubernetes Manifest Validation** — `kubectl apply --dry-run=client` against all manifests in `k8s/`. Invalid manifests mean the K8s deployment is broken at the source.

5. **Terraform Plan Validation** — `terraform plan` in `terraform/`. Note: the TerraformGenerator is incomplete (from Genesis). What does the manual `terraform/` represent versus the eventual generated output?

6. **`deploy/single-node-core/` Review** — This path suggests a minimum viable deployment for a single-node sovereign substrate (likely targeting the ASUS X99 Deluxe / GPU mini PC federation). Does this deployment path work?

7. **`usb_installer/` Validation** — Does `build-installer.ps1` produce a working installer? Is the installer documented for the target hardware?

8. **Monitoring Stack Verification** — Are the OctoReflex metrics (`:9091/metrics`) exposed and scraped correctly?

**Output:** `S02_deployment_readiness_report.json`  
Fields: `clean_install_passes`, `docker_compose_healthy`, `helm_lint_passes`, `k8s_dry_run_passes`, `terraform_plan_passes`, `single_node_deployment_works`, `monitoring_stack_works`, `steps_broken`, `steps_missing`

---

### AGENT S-03 — THE SOVEREIGN LANGUAGE RUNTIME TESTER

**Codename:** Pour the Water  
**Primary Target:** `src/thirsty_lang/`, `tarl/`, `tarl_os/`, `src/shadow_thirst/`  
**Secondary Target:** `linguist-submission/`

**Mission:**  
Five proprietary languages are claimed. This agent runs code in each language. Running ≠ documentation. Running ≠ demo. The runtime must execute arbitrary valid programs and reject invalid ones.

**What It Does:**

1. **Thirsty-Lang Interpreter Test Suite** — Run `npm run repl` and `node src/cli.js`. Write and execute 10 programs covering: variables, conditionals, functions, `shield`/`detect`/`defend` defensive blocks, all 4 security modes. Verify correct output.

2. **T.A.R.L. Compiler Pipeline Test** — Feed valid T.A.R.L. source through `CompilerFrontend` → `RuntimeVM`. Verify bytecode is produced, VM executes correctly, and resource limits are enforced when exceeded.

3. **T.A.R.L. JIT Verification** — Is the JIT compiler implemented? Does it produce faster execution for hot paths? Or is it a future milestone labeled as complete?

4. **Shadow Thirst Dual-Plane Verification** — Write a program with deliberate plane divergence (primary returns X, shadow returns Y). Does the invariant gate catch it? Does the `PlaneIsolationAnalyzer` block shadow-to-canonical mutation at compile time?

5. **TSCG/TSCG-B Round-Trip Test** — Encode a governance document: TSCG → TSCG-B → TSCG → original. Verify bit-identical round-trip. "Formal Bijectivity" requires zero information loss.

6. **TARL OS Boot Test** — Can TARL OS actually boot? If there is no executable entry point that starts the OS, TARL OS is architecture documentation, not an operating system.

7. **Error Rejection Verification** — Feed syntax errors, type errors, and security violations to each language. Do they produce clear, actionable error messages? Or Python tracebacks?

**Output:** `S03_sovereign_language_runtime_report.json`  
Fields: `language`, `interpreter_runs`, `programs_execute_correctly`, `invalid_programs_rejected`, `jit_implemented`, `shadow_invariant_catches_divergence`, `tscg_roundtrip_lossless`, `tarl_os_boots`, `error_messages_actionable`

---

### AGENT S-04 — THE RULES.MD COMPLIANCE OFFICER

**Codename:** The Law Itself  
**Primary Target:** `RULES.md`, `governance/`, `CONTRIBUTING.md`  
**Secondary Target:** All source files

**Mission:**  
RULES.md is the engineering governance law of Project-AI. It includes: prohibition on TODO stubs, mandatory pre/post-work summaries, and the architect's word as absolute law overriding all documentation. This agent verifies compliance with every rule against the actual codebase.

**What It Does:**

1. **TODO Stub Audit** — RULES.md prohibits TODO stubs. Search every file for: `TODO`, `FIXME`, `HACK`, `XXX`, `NotImplemented`, `raise NotImplementedError`, stub functions with only `return None`. Each is a RULES.md violation.

2. **Pre/Post-Work Summary Compliance** — If pre/post-work summaries are required in commits or file headers, sample 50 random commits. Do they contain the required structure?

3. **Architect Override Documentation** — Find cases where code diverges from `TECHNICAL_SPECIFICATION.md`. Is the divergence documented as an intentional architect override? Undocumented divergence is not an architect decision — it's an inconsistency.

4. **`RULES.md` Enforcement Verification** — Is `RULES.md` referenced in `CONTRIBUTING.md`? Is it enforced by any pre-commit hook or CI check? A RULES.md that no tooling enforces is a document, not a law.

5. **Governance Document Consistency** — Cross-check `RULES.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `DEVELOPER_QUICK_REFERENCE.md`. Contradictions between governance documents create ambiguity that will be exploited.

**Output:** `S04_rules_compliance_report.json`  
Fields: `todo_stub_count`, `todo_stub_locations`, `pre_post_summary_compliance_pct`, `architect_override_documented`, `rules_md_enforced_by_tooling`, `governance_doc_contradictions`

---

### AGENT S-05 — THE ACADEMIC INTEGRITY VERIFIER

**Codename:** The Citation Inspector  
**Primary Target:** All Zenodo DOIs in the codebase, `docs/spec/`, `governance/`  
**Secondary Target:** `README.md` (all badge DOIs and links)

**Mission:**  
Project-AI has 13+ Zenodo publications. DOIs are academic trust signals. This agent verifies every DOI resolves, every published paper matches the current implementation, and no citations are fabricated. This is explicitly a documented historical risk in the project.

**What It Does:**

1. **DOI Resolution Check** — Find every DOI in the codebase. Verify each resolves to a real Zenodo record. A DOI that returns 404 is a broken academic citation.

2. **Paper-to-Implementation Version Match** — For each paper, what version of the component does it describe? Does the current implementation match that version?

3. **Citation Fabrication Screen** — Run automated citation verification on all papers stored in `docs/`. Cross-reference author names, journal names, volume/issue numbers against real publication databases. This has been an issue before. It gets checked again.

4. **NPR Paper Status** — The "Naïve Passive Reviewer" paper targeting *AI and Ethics* (Springer): What submission stage is it at? Is the submitted version in `docs/` in submission-ready state?

5. **DARPA ERIS Alignment** — Are DARPA ERIS Marketplace presentation materials in the repo? Do they accurately represent the current state of the codebase? Presenting aspirational features as current capabilities to a government audience is a serious credibility risk.

**Output:** `S05_academic_integrity_report.json`  
Fields: `doi`, `resolves`, `version_match`, `fabrication_risk_score`, `paper_implementation_gap`, `npr_submission_status`, `darpa_materials_accurate`

---

## TRACK 4: META LAYER
### *"Does the fleet itself hold?"*

---

### AGENT M-01 — THE ARBITER

**Codename:** Codex Deus Maximus — External Instance  
**Role:** Receives all agent reports. Applies constitutional weighting. Renders the sovereign deploy/no-deploy verdict.

**This agent has no loyalty to the narrative. It has loyalty only to the aggregated evidence.**

**Verdict Matrix:**

```
DEPLOY-READY:          Score ≥ 90/100, 0 CRITICAL failures, 0 FABRICATED claims
CONDITIONAL-DEPLOY:    Score 75-89, ≤2 HIGH failures, 0 CRITICAL, 0 FABRICATED
HOLD-FOR-REMEDIATION:  Score 50-74, any HIGH or CRITICAL, ≤2 FABRICATED
SOVEREIGN-HOLD:        Score < 50, OR any EXISTENTIAL finding, OR any FABRICATED
                       claim in a constitutional document
```

**Weighting by Agent:**

| Agent | Weight | Rationale |
|---|---|---|
| D-01 Constitutional Auditor | 15% | The README is the face. False claims here are the most visible failures. |
| C-01 Triumvirate Verifier | 20% | The governance core. If it's broken, nothing else matters. |
| C-02 Iron Path Auditor | 15% | The cryptographic backbone. Fake crypto is worse than no crypto. |
| C-03 OctoReflex Truth | 10% | Most technically credible component. Failure breaks DOI integrity. |
| C-08 Security Surface | 15% | Security theater harms users more than no security claims. |
| S-01 Constitutional Adversary | 15% | Can the constitution be bypassed? Binary: yes or no. |
| S-02 Deployment Readiness | 10% | A system that cannot be deployed is not a platform. |
| All other agents | Remaining weight | Evidence-based deductions. |

**The Arbiter's Hard Stops (Instant SOVEREIGN-HOLD regardless of score):**

1. Any cryptographic key or secret found in commit history
2. Any `FABRICATED` finding in D-01 (constitutional claims) or S-05 (academic integrity)
3. `evaluate_triumvirate()` not wired to the actual runtime execution path
4. Any PSIA bypass that allows untrusted input to reach the governance layer
5. `governance/sovereign_runtime.py` has hardcoded test keys used in production

**Output:** `M01_arbiter_verdict.json`  
Fields: `verdict`, `score`, `hard_stops`, `critical_findings`, `remediation_queue` (ranked by severity × blast_radius), `estimated_remediation_effort`

---

## FLEET EXECUTION ARCHITECTURE

### Deployment Order

```
PHASE 1 — PARALLEL INTELLIGENCE (no dependencies)
├── D-01 Constitutional Auditor
├── D-02 Spec-to-Code Mapper
├── D-03 Issue Archaeologist
├── D-04 Changelog Integrity Officer
├── C-08 Security Surface Auditor
└── S-05 Academic Integrity Verifier

PHASE 2 — DEPENDENT ANALYSIS (requires Phase 1 outputs)
├── C-01 Triumvirate Verifier       ← requires D-01 claim list
├── C-02 Iron Path Auditor          ← requires D-01 claim list
├── C-03 OctoReflex Truth Checker   ← requires S-05 DOI results
├── C-04 PSIA Waterfall Inspector   ← requires D-02 spec map
├── C-05 Genesis Compiler Inspector ← requires D-02 spec map
├── C-06 Cognition Kernel Inspector ← requires D-01, D-02
├── C-07 Simulation Engine Check    ← requires D-01 claim list
└── C-09 Multi-Runtime Integrity    ← requires D-02 spec map

PHASE 3 — SOVEREIGN TESTING (requires Phase 1+2 outputs)
├── S-01 Constitutional Adversary   ← requires C-01, C-04 findings
├── S-02 Deployment Readiness       ← requires C-09 findings
├── S-03 Language Runtime Tester    ← requires C-06, D-02 findings
└── S-04 Rules Compliance Officer   ← requires D-04 findings

PHASE 4 — ARBITER SYNTHESIS
└── M-01 The Arbiter                ← all agent outputs required
```

### Runtime Requirements

| Requirement | Purpose |
|---|---|
| Read access to full git history | Commit analysis, secret detection |
| Python 3.11+ environment | Python code execution and testing |
| Go 1.22+ with eBPF toolchain | OctoReflex build verification |
| Node.js 14+ | Thirsty-Lang execution |
| Docker + compose | Deployment stack testing |
| `kubectl` (dry-run safe) | K8s manifest validation |
| `terraform` | Infrastructure code validation |
| `helm` | Chart linting |
| GitHub API token (read-only) | Issue fetching, PR analysis |
| Internet access | DOI resolution, badge verification |

---

## HONEST ASSESSMENT: WHAT THE FLEET WILL LIKELY FIND

This section exists because "Unprecedented Honesty" means stating the probable findings before running the fleet, not just reporting them after. If these predictions are wrong, the architecture is stronger than expected. If they are right, the remediation queue is already pre-loaded.

### HIGH PROBABILITY FINDINGS

**Documentation > Implementation Gap** — The README and architecture documents describe a system at a higher completeness level than the code. This is universal in ambitious solo projects built at speed. The gap is not a failure — it is a roadmap. The fleet's job is to map it precisely, not penalize it.

**Simulation Engines Are Specifications** — The AI Takeover engine (19 scenarios), Atlas Ω, and Zombie Defense are likely well-structured Python modules with the right architecture but without real execution depth. A "simulation" that deterministically returns pre-defined outcomes is a lookup table, not a simulation.

**Triumvirate Wiring Is Partial** — `evaluate_triumvirate()` likely exists and works correctly. Whether it is called at every decision point across the entire codebase (including `engines/`, `demos/`, `scripts/`, `tools/`) is a different question. Perimeter governance that doesn't reach the interior is a governance island.

**TODO Stubs Exist** — RULES.md prohibits them. They will be found. The meaningful question is whether they are in peripheral code or governance-critical paths.

**70 Open Issues Include Architecture Debt** — Some of the 70 issues are not bugs. They are honest admissions of incomplete implementation externalized to the issue tracker rather than kept as code comments. The fleet will surface which issues correspond to gaps in constitutional claims.

**Genesis Is Incomplete But Architecturally Sound** — The DSL→IR→Go/TS pipeline is verified (4 services, 17 files). The missing Rust emitter, LivingGenerator, and TerraformGenerator are known gaps. The fleet will verify the boundary is clean. Missing is better than broken.

**OctoReflex Is The Most Production-Ready Component** — Genuine eBPF implementation, real DOI, real benchmark numbers, 82% coverage. This is the component most likely to pass fleet inspection without significant findings.

### MEDIUM PROBABILITY FINDINGS

**TSCG-B Round-Trip May Have Edge Cases** — Bijective encoding is hard. The common case passes. Edge cases in Unicode handling, very long inputs, or constitutional documents with special characters may break round-trip fidelity.

**`h323_sec_profile/` Is Historical** — H.323 in an AI governance repo is almost certainly a historical import or security reference model. It needs to be confirmed, not assumed.

**`temp_data/ai_partner/` Contains Non-Public Data** — The naming suggests this was committed during a development session and never cleaned. Most likely location for accidentally committed credentials, API keys, or partner-confidential data.

**The PowerShell Launch Sequence Has No Error Handling** — `Master-Sovereign-Launch-Sequence.ps1` is almost certainly a "works on my machine" script written for a specific configuration, not a hardened deployment tool.

---

## REMEDIATION PRIORITY FRAMEWORK

**P0 — Fix Before Anything Else (Existential/Hard Stops)**  
Committed secrets in history | Fabricated academic citations | Triumvirate not in runtime path | PSIA bypass paths

**P1 — Fix Before External Claims of Production Readiness**  
Constitutional claim with no backing implementation | Cryptographic claims with mock implementations | TODO stubs in governance-critical paths | Security gates not blocking (advisory-only)

**P2 — Fix Before Institutional Presentation (DARPA, Zenodo, etc.)**  
DOI version drift | Paper-to-implementation gaps | Benchmark numbers without traceable test runs | Simulation engines returning static results

**P3 — Fix Before Team Expansion**  
Incomplete `RULES.md` enforcement tooling | `archive/` files still imported | `demos/` and `examples/` not current | Open issues without classification

**P4 — Fix Before v3.0 Declaration**  
Missing Genesis components (Rust emitter, LivingGenerator, TerraformGenerator) | TARL OS boot verification | Android/Unity surface assessment | Linguist submission completeness

---

## FLEET SELF-HONESTY REQUIREMENT

The fleet must operate under one final rule:

> **A finding of "VERIFIED" requires positive evidence of verification, not absence of evidence of failure.**

The difference:
- "I could not find a bypass path" → NOT VERIFIED (absence of evidence)
- "I constructed 5 bypass attempt scenarios and all were caught" → VERIFIED (positive evidence)

This is the difference between security theater and actual security. The fleet does not pass what it cannot prove. It escalates what it cannot determine.

---

## COMPLETE AGENT ROSTER

| ID | Codename | Track | Primary Target | Weight |
|---|---|---|---|---|
| D-01 | Galahad's Ghost | DOCS | README, TECHNICAL_SPECIFICATION, governance/ | 15% |
| D-02 | Shadow Reader | DOCS | docs/spec/, all language specs | — |
| D-03 | The 70 | DOCS | 70 open issues, ci-reports/, archive/ | — |
| D-04 | The Honest History | DOCS | Git log (1,856 commits), SECURITY.md | — |
| C-01 | The Third Eye | CODE | cognition/, governance/, liara_guard.py | 20% |
| C-02 | Proof of Stage | CODE | iron_path.py, sovereign_runtime.py, existential_proof.py | 15% |
| C-03 | The eBPF Inspector | CODE | octoreflex/, kernel/ | 10% |
| C-04 | Stage by Stage | CODE | src/psia/, canonical/, adversarial_tests/ | — |
| C-05 | The Pipeline Auditor | CODE | emergent-microservices/, Genesis components | — |
| C-06 | The Center | CODE | cognition_kernel.py, orchestrator/, taar/ | — |
| C-07 | The 19 Questions | CODE | engines/ (all 14+) | — |
| C-08 | The Attacker's First Look | CODE | security/, .bandit, codeql-custom-queries-python/ | 15% |
| C-09 | The Polyglot | CODE | All runtime surfaces (Python, Go, Node, Gradle, C) | — |
| S-01 | The Adversary | SOVEREIGN | adversarial_tests/, governance/ | 15% |
| S-02 | The Real Gate | SOVEREIGN | PRODUCTION_DEPLOYMENT.md, deploy/, helm/, k8s/, terraform/ | 10% |
| S-03 | Pour the Water | SOVEREIGN | All 5 sovereign language runtimes | — |
| S-04 | The Law Itself | SOVEREIGN | RULES.md, all source files | — |
| S-05 | The Citation Inspector | SOVEREIGN | All 13+ Zenodo DOIs, academic citations | — |
| M-01 | Codex Deus Maximus | META | All agent outputs → sovereign verdict | Arbiter |

**Total Agents: 19**  
**Total Weighted Coverage: 100%**  
**Deploy Authority: M-01 Alone**

---

*End of Comprehensive Strategy Guide for Unprecedented Honesty in Project-AI*  
*Version 1.0.0 — April 15, 2026*  
*Authored in SLC. Built for what comes next.*
