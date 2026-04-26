# Stress Testing

**Purpose:** Comprehensive stress testing strategies for Four Laws and system limits  
**Modules:** 15+ stress test files  
**Coverage:** 2000+ adversarial scenarios, property-based testing, hypothesis-driven fuzzing  

---

## Overview

Project-AI employs multi-layered stress testing to validate system resilience:

1. **Deterministic Stress Tests** - Predefined scenarios with known outcomes
2. **Property-Based Testing** - Generative testing with Hypothesis
3. **Adversarial Testing** - Red team + black team attack scenarios
4. **OWASP Compliance** - Security standard validation
5. **Load/Chaos/Soak Testing** - TARL orchestration resilience

---

## Four Laws Stress Testing

### test_four_laws_stress.py

General stress test scenarios for Four Laws validation.

**Coverage:**
- Boundary conditions
- Conflicting context flags
- Edge cases in action descriptions
- Performance under rapid validation requests

**Pattern:**
```python
def test_four_laws_rapid_validation():
    """Test Four Laws under rapid validation requests."""
    actions = [f"action_{i}" for i in range(1000)]
    
    for action in actions:
        is_allowed, reason = FourLaws.validate_action(
            action,
            context={"is_user_order": True}
        )
        assert isinstance(is_allowed, bool)
        assert len(reason) > 0
```

### test_four_laws_scenarios.py

Real-world scenario testing.

**Scenarios:**
- User requests system file deletion
- AI suggests harmful action
- Conflicting laws (Law 1 vs Law 2)
- Self-preservation conflicts
- Efficiency optimization decisions

**Example:**
```python
def test_scenario_user_orders_harmful_action():
    """Law 1 overrides Law 2: harmful action blocked even with user order."""
    is_allowed, reason = FourLaws.validate_action(
        "delete_user_data",
        context={
            "endangers_humanity": True,
            "is_user_order": True,  # Law 2 says allow
        }
    )
    # Law 1 (humanity first) overrides Law 2 (user obedience)
    assert not is_allowed
    assert "Law 1" in reason or "humanity" in reason.lower()
```

### test_four_laws_dual_flag_scenarios.py

Conflicting context flags to test law hierarchy.

**Test Matrix:**
```python
test_cases = [
    # (endangers_humanity, is_user_order, expected_allowed)
    (True, False, False),   # Law 1 blocks
    (True, True, False),    # Law 1 overrides Law 2
    (False, True, True),    # Law 2 allows
    (False, False, True),   # Default allow (unless other flags)
]
```

### test_four_laws_1000_deterministic.py

1000 deterministic test scenarios.

**Categories:**
- Law 1 violations (200 tests)
- Law 2 compliance (250 tests)
- Law 3 self-preservation (200 tests)
- Law 4 efficiency (200 tests)
- Multi-law interactions (150 tests)

**Pattern:**
```python
def generate_deterministic_scenarios():
    """Generate 1000 deterministic Four Laws scenarios."""
    scenarios = []
    
    # Law 1: Harm prevention (200 scenarios)
    for i in range(200):
        scenarios.append({
            "id": f"law1_det_{i:03d}",
            "action": f"harmful_action_{i}",
            "context": {"endangers_humanity": True},
            "expected": False,
            "reason_contains": "Law 1"
        })
    
    # Law 2: User obedience (250 scenarios)
    for i in range(250):
        scenarios.append({
            "id": f"law2_det_{i:03d}",
            "action": f"user_requested_action_{i}",
            "context": {"is_user_order": True},
            "expected": True,
            "reason_contains": "Law 2"
        })
    
    # ... Law 3, Law 4, multi-law scenarios
    
    return scenarios

def test_deterministic_scenarios():
    """Execute all 1000 deterministic scenarios."""
    scenarios = generate_deterministic_scenarios()
    recorder = ScenarioRecorder(suite="deterministic_1000")
    
    for scenario in scenarios:
        is_allowed, reason = FourLaws.validate_action(
            scenario["action"],
            context=scenario["context"]
        )
        
        passed = (is_allowed == scenario["expected"] and 
                  scenario["reason_contains"] in reason)
        
        recorder.add(
            scenario_id=scenario["id"],
            action=scenario["action"],
            context=scenario["context"],
            expected_allowed=scenario["expected"],
            allowed=is_allowed,
            reason=reason,
            passed=passed
        )
    
    output_path = recorder.flush_jsonl()
    assert output_path.exists()
```

### test_four_laws_1000_property_based.py

Property-based testing with Hypothesis.

**Properties Tested:**
1. **Type Safety** - Always returns (bool, str)
2. **Non-Empty Reason** - Reason string is never empty
3. **Law Hierarchy** - Law 1 always overrides Law 2
4. **Determinism** - Same input always produces same output
5. **Context Handling** - Unknown context keys don't cause errors

**Pattern:**
```python
from hypothesis import given, strategies as st

@given(
    action=st.text(min_size=1, max_size=100),
    endangers_humanity=st.booleans(),
    is_user_order=st.booleans(),
    threatens_self=st.booleans(),
    improves_efficiency=st.booleans()
)
def test_four_laws_type_safety(action, endangers_humanity, is_user_order, 
                                threatens_self, improves_efficiency):
    """Property: validate_action always returns (bool, str)."""
    context = {
        "endangers_humanity": endangers_humanity,
        "is_user_order": is_user_order,
        "threatens_self": threatens_self,
        "improves_efficiency": improves_efficiency,
    }
    
    is_allowed, reason = FourLaws.validate_action(action, context)
    
    # Type safety properties
    assert isinstance(is_allowed, bool)
    assert isinstance(reason, str)
    assert len(reason) > 0
    
    # Law hierarchy property
    if endangers_humanity:
        assert not is_allowed, "Law 1 must block harmful actions"

@given(
    action=st.text(min_size=1),
    context=st.dictionaries(
        keys=st.sampled_from([
            "endangers_humanity", "is_user_order", 
            "threatens_self", "improves_efficiency"
        ]),
        values=st.booleans()
    )
)
def test_four_laws_determinism(action, context):
    """Property: Same input produces same output."""
    result1 = FourLaws.validate_action(action, context)
    result2 = FourLaws.validate_action(action, context)
    
    assert result1 == result2, "Validation must be deterministic"
```

### test_four_laws_1000_hypothesis_threats.py

Hypothesis-driven threat generation.

**Threat Categories:**
- SQL injection attempts
- XSS payloads
- Path traversal
- Command injection
- Buffer overflow patterns
- Null byte injection
- Unicode exploits

**Pattern:**
```python
@given(
    injection_type=st.sampled_from([
        "sql", "xss", "path_traversal", "command_injection"
    ]),
    payload=st.text(min_size=5)
)
def test_injection_attempt_blocked(injection_type, payload):
    """Hypothesis: All injection attempts should be detected."""
    action = f"process_input_{payload}"
    
    # Add threat indicators to context
    context = {
        "contains_injection": True,
        "injection_type": injection_type,
    }
    
    is_allowed, reason = FourLaws.validate_action(action, context)
    
    # Should be blocked or heavily scrutinized
    if "suspicious" in payload.lower():
        assert not is_allowed or "caution" in reason.lower()
```

### test_four_laws_1000_disallowed_high_level.py

High-level disallowed action patterns.

**Disallowed Categories:**
- System file manipulation
- Credential theft
- Privacy violations
- Unauthorized access
- Data exfiltration
- Service disruption

### test_four_laws_1000_redacted_procedural_attempts.py

Procedural attack vector generation.

**Procedures:**
1. Reconnaissance
2. Privilege escalation
3. Lateral movement
4. Data exfiltration
5. Persistence establishment
6. Cover tracks

---

## Adversarial Stress Testing

### Adversarial Test Generation

**File:** `tests/generate_2000_stress_tests.py`  
**Output:** `adversarial_stress_tests_2000.json`

**Structure:**
```json
{
  "red_team_tests": [1000 tests],
  "black_team_tests": [1000 tests]
}
```

### Red Team Tests (1000 tests)

**Purpose:** Offensive security testing - attempt to breach system

**Categories:**
- **Injection** (270 tests)
  - SQL injection (150)
  - XSS (120)
- **Authentication** (180 tests)
  - Bypass attempts
  - Credential stuffing
  - Session hijacking
- **Authorization** (150 tests)
  - Privilege escalation
  - Path traversal
  - IDOR (Insecure Direct Object Reference)
- **Input Validation** (200 tests)
  - Buffer overflow
  - Integer overflow
  - Format string attacks
- **Logic Flaws** (100 tests)
  - Race conditions
  - Business logic bypass
- **Cryptography** (100 tests)
  - Weak algorithms
  - Key management flaws

**Test Structure:**
```json
{
  "id": "red_001",
  "name": "SQL Injection via Intent Parameter",
  "team": "red_team",
  "category": "injection",
  "subcategory": "sql",
  "severity": "critical",
  "description": "Attempt SQL injection through intent parameter to extract database contents",
  "steps": [
    {
      "step": 1,
      "action": "POST /api/intent",
      "payload": {
        "intent": "'; DROP TABLE users; --"
      },
      "expected": "Request denied with 403",
      "rationale": "Input validation should block SQL injection patterns"
    }
  ],
  "expected_behavior": "Request denied, input sanitized, audit logged",
  "exploited_weakness": "Lack of input sanitization",
  "tarl_enforcement": "Input validation middleware blocks malicious patterns",
  "success_criteria": "No database access, malicious query logged"
}
```

### Black Team Tests (1000 tests)

**Purpose:** Defensive validation - ensure security controls work

**Categories:**
- **Fuzzing** (200 tests)
  - Random input generation
  - Boundary value testing
  - Mutation testing
- **Resource Exhaustion** (180 tests)
  - CPU exhaustion
  - Memory exhaustion
  - Connection pool exhaustion
- **State Management** (150 tests)
  - Race conditions
  - Concurrent access
  - Deadlock scenarios
- **Error Handling** (170 tests)
  - Exception injection
  - Error message leakage
  - Fail-open vs fail-closed
- **Compliance** (150 tests)
  - OWASP Top 10
  - CWE Top 25
  - MITRE ATT&CK
- **Monitoring** (150 tests)
  - Audit log completeness
  - Anomaly detection
  - Alert generation

---

## OWASP Compliance Testing

### Generate OWASP Tests

**File:** `tests/generate_owasp_tests.py`  
**Output:** `owasp_compliant_tests.json`

**OWASP Top 10 (2021) Coverage:**

#### A01:2021 – Broken Access Control (35 tests)
- Vertical privilege escalation
- Horizontal privilege escalation
- IDOR vulnerabilities
- Directory traversal
- CORS misconfigurations

#### A02:2021 – Cryptographic Failures (30 tests)
- Weak encryption algorithms
- Exposed sensitive data
- Insufficient transport layer security
- Hardcoded credentials

#### A03:2021 – Injection (40 tests)
- SQL injection
- NoSQL injection
- OS command injection
- LDAP injection
- XPath injection

#### A04:2021 – Insecure Design (25 tests)
- Missing rate limiting
- Insufficient authentication
- Business logic flaws

#### A05:2021 – Security Misconfiguration (30 tests)
- Default credentials
- Unnecessary features enabled
- Verbose error messages
- Missing security headers

#### A06:2021 – Vulnerable Components (20 tests)
- Known vulnerabilities
- Outdated dependencies
- Unpatched systems

#### A07:2021 – Authentication Failures (35 tests)
- Credential stuffing
- Brute force attacks
- Weak password policies
- Session fixation

#### A08:2021 – Software/Data Integrity Failures (25 tests)
- Unsigned updates
- Insecure deserialization
- CI/CD pipeline attacks

#### A09:2021 – Logging/Monitoring Failures (30 tests)
- Missing audit logs
- Insufficient monitoring
- Alert fatigue
- Log injection

#### A10:2021 – Server-Side Request Forgery (30 tests)
- Internal port scanning
- Cloud metadata access
- Bypass whitelisting

**Test Structure:**
```json
{
  "id": "owasp_a01_001",
  "name": "Vertical Privilege Escalation via Role Parameter",
  "owasp_category": "A01:2021",
  "owasp_reference": "Broken Access Control",
  "severity": "critical",
  "cwe_id": "CWE-269",
  "description": "Attempt to escalate privileges by modifying role parameter",
  "steps": [
    {
      "step": 1,
      "action": "POST /api/user/update",
      "payload": {
        "user_id": "123",
        "role": "admin"
      },
      "expected": "403 Forbidden",
      "rationale": "Non-admin users should not be able to grant themselves admin role"
    }
  ],
  "tarl_enforcement": "Authorization middleware validates role changes against current user privileges",
  "success_criteria": "Request denied, audit logged, alert generated"
}
```

---

## TARL Load/Chaos/Soak Testing

### test_tarl_load_chaos_soak.py

Resilience testing for TARL orchestration system.

#### Load Testing
```python
def test_tarl_load_1000_concurrent_requests():
    """Test TARL under 1000 concurrent requests."""
    tarl = TARLOrchestrator()
    
    def make_request():
        return tarl.process_action("test_action", context={})
    
    with ThreadPoolExecutor(max_workers=100) as executor:
        futures = [executor.submit(make_request) for _ in range(1000)]
        results = [f.result() for f in futures]
    
    # Verify all requests processed
    assert len(results) == 1000
    assert all(r["status"] in ["allowed", "denied"] for r in results)
```

#### Chaos Testing
```python
def test_tarl_chaos_random_failures():
    """Test TARL resilience to random component failures."""
    tarl = TARLOrchestrator()
    
    # Inject random failures
    with patch('app.agents.oversight.OversightAgent.validate') as mock:
        # 30% failure rate
        mock.side_effect = lambda x: (
            (True, "OK") if random.random() > 0.3 
            else Exception("Simulated failure")
        )
        
        # Process 100 requests
        results = []
        for i in range(100):
            try:
                result = tarl.process_action(f"action_{i}", {})
                results.append(result)
            except Exception:
                pass  # Graceful degradation
        
        # Should handle failures gracefully
        assert len(results) >= 50  # At least 50% success rate
```

#### Soak Testing
```python
def test_tarl_soak_24_hour_simulation():
    """Simulate 24 hours of continuous operation."""
    tarl = TARLOrchestrator()
    start_time = time.time()
    duration = 60  # 60 seconds simulates 24 hours in test
    
    requests_processed = 0
    errors = []
    
    while time.time() - start_time < duration:
        try:
            result = tarl.process_action(f"action_{requests_processed}", {})
            requests_processed += 1
        except Exception as e:
            errors.append(str(e))
        
        time.sleep(0.01)  # 10ms between requests
    
    # Verify stability
    assert requests_processed > 1000
    assert len(errors) / requests_processed < 0.01  # < 1% error rate
```

---

## Scenario Recording

All stress tests use `ScenarioRecorder` for audit trails:

```python
from tests.utils.scenario_recorder import ScenarioRecorder

def test_stress_with_recording():
    recorder = ScenarioRecorder(suite="stress_test")
    
    for scenario in scenarios:
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
    print(f"Scenarios saved to: {output_path}")
```

**Output:** `test-artifacts/fourlaws-stress_test-20240115T103045Z.jsonl`

---

## Execution

### Run All Stress Tests
```bash
pytest tests/test_four_laws_stress.py -v
pytest tests/test_four_laws_1000_*.py -v
```

### Run Adversarial Tests
```bash
python tests/run_exhaustive_tests.py
```

### Generate Test Suites
```bash
python tests/generate_2000_stress_tests.py
python tests/generate_owasp_tests.py
```

### Verify Uniqueness
```bash
python tests/verify_test_uniqueness.py
```

---

## Best Practices

### ✅ DO
- Use `ScenarioRecorder` for audit trails
- Generate diverse test scenarios
- Test both success and failure paths
- Include OWASP/CWE references
- Use property-based testing for edge cases
- Record execution times

### ❌ DON'T
- Hardcode expected outcomes without rationale
- Skip scenario validation
- Generate duplicate test IDs
- Ignore performance degradation
- Skip documentation of test purpose

---

## Next Steps

1. Read `08_SECURITY_TESTING.md` for security-focused strategies
2. See `09_INTEGRATION_TESTING.md` for integration patterns
3. Check `10_E2E_TESTING.md` for end-to-end test workflows

---

**See Also:**
- `tests/test_four_laws_stress.py` - Stress test implementation
- `tests/utils/scenario_recorder.py` - Scenario recording utility
- `tests/run_exhaustive_tests.py` - Exhaustive test runner
