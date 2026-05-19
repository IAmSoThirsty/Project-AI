---
description: "Protocol for creating, modifying, and testing AI agents with mandatory governance integration."
applyTo: "src/app/agents/**"
tags: [agent-development, governance, testing, integration]
created: 2026-05-13
status: mandatory
---

# Agent Development Protocol

Guidelines for creating and modifying AI agents in `src/app/agents/`.

## Agent Classification

All agents fall into one of two categories:

### 1. Governed Agents (Default)
**Must** route through `CognitionKernel` for all actions.

Required for agents that:
- Make AI/LLM API calls
- Modify files or databases
- Execute external commands
- Make network requests
- Handle sensitive data
- Perform security-critical operations

### 2. Bypass-by-Design Agents (Rare Exception)
Only permitted when **all** of these conditions hold:
- No AI calls
- No external APIs
- No file system modifications
- No network I/O
- No security implications
- Pure utility/coordination logic

**Bypass requires explicit justification in code comments.**

## Creating a New Agent

### Step 1: Determine Governance Requirement
Ask: Does this agent perform ANY of these?
- [ ] AI/LLM API calls
- [ ] File/database writes
- [ ] External API calls
- [ ] Code execution
- [ ] Security operations

If **any** checkbox is true → **Governed Agent** (use template below)

### Step 2: Choose Risk Level
- **High**: Security, adversarial, sandbox, code modification
- **Medium**: CI/CD, refactoring, expert actions, dependency auditing
- **Low**: Documentation, knowledge curation, telemetry, retrieval

### Step 3: Implement with Kernel Integration

**File**: `src/app/agents/my_new_agent.py`

```python
"""my_new_agent.py — Brief description of agent purpose.

GOVERNANCE STATUS: ✅ GOVERNED
- Routes through CognitionKernel
- Risk level: [high|medium|low]
- Requires approval: [yes|no]
"""
from __future__ import annotations

import logging
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class MyNewAgent(KernelRoutedAgent):
    """Brief one-line description.
    
    Detailed description of what this agent does, when to use it,
    and what governance controls apply.
    """
    
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        """Initialize agent with optional kernel injection.
        
        Args:
            kernel: CognitionKernel instance for governance routing.
                   If None, a default kernel will be created.
        """
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",  # Adjust based on Step 2
        )
    
    def primary_action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Primary agent action with governance routing.
        
        Args:
            input_data: Input parameters for the action.
        
        Returns:
            dict with 'success': bool and action results.
        """
        return self._execute_through_kernel(
            action=self._do_primary_action,
            action_name="MyNewAgent.primary_action",
            action_args=(input_data,),
            requires_approval=True,  # Set based on risk
            risk_level="medium",  # Can override default per-action
            metadata={
                "operation_type": "describe_operation",
                "input_keys": list(input_data.keys()),
            },
        )
    
    def _do_primary_action(self, input_data: dict[str, Any]) -> dict[str, Any]:
        """Internal implementation — only called if governance approves.
        
        This method contains the actual business logic and is only
        invoked after successful governance checks.
        
        Args:
            input_data: Validated input parameters.
        
        Returns:
            dict with action results.
        """
        try:
            # Actual implementation here
            result = self._process_input(input_data)
            
            return {
                "success": True,
                "result": result,
                "agent": "MyNewAgent",
            }
        except Exception as e:
            logger.error(f"MyNewAgent.primary_action failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent": "MyNewAgent",
            }
    
    def _process_input(self, input_data: dict[str, Any]) -> Any:
        """Private helper method for business logic."""
        # Implementation details
        pass
```

### Step 4: Create Tests

**File**: `tests/agents/test_my_new_agent.py`

```python
"""Tests for MyNewAgent governance and functionality."""
import pytest
from app.agents.my_new_agent import MyNewAgent
from app.core.cognition_kernel import CognitionKernel


class TestMyNewAgent:
    """Test suite for MyNewAgent."""
    
    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        kernel = CognitionKernel()
        return MyNewAgent(kernel=kernel)
    
    def test_agent_initialization(self, agent):
        """Verify agent initializes with kernel."""
        assert agent.kernel is not None
        assert agent.execution_type.value == "agent_action"
        assert agent.default_risk_level == "medium"
    
    def test_primary_action_success(self, agent):
        """Verify primary action succeeds with valid input."""
        input_data = {"key": "value"}
        result = agent.primary_action(input_data)
        
        assert result["success"] is True
        assert "result" in result
        assert result["agent"] == "MyNewAgent"
    
    def test_primary_action_requires_governance(self, agent):
        """Verify action routes through governance."""
        # Mock governance to deny
        original_kernel = agent.kernel
        
        class DenyingKernel:
            def evaluate_action(self, domain, action, context):
                class Decision:
                    reason = "Test denial"
                return False, Decision()
        
        agent.kernel = DenyingKernel()
        
        result = agent.primary_action({"key": "value"})
        
        # Should respect governance denial
        assert result["success"] is False
        
        # Restore original kernel
        agent.kernel = original_kernel
    
    def test_primary_action_generates_audit(self, agent, tmp_path):
        """Verify action generates audit evidence."""
        # Configure evidence path
        import os
        os.environ["EVIDENCE_DIR"] = str(tmp_path)
        
        input_data = {"key": "value"}
        agent.primary_action(input_data)
        
        # Check for evidence files
        evidence_files = list(tmp_path.glob("*.json"))
        assert len(evidence_files) > 0, "Audit evidence must be created"
    
    def test_primary_action_handles_errors(self, agent):
        """Verify graceful error handling."""
        # Test with invalid input that triggers error
        result = agent.primary_action(None)
        
        assert result["success"] is False
        assert "error" in result
```

### Step 5: Update Documentation

Add entry to `src/app/agents/README.md`:

```markdown
### My Category (X agents)
- `my_new_agent.py` - Brief description of purpose
```

Add entry to `src/app/agents/AGENT_CLASSIFICATION.md`:

```markdown
#### MyNewAgent
- **File**: `my_new_agent.py`
- **Status**: ✅ GOVERNED
- **Risk Level**: Medium
- **Requires Approval**: Yes
- **Purpose**: [Description]
- **Governance Route**: CognitionKernel → ExecutionGate
- **AI Integration**: [None|Planned|Active]
```

## Modifying Existing Agents

### Before Modifying
1. Read the agent's docstring and governance status
2. Check `AGENT_CLASSIFICATION.md` for risk level
3. Review existing tests in `tests/agents/`
4. Understand the governance flow

### Modification Rules
- **Preserve** governance routing (never remove kernel integration)
- **Maintain** public interface unless explicitly changing API
- **Add/update** tests for new behavior
- **Update** docstrings to reflect changes
- **Preserve** audit logging

### After Modifying
1. Run agent-specific tests: `pytest tests/agents/test_<agent>.py -v`
2. Run governance suite: `py -3.12 canonical/replay.py` (must show 5/5)
3. Check audit logs in `data/governance_drift_alerts/`
4. Verify no bypass paths introduced

## Anti-Patterns to Avoid

### ❌ Conditional Governance
```python
# WRONG
if self.kernel:
    return self._execute_through_kernel(...)
else:
    return self._execute_directly(...)  # Bypass
```

### ❌ Silent Error Handling
```python
# WRONG
try:
    approved, result = self.kernel.evaluate_action(...)
except Exception:
    pass  # Silent failure
return execute_anyway()
```

### ❌ Mock Approval
```python
# WRONG
def _mock_approval(self):
    return True  # Always approve in production code
```

### ❌ Untested Actions
```python
# WRONG — new action without tests
def new_risky_action(self):
    return self._execute_through_kernel(...)
    # No corresponding test in test file
```

## Testing Checklist

For every agent action:
- [ ] Unit test validates success case
- [ ] Unit test validates governance denial
- [ ] Unit test validates error handling
- [ ] Integration test validates end-to-end flow
- [ ] Test validates audit evidence generation
- [ ] Test validates invariant compliance
- [ ] All tests pass before commit

## Agent Lifecycle

### Development
1. Create agent file with governance integration
2. Create test file with comprehensive tests
3. Update documentation (README.md, AGENT_CLASSIFICATION.md)
4. Run tests locally
5. Run canonical replay: `py -3.12 canonical/replay.py`

### Code Review
- Verify governance integration present
- Verify no bypass paths
- Verify tests cover governance behavior
- Verify documentation updated
- Verify canonical replay passes

### Deployment
- All tests pass in CI
- Governance compliance verified
- Audit logging confirmed
- Evidence bundles generated

### Maintenance
- Monitor `data/governance_drift_alerts/` for denials
- Review audit logs in `data/acceptance_ledger/`
- Update tests when behavior changes
- Keep documentation current

## Common Questions

**Q: When can I bypass governance?**  
A: Only for pure utility functions with no I/O, no AI, no security impact. Document the bypass justification explicitly.

**Q: What if governance is too slow?**  
A: Optimize the governance path, don't bypass it. Talk to the team about performance improvements.

**Q: Can I cache governance decisions?**  
A: Only with explicit kernel support and audit trail preservation. Never cache approvals without evidence.

**Q: What if my agent needs elevated permissions?**  
A: Use capability tokens and document the elevated permission requirement. Don't bypass governance.

## Related Files

- `src/app/core/execution_gate.py` — Execution gate
- `src/app/core/cognition_kernel.py` — Cognition kernel
- `src/app/core/kernel_integration.py` — Integration base classes
- `src/app/agents/AGENT_CLASSIFICATION.md` — Agent inventory
- `canonical/scenario.yaml` — Governance ground truth
- `canonical/replay.py` — Validation suite
