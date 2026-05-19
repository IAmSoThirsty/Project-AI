---
description: "Governance-enforced development protocol: execution gates, audit trails, fail-closed behavior, and no bypass paths."
applyTo: "**"
tags: [governance, execution-gate, audit, fail-closed, security]
created: 2026-05-13
status: mandatory
enforcement: pre-commit
---

# Governance-Enforced Development Protocol

All AI agents and IDE copilots operating in this repository must follow governance-first execution principles.

## Core Principles

### 1. Governance Before Execution
- **Every meaningful action** must route through `ExecutionGate.execute()` or `CognitionKernel.evaluate_action()`.
- No direct provider calls (OpenAI, Anthropic, etc.) without kernel governance.
- No direct file system mutations without authorization.
- No direct database writes without capability verification.

### 2. Fail-Closed by Default
- When governance checks fail, the action **must not execute**.
- Degraded modes are only permitted for read-only operations and must be explicitly justified.
- Silent failures are prohibited — all denials must be audited.

### 3. No Bypass Paths
Prohibited patterns:
- `if not kernel: return execute_anyway()`
- `try: check_governance() except: pass`
- `if config.get("skip_governance"): direct_execute()`
- Trusted shortcuts that skip authorization
- Fallback execution when governance is unavailable

### 4. Audit Everything
All actions must generate audit evidence:
- Request hash (SHA-256 of request text)
- Context hash (for reproducibility)
- Policy version and hash
- Outcome (ALLOW/DENY/ESCALATE/TERMINATE)
- Risk score
- Evidence bundle location

## Mandatory Patterns

### Action Execution Pattern
```python
from app.core.execution_gate import ExecutionGate

gate = ExecutionGate()

# Correct
approved, result = gate.execute(
    domain="agent.knowledge",
    action="update_knowledge_base",
    context={
        "session_id": session_id,
        "request_text": "Update knowledge base with new entry",
        "user_id": user_id,
    },
    executor_fn=lambda ctx: perform_update(ctx),
)

if not approved:
    # Action was denied — log and return
    logger.warning(f"Action denied: {result}")
    return {"success": False, "reason": result}

# Proceed with approved result
return result
```

### Agent Integration Pattern
```python
from app.core.kernel_integration import KernelRoutedAgent
from app.core.cognition_kernel import CognitionKernel, ExecutionType

class MyAgent(KernelRoutedAgent):
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",
        )
    
    def perform_action(self, args: dict) -> dict:
        return self._execute_through_kernel(
            action=self._do_action,
            action_name="MyAgent.perform_action",
            action_args=(args,),
            requires_approval=True,
            risk_level="high",
            metadata={"operation": "data_mutation"},
        )
    
    def _do_action(self, args: dict) -> dict:
        # Implementation — only called if governance approves
        return {"success": True, "data": process(args)}
```

### Capability Verification Pattern
```python
from app.core.capability_token import CapabilityTokenSystem

cap_system = CapabilityTokenSystem()

# Check capability before action
has_capability, reason = cap_system.validate_capability(
    domain="file.write",
    action="modify_source",
    context={"path": target_path, "user_id": user_id},
)

if not has_capability:
    logger.error(f"Capability denied: {reason}")
    return {"success": False, "reason": reason}

# Proceed with capability-authorized action
```

### Invariant Validation Pattern
```python
from app.core.invariant_engine import InvariantEngine

inv_engine = InvariantEngine()

# Load and validate invariants before execution
violations = inv_engine.validate_all(context={
    "action": action_name,
    "domain": domain,
    "state": current_state,
})

if violations:
    logger.error(f"Invariant violations: {violations}")
    return {"success": False, "violations": violations}

# Proceed only if no invariants violated
```

## Prohibited Patterns

### ❌ Direct Execution Without Governance
```python
# WRONG — bypasses governance
def update_config(new_config):
    with open("config.json", "w") as f:
        json.dump(new_config, f)
```

### ❌ Silent Fallback
```python
# WRONG — executes on governance failure
try:
    approved = kernel.evaluate_action(domain, action, context)
    if approved:
        execute()
except Exception:
    execute()  # Bypass on error
```

### ❌ Mock Security
```python
# WRONG — fake security check
def check_permission(user):
    return True  # Always allows
```

### ❌ Trusted Shortcuts
```python
# WRONG — skips verification for "trusted" users
if user.is_admin:
    return execute_directly()  # No governance
else:
    return execute_through_gate()
```

## Testing Requirements

### Every Code Change Must Include:
1. **Unit tests** validating governed behavior
2. **Integration tests** verifying end-to-end governance flow
3. **Negative tests** confirming denials work correctly
4. **Audit verification** confirming evidence generation

### Test Pattern
```python
def test_action_requires_governance():
    """Verify action cannot execute without governance approval."""
    gate = ExecutionGate()
    
    # Simulate denial
    approved, result = gate.execute(
        domain="test.domain",
        action="forbidden_action",
        context={"should_deny": True},
        executor_fn=lambda ctx: {"executed": True},
    )
    
    assert not approved, "Action should be denied"
    assert "executed" not in str(result), "Executor should not run"

def test_denial_generates_audit():
    """Verify denials generate audit evidence."""
    gate = ExecutionGate()
    
    approved, result = gate.execute(
        domain="test.domain",
        action="test_action",
        context={"session_id": "test-session"},
        executor_fn=lambda ctx: {"data": "value"},
    )
    
    # Check evidence bundle created
    evidence_path = Path(f"data/evidence/test-session-*.json")
    assert list(evidence_path.parent.glob(evidence_path.name)), \
        "Evidence bundle must be created"
```

## Verification Checklist

Before committing code that performs actions:

- [ ] Routes through `ExecutionGate.execute()` or `CognitionKernel.evaluate_action()`
- [ ] No direct provider/API calls without kernel governance
- [ ] No direct file/DB mutations without authorization
- [ ] Fail-closed behavior on governance failure
- [ ] No bypass paths or fallback execution
- [ ] Audit evidence generated for all actions
- [ ] Tests verify governance behavior
- [ ] Tests verify denial behavior
- [ ] Tests verify audit trail creation

## Enforcement

- **Pre-commit hooks** validate governance patterns
- **CI pipeline** runs governance compliance tests
- **Code review** requires governance verification
- **Non-compliant code** will be rejected

## Related Documentation

- `src/app/core/execution_gate.py` — Execution gate implementation
- `src/app/core/cognition_kernel.py` — Cognition kernel
- `src/app/core/kernel_integration.py` — Agent integration patterns
- `canonical/scenario.yaml` — Canonical governance scenario
- `canonical/replay.py` — Invariant validation suite (must pass 5/5)

## Questions?

If governance requirements are unclear:
1. Read `canonical/scenario.yaml` for ground-truth behavior
2. Run `py -3.12 canonical/replay.py` to see governance in action
3. Review existing governed agents in `src/app/agents/`
4. Ask for clarification rather than implementing without governance
