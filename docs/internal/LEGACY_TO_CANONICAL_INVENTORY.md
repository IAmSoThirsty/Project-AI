# Legacy → Canonical Inventory

**Status:** DISCOVERY + MAP (no source written yet)
**Authority:** User directive 2026-06-30 ("every single scenario engine will be integrated into the repo")
**Scope:** Full surface mapping of `T:\00-Active\Project-AI-main` against `T:\00-Active\Project-AI-Beginnings`
**Date:** 2026-06-30
**Author:** Hermes (Quencher session)

---

## 0. Method

Two parallel inventories. Every legacy item gets a row; every canonical
counterpart (or "NOT YET IN CANONICAL" marker) gets a row alongside it.
Dispositions: **PORT** (faithful port needed), **SUPERSEDED** (already
rebuilt in canonical with stricter invariants), **REFERENCE** (kept as
docs/reference, not rebuilt as code), **DROPPED** (empty / cache / generated),
**ALREADY-INTEGRATED** (no work needed).

**Numbers as of 2026-06-30:**

| Repo | Tracked files | Top-level entries | Python files | Markdown files |
|---|---|---|---|---|
| `T:\00-Active\Project-AI-main` | 5,276 | 166 | 2,549 | 2,459 |
| `T:\00-Active\Project-AI-Beginnings` | (growing) | ~30 | 14,930 (tests dominate) | 2,459 |

---

## 1. Top-level domain map (166 main entries → 30 canonical)

| # | Legacy (Project-AI-main) | Canonical (Project-AI-Beginnings) | Disposition |
|---|---|---|---|
| 1 | `adversarial_tests/` | n/a | **REFERENCE** — keep in legacy-archive; read for red-team patterns |
| 2 | `agent_playbook/` | spread across `packages/*` (per `MERGE_PROVENANCE.md`) | **ALREADY-INTEGRATED** — 20 integration files already absorbed into `kernel`/`governance`/`execution` per strategy doc |
| 3 | `android/` | `apps/android/` | **ALREADY-INTEGRATED** — modernized; legacy is reference |
| 4 | `api/` | `packages/api/` | **ALREADY-INTEGRATED** — FastAPI gateway built from scratch |
| 5 | `app/` (Flutter) | n/a | **DROP** — Flutter app not part of canonical stack |
| 6 | `archive/` (historical cleanup) | n/a | **DROP** — already in legacy history; canonical has `docs/legacy-archive/` for the kept pieces |
| 7 | `atlas/` | `packages/atlas/` | **PARTIAL** — J2.1–J2.9 ported; staging residue below (item 31) |
| 8 | `audit_reports/`, `ci-reports/`, `automation-reports/`, `automation-backups/`, `baseline/` | n/a | **DROP** — generated artifacts; reproducible from canonical |
| 9 | `benchmarks/` | n/a | **REFERENCE** — keep in legacy-archive |
| 10 | `build/`, `buildSrc/`, `gradle/`, `gradle-evolution/`, `gradle_evolution/`, `gradlew*`, `build.gradle*`, `settings.gradle*`, `build.tarl`, `build-wrapper.*` | `Cargo.toml`/`Cargo.lock` (Rust `crates/`) + `pyproject.toml` (Python `packages/`) | **SUPERSEDED** — Gradle/Kotlin dropped; canonical is Rust + Python + TypeScript only |
| 11 | `canonical/` (acceptance oracle) | `tools/canonical_replay.py` + `tools/acceptance_gate.*` | **ALREADY-INTEGRATED** — canonical replay system; J2.9 added `replay_system.py` |
| 12 | `cognition/` | `packages/companion/src/companion/cognition.py` | **ALREADY-INTEGRATED** — cognition kernel is part of companion |
| 13 | `config/` | `packages/*/src/*/config.py` (per package) | **ALREADY-INTEGRATED** — per-package config is canonical |
| 14 | `conformance/` | n/a | **REFERENCE** — keep in legacy-archive |
| 15 | `data/` (runtime state, ledgers, logs) | n/a | **DROP** — runtime state, generated; never tracked in canonical |
| 16 | `dataview-queries/` | n/a | **DROP** — Obsidian-vault artifact |
| 17 | `demos/` | n/a | **REFERENCE** — keep in legacy-archive |
| 18 | `desktop/` (Electron + PyQt) | `apps/desktop/` (Python) | **PARTIAL** — Electron dropped, PyQt6 portion ported; verify what main has that canonical doesn't |
| 19 | `diagrams/`, `graph-views/` | `docs/diagrams/` (Mermaid generated) | **SUPERSEDED** — canonical generates diagrams from source |
| 20 | `docs/` | `docs/` (index/internal/operations/reference/runbooks/audit/deployment) | **ALREADY-INTEGRATED** — canonical `docs/reference/` has all published papers per `MERGE_PROVENANCE.md` |
| 21 | `e2e/` | `tests/` (integration tests) | **ALREADY-INTEGRATED** — e2e replaced by `tests/test_*_integration.py` |
| 22 | `emergent-microservices/` | n/a | **DROPPED** — confirmed zero source content (Q4 resolution, 2026-06-25) |
| 23 | `engines/` | `packages/atlas/`, `packages/swr/`, `packages/hydra_50/`, others | **PARTIAL** — see §2 below |
| 24 | `examples/` | `packages/temporal/examples/` + test fixtures | **ALREADY-INTEGRATED** — see §3 |
| 25 | `governance/` | `packages/governance/` | **ALREADY-INTEGRATED** |
| 26 | `gradle.properties`, `gradle-evolution` | n/a | **DROP** — Gradle dropped |
| 27 | `h323_sec_profile/` | n/a | **REFERENCE** — keep in legacy-archive; telecom artifact, not project core |
| 28 | `hardware_schematics/` | n/a | **REFERENCE** — keep in legacy-archive |
| 29 | `helm/` | `helm/project-ai/` | **ALREADY-INTEGRATED** — K8s manifests exist in canonical |
| 30 | `indexes/` | n/a | **DROP** — Obsidian-vault artifact |
| 31 | `integrations/` (`openclaw/`, `thirstys_trading_hub/`, `thirsty_lang_complete/`) | n/a | **PORT** — none in canonical yet; need audit per integration |
| 32 | `kernel/` | `packages/kernel/` | **ALREADY-INTEGRATED** |
| 33 | `linguist-submission/` | n/a | **REFERENCE** — GitHub Linguist grammar submission, archive only |
| 34 | `monitoring/` (Grafana) | `crates/genesis-emitter/` + observability hooks | **PARTIAL** — see §4 |
| 35 | `package.json`, `package-lock.json`, `pnpm-*` | `package.json`, `pnpm-workspace.yaml`, `pnpm-lock.yaml`, `tsconfig.web.json` | **ALREADY-INTEGRATED** — pnpm workspace exists in canonical |
| 36 | `plans/`, `policies/`, `relationships/` | `docs/operations/`, `packages/rlp/governance_framework/policies/`, `docs/index/wiki-pointer-map.md` | **PARTIAL** — policies partially ported into `rlp/governance_framework/policies/`; `plans/` and `relationships/` are Obsidian-vault artifacts (DROP) |
| 37 | `project_ai/` | `packages/*` (full reorg) | **ALREADY-INTEGRATED** — old `project_ai/` engine split into 16 packages |
| 38 | `Project_ai_index/`, `Project-Ai/` (Obsidian vault) | n/a | **DROP** — Obsidian-vault per user instruction |
| 39 | `recovery/` | n/a | **REFERENCE** — recovery notes; archive only |
| 40 | `scripts/` | `tools/` | **ALREADY-INTEGRATED** — scripts renamed to `tools/` and re-categorized |
| 41 | `security/` | `packages/security/` | **ALREADY-INTEGRATED** |
| 42 | `source-docs/` | `docs/reference/` | **ALREADY-INTEGRATED** — reference docs copied per `MERGE_PROVENANCE.md` |
| 43 | `SOVEREIGN-WAR-ROOM/` (top-level duplicate) | `packages/swr/` (partial) + `_staging/swr/` (full legacy mirror) | **PORT** — see §5 |
| 44 | `tarl/`, `tarl_os/` | `packages/tarl/` | **PARTIAL** — `tarl/` ported (H0–H3); `tarl_os/` configs in `docs/legacy-archive/tarl_os_config/` |
| 45 | `templates/` | n/a | **REFERENCE** — Obsidian templates; archive only |
| 46 | `temporal/` | `packages/temporal/` | **ALREADY-INTEGRATED** |
| 47 | `test-artifacts/`, `test-data/` | n/a | **DROP** — test run outputs, never tracked in canonical |
| 48 | `tests/` | `tests/` (integration) + `packages/*/tests/` (unit) | **ALREADY-INTEGRATED** — tests reorganized per-package |
| 49 | `thirsty_lang/` | PyPI dep `thirsty-lang==0.1.4` | **ALREADY-INTEGRATED** — runtime comes from PyPI, not in-repo source |
| 50 | `tools/` | `tools/` | **ALREADY-INTEGRATED** — tools reorganized |
| 51 | `unity/`, `usb_installer/` | n/a | **REFERENCE** — keep in legacy-archive |
| 52 | `utils/`, `validation/` | `packages/*/src/*/` utilities | **ALREADY-INTEGRATED** — utilities distributed to packages |
| 53 | `vault/` (top-level) | n/a (separate repo: `T:\Project-AI-vault\`) | **OUT-OF-SCOPE** — separate repo, not under `Project-AI-main/` |
| 54 | `web/` (Vite/React) | `apps/web/` (docs-portal, proof-portal, shared) + `web/hub-epstein` (Vite) | **PARTIAL** — `web/` partially in canonical; `web/hub-epstein` has unique content (referenced by `web-static`?) |
| 55 | `whitepaper/`, `wiki/` | `docs/reference/` + `docs/index/wiki-pointer-map.md` | **ALREADY-INTEGRATED** — wiki content absorbed into `wiki-pointer-map.md`; whitepapers into `docs/reference/` |
| 56 | `work/`, `writer-reviewer-workflow/` | n/a | **REFERENCE** — workflow notes, archive only |

### 1a. Root-level config files (matched)

| Legacy file | Canonical | Disposition |
|---|---|---|
| `pyproject.toml` | `pyproject.toml` | **SUPERSEDED** — workspace pyproject is canonical |
| `requirements.in`, `requirements.lock`, `requirements.txt`, `requirements-dev.txt` | `uv.lock` | **SUPERSEDED** — uv is canonical |
| `setup.py`, `setup.cfg`, `MANIFEST.in` | per-package `pyproject.toml` | **SUPERSEDED** — hatchling per-package |
| `Makefile` | `tools/*.sh` + `tools/*.ps1` | **SUPERSEDED** — no Makefile in canonical |
| `Dockerfile` (root) | `docker/api.Dockerfile`, `docker/service.Dockerfile`, `docker/web.Dockerfile`, `docker/genesis.Dockerfile` | **ALREADY-INTEGRATED** — per-service Dockerfiles |
| `docker-compose.yml`, `docker-compose.override.yml` | `compose.yaml` | **ALREADY-INTEGRATED** |
| `AGENTS.md` | `AGENTS.md` | **ALREADY-INTEGRATED** — rewritten per AGENTS.md v3 |
| `CHANGELOG.md` | `CHANGELOG.md` | **ALREADY-INTEGRATED** |
| `README.md`, `README_HONEST.md`, `README_ORIGINAL_BACKUP.md`, `DEVELOPER_QUICK_REFERENCE.md`, `API_QUICK_REFERENCE.md` | `README.md` | **SUPERSEDED** — single canonical README |
| `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CODEOWNERS`, `LICENSE` | same names | **ALREADY-INTEGRATED** — kept where applicable |
| `mcp.json` | n/a | **REFERENCE** — MCP server config, keep in legacy-archive |
| `app-config.json` | per-package config | **SUPERSEDED** |
| `quickstart.py`, `bootstrap.py`, `start_api.py` | `tools/verify_pre_deployment.py`, `tools/acceptance_gate.sh` | **SUPERSEDED** — single acceptance gate |
| `extract_with_permissions.py`, `export_baseline.py`, `add_*links*.py/ps1`, `generate_*pdf.py`, `agent_07*link*.py` | n/a | **DROP** — one-shot link/PDF tools, not needed in canonical |
| `install_production.ps1` | `tools/acceptance_gate.ps1` + `docs/deployment/PRE_DEPLOYMENT_CHECKLIST.md` | **SUPERSEDED** |
| `LAUNCH_MISSION_CONTROL.bat` | n/a | **DROP** — Windows-only launcher not needed |
| `run_shadow_tests.bat` | n/a | **DROP** — shadow test driver not in canonical |
| `test_connection.py`, `test_memory_security_audit.py`, `test_mock_openrouter.py`, `test_openrouter_integration.py`, `test_path_traversal_fix.py` | `tests/test_*_integration.py` | **ALREADY-INTEGRATED** — moved into proper integration test files |
| `page1_preview.png` | n/a | **DROP** — preview image, not needed |
| `audit.log`, `remediation_integration.log`, `shadow_test_output.txt`, `session.sqlite` | n/a | **DROP** — runtime state, never tracked |
| `PR_Overseer.prompt.yml` | n/a | **REFERENCE** — CI prompt file, keep in legacy-archive |
| `project_ai_cli.py` | `packages/cli/src/project_ai_cli/` | **ALREADY-INTEGRATED** |

---

## 2. `engines/` — the critical integration surface

`engines/` in main has 8 sub-packages. Mapping:

| Legacy engine | LOC (.py) | Canonical target | Disposition |
|---|---|---|---|
| `engines/ai_takeover/` | 4 + modules + schemas | `packages/ai_takeover/` (new) | **PORT** — scenario engine, not yet in canonical |
| `engines/alien_invaders/` | 4 + modules + schemas | `packages/alien_invaders/` (new) | **PORT** — scenario engine, not yet in canonical |
| `engines/cognitive_warfare/` | 2 | `packages/cognitive_warfare/` (new) | **PORT** — scenario engine, not yet in canonical |
| `engines/django_state/` | 2 + kernel + modules + schemas | `packages/django_state/` (new) | **PORT** — scenario engine, not yet in canonical |
| `engines/emp_defense/` | 3 + modules + schemas | `packages/emp_defense/` (new) | **PORT** — scenario engine, not yet in canonical |
| `engines/global_scenario/` | 3 | `packages/global_scenario/` (new) | **PORT** — scenario engine, not yet in canonical |
| `engines/hydra_50/` | 13 | `packages/hydra_50/` | **ALREADY-INTEGRATED** — fully ported (Phase F/G) |
| `engines/sovereign_war_room/` | 21 (incl. swr/ subpkg + web/ + tests) | `packages/swr/` (partial) + `_staging/swr/` (full) | **PORT** — see §5 |
| `engines/atlas/` | 51 (overlaps with `atlas/`) | `packages/atlas/` (most) + `_staging/atlas/` (residue) | **SUPERSEDED** for most; see §6 |

### 2a. Each scenario engine — file-by-file inventory

Per the user directive, EVERY scenario engine is in scope. Below is the
per-file inventory of each, with what canonical currently has (typically
nothing) and the per-file port plan.

**`engines/ai_takeover/`** — 4 .py + `modules/` + `schemas/` + `tests/` + `docs/`:
- `__init__.py`, `engine.py`, `demo.py`, `demo_reviewer_trap.py`
- `modules/no_win_proof.py`
- `tests/test_proof_and_trap.py`
- `docs/README_2026.md`, `README.md`, `README_COMPLETE.md`, `TECHNICAL_FIXES.md`, `VERIFICATION_RESULTS.md`
- `schemas/` (JSON schemas)
- `.github/` (workflows)
- **Plan:** New `packages/ai_takeover/` workspace member, faithful port with strict typing per the J2 sub-phase pattern.

**`engines/alien_invaders/`** — 4 .py + `modules/` + `schemas/` + `tests/` + `artifacts/` + `docs/`:
- `__init__.py`, `engine.py`, `integration.py`, `run_simulation.py`
- `modules/`
- `tests/`
- `artifacts/`
- `docs/`
- `schemas/`
- **Plan:** New `packages/alien_invaders/`, faithful port.

**`engines/cognitive_warfare/`** — 2 .py:
- `__init__.py`, `cognitive_warfare_framework.py`
- **Plan:** New `packages/cognitive_warfare/`, faithful port.

**`engines/django_state/`** — 2 .py + `kernel/` + `modules/` + `schemas/` + `tests/` + `evaluation/` + `docs/`:
- `__init__.py`, `engine.py`
- `kernel/`, `modules/`, `schemas/`, `tests/`, `evaluation/`, `docs/`
- **Plan:** New `packages/django_state/`, faithful port.

**`engines/emp_defense/`** — 3 .py + `modules/` + `schemas/` + `tests/` + `artifacts/` + `docs/`:
- `__init__.py`, `engine.py`, `demo.py`
- `modules/`, `schemas/`, `tests/`, `artifacts/`, `docs/`
- **Plan:** New `packages/emp_defense/`, faithful port.

**`engines/global_scenario/`** — 3 .py:
- `__init__.py`, `global_scenario_engine.py`, `scenario_config.py`
- **Plan:** New `packages/global_scenario/`, faithful port.

### 2b. `engines/sovereign_war_room/` — see §5

### 2c. `engines/atlas/` — see §6

---

## 3. `examples/`, `tests/`, `data/`, `wiki/`, `Project-Ai/`

| Legacy | Canonical | Disposition |
|---|---|---|
| `examples/temporal/` | `packages/temporal/examples/` | **ALREADY-INTEGRATED** |
| `tests/agents/`, `tests/attack_vectors/`, `tests/chaos/`, `tests/gradle_evolution/`, `tests/gui_e2e/`, `tests/inspection/`, `tests/integration/`, `tests/kernel/`, `tests/load/`, `tests/manual/`, `tests/e2e/` | `tests/test_*_integration.py` + `packages/*/tests/` | **ALREADY-INTEGRATED** (reorganized) |
| `data/` (runtime state — 25M of fates, audit, logs, etc.) | n/a (generated) | **DROP** — never tracked; canonical regenerates at runtime |
| `wiki/` (Obsidian 6.7M) | `docs/index/wiki-pointer-map.md` | **SUPERSEDED** — per-user "no vault"; pointer map captures the useful content |
| `Project-Ai/` (Obsidian vault root) | n/a | **DROP** — per user instruction |

---

## 4. `monitoring/`, `helm/`, `docker/`, `cargo`

| Legacy | Canonical | Disposition |
|---|---|---|
| `monitoring/grafana/` | `crates/genesis-emitter/` + observability hooks in `packages/*/src/*/` | **PORT** — Grafana dashboards and alerts; canonical needs a `monitoring/` sub-tree (move to canonical `monitoring/`?) |
| `helm/` (legacy K8s manifests) | `helm/project-ai/` | **ALREADY-INTEGRATED** |
| `docker-compose.yml`, `docker-compose.override.yml`, `Dockerfile` (root) | `compose.yaml`, `docker/*.Dockerfile` | **ALREADY-INTEGRATED** |
| `Cargo.toml` (none in main — main is Python + Kotlin) | `Cargo.toml` + `Cargo.lock` + `crates/genesis-emitter/` | **ALREADY-INTEGRATED** — Rust crate for genesis event emitter |
| `rust-toolchain.toml` | same | **ALREADY-INTEGRATED** |

---

## 5. SWR — full surface (largest single gap)

Canonical `packages/swr/` has 2 source files: `scenario.py`, `war_room.py`.
Staging `_staging/swr/` mirrors the full legacy. Mapping:

| Legacy file (in `_staging/swr/`) | Canonical target | Disposition |
|---|---|---|
| `cli.py` (top-level) | `packages/swr/src/swr/cli.py` | **PORT** |
| `demo.py` | `packages/swr/src/swr/demo.py` | **PORT** |
| `verify_quality.tarl` | `packages/swr/src/swr/verify_quality.tarl` (or `tests/fixtures/`) | **PORT** — Thirsty-Lang policy artifact |
| `requirements.txt` | n/a (uv workspace) | **DROP** — replaced by `pyproject.toml` deps |
| `README.md`, `DEPLOYMENT_SUMMARY.md`, `IMPLEMENTATION_COMPLETE.md` | `packages/swr/README.md` (consolidated) | **PORT** — merge into single canonical README |
| `swr/__init__.py` | `packages/swr/src/swr/__init__.py` | **PORT** (already exists, expand) |
| `swr/api.py` | `packages/swr/src/swr/api.py` | **PORT** |
| `swr/bundle.py` | `packages/swr/src/swr/bundle.py` | **PORT** |
| `swr/core.py` | `packages/swr/src/swr/core.py` | **PORT** |
| `swr/crypto.py` | `packages/swr/src/swr/crypto.py` | **PORT** |
| `swr/governance.py` | `packages/swr/src/swr/governance.py` | **PORT** |
| `swr/proof.py` | `packages/swr/src/swr/proof.py` | **PORT** |
| `swr/scenario.py` | `packages/swr/src/swr/scenario.py` | **SUPERSEDED** (already ported; verify parity) |
| `swr/scoreboard.py` | `packages/swr/src/swr/scoreboard.py` | **PORT** |
| `tests/test_core.py` | `packages/swr/tests/test_core.py` | **PORT** |
| `tests/test_governance.py` | `packages/swr/tests/test_governance.py` | **PORT** |
| `tests/test_proof.py` | `packages/swr/tests/test_proof.py` | **PORT** |
| `web/app.py` | `apps/swr-dashboard/` (new) or `apps/web/` (existing) | **PORT** — Python web dashboard |
| `web/templates/dashboard.html` | `apps/swr-dashboard/templates/` | **PORT** |
| `legacy_extras/fleet_agent_5_tracking.md` | `docs/reference/swr/fleet-agent-5-tracking.md` | **PORT** (reference) |
| `legacy_extras/GROUP_2_AGENT_8_REPORT.md` | `docs/reference/swr/group-2-agent-8-report.md` | **PORT** (reference) |

**Staging subdir `__pycache__/`** (3 files): **DROP** — Python cache.

### 5a. `SOVEREIGN-WAR-ROOM/` (top-level duplicate)

| Legacy file | Canonical target | Disposition |
|---|---|---|
| All files in `SOVEREIGN-WAR-ROOM/` (22 .py + .md) | already mirrored in `_staging/swr/` (covered above) | **SUPERSEDED** by staging mirror |

---

## 6. Atlas staging residue (per J1 audit)

`packages/_staging/atlas/` mirrors all of `atlas/` and `engines/atlas/`.
J2.1–J2.9 ports consumed 9 of 17 J1-audit features. Remaining 8:

| Feature | Legacy source | LOC est | Canonical | Disposition |
|---|---|---|---|---|
| Bayesian engine | `core/bayesian_engine.py` | ~800 | `packages/atlas/src/atlas/bayesian.py` (J2.3) | **SUPERSEDED** — J2.3 port is canonical; staging copy is dead |
| Ingester | `core/ingestion/ingester.py` | ~350 | n/a | **PORT** — needed for full ingestion pipeline |
| Tier classifier | `core/ingestion/tier_classifier.py` | ~250 | n/a | **PORT** — auto-classify evidence tier |
| Normalizer | `core/normalization/normalizer.py` | ~400 | n/a | **PORT** — schema normalization |
| Projections simulator | `core/projections/simulator.py` | ~350 | partial via J2.1 sensitivity | **PORT** — extends J2.1 surface |
| Scorer | `core/scoring/scorer.py` | ~400 | n/a | **PORT** — multi-factor scoring |
| Calculator | `core/drivers/calculator.py` | ~300 | partial via J2.4b `driver_engine.py` | **PORT** — extends driver surface |
| Config loader | `config/loader.py` | ~200 | n/a | **PORT** — load YAML configs (6 files below) |
| Council | `council/` | ~50 | n/a | **AUDIT** — likely empty/structural; verify |
| Epistemic safeguards | `safeguards/epistemic_safeguards.py` | ~600 | n/a (distinct from J2.5 constitutional kernel) | **PORT** — critical safety layer |
| Schemas | `schemas/validator.py` + 6 JSON | ~300 | n/a | **PORT** — schema validator + JSON schemas |
| Simulation | `simulation/{agent_simulator,contingency_triggers,monte_carlo_engine,timeline_divergence}.py` | ~2000 | n/a | **PORT** — J3 sub-phase per discovery |
| Config YAMLs (6 files) | `config/*.yaml` | ~200 | n/a (defaults hard-coded in canonical) | **PORT** — runtime-tunable config |

**Staging top-level files:**

| Legacy (in `_staging/atlas/`) | Canonical | Disposition |
|---|---|---|
| `__init__.py` | `packages/atlas/src/atlas/__init__.py` | **SUPERSEDED** — staging init is for legacy, canonical is rebuilt |
| `README.md` | `packages/atlas/README.md` | **REFERENCE** — copy content to canonical README, then deprecate staging |
| `STATUS.md`, `PROGRESS_REPORT.md`, `COMPLETION.md` | n/a | **DROP** — porting status notes, not needed in canonical |
| `SUBORDINATION.md` | `docs/internal/SUBORDINATION_NOTICE.md` (or incorporated into atlas README) | **REFERENCE** — copy key content, deprecate staging |
| `IMPLEMENTATION_SUMMARY.md` (in `legacy_extras/`) | `docs/reference/atlas-implementation-summary.md` | **PORT** (reference) |

---

## 7. `integrations/` — three sub-packages, all NOT in canonical

| Legacy sub-package | Canonical | Disposition |
|---|---|---|
| `integrations/openclaw/` (with `skills/`) | n/a | **DROP** — 17-file "God-Tier" Legion agent; user directive 2026-07-06 ("oh no fuck open claw") |
| `integrations/thirstys_trading_hub/` (core + tests) | n/a | **DEFERRED** — user directive 2026-07-06 ("skip it for now, maybe future work"); 7-file trading system with paper/live mode; not blocking |
| `integrations/thirsty_lang_complete/` (bridge) | PyPI dep `thirsty-lang==0.8.2` | **SUPERSEDED** — v1.0 deployment-script bridge is obsolete; the canonical Thirsty-Lang/UTF family lives at `C:\Users\Quencher\Desktop\Github\Personal Repo's\thirsty_lang_exploration_0754` (user directive 2026-07-06) and is consumed via PyPI. The Beginnings `convergence` package already calls into `thirsty-lang` for the T1–T7 tier specs. Bridge docs ported to `docs/reference/integrations/thirsty-lang-v1-deployment-kit/` if needed (not blocking). |

---

## 8. `monitoring/` — partial port needed

`monitoring/grafana/` has dashboards. Canonical has `crates/genesis-emitter/` for telemetry. Audit: do the Grafana dashboards have content canonical needs? If yes, port; if they're config-only, document and reference.

---

## 9. T:\ drive satellites (not under main, but on the same drive)

| Path | Size | Disposition |
|---|---|---|
| `T:\Project-AI-vault\` | 327 MB | **OUT-OF-SCOPE for this turn** — separate repo; user decision needed (Decision 4 in strategy doc: A integrate, B keep separate, C archive) |
| `T:\Project-AI-Pentest-Mainframe\` | 0 (empty) | **DROP** — empty directory |
| `T:\Project-AI-pre-phase2-hold-20260603_070143\` | 798 MB | **OUT-OF-SCOPE for this turn** — historical hold; needs user decision (archive to external?) |
| `T:\Project-AI-Canonical\` | n/a (not yet inspected) | **OUT-OF-SCOPE for this turn** — separate repo, not part of main |
| `T:\Project-AI-consolidation-logs\` | n/a (not yet inspected) | **OUT-OF-SCOPE for this turn** — log archive |
| `T:\00-Active\Project-AI-main.worktrees\` | 0 (empty) | **DROP** — empty |

---

## 10. What this inventory is NOT

This document is **a map, not a plan**. It tells you which files in main
have which counterpart in canonical. It does NOT commit to a port
schedule, sub-phase breakdown, or wave budget. Those come after this
envelope is committed and you pick the next slice.

The next step is your call. The recommended slices, in priority order:

1. **Scenario engines batch** (engines/ai_takeover, alien_invaders, cognitive_warfare, django_state, emp_defense, global_scenario) — 6 new packages, ~18-30 files each + tests. Each engine is its own sub-phase per the J2 wave-budget rule (≤5 new files per wave).
2. **SWR full port** — 1 sub-phase, well-scoped (the staging mirror is the full surface).
3. **Atlas staging residue** — pick one of: simulation (J3, ~2000 LOC), ingestion+normalization+scoring+calculator (~1300 LOC), epistemic safeguards (~600 LOC), schemas (~300 LOC), config loader + YAMLs (~400 LOC).
4. **`integrations/`** — 3 sub-packages, ~5-10 files each.
5. **`monitoring/` audit** — small but unclear scope.
6. **Satellite repos** (`Project-AI-vault`, `pre-phase2-hold`, `Canonical`, `consolidation-logs`) — separate decisions, separate turn.

---

## 11. Honest disclosure

This is **discovery + inventory only**. NO source code has been written
or moved. The `_staging/` mirror remains as-is. `Project-AI-main` is
untouched. Canonical `Project-AI-Beginnings` is at HEAD `c752fd31`,
1,347 tests passing, all four gates green at last verify.

**No disposition is final until you say "go [slice name]."**

The strategy doc (`PROJECT_AI_INTEGRATION_STRATEGY.md`, 2026-06-29) is
stale on test counts (it cites 1,467; current is 1,347 — the 1,467 was
before some test consolidation). It is also pre-J2.5 through J2.9. This
inventory supersedes it for the immediate next-slice planning.

---

## 12. Verification

To reproduce this inventory:

```bash
# main structure
cd T:/00-Active/Project-AI-main && ls -1 | wc -l                # 166
cd T:/00-Active/Project-AI-main && find . -name "*.py" -not -path "*/__pycache__/*" -not -path "*/node_modules/*" | wc -l   # 2549
cd T:/00-Active/Project-AI-main && find . -name "*.md" -not -path "*/__pycache__/*" -not -path "*/node_modules/*" | wc -l   # 2459

# canonical structure
cd T:/00-Active/Project-AI-Beginnings && find packages -name "*.py" -not -path "*pycache*" | wc -l
cd T:/00-Active/Project-AI-Beginnings && git log --oneline -1    # c752fd31 docs(pre-deployment): record CI evidence

# staging residue
ls T:/00-Active/Project-AI-Beginnings/packages/_staging/atlas/    # mirrors legacy atlas
ls T:/00-Active/Project-AI-Beginnings/packages/_staging/swr/      # mirrors legacy SWR
```
