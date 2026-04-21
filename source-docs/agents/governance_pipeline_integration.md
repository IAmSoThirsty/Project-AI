# Agent-Governance Pipeline Integration Guide

**Document:** How AI Agents Integrate with CognitionKernel Governance  
**Version:** 1.0.0  
**Created:** 2025-01-26  

---

## 📋 Overview

This guide explains how the four core AI agents (OversightAgent, ValidatorAgent, ExplainabilityAgent, PlannerAgent) integrate with the Project-AI governance pipeline, specifically the **CognitionKernel** and **Triumvirate** systems.

---

## 🏗️ Governance Architecture

### Three-Tier Platform Model

```
┌─────────────────────────────────────────────────────────┐
│ TIER 1: GOVERNANCE (Sovereign Authority)               │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │        CognitionKernel (Central Hub)             │  │
│  │  - Process all executions                        │  │
│  │  - Enforce governance policies                   │  │
│  │  - Track execution context                       │  │
│  └───────────────┬──────────────────────────────────┘  │
│                  │                                      │
│  ┌───────────────▼──────────────────────────────────┐  │
│  │           Triumvirate Council                    │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │  │
│  │  │  FourLaws   │ │ BlackVault  │ │  Identity  │ │  │
│  │  │  Guardian   │ │  Guardian   │ │  Guardian  │ │  │
│  │  └─────────────┘ └─────────────┘ └────────────┘ │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ TIER 2: CAPABILITY (Agent Layer)                       │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  Oversight   │  │  Validator   │  │Explainability│ │
│  │    Agent     │  │    Agent     │  │    Agent    │  │
│  └──────────────┘  └──────────────┘  └─────────────┘  │
│                                                         │
│  ALL route through KernelRoutedAgent base class        │
└─────────────────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────────────┐
│ TIER 3: EXECUTION (Tools & Plugins)                    │
│  - Execute validated actions                            │
│  - Report results back to Tier 2                        │
└─────────────────────────────────────────────────────────┘
```

---

## 🔄 Governance Flow

### Complete Execution Flow

```
1. Agent Method Call
   agent.some_action(args)
   
2. KernelRoutedAgent._execute_through_kernel()
   ├─ Wrap action in metadata
   ├─ Set risk level
   └─ Set approval requirements
   
3. CognitionKernel.process()
   ├─ Create ExecutionContext
   ├─ Assign execution ID
   ├─ Set timestamp
   └─ Route to governance
   
4. Triumvirate.review_action()
   ├─ FourLaws Guardian validates safety
   ├─ BlackVault Guardian checks forbidden content
   └─ Identity Guardian validates mutations
   
5. Consensus Decision
   ├─ If all approve → APPROVED
   └─ If any blocks → BLOCKED
   
6. Execution (if approved)
   ├─ Call action callable
   ├─ Capture result
   └─ Handle errors
   
7. Post-Processing
   ├─ Log to Memory
   ├─ Trigger Reflection
   ├─ Update audit trail
   └─ Return ExecutionResult
   
8. Unwrap Result
   ├─ If success → return result
   └─ If blocked → raise PermissionError
```

---

## 📦 KernelRoutedAgent Base Class

### Inheritance Hierarchy

```python
# src/app/core/kernel_integration.py

class KernelRoutedAgent:
    """Base class for agents that route through CognitionKernel."""
    
    def __init__(
        self,
        kernel: CognitionKernel | None = None,
        execution_type: ExecutionType = ExecutionType.AGENT_ACTION,
        default_risk_level: str = "low",
    ):
        self.kernel = kernel or get_global_kernel()
        self.execution_type = execution_type
        self.default_risk_level = default_risk_level
    
    def _execute_through_kernel(
        self,
        action: Callable,
        action_name: str,
        action_args: tuple = (),
        action_kwargs: dict | None = None,
        requires_approval: bool = False,
        risk_level: str | None = None,
        user_id: str | None = None,
        metadata: dict | None = None,
    ) -> Any:
        """Route action through CognitionKernel."""
        # Route to kernel.process()
        result = self.kernel.process(
            action=action,
            action_name=action_name,
            execution_type=self.execution_type,
            action_args=action_args,
            action_kwargs=action_kwargs,
            user_id=user_id,
            requires_approval=requires_approval,
            risk_level=risk_level or self.default_risk_level,
            metadata=metadata or {},
        )
        
        # Unwrap ExecutionResult
        if result.success:
            return result.result
        else:
            if result.blocked_reason:
                raise PermissionError(f"Blocked: {result.blocked_reason}")
            raise RuntimeError(result.error or "Execution failed")
```

### Agent Implementation Pattern

```python
# src/app/agents/oversight.py

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

class OversightAgent(KernelRoutedAgent):
    """Oversight agent with kernel integration."""
    
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        # Initialize base class (REQUIRED)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",
        )
        
        # Agent-specific state
        self.enabled = False
        self.monitors = {}
    
    # Future implementation:
    def monitor_system_health(self, components: list[str]) -> dict:
        """Monitor system health (routed through kernel)."""
        return self._execute_through_kernel(
            action=self._do_monitor_health,
            action_name="OversightAgent.monitor_system_health",
            action_args=(components,),
            requires_approval=False,  # Low-risk monitoring
            risk_level="low",
            metadata={"components": components},
        )
    
    def _do_monitor_health(self, components: list[str]) -> dict:
        """Implementation logic (NOT routed)."""
        # Actual monitoring logic here
        return {"status": "healthy", "components": components}
```

---

## 🛡️ Triumvirate Integration

### Three Guardian System

#### 1. FourLaws Guardian

**Purpose:** Validate actions against Asimov's Laws

```python
# In Triumvirate.review_action()

# FourLaws Guardian vote
from app.core.ai_systems import [[src/app/core/ai_systems.py]]

four_laws = FourLaws()
is_allowed, reason = four_laws.validate_action(
    action=action_name,
    context=metadata,
)

if not is_allowed:
    return {
        "guardian": "FourLaws",
        "approved": False,
        "reason": reason,
        "violated_law": four_laws.get_violated_law(),
    }
```

**Agent Impact:**
- **OversightAgent:** Must not harm humans through inaction
- **ValidatorAgent:** Must not allow harmful inputs
- **ExplainabilityAgent:** Must explain without deception
- **PlannerAgent:** N/A (stub, no operations)

#### 2. BlackVault Guardian

**Purpose:** Check against forbidden content

```python
# In Triumvirate.review_action()

# BlackVault Guardian vote
from app.core.ai_systems import LearningRequestManager

learning_manager = LearningRequestManager()
content_hash = hashlib.sha256(str(action_args).encode()).hexdigest()

if content_hash in learning_manager.black_vault:
    return {
        "guardian": "BlackVault",
        "approved": False,
        "reason": "Content is in Black Vault (previously denied)",
        "content_hash": content_hash,
    }
```

**Agent Impact:**
- **OversightAgent:** Must not monitor forbidden patterns
- **ValidatorAgent:** Must block Black Vault content
- **ExplainabilityAgent:** Must not explain forbidden content
- **PlannerAgent:** N/A

#### 3. Identity Guardian

**Purpose:** Validate identity mutations

```python
# In Triumvirate.review_action()

# Identity Guardian vote
from app.core.identity import IdentitySystem
from app.core.cognition_kernel import MutationIntent

identity = IdentitySystem()

if metadata.get("mutation_intent") == MutationIntent.CORE.value:
    # CORE mutations require unanimous consensus
    return {
        "guardian": "Identity",
        "approved": False,  # Escalate to full consensus
        "reason": "CORE mutation requires Triumvirate consensus",
        "escalation_required": True,
    }

# Validate genesis hash integrity
if not identity.verify_genesis_hash():
    return {
        "guardian": "Identity",
        "approved": False,
        "reason": "Genesis hash integrity violation",
    }
```

**Agent Impact:**
- **OversightAgent:** Must not allow identity tampering
- **ValidatorAgent:** Must validate identity mutations
- **ExplainabilityAgent:** Must not expose identity internals
- **PlannerAgent:** N/A

### Consensus Algorithm

```python
# In Triumvirate.review_action()

def review_action(self, action_context: dict) -> dict:
    """Triumvirate consensus review."""
    votes = {
        "FourLaws": self._four_laws_vote(action_context),
        "BlackVault": self._black_vault_vote(action_context),
        "Identity": self._identity_vote(action_context),
    }
    
    # Check for consensus (all must approve)
    all_approved = all(vote["approved"] for vote in votes.values())
    
    if all_approved:
        return {
            "consensus": True,
            "votes": votes,
            "decision": "APPROVED",
        }
    else:
        # Find blocking guardians
        blockers = [
            name for name, vote in votes.items()
            if not vote["approved"]
        ]
        
        return {
            "consensus": False,
            "votes": votes,
            "decision": "BLOCKED",
            "blocked_by": blockers,
            "block_reason": "; ".join([
                votes[b]["reason"] for b in blockers
            ]),
        }
```

---

## 🎯 Agent-Specific Integration

### OversightAgent → Governance

**Role:** Monitor compliance with governance policies

```python
class OversightAgent(KernelRoutedAgent):
    def monitor_compliance(self, policies: list[str]) -> dict:
        """Monitor compliance (routes through governance)."""
        return self._execute_through_kernel(
            action=self._check_compliance,
            action_name="OversightAgent.monitor_compliance",
            action_args=(policies,),
            requires_approval=False,  # Monitoring is low-risk
            risk_level="low",
            metadata={
                "policies": policies,
                "check_type": "compliance",
            },
        )
    
    def _check_compliance(self, policies: list[str]) -> dict:
        """Implementation: Check compliance with policies."""
        # Access governance state through kernel
        kernel_state = self.kernel.get_execution_history()
        
        violations = []
        for policy in policies:
            if not self._validate_policy(policy, kernel_state):
                violations.append(policy)
        
        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "policies_checked": policies,
        }
```

**Governance Impact:**
- Monitoring actions logged to audit trail
- Can trigger Triumvirate escalation if violations detected
- Reports integrated into Reflection system

### ValidatorAgent → Governance

**Role:** Pre-execution validation to prevent violations

```python
class ValidatorAgent(KernelRoutedAgent):
    def validate_against_black_vault(self, content: str) -> dict:
        """Validate content against Black Vault (routes through governance)."""
        return self._execute_through_kernel(
            action=self._check_black_vault,
            action_name="ValidatorAgent.validate_against_black_vault",
            action_args=(content,),
            requires_approval=False,  # Validation is low-risk
            risk_level="medium",  # Black Vault checks are medium risk
            metadata={
                "content_length": len(content),
                "check_type": "black_vault",
            },
        )
    
    def _check_black_vault(self, content: str) -> dict:
        """Implementation: Check Black Vault."""
        import hashlib
        from app.core.ai_systems import LearningRequestManager
        
        manager = LearningRequestManager()
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        
        is_forbidden = content_hash in manager.black_vault
        
        if is_forbidden:
            # This action will be logged but not blocked at validator level
            # Triumvirate will block during execution phase
            return {
                "valid": False,
                "forbidden": True,
                "content_hash": content_hash,
                "reason": "Content in Black Vault",
            }
        
        return {"valid": True, "forbidden": False}
```

**Governance Impact:**
- Validates inputs before they reach Triumvirate
- Can block actions at validation layer (enforcement authority)
- Prevents invalid requests from consuming governance resources

### ExplainabilityAgent → Governance

**Role:** Explain governance decisions to users

```python
class ExplainabilityAgent(KernelRoutedAgent):
    def explain_governance_decision(self, decision_id: str) -> dict:
        """Explain Triumvirate decision (routes through governance)."""
        return self._execute_through_kernel(
            action=self._generate_governance_explanation,
            action_name="ExplainabilityAgent.explain_governance_decision",
            action_args=(decision_id,),
            requires_approval=False,  # Explanation is low-risk
            risk_level="low",
            metadata={
                "decision_id": decision_id,
                "explanation_type": "governance",
            },
        )
    
    def _generate_governance_explanation(self, decision_id: str) -> dict:
        """Implementation: Generate governance explanation."""
        # Access Triumvirate decision through kernel
        from app.core.triumvirate import Triumvirate
        
        triumvirate = Triumvirate()
        decision = triumvirate.get_decision(decision_id)
        
        # Format explanation
        explanation_lines = [
            f"Governance Decision: {decision['action']}",
            f"Result: {decision['decision']}",
            "",
            "Guardian Votes:",
        ]
        
        for guardian, vote in decision["votes"].items():
            status = "✅ APPROVED" if vote["approved"] else "❌ BLOCKED"
            explanation_lines.append(f"  {guardian}: {status}")
            explanation_lines.append(f"    Reason: {vote['reason']}")
        
        if not decision["consensus"]:
            explanation_lines.append("")
            explanation_lines.append(f"Blocked By: {', '.join(decision['blocked_by'])}")
            explanation_lines.append(f"Block Reason: {decision['block_reason']}")
        
        return {
            "decision_id": decision_id,
            "explanation": "\n".join(explanation_lines),
            "consensus": decision["consensus"],
        }
```

**Governance Impact:**
- Provides transparency into governance decisions
- Does not affect governance flow (advisory authority)
- Logged for auditability and reflection

### PlannerAgent → Governance

**Status:** Legacy stub, bypasses governance (justified)

```python
# GOVERNANCE BYPASS: Legacy stub agent with no AI operations
# Justification: Simple in-memory task queue with no AI calls
# Risk: Minimal - no AI, no I/O, no security implications
# Alternative: Use planner_agent.py for governed task planning

class PlannerAgent:
    """Legacy stub (no kernel integration)."""
    
    def __init__(self) -> None:
        self.enabled = False
        self.tasks = {}
    
    # No methods - stub only
```

**Governance Impact:** None (bypassed)

**Migration:** Use `planner_agent.py` (PlannerAgentGoverned) for production

---

## 🔍 Governance Metadata

### ExecutionContext Structure

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ExecutionContext:
    """Context for execution routed through kernel."""
    
    execution_id: str  # Unique ID (e.g., "exec_abc123")
    action_name: str   # Human-readable name (e.g., "OversightAgent.monitor_compliance")
    execution_type: ExecutionType  # AGENT_ACTION, TOOL_INVOCATION, etc.
    timestamp: datetime
    user_id: str | None
    
    # Agent metadata
    agent_class: str  # e.g., "OversightAgent"
    requires_approval: bool
    risk_level: str  # "low", "medium", "high", "critical"
    
    # Triumvirate review
    triumvirate_decision: dict | None
    consensus: bool | None
    blocked_by: list[str] | None
    block_reason: str | None
    
    # Execution result
    status: ExecutionStatus  # PENDING, APPROVED, EXECUTING, COMPLETED, FAILED, BLOCKED
    result: Any | None
    error: str | None
    
    # Tracking
    parent_execution_id: str | None  # For nested executions
    child_executions: list[str]  # List of child execution IDs
    
    # Timing
    start_time: datetime
    end_time: datetime | None
    duration_ms: float | None
```

### Agent-Specific Metadata

```python
# OversightAgent
metadata = {
    "agent_class": "OversightAgent",
    "action_name": "monitor_system_health",
    "components": ["kernel", "agents", "memory"],
    "check_type": "health",
    "requires_approval": False,
    "risk_level": "low",
}

# ValidatorAgent
metadata = {
    "agent_class": "ValidatorAgent",
    "action_name": "validate_sql_injection",
    "query_length": 256,
    "check_type": "security",
    "requires_approval": True,  # Security checks may require approval
    "risk_level": "high",
}

# ExplainabilityAgent
metadata = {
    "agent_class": "ExplainabilityAgent",
    "action_name": "explain_decision",
    "decision_id": "dec_123",
    "explanation_type": "detailed",
    "requires_approval": False,
    "risk_level": "low",
}
```

---

## 📊 Governance Logging

### Audit Trail Structure

```json
{
  "execution_id": "exec_abc123",
  "timestamp": "2025-01-26T10:30:00Z",
  "agent": "ValidatorAgent",
  "action": "validate_input",
  "user_id": "user_456",
  "governance_review": {
    "triumvirate_decision": {
      "consensus": true,
      "votes": {
        "FourLaws": {"approved": true, "reason": "No safety violations"},
        "BlackVault": {"approved": true, "reason": "No forbidden content"},
        "Identity": {"approved": true, "reason": "No identity mutations"}
      }
    }
  },
  "execution_result": {
    "status": "completed",
    "success": true,
    "duration_ms": 45,
    "result": {"valid": true}
  },
  "metadata": {
    "risk_level": "low",
    "requires_approval": false,
    "validation_type": "type_check"
  }
}
```

### Query Audit Trail

```python
from app.core.memory_expansion import MemoryExpansionSystem

memory = MemoryExpansionSystem()

# Query all ValidatorAgent actions
validator_logs = memory.query_knowledge(
    category="audit_logs",
    filter_fn=lambda log: log["agent"] == "ValidatorAgent"
)

# Query blocked actions
blocked_logs = memory.query_knowledge(
    category="audit_logs",
    filter_fn=lambda log: (
        log["execution_result"]["status"] == "blocked"
    )
)

# Query high-risk actions
high_risk_logs = memory.query_knowledge(
    category="audit_logs",
    filter_fn=lambda log: (
        log["metadata"]["risk_level"] in ["high", "critical"]
    )
)
```

---

## 🧪 Testing Governance Integration

### Test Pattern

```python
import pytest
from app.core.cognition_kernel import CognitionKernel
from app.agents import ValidatorAgent

def test_validator_governance_integration():
    """Test ValidatorAgent routes through governance."""
    kernel = CognitionKernel()
    validator = ValidatorAgent(kernel=kernel)
    
    # Mock action
    def mock_validation(data: dict) -> dict:
        return {"valid": True}
    
    # Execute through kernel
    result = validator._execute_through_kernel(
        action=mock_validation,
        action_name="ValidatorAgent.test",
        action_args=({"test": "data"},),
        risk_level="low",
    )
    
    # Verify result
    assert result["valid"] == True
    
    # Verify governance logging
    history = kernel.get_execution_history()
    assert len(history) > 0
    assert history[-1]["action_name"] == "ValidatorAgent.test"
    assert history[-1]["status"] == "completed"

def test_validator_blocked_by_governance():
    """Test ValidatorAgent action blocked by Triumvirate."""
    kernel = CognitionKernel()
    validator = ValidatorAgent(kernel=kernel)
    
    # Mock high-risk action that violates FourLaws
    def dangerous_action() -> dict:
        return {"action": "harm_human"}
    
    # Attempt execution (should be blocked)
    with pytest.raises(PermissionError) as exc_info:
        validator._execute_through_kernel(
            action=dangerous_action,
            action_name="ValidatorAgent.dangerous_action",
            risk_level="critical",
            requires_approval=True,
            metadata={"endangers_humanity": True},
        )
    
    # Verify block reason
    assert "[[src/app/core/ai_systems.py]]" in str(exc_info.value)
    assert "blocked" in str(exc_info.value).lower()
```

---

## 🎯 Best Practices

### ✅ DO

1. **Always route through kernel** (except justified bypasses)
2. **Set appropriate risk levels** (low/medium/high/critical)
3. **Provide descriptive action names** (e.g., "AgentName.method_name")
4. **Include relevant metadata** (user_id, context, parameters)
5. **Handle PermissionError** (governance blocks)
6. **Handle RuntimeError** (execution failures)
7. **Log all agent actions** (automatic via kernel)
8. **Test governance integration** (unit + integration tests)

### ❌ DON'T

1. **Don't bypass kernel** (unless documented justification)
2. **Don't ignore governance blocks** (handle PermissionError)
3. **Don't use generic action names** ("action", "execute")
4. **Don't omit risk levels** (defaults may be incorrect)
5. **Don't skip metadata** (impacts governance decisions)
6. **Don't catch PermissionError silently** (governance violations must surface)
7. **Don't disable logging** (audit trail required)
8. **Don't test agents in isolation** (always test with kernel)

---

## 🔗 Related Documentation

- [CognitionKernel Architecture](../core/cognition_kernel.md)
- [Triumvirate System](../core/triumvirate.md)
- [FourLaws Implementation](../core/four_laws.md)
- [Black Vault](../core/black_vault.md)
- [Identity System](../core/identity.md)
- [Memory Expansion](../core/memory_expansion.md)
- [Reflection System](../core/reflection.md)
- [Platform Tiers](../core/platform_tiers.md)

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
