# Heart Restore Map

Date: 2026-04-02

Scope: restore the control plane first. Structural cleanup stays frozen until this map is complete and verified.

## What the screenshots prove

- The repo was being used as an active control plane, not just an archive of experiments.
- The working set centered on `src/app/core/`, `src/app/agents/`, `.github/workflows/`, `config/`, `canonical/`, and the workspace wiring in `Project-AI.code-workspace`.
- `archive/` and `history/` are reference pools. They are not automatic source-of-truth roots.

## Current-state mismatches

- `archive/governance/` is not present in the current tree.
- `archive/services/` is not present in the current tree.
- `IDE_Work_Spaces/` is absent in the current tree.
- `FIX_WORKSTATION.ps1` is absent in the current tree.
- `Project-AI.code-workspace` exists and should be treated as workspace wiring, not proof that the repo is correct.

## Bucket 1: Must Restore Now

These paths define the control plane. Restore them before touching any structural cleanup.

### Governance, identity, and proof

- `governance/sovereign_runtime.py`
- `governance/iron_path.py`
- `governance/existential_proof.py`
- `governance/singularity_override.py`
- `governance/sovereign_verifier.py`
- `governance/core.py`
- `src/app/governance/audit_log.py`
- `src/app/governance/sovereign_audit_log.py`
- `src/app/governance/tsa_provider.py`
- `canonical/replay.py`
- `canonical/server.py`

### Control-plane runtime

- `src/app/core/ai_systems.py`
- `src/app/core/command_override.py`
- `src/app/core/config_loader.py`
- `src/app/core/distress_kernel.py`
- `src/app/core/error_aggregator.py`
- `src/app/core/cognition_kernel.py`
- `src/app/core/guardian_approval_system.py`
- `src/app/core/legion_protocol.py`
- `src/app/core/memory_engine.py`
- `src/app/core/operational_substructure.py`
- `src/app/core/perspective_engine.py`
- `src/app/core/realtime_monitoring.py`
- `src/app/core/red_hat_expert_defense.py`
- `src/app/core/red_team_stress_test.py`
- `src/app/core/relationship_model.py`
- `src/app/core/robotic_controller_manager.py`
- `src/app/core/robotic_hardware_layer.py`
- `src/app/core/robotic_mainframe_integration.py`
- `src/app/core/sensor_fusion.py`
- `src/app/core/shadow_containment.py`
- `src/app/core/shadow_execution_plane.py`
- `src/app/core/super_kernel.py`
- `src/app/core/tarl_operational_extensions.py`
- `src/app/core/tier_governance_policies.py`
- `src/app/core/tier_health_dashboard.py`
- `src/app/core/location_tracker.py`
- `src/app/core/master_harness.py` if present in the manifest baseline
- `src/app/core/nld_harness.py` if present in the manifest baseline
- `src/app/pipeline/signal_flows.py`

### Arbitration and agent control

- `cognition/triumvirate.py`
- `cognition/kernel_liara.py`
- `cognition/liara_guard.py`
- `src/app/agents/oversight.py`
- `src/app/agents/planner.py`
- `src/app/agents/validator.py`
- `src/app/agents/explainability.py`
- `src/app/agents/tarl_protector.py`
- `src/app/agents/thirsty_lang_validator.py`

### Workflow and config surfaces

- `.github/workflows/codex-deus-ultimate.yml`
- `.github/workflows/project-ai-monolith.yml`
- `.github/workflows/format-and-fix.yml`
- `.github/workflows/tk8s-civilization-pipeline.yml`
- `.github/workflows/codeql.yml`
- `.github/workflows/bandit.yml`
- `.github/workflows/security-secret-scan.yml`
- `.github/workflows/generate-sbom.yml`
- `config/distress_simplified.yaml`
- `config/defense_engine.toml`
- `config/god_tier_config.yaml`
- `config/security_hardening.yaml`
- `config/memory_optimization.yaml`
- `config/settings.py`

## Bucket 2: Restore Only If Missing From Live Roots

These surfaces are legitimate, but only when the live root is incomplete or absent.

- `src/app/miniature_office/`
- `src/app/agents/cerberus_codex_bridge.py`
- `src/app/agents/constitutional_guardrail_agent.py`
- `src/app/agents/red_team_agent.py`
- `src/app/agents/red_team_persona_agent.py`
- `desktop/`
- `web/`
- `android/`
- `services/`
- `integrations/`
- `emergent-microservices/`
- `project_ai/`
- `Project-AI.code-workspace`
- `FIX_WORKSTATION.ps1`
- `IDE_Work_Spaces/`
- `archive/aspirational_architecture/` `.thirsty` files only as gap-filler candidates

Rule for this bucket:

- Copy only what is missing from the live root.
- Diff each candidate against the current authoritative file before restoring.
- If a live file already exists and is still coherent, do not overwrite it from archive material.

## Bucket 3: Ignore Until Control Plane Is Stable

These are not part of the control-plane restoration pass.

- `archive/` as a whole, except for targeted gap-filling from Bucket 2
- `history/`
- `branches/`
- `trunk/`
- `unity/`
- `.next/`
- `target/`
- `.venv/`
- `.vs/`
- `.pytest_cache/`
- `__pycache__/`
- `logs/`
- `output/`
- `ci-reports/`
- `test-artifacts/`
- `boot_log_v2.txt`
- `out.txt`
- `tmp_sovereign_pipeline.yaml`
- `Project-AI Master Control.lnk`
- generated inventories such as `inventory.csv`, `full_file_list.txt`, and `REPO_TREE_DIAGRAM.md`

## Verification Order

1. Validate the live roots against the manifest and the screenshots.
2. Restore only missing or obviously partial control-plane files.
3. Reopen `Project-AI.code-workspace` and confirm the expected folders resolve.
4. Run targeted tests for `governance/`, `cognition/`, `src/app/core/`, and `.github/workflows/`-related paths.
5. Update `SYSTEM_MANIFEST.md` only after the control plane is coherent again.
6. Do not start structural cleanup until the above is stable.

## Operating Rule

The repo should be repaired in this order:

1. Control plane
2. Workspace wiring
3. Verification
4. Only then structural cleanup

If a file is ambiguous, keep it out of the cleanup pass and classify it first.
