# ExplainabilityAgent - Decision Transparency and Reasoning

**Module:** `src/app/agents/explainability.py`  
**Classification:** Core AI Agent (Governance-Routed)  
**Lines:** 43  
**Status:** Stub (Ready for Implementation)  
**Created:** 2025-01-26  

---

## 📋 Overview

### Purpose
The **ExplainabilityAgent** provides explanations for AI decisions, generates reasoning traces, and supports interpretability for user trust and debugging. It acts as a transparency layer that makes AI decision-making understandable to humans.

### Design Philosophy
All explanation operations route through `CognitionKernel`, ensuring transparent governance tracking. The agent operates as a **post-processing reporter** that translates complex AI decisions into human-understandable explanations, bridging the gap between machine logic and human comprehension.

### Current State
**Implementation Status:** Disabled stub with placeholder infrastructure

The agent is initialized with `enabled=False` and empty explanation storage (`self.explanations = {}`). This is a placeholder design that:
- Maintains API stability for dependent code
- Allows future implementation without breaking changes
- Provides clear integration points with CognitionKernel
- Defers compute-intensive explanation generation to future phases

---

## 🏗️ Architecture

### Class Hierarchy
```
KernelRoutedAgent (base)
    ↓
ExplainabilityAgent (inherits)
    ↓ routes through
CognitionKernel (governance hub)
```

### Inheritance Pattern
**Inherits from:** `KernelRoutedAgent` (defined in `app.core.kernel_integration`)

**Key Benefits:**
- Automatic kernel routing via `_execute_through_kernel()`
- Built-in execution type classification (`ExecutionType.AGENT_ACTION`)
- Standardized error handling with governance integration
- Thread-safe execution context tracking

### Risk Classification

**Default Risk Level:** `"low"` (Line 34)

**Rationale:**
- Explanation generation is typically **read-only**
- No mutations to system state
- No privileged operations
- Transparent operation with no side effects

**Exceptions (higher risk):**
- Explanations that reveal sensitive data (medium)
- Explanations of security decisions (medium)
- Explanations that expose model internals (low-medium)

### Integration Points

#### 1. CognitionKernel Routing (Lines 9-10, 29-34)
```python
from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

super().__init__(
    kernel=kernel,
    execution_type=ExecutionType.AGENT_ACTION,
    default_risk_level="low",  # Explanation generation is low risk
)
```

**Flow:**
1. Agent initialized with optional kernel instance
2. If no kernel provided, uses global kernel from `kernel_integration`
3. All explanation actions route through `_execute_through_kernel()`
4. Kernel applies governance, logging, and reflection
5. Results unwrapped from `ExecutionResult`

#### 2. Platform Tier Integration
**Tier:** Tier 2 (Capability Layer)  
**Role:** `ComponentRole.EXPLAINABILITY` (from `platform_tiers.py`)  
**Authority:** `AuthorityLevel.ADVISORY` (can explain, not enforce)

The ExplainabilityAgent operates as a **reporter** in the platform hierarchy:
- **Tier 1 (Governance):** CognitionKernel, Triumvirate, FourLaws
- **Tier 2 (Capability):** **ExplainabilityAgent** ← (explains Tier 1 & 3)
- **Tier 3 (Execution):** Tools, plugins, external APIs

Authority flows downward, explanations flow upward (reporting).

#### 3. Module Dependencies
```python
# Direct imports
from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

# Indirect (via kernel)
# - app.core.reflection (reflection analysis)
# - app.core.memory_expansion (decision history)
# - app.core.triumvirate (governance explanations)
# - app.core.ai_systems.FourLaws (law violation explanations)
```

---

## 📚 API Reference

### Class: `ExplainabilityAgent`

```python
class ExplainabilityAgent(KernelRoutedAgent):
    """Explains AI decisions and provides reasoning transparency.
    
    All explanation generation routes through CognitionKernel.
    """
```

#### Constructor

```python
def __init__(self, kernel: CognitionKernel | None = None) -> None:
    """Initialize the explainability agent with explanation models.
    
    Args:
        kernel: CognitionKernel instance for routing operations.
                If None, uses global kernel from kernel_integration.
                
    Attributes:
        enabled (bool): Agent active status. Default: False (stub mode)
        explanations (dict): Storage for explanation templates. Default: {}
        
    Side Effects:
        - Logs warning if kernel is None (governance bypass)
        - Registers agent with platform tier registry
    """
```

**Usage Example:**
```python
from app.core.cognition_kernel import CognitionKernel
from app.agents import ExplainabilityAgent

# With explicit kernel
kernel = CognitionKernel()
agent = ExplainabilityAgent(kernel=kernel)

# With global kernel (set in main.py)
from app.core.kernel_integration import set_global_kernel
set_global_kernel(kernel)
agent = ExplainabilityAgent()  # Uses global kernel
```

#### Instance Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | `bool` | `False` | Agent operational status (stub mode) |
| `explanations` | `dict` | `{}` | Explanation template registry (empty in stub) |
| `kernel` | `CognitionKernel \| None` | `None` | Kernel instance for routing |
| `execution_type` | `ExecutionType` | `AGENT_ACTION` | Classification for governance |
| `default_risk_level` | `str` | `"low"` | Risk level for explanation actions |

---

## 🔗 Integration Points

### 1. CognitionKernel Integration

**Pattern:** All agent actions route through `_execute_through_kernel()`

```python
# Future implementation example
def explain_decision(
    self,
    decision: dict[str, Any],
    explanation_type: str = "detailed",
) -> dict[str, Any]:
    """Generate explanation for AI decision."""
    return self._execute_through_kernel(
        action=self._do_explain_decision,
        action_name="ExplainabilityAgent.explain_decision",
        action_args=(decision, explanation_type),
        requires_approval=False,  # Low-risk explanation
        risk_level="low",
        metadata={
            "decision_id": decision.get("id"),
            "explanation_type": explanation_type,
        },
    )

def _do_explain_decision(
    self,
    decision: dict[str, Any],
    explanation_type: str,
) -> dict[str, Any]:
    """Implementation of decision explanation logic."""
    # Extract decision context
    action = decision.get("action")
    outcome = decision.get("outcome")
    reasoning = decision.get("reasoning", [])
    
    # Generate explanation based on type
    if explanation_type == "brief":
        explanation = f"Decision: {action}. Result: {outcome}."
    elif explanation_type == "detailed":
        explanation = self._generate_detailed_explanation(
            action, outcome, reasoning
        )
    else:
        explanation = f"Unknown explanation type: {explanation_type}"
    
    return {
        "decision_id": decision.get("id"),
        "explanation": explanation,
        "confidence": decision.get("confidence", 0.0),
        "explanation_type": explanation_type,
    }

def _generate_detailed_explanation(
    self,
    action: str,
    outcome: str,
    reasoning: list[str],
) -> str:
    """Generate detailed human-readable explanation."""
    lines = [
        f"Action Taken: {action}",
        f"Outcome: {outcome}",
        "",
        "Reasoning Chain:",
    ]
    
    for i, step in enumerate(reasoning, 1):
        lines.append(f"  {i}. {step}")
    
    return "\n".join(lines)
```

**Kernel Behavior:**
1. Receives action via `_execute_through_kernel()`
2. Creates `ExecutionContext` with metadata
3. Routes through governance pipeline (Triumvirate, [[src/app/core/ai_systems.py]])
4. If approved: executes `_do_explain_decision()`
5. If blocked: raises `PermissionError` with reason
6. Logs to memory, reflection, and audit trail

### 2. Reflection System Integration

**Reflection Explanation Pattern:**
```python
def explain_reflection(
    self,
    reflection_id: str,
) -> dict[str, Any]:
    """Explain a specific reflection cycle."""
    from app.core.reflection import ReflectionSystem
    
    reflection_system = ReflectionSystem()
    reflection = reflection_system.get_reflection(reflection_id)
    
    return self._execute_through_kernel(
        action=self._do_explain_reflection,
        action_name="ExplainabilityAgent.explain_reflection",
        action_args=(reflection,),
        risk_level="low",
        metadata={"reflection_id": reflection_id},
    )

def _do_explain_reflection(
    self,
    reflection: dict,
) -> dict[str, Any]:
    """Generate explanation of reflection cycle."""
    return {
        "reflection_id": reflection["id"],
        "explanation": f"""
Reflection Analysis:
- Trigger: {reflection['trigger']}
- Insights: {len(reflection['insights'])} key insights identified
- Actions Taken: {', '.join(reflection['actions'])}
- Outcome: {reflection['outcome']}

Key Insights:
{self._format_insights(reflection['insights'])}
        """,
        "timestamp": reflection["timestamp"],
    }
```

### 3. Triumvirate Explanation Pattern

**Governance Decision Explanation:**
```python
def explain_governance_decision(
    self,
    decision_id: str,
) -> dict[str, Any]:
    """Explain why Triumvirate made a specific decision."""
    from app.core.triumvirate import Triumvirate
    
    triumvirate = Triumvirate()
    decision = triumvirate.get_decision(decision_id)
    
    return self._execute_through_kernel(
        action=self._do_explain_governance,
        action_name="ExplainabilityAgent.explain_governance_decision",
        action_args=(decision,),
        risk_level="low",
        metadata={"decision_id": decision_id},
    )

def _do_explain_governance(
    self,
    decision: dict,
) -> dict[str, Any]:
    """Generate explanation of governance decision."""
    # Extract votes from guardians
    votes = decision.get("votes", {})
    consensus = decision.get("consensus")
    
    explanation_lines = [
        f"Governance Decision: {decision['action']}",
        f"Result: {'APPROVED' if consensus else 'BLOCKED'}",
        "",
        "Guardian Votes:",
    ]
    
    for guardian, vote in votes.items():
        emoji = "✅" if vote["approved"] else "❌"
        explanation_lines.append(f"  {emoji} {guardian}: {vote['reason']}")
    
    if not consensus:
        explanation_lines.append("")
        explanation_lines.append(f"Decision blocked: {decision['block_reason']}")
    
    return {
        "decision_id": decision["id"],
        "explanation": "\n".join(explanation_lines),
        "consensus": consensus,
    }
```

### 4. FourLaws Violation Explanation

**Law Violation Explanation:**
```python
def explain_law_violation(
    self,
    action: dict,
    violation: dict,
) -> dict[str, Any]:
    """Explain why action violated [[src/app/core/ai_systems.py]]."""
    return self._execute_through_kernel(
        action=self._do_explain_violation,
        action_name="ExplainabilityAgent.explain_law_violation",
        action_args=(action, violation),
        risk_level="low",
        metadata={
            "action": action.get("name"),
            "violated_law": violation.get("law"),
        },
    )

def _do_explain_violation(
    self,
    action: dict,
    violation: dict,
) -> dict[str, Any]:
    """Generate explanation of law violation."""
    law_descriptions = {
        "law_1": "A robot may not injure a human being or, through inaction, allow a human being to come to harm.",
        "law_2": "A robot must obey orders given by human beings except where such orders would conflict with the First Law.",
        "law_3": "A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.",
        "law_4": "A robot may not harm humanity, or, by inaction, allow humanity to come to harm.",
    }
    
    violated_law = violation.get("law")
    law_text = law_descriptions.get(violated_law, "Unknown law")
    
    explanation = f"""
Action Blocked by FourLaws

Action: {action['name']}
Violated Law: {violated_law}

Law Definition:
{law_text}

Reason for Violation:
{violation['reason']}

Suggested Alternatives:
{', '.join(violation.get('alternatives', ['None available']))}
    """
    
    return {
        "action": action["name"],
        "violated_law": violated_law,
        "explanation": explanation.strip(),
        "alternatives": violation.get("alternatives", []),
    }
```

### 5. Memory-Based Explanation

**Historical Context Explanation:**
```python
def explain_with_history(
    self,
    decision: dict,
    context_window: int = 10,
) -> dict[str, Any]:
    """Explain decision with historical context."""
    from app.core.memory_expansion import MemoryExpansionSystem
    
    memory = MemoryExpansionSystem()
    
    return self._execute_through_kernel(
        action=self._do_explain_with_history,
        action_name="ExplainabilityAgent.explain_with_history",
        action_args=(decision, memory, context_window),
        risk_level="low",
        metadata={
            "decision_id": decision.get("id"),
            "context_window": context_window,
        },
    )

def _do_explain_with_history(
    self,
    decision: dict,
    memory: MemoryExpansionSystem,
    context_window: int,
) -> dict[str, Any]:
    """Generate explanation with historical context."""
    # Retrieve related past decisions
    similar_decisions = memory.query_knowledge(
        category="decision_history",
        filter_fn=lambda d: (
            d.get("action_type") == decision.get("action_type")
        ),
        limit=context_window,
    )
    
    # Build context explanation
    context_lines = [
        f"Current Decision: {decision['action']}",
        "",
        f"Historical Context ({len(similar_decisions)} similar decisions):",
    ]
    
    for i, past_decision in enumerate(similar_decisions, 1):
        outcome = past_decision.get("outcome")
        context_lines.append(
            f"  {i}. {past_decision['action']} → {outcome}"
        )
    
    # Analyze patterns
    success_rate = sum(
        1 for d in similar_decisions
        if d.get("outcome") == "success"
    ) / len(similar_decisions) if similar_decisions else 0.0
    
    context_lines.append("")
    context_lines.append(
        f"Historical Success Rate: {success_rate * 100:.1f}%"
    )
    
    return {
        "decision_id": decision.get("id"),
        "explanation": "\n".join(context_lines),
        "historical_context": similar_decisions,
        "success_rate": success_rate,
    }
```

### 6. Platform Tier Registry

**Registration Pattern:**
```python
from app.core.platform_tiers import (
    get_tier_registry,
    PlatformTier,
    ComponentRole,
    AuthorityLevel,
)

registry = get_tier_registry()
registry.register_component(
    name="ExplainabilityAgent",
    tier=PlatformTier.CAPABILITY,
    role=ComponentRole.EXPLAINABILITY,
    authority_level=AuthorityLevel.ADVISORY,
)
```

**Authority Constraints:**
- Can **explain** decisions (reporting authority)
- Can **observe** Tier 1 and Tier 3 actions
- Cannot **enforce** or **block** actions

---

## 💡 Usage Patterns

### Pattern 1: Basic Decision Explanation

```python
from app.core.cognition_kernel import CognitionKernel
from app.agents import ExplainabilityAgent

# Initialize
kernel = CognitionKernel()
agent = ExplainabilityAgent(kernel=kernel)

# Future implementation: explain decision
decision = {
    "id": "dec_12345",
    "action": "Delete user data",
    "outcome": "blocked",
    "reasoning": [
        "Action requires user consent",
        "No consent record found",
        "Data retention policy requires 30-day notice",
    ],
    "confidence": 0.95,
}

explanation = agent.explain_decision(decision, explanation_type="detailed")
print(explanation["explanation"])
```

**Output:**
```
Action Taken: Delete user data
Outcome: blocked

Reasoning Chain:
  1. Action requires user consent
  2. No consent record found
  3. Data retention policy requires 30-day notice
```

### Pattern 2: Multi-Level Explanation

```python
def explain_action_fully(
    agent: ExplainabilityAgent,
    action_id: str,
) -> dict[str, Any]:
    """Provide multi-level explanation of action."""
    # Level 1: Basic decision
    basic = agent.explain_decision(action_id, explanation_type="brief")
    
    # Level 2: Governance context
    governance = agent.explain_governance_decision(action_id)
    
    # Level 3: Historical context
    historical = agent.explain_with_history(action_id, context_window=5)
    
    # Level 4: Reflection insights
    reflection = agent.explain_reflection(action_id)
    
    return {
        "basic": basic,
        "governance": governance,
        "historical": historical,
        "reflection": reflection,
        "full_explanation": _combine_explanations(
            basic, governance, historical, reflection
        ),
    }
```

### Pattern 3: Interactive Explanation

```python
def interactive_explanation_loop(
    agent: ExplainabilityAgent,
    decision: dict,
) -> None:
    """Interactive Q&A about decision."""
    print("Decision Explanation System")
    print("=" * 50)
    
    # Start with brief explanation
    brief = agent.explain_decision(decision, explanation_type="brief")
    print(brief["explanation"])
    print()
    
    while True:
        print("Ask a question (or 'quit' to exit):")
        question = input("> ")
        
        if question.lower() == "quit":
            break
        
        # Route question to appropriate explanation
        if "why" in question.lower():
            # Detailed reasoning
            detailed = agent.explain_decision(decision, explanation_type="detailed")
            print(detailed["explanation"])
        elif "history" in question.lower():
            # Historical context
            historical = agent.explain_with_history(decision)
            print(historical["explanation"])
        elif "law" in question.lower():
            # Law-based explanation
            if "violation" in decision:
                law_exp = agent.explain_law_violation(decision, decision["violation"])
                print(law_exp["explanation"])
        else:
            print("I can explain: 'why' (reasoning), 'history' (context), 'law' (violations)")
        
        print()
```

### Pattern 4: Explanation Templates

```python
# Future implementation
class ExplainabilityAgent(KernelRoutedAgent):
    def register_template(
        self,
        name: str,
        template: str,
        variables: list[str],
    ) -> None:
        """Register explanation template."""
        self.explanations[name] = {
            "template": template,
            "variables": variables,
        }
    
    def explain_with_template(
        self,
        template_name: str,
        values: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate explanation using template."""
        if template_name not in self.explanations:
            raise ValueError(f"Template not found: {template_name}")
        
        template_config = self.explanations[template_name]
        template = template_config["template"]
        
        return self._execute_through_kernel(
            action=lambda: template.format(**values),
            action_name=f"ExplainabilityAgent.explain_{template_name}",
            risk_level="low",
        )

# Usage
agent = ExplainabilityAgent()

agent.register_template(
    name="blocked_action",
    template="""
Action Blocked

Action: {action}
Reason: {reason}
Blocked By: {blocked_by}

To proceed:
{next_steps}
    """,
    variables=["action", "reason", "blocked_by", "next_steps"],
)

explanation = agent.explain_with_template(
    template_name="blocked_action",
    values={
        "action": "Delete production database",
        "reason": "Insufficient permissions",
        "blocked_by": "Triumvirate (FourLaws Guardian)",
        "next_steps": "Request override from system administrator",
    },
)
```

---

## ⚠️ Edge Cases and Gotchas

### Edge Case 1: Circular Explanation

**Scenario:** Explaining explanation generation

**Problem:**
```python
# DON'T DO THIS: Infinite loop
def explain_decision(self, decision: dict) -> dict:
    # Explain how we explain (circular!)
    explanation = self.explain_decision(decision)  # INFINITE RECURSION!
    return explanation
```

**Detection:**
```python
# CognitionKernel detects circular execution
if self._in_execution():
    raise RuntimeError("Circular execution: ExplainabilityAgent explaining itself")
```

### Edge Case 2: Sensitive Data Exposure

**Scenario:** Explanation reveals sensitive information

**Problem:**
```python
# Explanation contains user credentials
decision = {
    "action": "Login failed",
    "reasoning": ["Password 'secret123' is incorrect"],  # LEAKS PASSWORD!
}

explanation = agent.explain_decision(decision)
# explanation["explanation"] now contains password!
```

**Mitigation:**
```python
def _sanitize_sensitive_data(self, text: str) -> str:
    """Remove sensitive data from explanations."""
    import re
    
    # Mask passwords
    text = re.sub(r"Password\s+'[^']*'", "Password '****'", text)
    
    # Mask API keys
    text = re.sub(r"(api_key|token):\s*\S+", r"\1: ****", text)
    
    # Mask email addresses (optional)
    text = re.sub(r"[\w.-]+@[\w.-]+\.\w+", "[email protected]", text)
    
    return text

def _do_explain_decision(self, decision: dict, explanation_type: str) -> dict:
    """Generate sanitized explanation."""
    raw_explanation = self._generate_explanation(decision, explanation_type)
    sanitized = self._sanitize_sensitive_data(raw_explanation)
    
    return {
        "explanation": sanitized,
        "sanitized": True,
    }
```

### Edge Case 3: Missing Context

**Scenario:** Insufficient information to explain decision

**Problem:**
```python
# Partial decision object
decision = {"id": "dec_123"}  # Missing action, outcome, reasoning

explanation = agent.explain_decision(decision)
# Cannot generate meaningful explanation!
```

**Solution:**
```python
def _do_explain_decision(
    self,
    decision: dict,
    explanation_type: str,
) -> dict[str, Any]:
    """Generate explanation with validation."""
    # Validate decision has required fields
    required_fields = ["id", "action", "outcome"]
    missing = [f for f in required_fields if f not in decision]
    
    if missing:
        return {
            "decision_id": decision.get("id"),
            "explanation": f"Cannot explain: missing fields {missing}",
            "error": "insufficient_context",
            "missing_fields": missing,
        }
    
    # Generate explanation
    return self._generate_full_explanation(decision, explanation_type)
```

### Edge Case 4: Performance Impact

**Scenario:** Explanation generation is slow for complex decisions

**Problem:**
```python
# Complex decision with large reasoning chain
decision = {
    "reasoning": [f"Step {i}" for i in range(10000)],  # 10k steps!
}

explanation = agent.explain_decision(decision)  # SLOW!
```

**Solution: Lazy Loading**
```python
def explain_decision(
    self,
    decision: dict,
    explanation_type: str = "brief",
    max_reasoning_steps: int = 10,
) -> dict[str, Any]:
    """Generate explanation with lazy loading."""
    return self._execute_through_kernel(
        action=self._do_explain_lazy,
        action_name="ExplainabilityAgent.explain_decision",
        action_args=(decision, explanation_type, max_reasoning_steps),
        risk_level="low",
    )

def _do_explain_lazy(
    self,
    decision: dict,
    explanation_type: str,
    max_reasoning_steps: int,
) -> dict[str, Any]:
    """Generate explanation with limited detail."""
    reasoning = decision.get("reasoning", [])
    
    if len(reasoning) > max_reasoning_steps:
        # Truncate reasoning
        truncated_reasoning = reasoning[:max_reasoning_steps]
        explanation = self._generate_explanation(
            {**decision, "reasoning": truncated_reasoning},
            explanation_type,
        )
        explanation += f"\n\n(Showing {max_reasoning_steps} of {len(reasoning)} steps)"
    else:
        explanation = self._generate_explanation(decision, explanation_type)
    
    return {
        "explanation": explanation,
        "truncated": len(reasoning) > max_reasoning_steps,
        "total_steps": len(reasoning),
    }
```

### Edge Case 5: Kernel Not Available

**Scenario:** Agent initialized without kernel

**Behavior:**
```python
agent = ExplainabilityAgent()  # kernel=None
# Logs warning: "ExplainabilityAgent initialized without CognitionKernel.
#                Actions will bypass kernel governance (NOT RECOMMENDED)."
```

**Mitigation:**
```python
from app.core.kernel_integration import get_global_kernel

agent = ExplainabilityAgent()
if agent.kernel is None:
    raise RuntimeError("CognitionKernel not configured for ExplainabilityAgent")
```

---

## 🧪 Testing

### Test Strategy

**Coverage Target:** 100% (trivial for stub, 80%+ for full implementation)

**Test Categories:**
1. **Initialization Tests:** Verify constructor behavior
2. **Kernel Integration Tests:** Validate routing behavior
3. **Explanation Generation Tests:** Test explanation quality
4. **Sanitization Tests:** Verify sensitive data removal
5. **Template Tests:** Test template rendering
6. **Performance Tests:** Benchmark explanation speed

### Test Suite Structure

```python
# tests/test_explainability_agent.py

import pytest
from app.core.cognition_kernel import CognitionKernel
from app.agents import ExplainabilityAgent

class TestExplainabilityAgentInitialization:
    """Test agent initialization and configuration."""
    
    def test_init_with_kernel(self):
        """Agent initializes with provided kernel."""
        kernel = CognitionKernel()
        agent = ExplainabilityAgent(kernel=kernel)
        
        assert agent.kernel is kernel
        assert agent.enabled == False
        assert agent.explanations == {}
        assert agent.execution_type.value == "agent_action"
        assert agent.default_risk_level == "low"
    
    def test_inherits_kernel_routed_agent(self):
        """Agent properly inherits from KernelRoutedAgent."""
        from app.core.kernel_integration import KernelRoutedAgent
        agent = ExplainabilityAgent()
        assert isinstance(agent, KernelRoutedAgent)

class TestExplainabilityAgentStubBehavior:
    """Test stub mode behavior (current implementation)."""
    
    def test_stub_mode_disabled(self):
        """Stub agent is disabled by default."""
        agent = ExplainabilityAgent()
        assert agent.enabled == False
    
    def test_stub_mode_empty_explanations(self):
        """Stub agent has no explanation templates."""
        agent = ExplainabilityAgent()
        assert agent.explanations == {}

# Future tests:

class TestExplainabilityAgentDecisionExplanation:
    """Test decision explanation functionality."""
    
    def test_explain_simple_decision(self, agent):
        """Generate explanation for simple decision."""
        decision = {
            "id": "dec_1",
            "action": "Save file",
            "outcome": "success",
            "reasoning": ["File path valid", "Permissions granted"],
        }
        
        result = agent.explain_decision(decision, explanation_type="brief")
        assert "Save file" in result["explanation"]
        assert "success" in result["explanation"]
    
    def test_explain_blocked_decision(self, agent):
        """Generate explanation for blocked decision."""
        decision = {
            "id": "dec_2",
            "action": "Delete database",
            "outcome": "blocked",
            "reasoning": ["[[src/app/core/ai_systems.py]] violation", "Lacks consensus"],
        }
        
        result = agent.explain_decision(decision, explanation_type="detailed")
        assert "blocked" in result["explanation"].lower()
        assert "[[src/app/core/ai_systems.py]]" in result["explanation"]

class TestExplainabilityAgentSanitization:
    """Test sensitive data sanitization."""
    
    def test_sanitize_password(self, agent):
        """Sanitize password from explanation."""
        text = "Login failed. Password 'secret123' is incorrect."
        sanitized = agent._sanitize_sensitive_data(text)
        assert "secret123" not in sanitized
        assert "****" in sanitized
    
    def test_sanitize_api_key(self, agent):
        """Sanitize API key from explanation."""
        text = "API call failed. api_key: sk-1234567890"
        sanitized = agent._sanitize_sensitive_data(text)
        assert "sk-1234567890" not in sanitized

class TestExplainabilityAgentTemplates:
    """Test explanation templates."""
    
    def test_register_template(self, agent):
        """Register custom explanation template."""
        agent.register_template(
            name="error",
            template="Error: {message}",
            variables=["message"],
        )
        assert "error" in agent.explanations
    
    def test_explain_with_template(self, agent):
        """Generate explanation using template."""
        agent.register_template(
            name="greeting",
            template="Hello {name}!",
            variables=["name"],
        )
        
        result = agent.explain_with_template(
            template_name="greeting",
            values={"name": "Alice"},
        )
        assert result["explanation"] == "Hello Alice!"
```

### Running Tests

```powershell
# Run all explainability agent tests
pytest tests/test_explainability_agent.py -v

# Run with coverage
pytest tests/test_explainability_agent.py --cov=app.agents.explainability --cov-report=term-missing

# Run specific test class
pytest tests/test_explainability_agent.py::TestExplainabilityAgentDecisionExplanation -v
```

---

## 📊 Metadata

### Classification

| Property | Value |
|----------|-------|
| **Agent Type** | Decision Transparency & Reasoning |
| **Governance Status** | ✅ Governed (routes through CognitionKernel) |
| **Implementation Status** | 🚧 Stub (ready for implementation) |
| **Risk Level** | Low (explanation is read-only) |
| **Platform Tier** | Tier 2 (Capability Layer) |
| **Authority Level** | Advisory (can explain, not enforce) |
| **AI Integration** | None (no AI calls in current design) |

### Dependencies

**Direct:**
- `app.core.cognition_kernel` (CognitionKernel, ExecutionType)
- `app.core.kernel_integration` (KernelRoutedAgent)

**Indirect (via kernel):**
- `app.core.reflection` (reflection analysis)
- `app.core.memory_expansion` (decision history)
- `app.core.triumvirate` (governance explanations)
- `app.core.ai_systems.[[src/app/core/ai_systems.py]]` (law violation explanations)

### File Statistics

| Metric | Value |
|--------|-------|
| **Lines of Code** | 43 |
| **Imports** | 2 modules |
| **Classes** | 1 (ExplainabilityAgent) |
| **Methods** | 1 (__init__) |
| **Docstring Coverage** | 100% |
| **Type Annotations** | 100% |

### Governance Compliance

| Requirement | Status |
|-------------|--------|
| ✅ Routes through CognitionKernel | Yes (via KernelRoutedAgent) |
| ✅ Logs all executions | Yes (automatic via kernel) |
| ✅ Respects FourLaws | Yes (validated by kernel) |
| ✅ Triumvirate oversight | Yes (high-risk explanations) |
| ✅ Sensitive data protection | Future (sanitization) |
| ✅ Reflection integration | Yes (via kernel) |
| ✅ Audit trail | Yes (all actions logged) |

### Related Documentation

- **[AGENT_CLASSIFICATION.md](../agents/AGENT_CLASSIFICATION.md)** - Full agent taxonomy
- **[reflection.md](../core/reflection.md)** - Reflection system integration
- **[triumvirate.md](../core/triumvirate.md)** - Governance explanation patterns
- **[memory_expansion.md](../core/memory_expansion.md)** - Historical context retrieval
- **[governance_pipeline.md](../governance/governance_pipeline.md)** - Governance flow

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-26 | Initial documentation (stub implementation) |

---

## 🎯 Implementation Roadmap

### Phase 1: Core Explanation (Planned)
- [ ] Basic decision explanation (brief, detailed)
- [ ] Reasoning chain formatting
- [ ] Confidence score display
- [ ] Template system

### Phase 2: Governance Integration (Planned)
- [ ] Triumvirate decision explanations
- [ ] FourLaws violation explanations
- [ ] Black Vault explanations
- [ ] Identity mutation explanations

### Phase 3: Advanced Features (Future)
- [ ] Interactive Q&A system
- [ ] Historical context integration
- [ ] Multi-level explanations
- [ ] Sensitive data sanitization
- [ ] LLM-powered natural language explanations

---

**Documentation maintained by:** AI Systems Documentation Team  
**Last verified:** 2025-01-26  
**Next review:** After explainability agent implementation

---

## 📁 Source Code References

This documentation references the following source files:

- [[src/app/agents/explainability.py]]
- [[src/app/agents/oversight.py]]

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
