# Stage 19.5J2.6 Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J
**Discovery source:** `packages/_staging/atlas/analysis/failure_surveillance.py`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-28

---

## 0. Phase J2.6 scope

Brings legacy failure-mode surveillance checks into canonical Atlas as
audit-visible analytical monitoring:

- `AnomalyType`
- `SeverityLevel`
- `SurveillanceThresholds`
- `Anomaly`
- `SystemHealth`
- `FailureSurveillanceSystem`
- `get_failure_surveillance`
- `reset_failure_surveillance`
- drift detection
- driver volatility detection
- influence-graph edge inflation detection
- claim posterior explosion detection
- Sludge-to-Reality-Stack narrative bleed detection
- sensitivity blowup detection
- parameter bounds violation detection
- SHA-256 hash-integrity mismatch detection
- local abort-condition reporting
- local kill-switch state with audit evidence

This closes the J2.6 failure-surveillance gap locally. It does not claim
external actuation, production deployment, or autonomous shutdown. The
kill-switch is local surveillance state and audit evidence only.

---

## 1. Files created/modified

| Path | Type |
|---|---|
| `packages/atlas/src/atlas/failure_surveillance.py` | source (new) |
| `packages/atlas/src/atlas/__init__.py` | public exports updated |
| `packages/atlas/tests/test_failure_surveillance.py` | unit tests (new) |
| `packages/atlas/README.md` | package documentation updated |
| `CHANGELOG.md` | unreleased checkpoint updated |
| `docs/internal/STAGE_19_5_SESSION_LEDGER.md` | current status updated |
| `docs/internal/STAGE_19_5J2_6_ACCEPTANCE.md` | this file |
| `docs/operations/CONTINUITY_MAP.md` | continuity entry updated |

---

## 2. Verification gates

Red test evidence before source implementation:

```text
uv run python -m pytest packages/atlas/tests/test_failure_surveillance.py -q
ImportError: cannot import name 'Anomaly' from 'atlas'
```

Executed before this acceptance file was written:

```text
uv run python -m pytest packages/atlas/tests/test_failure_surveillance.py -q
21 passed in 0.31s

uv run mypy packages/atlas/src/atlas/failure_surveillance.py packages/atlas/tests/test_failure_surveillance.py --strict
Success: no issues found in 2 source files

uv run python -m pytest packages/atlas/tests/test_failure_surveillance.py packages/atlas/tests -q
349 passed in 0.78s

uv run ruff check .
All checks passed!

uv run ruff format --check .
183 files already formatted

uv run mypy --ignore-missing-imports packages/kernel/src packages/security/src packages/governance/src packages/capability/src packages/execution/src packages/companion/src packages/swr/src packages/atlas/src packages/arbiter/src packages/rlp/src packages/api/src packages/cli/src apps/desktop/src apps/services/src tools
Success: no issues found in 91 source files

uv run python -m pytest -q --tb=short
1441 passed in 4.25s

QT_QPA_PLATFORM=offscreen uv run python -m pytest -q --tb=short --cov=kernel --cov=security --cov=governance --cov=capability --cov=execution --cov=companion --cov=swr --cov=atlas --cov=arbiter_gov --cov=rlp --cov=project_ai_api --cov=project_ai_cli --cov=project_ai_desktop --cov=project_ai_services --cov-branch --cov-report=term-missing --cov-fail-under=80
1441 passed, 89.57% branch coverage, threshold 80%

uv run python tools/canonical_replay.py
canonical replay: 5/5 invariants passed

uv run python tools/verify_frozen_history.py
CHAIN INTACT. 2264 sections verified.
```

Coverage emitted the existing warning that `arbiter_gov` was not imported.
Classification: not blocking current task; the coverage command exited 0 and
remained above threshold.

---

## 3. Architectural invariants verified

- **Observation only:** Failure surveillance records anomalies and local state;
  it does not execute actions, issue capabilities, or bypass the execution
  gate.
- **Audit-visible:** Initialization, anomaly detection, abort conditions, reset,
  and kill-switch activation can append hash-chained `AuditTrail` events.
- **Fail-closed validation:** Invalid thresholds, hashes, non-finite values,
  invalid timestamps, and impossible edge baselines raise
  `FailureSurveillanceError`.
- **Deterministic tests:** The system accepts a clock callable so tests can
  prove stable timestamps.
- **Subordination preserved:** `Anomaly`, `SystemHealth`, and statistics carry
  the canonical Atlas subordination notice.
- **No hidden dependency:** The canonical implementation uses stdlib
  `statistics.pstdev`; it does not require the legacy NumPy import path.

---

## 4. Remaining J2 work

- J2.6 failure surveillance is locally closed.
- The next open J1 audit gap after J2.6 is J2.7 sandbox, unless the user pivots.

Safe to continue: yes.
