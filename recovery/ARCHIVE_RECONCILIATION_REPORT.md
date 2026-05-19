# Archive Reconciliation Report
**Branch:** recovery/archive-reconciliation-20260519  
**Date:** 2026-05-19  
**Sources:** `github/verified-poc-face` (3,014 unique files) · `repo-restructure` (196 unique files)  
**Rule:** Recover aggressively. Promote conservatively. Preserve everything. Canonicalize only after inspection.

---

## How to Read This Report

- **A** = file exists in archive, not in master → recovery candidate  
- **M** = file exists in both but differs → compare before deciding  
- **D** = file exists in master but not in archive → master is newer, skip  
- **R** = renamed between branches  

Raw inventories:
- `recovery_verified_poc_unique.txt` — full diff `master..github/verified-poc-face`
- `recovery_repo_restructure_unique.txt` — full diff `master..repo-restructure`

To cherry-pick a single file from an archive branch:
```bash
git checkout github/verified-poc-face -- <path>
# or
git checkout repo-restructure -- <path>
```

---

## Source: `github/verified-poc-face`

Unique files: **3,014 added**, 2,002 deleted (master has these, archive lost them), 1,981 modified.  
Focus is on the 3,014 **added** files — content in the archive that master does not have.

---

### Category 1 — Canonical Source Candidates
*Inspect individually before promoting. These are real implementation files.*

**src/app/agents/** (unique to archive):
- `alpha_red.py` — Red-team adversarial agent
- `arch_angel.py` — Arch Angel governance guard
- `attack_train_loop.py` — Attack training loop
- `planner.py` — Planning agent

**src/app/core/** (unique to archive):
- `shadow_containment.py` — Shadow Containment system
- `shadow_execution_plane.py` — Shadow Execution Plane
- `shadow_resource_limiter.py` — Shadow resource enforcement
- `shadow_types.py` — Shared shadow type definitions
- `distress_kernel.py` — Distress signal kernel
- `explainability_agent.py` — Explainability layer
- `legion_protocol.py` — Legion multi-agent protocol
- `unified_integration_bus.py` — Cross-subsystem integration bus
- `observability.py` — Observability infrastructure
- `secrets_manager.py` — Secrets management (code, not secrets)
- `security_validator.py` — Security validation layer
- `cathedral_adapter.py` — Cathedral infrastructure adapter
- `config_loader.py` / `config_validator.py` — Config subsystem
- `domain_base.py` / `error_aggregator.py` / `exceptions.py` — Core framework
- `per_service_retry_tracker.py` — Per-service retry tracking
- `mocks/governance_mock.py` / `mocks/iron_path_mock.py` — Test mocks
- `utils/path_validator.py` / `utils/secure_storage.py` — Utility layer

**src/app/governance/** (unique to archive):
- `genesis_continuity.py` — Genesis continuity enforcement
- `sovereign_audit_log.py` — Sovereign audit log implementation
- `tsa_anchor_manager.py` / `tsa_provider.py` — RFC 3161 TSA anchoring
- `external_merkle_anchor.py` — External Merkle tree anchoring
- `audit_log_json.py` / `audit_manager.py` — Audit infrastructure
- `company_pricing.py` / `government_pricing.py` — Pricing models
- `fairness_audit.thirsty` — Fairness audit in Thirsty-Lang

**src/app/vault/auth/**:
- `usb_token.py` — USB physical token auth

**src/security/** / **src/cerberus/sase/governance/**:
- `key_management.py` (both paths) — Key management implementations

**src/app/gui/**:
- `ignition_sequence.py` — Startup ignition sequence (non-legacy)

**engines/atlas/** (~40 files):
Full Atlas engine — ingestion, analysis, normalization, scoring, governance, simulation, verification. Standalone engine not present in master. High-value recovery candidate.

**engines/hydra_50/**:
- `cerberus_hydra.py` — Cerberus Hydra 50-language polyglot engine
- `hydra_50_engine.py` — Core engine
- `hydra_incident_response.py` — Incident response integration

**engines/sovereign_war_room/**:
- `cli.py` — Sovereign War Room CLI
- `demo.py` — Demo script
- `swr/` — Full swr package
- `requirements.txt`

**engines/cognitive_warfare/**:
- `cognitive_warfare_framework.py` — Cognitive warfare defense framework

**engines/consigliere/**:
- `consigliere_engine.py` — Consigliere engine (standalone, differs from thirstys_waterfall version)

**engines/global_scenario/**:
- `global_scenario_engine.py` / `scenario_config.py` — Global scenario simulation

**canonical/**:
- `sovereign_proof.py` — Sovereign proof validation
- `sovereign_scenario.yaml` — Sovereign scenario definition

**cognition/**:
- `triumvirate.thirsty` — Triumvirate governance in Thirsty-Lang

**octoreflex/** (standalone Go implementation, ~68 files):
OctoReflex as a standalone Go microservice — separate from the Python `src/app/core/octoreflex.py` already in master. Includes budget enforcement, Go runtime, internal packages. High-value if the Go implementation is intended.

**native_browser/project_ai_browser_core/src/**:
- `app/core/waterfall_orchestrator.py` — Browser-specific Waterfall orchestrator
- `app/testing/pa_shield/` — PA Shield testing framework

**data/** (non-runtime):
- `genesis_pins/continuity_log.json` / `external_pins.json` — Governance continuity pins (structured, not runtime)
- `migrations/V1__Initialize_Sovereign_Schema.sql` — Database schema migration
- `cerberus/agent_templates/pace_agent_template.py` — Pace agent template (not in master)

---

### Category 2 — Documentation / Architecture Evidence
*High-value historical record. Promote selectively or preserve as-is in archive.*

- **`docs/`** — 158 files. Architecture, governance, security, deployment, developer docs.
- **`wiki/`** — 194 files. Full wiki content from pre-restructure state.
- **`governance/`** — 24 files. Governance policy documents.
- **`hardware_schematics/`** — 22 files. Platform integration specs (android, cloud, edge, linux, raspberry_pi, stm32) + 13 variant specs (biologist, contractor, engineer, enterprise, geologist, journalist, law_enforcement, lawyer, medical, military, researcher, scientist, stock_analyst, student).
- **`archive/docs/`** — Architecture overview, security ethics overview, kernel modularization, deployment, governance policy, SBOM policy, audit reports, civilization timeline, documentation structure guide.
- **`.github/`** — Active_Governance_Policy.md, BRANCH_PROTECTION.md, THIRST_BRANCH_ACCEPTANCE_CRITERIA.md, branch-transfer-matrix.yaml, GITHUB_SECURITY_COMPLIANCE.md, SECURITY_ADVISORY_TEMPLATE.md, SECURITY_VALIDATION_CHECKLIST.md, SECURITY_VALIDATION_POLICY.md, instructions/README.md.
- **`k8s/`** — K8S_DEPLOYMENT_GUIDE.md, README.md (docs only from this dir).
- Root-level docs: `WHITEPAPER.md`, `README_HONEST.md`, `README_ORIGINAL_BACKUP.md`, `SYSTEM_MANIFEST.md`, `SOVEREIGN_MANIFEST.md`, `TECHNICAL_SPECIFICATION.md`, `TAMS_SUPREME_SPECIFICATION.md`, `SOVEREIGN_VAULT_ARCHITECTURE.md`, `SOVEREIGN_MANIFEST.md`, `VAULT_SECURITY_GAPS_ANALYSIS.md`, `VAULT_IMPLEMENTATION_PHASES.md`, `VAULT_ADVANCED_PATTERNS_ANALYSIS.md`, `The_Guide_Book.md`, `CITATIONS.md`, `ARCHITECT_MANIFEST.md`.
- `engines/atlas/README.md` / `PROGRESS_REPORT.md`
- `engines/sovereign_war_room/README.md` / `IMPLEMENTATION_COMPLETE.md`

---

### Category 3 — Tests / Adversarial Suites
*Strong recovery candidates. 92 unique test files not in master.*

**tests/** (92 files total):
- `tests/test_12_vector_constitutional_break.py` — 12-vector constitutional break suite
- `tests/test_anti_sovereign_stress_tests.py` — Anti-sovereign stress testing
- `tests/test_attack_simulation_suite.py` — Attack simulation
- `tests/test_attack_train_loop.py` — Attack training loop tests
- `tests/test_asymmetric_security_coverage.py` — Asymmetric security coverage
- `tests/test_arch_angel.py` / `tests/agents/test_arch_angel.py` — Arch Angel tests
- `tests/test_alpha_red.py` — Red-team agent tests
- `tests/test_ai_systems_comprehensive.py` / `test_ai_systems_coverage.py`
- `tests/test_bft_deployed.py` — Byzantine fault tolerance
- `tests/test_cathedral_infrastructure.py`
- `tests/test_cognition_comprehensive.py`
- `tests/test_containment.py` — Containment tests
- `tests/test_deadman_switch.py` — Deadman switch
- `tests/test_ed25519_crypto.py` — Ed25519 cryptography
- `tests/test_enterprise_monolithic.py`
- `tests/test_entropy_slope.py`
- `tests/test_existential_proof.py`
- `tests/test_external_merkle_anchor.py`
- `tests/test_formal_properties.py`
- `tests/chaos/` — Chaos engineering tests
- `tests/e2e/test_production_readiness.py` — E2E production readiness
- `tests/integration/test_sovereign_stack.py` — Integration: full sovereign stack
- `tests/load/k6-load-test.js` — k6 load testing
- `tests/manual/` — Manual test scripts
- `tests/sase/core/test_normalization.py`
- `tests/security/` — Security test suite
- `tests/security_verify_fix.py`

---

### Category 4 — Website / Demo Material

- `scripts/demos/demo_explainability.py` — Explainability demo
- `scripts/demos/rainbow_csv_visualizer.py` — Rainbow CSV visualizer
- `scripts/demos/vr_simulation_demo.py` — VR simulation demo
- `scripts/demo/proof_of_sovereignty.thirsty` — Proof of sovereignty in Thirsty-Lang
- `scripts/demo/proof_of_sovereignty_exec.py` — Sovereignty proof runner
- `bayesian_proof_demo.py` — Bayesian proof demo
- `engines/sovereign_war_room/demo.py`
- `unity/ProjectAI/Assets/Scripts/VR/RainbowCSVConnector.cs` — VR Rainbow CSV connector
- `unity/ProjectAI/Assets/Scripts/VR/World/Presence/PresenceController.cs` — VR presence controller

---

### Category 5 — Tooling / Automation Scripts
*Useful for ops. Promote if actively needed; otherwise preserve in archive.*

**scripts/** (49 files):
- `scripts/personal_agent.py` — Personal agent launcher
- `scripts/validate_production_claims.py` / `scripts/validate_all_code.py`
- `scripts/verify_poc_surface.py` / `scripts/verify_heart_restore_map.py`
- `scripts/verify/` — Startup test suite, UTF master runner, runbook verifier, Thirsty interpreter verifier
- `scripts/build_sovereign_agent.py` / `scripts/build_standalone.py` / `scripts/build_training_data.py`
- `scripts/train_sovereign.py` / `scripts/merge_and_quantize.py`
- `scripts/maintenance/` — Heal substrate, archive files, audit repo, fix TOML, verify system
- `scripts/sync_sovereign_workspace.py` / `scripts/organize_tree.py`
- `scripts/deploy_sovereign.sh` / `scripts/deploy_shortcut.ps1`
- `scripts/run_daily_tests.py` / `scripts/run_weekly_tests.py`
- `scripts/generate_coverage_tests.py` / `scripts/generate_modelfile.py`
- `scripts/arch_angel_docs_guard.py`

**k8s/** (77 files, non-doc):
Full Kubernetes deployment manifests — base configs (configmap, deployment, hpa, ingress, kustomization, monitoring, namespace, networkpolicy, pdb, postgres, pvc, rbac, redis, service, sovereign_policy), blue-green deploy script, mutating webhooks, tk8s civilization pipeline.

**helm/** (14 files):
Helm chart for project-ai deployment.

**deploy/** (46 files):
Single-node deployment configs including MCP gateway (secrets.env is a template — all values empty).

**.github/workflows/** (active workflows unique to archive):
- `bandit.yml`, `ci.yml`, `codeql.yml`, `dependency-review.yml`, `deploy.yml`, `format-and-fix.yml`, `production-deployment.yml`, `project-ai-monolith.yml`, `security-secret-scan.yml`, `stale.yml`, `tk8s-civilization-pipeline.yml`, `update-deployment-standard.yml`, `verified-poc-surface.yml`

**emergent-microservices/** (339 files — per-service infra):
Full microservices fleet — 7+ services each with Dockerfile, CI config, app/, database/, docs/, kubernetes/, tests/:
- `ai-mutation-governance-firewall`
- `autonomous-compliance`
- `autonomous-incident-reflex-system`
- `autonomous-negotiation-agent`
- `sovereign-data-vault`
- `trust-graph-engine`
- `verifiable-reality`

**Other tooling**:
- `entrypoint.sh` / `workspace_init.sh` / `setup_native_linux_substrate.sh` / `run_headless.sh`
- `build-installer.ps1` / `FIX_WORKSTATION.ps1` / `Project-AI.ps1` / `Master-Sovereign-Launch-Sequence.ps1`
- `terraform/` — 2 files
- `desktop/` — 2 files (desktop app source)
- `android/` — 1 file

---

### Category 6 — Generated Artifacts
*Do not promote. These are runtime outputs.*

- `canonical/execution_trace.json` — runtime trace (already in .gitignore)
- `ci-reports/garak-latest.json` / `hydra-latest.json` / `jbb-latest.json` / `multiturn-latest.json` / `unified-report.json` — CI run outputs
- `archive/cleanup_2026-03-04/cognition/governance_audit.log`
- `archive/cleanup_2026-03-04/data/defense_engine.log`
- `archive/history/audit.log` / `boot_log_v2.txt` / `debug_error.log` / `debug_error.txt` / `final_results.txt` / `out.txt` / `showcase_audit.log` / `test_results.txt`
- `archive/train_error.log` / `train_error_v2.log` / `train_v3.log` / `train_v4.log` / `train_v5.log`
- `coverage_run.log` / `coverage_run2.log` / `coverage_run_final.log`
- `coverage_baseline.txt` / `baseline_coverage.txt` / `coverage_output.txt`
- `final_coverage_report.txt` / `final_coverage.txt` / `full_coverage_report.txt`
- `test_report.txt` / `output/` directory
- `compliance_manifest.json` / `RELEASE_MANIFEST.json` — generated manifests
- `benchmarks/benchmark_report.json` — generated benchmark output
- `inventory.csv` / `full_file_list.txt` — generated file lists
- `data/cerberus/logs/bypasses_202603.jsonl` — runtime log
- `archive/cleanup_2026-03-04/temp_data/` — runtime session state
- `archive/cleanup_2026-03-04/test_results/` — generated test result screenshots/perf data
- `unity/ProjectAI/Library/Bee/` — Unity build artifacts (all DAG/artifact files)
- `.lsp/.cache/db.transit.json` — LSP editor cache
- `tmp/` — 2 temporary files
- `tmp_test_frame.tsgb` — temp file

---

### Category 7 — Duplicates / Stale Snapshots
*Master has equivalent or better. Skip unless diff reveals something worth keeping.*

- `src/app/gui/archive/dashboard_handlers_legacy.py` / `dashboard_main_legacy.py` / `dashboard_utils_legacy.py` — explicitly labeled legacy
- `Project-AI-Monorepo/Branches/` — 84 files of branch structure documentation about branches that no longer exist. Metadata docs, not source.
- `archive/PROJECT_STATUS.md` / `archive/PROJECT_STRUCTURE.md` / `archive/CHANGELOG.md` — stale state snapshots superseded by current repo state
- `requirements-updated.txt` / `requirements-stabilized.txt` / `requirements-optional.txt` / `requirements-test.txt` — stale alternate requirements files
- `.gitmodules.local_backup` — backup of gitmodules, not needed
- `archive/cleanup_2026-03-04/data/training_datasets/agi_partner_dataset.json` — old training data
- `archive/cleanup_2026-03-04/test-data/test_intent.json` — stale test fixture
- `.venv_prod/` — 5 venv files (never commit venv)
- `.hypothesis/` — 3 hypothesis test database files (generated)

---

### Category 8 — Secrets / Unsafe Material
*Inspect before any action. Do not promote without explicit review.*

**Inspect (likely safe — confirm before promoting):**
- `data/genesis_keys/genesis_audit.pub` — Public key (Ed25519). Public keys are inherently safe, but confirm this is intentional to expose.
- `data/genesis_keys/genesis_id.txt` — Contains `GENESIS-6985DC0939714B77`. Public identifier. Confirm it's not a private seed.
- `deploy/single-node-core/mcp/secrets.env` — All values empty (template only). Safe structure, safe to promote as template.
- `k8s/base/secret.yaml` / `k8s/mutating-webhooks/secret.yaml` / `emergent-microservices/*/kubernetes/secret.yaml` — Verify all are templates with no real values before promoting.
- `config/personal_agent.json` — Personal configuration. Inspect for hardcoded paths, tokens, or personal identifiers before promoting.
- `.vscode/launch.json` / `.vscode/tasks.json` — Inspect for hardcoded paths or credentials.
- `archive/src/security/key_management.py` — Key management code (not keys). Safe if it's source code only.
- `src/cerberus/sase/.env.example` — Example env file. Should be safe.

**Likely skip:**
- `archive/cleanup_2026-03-04/temp_data/ai_partner/partner_state.json` — Session state file. Likely contains runtime identity data.

---

### Category 9 — Deprecated but Historically Valuable
*Keep in archive. Do not promote to master. Reference during active development of related systems.*

**Thirsty-Lang source variants** (pre-UTF-stack, now superseded by `src/utf/`):
- `src/app/main.thirsty` — Main entry point in Thirsty-Lang
- `src/app/browser/governance.tarl` / `verification.shadow` — Browser-specific T.A.R.L. and Shadow scripts
- `src/app/ai/model_sovereignty.thirsty` — Model sovereignty spec
- `src/app/arch_ledger.thirsty` / `bootstrap.thirsty` / `global_jurisdiction.thirsty` — Key governance files
- `src/app/core/adversary_generator.thirsty` / `catalog_manager.thirsty` / `crypto_agility.thirsty` / `research_agent.thirsty`

**Scenario/simulation engines** (prototype-stage):
- `engines/novel_security_scenarios/` — Novel security scenario prototypes
- `engines/constitutional_scenario/` — Constitutional scenario engine
- `engines/simulation_contract/` — Simulation contract engine
- `engines/emp_defense/GOD_TIER_ESCALATION_COMPLETE.md` — Completion doc for EMP defense work

**Native browser implementation** (pre-Waterfall integration):
- `native_browser/project_ai_browser_core/` — Full native browser core (Electron-based). Contains waterfall_orchestrator.py and pa_shield testing. Superseded by thirstys_waterfall package but historically significant.

**Archive API** (pre-restructure API):
- `archive/api/main.py` / `archive/api/versioning.py` — Old API server
- `archive/check_sig.py` — Old signature verification

**Cognition docs**:
- `cognition/README.md` — Cognition system README

---

## Source: `repo-restructure`

Unique files: **196 added**, 701 deleted (master has these), 463 modified.

---

### Category 1 — Canonical Source Candidates

**src/** (3 files):
- `src/app/agents/alpha_red.py` — Red-team agent (compare with poc version before choosing)
- `src/app/agents/attack_train_loop.py` — Attack training loop
- `src/app/agents/planner.py` — Planner agent

**Developer tooling scripts** (root-level):
- `add_developer_metadata.py` — Adds developer metadata to files
- `analyze_coverage.py` — Coverage analysis script
- `compare_bandit_results.py` — Bandit security scan comparison
- `enrich_engine_docs.py` — Engine documentation enrichment

**`pytest.ini`** — Test configuration. Compare with any existing pytest.ini before promoting.

**`docs/reports/` agent linker scripts**:
- `AGENT-072-link-generator.py` — Cross-document link generator
- `agent_074_cross_doc_linker.py` / `agent_074_inline_linker.py` / `agent_074_link_processor.py`
- `agent_075_link_system.py` / `agent_075_phase2_links.py`
- `agent_079_crosslink_batch.py`

---

### Category 2 — Documentation / Architecture Evidence

**`docs/`** (unique to restructure):
- `docs/GOD_TIER_CROSS_TIER_PERFORMANCE_MONITORING.md`
- `docs/GOD_TIER_SUGGESTIONS_IMPLEMENTATION.md`
- `docs/architecture/GOD_TIER_DISTRIBUTED_ARCHITECTURE.md`
- `docs/architecture/GOD_TIER_INTELLIGENCE_SYSTEM.md`
- `docs/architecture/GOD_TIER_PLATFORM_IMPLEMENTATION.md`
- `docs/architecture/GOD_TIER_SYSTEMS_DOCUMENTATION.md`
- `docs/internal/archive/GOD_TIER_EXPANSION_COMPLETE.md`
- `docs/internal/archive/GOD_TIER_EXPANSION_SUMMARY.md`
- `docs/internal/archive/GOD_TIER_IMPLEMENTATION_EXECUTIVE_SUMMARY.md`
- `docs/internal/archive/GOD_TIER_IMPLEMENTATION_SUMMARY_NEW.md`

**`vault-validation-report.md`** — Vault validation evidence.

---

### Category 5 — Tooling / Automation Scripts

- `automation-backups/` (2 files) — Automation backup snapshots
- `.github/` (2 files) — GitHub config unique to restructure
- `ci-reports/` (5 files) — CI reports (see Category 6)

---

### Category 6 — Generated Artifacts

- `canonical/execution_trace.json` — Runtime trace. Skip.
- `ci-reports/` (5 files) — Generated CI scan outputs.
- `tarl_os/GOD_TIER_IMPLEMENTATION_COMPLETE.md` — Agent completion doc.
- `engines/emp_defense/GOD_TIER_ESCALATION_COMPLETE.md` — Agent completion doc.

---

### Category 9 — Deprecated but Historically Valuable

**Agent mission reports** (115 AGENT-* and AGENT_* files at root):  
These are auto-generated mission completion documents from 100+ named agents (AGENT-007 through AGENT-112, AGENT_008 through AGENT_057). They are not source code, but they are an audit trail of what was built, when, by which agent, and what was verified. High historical value as evidence of the build process. Do not promote to master root — too noisy. Recommend moving to `docs/agent-mission-archive/` if harvesting.

**Root-level audit/report files** (43 `*_REPORT.md` files):
- `AUTHENTICATION_SECURITY_AUDIT_REPORT.md`
- `SECURITY_VULNERABILITY_ASSESSMENT_REPORT.md`
- `CONSTITUTIONAL_AI_IMPLEMENTATION_REPORT.md`
- `TECHNICAL_DEBT_REPORT.md`
- `CODE_QUALITY_REPORT.md`
- `OBSIDIAN_VAULT_FINAL_REPORT.md`
- `SHA256_AUDIT_REPORT.md`
- `BYPASS_FIX_REPORT.md`
- `TIMING_ATTACK_FIX_REPORT.md`
- (and 34 others)

These are evidence of work done during the restructure phase. Historically valuable, not current state.

---

## Priority Harvest Recommendations

Listed in order of importance. None of these should be merged wholesale — cherry-pick each file individually.

### Immediate (highest confidence, no known conflicts):

1. **`engines/atlas/`** — Full standalone engine, ~40 files. No equivalent in master.
2. **`engines/hydra_50/`** — Cerberus Hydra 50-language engine. Not in master.
3. **`engines/sovereign_war_room/`** — Sovereign War Room CLI + package. Not in master.
4. **`engines/cognitive_warfare/`** / **`engines/global_scenario/`** — Scenario engines.
5. **`tests/`** — 92 adversarial test files. Pure additions, no conflicts with existing tests in master.
6. **`src/app/core/shadow_*.py`** — Shadow Execution Plane and Containment. Core architecture.
7. **`src/app/governance/genesis_continuity.py`** + tsa_anchor_manager, external_merkle_anchor — Audit anchoring infrastructure.
8. **`canonical/sovereign_proof.py`** — Proof validation.
9. **`octoreflex/`** — Standalone Go OctoReflex (if Go implementation is intended).
10. **`hardware_schematics/`** — Deployment variant specs. Pure documentation, safe.

### Secondary (inspect content before promoting):

11. **`src/app/agents/alpha_red.py`** / `arch_angel.py` / `attack_train_loop.py` / `planner.py`
12. **`src/app/core/distress_kernel.py`** / `legion_protocol.py` / `explainability_agent.py`
13. **`src/app/core/utils/`** — path_validator, secure_storage
14. **`emergent-microservices/`** — Individual services, inspect each
15. **`scripts/verify/`** — Verification scripts
16. **`k8s/`** + **`helm/`** + **`deploy/`** — If k8s deployment is active

### Hold for explicit decision:

17. **`data/genesis_keys/`** — Public key material. Safe technically, but confirm intent.
18. **`config/personal_agent.json`** — Inspect for personal data.
19. **`native_browser/`** — Large Electron implementation. Confirm relevance.
20. **`unity/`** — 919 files. 861 are code/doc. Confirm Unity VR is active work.
21. **Agent mission reports** (repo-restructure) — Move to archive subdir if harvesting.

### Do not promote:

- All log files, trace files, coverage outputs, CI JSON reports
- `Project-AI-Monorepo/Branches/` — branch metadata docs
- Legacy GUI files (`gui/archive/`)
- `.venv_prod/` / `.hypothesis/`
- `canonical/execution_trace.json`

---

## Antigravity Reconstruction Note

This archive represents the closest reconstruction point after the Antigravity repo accident. The `github/verified-poc-face` branch in particular preserves:

- The Shadow Execution Plane (`shadow_containment.py`, `shadow_execution_plane.py`)
- The full Cerberus Hydra 50-language engine
- The Atlas engine (standalone)
- The Sovereign War Room
- The emergent microservices fleet (7 services)
- The Unity VR integration (919 files)
- The k8s/helm/deploy production infrastructure
- The full adversarial test suite (92 files)
- 194 wiki files
- The Arch Angel governance guard
- Genesis continuity and TSA anchoring

None of these exist in master. They are not duplicated elsewhere. The archive branch is the only copy.

---

*Report generated 2026-05-19. Raw inventories: `recovery_verified_poc_unique.txt`, `recovery_repo_restructure_unique.txt`.*
