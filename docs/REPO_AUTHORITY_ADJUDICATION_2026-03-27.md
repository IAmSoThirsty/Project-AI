# Repo Authority Adjudication

Date: 2026-03-27

Repo: `C:\Users\Quencher\.gemini\antigravity\scratch\Sovereign-Governance-Substrate`

Current commit baseline: `ff10f1c71eb37ef0f8c44bda28fc9bf313b15a27`

Safety anchors created before classification:
- Full local backup copy: `C:\Users\Quencher\.gemini\antigravity\backups\Sovereign-Governance-Substrate_20260327_162256`
- Local safety tag: `codex/pre-classification-20260327`

## Governing Model

This repo is adjudicated under the closed triad:

- `C` = Code. Behavior-defining source and execution-defining configuration.
- `T` = Constitutional Data. Proof-bearing, continuity-bearing, replay-bearing, or identity-bearing state.
- `O` = Operational Data. Ephemeral, cache-like, performance-oriented, or environment-local execution substrate.
- `INVALID` = Non-authoritative residue, duplicated authority, historical mirrors, junk, or artifacts that should not live in the active source tree.

Authority hierarchy:

- `T > C > O`

Operational rule:

- Keep `C`
- Keep `T`
- Remove or externalize `O`
- Delete or archive out of the active tree anything classified `INVALID`

Critical constraint:

- `data/` cannot be bulk-cleaned.
- `archive/` cannot be bulk-removed until extraction decisions are frozen.
- Duplicate authorities must be canonicalized before final tree stabilization. The phase-2 history rewrite was restricted to already-adjudicated `O` paths only.

## Top-Level Adjudication

| Path | Class | Action | Basis |
| --- | --- | --- | --- |
| `.agent/` | `C` | Keep | Authored agent workflow/config surface. |
| `.agents/` | `C` | Keep | Small authored automation/agent surface. |
| `.antigravity/` | `C` | Keep, but inspect for hidden `O` later | Tracked content is small and likely authored config, not the large ignored artifact/cache areas. |
| `.codacy/` | `C` | Keep | Tooling configuration, not runtime residue. |
| `.devcontainer/` | `C` | Keep | Deterministic dev/runtime environment definition. |
| `.githooks/` | `C` | Keep | Repo-execution policy surface. |
| `.github/` | `C` | Keep | CI/CD, guardianship, verification, and security enforcement. |
| `.gradle/` | `O` | Remove from tracking | Local build cache surface. |
| `.venv_prod/` | `O` | Remove from tracking | Environment-local interpreter/package state. |
| `adversarial_tests/` | `C` | Keep | Verification source. |
| `android/` | `C` | Keep | Active platform source. |
| `api/` | `C` | Keep | External execution surface. |
| `archive/` | `INVALID` | Freeze; extract only curated survivors | Historical mirrors and package payloads are not active authority. |
| `benchmarks/` | `C` | Keep | Verification/performance source. |
| `branches/` | `INVALID` | Remove from active tree after review | Repo-in-repo branch mirror. |
| `canonical/` | `T` | Keep and protect | This is the proof spine and replay truth surface. |
| `ci-reports/` | `O` | Remove from tracking unless a report is formally promoted | Generated CI/run output. |
| `cognition/` | `C` | Keep | Arbitration and cognition core. |
| `config/` | `C` | Keep | Execution and constraint definitions. |
| `data/` | `T` | Protect at root, split internally before cleanup | Contains both constitutional state and operational residue; root must be treated as protected until subdivision is complete. |
| `demos/` | `C` | Keep | Authored demonstration source. |
| `deploy/` | `C` | Keep | Operational infrastructure source. |
| `desktop/` | `C` | Keep | Active surface for browser/office/product shell. |
| `docs/` | `C` | Keep | Human-authored contract/spec layer; some files are structural inputs to proof checks. |
| `e2e/` | `C` | Keep | Verification source. |
| `EditionV1/` | `C` | Keep for now | Small release-metadata root, not the giant archived payloads. |
| `emergent-microservices/` | `C` | Keep | Active service source tree. |
| `engines/` | `C` | Keep, but strip embedded build output | Simulation and contingency engines are core; `target/` under them is not. |
| `examples/` | `C` | Keep | Curated examples until proven redundant. |
| `governance/` | `C` | Keep | Constitutional enforcement and cryptographic runtime. |
| `gradle/` | `C` | Keep | Build tool wrapper/config. |
| `gradle-evolution/` | `C` | Keep | Authored build/integration source. |
| `h323_sec_profile/` | `C` | Keep | Small authored profile/spec surface. |
| `hardware_schematics/` | `C` | Keep pending deprecation review | Could become archival later, but not safe to delete blindly. |
| `helm/` | `C` | Keep | Deployment source. |
| `history/` | `INVALID` | Remove from active tree after review | Historical mirror, not live authority. |
| `integrations/` | `C` | Keep | Full service implementations; appears to be active native component surface. |
| `k8s/` | `C` | Keep | Active infra source. |
| `kernel/` | `C` | Keep | Enforcement/runtime substrate. |
| `linguist-submission/` | `C` | Keep | Small authored package with repo-specific purpose. |
| `logs/` | `O` | Remove from tracking unless promoted into signed `T` | Raw run residue. |
| `monitoring/` | `C` | Keep | Authored observability logic. |
| `native_components/` | `C` | Keep | Thin repo-specific workflow/governance overlays for native components. |
| `octoreflex/` | `C` | Keep | Kernel containment layer. |
| `orchestrator/` | `C` | Keep | Execution coordination surface. |
| `output/` | `O` | Remove from tracking | Run output. |
| `plugins/` | `C` | Keep | Active execution extension surface. |
| `policies/` | `C` | Keep | Constitutional policy source. |
| `project_ai/` | `C` | Keep as canonical importable package root | Clean Python package naming and repeated advisor preference. |
| `Project-AI/` | `INVALID` | Freeze and diff into `project_ai/` before removal | Duplicate authority root with overlapping code and a small set of source divergences. |
| `projects/` | `C` | Keep | Includes miniature office and browser-adjacent projects. |
| `proto/` | `C` | Keep | Contract/source surface. |
| `reports/` | `C` | Keep provisionally | Small curated report root until content review proves otherwise. |
| `roots/` | `INVALID` | Remove from active tree after review | Namespace-proxy root with no clear active authority. |
| `scripts/` | `C` | Keep | Build/ops/util scripts. |
| `security/` | `C` | Keep | Core security source. |
| `services/` | `C` | Keep | Active service source. |
| `src/` | `C` | Keep | Main source tree. |
| `taar/` | `C` | Keep | Active orchestration/build substrate. |
| `tarl/` | `C` | Keep | Language stack core. |
| `tarl_os/` | `C` | Keep | Language stack core. |
| `Tasks completed/` | `INVALID` | Extract surviving docs/scripts, remove the dump root | Mixed historical residue, not a canonical namespace. |
| `temporal/` | `C` | Keep | Small authored subsystem. |
| `terraform/` | `C` | Keep | Infra source. |
| `test-artifacts/` | `O` | Remove from tracking | Generated test output. |
| `test-data/` | `C` | Keep | Curated fixtures. |
| `tests/` | `C` | Keep | Verification source. |
| `tmp/` | `O` | Remove from tracking | Temp output/state. |
| `tools/` | `C` | Keep | Authored tool source. |
| `trunk/` | `INVALID` | Freeze and extract surviving authorities; do not treat as live canonical source | Grouped forest of duplicated project authorities and presentation surfaces. |
| `ui/` | `C` | Keep | Small authored interface surface. |
| `unity/` | `C` | Keep authored project files only | Current tracked footprint is small and looks like project source, not Unity cache. |
| `usb_installer/` | `C` | Keep | Authored deployment/install surface. |
| `utils/` | `C` | Keep | Shared source. |
| `validation_evidence/` | `C` | Keep | Curated evidence/doc surface, currently very small. |
| `web/` | `C` | Keep | Active application surface. |
| `whitepaper/` | `C` | Keep | Formal authored documentation. |
| `zenodo_package/` | `C` | Keep | Release/provenance metadata surface. |

## Root File Adjudication

| Path or Group | Class | Action | Basis |
| --- | --- | --- | --- |
| `pyproject.toml`, `requirements*.txt`, `package*.json`, `build.gradle.kts`, `settings.gradle.kts`, `gradle.properties`, `Makefile`, `Dockerfile*`, `taar.toml`, `MANIFEST.in`, `setup.cfg` | `C` | Keep | Deterministic build/runtime definition. |
| `README.md`, `SECURITY.md`, `INSTALL.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `The_Guide_Book.md`, `TECHNICAL_SPECIFICATION.md`, `TAMS_SUPREME_SPECIFICATION.md`, `THIRSTY_LANG_UTF_SPEC.md`, `PRODUCTION_DEPLOYMENT.md`, `CHANGELOG.md` | `C` | Keep | Human-authored contract/spec layer. |
| `ARCHITECT_MANIFEST.md`, `COMPLETION_MANIFEST.md`, `SOVEREIGN_MANIFEST.md`, `SYSTEM_MANIFEST.md`, `RELEASE_MANIFEST.json`, `compliance_manifest.json` | `C` | Keep and later test for promotion into `T` | Provenance-facing metadata; not yet treated as append-only constitutional ledgers. |
| `.env.example`, `.gitignore`, `.gitattributes`, `.pre-commit-config.yaml`, `.bandit`, `.eslintrc.json`, `.dockerignore`, `.markdownlint.yaml`, `.prettierrc`, `.python-version` | `C` | Keep | Execution/tooling definition. |
| `.gitmodules.local_backup` | `C` | Keep until submodule intent is restored elsewhere | Only current tracked record of prior submodule layout. |
| `boot_sovereign.py`, `build_orchestrator.py`, `build-installer.ps1`, `Project-AI.ps1`, `Master-Sovereign-Launch-Sequence.ps1`, `start.ps1`, `launcher.py`, `sovereign_mcp_server.py`, `sovereign_runtime_proof.py`, `verify_rebirth.py`, `activate_transcendence.py`, `yggdrasil_final_activation.py` | `C` | Keep | Entry/orchestration surface. |
| `inventory.csv`, `full_file_list.txt`, `REPO_TREE_DIAGRAM.md` | `INVALID` | Remove from active tree after a stable curated index exists | Generated or derivable inventory snapshots, not primary authority. |
| `audit.log`, `test_report.txt` | `O` | Remove from tracking unless promoted into signed `T` | Raw run output. |
| `Project-AI Master Control.lnk`, `Project-AI.code-workspace`, `tmp_sovereign_pipeline.yaml` | `INVALID` | Remove from active tree | Machine-local or temporary convenience artifacts. |

## High-Risk Drilldown: `data/`

This is the most dangerous root in the repo. It contains all three categories:

- constitutional continuity state
- authored datasets and fixtures
- operational residue

The root classification therefore defaults to `T` for safety, but cleanup must act on the subpaths below.

| Path | Class | Action | Basis |
| --- | --- | --- | --- |
| `data/ai_persona/state.json` | `T` | Keep and protect | Identity-bearing state anchor. |
| `data/memory/knowledge.json` | `T` | Keep and protect | Persistent memory continuity surface. |
| `data/constitutional_store/manifest.json` | `T` | Keep and protect | Constitutional manifest. |
| `data/constitutional_store/manifest.sig` | `T` | Keep and protect | Signature-bearing proof artifact. |
| `data/audit/audit_20260317.jsonl` | `T` | Keep and protect | Audit timeline candidate and replay-bearing record. |
| `data/genesis_keys/` | `T` | Keep and protect | Genesis/public identity anchors. |
| `data/genesis_pins/` | `T` | Keep and protect | External identity/proof anchors. |
| `data/learning_requests/` | `T` | Keep, but harden | Treated as constitutional continuity by project doctrine, but the SQLite file inside should eventually be backed by explicit hash/signature policy. |
| `data/legal/acceptance_ledger.db` | `T` | Keep, but harden | Ledger-like store with legal/proof semantics; current DB form is a risk unless bounded by explicit integrity guarantees. |
| `data/cerberus/agent_templates/` | `C` | Keep | Authored templates. |
| `data/cerberus/languages.json`, `data/cerberus/runtimes.json` | `C` | Keep | Static authored execution data. |
| `data/cerberus/agents/` | `O` | Remove from tracking unless promoted with explicit provenance | Instance-like generated agent material, not canonical templates. |
| `data/training_datasets/` | `C` | Keep | Curated training/input corpus. |
| `data/comprehensive_security_tests/` | `C` | Keep | Verification corpus. |
| `data/red_team_stress_tests/` | `C` | Keep | Verification corpus. |
| `data/novel_security_scenarios/` | `C` | Keep | Verification/input corpus. |
| `data/red_hat_expert_simulations/` | `C` | Keep | Curated scenario/input corpus. |
| `data/datasets/` | `C` | Keep | Curated input root. |
| `data/osint/` | `C` | Keep | Authored knowledge/input corpus. |
| `data/migrations/` | `C` | Keep | Schema/source input. |
| `data/access_control.json`, `data/boot_manifest.json`, `data/command_override_config.json`, `data/settings.example.json` | `C` | Keep | Static execution/config inputs. |
| `data/robustness_metrics/` | `O` | Remove from tracking unless explicitly elevated into signed benchmark truth | Metrics outputs are observational by default, not proof-bearing by default. |
| `data/demo_god_tier/` | `O` | Remove from tracking unless a specific file is promoted | Demo state and continuity snapshots are not automatically constitutional truth. |
| `data/enhanced_scenarios_demo/` | `O` | Remove from tracking | Demo/runtime state with cache and engine snapshots. |
| `data/global_scenarios_demo/` | `O` | Remove from tracking | Demo runtime snapshot. |
| `data/savepoints/` | `O` | Remove from tracking | Savepoint convenience state; replaceable execution substrate. |
| `data/secure.db` | `O` | Remove from tracking unless explicitly reclassified with integrity guarantees | Mutable runtime DB, not self-proving. |
| `data/settings.json`, `data/users.json`, `data/telemetry.json` | `O` | Remove from tracking | Local mutable runtime state. |
| `data/trading_hub/` | `O` | Remove from tracking | Cache/portfolio/order runtime state. |
| `data/defense_engine.log` | `O` | Remove from tracking | Raw log. |
| `data/security/` | `O` | Remove from tracking unless specific reports are promoted | Raw assessment/report output. |
| `data/asl_assessments/` | `O` | Remove from tracking unless promoted | Assessment output. |
| `data/continuous_learning/reports.json` | `O` | Remove from tracking | Observational report output. |
| `data/continuous_learning/curated.json`, `data/continuous_learning/curated.example.json` | `C` | Keep | Curated input definitions. |
| `data/cybersecurity_knowledge.json` | `C` | Keep | Static authored knowledge/input. |
| `data/tarl_protection/shield_registry.json` | `T` | Keep provisionally | Registry reads like protected security identity state and should be treated conservatively. |
| `data/black_vault_secure/` | `T` | Keep and protect | Explicitly protected secure state root. |

## High-Risk Drilldown: `archive/`

`archive/` is not active authority. It is a mixture of:

- historical mirrors
- prior builds
- retained documents
- package payloads

The active tree should not treat `archive/` as canonical source. Specific survivors may be extracted, but the root itself is `INVALID`.

| Path | Class | Action | Basis |
| --- | --- | --- | --- |
| `archive/history/timeline/EditionV1/RELEASE_BUNDLE/*.zip` | `O` | Externalize out of Git history | Packaged release payloads, not active source or constitutional truth. |
| `archive/history/timeline/EditionV1/ARCHITECTURE.md`, `PLAN.md`, `RELEASE_PACKAGE.md`, `TODO.json`, `RELEASE_MANIFEST.json`, `BUILD_EDITION_V1_CI.py`, `pack_release.py`, `cts5/**` | `C` | Extract into a curated live release-metadata/docs surface | Small authored release metadata worth preserving. |
| `archive/web/.next/**` | `O` | Remove from tracking and history | Built Next.js output. |
| `archive/cleanup_2026-03-04/**` | `INVALID` | Remove from active tree after backup | Cleanup residue and duplicate snapshots. |
| `archive/docs/**` | `C` | Review and selectively extract | Some documents may still explain live behavior. |
| `archive/aspirational_architecture/**` | `INVALID` | Extract only if still referenced | Aspirational material is not live authority by default. |
| `archive/external/**` | `INVALID` | Remove from active tree after backup | Archived copies of external trees are not active dependencies. |
| `archive/src/**`, `archive/tests/**`, `archive/api/**`, `archive/engines/**`, `archive/unity/**`, `archive/emergent-microservices/**`, `archive/k8s/**` | `INVALID` | Remove after extracting any truly live files | Historical mirrors of active namespaces. |

## High-Risk Drilldown: `integrations/`, `native_components/`, and Structural Dependencies

Observed structure:

- `integrations/*` contains full component implementations with source, tests, docs, Docker, Kubernetes, and packaging files.
- `integrations/actions-runner/` is an exception: it contains a vendored self-hosted GitHub Actions runner archive plus local runner registration/state files, not authored subsystem source.
- `native_components/*` appears to be a thin overlay layer, often only CI/CD workflow files per component.
- `security/penetration-testing-tools` was stored as a gitlink (`160000 cce4364defa48623451681e7384bee00b76c78f1`) but the live repo had no `.gitmodules` file, only `.gitmodules.local_backup`.

Decisions:

| Path | Class | Action | Basis |
| --- | --- | --- | --- |
| `integrations/` | `C` | Keep | This is active code, not boilerplate junk. |
| `integrations/actions-runner/` | `O` | Remove from tracking and history | Vendored CI runner payload and local runner state are operational substrate, not authored source. |
| `native_components/` | `C` | Keep | Repo-specific native governance/workflow overlays. |
| `security/penetration-testing-tools` | `C` | Preserve as a normal tracked vendor tree | Structural security dependency with broken metadata state; converted out of orphaned gitlink form during Phase 4. |
| `.gitmodules.local_backup` | `C` | Preserve until submodule intent is re-declared cleanly | Only tracked map of prior submodule layout. |

Observed anomaly:

- `git submodule status` failed with `fatal: no submodule mapping found in .gitmodules for path 'security/penetration-testing-tools'`
- The live worktree still contained a small file tree under that path, but it was not a nested repo and had no active `.gitmodules` declaration.
- Phase 4 resolution was to replace the orphaned gitlink with a normal tracked directory so the path can be pushed and cloned deterministically.

## High-Risk Drilldown: `project_ai/` vs `Project-AI/`

Observed structure before canonicalization:

- Both roots existed.
- They overlapped heavily.
- `project_ai/` was the cleaner canonical Python package form.
- A direct tree comparison showed a small set of source divergences between corresponding files, plus local ignored `__pycache__` noise in the package-style tree.

Decision:

| Path | Class | Action | Basis |
| --- | --- | --- | --- |
| `project_ai/` | `C` | Keep as canonical | Import-safe package root and the better authority candidate. |
| `Project-AI/` | `INVALID` | Freeze, diff fully, merge surviving deltas into `project_ai/`, then remove | Duplicate authority is too dangerous to leave unresolved. |

Phase 3 reconciliation result:

- `project_ai/save_points/auto_save.py` kept the package version behavior for `asyncio.CancelledError`; cancellation is expected and should remain silent.
- `project_ai/tarl/integrations/config_presets.py` absorbed the surviving non-fatal warning path from the duplicate tree.
- `project_ai/utils/tscg_b.py` absorbed the surviving non-fatal warning path from the duplicate tree.
- `Project-AI/` was then removed from tracking as a resolved duplicate authority root.

## Second-Pass Adjudication: `trunk/`, `projects/`, `unity/`, `reports/`, `temporal/`, and `data/cerberus/`

### `trunk/`

Observed structure:

- `trunk/leaf/leaf_group_01/Thirstys-waterfall/**` strongly overlaps the active browser/open-web-engine product currently present under `projects/waterfall-open-web-engine/**`
- `trunk/leaf/leaf_group_01/AI_Mutation_Governance_Firewall/**` is a full standalone service tree
- `trunk/leaf/leaf_group_05/Cerberus/**` is another large standalone component tree
- `trunk/leaf/leaf_group_08/The_Triumvirate/**` includes site pages, assets, and at least one temp-named image artifact
- `trunk/super/penetration-testing-tools` corresponds to a prior submodule path named in `.gitmodules.local_backup`

Decision:

| Path | Class | Action | Basis |
| --- | --- | --- | --- |
| `trunk/` | `INVALID` | Freeze and extract only surviving canonical authorities | This root is acting as a grouped super-project mirror, not a single authoritative namespace. |
| `trunk/leaf/leaf_group_01/Thirstys-waterfall/**` | `INVALID` | Diff against `projects/waterfall-open-web-engine/**` and merge surviving deltas there | Duplicate browser/open-web-engine authority. |
| `trunk/leaf/leaf_group_01/AI_Mutation_Governance_Firewall/**` | `C` | Candidate for extraction into a canonical active root | Full service source tree, not junk. |
| `trunk/leaf/leaf_group_05/Cerberus/**` | `C` | Candidate for extraction into canonical security/component surface | Full authored component tree. |
| `trunk/leaf/leaf_group_08/The_Triumvirate/**` | `C` | Candidate for extraction into a canonical site/product surface after temp asset scrub | Authored site/content surface with some residue mixed in. |
| `trunk/leaf/leaf_group_08/The_Triumvirate/assets/images/tmponrptw4m-1766462626908.jpg` | `O` | Remove during extraction | Temp-named asset residue. |
| `trunk/super/penetration-testing-tools` | `C` | Reconcile with `security/penetration-testing-tools` before any deletion | Structural security dependency appears in two broken/archival locations. |

### `projects/`

Observed structure:

- `projects/miniature-office/**` is a self-contained active product tree
- `projects/waterfall-open-web-engine/**` is a full active browser/open-web-engine product tree
- `projects/waterfall-open-web-engine/**` overlaps heavily with `trunk/leaf/leaf_group_01/Thirstys-waterfall/**`

Decision:

| Path | Class | Action | Basis |
| --- | --- | --- | --- |
| `projects/` | `C` | Keep | This is a legitimate active product namespace, not a dump root. |
| `projects/miniature-office/**` | `C` | Keep | Directly aligned with stated repo goal. |
| `projects/waterfall-open-web-engine/**` | `C` | Keep as canonical browser/open-web-engine root | Cleaner active product root than the mirrored `trunk` copy. |

### `unity/`

Observed structure:

- Tracked Unity content consists of authored `Assets/`, `Packages/`, tests, and docs
- No tracked `Library/` cache is present under the current `unity/` root

Decision:

| Path | Class | Action | Basis |
| --- | --- | --- | --- |
| `unity/` | `C` | Keep | Current tracked content is authored Unity project source, not cache. |

### `reports/`

Observed structure:

- `reports/ascendancy_report.md`
- `reports/legal_framework/Yggdrasil_Legal_Framework.md`
- `reports/transcendent_lock.json`

Decision:

| Path | Class | Action | Basis |
| --- | --- | --- | --- |
| `reports/` | `C` | Keep | Small curated authored report/legal root, not raw run residue. |

### `temporal/`

Observed structure:

- Small workflow package with security/triumvirate workflow code and README

Decision:

| Path | Class | Action | Basis |
| --- | --- | --- | --- |
| `temporal/` | `C` | Keep | Authored workflow source. |

### `data/cerberus/`

Observed structure:

- `agent_templates/*` are clear authored templates
- `agents/*` are instance-like concrete generated agents in multiple languages
- `languages.json` and `runtimes.json` are static inventory/config data
- `registry/state.json`, `lockdown/lockdown_state.json`, `logs/bypasses_202603.jsonl`, and `audit_report_20260123_152308.md` are mutable state/report surfaces

Decision:

| Path | Class | Action | Basis |
| --- | --- | --- | --- |
| `data/cerberus/agent_templates/**` | `C` | Keep | Authoritative templates. |
| `data/cerberus/languages.json`, `data/cerberus/runtimes.json` | `C` | Keep | Static authored inventory/config inputs. |
| `data/cerberus/agents/**` | `O` | Remove from tracking unless formally elevated with provenance | Generated instance material, not template authority. |
| `data/cerberus/registry/state.json` | `O` | Remove from tracking unless upgraded into explicit proof-bearing ledger form | Mutable registry state, not self-proving. |
| `data/cerberus/lockdown/lockdown_state.json` | `O` | Remove from tracking unless upgraded into explicit proof-bearing ledger form | Mutable incident state snapshot. |
| `data/cerberus/logs/bypasses_202603.jsonl` | `O` | Remove from tracking unless signed/replayable policy says otherwise | Raw log by default. |
| `data/cerberus/audit_report_20260123_152308.md` | `O` | Remove from tracking or promote into curated docs | Static report output, not core authority. |

## Immediate No-Touch List

Do not bulk-delete or rewrite history against these paths until their extraction/canonicalization step is complete:

- `canonical/`
- `data/`
- `governance/`
- `cognition/`
- `src/`
- `integrations/`
- `native_components/`
- `security/penetration-testing-tools`
- `project_ai/`
- `Project-AI/`

## Immediate Remove-First Targets

These are the safest high-value `O`/`INVALID` candidates once the cleanup phase begins:

- `archive/history/timeline/EditionV1/RELEASE_BUNDLE/*.zip`
- `archive/web/.next/**`
- `engines/**/target/**`
- `.gradle/`
- `.venv_prod/`
- `ci-reports/`
- `logs/`
- `output/`
- `test-artifacts/`
- `tmp/`
- `audit.log`
- `test_report.txt`
- `Project-AI Master Control.lnk`
- `Project-AI.code-workspace`

## Next Required Pass

Before any history rewrite, the next decision pass should explicitly adjudicate:

- `trunk/`
- `projects/`
- `unity/`
- `reports/`
- `temporal/`
- any remaining `data/cerberus/*` state surfaces that may need to move from provisional `T` into either hardened `T` or disposable `O`
