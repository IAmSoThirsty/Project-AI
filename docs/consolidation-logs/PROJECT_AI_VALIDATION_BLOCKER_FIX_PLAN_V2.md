# PROJECT_AI_VALIDATION_BLOCKER_FIX_PLAN_V2.md

**Classification:** COMBINED_ENVIRONMENT_AND_IMPORT_ARCHITECTURE (with strong TEST_COLLECTION_SIDE_EFFECT and MISSING_TEST_GUARD elements)

## 1. Classification
See DIAGNOSIS_V2.md for full details. Primary: import-time optional ML load triggered by test module side-effect during collection, exacerbated by missing triton + fragile torch/sentence_transformers stack in the current environment.

## 2. Minimal fix
Preferred (least invasive):
- In src/app/core/safe_allow_calibration.py: respect GOVERNANCE_SEMANTIC_CLASSIFIER (or add a secondary PYTEST_COLLECTION_SAFE=1 / NO_HEAVY_ML=1 check) and fall back to a lexical-only RiskClassifier (or stub) when the flag indicates "light mode" (e.g. during collection or CI light validation).
- Or (simpler for tests): move the top-level layer = SafeAllowCalibrationLayer() in 	ests/test_governance_liveness.py inside the test methods or behind a fixture that is not executed at collection time.

Alternative (if env issues persist):
- Document + use an existing or new env flag to skip Tier-1 semantic entirely for collection gates.
- Add a lightweight stub for SemanticRiskClassifier when heavy deps are unavailable or disabled.

Do not implement broad stubbing or change the production path.

## 3. Files likely involved (minimal surface)
- src/app/core/safe_allow_calibration.py (guard + fallback logic)
- tests/test_governance_liveness.py (move instantiation out of module level)
- (optionally) src/app/core/semantic_risk_classifier.py (make the load guard even earlier / more robust)

## 4. Files that must not be touched
- pyproject.toml (no dependency / pytest config changes)
- .gitignore
- Any core production logic beyond the import guard
- Other test files (do not broadly stub)
- No changes to torch/triton/transformers/sentence-transformers installation or pins

## 5. Test strategy after fix
- Re-run the exact 4 targeted collection probes from Phase 4 (with -p no:cacheprovider and faulthandler) and confirm exit 0 + no access violation + no heavy ML import in the failing test.
- Run the governance liveness test normally (it should still exercise semantic when the flag allows).
- Add a light "collection only" CI job that runs the targeted probes without heavy ML.
- Verify that setting the env flag (GOVERNANCE_SEMANTIC_CLASSIFIER=false or new equivalent) makes collection of the liveness test succeed without the ML stack.
- Confirm production behavior unchanged (semantic still active by default).

## 6. Rollback plan
- Revert the guard/fallback change or the test instantiation move.
- The original (crashing) behavior is restored; no data loss.
- Since the semantic path is optional (guarded), rollback is low risk.

## 7. Owner approval question
Does the owner want to:
A) Use/extend the existing GOVERNANCE_SEMANTIC_CLASSIFIER env var for collection safety (preferred, minimal new surface), or
B) Move the layer instantiation in test_governance_liveness.py to test-method scope (simplest, no new flags), or
C) Both + document the collection-safe flag for future gates?

Approval needed before any code change. This diagnosis + evidence + plan is the deliverable; no implementation performed.

All steps followed the hard restrictions. No fixes were implemented.
