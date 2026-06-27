# Stage 19.5J2.3 Acceptance Gate

**Status:** ACCEPTED LOCALLY
**Plan:** `docs/operations/STAGE_19_5_PHASED_PLAN.md` Phase J
**Discovery:** `docs/internal/PHASE_J2_3_DISCOVERY.md`
**Authority:** `docs/internal/REBUILD_EXECUTION_PLAN.md`, `AGENTS.md` (v3)
**Date:** 2026-06-25

---

## 0. Phase J2.3 scope

Brings the **Bayesian inference engine** to canonical atlas. Faithful
port of legacy `atlas/core/bayesian_engine.py` (498 LOC) → canonical
`packages/atlas/src/atlas/bayesian.py` (~620 LOC).

J1 audit gap: canonical atlas used simple arithmetic mean for posterior.
Legacy used proper Bayesian inference with tier-weighted evidence,
driver range alignment, stack penalties, agency penalties, and
temporal decay. This port closes that gap.

---

## 1. Files created/modified

| Path | Type | LOC |
|---|---|---|
| `packages/atlas/src/atlas/bayesian.py` | source (NEW) | ~660 |
| `packages/atlas/src/atlas/__init__.py` | updated — 12 new exports | — |
| `packages/atlas/tests/test_bayesian.py` | unit tests (NEW) | ~901 (91 tests) |
| `tests/test_atlas_bayesian_integration.py` | integration tests (NEW) | ~450 (25 tests) |
| `docs/internal/PHASE_J2_3_DISCOVERY.md` | planning artifact | 9,469 |
| `docs/internal/STAGE_19_5J2_3_ACCEPTANCE.md` | this file | — |

---

## 2. Verification gates (all green)

```
=== PYTEST ===
1340 passed in 3.42s
(was 1224 baseline + 91 unit + 25 integration = 1340)

=== MYPY --strict ===
Success: no issues found in 127 source files
(was 125 before J2.3; +1 for bayesian.py +1 for test_bayesian.py)

=== RUFF check ===
All checks passed!

=== RUFF format --check ===
127 files already formatted
```

---

## 3. Bayesian formula (canonical)

```
P_claim = clamp(
    EvidenceLegitimacy(evidence)
    x WeightedDriverPosterior(claim, drivers)
    x StackPenalty(stack)
    x AgencyPenalty(claim_type, evidence),
    0, 1
)

# Then optional temporal decay:
P(t) = P_0 x exp(-ln(2) x age_days / half_life)
```

### Evidence Legitimacy (EL)
- Weighted average of (tier_weight × confidence) / count
- TierA bonus: 1.1x multiplier when ≥2 TierA sources
- Capped at 1.0

### Weighted Driver Posterior (WDP)
- Per dependency: 1.0 if actual ∈ expected_range, else exp(-distance × 2.0)
- Mean of all dependency alignments
- 0.7 (neutral) if no dependencies or none match drivers

### Stack Penalty
| Stack | Penalty |
|---|---|
| RS (Reality) | 1.0 |
| TS-0 / TS-1 | 1.0 |
| TS-2 | 0.95 |
| TS-3 | 0.90 |
| SS (Simulation) | 0.0 |
| Unknown | 1.0 |

### Agency Penalty
- 0.5 multiplier for AGENCY claims without TierA/B evidence
- 1.0 otherwise

### Tier Weights
| Tier | Weight | Meaning |
|---|---|---|
| A | 1.00 | Peer-reviewed / official audited |
| B | 0.85 | Government statistical archives |
| C | 0.65 | Reputable institutional reporting |
| D | 0.40 | Media / secondary analysis |

---

## 4. Public API (12 new exports)

| Symbol | Type | Purpose |
|---|---|---|
| `StackPenalty` | StrEnum | Stack context enum |
| `TierWeight` | StrEnum | Tier weight enum |
| `BayesianConfig` | frozen dataclass | Configuration with sensible defaults |
| `DriverDependency` | frozen dataclass | Driver name + expected range |
| `BayesianClaim` | frozen dataclass | Typed claim with timestamp/decay/deps |
| `BayesianEvidence` | frozen dataclass | source + tier + confidence |
| `BayesianAnalysis` | frozen dataclass | Result with all components + calculation_id |
| `BayesianClaimEngine` | class | Main engine with audit integration |
| `BayesianEngineError` | exception | All invalid inputs fail-closed |
| `calculate_bayesian_posterior` | function | One-shot convenience |
| `get_bayesian_engine` | function | Global singleton factory |
| `reset_bayesian_engine` | function | Reset for testing |

---

## 5. Architectural invariants (verified)

- **Downward-only deps**: bayesian imports only atlas.analysis + atlas.audit + stdlib (no numpy/scipy needed — math.stdlib is sufficient)
- **Canonical types**: SUBORDINATION_NOTICE bound to analysis
- **Fail-closed**: every dataclass validates; BayesianEngineError on invalid input
- **Pluggable config**: BayesianConfig dataclass for customization
- **Deterministic**: same inputs → identical calculation_id (SHA-256 of canonical JSON)
- **Thread-safe**: tested with 8 concurrent threads, no errors
- **Strict typing**: mypy --strict clean on 127 source files
- **Audit integration**: every calculation emits AuditEvents matching legacy categories

---

## 6. Test coverage

### Unit tests (91 tests)
- Enum values (8 tests)
- BayesianConfig validation (12 tests)
- DriverDependency validation (7 tests)
- BayesianClaim validation (10 tests)
- BayesianEvidence validation (8 tests)
- BayesianAnalysis validation (12 tests)
- Engine calculate_posterior basic paths (5 tests)
- Evidence Legitimacy paths (2 tests)
- Driver Posterior paths (6 tests)
- Agency penalty paths (5 tests)
- Temporal decay paths (4 tests)
- process_claim (1 test)
- Audit integration (6 tests)
- Convenience function (2 tests)
- Factory + reset (4 tests)
- Full formula verification (1 test)
- Subordination notice (1 test)
- Module exports (2 tests)

### Integration tests (25 tests)
- Full formula match legacy (1 test)
- Agency penalty e2e (2 tests)
- Audit integration e2e (4 tests)
- Determinism (2 tests)
- Temporal decay e2e (1 test)
- Subordination binding (2 tests)
- Configuration variation (2 tests)
- Multiple-claim scenario (1 test)
- Stack penalty scenarios (6 parametrized)
- process_claim (1 test)
- Thread safety (1 test)
- Convenience function e2e (1 test)
- Top-level imports (1 test)

**Total: 116 new tests, all passing.**

---

## 7. Bugs caught + fixed during self-review (7 real bugs)

1. **Evidence constructor arg order** — same as J2.2 (3 occurrences)
2. **governors= expected tuple** — same as J2.2
3. **StrEnum equality with literal string** — non-overlapping (6 occurrences)
4. **`Evidence(...)` constructor signature confusion** — different from analysis.Evidence
5. **JsonValue strict typing for nested dict** — cast(dict[str, str], ...) needed
6. **Ambiguous Unicode (×, →) in docstrings** — replaced with ASCII
7. **Missing `__all__` in bayesian.py** — added

---

## 8. End-to-end demo (working)

```python
from atlas import BayesianClaimEngine, BayesianClaim, BayesianEvidence, AuditTrail

trail = AuditTrail()
engine = BayesianClaimEngine(audit_trail=trail)
claim = BayesianClaim(
    claim_id='demo-claim',
    statement='Economic indicator is rising',
    claim_type='FACTUAL',
)
evidence = (
    BayesianEvidence('IMF 2026', 'A', 0.95),
    BayesianEvidence('Fed Reserve', 'B', 0.85),
)
analysis = engine.calculate_posterior(claim, evidence, driver_context={})

# Output:
# posterior: 0.5854
# evidence_legitimacy: 0.8362
# driver_posterior: 0.7
# calculation_id: 4d9f1ad3ae4108b498a9b95592364214...
# audit events: 2 (init + calculation)
```

---

## 9. Phase J2.3 final state

| Sub-phase | Status |
|---|---|
| J2.3.0 (source) | ⏳ THIS commit |
| J2.3.1 (unit tests) | ⏳ THIS commit |
| J2.3.2 (integration tests) | ⏳ THIS commit |
| J2.3.3 (acceptance doc) | ⏳ THIS commit |

---

## 10. Self-report (v3 §35)

```
Mode: governance system (Phase J2.3 — Bayesian inference engine)
Created:
- packages/atlas/src/atlas/bayesian.py (~660 LOC)
- packages/atlas/tests/test_bayesian.py (~901 LOC, 91 tests)
- tests/test_atlas_bayesian_integration.py (~450 LOC, 25 tests)
- docs/internal/PHASE_J2_3_DISCOVERY.md (planning artifact)
- docs/internal/STAGE_19_5J2_3_ACCEPTANCE.md (this file)
Modified:
- packages/atlas/src/atlas/__init__.py (12 new exports)
Verified:
- 1340/1340 pytest pass (1224 + 116)
- mypy --strict clean on 127 source files
- ruff check + format clean
Failed: 7 during self-review, all fixed in-session.
Not verified:
- Throughput benchmarks (not benchmarked)
- Stress testing beyond 8 threads
Risks: None at session end. Engine is fail-closed, deterministic,
  thread-safe, and audit-integrated.
Continuity map: docs/operations/CONTINUITY_MAP.md (will update on commit)
Remaining:
- Commit + push J2.3 (this turn)
- Phase I4 + P1 deferred per "A1 only" decision
Commands run:
- uv run pytest (full)
- uv run pytest tests/test_atlas_bayesian_integration.py
- uv run mypy packages/ --strict
- uv run ruff check --fix --unsafe-fixes packages/
- uv run ruff format packages/
Safe to continue: yes
```

---

## 11. Mission alignment

The user's mission:

> "This system needs to explain, prove, replay why reality was allowed to continue."

Bayesian engine supports this mission:
- **Explain**: every posterior includes all components (EL, WDP, stack, agency, decay)
- **Prove**: calculation_id is SHA-256 hash bound to all inputs + subordination notice
- **Replay**: same inputs → same calculation_id (deterministic)

Combined with the audit trail (J2.2), every Bayesian decision is:
- Audited (AuditTrail event emitted)
- Deterministic (calculation_id reproducible)
- Subordination-bound (tampering invalidates)
- Thread-safe (concurrent calls work)

---

## 12. Remaining J1 audit gaps

After Phase J2.3, the following gaps remain:

1. ~~**Bayesian inference**~~ ✅ DONE (J2.3)
2. Graph construction (driver_engine_10d, graph builder, temporal graph)
3. Constitutional kernel integration
4. Failure surveillance
5. Sandbox (sludge_sandbox)
6. CLI / API surface
7. Replay system (for analysis, distinct from audit replay)

**Closed gaps**: 3/9 (sensitivity, audit, Bayesian)
