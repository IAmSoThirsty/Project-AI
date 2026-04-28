# Root Cleanup — Known Problems Register

**Date:** 2026-04-28
**Status:** Active

## Cleanup outcome

- Root report/script candidates remaining: **0**
- Root files reduced to an essentials-first set (84 files at validation time)
- Report relocation actions: **253**
  - Moved to `docs/reports/`: **95**
  - Root duplicates removed (already present in `docs/reports/`): **145**
  - Conflicting-name files preserved in `docs/reports/root_conflicts/`: **13**
- Script relocation actions: **43** moved to `scripts/automation/`, `scripts/verify/`, `scripts/demo/`

## Known problems (tracked, not ignored)

1. **Report conflicts requiring merge decisions**
   - ✅ **Resolved (2026-04-28)**
   - 13 same-name files were reviewed and promoted to canonical versions in `docs/reports/`
   - `docs/reports/root_conflicts/` now only retains process documentation (`README.md`)
   - Residual risk: low (conflict set closed)

2. **Large existing workspace delta unrelated to this cleanup**
   - There are many pre-existing modified/untracked files in the workspace
   - Risk: harder review signal/noise during future commits

3. **Root artifact files still present by design**
   - ⚠️ **Partially remediated (Phase 2 + Phase 2B sweeps, 2026-04-28)**
   - 19 low/medium-coupled root artifacts were relocated to `test-artifacts/` with reference/path updates
   - Phase 2B moved: `classification_plan.json`, `constitutional_validation_report.txt`, `verification_report.json`
   - Remaining root JSON/TXT files are intentionally retained high-coupling config/dependency manifests per root-structure policy
   - Risk: low-to-moderate (re-accumulation remains possible without recurring hygiene controls)

## Integrated fix plan

- [x] **Resolve conflict files** in `docs/reports/root_conflicts/` and either merge into canonical report or archive decisively
- [x] **Stabilize root artifact policy** (either move artifacts + update references, or codify allowed root artifact list)
- [ ] **Enforce recurring root hygiene** using a periodic cleanup pass and pre-commit review of new root files
- [ ] **Add/refresh lightweight documentation** for “what belongs in root” in contributor docs

## Phase 2 sweep update (2026-04-28)

- Relocated 16 root artifacts to `test-artifacts/`
- Updated active report references to new artifact paths in `docs/reports/AGENT_009_MISSION_COMPLETE_CHECKLIST.md`, `docs/reports/AGENT_009_P0_GOVERNANCE_SECURITY_METADATA_REPORT.md`, `docs/reports/AGENT_017_COMPLETION.md`, `docs/reports/AGENT-007-MISSION-SUMMARY.md`, `docs/reports/AGENT-007-DOCUMENTATION-INDEX.md`, `docs/reports/vault-sign-off-document.md`, and `docs/reports/vault-validation-report.md`.

## Phase 2B sweep update (2026-04-28)

- Relocated 3 additional verification artifacts to `test-artifacts/`: `classification_plan.json`, `constitutional_validation_report.txt`, `verification_report.json`.
- Updated reference/output paths in `.github/COPILOT_MANDATORY_GUIDE.md`, `docs/reports/HONEST-ACCOUNTABILITY-REPORT.md`, `src/app/core/validate_constitution.py`, `project_ai_cli.py`, `docs/architecture/SOVEREIGN_VERIFICATION_GUIDE.md`, `docs/architecture/SOVEREIGN_RUNTIME.md`, and `source-docs/cli-automation/04-SOVEREIGN-CLI.md`.

## Notes

This register intentionally treats prior issues as **known active issues** and includes a concrete remediation path.
