# Stage 19.5J2.8 Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J
**Discovery source:** `packages/_staging/atlas/cli/atlas_cli.py`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-29

---

## 0. Phase J2.8 scope

Brings the legacy Atlas operator surface into the canonical API and CLI without
giving the CLI direct governance, capability, execution, Arbiter, RLP, or Atlas
imports.

Implemented surfaces:

- Public API `GET /atlas/status`
- Protected API `POST /atlas/sludge`
- CLI command `project-ai atlas-status`
- CLI command `project-ai atlas-sludge --snapshot-file <path>`
- API package dependency on canonical `project-ai-atlas`
- CLI gateway-only tests proving no direct execution/governance dependency

This closes the J2.8 CLI / API surface gap locally. It does not claim production
deployment, public hosting, or remote CI success until the implementation commit
is pushed and GitHub Actions reports success.

---

## 1. Files created/modified

| Path | Type |
|---|---|
| `packages/api/src/project_ai_api/app.py` | API routes updated |
| `packages/api/src/project_ai_api/models.py` | API models updated |
| `packages/api/pyproject.toml` | API dependency updated |
| `packages/api/tests/test_api.py` | API tests updated |
| `packages/cli/src/project_ai_cli/app.py` | CLI commands updated |
| `packages/cli/tests/test_cli.py` | CLI tests updated |
| `packages/api/README.md` | package documentation updated |
| `packages/cli/README.md` | package documentation updated |
| `CHANGELOG.md` | unreleased checkpoint updated |
| `docs/internal/STAGE_19_5_SESSION_LEDGER.md` | current status updated |
| `docs/internal/STAGE_19_5J2_8_ACCEPTANCE.md` | this file |
| `docs/operations/CONTINUITY_MAP.md` | continuity entry updated |
| `uv.lock` | workspace dependency lock updated |

---

## 2. Verification gates

Red test evidence before source implementation:

```text
uv run python -m pytest packages/api/tests/test_api.py packages/cli/tests/test_cli.py -q
7 failed, 24 passed

Representative failures:
- KeyError: 'status' for GET /atlas/status
- 404 for POST /atlas/sludge
- exit_code 2 for missing CLI command atlas-status
```

Executed before this acceptance file was written:

```text
uv run python -m pytest packages/api/tests/test_api.py packages/cli/tests/test_cli.py -q
31 passed in 1.14s

uv run ruff check packages/api/src/project_ai_api packages/api/tests packages/cli/src/project_ai_cli packages/cli/tests
All checks passed!

uv run mypy packages/api/src packages/api/tests packages/cli/src packages/cli/tests
Success: no issues found in 9 source files

uv run ruff check .
All checks passed!

uv run ruff format --check .
185 files already formatted

uv run mypy --ignore-missing-imports packages/kernel/src packages/security/src packages/governance/src packages/capability/src packages/execution/src packages/companion/src packages/swr/src packages/atlas/src packages/arbiter/src packages/rlp/src packages/api/src packages/cli/src apps/desktop/src apps/services/src tools
Success: no issues found in 92 source files

uv run python -m pytest -q --tb=short
1456 passed in 3.80s

QT_QPA_PLATFORM=offscreen uv run python -m pytest -q --tb=short --cov=kernel --cov=security --cov=governance --cov=capability --cov=execution --cov=companion --cov=swr --cov=atlas --cov=arbiter_gov --cov=rlp --cov=project_ai_api --cov=project_ai_cli --cov=project_ai_desktop --cov=project_ai_services --cov-branch --cov-report=term-missing --cov-fail-under=80
1456 passed, 89.35% branch coverage, threshold 80%

uv run python tools/canonical_replay.py
canonical replay: 5/5 invariants passed

uv run python tools/verify_frozen_history.py
CHAIN INTACT. 2264 sections verified.

SKIP=no-commit-to-branch,gitleaks uv run pre-commit run --all-files
Passed all non-skipped hooks.
```

Coverage emitted the existing warning that `arbiter_gov` was not imported.
Classification: not blocking current task; the coverage command exited 0 and
remained above threshold.

Remote CI after commit/push:

```text
GitHub Actions CI run 28348049368
Commit: 2e6644344cb2f17a1f506243600a170706dbe8c1
Conclusion: success
URL: https://github.com/IAmSoThirsty/Project-AI/actions/runs/28348049368
```

The run emitted a non-blocking cache reservation annotation in the SBOM job.
Classification: not blocking current task; the workflow conclusion was success.

---

## 3. Architectural invariants verified

- **Gateway-only CLI:** CLI tests still prove `project-ai-cli` depends only on
  Typer and does not import governance, capability, execution, Arbiter, or RLP
  internals.
- **Analysis-only Atlas status:** `/atlas/status` returns subordination language
  and labels the surface as `analysis_only`.
- **Protected Sludge generation:** `/atlas/sludge` requires the existing
  protected API configuration and bearer token.
- **Audit-visible Sludge route:** successful Sludge generation appends an
  `atlas.sludge_narrative` hash-chain record through the configured API audit
  relay.
- **No raw snapshot in CLI arguments:** `atlas-sludge` reads the Reality Stack
  snapshot from `--snapshot-file` and posts it through the gateway.
- **Fail-closed validation:** invalid archetypes and non-RS snapshots are
  rejected with HTTP 422 before an artifact is accepted.

---

## 4. Remaining J2 work

- J2.8 CLI / API surface is closed with implementation CI evidence.
- The next open J1 audit gap after J2.8 is J2.9 replay system, unless the user
  pivots.

Safe to continue: yes.
