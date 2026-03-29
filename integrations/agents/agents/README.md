# ============================================================================ #
#                                           [2026-03-18 20:20]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 20:20             #
# COMPLIANCE: Sovereign Substrate / Integrated Service: agents / README.md
# ============================================================================ #
# Governance Agents

Static analysis agents that tell you what's real. No AI calls. No mocking. Run and exit.

## Setup

Drop the `tools/` files into your repo root `tools/` directory.
Drop the `github_workflows/architect.yml` into `.github/workflows/architect.yml`.

## Agents

| Agent | File | What It Does |
|-------|------|--------------|
| Architect | `tools/architect_agent.py` | Full file manifest. Categorizes every file. Estimates completion %. |
| Dependency | `tools/dependency_agent.py` | Maps every import. Flags unresolved ones. Detects circular deps. |
| Path Integrity | `tools/path_integrity_agent.py` | Finds import path mismatches. Suggests correct paths. |
| Stub Hunter | `tools/stub_hunter_agent.py` | Finds every stub, pass, placeholder, fake delay. |
| Dead Code | `tools/dead_code_agent.py` | Finds defined classes/functions never referenced anywhere. |
| Boot Verification | `tools/boot_verification_agent.py` | Runs the actual boot. Fails if any layer is DEGRADED/FALLBACK. |
| Completion Tracker | `tools/completion_tracker_agent.py` | Diffs against last run. Shows what improved, what regressed. |

## Run Order

```bash
# First time — build the baseline
python tools/architect_agent.py
python tools/dependency_agent.py
python tools/path_integrity_agent.py
python tools/stub_hunter_agent.py
python tools/dead_code_agent.py
python tools/completion_tracker_agent.py  # archives baseline
python tools/boot_verification_agent.py

# After making fixes — see what changed
python tools/architect_agent.py
python tools/completion_tracker_agent.py  # shows diff vs baseline
```

## Output

All manifests are written to `governance/`:

```
governance/
├── ARCHITECT_MANIFEST.json
├── ARCHITECT_MANIFEST.md
├── DEPENDENCY_MANIFEST.json
├── DEPENDENCY_MANIFEST.md
├── PATH_INTEGRITY_MANIFEST.json
├── PATH_INTEGRITY_MANIFEST.md
├── STUB_MANIFEST.json
├── STUB_MANIFEST.md
├── DEAD_CODE_MANIFEST.json
├── DEAD_CODE_MANIFEST.md
├── BOOT_VERIFICATION.json
├── BOOT_VERIFICATION.md
├── COMPLETION_TRACKER.json
├── COMPLETION_TRACKER.md
└── history/
    └── ARCHITECT_MANIFEST_YYYYMMDD_HHMMSS.json
```

## GitHub Actions

The workflow runs automatically on push to main and every Monday.
It commits the updated manifests back to the repo so you always have
a current picture of what's real.
