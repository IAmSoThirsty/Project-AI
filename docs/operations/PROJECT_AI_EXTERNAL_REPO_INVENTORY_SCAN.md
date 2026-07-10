# Project-AI External Repo Inventory Scan

**Status:** exact-term cross-repo discovery report
**Date:** 2026-07-07
**Inventory source:** `docs/operations/PROJECT_AI_MASTER_CONTINUITY_TRACEABILITY_MATRIX.md`
**Target repos:** `T:\00-Active\Project-AI-main`, `T:\00-Active\Project-AI-vault`, `T:\00-Active\Sovereign-IDE`, `T:\00-Active\mobile-recovery-ops`
**Scan scope:** all files reachable by `rg --hidden --no-ignore --text`, including tracked, untracked, ignored, hidden, archive-named paths, and `.git` metadata/object surfaces. No path exclusions were used.

## Summary

| Metric | Count |
|---|---:|
| Inventory items scanned | 112 |
| Found in at least one external repo | 77 |
| Not found in any external repo by exact item name | 35 |
| Found in Project-AI-main | 76 |
| Found in Project-AI-vault | 72 |
| Found in Sovereign-IDE | 9 |
| Found in mobile-recovery-ops | 5 |

## Repo Surface Counts

| Repo | Files from `rg --files --hidden --no-ignore` | Archive/backup/vault-named paths | `.git` metadata files counted separately |
|---|---:|---:|---:|
| Project-AI-main | 72402 | 472 | 1232 |
| Project-AI-vault | 5465 | 512 | 193 |
| Sovereign-IDE | 3634 | 0 | 784 |
| mobile-recovery-ops | 6019 | 5 | 186 |

## Found Markers

| Inventory item | Main | Vault | Sovereign IDE | Mobile recovery | Repos found | First evidence sample |
|---|:---:|:---:|:---:|:---:|---:|---|
| 5W Relationship Framework |  | Y |  |  | 1 | `Project-AI-vault/RELATIONSHIP_INDEX.md` |
| AADA | Y | Y | Y | Y | 4 | `Project-AI-main/.git/opencode` |
| Acceptance Ledger | Y | Y |  |  | 2 | `Project-AI-main/.github/instructions/refactor-engineer.agent.md` |
| Admissibility Debt |  |  |  |  | 0 | `` |
| Adversarial Red-Teaming Codex | Y | Y |  |  | 2 | `Project-AI-main/adversarial_tests/THE_CODEX.md` |
| Agency Formation |  |  |  |  | 0 | `` |
| AGI Charter | Y | Y |  |  | 2 | `Project-AI-main/.antigravity/security.yaml` |
| AI Takeover Engine | Y | Y |  |  | 2 | `Project-AI-main/.github/workflows/ai_takeover_reviewer_trap.yml` |
| Alpha Red Agent | Y | Y |  |  | 2 | `Project-AI-main/docs/executive/whitepapers/PROJECT_AI_COMPREHENSIVE_WHITEPAPER.md` |
| Appointed Ambassador / Legion |  |  |  |  | 0 | `` |
| Atlas Omega |  |  |  |  | 0 | `` |
| Atropos | Y | Y |  |  | 2 | `Project-AI-main/.hypothesis/constants/13bc2af24a239028` |
| Authority Traceability Threshold |  |  |  |  | 0 | `` |
| Black Vault | Y | Y |  |  | 2 | `Project-AI-main/.github/instructions/IMPLEMENTATION_SUMMARY.md` |
| Camouflage and Deception Plane |  |  |  |  | 0 | `` |
| Canonical Spine / Golden Path |  |  |  |  | 0 | `` |
| CanonicalLog | Y | Y |  |  | 2 | `Project-AI-main/.hypothesis/constants/10fbb1441c347d37` |
| Capability Tokens | Y | Y | Y |  | 3 | `Project-AI-main/.github/instructions/agent-development-protocol.instructions.md` |
| Cerberus | Y | Y |  |  | 2 | `Project-AI-main/.antigravity/workflows/security-fix.yaml` |
| Cerberus Hydra |  |  |  |  | 0 | `` |
| ChainMark |  |  |  |  | 0 | `` |
| Civic-Attest | Y | Y |  |  | 2 | `Project-AI-main/.git/index` |
| Clotho | Y | Y |  |  | 2 | `Project-AI-main/.hypothesis/constants/13bc2af24a239028` |
| Codex Deus Maximus | Y | Y |  |  | 2 | `Project-AI-main/.github/pull_request_template.md` |
| CognitionKernel | Y | Y |  |  | 2 | `Project-AI-main/.agent/workflows/add_gpt_oss_1208.md` |
| Cognitive Warfare | Y | Y |  |  | 2 | `Project-AI-main/api/__pycache__/main.cpython-312.pyc` |
| Companion Intelligence |  |  |  |  | 0 | `` |
| Contingency Engines | Y | Y |  |  | 2 | `Project-AI-main/audit_reports/historical/automation_backups_index/autobackup__README_ORIGINAL_20260420_104842.md` |
| Continuity Reactor | Y | Y |  |  | 2 | `Project-AI-main/docs/governance/PROJECT_AI_SOVEREIGN_VERIFICATION_RUNBOOK.md` |
| COPILOT GOVERNANCE WRAPPER |  |  |  |  | 0 | `` |
| Dark Box | Y | Y |  |  | 2 | `Project-AI-main/docs/governance/PROJECT_AI_SOVEREIGN_VERIFICATION_RUNBOOK.md` |
| DecisionRecord Ledger |  |  |  |  | 0 | `` |
| Detectability Collapse | Y |  |  |  | 1 | `Project-AI-main/web/site/assets/data/papers.json` |
| DICPS | Y | Y |  |  | 2 | `Project-AI-main/web/site/assets/data/projects.json` |
| Directness Doctrine | Y | Y |  |  | 2 | `Project-AI-main/api/main.py` |
| EMP Engine | Y | Y |  |  | 2 | `Project-AI-main/audit_reports/historical/automation_backups_index/autobackup__README_ORIGINAL_20260420_104842.md` |
| Event Spine | Y | Y |  |  | 2 | `Project-AI-main/.hypothesis/constants/210bfb772b41132d` |
| ExecutionGate | Y | Y |  |  | 2 | `Project-AI-main/.github/instructions/refactor-engineer.agent.md` |
| Existential Proof System | Y | Y |  |  | 2 | `Project-AI-main/governance/__pycache__/existential_proof.cpython-312.pyc` |
| Extended Episodic Database | Y | Y |  |  | 2 | `Project-AI-main/integrations/openclaw/config.py` |
| Federated Cell Architecture | Y | Y |  |  | 2 | `Project-AI-main/docs/internal/DEFENSE_ENGINE_README.md` |
| Five-Channel Memory System | Y | Y |  |  | 2 | `Project-AI-main/automation-backups/wiki-conversion-20260420-104830/docs/project_ai_god_tier_diagrams/README_20260420_104910.md` |
| Flat Gap | Y | Y | Y |  | 3 | `Project-AI-main/wiki/07_Research/Publications/The-Flat-Gap.md` |
| Four-State Constitutional Machine |  |  |  |  | 0 | `` |
| Galahad | Y | Y |  |  | 2 | `Project-AI-main/.antigravity/README.md` |
| GENESIS | Y | Y | Y | Y | 4 | `Project-AI-main/.antigravity/security.yaml` |
| Genesis Event |  |  |  |  | 0 | `` |
| Genesis-Born Individual |  |  |  |  | 0 | `` |
| God-Tier Documentation Mandate |  |  |  |  | 0 | `` |
| Governance Graph | Y | Y |  |  | 2 | `Project-AI-main/web/site/about.html` |
| Governance proof checklist |  |  |  |  | 0 | `` |
| Governance-enforced development | Y |  |  |  | 1 | `Project-AI-main/.github/instructions/governance-enforced-development.instructions.md` |
| Governance-IDE / Cognitive IDE |  |  |  |  | 0 | `` |
| GSS-1 |  |  |  |  | 0 | `` |
| Hatter Tests | Y | Y |  |  | 2 | `Project-AI-main/audit_reports/historical/automation_backups_index/autobackup__README_ORIGINAL_20260420_104842.md` |
| Hub of Epstein Files Directory | Y |  |  |  | 1 | `Project-AI-main/web/site/legal.html` |
| Hydra-50 | Y | Y |  |  | 2 | `Project-AI-main/.hypothesis/constants/0d487850fa162859` |
| I AM Moment | Y | Y |  |  | 2 | `Project-AI-main/WHITEPAPER.md` |
| Identity/bonding/fates/NIRL/voice/cognition companion layer |  |  |  |  | 0 | `` |
| InvariantEngine | Y | Y |  |  | 2 | `Project-AI-main/.github/instructions/refactor-engineer.agent.md` |
| Iron Path | Y | Y |  |  | 2 | `Project-AI-main/.git/logs/HEAD` |
| Joint Council |  |  |  |  | 0 | `` |
| Lachesis | Y | Y |  |  | 2 | `Project-AI-main/.hypothesis/constants/13bc2af24a239028` |
| Liara | Y | Y |  |  | 2 | `Project-AI-main/api/__pycache__/main.cpython-312.pyc` |
| Mental-Health-Escalation-Router | Y | Y |  |  | 2 | `Project-AI-main/web/site/projects/mhe-router/index.html` |
| Miniature Office / AI City |  |  |  |  | 0 | `` |
| mono_seal.py |  |  |  |  | 0 | `` |
| Moral Codex | Y | Y |  |  | 2 | `Project-AI-main/canonical/__pycache__/sovereign_proof.cpython-312.pyc` |
| MutationGovernanceBinding | Y |  | Y |  | 2 | `Project-AI-main/src/app/core/__pycache__/mutation_binding.cpython-312.pyc` |
| NIRL | Y | Y |  |  | 2 | `Project-AI-main/.github/instructions/refactor-engineer.agent.md` |
| OAKD / Open-Access-Knowledge-Distiller |  |  |  |  | 0 | `` |
| OctoReflex | Y | Y | Y |  | 3 | `Project-AI-main/.codacy/logs/codacy-cli.log` |
| PAGL | Y | Y |  |  | 2 | `Project-AI-main/archive/docs/reports/FINAL_SOVEREIGN_AUDIT_REPORT.md` |
| Pip-Boy wrist-mount variants | Y |  |  |  | 1 | `Project-AI-main/hardware_schematics/README.md` |
| Post-Bonding Autonomy |  |  |  |  | 0 | `` |
| Project-AI identity | Y | Y |  |  | 2 | `Project-AI-main/gradle-evolution/constitutional/__pycache__/enforcer.cpython-312.pyc` |
| PSIA | Y | Y |  |  | 2 | `Project-AI-main/.git/gk/config` |
| Replay Equivalence | Y | Y |  |  | 2 | `Project-AI-main/docs/design/OMPT_luxury_dark_mode_site.md` |
| Reviewer Trap System | Y | Y |  |  | 2 | `Project-AI-main/README_ORIGINAL_BACKUP.md` |
| Right to Refusal |  |  |  |  | 0 | `` |
| SAFE_HALT | Y | Y |  |  | 2 | `Project-AI-main/.git/index` |
| Shadow Thirst | Y | Y |  |  | 2 | `Project-AI-main/__pycache__/generate_pdf.cpython-312.pyc` |
| Sovereign Audit Log | Y | Y |  |  | 2 | `Project-AI-main/recovery/ARCHIVE_RECONCILIATION_REPORT.md` |
| Sovereign Resilience Score | Y | Y |  |  | 2 | `Project-AI-main/engines/sovereign_war_room/__pycache__/demo.cpython-312.pyc` |
| Sovereign War Room | Y | Y |  |  | 2 | `Project-AI-main/IMPLEMENTATION_BACKLOG.md` |
| SovereignSoul Shield |  |  |  |  | 0 | `` |
| STATE_INTEGRITY | Y | Y |  |  | 2 | `Project-AI-main/README_ORIGINAL_BACKUP.md` |
| STATE_REGISTER | Y | Y | Y |  | 3 | `Project-AI-main/.codacy/logs/codacy-cli.log` |
| T.A.M.S.-Omega |  |  |  |  | 0 | `` |
| T.A.R.L. | Y | Y |  |  | 2 | `Project-AI-main/__pycache__/generate_pdf.cpython-312.pyc` |
| T.H.S.D. | Y | Y |  |  | 2 | `Project-AI-main/audit_reports/historical/automation_backups_index/autobackup__README_ORIGINAL_20260420_104842.md` |
| TAAR | Y | Y | Y | Y | 4 | `Project-AI-main/wiki/09_Repo-Library/Project-AI-Canonical-Reference-Pack.md` |
| The Fates | Y | Y |  |  | 2 | `Project-AI-main/WHITEPAPER.md` |
| Thirst of Gods | Y | Y |  |  | 2 | `Project-AI-main/.github/THIRST_BRANCH_ACCEPTANCE_CRITERIA.md` |
| Thirsty-Lang | Y | Y |  |  | 2 | `Project-AI-main/.gitignore` |
| Thirsty's Standards V3 |  |  |  |  | 0 | `` |
| Threat Simulation Matrix |  |  |  |  | 0 | `` |
| Three-Layer Mechanical Proof |  |  |  |  | 0 | `` |
| TK8S | Y | Y |  | Y | 3 | `Project-AI-main/.git/index` |
| Transit Gate | Y | Y |  |  | 2 | `Project-AI-main/docs/internal/archive/legion.modelfile` |
| Triumvirate | Y | Y |  |  | 2 | `Project-AI-main/.dockerignore` |
| TSCG | Y | Y |  |  | 2 | `Project-AI-main/__pycache__/generate_pdf.cpython-312.pyc` |
| TSCG-B |  |  |  |  | 0 | `` |
| User Perception and Identity Problem | Y | Y |  |  | 2 | `Project-AI-main/wiki/07_Research/Publications/User-Perception-Identity.md` |
| Volition Engine | Y | Y |  |  | 2 | `Project-AI-main/docs/governance/PROJECT_AI_SOVEREIGN_VERIFICATION_RUNBOOK.md` |
| VOS | Y | Y | Y | Y | 4 | `Project-AI-main/.venv/Lib/site-packages/wheel/macosx_libfile.py` |
| VR Observatory |  |  |  |  | 0 | `` |
| Waiting Room | Y | Y |  |  | 2 | `Project-AI-main/src/app/gui/__pycache__/dashboard_main.cpython-312.pyc` |
| Waterfall Privacy Suite | Y | Y |  |  | 2 | `Project-AI-main/archive/docs/whitepapers/WATERFALL_PRIVACY_SUITE_WHITEPAPER.md` |
| Waterfall Protocol |  |  |  |  | 0 | `` |
| Web/static public reference surfaces |  |  |  |  | 0 | `` |
| YGGDRASIL | Y | Y |  |  | 2 | `Project-AI-main/.git/index` |

## Not Found Anywhere By Exact Inventory Item Name

- Admissibility Debt
- Agency Formation
- Appointed Ambassador / Legion
- Atlas Omega
- Authority Traceability Threshold
- Camouflage and Deception Plane
- Canonical Spine / Golden Path
- Cerberus Hydra
- ChainMark
- Companion Intelligence
- COPILOT GOVERNANCE WRAPPER
- DecisionRecord Ledger
- Four-State Constitutional Machine
- Genesis Event
- Genesis-Born Individual
- God-Tier Documentation Mandate
- Governance proof checklist
- Governance-IDE / Cognitive IDE
- GSS-1
- Identity/bonding/fates/NIRL/voice/cognition companion layer
- Joint Council
- Miniature Office / AI City
- mono_seal.py
- OAKD / Open-Access-Knowledge-Distiller
- Post-Bonding Autonomy
- Right to Refusal
- SovereignSoul Shield
- T.A.M.S.-Omega
- Thirsty's Standards V3
- Threat Simulation Matrix
- Three-Layer Mechanical Proof
- TSCG-B
- VR Observatory
- Waterfall Protocol
- Web/static public reference surfaces

## Verification Limits

- This is an exact fixed-string item-name scan from the matrix rows. It does not prove absence under aliases, renamed files, acronyms, or conceptually equivalent implementations.
- `--text` was used so binary files were scanned as text. Compressed git object storage may still not reveal compressed source terms as readable text.
- No target repo files were edited during this scan.
