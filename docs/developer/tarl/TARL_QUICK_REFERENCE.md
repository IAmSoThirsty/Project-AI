# TARL Quick Reference Guide

## Quick Start

### 1. Initialize the System

```bash
python bootstrap.py
```

### 2. Import Components

```python
from tarl.runtime import TarlRuntime
from tarl.policies.default import DEFAULT_POLICIES
from kernel.execution import ExecutionKernel
from governance.core import GovernanceCore
from src.cognition.codex.escalation import CodexDeus
```

### 3. Basic Usage

```python

# Initialize

runtime = TarlRuntime(DEFAULT_POLICIES)
codex = CodexDeus()
governance = GovernanceCore()
kernel = ExecutionKernel(governance, runtime, codex)

# Execute with context

context = {"agent": "my_agent", "mutation": False}
result = kernel.execute("action", context)
```

## Context Keys

Required keys for TARL policy evaluation:

| Key                | Type        | Description                   | Required    |
| ------------------ | ----------- | ----------------------------- | ----------- |
| `agent`            | str or None | Agent identity                | Yes         |
| `mutation`         | bool        | Whether action mutates state  | Yes         |
| `mutation_allowed` | bool        | Whether mutation is permitted | Conditional |

## Policy Behavior

### deny_unauthorized_mutation

- **Triggers**: `mutation=True` AND `mutation_allowed=False`
- **Verdict**: DENY
- **Reason**: "Mutation not permitted by TARL policy"

### escalate_on_unknown_agent

- **Triggers**: `agent=None`
- **Verdict**: ESCALATE
- **Reason**: "Unknown agent identity"

## Common Patterns

### Safe Read Operation

```python
context = {
    "agent": "authenticated_user",
    "mutation": False,
    "mutation_allowed": False,
}

# Result: ALLOW

```

### Authorized Mutation

```python
context = {
    "agent": "admin_user",
    "mutation": True,
    "mutation_allowed": True,
}

# Result: ALLOW

```

### Denied Mutation

```python
context = {
    "agent": "user",
    "mutation": True,
    "mutation_allowed": False,
}

# Result: DENY

```

### Escalated Request

```python
context = {
    "agent": None,
    "mutation": False,
    "mutation_allowed": False,
}

# Result: ESCALATE (SystemExit)

```

## Custom Policy Example

```python
from tarl.policy import TarlPolicy
from tarl.spec import TarlDecision, TarlVerdict
from tarl.runtime import TarlRuntime

def rate_limit_policy(ctx):
    if ctx.get("requests_per_minute", 0) > 100:
        return TarlDecision(
            verdict=TarlVerdict.DENY,
            reason="Rate limit exceeded",
            metadata={"limit": 100}
        )
    return TarlDecision(TarlVerdict.ALLOW, "OK")

# Add to runtime

policies = DEFAULT_POLICIES + [
    TarlPolicy("rate_limit", rate_limit_policy)
]
runtime = TarlRuntime(policies)
```

## Error Handling

```python
from kernel.tarl_gate import TarlEnforcementError

try:
    kernel.execute(action, context)
except TarlEnforcementError as e:
    print(f"TARL blocked action: {e}")
except SystemExit as e:
    print(f"Critical escalation: {e}")
```

## Testing

### Run All Tests

```bash
python test_tarl_integration.py
```

### Run Fuzzer

```bash
python -m tarl.fuzz.fuzz_tarl
```

### Bootstrap Verification

```bash
python bootstrap.py
```

## Troubleshooting

### Issue: "Unknown agent identity" escalation

**Solution**: Ensure `agent` is set in context

```python
context["agent"] = "authenticated_user"
```

### Issue: "Mutation not permitted" denial

**Solution**: Set `mutation_allowed=True` for authorized mutations

```python
context["mutation_allowed"] = True
```

### Issue: SystemExit on escalation

**Solution**: This is expected for HIGH priority escalations. Handle in production:

```python

# In production, consider catching SystemExit

# and routing to incident response system

```

## Best Practices

1. **Always provide agent identity**: Never leave `agent=None` unless intentional
1. **Explicit mutation flags**: Always set `mutation` and `mutation_allowed`
1. **Test policies**: Use fuzzer before deploying new policies
1. **Audit logs**: Review governance audit logs regularly
1. **Policy ordering**: Place more specific policies first in the list
1. **Metadata usage**: Include meaningful metadata for debugging

## Performance Tips

- Policies are evaluated in order; place most common ALLOW cases first
- Use metadata sparingly to avoid memory overhead
- Consider caching policy decisions for identical contexts
- Monitor escalation frequency to detect anomalies

## API Reference

### TarlRuntime

- `__init__(policies: List[TarlPolicy])`
- `evaluate(context: Dict[str, Any]) -> TarlDecision`

### TarlGate

- `__init__(runtime: TarlRuntime, codex: CodexDeus)`
- `enforce(execution_context: Dict[str, Any]) -> TarlDecision`

### ExecutionKernel

- `__init__(governance, tarl_runtime, codex: CodexDeus)`
- `execute(action, context=None) -> Dict`

### GovernanceCore

- `add_policy(policy)`
- `audit(event)`
- `get_audit_log() -> List`

## Environment Variables

| Variable                   | Default | Description                 |
| -------------------------- | ------- | --------------------------- |
| `TARL_ENABLED`             | `1`     | Enable TARL security layer  |
| `CODEX_ESCALATION_ENABLED` | `1`     | Enable CodexDeus escalation |

## Common Commands

```bash

# Initialize system

python bootstrap.py

# Run tests

python test_tarl_integration.py

# Fuzz policies

python -m tarl.fuzz.fuzz_tarl

# Run with logging

PYTHONPATH=. python -c "from bootstrap import main; main()"
```

## Support and Documentation

- Full Documentation: `TARL_IMPLEMENTATION.md`
- Technical Docs: `TARL_TECHNICAL_DOCUMENTATION.md`
- Usage Scenarios: `TARL_USAGE_SCENARIOS.md`
- Code Examples: `TARL_CODE_EXAMPLES.md`
