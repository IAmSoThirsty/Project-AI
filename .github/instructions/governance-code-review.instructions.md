---
description: "Code review checklist for governance compliance: bypass detection, fail-closed verification, audit validation."
applyTo: "**/*.py"
tags: [code-review, governance, compliance, security]
created: 2026-05-13
status: mandatory
enforcement: pull-request
---

# Governance Code Review Checklist

All code changes must be reviewed for governance compliance before merging.

## Critical Review Points

### 1. Bypass Path Detection 🚨

**Check for these anti-patterns:**

#### ❌ Conditional Governance
```python
# REJECT — bypasses governance when kernel is unavailable
if self.kernel:
    return self._execute_through_kernel(...)
else:
    return self._execute_directly(...)
```

#### ❌ Silent Fallback
```python
# REJECT — executes on governance failure
try:
    approved = kernel.evaluate_action(...)
    if approved:
        execute()
except Exception:
    execute()  # Bypass on error
```

#### ❌ Trusted Shortcuts
```python
# REJECT — skips governance for "trusted" entities
if user.is_admin or source == "internal":
    return execute_directly()
else:
    return execute_through_gate()
```

#### ❌ Mock Security
```python
# REJECT — always returns true
def check_permission(user):
    return True
```

#### ❌ Default Allow
```python
# REJECT — allows when governance unavailable
allowed = kernel.evaluate(...) if kernel else True
```

### 2. Fail-Closed Verification ✅

**Verify these patterns:**

#### ✅ Explicit Denial
```python
# APPROVE — explicit fail-closed behavior
approved, result = gate.execute(...)
if not approved:
    logger.warning(f"Action denied: {result}")
    return {"success": False, "reason": result}
# Only proceed if approved
```

#### ✅ No Silent Fallthrough
```python
# APPROVE — no execution without approval
approved, result = gate.execute(...)
if not approved:
    return False, result  # Stop here

# Approved path continues
return True, execute_action()
```

#### ✅ Degraded Mode Restrictions
```python
# APPROVE — degraded mode only for read-only
if degraded_mode:
    if action.is_write_operation():
        return False, "Degraded mode blocks writes"
    # Allow read-only in degraded mode
```

### 3. Audit Trail Validation 📝

**Ensure evidence generation:**

#### ✅ Evidence Bundle Creation
```python
# APPROVE — evidence automatically created
approved, result = gate.execute(
    domain="my_domain",
    action="my_action",
    context={
        "session_id": session_id,
        "request_text": "Human-readable description",
    },
    executor_fn=lambda ctx: perform_action(ctx),
)
# Evidence bundle created at data/evidence/{session_id}-*.json
```

#### ✅ Denial Evidence
```python
# APPROVE — denials generate evidence
if not approved:
    # Evidence bundle includes:
    # - outcome: "DENY"
    # - outcome_reason: reason for denial
    # - request_hash, context_hash, timestamp
    return False, result
```

### 4. Capability Verification 🔑

**Check capability enforcement:**

#### ✅ Capability Check Before Action
```python
# APPROVE — capability verified before execution
has_capability, reason = cap_system.validate_capability(
    domain="file.write",
    action="modify_source",
    context={"path": target_path},
)
if not has_capability:
    return {"success": False, "reason": reason}
# Only proceed with capability
```

#### ❌ Missing Capability Check
```python
# REJECT — no capability verification
def write_file(path, content):
    with open(path, "w") as f:  # Direct write
        f.write(content)
```

### 5. Invariant Compliance 🛡️

**Verify invariant validation:**

#### ✅ Invariant Check Before Execution
```python
# APPROVE — invariants validated
violations = inv_engine.validate_all({
    "action": action_name,
    "domain": domain,
    "state": current_state,
})
if violations:
    return {"success": False, "violations": violations}
```

#### ❌ Missing Invariant Validation
```python
# REJECT — no invariant check
def escalate_issue(issue_id):
    # Missing severity check (violates invariant)
    send_alert(issue_id)
```

## Review Workflow

### Phase 1: Automated Checks
- [ ] Pre-commit hooks pass (mandatory structured generation)
- [ ] CI pipeline passes (tests, linting, type checking)
- [ ] Canonical replay passes: `py -3.12 canonical/replay.py` shows 5/5
- [ ] Codacy analysis passes (if applicable)

### Phase 2: Manual Review
- [ ] **Bypass detection**: No bypass paths present
- [ ] **Fail-closed**: All denial paths prevent execution
- [ ] **Audit generation**: Evidence bundles created
- [ ] **Capability checks**: Required capabilities verified
- [ ] **Invariant validation**: Invariants checked before execution
- [ ] **Test coverage**: Denial tests present
- [ ] **Documentation**: Governance behavior documented

### Phase 3: Integration Validation
- [ ] **End-to-end test**: Governance flow tested
- [ ] **Evidence integrity**: Evidence bundles validated
- [ ] **No regressions**: Existing governance preserved
- [ ] **Interface preservation**: Public interfaces unchanged (unless intended)

## Common Issues and Fixes

### Issue 1: Missing Governance Integration

**Problem:**
```python
class NewAgent:
    def perform_action(self, args):
        return self._execute(args)  # No governance
```

**Fix:**
```python
from app.core.kernel_integration import KernelRoutedAgent

class NewAgent(KernelRoutedAgent):
    def __init__(self, kernel=None):
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",
        )
    
    def perform_action(self, args):
        return self._execute_through_kernel(
            action=self._execute,
            action_name="NewAgent.perform_action",
            action_args=(args,),
            requires_approval=True,
            risk_level="medium",
        )
```

### Issue 2: Direct API Call Without Governance

**Problem:**
```python
def generate_text(prompt):
    client = OpenAI()
    return client.chat.completions.create(...)  # Direct call
```

**Fix:**
```python
def generate_text(prompt):
    gate = ExecutionGate()
    
    approved, result = gate.execute(
        domain="ai.generation",
        action="generate_text",
        context={
            "session_id": get_session_id(),
            "request_text": f"Generate text for: {prompt}",
        },
        executor_fn=lambda ctx: _call_openai(prompt),
    )
    
    if not approved:
        return {"success": False, "reason": result}
    return result

def _call_openai(prompt):
    client = OpenAI()
    return client.chat.completions.create(...)
```

### Issue 3: Missing Denial Test

**Problem:**
```python
# Only success test present
def test_action_success():
    result = agent.perform_action({"valid": True})
    assert result["success"]
# No denial test
```

**Fix:**
```python
def test_action_success():
    result = agent.perform_action({"valid": True})
    assert result["success"]

def test_action_denial():
    """Verify action respects denial."""
    # Mock governance to deny
    original_kernel = agent.kernel
    
    class DenyingKernel:
        def evaluate_action(self, domain, action, context):
            class Decision:
                reason = "Test denial"
            return False, Decision()
    
    agent.kernel = DenyingKernel()
    result = agent.perform_action({"valid": True})
    
    assert result["success"] is False
    assert "denied" in str(result).lower()
    
    agent.kernel = original_kernel
```

### Issue 4: Missing Audit Evidence

**Problem:**
```python
def perform_action(context):
    if authorized(context):
        execute()  # No evidence generated
```

**Fix:**
```python
def perform_action(context):
    gate = ExecutionGate()
    
    approved, result = gate.execute(
        domain="my_domain",
        action="my_action",
        context=context,
        executor_fn=lambda ctx: execute(),
    )
    # Evidence automatically generated
    return result
```

## Reviewer Questions

When reviewing code, ask:

1. **"How does this handle denial?"**
   - Look for explicit denial path handling
   - Verify no execution on denial

2. **"What happens if governance is unavailable?"**
   - Should fail-closed (block execution)
   - Degraded mode only for read-only operations

3. **"Where is the evidence generated?"**
   - ExecutionGate.execute() creates evidence
   - Manual evidence creation must be validated

4. **"Are there bypass paths?"**
   - Check for conditional governance
   - Check for try/except patterns
   - Check for trusted shortcuts

5. **"Are invariants validated?"**
   - Check for invariant engine usage
   - Verify critical invariants checked

6. **"Is there a denial test?"**
   - Every governed action needs denial test
   - Test must verify no execution on denial

7. **"Does this preserve existing governance?"**
   - No removal of kernel integration
   - No bypass paths introduced
   - Public interfaces maintained

## Approval Criteria

**Code may be approved only if:**

- ✅ All automated checks pass
- ✅ No bypass paths detected
- ✅ Fail-closed behavior verified
- ✅ Audit evidence generated
- ✅ Capability checks present (where applicable)
- ✅ Invariant validation present (where applicable)
- ✅ Denial tests present
- ✅ Documentation updated
- ✅ No regressions introduced
- ✅ Canonical replay passes (5/5 invariants)

**Code must be rejected if:**

- ❌ Bypass paths present
- ❌ Silent fallback on governance failure
- ❌ Missing audit evidence
- ❌ Missing denial tests
- ❌ Governance integration removed
- ❌ Canonical replay fails

## Review Comments Template

### Bypass Path Detected
```
**Governance Bypass Detected** 🚨

This code bypasses governance when [condition]:
[code snippet]

**Required fix**: Route through ExecutionGate.execute() or remove bypass path.

**Reference**: .github/instructions/governance-enforced-development.instructions.md
```

### Missing Denial Test
```
**Missing Denial Test** 📋

This action requires a denial test to verify governance compliance.

**Required test**:
```python
def test_[action]_denial():
    # Test that action respects denial
    # Verify no execution when denied
```

**Reference**: .github/instructions/governance-testing-protocol.instructions.md
```

### Missing Audit Evidence
```
**Missing Audit Evidence** 📝

This action must generate audit evidence.

**Required fix**: Route through ExecutionGate.execute() to automatically generate evidence.

**Reference**: .github/instructions/audit-evidence-protocol.instructions.md
```

## Related Files

- `.github/instructions/governance-enforced-development.instructions.md`
- `.github/instructions/agent-development-protocol.instructions.md`
- `.github/instructions/governance-testing-protocol.instructions.md`
- `.github/instructions/audit-evidence-protocol.instructions.md`
- `canonical/scenario.yaml` — Ground truth governance
- `canonical/replay.py` — Invariant validation (must pass 5/5)
