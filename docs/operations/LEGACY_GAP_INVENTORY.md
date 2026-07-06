# Legacy Coverage Gap Inventory — Project-AI Beginnings

> **Generated:** 2026-06-24
> **Source-of-truth:** `T:\00-Active\Project-AI-main` (soft-frozen, read-only input)
> **Target:** `T:\00-Active\Project-AI-Beginnings` (rebuild at `ca3477a`, 18 stages accepted)
> **Standard:** Thirsty's Standard v3 (binding via `AGENTS.md`)
> **Method:** Read-only disk walk + manifest cross-reference + SHA-256 spot-check
> **Companion files:** `LEGACY_GAP_INVENTORY.csv` (machine-readable), `LEGACY_GAP_INVENTORY_VERIFICATION.md` (hostile self-review log)
> **Plan that produced this:** `C:\Users\Quencher\.hermes\plans\2026-06-24_080000-project-ai-gap-discovery.md`

---

## 0. Headline numbers

| Metric | Value | Evidence |
|---|---|---|
| Legacy repo tracked files | **5,276** | `git -C T:\00-Active\Project-AI-main ls-files \| wc -l` |
| Legacy repo total files on disk | **71,066** (top-level dirs; excludes `.git`) | `find` walk; see Phase B below |
| Legacy tracked files dispositioned | **5,276 / 5,276 (100%)** | `docs/reference/DROPPED_FILES_MANIFEST.md` line 4 |
| Legacy tracked files dropped from Beginnings runtime | **5,138** (97.4%) | DROPPED manifest, "not selected" rows |
| Legacy tracked files "scheduled for owning migration gate" | **127** (2.4%) | DROPPED manifest, "scheduled" rows (Android + SOVEREIGN-WAR-ROOM + atlas + API + canonical) |
| Legacy tracked files "indexed as legacy navigation; not copied verbatim" | **19** (0.4%) | DROPPED manifest, `.obsidian/` rows |
| Beginnings repo tracked files (this session) | **516** | `git ls-files` |
| Beginnings total files on disk | **28,436** (dominated by `target/` 209MB, `node_modules/` 173MB, `build/` 100MB) | `find` walk |
| Beginnings source packages | **13** (kernel, governance, capability, execution, companion, swr, atlas, api, cli, arbiter, rlp, security, _staging) | `packages/` |
| Beginnings source .py files total (in packages) | **~95** | `find packages -name '*.py' \| wc -l` (excluding `__pycache__`) |
| Legacy source .py files total (in scoped domains) | **~3,000+** | Estimated from Phase C |

---

## 1. Top-level coverage matrix (legacy dir → classification)

Every top-level directory in `T:\00-Active\Project-AI-main` (excluding `.git`). `trk` = git-tracked, `real` = on-disk after removing `.venv`, `node_modules`, `__pycache__`, `.ruff_cache`. Classification uses both `DROPPED_FILES_MANIFEST.md` disposition and direct content inspection.

| Legacy dir | trk | real | Disposition / classification |
|---|---|---|---|
| `.agent` | 1 | 1 | not selected (IDE config). **Class: cache/ide. Drop.** |
| `.antigravity` | 7 | 10 | not selected (IDE config). **Class: cache/ide. Drop.** |
| `.claude` | 1 | 2 | not selected (IDE config). **Class: cache/ide. Drop.** |
| `.codacy` | 2 | 6 | not selected (CI tool config). **Class: ci-config. Drop.** |
| `.devcontainer` | 3 | 3 | not selected (DevContainer config). **Class: dev-config. Drop.** |
| `.githooks` | 1 | 1 | not selected (git hooks). **Class: ci-config. Drop.** |
| `.github` | 149 | 152 | not selected (CI workflows, agents, instructions). **Class: ci-config. Drop or cherry-pick `ci.yaml` only — Beginnings already has its own.** |
| `.gradle` | 1 | 74 | ignored cache. **Class: cache. Drop.** |
| `.hypothesis` | 1 | 1,556 | ignored cache. **Class: cache. Drop.** |
| `.mypy_cache` | 1 | 4 | ignored cache. **Class: cache. Drop.** |
| `.obsidian` | 18 | 32 | "indexed as legacy navigation; not copied verbatim" per DROPPED. **Class: navigation. Drop.** |
| `.pytest_cache` | 1 | 6 | ignored cache. **Class: cache. Drop.** |
| `.ruff_cache` | 1 | 2,003 | ignored cache. **Class: cache. Drop.** |
| `.tmp` | 82 | 82 | all `neo_exec_*.bat` — execution logs. **Class: runtime-trace. Drop.** |
| `.venv` | 1 | 9,036 | virtual env. **Class: cache. Drop.** |
| `.venv_airllm` | 1 | 20,014 | virtual env. **Class: cache. Drop.** |
| `.vscode` | 1 | 4 | IDE config. **Class: cache/ide. Drop.** |
| `__pycache__` | 1 | 16 | bytecode cache. **Class: cache. Drop.** |
| **adversarial_tests** | 313 | 326 | not selected. Contains 313/326 = 96% real adversarial test scenarios (garak/jbb/hydra transcripts). **Class: runtime-test. DROP, but high-value preservation candidate → `docs/legacy-archive/adversarial_tests/`.** |
| **agent_playbook** | 13 | 22 | not selected. Partial: `governance_framework/` content was carried into `packages/rlp/` per STAGE_4.8. Leftover: `src/agent_playbook/cli.py`, `governance_core.py`, `provenance_verify.py`, `pyproject.toml`, validation tools. **Class: runtime-source. RECOMMEND: re-incorporate into `packages/rlp/` or new `packages/agent_playbook/`.** |
| **android** | 32 | 32 | scheduled for owning migration gate. STAGE_9.5 confirmed scoped carry. **Class: app. Beginnings has scoped Android client (tested per STAGE_18_ACCEPTANCE). PARTIAL — verify what is in Beginnings vs legacy `android/`.** |
| api | 8 | 13 | not selected. Real source: `api/main.py`, `save_points_routes.py`, `Dockerfile`. Beginnings has `packages/api/` with FastAPI gateway + Chimera routes. **Class: runtime-source. PARTIAL — `packages/api/` is rebuilt; legacy `api/` not used as source.** |
| **app** | 5 | 6 | not selected. Java Android app (separate from `android/`). **Class: app. DROP — superseded by Android.** |
| archive | 39 | 43 | not selected. Archived docs and experimental code. **Class: archive-material. Preserve as `docs/legacy-archive/archive/` only if space; otherwise drop.** |
| atlas | 69 | 120 | scheduled for owning migration gate. STAGE_4 + STAGE_11 merged. Beginnings has `packages/atlas/src/atlas/{analysis.py, service.py}`. Legacy has 17 subdirs + 102 Python files. **Class: runtime-source. PARTIAL — only 2 source files carried; 100+ files NOT carried.** |
| audit_reports | 1 | 120 | ignored per `.gitignore` (`audit_reports/`). **Class: log. Drop.** |
| automation-backups | 92 | 92 | not selected (legacy backup scripts). **Class: archive-material. Drop.** |
| automation-reports | 1 | 1 | ignored per `.gitignore`. **Class: log. Drop.** |
| baseline | 9 | 9 | not selected. **Class: archive-material. Drop.** |
| benchmarks | 1 | 1 | not selected. **Class: test-helper. Drop.** |
| build | 1 | 6 | ignored per `.gitignore` (`build/`). **Class: cache. Drop.** |
| buildSrc | 4 | 141 | not selected. Gradle build scripts. **Class: ci-config. Drop.** |
| canonical | 8 | 14 | not selected. Contains `replay.py` (23KB), `invariants.py` (20KB), `sovereign_proof.py`, `expected_outcome.md`. **Class: runtime-source. CRITICAL — Beginnings has `tools/canonical_replay.py`; verify the canonical/replay.py invariants are reused. RECOMMEND: preserve legacy `canonical/` as `docs/legacy-archive/canonical/` reference; `tools/canonical_replay.py` may already pull from this.** |
| ci-reports | 1 | 6 | ignored per `.gitignore`. **Class: log. Drop.** |
| cognition | 16 | 41 | not selected. Contains `cognition_kernel.py` stubs. Real cognition lives in `src/app/core/cognition_kernel.py` (53KB). **Class: runtime-source-stub. DROP the cognition/ dir; root cognition in `src/app/core/`.** |
| config | 40 | 48 | not selected (40 tracked config files). **Class: config. Preserve selectively as `docs/legacy-archive/config/`.** |
| conformance | 13 | 17 | not selected. **Class: runtime-test. Preserve as `docs/legacy-archive/conformance/`.** |
| **data** | 103 | 160 | ignored per `.gitignore` (`data/`). Real data dirs: `health_snapshots/`, `audit/`, `arch_angel/`, `savepoints/`, `triumvirate_notifications/`, `fates/memory/`, `sovereign_messages/`. **Class: runtime-state + paper-archive. Do not move runtime data; preserve paper-archive data as `docs/legacy-archive/data/`.** |
| dataview-queries | 33 | 33 | not selected (Obsidian dataview queries). **Class: navigation. Drop.** |
| demos | 24 | 41 | not selected. **Class: examples. Preserve as `docs/legacy-archive/demos/`.** |
| desktop | 31 | 31 | scheduled for owning migration gate. STAGE_14.5 confirmed desktop. **Class: app. PARTIAL — Beginnings has desktop source.** |
| diagrams | 42 | 43 | not selected (29 markdown, 1 py, 12 other). **Class: doc. Preserve as `docs/legacy-archive/diagrams/`.** |
| docs | 924 | 936 | not selected. **CRITICAL: 924 of 936 are tracked. Contains the entire legacy docs tree including `docs/governance/COMPREHENSIVE_STRATEGY_GUIDE_PROJECT_AI.md` which is also in Beginnings `docs/reference/` (SHA-confirmed).** **Class: doc. PARTIAL — substantial content carried into `docs/reference/` per MERGE_PROVENANCE; remainder is drop.** |
| e2e | 32 | 62 | not selected. **Class: runtime-test. Preserve as `docs/legacy-archive/e2e/`.** |
| **emergent-microservices** | 1 | 0 real | "tracked" file is just a placeholder. All 42 on-disk files are `.ruff_cache` debris from subdirs that never had source. **Class: empty/dead. Drop entirely — no real content ever existed here.** |
| **engines** | 220 | 379 | not selected. Critical domain: 10 engines (`ai_takeover`, `alien_invaders`, `atlas`, `cognitive_warfare`, `django_state`, `emp_defense`, `global_scenario`, `hydra_50`, `sovereign_war_room`). 220 tracked. **Class: runtime-source. CRITICAL — `engines/atlas/` and `engines/sovereign_war_room/swr/` were merged; 8 other engines completely NOT in Beginnings.** |
| examples | 30 | 56 | not selected. 26 py demos. **Class: examples. Preserve as `docs/legacy-archive/examples/`.** |
| gradle | 3 | 3 | not selected. **Class: ci-config. Drop.** |
| **gradle-evolution** | 44 | 87 | not selected. 37 py + 7 md. **Class: ci-config. Preserve as `docs/legacy-archive/gradle-evolution/`.** |
| gradle_evolution | 1 | 3 | not selected. **Class: ci-config. Drop (superseded by gradle-evolution).** |
| graph-views | 1 | 1 | not selected. **Class: navigation. Drop.** |
| **governance** | 59 | 89 | not selected. Contains `triumvirate_server.py` (21KB), `iron_path.py` (20KB), `singularity_override.py` (23KB), `existential_proof.py` (21KB), `core.py`, `audit_log.yaml`, `governance_state.json`, `ai-mutation-governance-firewall/` (15 files), `sovereign_data/` (artifacts JSON). **Class: runtime-source. CRITICAL — Beginnings `packages/governance/` has 4 source files; legacy has 89. Most of legacy governance is NOT in Beginnings.** |
| h323_sec_profile | 22 | 25 | not selected. **Class: security-config. Preserve as `docs/legacy-archive/h323_sec_profile/`.** |
| hardware_schematics | 22 | 22 | not selected. **Class: hardware-doc. Preserve as `docs/legacy-archive/hardware_schematics/`.** |
| helm | 6 | 6 | not selected. Beginnings has `helm/`. **Class: deploy-config. Beginnings has its own; drop legacy.** |
| indexes | 12 | 12 | not selected. **Class: doc. Drop (index of dropped content).** |
| integrations | 52 | 87 | not selected. 33 py + 12 md. **Class: runtime-source. Preserve as `docs/legacy-archive/integrations/`.** |
| **kernel** | 27 | 63 | not selected. Contains `thirsty_super_kernel.py` (17KB), `deception.py` (18KB), `syscall_interception.py` (10KB), `tarl_gate.py`, `tarl_codex_bridge.py`, `threat_detection.py` (16KB), `learning_engine.py` (16KB), `holographic.py` (15KB), `visualize.py` (15KB), `defcon_stress_test.py` (39KB), `advanced_visualizations.py`. Beginnings `packages/kernel/` has 8 source files. **Class: runtime-source. CRITICAL — large gap, especially kernel-adjacent infrastructure (`syscall_interception`, `holographic`, `learning_engine`).** |
| linguist-submission | 12 | 12 | not selected. **Class: misc. Drop.** |
| monitoring | 2 | 2 | not selected. **Class: runtime-source. Drop — only 2 YAML files, nothing to rebuild.** |
| **plans** | 1 | 1 | not selected. `plans/plan.md`. **Class: doc. DROP — superseded by `~/.hermes/plans/` and `docs/internal/REBUILD_EXECUTION_PLAN.md`.** |
| policies | 4 | 8 | not selected. **Class: config. Drop or merge into `packages/governance/policy.py`.** |
| project_ai | 30 | 70 | not selected. **Class: runtime-source. Inspect contents — likely legacy package source predating `packages/` reorganization.** |
| Project-Ai | 6 | 6 | "indexed as legacy navigation; not copied verbatim" — live Obsidian workspace state. **Class: ide-state. Excluded from inventory (live state).** |
| Project_ai_index | 1 | 0 | tracked but 0 on-disk. **Class: empty/dead. Drop.** |
| recovery | 47 | 47 | not selected. **Class: op-history. Preserve as `docs/legacy-archive/recovery/` (operational history has audit value).** |
| relationships | 195 | 195 | not selected. 194 markdown + 1 small. **Class: data-model. Preserve as `docs/legacy-archive/relationships/`.** |
| scripts | 160 | 268 | not selected. 105 py + 10 md. **Class: ops-scripts. Preserve as `docs/legacy-archive/scripts/`.** |
| security | 1 | 0 | tracked but empty. **Class: empty/dead. Drop.** |
| **SOVEREIGN-WAR-ROOM** | 22 | 37 | scheduled for owning migration gate. STAGE_4 merged `SOVEREIGN-WAR-ROOM/swr/`. Beginnings `packages/swr/` has 2 source files vs legacy's 8. **Class: runtime-source. PARTIAL — merged but shallow (6 swr files NOT carried).** |
| **source-docs** | 244 | 245 | not selected. 241 markdown. **Class: doc. CRITICAL — domain reference; "all docs of all kinds." Some content carried via MERGE_PROVENANCE. Preserve remainder as `docs/legacy-archive/source-docs/`.** |
| **src** | 981 | 2,179 | not selected. 2,179 files including `src/app/core/` (225 py files, 3.8MB). **Class: runtime-source. CRITICAL — `src/app/core/` is the largest single source gap.** |
| templates | 23 | 23 | not selected. **Class: doc. Drop or cherry-pick.** |
| **tarl** | 33 | 69 | not selected. Complete TARL compiler + runtime + adapters. **Class: runtime-source. CRITICAL — Beginnings has NO `packages/tarl/`. Complete subsystem missing.** |
| **tarl_os** | 39 | 46 | not selected. `*.thirsty` config files + bridge.py + implementation reports + tests. **Class: runtime-source + config. CRITICAL — no Beginnings counterpart.** |
| **temporal** | 8 | 16 | not selected. **Class: runtime-source. CRITICAL — no Beginnings counterpart; `.thirsty` Temporal workflows.** |
| test-artifacts | 1 | 41 | ignored per `.gitignore`. **Class: test-output. Drop.** |
| test-data | 5 | 5 | not selected. **Class: test-data. Drop.** |
| **tests** | 317 | 1,431 | not selected. 309 py tests across 19 subdirs (agents, attack_vectors, chaos, e2e, gradle_evolution, gui_e2e, inspection, integration, kernel, load, manual, monitoring, plugins, sase, security, temporal, thirstys_waterfall, utils). **Class: runtime-test. CRITICAL — Beginnings `packages/*/tests/` is per-package only; no integration/e2e/chaos/security tests equivalent.** |
| thirsty_lang | 1 | 0 | tracked but empty. **Class: empty. Drop — superseded by PyPI `thirsty-lang 0.1.4` per §1 decision #4.** |
| **unity** | 21 | 21 | not selected. **Class: app. DEFERRED per 2026-06-21 user instruction (Unity 3DOF). Flag for confirmation, do not auto-include.** |
| usb_installer | 4 | 4 | not selected. **Class: deploy-tool. Drop or preserve.** |
| utils | 12 | 24 | not selected. **Class: runtime-source. Preserve as `docs/legacy-archive/utils/`.** |
| validation | 18 | 18 | not selected. **Class: test-framework. Preserve as `docs/legacy-archive/validation/`.** |
| **web** | 153 | 29,043 | not selected. Of 29,043, 28,889 are `node_modules/` (~426MB). Real content: `hub-epstein/` (70 files), `site/` (49), `components/` (4), `app/` (6), `backend/` (2). Beginnings has `apps/` (Beginnings-only) and `packages/security/reference/`. **Class: web-source. PARTIAL — hub-epstein and site not carried; consider whether to preserve as `docs/legacy-archive/web/`.** |
| whitepaper | 1 | 1 | not selected. `whitepaper/THIRSTYS_ASYMMETRIC_SECURITY_WHITEPAPER.md`. **Class: paper. Verify if already in Beginnings `docs/reference/` via MERGE_PROVENANCE.** |
| wiki | 191 | 192 | not selected. 184 md + 1 py + 7 other. **Class: navigation. Per Addendum K §K.0, 16 substantial files were carried as `docs/reference/zenodo-summaries/` etc.; 174 lightweight stubs correctly excluded. PARTIAL — verify the 16 substantial files vs Beginnings `docs/reference/`.** |
| work | 1 | 0 | tracked but empty. **Class: empty. Drop.** |
| writer-reviewer-workflow | 8 | 10 | not selected. **Class: app. Preserve as `docs/legacy-archive/writer-reviewer-workflow/`.** |

---

## 2. Per-package gap detail (Beginnings packages vs legacy domain)

This is the heart of the inventory: per Beginnings package, which legacy files were NOT incorporated.

### 2.1 `packages/kernel/`

**Beginnings carries (8 source files):**
- `__init__.py`, `py.typed`, `deterministic_replay.py`, `event_spine.py`, `evidence_bundle.py`, `invariant_engine.py`, `invariant_severity.py`, `state_register.py`, `time_trust.py`, `types.py`

**Legacy `kernel/` (27 files) NOT carried:**
- `advanced_visualizations.py` (10.8KB)
- `dashboard_server.py` (7.4KB)
- `deception.py` (18.1KB) — deception detection
- `defcon_stress_test.py` (39.8KB) — DEFCON stress test
- `demo_comprehensive.py`, `demo_holographic.py`, `presentation_demo.py`
- `execution.py` (5.5KB) — kernel-side execution
- `holographic.py` (15.5KB)
- `learning_engine.py` (16.5KB)
- `performance_benchmark.py`
- `project_ai_bridge.py`
- `start_dashboard.py`, `start_kernel_service.py`
- `syscall_interception.py` (10.5KB) — eBPF-style syscall interception
- `tarl_codex_bridge.py` (561B) — bridge to TARL
- `tarl_gate.py` (1.2KB) — TARL gate enforcement
- `test_holographic.py`, `test_integration.py`
- `thirsty_super_kernel.py` (17.5KB) — super-kernel class
- `threat_detection.py` (16.3KB) — threat detection at kernel level
- `visualize.py` (15.2KB)
- `web_dashboard/{dashboard.js, index.html, style.css}` — web dashboard

**Legacy `src/app/core/` files that may map to kernel:**
- `cognition_kernel.py` (53.9KB) — cognition kernel
- `governance_kernel.py` (7.3KB) — governance kernel
- `kernel_adapters.py` (10.1KB) — kernel adapters
- `kernel_fuzz_harness.py` (14.3KB) — fuzz testing
- `kernel_integration.py` (15.5KB) — integration with subsystems
- `kernel_types.py` (2.9KB)
- `super_kernel.py` (16.9KB)
- `super_kernel_bootstrap.py` (5.4KB)
- `kernel/execution.py` (5.5KB)

**Disposition:** REBUILD-AS-RUNTIME for ~10 high-value files (`thirsty_super_kernel.py`, `syscall_interception.py`, `deception.py`, `threat_detection.py`, `learning_engine.py`, `holographic.py`, `defcon_stress_test.py`, `tarl_gate.py`, `kernel_integration.py`, `governance_kernel.py`). PRESERVE-AS-REFERENCE for the rest in `docs/legacy-archive/kernel/`.

### 2.2 `packages/governance/`

**Beginnings carries (4 source files):**
- `__init__.py`, `py.typed`, `asymmetric_security.py`, `engine.py`, `policy.py`, `types.py`

**Legacy `governance/` (89 files) NOT carried — critical:**
- `ai-mutation-governance-firewall/` (15 files: `__init__.py`, `config.py`, `errors.py`, `health.py`, `logging_config.py`, `main.py`, `metrics.py`, `middleware.py`, `models.py`, `repository.py`, `routes.py`, `security.py`, `services.py`)
- `core.py` (615B)
- `existential_proof.py` (21.5KB) — existential proof module
- `iron_path.py` (20.2KB) — Iron Path enforcement
- `singularity_override.py` (23.9KB) — singularity override
- `triumvirate_server.py` (21.9KB) — **TRIUMVIRATE SERVER** — central coordination
- `audit_log.yaml` (7.7KB) — live audit log
- `governance_state.json`
- `schemas/{agent_schema.tog, skill_schema.tog, threat_schema.tog}` — TOG schemas
- `sovereign_data/artifacts/20260203_*/` — 11 phase artifact bundles (~115KB each)

**Legacy `src/app/core/governance/` NOT carried:**
- `external_ecosystem_bridge.py` (9.3KB)
- `iron_path_executor.py` (34.2KB) — **LARGE** — Iron Path executor
- `pipeline.py` (53.8KB) — **LARGE** — governance pipeline
- `rate_limiter.py` (17.6KB)
- `validators.py` (7.5KB)

**Legacy `src/app/core/` other governance-related:**
- `asymmetric_security_engine.py` (22.7KB) — the symmetric-asymmetric security engine
- `god_tier_asymmetric_security.py` (27.6KB)
- `governance.py` (24.7KB)
- `governance_drift_monitor.py` (13.2KB)
- `governance_graph.py` (18.1KB)
- `governance_mode.py` (1.8KB)
- `governance_observability.py` (4.7KB)
- `governance_operational_extensions.py` (46.4KB) — **LARGE**
- `governance_outcomes.py` (2.5KB)
- `governance_quorum.py` (11.5KB)
- `guardian_approval_system.py` (44.7KB) — **LARGE**

**Disposition:** REBUILD-AS-RUNTIME for ~5 critical files (`triumvirate_server.py`, `iron_path_executor.py`, `pipeline.py`, `asymmetric_security_engine.py`, `guardian_approval_system.py`). PRESERVE-AS-REFERENCE for the rest in `docs/legacy-archive/governance/`.

### 2.3 `packages/capability/`

**Beginnings carries (1 source file):**
- `__init__.py`, `py.typed`, `authority.py`

**Legacy `src/app/core/` capability-related NOT carried:**
- `capability_token.py` (6.9KB) — token definition
- `tier_interfaces.py` (18KB) — tier interface definitions
- `execution_authorization.py` (6.7KB)
- `access_control.py` (2.3KB)
- `policy_decision.py` (3.5KB)
- `policy_registry.py` (9.1KB)
- `tier_governance_policies.py` (19.8KB)
- `platform_tiers.py` (18.6KB)

**Disposition:** REBUILD-AS-RUNTIME for `capability_token.py`, `tier_interfaces.py`. PRESERVE-AS-REFERENCE for the rest.

### 2.4 `packages/execution/`

**Beginnings carries (1 source file):**
- `__init__.py`, `py.typed`, `gate.py`

**Legacy `canonical/` (9 files) NOT carried:**
- `execution_trace.json` (10KB) — trace artifact
- `expected_outcome.md` (16.4KB) — expected outcomes
- `invariants.py` (20.9KB) — canonical invariants
- `replay.py` (23.5KB) — canonical replay
- `scenario.yaml` (16KB)
- `server.py` (9.8KB)
- `sovereign_proof.py` (3.1KB)
- `test_server.py` (4.4KB)
- `README.md` (26.7KB)

**Legacy `src/app/core/` execution-related NOT carried:**
- `execution_gate.py` (17.9KB) — legacy execution gate
- `execution_router.py` (4.3KB)
- `execution_authorization.py` (6.7KB)
- `polyglot_execution.py` (40.1KB) — **LARGE**
- `swr_activation.py` (8.1KB)
- `engine_registry.py` (10.1KB)
- `function_registry.py` (12.2KB)
- `interface_abstractions.py` (15.7KB)
- `interfaces.py` (10.9KB)
- `service.py` (beg-package only)
- `runtime/router.py` (3KB)
- `platform_tiers.py` (18.6KB)
- `shadow_execution_plane.py` (26.3KB) — shadow execution
- `shadow_types.py` (16.8KB)
- `shadow_resource_limiter.py` (15.3KB)
- `shadow_containment.py` (20.9KB)

**Disposition:** REBUILD-AS-RUNTIME for `execution_gate.py`, `replay.py`, `invariants.py`. PRESERVE-AS-REFERENCE for the rest in `docs/legacy-archive/execution/`.

### 2.5 `packages/companion/`

**Beginnings carries (1 source file):**
- `__init__.py`, `py.typed`, `service.py`

**Legacy `src/app/core/identity/`: MISSING (not in legacy). Identity lives at:**
- `src/app/core/identity.py` (33.3KB) — Identity system
- `src/app/core/meta_identity.py` (17.1KB)
- `src/app/core/identity_operational_extensions.py` (29.7KB)
- `src/app/core/bonding_protocol.py` (29.5KB)
- `src/app/core/relationship_model.py` (23.6KB)
- `src/app/core/conversation_context_engine.py` (30.3KB)
- `src/app/core/voice_bonding_protocol.py` (25.7KB)
- `src/app/core/voice_models.py` (18.2KB)
- `src/app/core/visual_bonding_controller.py` (22.5KB)
- `src/app/core/visual_cue_models.py` (21.8KB)
- `src/app/core/fates/fates.py` (18.3KB) — fates subsystem

**Legacy `src/app/core/nirl/` (NIRL — Neuro-Inspired Runtime Logic):**
- `__init__.py`, `antibody.py` (5KB), `forge.py` (7.3KB), `heart.py` (8.1KB), `mini_brain.py` (8.5KB)

**Legacy `data/fates/`:**
- `memory/THE_FATES.json` (9.9KB) — fates data
- `memory/THE_FATES.md` (1.9KB)

**Disposition:** REBUILD-AS-RUNTIME for `identity.py`, `nirl/*` (5 files), `fates.py`, `voice_bonding_protocol.py`. PRESERVE-AS-REFERENCE for the rest in `docs/legacy-archive/companion/`.

### 2.6 `packages/swr/`

**Beginnings carries (2 source files):**
- `__init__.py`, `py.typed`, `scenario.py`, `war_room.py`

**Legacy `SOVEREIGN-WAR-ROOM/swr/` (9 files):**
- ✅ `__init__.py` (847B) — carried (size mismatch with Beginnings)
- ✅ `scenario.py` (18.9KB) — carried
- ❌ `api.py` (7.9KB)
- ❌ `bundle.py` (8.9KB)
- ❌ `core.py` (12KB)
- ❌ `crypto.py` (9.2KB)
- ❌ `governance.py` (14.7KB)
- ❌ `proof.py` (12.5KB)
- ❌ `scoreboard.py` (16KB)

**Legacy `SOVEREIGN-WAR-ROOM/` non-swr files:**
- `cli.py`, `demo.py`, `DEPLOYMENT_SUMMARY.md`, `fleet_agent_5_tracking.md`, `GROUP_2_AGENT_8_REPORT.md`, `IMPLEMENTATION_COMPLETE.md`, `README.md`, `requirements.txt`
- `web/app.py`, `web/templates/dashboard.html`

**Disposition:** REBUILD-AS-RUNTIME for the 6 swr files not carried (api, bundle, core, crypto, governance, proof, scoreboard). Beginnings has 2 vs legacy's 8; merge was shallow.

### 2.7 `packages/atlas/`

**Beginnings carries (2 source files):**
- `__init__.py`, `py.typed`, `analysis.py`, `service.py`

**Legacy `atlas/` (69 files, 17 subdirs):**
- 17 subdirs: `analysis/`, `audit/`, `cli/`, `config/`, `core/`, `council/`, `data/`, `export/`, `governance/`, `logs/`, `reports/`, `safeguards/`, `safety/`, `sandbox/`, `schemas/`, `simulation/`, `verification/`
- Major Python files:
  - `core/bayesian_engine.py` (16.3KB)
  - `core/drivers/calculator.py` (24KB)
  - `core/drivers/driver_engine_10d.py` (19.8KB)
  - `core/graph/builder.py` (23.3KB)
  - `core/graph/temporal_graph.py` (20.2KB)
  - `core/ingestion/ingester.py` (20.3KB)
  - `core/ingestion/tier_classifier.py` (15.1KB)
  - `core/normalization/normalizer.py` (25.3KB)
  - `core/projections/simulator.py` (24.9KB)
  - `core/scoring/scorer.py` (23.1KB)
  - `cli/atlas_cli.py` (14.6KB)
  - `config/loader.py` (14.4KB)
  - `analysis/failure_surveillance.py` (16.9KB)
  - `analysis/sensitivity_analyzer.py` (15.9KB)
  - `audit/trail.py` (13.9KB)
  - `governance/constitutional_kernel.py` (31.7KB)
  - `safeguards/epistemic_safeguards.py` (19.9KB)

Plus 7 YAML config files (`drivers.yaml`, `penalties.yaml`, `safety.yaml`, `seeds.yaml`, `stacks.yaml`, `thresholds.yaml`, plus more).

**Disposition:** REBUILD-AS-RUNTIME for ALL 17 subdirs. This is the largest per-package gap. Beginnings has 2 source files vs legacy's 102 Python files + 7 YAML configs.

### 2.8 `packages/api/`

**Beginnings carries:** FastAPI gateway with Chimera routes (Stage 12). Builds on `execution/` and `governance/` integration.

**Legacy `api/` (8 files):**
- `Dockerfile`
- `__init__.py`
- `main.py`
- `openapi.json`
- `project-ai.postman_collection.json`
- `requirements.txt`
- `save_points_routes.py`
- `README.md`

**Disposition:** Beginnings API is already production. Legacy `api/` provides historical OpenAPI spec + postman collection. PRESERVE-AS-REFERENCE.

### 2.9 `packages/cli/`

**Beginnings carries:** Typer-based CLI (Stage 13).

**Legacy `agent_playbook/src/agent_playbook/cli.py`** — exists but flagged not selected.

**Disposition:** Verify if Beginnings CLI absorbed this content; if not, PRESERVE-AS-REFERENCE in `docs/legacy-archive/cli/`.

### 2.10 `packages/arbiter/`

**Beginnings carries:** `arbiter_gov.py` + `tests/test_arbiter_gov.py` (Stage 4.5).

**Legacy:** `agent_playbook/governance/GOVERNANCE_CORE.json` + related JSONs.

**Disposition:** Carried. No gap.

### 2.11 `packages/rlp/`

**Beginnings carries:** `rlp.py` + `governance_framework/` (Stage 4.6 + 4.8).

**Legacy `agent_playbook/src/agent_playbook/` NOT carried:**
- `cli.py`, `governance_core.py`, `provenance_verify.py`

**Disposition:** PRESERVE-AS-REFERENCE in `docs/legacy-archive/rlp/`. These are tooling/CLI, not policy.

### 2.12 `packages/security/`

**Beginnings carries:** `chimera.py`, `chimera_v2_2.py` (reference), `bridge.py` (Stage 4.7).

**Legacy `security/`: empty (just tracked placeholder).**

**Disposition:** No gap. Chimera integration is complete.

---

## 3. Legacy sub-systems with NO Beginnings counterpart

These are entire subsystems in legacy that have no package in Beginnings. Per v3 §30 (Minimum Governance Proof), if any are governance-bearing, they need their own package.

| Sub-system | Legacy location | Files | Disposition recommendation |
|---|---|---|---|
| **tarl/** | `tarl/` | 33 (21 py + adapter stubs + docs) | NEW PACKAGE: `packages/tarl/` |
| **tarl_os/** | `tarl_os/` | 39 (`.thirsty` config + bridge.py + tests) | NEW PACKAGE: `packages/tarl_os/` OR merge into `packages/tarl/` |
| **emergent-microservices/** | `emergent-microservices/` | 0 real (just `.ruff_cache`) | DROP — no source ever existed. Placeholder abandoned. |
| **temporal/** | `temporal/` | 16 (8 py + `.thirsty` workflows) | NEW PACKAGE: `packages/temporal/` OR integrate into `packages/execution/` |
| **conformance/** | `conformance/` | 17 (4 py + tests) | NEW PACKAGE: `packages/conformance/` OR add tests to existing packages |
| **monitoring/** | `monitoring/` | 2 (yaml only) | DROP — empty source |
| **h323_sec_profile/** | `h323_sec_profile/` | 25 (3 py + 18 md) | PRESERVE-AS-REFERENCE: `docs/legacy-archive/h323_sec_profile/` |
| **hardware_schematics/** | `hardware_schematics/` | 22 (md only) | PRESERVE-AS-REFERENCE: `docs/legacy-archive/hardware_schematics/` |
| **usb_installer/** | `usb_installer/` | 4 | PRESERVE-AS-REFERENCE |
| **writer-reviewer-workflow/** | `writer-reviewer-workflow/` | 10 | PRESERVE-AS-REFERENCE |
| **Project_ai_index/** | `Project_ai_index/` | 0 | DROP — empty tracked file |

### 3.1 Engines not represented in Beginnings

Legacy `engines/` has 10 engines. Beginnings has `packages/swr/` and `packages/atlas/`. **8 engines are not represented at all:**

| Engine | Legacy files | Notes |
|---|---|---|
| `ai_takeover` | many | AI takeover scenarios |
| `alien_invaders` | many | adversarial scenario |
| `cognitive_warfare` | many | cognitive warfare |
| `django_state` | many | state management |
| `emp_defense` | many | EMP defense scenario |
| `global_scenario` | many | global scenarios |
| `hydra_50` | many | 50-head hydra adversarial |
| `sovereign_war_room` | merged | ✅ in `packages/swr/` |
| `atlas` | merged | ✅ in `packages/atlas/` |

**Disposition:** PRESERVE-AS-REFERENCE: `docs/legacy-archive/engines/{ai_takeover,alien_invaders,cognitive_warfare,django_state,emp_defense,global_scenario,hydra_50}/`.

### 3.2 Top-level src/app/core/ — the largest single gap

3.8MB, 225 Python files. Some are already in Beginnings (deterministic_replay, event_spine, evidence_bundle, invariant_engine, state_register, capability_token stub, execution_gate). Most are not.

**High-value files NOT in Beginnings (recommend REBUILD-AS-RUNTIME):**
- `cognition_kernel.py` (53.9KB)
- `agent_operational_extensions.py` (33.3KB)
- `ai_systems.py` (44.2KB)
- `cerberus_hydra.py` (39.9KB)
- `cerberus_lockdown_controller.py` (12.7KB)
- `cerberus_spawn_constraints.py` (16KB)
- `cerberus_runtime_manager.py` (11.5KB)
- `cerberus_agent_process.py` (10.5KB)
- `cerberus_observability.py` (16.1KB)
- `cerberus_template_renderer.py` (8.7KB)
- `cloud_sync.py` (15.1KB)
- `command_override.py` (18.8KB)
- `comprehensive_security_expansion.py` (27.3KB)
- `bio_brain_mapper.py` (49.1KB)
- `conversation_context_engine.py` (30.3KB)
- `conversation_threat_register.py` (12.1KB)
- `council_hub.py` (24.9KB)
- `cybersecurity_knowledge.py` (30.8KB)
- `data_persistence.py` (23.9KB)
- `deepseek_v32_inference.py` (14.5KB)
- `degraded_mode.py` (6.1KB)
- `distributed_cluster_coordinator.py` (25KB)
- `distributed_event_streaming.py` (24.5KB)
- `ebpf_bridge.py` (2.8KB)
- `emergency_alert.py` (4.8KB)
- `engine_registry.py` (10.1KB)
- `enhanced_bootstrap.py` (23.7KB)
- `enhanced_data_sources.py` (13.3KB)
- `fates/fates.py` (18.3KB)
- `function_registry.py` (12.2KB)
- `genesis_reanchor.py` (6.4KB)
- `global_intelligence_library.py` (42.5KB)
- `global_scenario_engine.py` (40.9KB)
- `global_watch_tower.py` (20KB)
- `god_tier_command_center.py` (19.5KB)
- `god_tier_config.py` (13KB)
- `god_tier_integration.py` (23.4KB)
- `god_tier_integration_layer.py` (20.7KB)
- `god_tier_intelligence_system.py` (25.4KB)
- `governance_drift_monitor.py` (13.2KB)
- `governance_graph.py` (18.1KB)
- `governance_kernel.py` (7.3KB)
- `governance_mode.py` (1.8KB)
- `governance_observability.py` (4.7KB)
- `governance_outcomes.py` (2.5KB)
- `governance_quorum.py` (11.5KB)
- `guardian_approval_system.py` (44.7KB)
- `hardware_auto_discovery.py` (23.4KB)
- `health_monitoring_continuity.py` (24.5KB)
- `honeypot_detector.py` (17.5KB)
- `hydra_50_*` (8 files, 200KB main engine)
- `identity.py` (33.3KB)
- `identity_operational_extensions.py` (29.7KB)
- `image_generator.py` (16.2KB)
- `incident_responder.py` (20.4KB)
- `intelligence/` (5 files: attack_simulator, autonomy_engine, emotional_palette, meta_agents, intelligence_engine)
- `intent_detection.py` (1.2KB)
- `interface_operational_extensions.py` (32.4KB)
- `ip_blocking_system.py` (15.8KB)
- `kernel_adapters.py` (10.1KB)
- `kernel_fuzz_harness.py` (14.3KB)
- `kernel_integration.py` (15.5KB)
- `kernel_types.py` (2.9KB)
- `learning_paths.py` (4.4KB)
- `liara_bridge.py` (4.7KB)
- `live_metrics_dashboard.py` (27.5KB)
- `local_fbo.py` (20.2KB)
- `location_tracker.py` (4.9KB)
- `mcp_server.py` (37.9KB)
- `memory_engine.py` (37.1KB)
- `memory_operational_extensions.py` (27.7KB)
- `memory_optimization/` (10 files)
- `meta_identity.py` (17.1KB)
- `model_providers.py` (6.2KB)
- `multimodal_fusion.py` (18.8KB)
- `novel_security_scenarios.py` (26.1KB)
- `observability.py` (2.7KB)
- `octoreflex.py` (21KB)
- `openrouter_mock.py`, `openrouter_provider.py`
- `operational_substructure.py` (25.2KB)
- `optical_flow.py` (23.3KB)
- `perspective_engine.py` (23.9KB)
- `planetary_defense_monolith.py` (16.4KB)
- `policy_decision.py` (3.6KB)
- `policy_registry.py` (9.1KB)
- `rag_system.py` (17.5KB)
- `realtime_monitoring.py` (15.2KB)
- `rebirth_protocol.py` (16.6KB)
- `red_hat_expert_defense.py` (36.9KB)
- `red_team_stress_test.py` (36.9KB)
- `reflection_cycle.py` (24.2KB)
- `relationship_model.py` (23.6KB)
- `risingwave_integration.py` (14.8KB)
- `robotic_*` (3 files)
- `robustness_metrics.py` (24.8KB)
- `runtime/router.py` (3KB)
- `safe_allow_calibration.py` (11.6KB)
- `safety_levels.py` (26.7KB)
- `scenario_config.py` (8.6KB)
- `secrets_manager.py` (2.8KB)
- `secure_comms.py` (37.3KB)
- `security/` (auth.py, middleware.py)
- `security_enforcer.py` (27.9KB)
- `security_operations_center.py` (29.5KB)
- `security_resources.py` (4.6KB)
- `security_validator.py` (2.5KB)
- `semantic_collision.py` (3.6KB)
- `semantic_risk_classifier.py` (33.7KB)
- `sensor_fusion.py` (40.5KB)
- `services/` (execution_service.py, governance_service.py, memory_logging_service.py)
- `shadow_containment.py` (20.9KB)
- `shadow_execution_plane.py` (26.3KB)
- `shadow_resource_limiter.py` (15.3KB)
- `shadow_types.py` (16.8KB)
- `simulation_contingency_root.py` (13.9KB)
- `snn_integration.py` (21.1KB)
- `snn_mlops.py` (42.8KB)
- `storage.py` (20.7KB)
- `super_kernel.py` (16.9KB)
- `super_kernel_bootstrap.py` (5.4KB)
- `swr_activation.py` (8.1KB)
- `system_registry.py` (25.1KB)
- `tarl_operational_extensions.py` (28.8KB)
- `telemetry.py` (2.5KB)
- `tier_governance_policies.py` (19.8KB)
- `tier_health_dashboard.py` (18.5KB)
- `tier_interfaces.py` (18KB)
- `tier_performance_monitor.py` (21.5KB)
- `time_trust.py` (5.8KB)
- `tscg_codec.py` (15.8KB)
- `unified_integration_bus.py` (8.5KB)
- `user_manager.py` (15.1KB)
- `validate_constitution.py` (25KB)
- `visual_bonding_controller.py` (22.5KB)
- `visual_cue_models.py` (21.8KB)
- `voice_bonding_protocol.py` (25.7KB)
- `voice_models.py` (18.2KB)
- `waterfall_filter.py` (4.3KB)

### 3.3 Adversarial test corpus (313 files)

Legacy `adversarial_tests/` has 313/326 real files = **96% real test scenarios**:
- `transcripts/garak/` (16 files): jailbreak, injection, leakage, malicioususe, encoding, goodware, toxicity
- `transcripts/jbb/` (40 files): JailbreakBench scenarios
- `transcripts/hydra/` (200 files): 50-head hydra attacks
- `transcripts/multiturn/` (15 files): multi-turn attacks
- `multi_turn/scenarios/` (15 YAML)
- `garak/run_garak.py`, `jbb/run_jbb.py`, `hydra/run_hydra.py`
- `galahad_model.py`, `custom_prompts.yaml`, `hydra_dataset.json`

**Disposition:** PRESERVE-AS-REFERENCE in `docs/legacy-archive/adversarial_tests/`. Beginnings' 312/312 security matrix in `STAGE_18_ACCEPTANCE.md` is the SAME matrix per `governance.build_attack_catalog()` — so these transcripts are the input catalog.

### 3.4 Test infrastructure gap (309 .py files)

Legacy `tests/` has 309 Python tests across 19 subdirs:
- `agents/`, `attack_vectors/`, `chaos/`, `e2e/`, `gradle_evolution/`, `gui_e2e/`, `inspection/`, `integration/`, `kernel/`, `load/`, `manual/`, `monitoring/`, `plugins/`, `sase/`, `security/`, `temporal/`, `thirstys_waterfall/`, `utils/`

Beginnings has `packages/*/tests/` — only per-package unit tests. NO equivalent of:
- `tests/integration/` (2 py files)
- `tests/e2e/` (6 py)
- `tests/chaos/` (1 py)
- `tests/security/` (1 py)
- `tests/gradle_evolution/` (9 py)
- `tests/attack_vectors/` (0 py, but matches adversarial_tests)

**Disposition:** REBUILD-AS-RUNTIME for integration + e2e tests. Add `tests/` directory at repo root with `unit/`, `integration/`, `e2e/`, `chaos/`, `security/` subdirs per the Beginnings repo blueprint (§15 of v3).

---

## 4. Reference and paper coverage

Per `MERGE_PROVENANCE.md`, Beginnings `docs/reference/` has **150 artifacts** sourced from legacy + Papers directory. Already covered:
- 21 Zenodo DOI papers
- AGI Charter v2.3 (canonical)
- Asymmetric Offense, Constitutional Code Store, Iron Path Executor
- Legion Commission, NIRL Spec, OctoReflex, TARL, TSCG-B
- Genesis (consolidated from 3 orphan PDFs)
- Antiquity/attestations (4 chat model attestations)
- OMPT (website content)
- Many drafts and superseded versions

**Legacy `source-docs/` (244 markdown):** Domain-organized reference material. Categories: `agents`, `api`, `cli-automation`, `configuration`, `constitutional`, `core`, `data-models`, `deployment`, `error-handling`, `gui`, `infrastructure`, `integrations`, `misc`, `monitoring`, `performance`, `plugins`, `security`, `supporting`. NOT carried. **Disposition:** PRESERVE-AS-REFERENCE: `docs/legacy-archive/source-docs/`.

**Legacy `wiki/` (192 files):** Per Addendum K §K.0, 16 substantial files were carried as `docs/reference/zenodo-summaries/`, `docs/reference/PUBLICATION_TIMELINE.md`, etc. 174 lightweight stubs were excluded. **Disposition:** PARTIAL — already correctly handled.

**Legacy `whitepaper/` (1 file):** `THIRSTYS_ASYMMETRIC_SECURITY_WHITEPAPER.md`. Verify against `MERGE_PROVENANCE.md` (currently not in the 150-row list). If not carried, add as `docs/reference/`.

---

## 5. Operational-history material

These don't rebuild; they preserve the project's actual history. Per v3 §19 (Continuity Map), operational history is essential.

- `recovery/` (47 files) — phase promotion deltas
- `audit_reports/` (120 files, ignored)
- `automation-backups/` (92 files)
- `buildSrc/` (141 files)
- `gradle-evolution/` (87 files)
- `gradle_evolution/` (3 files, old)
- `plans/plan.md`
- `.tmp/neo_exec_*.bat` (82 execution logs)

**Disposition:** PRESERVE-AS-REFERENCE in `docs/legacy-archive/{recovery, audit_reports, automation-backups, buildSrc, gradle-evolution, plans, execution_logs}/`. None of these are runtime source.

---

## 6. Sub-systems to NEW-PACKAGE (per v3 §30)

These legacy sub-systems need their own Beginnings package because they have non-trivial runtime code, not just docs:

| Legacy sub-system | Recommendation |
|---|---|
| `tarl/` (33 files, 21 py) | NEW `packages/tarl/` |
| `tarl_os/` (39 files, mostly `.thirsty`) | NEW `packages/tarl_os/` OR merge with tarl |
| `temporal/` (16 files, 8 py + workflows) | NEW `packages/temporal/` |
| `conformance/` (17 files, 4 py + tests) | NEW `packages/conformance/` OR add to existing test infra |
| `kernel_adapters.py`, `kernel_integration.py`, `super_kernel.py` | EXTEND existing `packages/kernel/` |
| `cognition_kernel.py` | EXTEND existing `packages/companion/` |
| `execution_gate.py`, `polyglot_execution.py` | EXTEND existing `packages/execution/` |
| `identity.py`, `nirl/`, `fates/` | EXTEND existing `packages/companion/` |
| `governance/pipeline.py`, `iron_path_executor.py`, `triumvirate_server.py` | EXTEND existing `packages/governance/` |

---

## 7. Aggregate rebuild scope (estimate)

| Disposition | File count (approx) | Storage |
|---|---|---|
| REBUILD-AS-RUNTIME | ~150-200 py + YAMLs | ~3-5 MB |
| PRESERVE-AS-REFERENCE | ~3,000 files | ~50 MB |
| DROP (cache/ide/duplicate) | ~67,800 files | ~1 GB (mostly `node_modules`, `.venv*`) |

**REBUILD-AS-RUNTIME priority order:**
1. `kernel/{thirsty_super_kernel, syscall_interception, deception, threat_detection, learning_engine, holographic, defcon_stress_test, tarl_gate}.py` (8 files, ~140KB)
2. `governance/{triumvirate_server, iron_path_executor, pipeline, asymmetric_security_engine, guardian_approval_system}.py` (5 files, ~180KB)
3. `src/app/core/execution_gate.py` (1 file, 18KB)
4. `src/app/core/identity.py` + `nirl/` (6 files, ~70KB)
5. `atlas/core/`, `atlas/cli/`, `atlas/config/`, `atlas/audit/`, `atlas/safeguards/`, `atlas/governance/` (full atlas subsystem rebuild)
6. `SOVEREIGN-WAR-ROOM/swr/{api,bundle,core,crypto,governance,proof,scoreboard}.py` (7 files, ~80KB)
7. `tarl/` (33 files, 21 py)
8. `tarl_os/` (39 files)
9. `temporal/` (16 files)

---

## 8. Open questions to resolve before rebuild

1. **Unity 3DOF:** User said skip 2026-06-21. Re-include `unity/` (21 files)? → **RESOLVED 2026-06-25 (Phase B):** Default DROP per user's 2026-06-21 instruction. 21 files archived to `docs/legacy-archive/unity/` (SHA-256 verified) as preserved-as-reference.
2. **Web frontend:** Beginnings has `apps/` (separate from packages). Carry `web/hub-epstein/` and `web/site/` as `docs/legacy-archive/web/`? → **RESOLVED 2026-06-25 (Phase A):** 119 files archived to `docs/legacy-archive/web/`, SHA-256 verified. See `APPS_INVENTORY.md` for `apps/web/` distinction.
3. **TARL_OS `.thirsty` config files:** Carry these or treat as data? → **RESOLVED-PARTIAL 2026-06-25 (Phase A):** 27 `.thirsty` data files archived to `docs/legacy-archive/tarl_os_config/`, SHA-256 verified. `*.py` rebuild deferred to Phase H/I.
4. **`emergent-microservices/`:** Confirm DROP — appears never to have had source. → **RESOLVED 2026-06-25 (Phase B):** DROP CONFIRMED. 42 files on disk, 0 source files (all `.ruff_cache/` debris), 7 empty subdirs. See `docs/legacy-archive/EMERGENT_MICROSERVICES_DROP_CONFIRMATION.md`.
5. **Cerebus subsystem:** 9 cerberus_*.py files (~140KB). Carry into `packages/governance/` or new `packages/cerberus/`? → **RESOLVED 2026-06-25 (Phase F):** Default NEW `packages/cerberus/` chosen. Three source modules (~640 LOC) + 44 tests: `CerberusAgent` (per-agent state holder over StateRegister), `SpawnConstraints` + `SpawnPolicy` Protocol (fail-closed spawn gate), `LockdownController` + `LockdownTrigger` Protocol (emergency halt). All fail-closed, downward-only deps, pluggable seams, single audit chain via capability.consume.
6. **Hydra 50:** `engines/hydra_50/` + 7 `hydra_50_*.py` files in `src/app/core/`. Carry as new `packages/hydra_50/`? → **RESOLVED 2026-06-25 (Phase G):** Default NEW `packages/hydra_50/` chosen. Three source modules (~500 LOC) + 42 tests: `ThreatScenario` TypedDict + `make_scenario` (fail-closed validation), `EscalationLadder` over `kernel.StateRegister` (atomic level transitions 0→3, append-only history), `ScenarioEvaluator` + `EvaluationStrategy` Protocol (pluggable readiness gate). All fail-closed, downward-only deps (kernel-only), pluggable seams.
7. **Cognition subsystem:** `cognition_kernel.py` (54KB) + `cognition/` dir (17 stub files). Carry into `packages/companion/` or new `packages/cognition/`? → **RESOLVED 2026-06-25 (Phase E):** Default INTO `packages/companion/` as `companion/cognition.py` — Q7 closure. Minimum viable port: `CognitionController`, `Thought` validation, `CognitionStrategy` Protocol, atomic state via `kernel.StateRegister`. Fail-closed. See `packages/companion/src/companion/cognition.py`.
8. **Beginnings `apps/` vs `packages/`:** What is currently in `apps/` (Beginnings-only directory)? → **RESOLVED 2026-06-25 (Phase A):** `apps/` is the application tier (desktop PyQt6, services, android Kotlin, web React/Vite, web-static). Zero upward imports into `packages/governance|execution|capability` verified. See `APPS_INVENTORY.md`.

---

## 9. Sources cited (v3 §11 Evidence Before Claims)

- `git -C T:\00-Active\Project-AI-main ls-files | wc -l` = 5,276
- `find T:\00-Active\Project-AI-main -type f | wc -l` = 71,066
- `git -C T:\00-Active\Project-AI-Beginnings ls-files | wc -l` = 516
- `find T:\00-Active\Project-AI-Beginnings -type f | wc -l` = 28,436
- `T:\00-Active\Project-AI-Beginnings\docs\reference\DROPPED_FILES_MANIFEST.md` (5,284 lines, all 5,276 tracked paths dispositioned)
- `T:\00-Active\Project-AI-Beginnings\docs\reference\MERGE_PROVENANCE.md` (150 artifact rows)
- `T:\00-Active\Project-AI-Beginnings\docs\reference\INGEST_MANIFEST.md`
- `T:\00-Active\Project-AI-Beginnings\docs\reference\INGEST_SKIPPED.md` (6 explicit skips, all credentials)
- `T:\00-Active\Project-AI-Beginnings\docs\reference\ORPHAN_PAPERS.md` (4 entries, 2 are Genesis continuations)
- `T:\00-Active\Project-AI-Beginnings\docs\internal\REBUILD_EXECUTION_PLAN.md` (active authority)
- `T:\00-Active\Project-AI-Beginnings\docs\internal\STAGE_18_ACCEPTANCE.md` (Stage 18 local acceptance, remote CI billing blocker)
- `T:\00-Active\Project-AI-Beginnings\docs\internal\STAGE_4_MERGE_REPORT.json` (SWR + atlas merge)
- `T:\00-Active\Project-AI-Beginnings\docs\internal\STAGE_4_7_4_8_IMPORT_REPORT.json` (chimera + governance_framework)
- `T:\00-Active\Project-AI-Beginnings\docs\internal\LEGACY_SOURCE_STATE.json`
- All Beginnings `packages/*/src/` enumerations (read directly)
- All legacy `*/` directory enumerations (read directly via os.walk)

---

## 10. Self-report (v3 §35)

```
Mode: governance system (discovery)
Created:
  - T:\00-Active\Project-AI-Beginnings\docs\operations\LEGACY_GAP_INVENTORY.md (this file)
  - T:\00-Active\Project-AI-Beginnings\docs\operations\LEGACY_GAP_INVENTORY.csv (machine-readable)
  - T:\00-Active\Project-AI-Beginnings\docs\operations\LEGACY_GAP_INVENTORY_VERIFICATION.md (hostile review)
Modified: T:\00-Active\Project-AI-Beginnings\docs\operations\CONTINUITY_MAP.md (updated)
Deleted: None.
Verified:
  - Legacy 71,066 files on disk, 5,276 tracked, 100% dispositioned in DROPPED_FILES_MANIFEST
  - Beginnings 28,436 files on disk, 516 tracked, 13 packages, ~95 source .py files
  - Per-package source file counts: kernel 8/27+225 (in src/app/core), governance 4/89+39 (in src/app/core), swr 2/8, atlas 2/102, capability 1/scattered, execution 1/scattered, companion 1/scattered
  - Sub-systems with NO Beginnings counterpart: tarl, tarl_os, temporal, h323_sec_profile, hardware_schematics, usb_installer, conformance, monitoring, partial agent_playbook
  - emergent-microservices = 0 real source files (only .ruff_cache debris)
  - adversarial_tests = 313/326 (96%) real test transcripts
  - tests/ = 309 py tests in 19 subdirs (no Beginnings equivalent for integration/e2e/chaos)
Failed: None.
Not verified:
  - SHA-256 spot-check against MERGE_PROVENANCE.md for every legacy path (sampled; not exhaustive)
  - Per-file read of every Python file in legacy src/app/core/ (sampled high-value; full read would consume too much context)
  - Whether `apps/` in Beginnings (Beginnings-only dir) corresponds to any legacy dir (not yet inspected this session)
Risks:
  - Risk: Recommendations in §7 may exceed user's intended rebuild scope. Impact: scope creep. Action: surfaced open questions in §8; no rebuild started.
  - Risk: Some legacy files I classified as REBUILD-AS-RUNTIME may already be partially represented in Beginnings via dynamic import or dependency that I didn't trace. Impact: duplicate work. Action: per-package rebuild plan would need a deep import-graph check before any rebuild.
  - Risk: 65,894 untracked-by-git files mostly ignored; I sampled by directory but did not walk every path. Impact: a small number of items might be missed. Action: my classification is by directory, not by file; per-file reconciliation can be a follow-on.
Continuity map: docs/operations/CONTINUITY_MAP.md (updated)
Remaining:
  - User to answer the 8 open questions in §8
  - User to authorize next plan: which legacy content to rebuild vs preserve vs drop
  - After user direction: write separate per-package rebuild plan
Commands run:
  - find / du / git ls-files / git rev-parse on both repos (read-only)
  - read_file on DROPPED_FILES_MANIFEST.md (head), MERGE_PROVENANCE.md, INGEST_MANIFEST.md, INGEST_SKIPPED.md, ORPHAN_PAPERS.md, REBUILD_EXECUTION_PLAN.md, STAGE_18_ACCEPTANCE.md
  - Python script walk of every legacy top-level dir (Phase B): 91 entries, 71,066 files
  - Python script per-domain legacy surface vs Beginnings package (Phase C)
  - Python script per-package deep dive (Phase D)
  - Python script filtered emergent-microservices + src/app/core walk
  - Python script legacy web/ + tests/ + scripts/ + key singleton inspection
Safe to continue: yes (for clarification + per-package rebuild plan authoring);
NOT for actual code edits in any package without user direction
```
