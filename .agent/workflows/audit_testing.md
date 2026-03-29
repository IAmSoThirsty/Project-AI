# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-17 | TIME: 11:10               #
# SCOPE: SYSTEM-WIDE TESTING & VERIFICATION | COMPLIANCE: Sovereign Quality     #
# ============================================================================ #

# AUDIT: Sovereign Testing Workflow

## Mission
Ensure the absolute reliability and stability of the Project-AI monorepo.
Confirm test availability, execute comprehensive test suites, and preserve signed evidence of results.

## Authority
This workflow is enforced by the Triumvirate to guarantee production-grade maturity.
- **Galahad**: Verification of ethical guardrails and safety tests.
- **Cerberus**: Execution of adversarial and security boundary tests.
- **Codex Deus Maximus**: Validation of logical consistency and architectural invariants.

---

## Phase A: Test Inventory & Discovery

1. **Discovery**: Identify all test suites across the repository.
   - 🟢 `src/thirsty_lang/src/test/` (Interpreter Tests)
   - 🟢 `tests/` (Unit & Integration)
   - 🟢 `e2e/` (End-to-End Scenarios)
   - 🟢 `adversarial_tests/` (Security & Red Team)

2. **Compliance Check**: Ensure every test file has the Master-Tier header.

---

## Phase B: Test Execution

// turbo
1. **Core Substrate Tests**: Run unit tests for core Python logic.
```bash
pytest tests/unit --junitxml=test-artifacts/junit/core_unit_results.xml
```

// turbo
2. **Thirsty-Lang Tests**: Execute the interpreter test suite.
```bash
python src/thirsty_lang/src/thirsty_test_runner.py
```

// turbo
3. **E2E Integration**: Run full-stack integration scenarios.
```bash
pytest e2e/scenarios --junitxml=test-artifacts/junit/e2e_results.xml
```

---

## Phase C: Artifact Preservation & Categorization

// turbo
1. **Timestamped Archive**: Create a unique directory for the current test run.
```powershell
$timestamp = Get-Date -Format "yyyyMMdd_HHmm"
$test_id = (Get-ChildItem "test-artifacts/history" | Measure-Object).Count + 1
$target_dir = "test-artifacts/history/RUN_${timestamp}_T${test_id}"
mkdir $target_dir
move-item test-artifacts/junit/*.xml $target_dir
```

2. **Categorization**: Ensure logs are separated by domain (Security, Logic, Ethics).

---

## Phase D: Final Reporting

// turbo
1. **Generate Report**: Produce the final `VERIFICATION_REPORT.md`.
```bash
python tools/completion_tracker_agent.py --test-results test-artifacts/history/ --output governance/VERIFICATION_REPORT.md
```

STATUS: VERIFIED | QUALITY: MASTER-TIER
