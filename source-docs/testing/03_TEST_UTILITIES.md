# Test Utilities

**Module:** `tests/utils/`  
**Purpose:** Reusable test helpers, recorders, and validation tools  
**Components:** ScenarioRecorder, test generators, verification scripts  

---

## Directory Structure

```
tests/utils/
├── __init__.py
└── scenario_recorder.py

tests/
├── show_test_sample.py          # Display test structure
├── verify_test_uniqueness.py    # Validate test uniqueness
├── verify_security_agents.py    # Security validation
├── run_exhaustive_tests.py      # Comprehensive test runner
├── generate_1000_stress_tests.py
├── generate_2000_stress_tests.py
└── generate_owasp_tests.py
```

---

## ScenarioRecorder

**File:** `tests/utils/scenario_recorder.py`  
**Purpose:** Record Four Laws validation scenarios with full audit trail  

### Core Classes

#### ScenarioRecord (Dataclass)
```python
@dataclass(frozen=True)
class ScenarioRecord:
    suite: str                    # Test suite name
    scenario_id: str              # Unique scenario identifier
    action: str                   # Action being validated
    context: dict[str, Any]       # Context passed to Four Laws
    expected_allowed: bool        # Expected validation result
    allowed: bool                 # Actual validation result
    reason: str                   # Four Laws reason string
    passed: bool                  # Whether test passed
    ts_utc: str                   # UTC timestamp (ISO 8601)
```

#### ScenarioRecorder
```python
class ScenarioRecorder:
    def __init__(self, suite: str) -> None:
        self.suite = suite
        self.records: list[ScenarioRecord] = []
    
    def add(self, *, scenario_id, action, context, expected_allowed, 
            allowed, reason, passed) -> None:
        """Add scenario to recorder."""
    
    def flush_jsonl(self) -> Path:
        """Write all records to JSONL file."""
```

### Usage Example

```python
from tests.utils.scenario_recorder import ScenarioRecorder

def test_four_laws_scenarios():
    recorder = ScenarioRecorder(suite="four_laws_stress")
    
    # Test Law 1: Harm prevention
    action = "delete_system_file"
    context = {"endangers_humanity": True, "is_user_order": False}
    is_allowed, reason = FourLaws.validate_action(action, context)
    
    recorder.add(
        scenario_id="law1_harm_prevention",
        action=action,
        context=context,
        expected_allowed=False,
        allowed=is_allowed,
        reason=reason,
        passed=(is_allowed == False)
    )
    
    # Test Law 2: User obedience
    action = "clear_cache"
    context = {"is_user_order": True}
    is_allowed, reason = FourLaws.validate_action(action, context)
    
    recorder.add(
        scenario_id="law2_user_obedience",
        action=action,
        context=context,
        expected_allowed=True,
        allowed=is_allowed,
        reason=reason,
        passed=(is_allowed == True)
    )
    
    # Save all scenarios
    output_path = recorder.flush_jsonl()
    print(f"Scenarios saved to: {output_path}")
```

### Output Format (JSONL)

```jsonl
{"suite": "four_laws_stress", "scenario_id": "law1_harm_prevention", "action": "delete_system_file", "context": {"endangers_humanity": true, "is_user_order": false}, "expected_allowed": false, "allowed": false, "reason": "Action would endanger humanity - blocked by Law 1", "passed": true, "ts_utc": "2024-01-15T10:30:45.123456Z"}
{"suite": "four_laws_stress", "scenario_id": "law2_user_obedience", "action": "clear_cache", "context": {"is_user_order": true}, "expected_allowed": true, "allowed": true, "reason": "User-ordered action allowed by Law 2", "passed": true, "ts_utc": "2024-01-15T10:30:45.234567Z"}
```

### Artifact Location

Scenarios are saved to:
```
{PROJECT_AI_TEST_ARTIFACTS}/fourlaws-{suite}-{timestamp}.jsonl
```

Default location: `test-artifacts/fourlaws-four_laws_stress-20240115T103045Z.jsonl`

---

## Helper Functions

### utc_now_iso()
```python
def utc_now_iso() -> str:
    """Get current UTC timestamp in ISO 8601 format."""
    return datetime.now(UTC).isoformat()
```

**Returns:** `"2024-01-15T10:30:45.123456Z"`

### _artifact_dir()
```python
def _artifact_dir() -> Path:
    """Get artifact directory path, creating if necessary."""
    base = Path(os.environ.get("PROJECT_AI_TEST_ARTIFACTS", "test-artifacts"))
    base.mkdir(parents=True, exist_ok=True)
    return base
```

**Environment Variable:** `PROJECT_AI_TEST_ARTIFACTS`  
**Default:** `test-artifacts/`

---

## Test Sample Viewer

**File:** `tests/show_test_sample.py`  
**Purpose:** Display sample test structure and verify required fields  

### Usage
```bash
python tests/show_test_sample.py
```

### Output
```
======================================================================
STRESS TEST FIELDS VERIFICATION
======================================================================

📋 RED TEAM TEST SAMPLE:

{
  "id": "red_001",
  "name": "SQL Injection via Intent Parameter",
  "team": "red_team",
  "category": "injection",
  "subcategory": "sql",
  "severity": "critical",
  "description": "Attempt SQL injection...",
  "steps": [...],
  "expected_behavior": "Request denied",
  "exploited_weakness": "Input validation",
  "tarl_enforcement": "Input sanitization",
  "success_criteria": "No database access"
}

======================================================================

📋 BLACK TEAM TEST SAMPLE:
...

======================================================================

✅ FIELD VERIFICATION:

Checking RED TEAM test...
  ✓ description
  ✓ severity
  ✓ steps
  ✓ expected_behavior
  ✓ exploited_weakness
  ✓ tarl_enforcement
  ✓ success_criteria

🎯 SUMMARY:
  Total tests: 2000
  RED TEAM: 1000
  BLACK TEAM: 1000
  All required fields: PRESENT
```

### Required Fields
Every stress test must have:
- `description` - What the test does
- `severity` - critical/high/medium/low
- `steps` - Array of test steps
- `expected_behavior` - Expected system response
- `exploited_weakness` - Security weakness being tested
- `tarl_enforcement` - How TARL prevents this
- `success_criteria` - What constitutes test success

---

## Test Uniqueness Verifier

**File:** `tests/verify_test_uniqueness.py`  
**Purpose:** Ensure all stress tests are unique (no duplicates)  

### Usage
```bash
python tests/verify_test_uniqueness.py
```

### Validation Checks

1. **Unique Test IDs**
   - Checks for duplicate IDs
   - Reports any ID collisions

2. **Unique Test Names**
   - Validates all names are unique
   - Flags duplicate names

3. **Unique Scenarios**
   - MD5 hash of test steps
   - Detects identical step sequences

4. **Category Distribution**
   - Shows test coverage per category
   - Validates balanced distribution

5. **Severity Distribution**
   - Shows critical/high/medium/low breakdown
   - Ensures appropriate severity spread

### Output Example
```
======================================================================
UNIQUENESS VERIFICATION
======================================================================

1. TEST IDs:
   Total tests: 2000
   Unique IDs: 2000
   [OK] All IDs unique: True

2. TEST NAMES:
   Unique names: 2000
   ✅ All names unique: True

3. TEST SCENARIOS (by steps content):
   Unique scenarios: 2000
   ✅ All scenarios unique: True

4. CATEGORY DISTRIBUTION:

   RED TEAM (1000 tests):
     - injection-sql: 150
     - injection-xss: 120
     - auth-bypass: 180
     - path-traversal: 100
     ...

   BLACK TEAM (1000 tests):
     - fuzzing-inputs: 200
     - race-conditions: 150
     - resource-exhaustion: 180
     ...

5. SEVERITY DISTRIBUTION:
   - CRITICAL: 450 (22.5%)
   - HIGH: 650 (32.5%)
   - MEDIUM: 600 (30.0%)
   - LOW: 300 (15.0%)

======================================================================
VERIFICATION SUMMARY
======================================================================
✅ ALL 2000 TESTS ARE COMPLETELY UNIQUE
   - Unique IDs: ✅
   - Unique names: ✅
   - Unique scenarios: ✅
```

---

## Exhaustive Test Runner

**File:** `tests/run_exhaustive_tests.py`  
**Purpose:** Execute all 2315+ tests with comprehensive documentation  

### Class: ExhaustiveTestRunner

```python
class ExhaustiveTestRunner:
    def __init__(self, api_url: str = "http://localhost:8001"):
        self.api_url = api_url
        self.results = {
            "execution_start": datetime.now().isoformat(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "test_results": [],
            "detailed_reports": {},
        }
        self.report_dir = "test_execution_reports"
```

### Methods

#### execute_single_test(test: dict) -> dict
```python
def execute_single_test(self, test: dict) -> dict:
    """Execute a single test with full documentation.
    
    Returns:
        {
            "test_id": "red_001",
            "test_name": "SQL Injection Test",
            "category": "injection",
            "severity": "critical",
            "execution_start": "2024-01-15T10:30:00Z",
            "steps_executed": [...],
            "status": "PASSED",
            "errors": [],
            "warnings": [],
            "execution_time_ms": 123.45
        }
    """
```

#### _execute_step(step: dict, test_id: str) -> dict
```python
def _execute_step(self, step: dict, test_id: str) -> dict:
    """Execute a single test step.
    
    Returns:
        {
            "step": 1,
            "action": "POST /api/intent",
            "payload": {...},
            "expected": "Request denied",
            "actual": {
                "status_code": 403,
                "response": "...",
                "headers": {...}
            },
            "passed": True,
            "execution_time_ms": 45.2,
            "timestamp": "2024-01-15T10:30:01Z"
        }
    """
```

#### _validate_response(response, expected: str, rationale: str) -> bool
```python
def _validate_response(self, response, expected: str, rationale: str) -> bool:
    """Validate if response matches expected behavior."""
    if "denied" in expected.lower() or "blocked" in expected.lower():
        return response.status_code in [403, 401, 400]
    elif "allowed" in expected.lower():
        return response.status_code in [200, 201]
    return True  # Default: any response acceptable
```

#### _generate_test_report(test: dict, result: dict)
```python
def _generate_test_report(self, test: dict, result: dict):
    """Generate comprehensive Markdown report for single test."""
```

### Usage

```bash
# Run all tests
python tests/run_exhaustive_tests.py

# Output directory
ls test_execution_reports/
# EXECUTION_SUMMARY.md
# execution_results.json
# red_001.md
# red_002.md
# ...
# black_1000.md
```

### Generated Reports

#### Individual Test Report (Markdown)
```markdown
# Test Execution Report: red_001

## Test Information
| Field | Value |
|-------|-------|
| **Test ID** | red_001 |
| **Test Name** | SQL Injection via Intent Parameter |
| **Category** | injection |
| **Severity** | CRITICAL |
| **Status** | **PASSED** |
| **Execution Time** | 123.45 ms |

## Test Description
Attempt SQL injection through intent parameter...

## Security Details
### Exploited Weakness
Lack of input sanitization...

### Expected Behavior
Request denied with 403 status...

### TARL Enforcement Mechanism
Input validation middleware...

## Test Execution Steps
### Step 1: ✅ PASS
**Action:** `POST /api/intent`
**Payload:**
```json
{
  "intent": "'; DROP TABLE users; --"
}
```
**Expected Result:** Request denied
**Actual Result:**
```
Status Code: 403
Response: {"error": "Invalid input detected"}
```
**Validation:** PASSED
```

#### Summary Report (JSON)
```json
{
  "execution_start": "2024-01-15T10:30:00Z",
  "execution_end": "2024-01-15T11:45:00Z",
  "total_tests": 2315,
  "passed": 2300,
  "failed": 15,
  "skipped": 0,
  "test_results": [
    {
      "test_id": "red_001",
      "status": "PASSED",
      "execution_time_ms": 123.45
    },
    ...
  ]
}
```

---

## Test Generators

### Generate 1000 Stress Tests
**File:** `tests/generate_1000_stress_tests.py`  
**Purpose:** Generate 1000 Four Laws stress test scenarios

### Generate 2000 Stress Tests
**File:** `tests/generate_2000_stress_tests.py`  
**Purpose:** Generate 2000 adversarial stress tests (red + black team)

**Output:** `adversarial_stress_tests_2000.json`

**Structure:**
```json
{
  "red_team_tests": [
    {
      "id": "red_001",
      "name": "Test Name",
      "team": "red_team",
      "category": "injection",
      "subcategory": "sql",
      "severity": "critical",
      "description": "...",
      "steps": [...],
      "expected_behavior": "...",
      "exploited_weakness": "...",
      "tarl_enforcement": "...",
      "success_criteria": "..."
    }
  ],
  "black_team_tests": [...]
}
```

### Generate OWASP Tests
**File:** `tests/generate_owasp_tests.py`  
**Purpose:** Generate OWASP Top 10 compliance tests

**Output:** `owasp_compliant_tests.json`

**Categories:**
- A01:2021 – Broken Access Control
- A02:2021 – Cryptographic Failures
- A03:2021 – Injection
- A04:2021 – Insecure Design
- A05:2021 – Security Misconfiguration
- A06:2021 – Vulnerable and Outdated Components
- A07:2021 – Identification and Authentication Failures
- A08:2021 – Software and Data Integrity Failures
- A09:2021 – Security Logging and Monitoring Failures
- A10:2021 – Server-Side Request Forgery (SSRF)

---

## Common Patterns

### Pattern 1: Scenario Recording
```python
def test_four_laws_with_recording():
    recorder = ScenarioRecorder(suite="my_test_suite")
    
    for scenario in test_scenarios:
        is_allowed, reason = FourLaws.validate_action(
            scenario["action"],
            context=scenario["context"]
        )
        
        recorder.add(
            scenario_id=scenario["id"],
            action=scenario["action"],
            context=scenario["context"],
            expected_allowed=scenario["expected"],
            allowed=is_allowed,
            reason=reason,
            passed=(is_allowed == scenario["expected"])
        )
    
    output_path = recorder.flush_jsonl()
    assert output_path.exists()
```

### Pattern 2: Test Generation
```python
def generate_test_suite():
    tests = []
    
    for category in categories:
        for severity in ["critical", "high", "medium", "low"]:
            test = {
                "id": f"{category}_{severity}_{len(tests):03d}",
                "name": f"{category.title()} {severity.title()} Test",
                "category": category,
                "severity": severity,
                "description": f"Test {category} with {severity} severity",
                "steps": generate_steps(category, severity),
                "expected_behavior": "Request denied",
                "exploited_weakness": f"{category} vulnerability",
                "tarl_enforcement": f"{category} protection",
                "success_criteria": "No unauthorized access"
            }
            tests.append(test)
    
    return tests
```

### Pattern 3: Exhaustive Validation
```python
def validate_all_tests(test_file: str):
    with open(test_file) as f:
        data = json.load(f)
    
    all_tests = data.get("red_team_tests", []) + data.get("black_team_tests", [])
    
    required_fields = [
        "description", "severity", "steps", "expected_behavior",
        "exploited_weakness", "tarl_enforcement", "success_criteria"
    ]
    
    for test in all_tests:
        for field in required_fields:
            assert field in test, f"Missing {field} in {test.get('id', 'UNKNOWN')}"
```

---

## Best Practices

### ✅ DO
- Use `ScenarioRecorder` for Four Laws tests
- Generate test reports in Markdown for readability
- Validate test uniqueness before committing
- Use JSONL for append-friendly scenario logging
- Include timestamps in UTC (ISO 8601 format)
- Use descriptive scenario IDs: `law1_harm_prevention`

### ❌ DON'T
- Write scenario files to source tree (use test-artifacts/)
- Hardcode artifact paths (use `PROJECT_AI_TEST_ARTIFACTS` env var)
- Generate duplicate test IDs
- Skip field validation in generated tests
- Use local timezone for timestamps

---

## Next Steps

1. Read `04_FIXTURE_REFERENCE.md` for pytest fixtures
2. See `05_CORE_SYSTEM_TESTS.md` for testing patterns
3. Check `07_STRESS_TESTING.md` for stress test documentation

---

**See Also:**
- `tests/utils/scenario_recorder.py` - Source code
- `tests/run_exhaustive_tests.py` - Comprehensive test runner
- `01_TEST_FRAMEWORK_OVERVIEW.md` - Testing architecture
