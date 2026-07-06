# Stage 19 — Kernel + Governance + Execution Refactor Acceptance

> **Stage:** 19 (Kernel + Governance + Execution rebuild from legacy)
> **Standard:** Thirsty's Standard v3 (binding via `AGENTS.md`)
> **Mode:** governance system (rebuild)
> **Scope:** Wave 1 (kernel) + Wave 2 (governance triumvirate + iron path) + Wave 3 (execution risk + iron path extension)
> **Author:** Hermes Agent (assisted)
> **Date:** 2026-06-24
> **Plan executed:** `C:\Users\Quencher\.hermes\plans\2026-06-24_080000-project-ai-gap-discovery.md` (Phases A-G)
> **Source-of-truth:** `T:\00-Active\Project-AI-Beginnings\docs\internal\REBUILD_EXECUTION_PLAN.md`

---

## 1. Headline

**Refactored 5 legacy modules into 4 Beginnings-compliant modules,
plus introduced 3 new principal-architecture modules (Triumvirate,
Iron Path, RiskCalibrator Protocol). All 479 project tests pass, mypy
--strict clean, ruff clean, ruff format clean.**

The legacy code had the right *intent* (threat detection, TARL gate,
three-vote consensus, canonical action pipeline, risk calibration)
but the wrong *implementation*: side-channel logging, ad-hoc
severity scales, external imports of subsystems that don't exist in
Beginnings.

The refactored code conforms to Beginnings' existing constitutional
pattern: every action is an `ActionRequest`, every decision is a
`Decision(outcome, reasons, policy_version)`, every audit event lives
on the hash-chained `EventSpine`.

## 2. Module mapping (legacy → Beginnings)

| Legacy file | Refactored into | LOC delta | Notes |
|---|---|---|---|
| `kernel/threat_detection.py` (485 lines) | `packages/kernel/src/kernel/threat_detection.py` | +5 lines | Frozen dataclasses, `EventSpine` integration, pluggable predictor |
| `kernel/tarl_gate.py` (37 lines) + `kernel/tarl_codex_bridge.py` (17 lines) | `packages/kernel/src/kernel/tarl_bridge.py` | -10 lines | Merged, `TarlVerdictView` decouples from `tarl` package |
| `src/app/core/execution_gate.py` (387 lines) + `src/app/core/safe_allow_calibration.py` (310 lines) | `packages/execution/src/execution/risk.py` | -590 lines | Pure lexical classifier (no env-var lookups, no ML deps at runtime); pluggable `RiskClassifier` Protocol |
| (NEW — no legacy equivalent) | `packages/kernel/src/kernel/__init__.py` (+18 lines) | +18 lines | Re-exports public symbols |
| `governance/core.py` (25 lines, ad-hoc) | (already superseded) | — | Beginnings already had `GovernanceEngine` doing this properly |
| (NEW — derived from `triumvirate_server.py` 22KB ad-hoc) | `packages/governance/src/governance/triumvirate.py` | — | Three-vote consensus with 3 quorum rules |
| (NEW — derived from `iron_path_executor.py` 34KB + `pipeline.py` 54KB) | `packages/governance/src/governance/iron_path.py` | — | Canonical action pipeline with 5 stages |
| (NEW — `RiskCalibrator` Protocol) | `governance.iron_path.RiskCalibrator` | — | Decouples `governance` from `execution` (downward-only dep graph preserved) |

## 3. Architecture diagram (Wave 1 + 2 + 3)

```
┌─────────────────────────────────────────────────────────────────┐
│                  Iron Path (canonical pipeline)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ActionRequest                                                 │
│       │                                                          │
│       ├──> [1] ThreatDetectionEngine (kernel)                   │
│       │       │                                                  │
│       │       └── emits Event on EventSpine                     │
│       │              ↓                                          │
│       │       ThreatAssessment                                  │
│       │              │                                          │
│       │              └── .to_decision() ──> Decision (DENY/ESC)│
│       │                                                          │
│       ├──> [2] TarlGate (kernel)                                │
│       │       │                                                  │
│       │       └── emits Event on EventSpine                     │
│       │       └── TarlVerdictView (ALLOW/DENY/ESCALATE)         │
│       │                                                          │
│       ├──> [3] GovernanceEngine (existing)                      │
│       │       │                                                  │
│       │       ├── InvariantEngine (BLOCKING short-circuits)    │
│       │       │                                                  │
│       │       └── Governors ─> TriumvirateGovernor ─> Vote     │
│       │                                                          │
│       ├──> [4] SafeAllowCalibration (execution) [WAVE 3]        │
│       │       │                                                  │
│       │       └── RiskAssessment (BENIGN/AMBIGUOUS/HIGH_RISK)  │
│       │              │                                          │
│       │              └── can downgrade ALLOW → ESCALATE/DENY    │
│       │                                                          │
│       └──> [5] Executor (if ALLOW)                              │
│               │                                                  │
│               └── returns output captured on IronPathResult     │
│                                                                  │
│   IronPathResult { request, threats, tarl, governance,          │
│                    risk, final_decision, executor_output }      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 4. New modules — public API (waves 1+2+3)

### 4.1 `kernel.threat_detection`

```python
from kernel import (
    ThreatDetectionEngine, ThreatAssessment,
    AttackPatternLibrary, BehaviorAnalyzer, BehaviorPattern,
    HeuristicPredictor, RecommendedAction, ThreatCategory,
)

engine = ThreatDetectionEngine(spine)
assessment = engine.analyze(session_id="alice", command="sudo apt install x")
decision = assessment.to_decision(policy_version="v1")
```

**Severity → Outcome:** `INFO` → ALLOW, `WARNING` → ESCALATE, `BLOCKING+` → DENY.

### 4.2 `kernel.tarl_bridge`

```python
from kernel import TarlGate, TarlVerdictView, TarlEnforcementError

gate = TarlGate(spine, escalation_handler=my_handler)
gate.enforce(execution_context, verdict={"verdict": "DENY", "reason": "..."})
```

### 4.3 `execution.risk` (Wave 3)

```python
from execution import SafeAllowCalibration, LexicalRiskClassifier, RiskClass

cal = SafeAllowCalibration(spine, classifier=LexicalRiskClassifier())
assessment = cal.calibrate(action_request)
# assessment.risk_class ∈ {BENIGN, AMBIGUOUS, HIGH_RISK}
# assessment.risk_score ∈ [0.0, 1.0]
decision = assessment.to_decision(policy_version="v1")
```

**RiskClass → Outcome:** `BENIGN` → ALLOW, `AMBIGUOUS` → ESCALATE, `HIGH_RISK` → DENY.

### 4.4 `governance.triumvirate`

```python
from governance import TriumvirateGovernor, Quorum, RuleGovernor

tri = TriumvirateGovernor(
    name="triumvirate",
    governors=(safety_gov, policy_gov, capability_gov),
    quorum=Quorum.MAJORITY,
)
```

**Quorum:** UNANIMOUS / MAJORITY / SUPERMAJORITY. Any DENY vetoes.

### 4.5 `governance.iron_path` (now 5 stages)

```python
from governance import IronPath, RiskCalibrator

path = IronPath(
    spine=spine,
    governance=governance_engine,
    threat_engine=threat_engine,        # optional
    tarl_gate=tarl_gate,                # optional
    risk_calibrator=calibrator,         # optional (Protocol — no governance→execution import)
    executor=my_executor,               # optional (runs only when full ALLOW)
    policy_version=DEFAULT_POLICY_VERSION,
)
result = path.run(action_request, threat_session=..., threat_command=...)
assert result.allowed
assert result.executor_output  # captured output if executor ran
```

**Pipeline order:**
1. Optional `ThreatDetectionEngine.analyze` (emits event)
2. Optional `TarlGate.enforce` (emits event, may raise)
3. `GovernanceEngine.decide` (invariants → governors → triumvirate)
4. Optional `SafeAllowCalibration.calibrate` (downgrades ALLOW → ESC/DENY)
5. Optional `executor(request)` (only when EVERYTHING ALLOWs)

## 5. Architectural invariants preserved

- **Fail-closed:** all DENY paths veto regardless of any other condition.
- **Single audit chain:** all events go to one `EventSpine`, hash-chained, append-only.
- **Canonical types:** every module uses `ActionRequest`, `Decision`, `Outcome`, `InvariantSeverity`, `Event`, `EventSpine`.
- **Downward-only deps:** kernel → nothing; governance → kernel only; execution → kernel only; iron_path uses Protocol for risk_calibrator so it does NOT import execution.
- **Strict typing:** `mypy --strict` clean; `Any` banned except for the `risk_calibrator` parameter (where the Protocol indirection is intentional decoupling).
- **Deterministic:** every test uses fixed-time clocks; replays produce identical events.
- **Pluggable:** `HeuristicPredictor`, `EscalationHandler`, `RiskClassifier`, `Executor` are injection points.

## 6. Test coverage

| Module | Tests | Coverage focus |
|---|---|---|
| `test_threat_detection.py` | 17 | Pattern matching, behavioral analysis, severity mapping, predictor injection |
| `test_tarl_bridge.py` | 9 | Verdict validation, fail-closed on DENY/ESCALATE, escalation handler invocation |
| `test_risk.py` (Wave 3) | 17 | Lexical classifier scoring, signal detection, BENIGN/AMBIGUOUS/HIGH_RISK mapping, event recording, hash chain integrity |
| `test_triumvirate.py` | 13 | Quorum rules, DENY veto, fail-closed |
| `test_iron_path.py` | 14 | End-to-end pipeline, threat short-circuit, TARL propagation |
| `test_iron_path_integration.py` | 7 | Cross-package integration: Iron Path + Triumvirate + Kernel threat + TARL gate |
| `test_iron_path_risk.py` (Wave 3) | 10 | Risk calibration stage, executor stage, fail-closed propagation, full pipeline composition |

**Total: 87 new tests, all passing.**

## 7. Verification gate

```
=== TESTS ===
EXIT: 0
479 passed in 1.03s   (across 10 packages)

=== MYPY --strict ===
EXIT: 0
Success: no issues found in 32 source files

=== RUFF check ===
EXIT: 0
All checks passed!

=== RUFF format check ===
EXIT: 0
21 files already formatted
```

## 8. Per v3 §35 final report

```
Mode: governance system (rebuild)
Created:
  - T:\00-Active\Project-AI-Beginnings\packages\kernel\src\kernel\threat_detection.py
  - T:\00-Active\Project-AI-Beginnings\packages\kernel\src\kernel\tarl_bridge.py
  - T:\00-Active\Project-AI-Beginnings\packages\kernel\tests\test_threat_detection.py
  - T:\00-Active\Project-AI-Beginnings\packages\kernel\tests\test_tarl_bridge.py
  - T:\00-Active\Project-AI-Beginnings\packages\governance\src\governance\triumvirate.py
  - T:\00-Active\Project-AI-Beginnings\packages\governance\src\governance\iron_path.py
  - T:\00-Active\Project-AI-Beginnings\packages\governance\tests\test_triumvirate.py
  - T:\00-Active\Project-AI-Beginnings\packages\governance\tests\test_iron_path.py
  - T:\00-Active\Project-AI-Beginnings\packages\governance\tests\test_iron_path_integration.py
  - T:\00-Active\Project-AI-Beginnings\packages\governance\tests\test_iron_path_risk.py (Wave 3)
  - T:\00-Active\Project-AI-Beginnings\packages\execution\src\execution\risk.py (Wave 3)
  - T:\00-Active\Project-AI-Beginnings\packages\execution\tests\test_risk.py (Wave 3)
  - T:\00-Active\Project-AI-Beginnings\docs\operations\STAGE_19_ACCEPTANCE.md (this file)
Modified:
  - T:\00-Active\Project-AI-Beginnings\packages\kernel\src\kernel\__init__.py (re-export new symbols)
  - T:\00-Active\Project-AI-Beginnings\packages\governance\src\governance\__init__.py (re-export new symbols + RiskCalibrator Protocol)
  - T:\00-Active\Project-AI-Beginnings\packages\execution\src\execution\__init__.py (re-export risk module symbols)
  - T:\00-Active\Project-AI-Beginnings\packages\kernel\tests\test_tarl_bridge.py (mypy fixes)
Deleted: None.
Verified:
  - 479/479 project tests pass across 10 packages
  - 87 new tests pass (17 threat_detection + 9 tarl_bridge + 17 risk + 13 triumvirate + 14 iron_path + 7 integration + 10 iron_path_risk)
  - mypy --strict: clean on all 32 source files in scope
  - ruff check: clean
  - ruff format: clean
  - Architectural invariants: fail-closed, single audit chain, canonical types, downward-only deps, strict typing, deterministic, pluggable
  - Wave 3 architectural decision: governance → execution dependency AVOIDED via Protocol indirection
  - Real architectural bug caught: BLOCKING threat → ESCALATE fixed to → DENY (matches InvariantEngine convention)
Failed: None.
Not verified:
  - End-to-end runtime integration with packages/swr/, packages/api/, packages/atlas/ (next waves)
  - Real ML risk predictor implementation (pluggable seam exists; no concrete impl)
  - Real TARL runtime integration (pluggable seam exists; packages/tarl/ deferred)
  - Adversarial test catalog preservation
Risks:
  - Lexical classifier hardcoded patterns are a baseline; production needs domain-specific patterns
  - Default _default_heuristic for threats is acknowledged as a baseline, not policy
  - test_gate_records_context_keys_not_values asserts a security property that future refactors must preserve
Continuity map: docs/operations/CONTINUITY_MAP.md (updated by separate commit)
Remaining:
  - User to authorize commit
  - User to authorize next wave (recommend: packages/companion/ rebuild → packages/atlas/ rebuild → NEW packages/tarl/ → NEW packages/temporal/)
  - 8 open questions from LEGACY_GAP_INVENTORY.md §8 still pending user decisions
Commands run:
  - python -m pytest (multiple packages, full regression suite)
  - python -m mypy packages/kernel/ packages/governance/ packages/execution/ --strict
  - python -m ruff check (same scope)
  - python -m ruff format --check (same scope)
Safe to continue: yes (for user review of stage 19 + authorization to commit and proceed to next wave)
```

## 9. NEXT WAVE — recommended priority

1. **packages/companion/** rebuild — refactor `identity.py`, `nirl/*`, `fates.py`, `voice_bonding_protocol.py`. User-facing identity + bonding layer.
2. **packages/atlas/** rebuild — 17 subdirs, 102 Python files; large refactor.
3. **NEW packages/tarl/** — The TARL runtime + compiler + adapters from legacy `tarl/` (33 files, 21 py).
4. **NEW packages/temporal/** — From legacy `temporal/` (16 files, 8 py + `.thirsty` workflows).
5. **NEW packages/hydra_50/** — From legacy `engines/hydra_50/` + 7 `hydra_50_*.py` files.
