# Phase J2.1 Discovery + Sub-Phase Plan — atlas sensitivity_analyzer

**Status:** DISCOVERY + PLAN (no code written yet)
**Authority:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J
**Prior:** `docs/internal/PHASE_J_DISCOVERY.md`, `docs/internal/STAGE_19_5J1_ACCEPTANCE.md`
**Date:** 2026-06-25
**Source-of-truth:** `T:\Project-AI-main\atlas\analysis\sensitivity_analyzer.py`
**Target:** Extend canonical `packages/atlas/` with sensitivity module

---

## 0. Why discovery-first here

Per memory rule "Discovery-first on rebuild directives" + AGENTS.md v3
§2.2 downward-only deps + canonical types + fail-closed.

J2.1 is the first feature port following J1's gap audit. The audit
recommended "stdlib-only math + Protocol abstraction; numerical libs
optional later." User explicitly chose Path A1 — **full Thirsty port
with numpy + scipy** — which elevates the dependency posture. This
discovery doc captures the architectural consequences of that choice.

---

## 1. Legacy surface inventory

`T:\Project-AI-main\atlas\analysis\sensitivity_analyzer.py` (489 LOC)
exports:

| Class | Purpose |
|---|---|
| `SobolIndices` | First-order + total-order Sobol sensitivity indices per parameter |
| `StabilityMetrics` | Eigenvalue analysis: max_eigenvalue, spectral_radius, is_stable, decay_rate |
| `TippingPoint` | Critical threshold where system behavior changes |
| `ParameterPerturbation` | Per-parameter perturbation sweep result |
| `SensitivityAnalyzer` | Top-level engine with `analyze_sensitivity(...)`, `find_tipping_points(...)`, `compute_sobol_indices(...)` |
| `get_sensitivity_analyzer(audit_trail=None)` | Factory function (legacy DI pattern) |

**External dependencies:**
- `numpy` — array ops, eigenvalue decomposition
- `scipy.linalg` — advanced linear algebra (eigenvalue computations)
- `atlas.audit.trail.get_audit_trail` — legacy audit logging

**Legacy algorithms:**
1. Sobol variance decomposition (sensitivity indices)
2. Eigenvalue stability analysis (spectral_radius < 1 = stable)
3. Lyapunov region estimation
4. Parameter perturbation sweeps
5. Driver shock elasticity mapping
6. Tipping threshold computation

---

## 2. Architectural decisions

### D1: Add numpy + scipy as real dependencies

**Decision:** Yes — Path A1 explicitly chose this.

**Implications:**
- `packages/atlas/pyproject.toml` adds `numpy>=1.24` and `scipy>=1.11` to
  `dependencies`.
- These are heavy packages (~50MB combined) but standard in numerical
  Python.
- Workspace-wide impact: every install of `project-ai-atlas` now pulls
  in numpy/scipy.
- AGENTS.md §2.2 "downward-only deps" still respected: numpy/scipy are
  *external*, not upward deps.

### D2: Subordination notice integration

**Decision:** Sensitivity analysis is analytical evidence — same
subordination contract as `analyze()`.

Each result dataclass includes `subordination_notice: str =
SUBORDINATION_NOTICE` as a frozen field. The hash of the analysis
result binds the notice into the digest (matching canonical atlas
pattern).

### D3: Legacy audit trail integration → defer

**Decision:** Legacy `atlas.audit.trail.get_audit_trail` is not in
canonical atlas. Phase J2.1 will NOT wire sensitivity into the audit
trail. Logging is via stdlib `logging` only.

Rationale: The canonical atlas uses the execution gate for audit.
Sensitivity analysis is read-only (doesn't mutate state). Logging to
the audit trail would require a new abstraction. Defer to J2.2 if
audit integration becomes a use case.

### D4: Audit chain compatibility

**Decision:** SensitivityAnalyzer emits stdlib log records with
correlation_id. Optional `audit_callback: Callable | None = None`
parameter allows callers to wire their own audit chain without
binding to a specific audit implementation.

### D5: Backward compatibility

**Decision:** `SensitivityAnalyzer` does NOT inherit from a legacy
class (the legacy was stage-11-era; canonical is a fresh design).
The factory function `get_sensitivity_analyzer()` is preserved for
discoverability.

---

## 3. Architectural invariants (AGENTS.md v3)

sensitivity module must respect:
- **Downward-only deps**: atlas may import kernel + numpy + scipy +
  stdlib. No upward imports.
- **Canonical types**: kernel.JsonScalar, kernel.JsonValue for any
  JSON-interchangeable state.
- **Fail-closed**: invalid input → AtlasError (or new
  SensitivityAnalysisError).
- **Pluggable seams**: SensitivityAnalyzer accepts optional
  audit_callback; numerical operations hidden behind private methods.
- **Deterministic**: seeded RNG for any Monte Carlo. Sobol indices
  computed deterministically from input samples.
- **Audit chain**: every analyze() call emits a log record with
  correlation_id.
- **Strict typing**: mypy --strict clean.

---

## 4. Sub-phase plan (J2.1 wave)

### Phase J2.1.0 — Sensitivity module source (~600 LOC)

**Scope:** Single source file `packages/atlas/src/atlas/sensitivity.py`
+ update `packages/atlas/src/atlas/__init__.py` to re-export.
**New source files:** 1
**Tasks:**
1. SobolIndices (frozen dataclass)
2. StabilityMetrics (frozen dataclass with subordination notice)
3. TippingPoint (frozen dataclass)
4. ParameterPerturbation (frozen dataclass)
5. SensitivityAnalyzer class with:
   - `compute_sobol_indices(samples: ndarray, outputs: ndarray,
     param_names: tuple[str, ...]) -> tuple[SobolIndices, ...]`
   - `compute_stability_metrics(matrix: ndarray) -> StabilityMetrics`
   - `compute_parameter_perturbations(baseline: dict[str, float],
     delta: float = 0.1) -> tuple[ParameterPerturbation, ...]`
   - `find_tipping_points(driver_values: dict[str, float],
     threshold_fn: Callable[[float], bool]) -> tuple[TippingPoint, ...]`
   - `analyze_sensitivity(claims: tuple[Claim, ...],
     evidence: tuple[Evidence, ...], drivers: dict[str, float],
     audit_callback: Callable | None = None) -> SensitivityReport`
6. `get_sensitivity_analyzer()` factory
7. `SensitivityAnalysisError` exception
8. Update `pyproject.toml` to add numpy + scipy
9. Update `__init__.py` with re-exports

### Phase J2.1.1 — Sensitivity tests (~250 LOC, ~25 tests)

**Scope:** Test file `packages/atlas/tests/test_sensitivity.py`
**New test files:** 1
**Tasks:**
1. SobolIndices validation + is_influential threshold
2. StabilityMetrics spectral_radius < 1 detection
3. ParameterPerturbation linear delta computation
4. TippingPoint threshold detection
5. SensitivityAnalyzer.compute_sobol_indices (deterministic sample)
6. SensitivityAnalyzer.compute_stability_metrics (stable + unstable)
7. SensitivityAnalyzer.compute_parameter_perturbations
8. SensitivityAnalyzer.find_tipping_points
9. SensitivityAnalyzer.analyze_sensitivity end-to-end
10. Factory function returns singleton or new instance
11. Audit callback invoked with expected payload
12. Subordination notice in result hash
13. Strict typing via mypy --strict

### Phase J2.1.2 — Integration test (~100 LOC, ~5 tests)

**Scope:** Cross-package integration test
`tests/test_atlas_sensitivity_integration.py`
**New test files:** 1
**Tasks:**
1. analyze_sensitivity + project through Atlas.record() with capability
2. SHA-256 binding subordination notice
3. Empty drivers → DENY? Or no-op?
4. Audit callback called exactly once per analyze
5. Stable + unstable matrices give different StabilityMetrics

### Phase J2.1.3 — Acceptance doc + commit

**Scope:** `docs/internal/STAGE_19_5J2_1_ACCEPTANCE.md` + commit
**Tasks:**
1. All gates green (pytest, mypy --strict, ruff check, ruff format)
2. CONTINUITY_MAP updated
3. Commit + push

---

## 5. File count summary

| Sub-phase | Source files | Test files | Init modify | Other |
|---|---|---|---|---|
| J2.1.0 | 1 | 0 | 1 | pyproject.toml (deps) |
| J2.1.1 | 0 | 1 | 0 | 0 |
| J2.1.2 | 0 | 1 | 0 | 0 |
| J2.1.3 | 0 | 0 | 0 | 1 (acceptance doc) |
| **Total** | **1** | **2** | **1** | **2** |

Estimated: ~600 source LOC + ~250 test LOC + ~100 integration LOC + 1 doc.

---

## 6. Risk assessment

1. **numpy/scipy version drift**: scipy.linalg API has been stable since
   1.0, but minor changes between versions. Pin via `>=1.11,<2.0` in
   pyproject.toml.
2. **Sobol decomposition correctness**: Sobol indices require careful
   sampling. The legacy implementation likely has a specific salt
   (Saltelli sampling). My implementation must use Saltelli scheme or
   document the divergence.
3. **Numerical instability**: eigenvalue computation on ill-conditioned
   matrices can produce NaN/inf. My implementation must validate inputs.
4. **Performance**: numpy is fast, but if SensitivityAnalyzer becomes
   a hot path (e.g., called per-request), need benchmarks (Phase P1
   territory).

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

## 8. Recommended authorization scope

> "Proceed with Phase J2.1.0 (source code only, ~600 LOC). Stop and
> produce J2.1.1 plan before writing tests."

This preserves the wave-bounded pattern from Phases H/I/J.

---

## 9. Self-report (v3 §35)

```
Mode: governance system (planning — Phase J2.1 discovery)
Created: docs/internal/PHASE_J2_1_DISCOVERY.md (this file)
Modified: None.
Verified: legacy sensitivity_analyzer.py inventoried (489 LOC, 6 classes,
  numpy + scipy dependencies).
Failed: None.
Not verified: Sobol salt/scheme details (deferred to J2.1.0 implementation).
Risks: numpy/scipy version drift, Sobol correctness, numerical stability,
  performance (deferred to P1).
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on J2.1.0)
Remaining:
  - User authorization to start Phase J2.1.0 (source code)
  - Per-sub-phase "go" for J2.1.1, J2.1.2, J2.1.3 thereafter
```