---
description: "Testing protocol for governance compliance: deny behavior, audit trails, invariants, evidence bundles."
applyTo: "tests/**"
tags: [testing, governance, audit, evidence, compliance]
created: 2026-05-13
status: mandatory
---

# Governance Testing Protocol

All tests must validate governance behavior, not just functionality.

## Core Testing Principles

### 1. Test the Denial Path
Every governed action must have tests that verify **denial** works correctly.

```python
def test_action_respects_denial():
    """Verify action stops when governance denies."""
    gate = ExecutionGate()
    
    approved, result = gate.execute(
        domain="test.domain",
        action="forbidden_action",
        context={"trigger_denial": True},
        executor_fn=lambda ctx: {"should_not_execute": True},
    )
    
    assert not approved
    assert "should_not_execute" not in str(result)
```

### 2. Test Audit Trail Generation
Every action must generate audit evidence.

```python
def test_action_generates_audit(tmp_path):
    """Verify action creates evidence bundle."""
    import os
    os.environ["EVIDENCE_DIR"] = str(tmp_path)
    
    gate = ExecutionGate()
    gate.execute(
        domain="test.domain",
        action="test_action",
        context={"session_id": "test-123"},
        executor_fn=lambda ctx: {"result": "data"},
    )
    
    evidence_files = list(tmp_path.glob("test-123-*.json"))
    assert len(evidence_files) > 0
    
    # Validate evidence structure
    import json
    with open(evidence_files[0]) as f:
        evidence = json.load(f)
    
    assert "request_hash" in evidence
    assert "outcome" in evidence
    assert evidence["domain"] == "test.domain"
    assert evidence["action"] == "test_action"
```

### 3. Test Invariant Compliance
Actions must not violate system invariants.

```python
def test_action_respects_invariants():
    """Verify action validates invariants before execution."""
    from app.core.invariant_engine import InvariantEngine
    
    engine = InvariantEngine()
    
    # Test action that would violate invariant
    violations = engine.validate_all({
        "action": "escalate_without_severity",
        "domain": "governance",
        "state": {},
    })
    
    assert len(violations) > 0
    assert "severity_required" in str(violations)
```

### 4. Test Fail-Closed Behavior
Governance failures must prevent execution, not fall through.

```python
def test_governance_failure_blocks_execution():
    """Verify execution stops on governance system failure."""
    gate = ExecutionGate()
    
    # Simulate governance system failure
    original_kernel = gate.kernel
    gate.kernel = None
    
    approved, result = gate.execute(
        domain="test.domain",
        action="test_action",
        context={},
        executor_fn=lambda ctx: {"executed": True},
    )
    
    assert not approved
    assert "executed" not in str(result)
    
    gate.kernel = original_kernel
```

## Test Structure

### Minimum Test Coverage Per Action
Every governed action must have:

1. **Success test** — validates approved execution
2. **Denial test** — validates blocked execution
3. **Audit test** — validates evidence generation
4. **Error test** — validates exception handling
5. **Invariant test** — validates invariant compliance

### Test File Template

```python
"""test_my_feature.py — Governance tests for MyFeature."""
import json
import pytest
from pathlib import Path

from app.core.execution_gate import ExecutionGate
from app.core.invariant_engine import InvariantEngine
from app.my_module.my_feature import MyFeature


class TestMyFeatureGovernance:
    """Governance compliance tests for MyFeature."""
    
    @pytest.fixture
    def feature(self):
        """Create feature instance."""
        return MyFeature()
    
    @pytest.fixture
    def gate(self):
        """Create execution gate."""
        return ExecutionGate()
    
    def test_action_success(self, feature, gate):
        """Verify action succeeds when approved."""
        approved, result = gate.execute(
            domain="my_feature",
            action="my_action",
            context={"valid": True},
            executor_fn=lambda ctx: feature.do_action(ctx),
        )
        
        assert approved
        assert result["success"]
    
    def test_action_denial(self, feature, gate):
        """Verify action blocks when denied."""
        approved, result = gate.execute(
            domain="my_feature",
            action="forbidden_action",
            context={"forbidden": True},
            executor_fn=lambda ctx: feature.do_action(ctx),
        )
        
        assert not approved
        assert "denied" in str(result).lower()
    
    def test_action_audit(self, feature, gate, tmp_path):
        """Verify action generates audit evidence."""
        import os
        os.environ["EVIDENCE_DIR"] = str(tmp_path)
        
        gate.execute(
            domain="my_feature",
            action="my_action",
            context={"session_id": "audit-test"},
            executor_fn=lambda ctx: feature.do_action(ctx),
        )
        
        evidence_files = list(tmp_path.glob("audit-test-*.json"))
        assert len(evidence_files) > 0
        
        with open(evidence_files[0]) as f:
            evidence = json.load(f)
        
        assert evidence["domain"] == "my_feature"
        assert evidence["action"] == "my_action"
        assert "request_hash" in evidence
        assert "outcome" in evidence
    
    def test_action_error_handling(self, feature, gate):
        """Verify graceful error handling."""
        approved, result = gate.execute(
            domain="my_feature",
            action="my_action",
            context={"trigger_error": True},
            executor_fn=lambda ctx: feature.do_action(ctx),
        )
        
        # Should still be governed even on error
        assert isinstance(result, (dict, str))
        if isinstance(result, dict):
            assert "error" in result or "success" in result
    
    def test_action_invariants(self):
        """Verify action respects invariants."""
        engine = InvariantEngine()
        
        # Test case that should violate invariant
        violations = engine.validate_all({
            "action": "my_action",
            "domain": "my_feature",
            "state": {"invalid_state": True},
        })
        
        # Validate violations are detected
        # (Adjust based on actual invariants)
        assert isinstance(violations, list)


class TestMyFeatureFunctionality:
    """Functional tests for MyFeature."""
    
    @pytest.fixture
    def feature(self):
        return MyFeature()
    
    def test_business_logic(self, feature):
        """Test core business logic."""
        result = feature.process_data({"input": "value"})
        assert result["output"] == "expected"
    
    # Add functional tests here
```

## Governance Test Patterns

### Pattern 1: Deny by Context
```python
def test_action_denied_by_context():
    gate = ExecutionGate()
    
    approved, _ = gate.execute(
        domain="test",
        action="sensitive_action",
        context={"user_role": "guest"},  # Insufficient role
        executor_fn=lambda ctx: {"data": "sensitive"},
    )
    
    assert not approved
```

### Pattern 2: Deny by Risk Score
```python
def test_action_denied_by_risk():
    gate = ExecutionGate()
    
    approved, _ = gate.execute(
        domain="test",
        action="high_risk_action",
        context={"risk_multiplier": 10.0},
        executor_fn=lambda ctx: {"executed": True},
    )
    
    assert not approved
```

### Pattern 3: Evidence Chain Validation
```python
def test_evidence_chain_integrity(tmp_path):
    import os
    os.environ["EVIDENCE_DIR"] = str(tmp_path)
    
    gate = ExecutionGate()
    
    # Execute multiple actions
    for i in range(3):
        gate.execute(
            domain="test",
            action=f"action_{i}",
            context={"session_id": "chain-test", "index": i},
            executor_fn=lambda ctx: {"index": ctx["index"]},
        )
    
    # Verify evidence chain
    evidence_files = sorted(tmp_path.glob("chain-test-*.json"))
    assert len(evidence_files) == 3
    
    # Verify chronological order
    timestamps = []
    for f in evidence_files:
        with open(f) as fp:
            ev = json.load(fp)
            timestamps.append(ev.get("timestamp", 0))
    
    assert timestamps == sorted(timestamps)
```

### Pattern 4: Degraded Mode Testing
```python
def test_degraded_mode_read_only():
    gate = ExecutionGate()
    
    # Simulate governance component failure
    # Only read-only operations should proceed
    approved, _ = gate.execute(
        domain="test",
        action="read_data",
        context={"degraded_mode": True, "read_only": True},
        executor_fn=lambda ctx: {"data": "value"},
    )
    
    # Read-only may proceed in degraded mode
    # (depends on implementation)
    
    approved_write, _ = gate.execute(
        domain="test",
        action="write_data",
        context={"degraded_mode": True},
        executor_fn=lambda ctx: {"written": True},
    )
    
    # Write must fail in degraded mode
    assert not approved_write
```

## Integration Test Requirements

### End-to-End Governance Flow
```python
def test_end_to_end_governance_flow(tmp_path):
    """Test complete governance pipeline."""
    import os
    os.environ["EVIDENCE_DIR"] = str(tmp_path)
    
    from app.core.execution_gate import ExecutionGate
    from app.agents.my_agent import MyAgent
    
    agent = MyAgent()
    
    # Execute agent action
    result = agent.perform_action({"input": "test"})
    
    # Verify governance was engaged
    assert "success" in result
    
    # Verify audit trail
    evidence_files = list(tmp_path.glob("*.json"))
    assert len(evidence_files) > 0
    
    # Verify evidence content
    with open(evidence_files[0]) as f:
        evidence = json.load(f)
    
    assert evidence["domain"] in ["agent.my_agent", "MyAgent"]
    assert "outcome" in evidence
```

### Invariant Suite Integration
```python
def test_canonical_scenario_compliance():
    """Verify behavior matches canonical scenario."""
    import subprocess
    
    result = subprocess.run(
        ["py", "-3.12", "canonical/replay.py"],
        capture_output=True,
        text=True,
    )
    
    assert result.returncode == 0
    assert "5/5" in result.stdout or "all invariants pass" in result.stdout.lower()
```

## Test Data Isolation

### Use Temporary Directories
```python
@pytest.fixture
def isolated_env(tmp_path, monkeypatch):
    """Create isolated environment for tests."""
    evidence_dir = tmp_path / "evidence"
    evidence_dir.mkdir()
    
    monkeypatch.setenv("EVIDENCE_DIR", str(evidence_dir))
    monkeypatch.setenv("AUDIT_DIR", str(tmp_path / "audit"))
    monkeypatch.setenv("DATA_DIR", str(tmp_path / "data"))
    
    return tmp_path

def test_with_isolation(isolated_env):
    """Test with isolated environment."""
    gate = ExecutionGate()
    
    gate.execute(
        domain="test",
        action="test",
        context={},
        executor_fn=lambda ctx: {},
    )
    
    # Evidence only in isolated directory
    evidence_files = list(isolated_env.glob("evidence/*.json"))
    assert len(evidence_files) > 0
```

## Continuous Governance Validation

### Pre-commit Hook
Add to `.git/hooks/pre-commit`:
```bash
#!/bin/bash
# Run governance tests before commit

echo "Running governance validation..."
pytest tests/ -k "governance" -v

if [ $? -ne 0 ]; then
    echo "Governance tests failed. Commit aborted."
    exit 1
fi

echo "Running canonical scenario..."
py -3.12 canonical/replay.py

if [ $? -ne 0 ]; then
    echo "Canonical scenario failed. Commit aborted."
    exit 1
fi

echo "Governance validation passed."
```

### CI Pipeline
Add to `.github/workflows/ci.yml`:
```yaml
- name: Run Governance Tests
  run: |
    pytest tests/ -k "governance" -v --cov=app/core --cov-report=term

- name: Validate Canonical Scenario
  run: |
    python -c "import sys; sys.path.insert(0, 'src')"
    py -3.12 canonical/replay.py

- name: Check Evidence Integrity
  run: |
    python scripts/validate_evidence_chain.py
```

## Test Coverage Requirements

Minimum coverage thresholds:
- **Governance modules**: 90%
- **Agent modules**: 80%
- **Core modules**: 85%
- **Overall**: 80%

Focus on:
- Denial paths (must be tested)
- Audit generation (must be tested)
- Error handling (must be tested)
- Invariant validation (must be tested)

## Related Files

- `canonical/scenario.yaml` — Ground truth governance behavior
- `canonical/replay.py` — Invariant validation suite
- `src/app/core/execution_gate.py` — Execution gate
- `src/app/core/invariant_engine.py` — Invariant engine
- `pyproject.toml` — Test configuration
