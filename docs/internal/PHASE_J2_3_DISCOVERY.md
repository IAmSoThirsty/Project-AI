# Phase J2.3 Discovery — atlas Bayesian inference engine

**Status:** DISCOVERY + PLAN (no source code written yet)
**Authority:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J, J1 audit
**Date:** 2026-06-25
**Author:** Hermes (Quencher session)

---

## 0. Context

The J1 audit identified **9 feature gaps** in canonical atlas. Two have
been closed (J2.1 sensitivity, J2.2 audit trail). The remaining 7:

1. **Bayesian inference** — legacy has `core/bayesian_engine.py` (~498 LOC).
   Canonical uses simple arithmetic in `analyze()`. **THIS PHASE.**
2. Graph construction (driver_engine_10d, graph builder, temporal graph)
3. Constitutional kernel integration
4. Failure surveillance
5. Sandbox (sludge_sandbox)
6. CLI / API surface
7. Replay system (for analysis, distinct from audit replay)

J2.3 = Bayesian engine port. **Path A1** per established pattern: faithful
port of legacy code with numpy (already a dep) + scipy (already a dep),
no shortcuts.

---

## 1. Legacy code analysis (`atlas/core/bayesian_engine.py`, 498 LOC)

### Public surface
- `BayesianClaimEngine` class — main engine
- `get_bayesian_engine()` — global factory
- `reset_bayesian_engine()` — reset for testing

### `BayesianClaimEngine` methods
| Method | LOC | Purpose |
|---|---|---|
| `__init__` | 30 | Init audit + config + kernel + tier weights + stack penalties |
| `_load_stack_penalties` | 15 | Load penalties from config (with fallback defaults) |
| `calculate_claim_posterior` | 85 | Main formula: EL × WDP × StackPenalty × AgencyPenalty |
| `_calculate_evidence_legitimacy` | 45 | Weighted average + TierA bonus |
| `_calculate_driver_posterior` | 50 | Range alignment with exponential decay |
| `_normalize` | 3 | Clamp to [0, 1] |
| `_apply_temporal_decay` | 30 | Exponential half-life decay |
| `process_claim` | 45 | Orchestration: posterior + envelope |
| `influence_agent_perception` | 40 | Apply high-posters to agent state |
| `get_high_posterior_claims` | 20 | Filter by threshold |

### Formula (legacy)

```
P_claim = clamp(
    EvidenceLegitimacy(evidence)
    × WeightedDriverPosterior(claim, drivers)
    × StackPenalty(stack)
    × AgencyPenalty(claim_type, evidence),
    0, 1
)
```

Then temporal decay if claim has decay_half_life + timestamp.

### Evidence Legitimacy (EL)
```
weighted_sum = Σ tier_weight × confidence
total_weight = Σ tier_weight
EL = min((weighted_sum / len(evidence)) × (1.1 if ≥2 TierA else 1.0), 1.0)
```

### Weighted Driver Posterior (WDP)
For each driver dependency in claim:
- If actual ∈ expected_range: alignment = 1.0
- Else: alignment = exp(-distance × 2.0)
WDP = mean(alignments) — or 0.7 if no dependencies

### Stack Penalties
```
RS = 1.0   # Reality Stack
TS-0 = 1.0
TS-1 = 1.0
TS-2 = 0.95
TS-3 = 0.90
SS = 0.0   # Simulation Stack — claims have NO legitimacy
default = 1.0
```

### Agency Penalty
If claim type is AGENCY and NO TierA/B evidence:
  agency_penalty = 0.5

### Tier weights
```
TierA = 1.00  # Peer-reviewed / official audited
TierB = 0.85  # Government statistical archives
TierC = 0.65  # Reputable institutional reporting
TierD = 0.40  # Media / secondary analysis
```

### Temporal decay
```
P(t) = P_0 × exp(-ln(2) × age_days / half_life)
```

### External dependencies in legacy
- `atlas.audit.trail.AuditCategory`, `AuditLevel`, `get_audit_trail`
- `atlas.config.loader.get_config_loader`
- `atlas.governance.constitutional_kernel.get_constitutional_kernel`
- `logging`, `math`, `datetime`, `enum`, `typing`

---

## 2. Canonical atlas current state

| File | LOC | Purpose |
|---|---|---|
| `analysis.py` | 120 | Evidence-weighted deterministic analysis |
| `service.py` | 116 | Execution-gated persistence (now with audit) |
| `sensitivity.py` | 895 | Sobol decomposition + stability + tipping |
| `audit.py` | 626 | Hash-chained audit trail |

**Existing posterior calculation** (`analysis.py`):
```python
def analyze(claim, evidence, drivers=None, stack="RS"):
    tier_weights = {"A": 1.0, "B": 0.85, "C": 0.65, "D": 0.4}
    stack_penalty = {"SS": 0.0, "TS-0": 1.0, "TS-1": 0.95}.get(stack, 1.0)
    agency_penalty = 0.5 if claim.claim_type == AGENCY and no A/B evidence else 1.0
    driver_factor = product of driver values, default 1.0
    return Projection(
        posterior=clamp(evidence × driver × stack × agency, 0, 1),
        ...
    )
```

**Gap**: canonical uses simple arithmetic mean of evidence. Legacy uses:
- Tier-weighted confidence average
- Driver range alignment with exponential decay
- Exponential temporal decay
- Per-driver expected ranges (not raw driver values)

---

## 3. Port design

### Decision: New module `packages/atlas/src/atlas/bayesian.py`

Path A1 = faithful port. Add a NEW module that provides Bayesian inference
WITHOUT removing the existing `analyze()` function. This means:
- `analyze()` continues to work as it does (backward compat)
- New `BayesianClaimEngine` provides richer inference
- `analyze()` can OPTIONALLY delegate to Bayesian engine (feature flag)

### Public API additions

| Symbol | Type | Purpose |
|---|---|---|
| `StackPenalty` | class | Stack enum + penalty table |
| `TierWeight` | class | Tier enum + weight table |
| `BayesianConfig` | frozen dataclass | Tier weights + stack penalties + agency penalty |
| `BayesianClaim` | frozen dataclass | Typed claim with optional timestamp + decay_half_life + driver_dependencies |
| `BayesianEvidence` | frozen dataclass | source + tier + confidence |
| `BayesianAnalysis` | frozen dataclass | posterior + components + decay_factor |
| `BayesianClaimEngine` | class | Main engine (calculate_claim_posterior, process_claim) |
| `calculate_bayesian_posterior` | function | Convenience function (no class) |
| `get_bayesian_engine` | function | Global factory |
| `reset_bayesian_engine` | function | Reset for testing |
| `BayesianEngineError` | class | Exception |

### Config defaults (canonical)
- Match legacy defaults exactly (faithful port)
- Configurable via `BayesianConfig` parameter

### Determinism
- Engine takes optional `seed: int = None` (for any stochastic ops; current
  legacy has none, so seed is for future extension)
- All hashes SHA-256 canonical
- All results reproducible

### Audit integration
- Optional `audit_trail: AuditTrail | None = None`
- Emits events matching legacy categories:
  - `SYSTEM/INFORMATIONAL` on engine init
  - `VALIDATION/HIGH_PRIORITY` on agency penalty
  - `OPERATION/STANDARD` on posterior calculation
- All events include calculation details

### Downward-only deps
- `atlas.analysis.SUBORDINATION_NOTICE` for binding
- `atlas.audit.AuditTrail`, `AuditCategory`, `AuditLevel` (optional)
- stdlib only (no numpy/scipy needed — pure arithmetic + math.exp)

---

## 4. Sub-phase plan

### J2.3.0 — Source code (~450 LOC)
- `packages/atlas/src/atlas/bayesian.py`
- Update `packages/atlas/src/atlas/__init__.py` (12+ new exports)
- mypy --strict clean on 126 source files (was 125 + 1 new)
- ruff check + format clean

### J2.3.1 — Unit tests (~30 tests)
- `packages/atlas/tests/test_bayesian.py`
- Coverage: every formula path, every edge case, every dataclass
  validation, every error path, determinism, audit callback, config
- pytest pass count: 1224 + 30 = 1254

### J2.3.2 — Integration tests (~10 tests)
- `tests/test_atlas_bayesian_integration.py`
- Coverage: end-to-end with audit trail, with execution gate, with
  legacy claims, with mixed tier evidence, with temporal decay
- pytest pass count: 1224 + 30 + 10 = 1264

### J2.3.3 — Acceptance doc + commit + push
- `docs/internal/STAGE_19_5J2_3_ACCEPTANCE.md`
- Update CONTINUITY_MAP.md
- Single commit `feat(stage-19.5J2.3): atlas bayesian inference engine`
- Push to origin

---

## 5. Risk + decisions

### Risk 1: API overlap with existing `analyze()`
- **Decision**: `analyze()` stays. `BayesianClaimEngine` is additive.
  Tests for both stay passing.

### Risk 2: StackPenalty enum duplication with sensitivity.py
- sensitivity.py has Stack enum too. Audit: do they conflict?
- **Decision**: separate `StackPenalty` enum to keep modules independent.
  No cross-import.

### Risk 3: Agency penalty logic in analyze() vs Bayesian
- analyze() applies 0.5 penalty for AGENCY without A/B. Bayesian does same.
- **Decision**: keep both. Document that analyze() is fast-path and
  Bayesian is the canonical inference.

### Risk 4: Subordination notice binding
- Every `BayesianAnalysis` should include SUBORDINATION_NOTICE
- **Decision**: include as default field, bound to analysis hash

### Risk 5: Backward compat — analyze() callers
- None should break. analyze() remains available.
- **Decision**: zero-touch on analyze() + service.py.

---

## 6. Honest disclosure

This is **discovery only**. NO source code has been written yet. Per
Thirstys standards + the established J2.1/J2.2 pattern, source code
requires explicit "go J2.3.0" authorization.

The full legacy code (498 LOC) has been analyzed. The port will be
~450 LOC (slight reduction by stripping legacy's `influence_agent_perception`
which is an agent-specific concern not relevant to the canonical atlas's
analytical-evidence-only mission).

---

## 7. Quality gates per sub-phase

Each sub-phase MUST end with all four canonical gates green via `uv run`:
- `uv run pytest`
- `uv run mypy packages/ --strict`
- `uv run ruff check packages/`
- `uv run ruff format --check packages/`

NO sub-phase will be left in a broken state. NO shortcuts. Per Thirstys
standards.
