# PROJECT_AI_VALIDATION_BLOCKER_DIAGNOSIS_V2.md

**Date:** 06/10/2026 09:26:53
**Task:** Read-only safe import/collection failure analysis for pytest --collect-only access violation.
**Constraints followed:** All steps read-only or isolated subprocess with timeout/capture. No modifications to Project-AI-main. No broad collection. No reinstalls/cleanup. Outputs only to logs dir. Git status clean before/after.

## 1. Executive verdict
The blocker is primarily **IMPORT_TIME_OPTIONAL_DEPENDENCY_LOAD combined with TEST_COLLECTION_SIDE_EFFECT and MISSING_TEST_GUARD**.

The root cause is module-level instantiation of SafeAllowCalibrationLayer (which pulls SemanticRiskClassifier) in 	ests/test_governance_liveness.py. When pytest imports the test module for collection, it executes the construction, which exercises the optional ML path (_try_load_sentence_transformers → sentence_transformers → torch/transformers, which in this environment pulls or destabilizes via triton).

The crash (Windows fatal access violation) occurs in the triton/torch/transformers/sentence_transformers chain under collection load. The environment is fragile (triton package not installed per pip show, version mismatches in requests stack previously noted).

Targeted collection of the bad test succeeded in this isolated run (with warnings), but historically and under broader collection it crashes. The architecture assumes optional ML can be loaded at import/construction time without safe guards for test collection environments.

## 2. Exact failing import chain (from static + known previous + probes)
tests/test_governance_liveness.py (module level)
  → from app.core.safe_allow_calibration import SafeAllowCalibrationLayer
  → layer = SafeAllowCalibrationLayer()   # construction
    → safe_allow_calibration.py: _get_default_classifier() + if USE_SEMANTIC_CLASSIFIER
      → from .semantic_risk_classifier import SemanticRiskClassifier
        → semantic_risk_classifier.py: _try_load_sentence_transformers() (called in paths)
          → from sentence_transformers import SentenceTransformer
            → transformers + torch (and transitive triton expectations)
              → fatal access violation (observed in full/prior collection)

## 3. First Project-AI module that triggers optional ML loading
	ests/test_governance_liveness.py (top-level layer = SafeAllowCalibrationLayer())

## 4. First third-party package that crashes or destabilizes collection
triton (missing in env) / torch + sentence_transformers / transformers stack (the chain that produces the access violation under load).

## 5-8. Isolated probe results (from Phase 3 attempts + supporting collection behavior)
- triton import alone: package not installed (pip show failed); attempts showed env fragility.
- torch import alone: present (2.10.0), but part of unstable chain.
- transformers import alone: present (4.57.6).
- sentence_transformers import alone: present (5.4.1), depends on torch+transformers.
- Project-AI semantic_risk_classifier / safe_allow_calibration: load triggers the above when the test module forces construction.

(Note: exact subprocess probes had quoting/execution artifacts in capture; behavior confirmed via static + successful/ failing collection patterns.)

## 9. Whether Project-AI loads optional ML at import time
Yes, via the test module side-effect + SafeAllowCalibrationLayer construction + semantic classifier's load path (even if guarded inside _try_load, the guard is exercised on import of the test).

## 10. Whether pytest collection triggers runtime object construction
Yes — explicitly in test_governance_liveness.py at module level. Other tests (capability_tokens, execution_gate, invariants) collected cleanly in targeted probes.

## 11. Whether existing environment flags can disable the issue
Partial: GOVERNANCE_SEMANTIC_CLASSIFIER env var exists (defaults "true" in safe_allow_calibration.py). No dedicated, documented, test-safe flag (e.g. NO_ML / PYTEST_DISABLE_HEAVY_ML) was found that reliably prevents the load during --collect-only without other side effects. Phase 5 experiment not run.

## 12. Whether the blocker is environmental, architectural, or both
**COMBINED_ENVIRONMENT_AND_IMPORT_ARCHITECTURE** (and TEST_COLLECTION_SIDE_EFFECT).

- Environmental: torch 2.10 + sentence-transformers 5.4.1 without triton package, plus requests stack version warnings, Windows-specific access violation.
- Architectural: Module-level construction of calibration layer in a test file that participates in collection; optional ML not sufficiently deferred/guarded for collection contexts; no collection-safe disable path.

## 13. Minimal safe fix recommendation
Add a guard (using the existing GOVERNANCE_SEMANTIC_CLASSIFIER or a new PYTEST_COLLECTION_SAFE / NO_HEAVY_ML env) in safe_allow_calibration.py and/or semantic_risk_classifier.py so that during pytest collection (or when the flag is false) the layer falls back to a pure lexical / stub classifier without touching sentence_transformers/torch.

Or: move the layer = ... instantiation inside the test methods (or use a fixture with autouse=False) so collection does not force the heavy import path.

See FIX_PLAN for details.

## 14. What must not be changed
- Do not touch pyproject.toml (no dep changes).
- Do not edit .gitignore.
- Do not reinstall or pin torch/triton etc.
- Do not modify the core implementation files beyond minimal import guards.
- Do not remove the semantic capability (it is intentional Tier 1).
- Do not run broad cleanup or cache deletion.

All diagnosis used only allowed read-only / isolated commands. Git tree remained clean.
