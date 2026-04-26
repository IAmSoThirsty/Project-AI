# Agent API Quick Reference

**Document:** Quick API Reference for Core AI Agents  
**Version:** 1.0.0  
**Created:** 2025-01-26  

---

## 📚 Quick Navigation

| Agent | Status | Risk | Authority | Lines |
|-------|--------|------|-----------|-------|
| [OversightAgent](#oversightagent) | Stub | Medium | Advisory | 43 |
| [ValidatorAgent](#validatoragent) | Stub | Low | Enforcement | 43 |
| [ExplainabilityAgent](#explainabilityagent) | Stub | Low | Advisory | 43 |
| [PlannerAgent](#planneragent) | Legacy | Minimal | None | 32 |

---

## OversightAgent

**Module:** `src/app/agents/oversight.py`  
**Purpose:** System monitoring and compliance  
**Status:** Stub (Ready for Implementation)  

### Constructor

```python
from app.agents import OversightAgent
from app.core.cognition_kernel import CognitionKernel

agent = OversightAgent(kernel: CognitionKernel | None = None)
```

### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | `bool` | `False` | Operational status |
| `monitors` | `dict` | `{}` | Monitor registry |
| `kernel` | `CognitionKernel \| None` | `None` | Kernel instance |
| `execution_type` | `ExecutionType` | `AGENT_ACTION` | Classification |
| `default_risk_level` | `str` | `"medium"` | Default risk |

### Future Methods (Planned)

```python
# Monitor system health
result = agent.monitor_system_health(
    components: list[str]
) -> dict[str, Any]

# Monitor compliance
result = agent.monitor_compliance(
    policies: list[str]
) -> dict[str, Any]

# Validate identity mutations
result = agent.validate_identity_mutations(
    mutation_log: list[dict]
) -> dict[str, Any]
```

### Integration Pattern

```python
from app.core.cognition_kernel import CognitionKernel

kernel = CognitionKernel()
oversight = OversightAgent(kernel=kernel)

# Future: Monitor execution
# result = oversight.monitor_system_health(["kernel", "agents"])
```

### Common Use Cases

1. **System Health Monitoring**
2. **Compliance Validation**
3. **Anomaly Detection**
4. **Identity Drift Monitoring**
5. **Governance Audit Trail**

---

## ValidatorAgent

**Module:** `src/app/agents/validator.py`  
**Purpose:** Input validation and data integrity  
**Status:** Stub (Ready for Implementation)  

### Constructor

```python
from app.agents import ValidatorAgent
from app.core.cognition_kernel import CognitionKernel

agent = ValidatorAgent(kernel: CognitionKernel | None = None)
```

### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | `bool` | `False` | Operational status |
| `validators` | `dict` | `{}` | Validator registry |
| `kernel` | `CognitionKernel \| None` | `None` | Kernel instance |
| `execution_type` | `ExecutionType` | `AGENT_ACTION` | Classification |
| `default_risk_level` | `str` | `"low"` | Default risk |

### Future Methods (Planned)

```python
# Type validation
result = agent.validate_types(
    data: dict,
    schema: dict,
) -> dict[str, Any]

# Security validation
result = agent.validate_sql_injection(
    query: str,
) -> dict[str, Any]

result = agent.validate_xss(
    input_text: str,
) -> dict[str, Any]

# Black Vault validation
result = agent.validate_against_black_vault(
    content: str,
) -> dict[str, Any]

# Identity mutation validation
result = agent.validate_identity_mutation(
    mutation: dict,
    mutation_intent: str,
) -> dict[str, Any]

# Custom validator
agent.register_validator(
    name: str,
    validator_fn: Callable,
    risk_level: str = "low",
) -> None

result = agent.validate_with(
    validator_name: str,
    data: Any,
) -> dict[str, Any]

# Batch validation
result = agent.validate_batch(
    data_list: list[dict],
    schema: dict,
) -> list[dict]
```

### Integration Pattern

```python
from app.core.cognition_kernel import CognitionKernel

kernel = CognitionKernel()
validator = ValidatorAgent(kernel=kernel)

# Future: Validate user input
user_data = {
    "username": "alice",
    "email": "alice@example.com",
    "age": 30,
}

schema = {
    "username": str,
    "email": str,
    "age": int,
}

result = validator.validate_types(user_data, schema)

if result["valid"]:
    # Proceed with validated data
    process_user(result["validated_data"])
else:
    # Handle validation errors
    return {"error": result["errors"]}
```

### Common Use Cases

1. **Type Validation** (schema-based)
2. **Security Validation** (SQL injection, XSS)
3. **Black Vault Checks** (forbidden content)
4. **Identity Mutation Validation**
5. **Batch Processing**
6. **Custom Validator Registration**

---

## ExplainabilityAgent

**Module:** `src/app/agents/explainability.py`  
**Purpose:** Decision transparency and reasoning  
**Status:** Stub (Ready for Implementation)  

### Constructor

```python
from app.agents import ExplainabilityAgent
from app.core.cognition_kernel import CognitionKernel

agent = ExplainabilityAgent(kernel: CognitionKernel | None = None)
```

### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | `bool` | `False` | Operational status |
| `explanations` | `dict` | `{}` | Explanation templates |
| `kernel` | `CognitionKernel \| None` | `None` | Kernel instance |
| `execution_type` | `ExecutionType` | `AGENT_ACTION` | Classification |
| `default_risk_level` | `str` | `"low"` | Default risk |

### Future Methods (Planned)

```python
# Basic decision explanation
result = agent.explain_decision(
    decision: dict[str, Any],
    explanation_type: str = "detailed",  # "brief" or "detailed"
) -> dict[str, Any]

# Governance decision explanation
result = agent.explain_governance_decision(
    decision_id: str,
) -> dict[str, Any]

# Law violation explanation
result = agent.explain_law_violation(
    action: dict,
    violation: dict,
) -> dict[str, Any]

# Reflection explanation
result = agent.explain_reflection(
    reflection_id: str,
) -> dict[str, Any]

# Historical context explanation
result = agent.explain_with_history(
    decision: dict,
    context_window: int = 10,
) -> dict[str, Any]

# Template management
agent.register_template(
    name: str,
    template: str,
    variables: list[str],
) -> None

result = agent.explain_with_template(
    template_name: str,
    values: dict[str, Any],
) -> dict[str, Any]
```

### Integration Pattern

```python
from app.core.cognition_kernel import CognitionKernel

kernel = CognitionKernel()
explainer = ExplainabilityAgent(kernel=kernel)

# Future: Explain decision
decision = {
    "id": "dec_123",
    "action": "Delete user data",
    "outcome": "blocked",
    "reasoning": [
        "Action requires user consent",
        "No consent record found",
    ],
    "confidence": 0.95,
}

explanation = explainer.explain_decision(
    decision,
    explanation_type="detailed"
)

print(explanation["explanation"])
```

### Common Use Cases

1. **Decision Explanation** (brief, detailed)
2. **Governance Transparency** (Triumvirate decisions)
3. **Law Violation Reporting**
4. **Reflection Analysis**
5. **Historical Context**
6. **Template-Based Explanations**
7. **Sensitive Data Sanitization**

---

## PlannerAgent

**Module:** `src/app/agents/planner.py`  
**Purpose:** Task planning and orchestration (Legacy Stub)  
**Status:** Superseded by `planner_agent.py`  

### Constructor

```python
from app.agents import PlannerAgent

agent = PlannerAgent()  # No kernel (bypassed)
```

### Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | `bool` | `False` | Always disabled |
| `tasks` | `dict` | `{}` | Empty task storage |

### Governance Bypass

```python
# GOVERNANCE BYPASS: Legacy stub agent with no AI operations
# Justification: Simple in-memory task queue with no AI calls
# Risk: Minimal - no AI, no I/O, no security implications
# Alternative: Use planner_agent.py for governed task planning
```

### Migration Path

```python
# OLD (Legacy Stub)
from app.agents.planner import PlannerAgent
planner = PlannerAgent()

# NEW (Governed Version)
from app.agents.planner_agent import PlannerAgentGoverned
from app.core.cognition_kernel import CognitionKernel

kernel = CognitionKernel()
planner = PlannerAgentGoverned(kernel=kernel)

# Use governed planner for actual planning
result = planner.plan_task(
    task_description="Build ML pipeline",
    constraints=["use existing tools", "under 5 minutes"],
)
```

### Common Use Cases

**None** - Legacy stub has no operations. Use `planner_agent.py` instead.

---

## 🔄 Kernel Integration Pattern

All agents (except PlannerAgent stub) follow this pattern:

```python
from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

class MyAgent(KernelRoutedAgent):
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",  # or "medium", "high"
        )
        
        # Agent-specific initialization
        self.enabled = False  # Stub mode
        self.state = {}
    
    def some_action(self, args) -> dict[str, Any]:
        """Public method that routes through kernel."""
        return self._execute_through_kernel(
            action=self._do_some_action,
            action_name="MyAgent.some_action",
            action_args=(args,),
            requires_approval=False,  # or True for high-risk
            risk_level="low",  # override default if needed
            metadata={"key": "value"},
        )
    
    def _do_some_action(self, args) -> dict[str, Any]:
        """Implementation logic (private method)."""
        # Actual implementation here
        return {"success": True, "result": data}
```

---

## 🎯 Common Patterns

### Pattern 1: Agent Initialization

```python
# Method 1: Explicit kernel
kernel = CognitionKernel()
agent = SomeAgent(kernel=kernel)

# Method 2: Global kernel (recommended)
from app.core.kernel_integration import set_global_kernel

set_global_kernel(kernel)
agent = SomeAgent()  # Uses global kernel
```

### Pattern 2: Error Handling

```python
try:
    result = agent.some_action(args)
except PermissionError as e:
    # Blocked by governance
    print(f"Action blocked: {e}")
except RuntimeError as e:
    # Execution failed
    print(f"Execution failed: {e}")
```

### Pattern 3: Validation Pipeline

```python
def validate_and_execute(data: dict) -> dict:
    """Validate then execute."""
    validator = ValidatorAgent()
    
    # Step 1: Type validation
    type_result = validator.validate_types(data, schema)
    if not type_result["valid"]:
        return {"error": "Type validation failed"}
    
    # Step 2: Security validation
    security_result = validator.validate_security(data)
    if not security_result["valid"]:
        return {"error": "Security violation"}
    
    # Step 3: Execute
    return execute_action(data)
```

### Pattern 4: Monitor and Explain

```python
def monitored_execution(action: dict) -> dict:
    """Execute with monitoring and explanation."""
    oversight = OversightAgent()
    explainer = ExplainabilityAgent()
    
    # Pre-flight check
    pre_check = oversight.pre_flight_check(action)
    if not pre_check["ready"]:
        return {"error": "Pre-flight failed"}
    
    # Execute
    result = execute_action(action)
    
    # Post-execution monitoring
    post_check = oversight.post_execution_check(result)
    
    # Generate explanation
    explanation = explainer.explain_decision(result)
    
    return {
        "result": result,
        "monitoring": post_check,
        "explanation": explanation,
    }
```

---

## 🔗 Quick Links

### Documentation
- [OversightAgent Full Docs](oversight_agent.md)
- [ValidatorAgent Full Docs](validator_agent.md)
- [ExplainabilityAgent Full Docs](explainability_agent.md)
- [PlannerAgent Full Docs](planner_agent.md)
- [Agent Interaction Diagram](agent_interaction_diagram.md)

### Core Systems
- [CognitionKernel](../core/cognition_kernel.md)
- [KernelRoutedAgent](../core/kernel_integration.md)
- [Platform Tiers](../core/platform_tiers.md)
- [Triumvirate](../core/triumvirate.md)
- [FourLaws](../core/four_laws.md)

### Governance
- [Governance Pipeline](../governance/governance_pipeline.md)
- [Agent Classification](../agents/AGENT_CLASSIFICATION.md)
- [Bypass Policies](../governance/bypass_policies.md)

---

## 📊 Comparison Matrix

| Feature | Oversight | Validator | Explainability | Planner |
|---------|-----------|-----------|----------------|---------|
| **Kernel Integration** | ✅ Yes | ✅ Yes | ✅ Yes | ❌ Bypassed |
| **Governance Status** | ✅ Governed | ✅ Governed | ✅ Governed | ⚠️ Bypassed |
| **Risk Level** | Medium | Low | Low | Minimal |
| **Authority** | Advisory | Enforcement | Advisory | None |
| **Can Block Actions** | ❌ No | ✅ Yes | ❌ No | ❌ No |
| **AI Integration** | ❌ None | ❌ None | ❌ None | ❌ None |
| **Implementation Status** | 🚧 Stub | 🚧 Stub | 🚧 Stub | 🚫 Legacy |
| **Line Count** | 43 | 43 | 43 | 32 |
| **Test Coverage** | 100% (stub) | 100% (stub) | 100% (stub) | 100% (stub) |

---

## 🚀 Quick Start

### 1. Initialize Kernel

```python
from app.core.cognition_kernel import CognitionKernel
from app.core.kernel_integration import set_global_kernel

kernel = CognitionKernel()
set_global_kernel(kernel)
```

### 2. Create Agents

```python
from app.agents import (
    OversightAgent,
    ValidatorAgent,
    ExplainabilityAgent,
)

oversight = OversightAgent()
validator = ValidatorAgent()
explainer = ExplainabilityAgent()
```

### 3. Use Agents

```python
# Future implementation:

# Validate input
validation = validator.validate_input(user_data, schema)

# Monitor execution
monitoring = oversight.monitor_execution(execution_id)

# Explain decision
explanation = explainer.explain_decision(decision)
```

---

## 💡 Tips and Best Practices

### ✅ DO

- Use global kernel pattern for consistency
- Route all actions through kernel
- Handle `PermissionError` for blocked actions
- Validate inputs before execution
- Generate explanations for user-facing decisions
- Monitor high-risk operations
- Log all agent interactions

### ❌ DON'T

- Don't bypass kernel routing (except justified cases)
- Don't ignore validation failures
- Don't expose sensitive data in explanations
- Don't create circular agent calls
- Don't use legacy PlannerAgent for new code
- Don't disable governance without justification
- Don't skip error handling

---

## 🔍 Debugging

### Check Agent Status

```python
agent = SomeAgent()
print(f"Enabled: {agent.enabled}")  # Should be False for stubs
print(f"Kernel: {agent.kernel}")    # Should not be None
print(f"Risk: {agent.default_risk_level}")
```

### Check Kernel Integration

```python
from app.core.kernel_integration import get_global_kernel

kernel = get_global_kernel()
if kernel is None:
    raise RuntimeError("Global kernel not set!")
```

### Test Agent Routing

```python
from app.core.cognition_kernel import ExecutionType

agent = SomeAgent(kernel=kernel)

# Verify execution type
assert agent.execution_type == ExecutionType.AGENT_ACTION

# Verify kernel routing method exists
assert hasattr(agent, "_execute_through_kernel")
```

---

## 📞 Support

**Questions or Issues?**

- Check full documentation: [agent_name]_agent.md
- Review governance pipeline: [governance_pipeline.md](../governance/governance_pipeline.md)
- See agent classification: [AGENT_CLASSIFICATION.md](../agents/AGENT_CLASSIFICATION.md)
- Contact: AI Systems Documentation Team

---

**Last Updated:** 2025-01-26  
**Version:** 1.0.0  
**Maintained By:** AI Systems Documentation Team  
**Next Review:** After agent implementation

---

## 📁 Source Code References

This documentation references the following source files:

- [[src/app/agents/explainability.py]]
- [[src/app/agents/oversight.py]]
- [[src/app/agents/planner_agent.py]]
- [[src/app/agents/validator.py]]

---

---

## 🔗 Relationship Maps

This component is documented in the following relationship maps:
- [[relationships/agents/AGENT_ORCHESTRATION.md|Agent Orchestration]]
- [[relationships/agents/PLANNING_HIERARCHIES.md|Planning Hierarchies]]
- [[relationships/agents/VALIDATION_CHAINS.md|Validation Chains]]

---

---

## 📚 Referenced In Relationship Maps

This implementation is referenced in:
- [[relationships/agents/AGENT_ORCHESTRATION.md|Agent Orchestration Architecture]]
- [[relationships/agents/PLANNING_HIERARCHIES.md|Planning Hierarchies]]
- [[relationships/agents/VALIDATION_CHAINS.md|Validation Chains]]

---
