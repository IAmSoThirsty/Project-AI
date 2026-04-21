---
type: source-doc
tags: [source-docs, aggregated-content, technical-reference, ai-agents, cognitive-pipeline]
created: 2025-01-26
last_verified: 2026-04-20
status: current
related_systems: [oversight-agent, planner-agent, validator-agent, explainability-agent, four-laws, memory-expansion]
stakeholders: [content-team, knowledge-management, developers, ai-engineers, system-architects]
content_category: technical
review_cycle: quarterly
---

# AI Agents Documentation

**Directory:** `source-docs/agents/`  
**Source Code:** `src/app/agents/`  
**Version:** 1.0.0  
**Last Updated:** 2025-01-26

## Purpose

This directory contains documentation for the four specialized AI agent modules that provide advanced cognitive capabilities to Project-AI. These agents are **NOT plugins** but integral components of the AI decision-making pipeline, built on top of the core systems.

## Agent Architecture

### Design Philosophy

Project-AI's agent system follows a **modular cognitive pipeline** pattern:

```
User Input → Validator → FourLaws → Planner → Oversight → Core Systems → Explainability → User Output
```

Each agent has a specific responsibility and operates independently while sharing context through the core systems (particularly MemoryExpansion and FourLaws).

### Agent vs. Plugin Distinction

| Aspect | Agents | Plugins |
|--------|--------|---------|
| Purpose | Cognitive processing | Feature extensions |
| Integration | Core system dependencies | Isolated functionality |
| Lifecycle | Always active | User-controlled enable/disable |
| Location | `src/app/agents/` | `plugins/` directory |
| Management | Code-level integration | [[src/app/core/ai_systems.py]] in `ai_systems.py` |

## The Four Agents

### 🛡️ Oversight Agent (`oversight.py`)

**Purpose:** Pre-execution safety validation for all actions

**Complexity:** High | **Lines:** ~250 | **Dependencies:** FourLaws, MemoryExpansion

#### Capabilities

1. **Action Safety Validation**
   - Validates actions against Asimov's Laws before execution
   - Checks for potential harm to humans, self, or system integrity
   - Evaluates unintended consequences and edge cases

2. **Risk Assessment**
   - Assigns risk scores (0-100) to proposed actions
   - Low risk (0-30): Execute without additional checks
   - Medium risk (31-70): Require user confirmation
   - High risk (71-100): Block with override requirement

3. **Context-Aware Decision Making**
   - Considers current system state, user permissions, and environmental factors
   - Tracks historical action outcomes to improve future assessments
   - Adapts risk thresholds based on user trust level

#### API Reference

```python
from app.agents.oversight import OversightAgent

agent = OversightAgent(four_laws_system, memory_system)

# Validate action before execution
is_safe, risk_score, reasoning = agent.validate_action(
    action="delete_all_user_data",
    context={
        "user_requested": True,
        "has_backup": False,
        "is_emergency": False
    }
)

if is_safe:
    execute_action()
else:
    log_blocked_action(reasoning)
```

#### Integration Points

- **FourLaws:** Primary validation engine
- **MemoryExpansion:** Historical context for risk assessment
- **CommandOverride:** Can bypass oversight with master password
- **GUI:** Displays oversight warnings in dashboard alerts

#### Configuration

```python
# Override default risk thresholds
agent.set_risk_thresholds(
    low=25,
    medium=60,
    high=85
)

# Enable/disable specific checks
agent.configure_checks(
    check_data_loss=True,
    check_privacy_violation=True,
    check_resource_exhaustion=True
)
```

---

### 📋 Planner Agent (`planner.py`)

**Purpose:** Task decomposition and strategic planning

**Complexity:** High | **Lines:** ~280 | **Dependencies:** MemoryExpansion, Intelligence Engine

#### Capabilities

1. **Task Decomposition**
   - Breaks complex requests into executable subtasks
   - Creates dependency graphs for parallel/sequential execution
   - Estimates time and resource requirements per subtask

2. **Strategic Planning**
   - Generates multi-step plans for long-term goals
   - Identifies alternative approaches and contingency plans
   - Optimizes task ordering for efficiency

3. **Progress Tracking**
   - Monitors subtask completion and adjusts plans dynamically
   - Identifies blocked tasks and suggests workarounds
   - Provides real-time progress updates to user

#### API Reference

```python
from app.agents.planner import PlannerAgent

agent = PlannerAgent(memory_system, intelligence_engine)

# Decompose complex task
plan = agent.create_plan(
    goal="Build a machine learning model to predict stock prices",
    constraints={
        "max_time": "2 weeks",
        "available_tools": ["Python", "scikit-learn", "pandas"],
        "skill_level": "intermediate"
    }
)

# Plan structure:
# {
#     "goal": "...",
#     "subtasks": [
#         {
#             "id": "task_1",
#             "description": "Gather historical stock data",
#             "dependencies": [],
#             "estimated_time": "2 days",
#             "resources": ["Yahoo Finance API"]
#         },
#         ...
#     ],
#     "execution_order": ["task_1", "task_2", ...],
#     "critical_path": ["task_1", "task_3", "task_5"]
# }
```

#### Planning Strategies

1. **Breadth-First Decomposition**
   - Suitable for independent tasks with minimal dependencies
   - Maximizes parallelization opportunities

2. **Depth-First Decomposition**
   - Suitable for sequential tasks with strong dependencies
   - Minimizes context switching

3. **Hybrid Approach**
   - Combines breadth and depth strategies
   - Optimizes for both parallelization and coherence

#### Integration Points

- **MemoryExpansion:** Stores plan history and learns from outcomes
- **Intelligence Engine:** Uses GPT-4 for complex decomposition
- **GUI:** Displays plan visualization in dashboard
- **Oversight:** Plans validated before execution begins

---

### ✅ Validator Agent (`validator.py`)

**Purpose:** Input/output validation and sanitization

**Complexity:** Medium | **Lines:** ~200 | **Dependencies:** None (standalone)

#### Capabilities

1. **Input Validation**
   - Type checking (string, int, float, list, dict)
   - Range validation (min/max values, length constraints)
   - Format validation (email, URL, regex patterns)
   - SQL injection and XSS prevention

2. **Output Sanitization**
   - HTML escaping for web output
   - Removes sensitive data (passwords, API keys, PII)
   - Ensures output meets schema requirements

3. **Schema Enforcement**
   - Validates JSON payloads against predefined schemas
   - Auto-corrects common formatting issues
   - Provides detailed validation error messages

#### API Reference

```python
from app.agents.validator import ValidatorAgent

agent = ValidatorAgent()

# Validate user input
is_valid, errors = agent.validate_input(
    data={"email": "user@example.com", "age": 25},
    schema={
        "email": {"type": "email", "required": True},
        "age": {"type": "int", "min": 18, "max": 120, "required": True}
    }
)

if not is_valid:
    display_errors(errors)

# Sanitize output before displaying
sanitized = agent.sanitize_output(
    data="User password: secret123",
    remove_patterns=["password:\\s*\\S+"]
)
# Output: "User password: [REDACTED]"
```

#### Validation Rules

**Input Validation:**
- Emails: RFC 5322 compliant
- URLs: Valid scheme (http, https, ftp)
- Phone numbers: E.164 format
- Dates: ISO 8601 or configurable formats
- File paths: No path traversal (../ or ..\)

**Output Sanitization:**
- API keys: Regex patterns for common providers
- Passwords: Any field containing "password", "secret", "token"
- PII: Email addresses, phone numbers, SSNs
- HTML: `<`, `>`, `&`, `"`, `'` escaped

#### Integration Points

- **Core Systems:** All core modules use Validator for input sanitization
- **GUI:** Validates form inputs before processing
- **Web API:** Validates all incoming REST requests
- **Oversight:** Works with Validator to prevent injection attacks

---

### 🔍 Explainability Agent (`explainability.py`)

**Purpose:** Generate human-readable explanations for AI decisions

**Complexity:** Medium | **Lines:** ~220 | **Dependencies:** MemoryExpansion, Intelligence Engine

#### Capabilities

1. **Decision Transparency**
   - Explains why a particular action was taken or blocked
   - Traces decision path through FourLaws, Oversight, and Planner
   - Identifies key factors influencing the decision

2. **Confidence Reporting**
   - Provides confidence scores for AI predictions
   - Highlights uncertainty and ambiguous cases
   - Suggests when human review is recommended

3. **Interactive Explanations**
   - Supports "why" and "what if" questions from users
   - Generates counterfactual scenarios (what would happen if...)
   - Provides evidence for claims (citations to memory or knowledge base)

#### API Reference

```python
from app.agents.explainability import ExplainabilityAgent

agent = ExplainabilityAgent(memory_system, intelligence_engine)

# Explain a decision
explanation = agent.explain_decision(
    decision="Block file deletion",
    context={
        "action": "delete_important_file",
        "risk_score": 85,
        "four_laws_check": "Failed - potential harm to user",
        "oversight_check": "Blocked - no backup exists"
    }
)

# Explanation structure:
# {
#     "summary": "File deletion blocked due to high risk (85/100)",
#     "reasoning": [
#         "FourLaws check failed: Deleting file may cause harm to user",
#         "Oversight agent flagged: No backup exists",
#         "Recommendation: Create backup before deleting"
#     ],
#     "confidence": 0.95,
#     "alternatives": ["Archive file", "Create backup first"]
# }
```

#### Explanation Formats

1. **Summary Format** (1-2 sentences)
   - Quick overview for experienced users
   - Displayed in dashboard notifications

2. **Detailed Format** (paragraph)
   - Complete decision path with all factors
   - Shown in explainability panel

3. **Technical Format** (JSON)
   - Machine-readable with all metadata
   - Used for logging and debugging

#### Integration Points

- **All Agents:** Explainability wraps other agents' decisions
- **GUI:** Dedicated explainability panel in PersonaPanel
- **MemoryExpansion:** Stores explanations for future reference
- **User Feedback:** Learns from user reactions to explanations

---

## Agent Communication Pattern

Agents communicate through shared core systems:

```python
# Example: Planner creates task, Oversight validates, Explainability reports

# Step 1: Planner decomposes task
plan = planner_agent.create_plan(goal="Update user profile")

# Step 2: Oversight validates each subtask
for task in plan["subtasks"]:
    is_safe, risk, reason = oversight_agent.validate_action(
        task["description"],
        context={"user_requested": True}
    )
    task["validated"] = is_safe
    task["risk_score"] = risk

# Step 3: Validator checks inputs
for task in plan["subtasks"]:
    if task["requires_input"]:
        is_valid, errors = validator_agent.validate_input(
            task["input_data"],
            task["schema"]
        )
        task["input_valid"] = is_valid

# Step 4: Explainability explains overall plan
explanation = explainability_agent.explain_decision(
    decision="Execute plan",
    context={
        "plan": plan,
        "total_risk": sum(t["risk_score"] for t in plan["subtasks"]),
        "validation_status": all(t["input_valid"] for t in plan["subtasks"])
    }
)
```

## Testing Agent Systems

### Unit Testing

Each agent has isolated tests using mocked dependencies:

```python
import pytest
from unittest.mock import Mock
from app.agents.oversight import OversightAgent

@pytest.fixture
def mock_four_laws():
    four_laws = Mock()
    four_laws.validate_action.return_value = (True, "Action allowed")
    return four_laws

def test_oversight_low_risk_action(mock_four_laws):
    agent = OversightAgent(mock_four_laws, memory_system=None)
    is_safe, risk, reason = agent.validate_action(
        "read_file",
        context={"is_user_order": True}
    )
    assert is_safe is True
    assert risk < 30
```

### Integration Testing

Test agent interactions in realistic scenarios:

```python
def test_full_agent_pipeline():
    # Setup all agents
    validator = ValidatorAgent()
    oversight = OversightAgent(four_laws, memory)
    planner = PlannerAgent(memory, intelligence_engine)
    explainability = ExplainabilityAgent(memory, intelligence_engine)
    
    # Test complete workflow
    plan = planner.create_plan(goal="Export user data")
    for task in plan["subtasks"]:
        is_safe, _, _ = oversight.validate_action(task["description"], {})
        assert is_safe
    
    explanation = explainability.explain_decision("Execute plan", {"plan": plan})
    assert explanation["confidence"] > 0.8
```

## Performance Characteristics

### Resource Usage

- **Oversight:** < 10 MB memory, < 100ms per validation
- **Planner:** < 50 MB memory, 1-5 seconds for complex plans (GPT-4 call)
- **Validator:** < 5 MB memory, < 10ms per validation
- **Explainability:** < 20 MB memory, 500ms-2s per explanation (GPT-4 call)

### Optimization Strategies

1. **Caching:** Cache validation results for identical actions
2. **Parallel Processing:** Validate independent tasks concurrently
3. **Lazy Loading:** Load intelligence engine only when needed
4. **Batch Processing:** Group similar validations for efficiency

## Security Considerations

### Agent-Specific Risks

1. **Oversight Bypass:** Prevent agents from disabling oversight checks
2. **Planner Manipulation:** Validate plans don't contain malicious subtasks
3. **Validator Evasion:** Ensure validators can't be bypassed via encoding
4. **Explainability Leaks:** Don't reveal sensitive data in explanations

### Mitigation Strategies

- Agents are immutable (no runtime modification)
- All agent decisions logged for audit
- FourLaws validates agent actions same as user actions
- Sensitive data removed from explanations

## Configuration and Customization

### Agent Configuration File

```json
{
  "oversight": {
    "risk_thresholds": {"low": 30, "medium": 70, "high": 100},
    "enabled_checks": ["data_loss", "privacy", "resource_exhaustion"],
    "auto_block_high_risk": true
  },
  "planner": {
    "max_subtasks": 20,
    "max_depth": 5,
    "strategy": "hybrid",
    "use_gpt4": true
  },
  "validator": {
    "strict_mode": true,
    "auto_sanitize": true,
    "allowed_schemas": ["user_input", "api_request"]
  },
  "explainability": {
    "default_format": "detailed",
    "include_confidence": true,
    "show_alternatives": true
  }
}
```

### Runtime Configuration

```python
# Load config from JSON
with open("agent_config.json") as f:
    config = json.load(f)

# Apply to agents
oversight_agent.apply_config(config["oversight"])
planner_agent.apply_config(config["planner"])
validator_agent.apply_config(config["validator"])
explainability_agent.apply_config(config["explainability"])
```

## Future Enhancements

### Planned Features

1. **Learning Agent:** Reinforcement learning from user feedback
2. **Collaborative Agent:** Multi-agent coordination for complex tasks
3. **Proactive Agent:** Anticipates user needs and suggests actions
4. **Debugging Agent:** Helps developers troubleshoot issues

### Research Directions

- **Neuro-symbolic AI:** Combine neural networks with symbolic reasoning
- **Federated Learning:** Learn from user interactions while preserving privacy
- **Causal Reasoning:** Understand cause-effect relationships in decisions
- **Adversarial Robustness:** Resist manipulation and jailbreak attempts

## Related Documentation

- **Parent:** [source-docs/README.md](../README.md)
- **Core Systems:** [source-docs/core/README.md](../core/README.md)
- **GUI Integration:** [source-docs/gui/README.md](../gui/README.md)
- **Supporting:** [source-docs/supporting/README.md](../supporting/README.md)

---

**Document Status:** ✅ Production-Ready  
**Quality Gate:** PASSED - All 4 agents documented with API references  
**Compliance:** Fully compliant with Project-AI Governance Profile
