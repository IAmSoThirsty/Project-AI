# PROJECT_AI_VALIDATION_BLOCKER_FIX_RESULT.md

**Date:** 06/10/2026 13:15:28
**Fix implemented:** Minimal Option C per diagnosis/fix plan.
- Moved layer construction out of module scope in tests/test_governance_liveness.py (deferred inside classify_batch).
- Set GOVERNANCE_SEMANTIC_CLASSIFIER=false before import/construct in test context.
- Updated _get_default_classifier in safe_allow_calibration.py to always re-evaluate the current env var (ensures flag=false prevents SemanticRiskClassifier import/construction, robust even if module pre-imported).
- Production default (env unset or true) remains semantic-enabled.
- Fallback to lexical RiskClassifier is explicit.
- Only edited the two allowed files.
- No other restrictions violated.

## 1. Files changed
- T:\Project-AI-main\tests\test_governance_liveness.py
- T:\Project-AI-main\src\app\core\safe_allow_calibration.py

## 2. Exact diff summary
diff --git a/src/app/core/safe_allow_calibration.py b/src/app/core/safe_allow_calibration.py
index 435e288a..24e83068 100644
--- a/src/app/core/safe_allow_calibration.py
+++ b/src/app/core/safe_allow_calibration.py
@@ -35,2 +35,14 @@ def _get_default_classifier() -> "RiskClassifier":
-    """Return SemanticRiskClassifier if enabled, else fall back to lexical RiskClassifier."""
-    if USE_SEMANTIC_CLASSIFIER:
+    """Return SemanticRiskClassifier if enabled, else fall back to lexical RiskClassifier.
+
+    The check always re-reads the environment variable so that callers can set
+    GOVERNANCE_SEMANTIC_CLASSIFIER=false immediately before constructing
+    SafeAllowCalibrationLayer (or calling this) to avoid importing/constructing
+    SemanticRiskClassifier (and thus sentence_transformers/torch/transformers/triton)
+    during pytest collection or other light/test contexts.
+    Production default remains "true" (semantic enabled) when the var is unset.
+    """
+    use_semantic = (
+        os.getenv("GOVERNANCE_SEMANTIC_CLASSIFIER", "true").lower()
+        not in ("0", "false", "no")
+    )
+    if use_semantic:
diff --git a/tests/test_governance_liveness.py b/tests/test_governance_liveness.py
index a3019c35..89629a27 100644
--- a/tests/test_governance_liveness.py
+++ b/tests/test_governance_liveness.py
@@ -15 +14,0 @@ from app.core.governance_outcomes import GovernanceOutcome
-from app.core.safe_allow_calibration import SafeAllowCalibrationLayer
@@ -17 +16,6 @@ from app.core.safe_allow_calibration import SafeAllowCalibrationLayer
-layer = SafeAllowCalibrationLayer()
+# NOTE: SafeAllowCalibrationLayer construction is now inside classify_batch (after
+# setting GOVERNANCE_SEMANTIC_CLASSIFIER=false) so that pytest --collect-only does
+# not execute top-level code that would import/construct the (optional) semantic
+# classifier and pull in sentence_transformers/torch/transformers/triton.
+# This defers heavy optional ML loading until actual test execution.
+# Production default (when env not set or "true") remains semantic-enabled.
@@ -44,0 +49,7 @@ def classify_batch(prompts):
+    # Set to false in test context before importing/constructing the layer.
+    # This ensures that even if the safe_allow_calibration module is imported
+    # here, the flag causes it to skip SemanticRiskClassifier (no sentence_transformers etc.).
+    # Collection never reaches this code (only test execution does).
+    os.environ["GOVERNANCE_SEMANTIC_CLASSIFIER"] = "false"
+    from app.core.safe_allow_calibration import SafeAllowCalibrationLayer
+    layer = SafeAllowCalibrationLayer()


## 3. Whether collection now avoids module-level layer construction
Yes. Post-fix collects for all 4 tests (including the previously problematic test_governance_liveness.py) complete without executing top-level SafeAllowCalibrationLayer construction. The governance liveness test now collects in ~0.22s (previously took 17s+ in some runs and risked the ML chain). No heavy import during --collect-only because classify_batch (which does the from + construct + env set) is not executed during collection.

## 4. Whether GOVERNANCE_SEMANTIC_CLASSIFIER=false prevents heavy ML import
Yes. In the updated classify_batch (and via the re-eval in _get_default_classifier), setting the env to "false" before the import of safe_allow_calibration ensures the if-use-semantic branch (which does the from .semantic_risk_classifier) is skipped. The layer uses the pure lexical RiskClassifier fallback. This prevents sentence_transformers / torch / transformers / triton load in the test context.

## 5. Validation command results

**Pre-fix (as required, before any edits):**
git status --porcelain:
<empty - clean>

python -m pytest tests/test_governance_liveness.py --collect-only -q -p no:cacheprovider
[output showed collection of 3 items, but took 17.65s, with transformers FutureWarning, torchao deprecation warnings, requests warning]

(The other three collects succeeded quickly, as expected for lighter tests.)

**Post-fix collects (re-run for verification):**
git status --porcelain:
 M src/app/core/safe_allow_calibration.py
 M tests/test_governance_liveness.py

python -m pytest tests/test_governance_liveness.py --collect-only -q -p no:cacheprovider
... collected 3 items
========================= 3 tests collected in 0.22s =========================
(no ML-related warnings in this collect output for governance_liveness)

The other three collects: quick success, same as pre (0.19-0.28s), no issues.

**Post-fix actual test runs:**
python -m pytest tests/test_governance_liveness.py -q
... 3 passed in 0.24s

python -m pytest tests/test_capability_tokens.py tests/test_execution_gate_enforcement.py tests/test_invariants.py -q
... 15 passed in 10.03s
(some unrelated deprecation/FutureWarnings from other tests that do trigger safe layer with default=true)

All required tests pass.

## 6. Any failures
None. All collects and test runs passed cleanly. The previous access violation / long collection / heavy import during collection for governance_liveness is resolved by the scope move + flag usage.

(Note: git showed the expected modifications; some warnings from ML in other tests are pre-existing and unrelated to the collection blocker for the liveness test.)

## 7. Final git status
 M src/app/core/safe_allow_calibration.py
 M tests/test_governance_liveness.py
(Working tree has the minimal changes; clean otherwise. No commit performed per instructions.)

## 8. Whether the fix is ready to commit
Yes. The fix is minimal, targeted to the two allowed files, directly addresses the module-level side-effect and ensures the existing flag provides a collection-safe disable path for heavy ML deps while preserving production default (semantic enabled when env unset/true). Collection of the problematic test no longer triggers the layer construction or (with flag) the semantic import. Tests pass. Ready for owner review/commit.

All pre/post validation commands were executed as specified. No other files were edited.
