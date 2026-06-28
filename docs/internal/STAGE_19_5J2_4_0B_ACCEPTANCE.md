# Stage 19.5J2.4.0b Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J
**Discovery:** `docs/internal/PHASE_J2_4_DISCOVERY.md`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-28

---

## 0. Phase J2.4.0b scope

Brings the second graph-construction wave to canonical Atlas:

- `DriverType`
- `DriverDimension`
- `DriverState`
- `PCAResult`
- `DriverAnalysis`
- `DriverEngine`
- 10-dimensional historical anchor normalization
- deterministic state and analysis hashes with `SUBORDINATION_NOTICE` bound
- PCA via `numpy.linalg.eigh` over covariance matrices
- correlation matrices
- derived risk/control/stability metrics
- driver sensitivities against a selected derived metric
- optional `AuditTrail` integration for init, state creation, analysis, and
  fail-closed state-creation failures

This closes Wave 2 of the J2.4 graph-construction gap. J2.4 is not fully closed
until the temporal-graph wave is implemented or explicitly deferred.

---

## 1. Files created/modified

| Path | Type |
|---|---|
| `packages/atlas/src/atlas/driver_engine.py` | source (new) |
| `packages/atlas/src/atlas/__init__.py` | public exports updated |
| `packages/atlas/tests/test_driver_engine.py` | unit tests (new) |
| `tests/test_atlas_driver_engine_integration.py` | integration tests (new) |
| `packages/atlas/README.md` | package documentation updated |
| `CHANGELOG.md` | unreleased development checkpoint updated |
| `docs/internal/PHASE_J2_4_DISCOVERY.md` | wave status updated |
| `docs/internal/STAGE_19_5_SESSION_LEDGER.md` | next-session state updated |
| `docs/internal/STAGE_19_5J2_4_0B_ACCEPTANCE.md` | this file |
| `docs/operations/CONTINUITY_MAP.md` | continuity entry updated |

---

## 2. Verification gates

Executed before this acceptance file was written:

```text
uv run pytest packages/atlas/tests/test_driver_engine.py tests/test_atlas_driver_engine_integration.py -q
24 passed in 0.44s

uv run pytest packages/atlas/tests tests/test_atlas_graph_integration.py tests/test_atlas_driver_engine_integration.py tests/test_atlas_audit_integration.py tests/test_atlas_bayesian_integration.py tests/test_atlas_sensitivity_integration.py -q
381 passed in 0.73s

uv run mypy packages/atlas/src/atlas/driver_engine.py packages/atlas/tests/test_driver_engine.py tests/test_atlas_driver_engine_integration.py --strict
Success: no issues found in 3 source files

uv run ruff check packages/atlas/src/atlas/driver_engine.py packages/atlas/src/atlas/__init__.py packages/atlas/tests/test_driver_engine.py tests/test_atlas_driver_engine_integration.py
All checks passed!

uv run ruff format --check packages/atlas/src/atlas/driver_engine.py packages/atlas/src/atlas/__init__.py packages/atlas/tests/test_driver_engine.py tests/test_atlas_driver_engine_integration.py
4 files already formatted
```

Full repo gates executed after this acceptance file was created:

```text
uv run ruff check .
All checks passed!

uv run ruff format --check .
175 files already formatted

uv run mypy --ignore-missing-imports packages/kernel/src packages/security/src packages/governance/src packages/capability/src packages/execution/src packages/companion/src packages/swr/src packages/atlas/src packages/arbiter/src packages/rlp/src packages/api/src packages/cli/src apps/desktop/src apps/services/src tools
Success: no issues found in 88 source files

uv run pytest -q --tb=short
1391 passed in 3.45s

QT_QPA_PLATFORM=offscreen uv run pytest -q --tb=short --cov=kernel --cov=security --cov=governance --cov=capability --cov=execution --cov=companion --cov=swr --cov=atlas --cov=arbiter_gov --cov=rlp --cov=project_ai_api --cov=project_ai_cli --cov=project_ai_desktop --cov=project_ai_services --cov-branch --cov-report=term-missing --cov-fail-under=80
1391 passed, 90.80% branch coverage, threshold 80%

uv run python tools/canonical_replay.py
canonical replay: 5/5 invariants passed

uv run python tools/verify_frozen_history.py
CHAIN INTACT. 2264 sections verified.

SKIP=no-commit-to-branch,gitleaks uv run pre-commit run --all-files
passed all non-skipped hooks
```

Coverage emitted the existing warning that `arbiter_gov` was not imported.
Classification: not blocking current task; the coverage command exited 0 and
remained above threshold.

---

## 3. Public API added

| Symbol | Purpose |
|---|---|
| `DriverEngineError` | fail-closed driver exception |
| `DriverType` | canonical 10-dimensional driver enum |
| `DriverDimension` | weighted driver dimension |
| `DriverState` | normalized 10D state with deterministic SHA-256 |
| `PCAResult` | PCA components, explained variance, mean vector |
| `DriverAnalysis` | PCA, correlations, sensitivities, derived metrics |
| `DriverEngine` | normalization and analysis engine |
| `compute_pca` | deterministic PCA helper |
| `compute_correlation_matrix` | driver correlation matrix helper |
| `compute_driver_sensitivities` | finite-difference sensitivity helper |
| `compute_derived_metrics` | composite driver metric helper |
| `compute_state_hash` | canonical state hash helper |
| `get_driver_engine` | singleton factory |
| `reset_driver_engine` | singleton reset |

---

## 4. Architectural invariants verified

- **Downward-only deps:** `atlas.driver_engine` imports only `atlas.analysis`,
  `atlas.audit`, stdlib, and numpy.
- **Fail-closed:** missing drivers, invalid normalized values, invalid PCA
  inputs, invalid target metrics, invalid hashes, and invalid audit trail types
  raise `DriverEngineError`.
- **Subordination:** every public result dataclass carries
  `SUBORDINATION_NOTICE`; state and analysis hash bodies include that notice.
- **Deterministic:** states are canonicalized by driver order; PCA and analysis
  outputs are order-independent for equivalent input state sets.
- **Audit-visible:** init, state creation, analysis completion, and
  state-creation failure paths emit hash-chained `AuditTrail` events when a
  trail is attached.
- **Legacy-compatible semantics:** historical ranges, 10D driver set, derived
  metrics, and normalization behavior are ported from
  `packages/_staging/atlas/core/drivers/driver_engine_10d.py`; legacy config
  file creation was intentionally not ported because canonical Atlas should not
  create hidden baseline files during import or construction.

---

## 5. Remaining J2.4 work

- J2.4.0c: `temporal_graph.py` snapshot/change/evolution tracking.

Safe to continue: yes.
