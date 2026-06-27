# Stage 19.5J2.1 Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J
**Discovery:** `docs/internal/PHASE_J2_1_DISCOVERY.md`, `docs/internal/PHASE_J_DISCOVERY.md`, `docs/internal/STAGE_19_5J1_ACCEPTANCE.md`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-25
**Phase scope:** Phase J2.1 — sensitivity_analyzer port from legacy atlas to canonical atlas (Path A1: full Thirsty port with numpy + scipy).

---

## 0. Phase J2.1 scope

Brings the legacy `atlas/analysis/sensitivity_analyzer.py` (489 LOC) to
canonical `packages/atlas/`. Per Path A1 (user choice 2026-06-25):
**full Thirsty port with numpy + scipy as real dependencies**.

Six source-level concepts ported:

1. `SobolIndices` — Sobol sensitivity indices per parameter
2. `StabilityMetrics` — eigenvalue stability analysis
3. `TippingPoint` — critical threshold where behavior flips
4. `ParameterPerturbation` — per-parameter perturbation sweep result
5. `SensitivityAnalyzer` — top-level engine
6. `get_sensitivity_analyzer` — factory function (legacy compat)

Plus four top-level helper functions:
- `compute_sobol_indices(samples, outputs, param_names)`
- `compute_stability_metrics(matrix)`
- `compute_parameter_perturbations(claim, evidence, drivers, *, delta, stack)`
- `find_tipping_points(driver_values, threshold_fn)`

---

## 1. Files created

| Path | Type | LOC |
|---|---|---|
| `packages/atlas/src/atlas/sensitivity.py` | source | ~895 |
| `packages/atlas/tests/test_sensitivity.py` | unit tests | ~1148 (108 tests) |
| `tests/test_atlas_sensitivity_integration.py` | integration tests | ~410 (17 tests) |
| `packages/atlas/pyproject.toml` | modified — adds numpy + scipy | 22 |
| `packages/atlas/src/atlas/__init__.py` | modified — 12 new exports | 53 |
| `docs/internal/PHASE_J2_1_DISCOVERY.md` | planning artifact | ~250 |
| **Total** | **6 files** | **~2680 LOC** |

---

## 2. Public exports (12 new)

- `ParameterPerturbation`
- `SensitivityAnalysisError`
- `SensitivityAnalyzer`
- `SensitivityReport`
- `SobolIndices`
- `StabilityMetrics`
- `TippingPoint`
- `compute_parameter_perturbations`
- `compute_sobol_indices`
- `compute_stability_metrics`
- `find_tipping_points`
- `get_sensitivity_analyzer`

---

## 3. Architectural invariants (verified)

- **Downward-only deps**: atlas imports only `kernel` + `numpy` + `scipy` + stdlib. No upward imports.
- **Canonical types**: `npt.NDArray[np.float64]` everywhere (strict typing).
- **Fail-closed**: every dataclass validates NaN, inf, blank strings, wrong types.
  - `SensitivityAnalysisError` raised on:
    - Empty/non-string parameter names
    - NaN/inf in any float field
    - Non-finite matrices (NaN, inf)
    - Non-square matrices
    - Empty matrices
    - Invalid sample/output shapes
    - Empty drivers
    - Non-positive delta
    - Non-callable threshold_fn
    - threshold_fn exceptions
- **Pluggable seams**:
  - `audit_callback: Callable | None` optional parameter
  - `tipping_threshold: Callable[[float], bool] | None` optional
  - `sobol_samples: tuple | None` optional
  - `stability_matrix: NDArray | None` optional
- **Deterministic**: SHA-256 of matrix via canonical numpy string repr.
- **Subordination notice bound to digest**: tampering with notice invalidates hash.
- **Audit chain**: every analyze_sensitivity emits log record with correlation_id.
- **Strict typing**: mypy --strict clean on 123 source files.

---

## 4. New dependencies

```
numpy>=1.24,<2.0
scipy>=1.11,<2.0
```

These are heavy packages (~50MB combined) but standard for numerical
Python. Installed via `uv sync` and locked in uv.lock.

---

## 5. Verification gates (all green)

```
=== PYTEST ===
1136 passed in 3.41s
(was 1011 baseline + 108 new unit tests + 17 new integration tests = 1136)

=== MYPY --strict ===
Success: no issues found in 123 source files
(was 121 before J2.1; +2 for sensitivity.py + __init__.py modification)

=== RUFF check ===
All checks passed!
(was 121 files; now 123)

=== RUFF format --check ===
123 files already formatted
```

---

## 6. Bugs caught + fixed during self-review (5 real bugs)

1. **mypy rejected `threshold=np.inf` for `np.array2string`**
   - Fix: use `sys.maxsize` instead (valid int per mypy stub)
2. **`decay_rate=float("inf")` for zero matrix** → dataclass rejected
   - Fix: clamp `decay_rate = 0.0` when `spectral_radius == 0.0`
3. **Test expected 1 tipping point** for threshold `v > 0.4` with d1=0.5, d2=0.7
   - Both are > 0.4 → 2 tipping points
   - Fix: corrected test expectation to 2
4. **Test expected `decay_rate == float("inf")`** for zero matrix
   - Fix: corrected to 0.0 (matches new clamped behavior)
5. **Unused `type: ignore[no-untyped-call]`** comment
   - Fix: removed

### Integration test bugs caught (3 real bugs)

6. **Wrong CapabilityAuthority API**: used `mint()` which doesn't exist
   - Fix: use `authority.issue(subject, operation, resource, ttl)`
7. **Wrong Projection API**: tried to construct with `drivers=` kwarg
   - Fix: use `analyze(claim, evidence, drivers=...)` instead
8. **Capability scope mismatch**: resource format mismatch caused DENY
   - Fix: use `f"atlas:{projection.projection_sha256}"` as resource
   - This matches the existing test_atlas.py pattern

---

## 7. Subordination contract (canonical atlas pattern)

```
SUBORDINATION_NOTICE = (
    "ATLAS output is analytical evidence only; it is not a decision, "
    "authority grant, or actuation."
)
```

All sensitivity analysis results include this notice as a frozen field.
The result hash binds the notice — tampering invalidates the digest.

---

## 8. Cross-package compatibility

The integration tests verify:

1. `Atlas.record()` works with the canonical authority + gate (existing pattern).
2. `analyze_sensitivity()` audit callback receives correct correlation_id + report_sha256 + subordination_notice.
3. `analyze_sensitivity` end-to-end (sensitivity analysis → audit → capability token → projection record → atlas.projections()).
4. SHA-256 invalidates on tampered subordination notice.
5. SHA-256 is deterministic across multiple invocations.
6. Audit callback exceptions are caught + logged, not propagated.
7. Audit callback success sets `audit_emitted = True`.

---

## 9. Phase J final state

| Sub-phase | Status |
|---|---|
| J0 | ✓ committed `9e80da9` |
| J1 | ✓ committed `b8637a2` |
| J2.1 | ⏳ THIS (this commit) |
| J2.2+ | **deferred indefinitely** (9 other features documented in J1) |

---

## 10. Self-report (v3 §35)

```
Mode: governance system (Phase J2.1 execution — sensitivity_analyzer port)
Created:
- packages/atlas/src/atlas/sensitivity.py (~895 LOC)
- packages/atlas/tests/test_sensitivity.py (~1148 LOC, 108 tests)
- tests/test_atlas_sensitivity_integration.py (~410 LOC, 17 tests)
- docs/internal/PHASE_J2_1_DISCOVERY.md (planning artifact)
- docs/internal/STAGE_19_5J2_1_ACCEPTANCE.md (this file)
Modified:
- packages/atlas/pyproject.toml (added numpy + scipy)
- packages/atlas/src/atlas/__init__.py (12 new exports)
- uv.lock (numpy + scipy resolved)
Verified:
- 1136/1136 pytest pass (1011 + 125 new sensitivity tests)
- mypy --strict clean on 123 source files
- ruff check + format clean
Failed: 5 in unit + 3 in integration — all fixed in-session.
Not verified:
- Performance benchmarks (deferred to P1 per user direction)
- Numerical stability beyond basic eigenvalue tests
- Sobol correctness vs Saltelli reference implementation
Risks:
- numpy/scipy version drift (pinned via >=1.24,<2.0 / >=1.11,<2.0)
- Ill-conditioned matrices may produce NaN (caught by validation)
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on commit)
Remaining:
- User authorization to commit + push J2.1
- Phase I4 + P1 deferred per user's "A1 only" decision
Commands run:
- uv run pytest (full)
- uv run mypy packages/ --strict
- uv run ruff check --fix --unsafe-fixes packages/ tests/
- uv run ruff format packages/ tests/
Safe to continue: yes (for commit)
```

---

## 11. Recommendations

1. **Commit Phase J2.1 + push** (this turn)
2. **Phase I4 + P1**: deferred per "A1 only" decision
3. **Future J2.x**: other legacy atlas features (Bayesian, graphs, etc.) — defer per J1 recommendation
