---
# ═══════════════════════════════════════════════════════════════════════════
# AI AGENT MODULE DOCUMENTATION TEMPLATE
# Document Type: Module Documentation (Specialized AI Agents)
# Target: src/app/agents/ modules
# Schema Version: 2.0.0
# ═══════════════════════════════════════════════════════════════════════════

# Universal Fields (Required)
title: "<%tp.file.title%>"
id: "<%tp.file.title.toLowerCase().replace(/\s+/g, '-')%>"
type: "specification"
version: "1.0.0"
created_date: "<%tp.date.now("YYYY-MM-DD")%>"
updated_date: "<%tp.date.now("YYYY-MM-DD")%>"
status: "draft"
author:
  name: "<%tp.user.name || 'Agent Development Team'%>"
  email: ""
  github: ""

# Domain-Specific Fields
category: "architecture"
tags:
  - "agent"
  - "ai-system"
  - "automation"
  - "decision-logic"
  - "architecture/backend"
technologies:
  - "Python"
  - "OpenAI"
  - "AI Agents"
classification: "internal"
audience:
  - "architect"
  - "developer"
  - "ai-engineer"

# Agent-Specific Fields
agent_name: ""
agent_purpose: ""
input_schema: {}
output_schema: {}
decision_logic: "rule-based"

# Quality Metadata
review_status:
  reviewed: false
  reviewers: []
  review_date: null
  approved: false
test_coverage:
  has_tests: false
  coverage_percent: 0
  test_files: []

# Discovery & SEO
keywords:
  - "ai agent"
  - "autonomous system"
  - "intelligent automation"
summary: "Comprehensive documentation for <% await tp.system.prompt('Agent name (e.g., OversightAgent):') %> AI agent including decision logic, input/output schemas, and integration patterns."

# Relationships
related_docs: []
supersedes: null
---

# <%tp.file.title%>

> **Agent Type:** <%`${await tp.system.prompt('Agent type (oversight/planner/validator/explainability/custom):') || 'specialized'}`%>
> **Location:** `src/app/agents/`
> **Decision Model:** <%`${await tp.system.prompt('Decision model (rule-based/ML-based/hybrid):') || 'rule-based'}`%>
> **Last Updated:** <%tp.date.now("YYYY-MM-DD")%>

---

## Table of Contents

1. [Agent Overview](#agent-overview)
2. [Architecture](#architecture)
3. [Input/Output Specifications](#inputoutput-specifications)
4. [Decision Logic](#decision-logic)
5. [API Reference](#api-reference)
6. [Integration Patterns](#integration-patterns)
7. [Configuration](#configuration)
8. [Error Handling](#error-handling)
9. [Performance Considerations](#performance-considerations)
10. [Testing Agent Behavior](#testing-agent-behavior)
11. [Ethics and Safety](#ethics-and-safety)
12. [Related Agents](#related-agents)

---

## Agent Overview

### Purpose

**What:** [One-sentence description of agent's primary function]

**Why:** [Business/technical justification - what problem does this agent solve?]

**When:** [Under what conditions is this agent invoked?]

**Where:** [Where in the system pipeline does this agent operate?]

**Who:** [Which components/users trigger this agent?]

### Agent Responsibilities

- [ ] **Primary Responsibility:** [Description]
- [ ] **Secondary Responsibility:** [Description]
- [ ] **Safety/Validation:** [Description]
- [ ] **Logging/Audit:** [Description]

### Agent Classification

| Property | Value |
|----------|-------|
| **Autonomy Level** | Fully Autonomous / Semi-Autonomous / Human-in-Loop |
| **Domain** | Security / Planning / Validation / Explanation / Custom |
| **Decision Type** | Deterministic / Probabilistic / Hybrid |
| **Criticality** | Critical / High / Medium / Low |
| **Asimov Compliance** | Yes / No |

---

## Architecture

### Agent Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                      Agent Execution Flow                   │
└─────────────────────────────────────────────────────────────┘

Input Validation
     ↓
Schema Validation (JSON Schema)
     ↓
Context Enrichment (Add metadata, history, state)
     ↓
┌──────────────────────────┐
│   DECISION LOGIC CORE    │
│                          │
│  ┌─────────────────┐    │
│  │ Rule Engine     │    │
│  │ - Rule 1        │    │
│  │ - Rule 2        │    │
│  │ - Rule N        │    │
│  └─────────────────┘    │
│          ↓              │
│  ┌─────────────────┐    │
│  │ Scoring         │    │
│  │ - Confidence    │    │
│  │ - Priority      │    │
│  └─────────────────┘    │
│          ↓              │
│  ┌─────────────────┐    │
│  │ Decision        │    │
│  │ - Action        │    │
│  │ - Rationale     │    │
│  └─────────────────┘    │
└──────────────────────────┘
     ↓
Output Formatting
     ↓
Audit Logging
     ↓
Response Return
```

### System Context

```
┌──────────────────────┐
│   User/System        │
│   Request            │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────────────────────┐
│      Agent Orchestrator              │
│  (Routes requests to agents)         │
└──────────┬───────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│    [THIS AGENT]                      │
│    src/app/agents/agent_name.py      │
│                                      │
│    ┌────────────────────┐           │
│    │ Validation         │           │
│    │ Decision Engine    │           │
│    │ Output Generation  │           │
│    └────────────────────┘           │
└──────────┬───────────────────────────┘
           │
           ├─→ Core Systems (src/app/core/)
           ├─→ External APIs (OpenAI, etc.)
           └─→ Data Persistence (data/)
```

### Agent Lifecycle

1. **Initialization:** Load configuration, initialize models
2. **Activation:** Triggered by system event or API call
3. **Processing:** Execute decision logic
4. **Response:** Return structured output
5. **Audit:** Log decision and rationale
6. **Deactivation:** Clean up resources

---

## Input/Output Specifications

### Input Schema

**JSON Schema:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AgentInputSchema",
  "type": "object",
  "required": ["action", "context"],
  "properties": {
    "action": {
      "type": "string",
      "description": "Action to be validated/processed"
    },
    "context": {
      "type": "object",
      "required": ["user_id", "timestamp"],
      "properties": {
        "user_id": {
          "type": "string",
          "description": "ID of user initiating action"
        },
        "timestamp": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp"
        },
        "additional_metadata": {
          "type": "object",
          "description": "Optional context-specific metadata"
        }
      }
    },
    "parameters": {
      "type": "object",
      "description": "Action-specific parameters"
    }
  }
}
```

**Python Type Hint:**
```python
from typing import TypedDict, Any, Optional
from datetime import datetime

class AgentContext(TypedDict):
    user_id: str
    timestamp: str
    additional_metadata: Optional[dict[str, Any]]

class AgentInput(TypedDict):
    action: str
    context: AgentContext
    parameters: Optional[dict[str, Any]]
```

**Example Input:**
```json
{
  "action": "execute_command",
  "context": {
    "user_id": "user_123",
    "timestamp": "2026-04-20T14:30:00Z",
    "additional_metadata": {
      "session_id": "sess_abc",
      "ip_address": "192.168.1.100"
    }
  },
  "parameters": {
    "command": "delete_cache",
    "flags": ["force", "recursive"]
  }
}
```

---

### Output Schema

**JSON Schema:**
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "AgentOutputSchema",
  "type": "object",
  "required": ["decision", "confidence", "rationale"],
  "properties": {
    "decision": {
      "type": "string",
      "enum": ["approve", "deny", "escalate"],
      "description": "Agent's decision on the input"
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0,
      "description": "Confidence score (0.0-1.0)"
    },
    "rationale": {
      "type": "string",
      "description": "Human-readable explanation of decision"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "rules_triggered": {
          "type": "array",
          "items": {"type": "string"}
        },
        "processing_time_ms": {
          "type": "number"
        },
        "agent_version": {
          "type": "string"
        }
      }
    },
    "recommendations": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "action": {"type": "string"},
          "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
        }
      }
    }
  }
}
```

**Python Type Hint:**
```python
from typing import TypedDict, Literal, Optional
from enum import Enum

class Decision(str, Enum):
    APPROVE = "approve"
    DENY = "deny"
    ESCALATE = "escalate"

class AgentOutput(TypedDict):
    decision: Decision
    confidence: float
    rationale: str
    metadata: Optional[dict[str, Any]]
    recommendations: Optional[list[dict[str, str]]]
```

**Example Output:**
```json
{
  "decision": "approve",
  "confidence": 0.95,
  "rationale": "Command execution approved: low risk operation on non-critical data",
  "metadata": {
    "rules_triggered": ["safety_check", "resource_validation"],
    "processing_time_ms": 42,
    "agent_version": "1.2.0"
  },
  "recommendations": [
    {
      "action": "enable_detailed_logging",
      "priority": "medium"
    }
  ]
}
```

---

## Decision Logic

### Decision Algorithm

**Algorithm Type:** <%`${await tp.system.prompt('Algorithm type (rule-based/tree-based/neural/hybrid):') || 'rule-based'}`%>

**Pseudocode:**
```
FUNCTION make_decision(input: AgentInput) -> AgentOutput:
    # Step 1: Validate input
    IF NOT validate_input(input):
        RETURN error_response("Invalid input schema")

    # Step 2: Extract features
    features = extract_features(input)

    # Step 3: Apply decision rules
    score = 0.0
    triggered_rules = []

    FOR EACH rule IN decision_rules:
        IF rule.condition(features):
            score += rule.weight
            triggered_rules.append(rule.name)

    # Step 4: Determine decision
    IF score >= THRESHOLD_APPROVE:
        decision = "approve"
        confidence = min(score / MAX_SCORE, 1.0)
    ELSE IF score <= THRESHOLD_DENY:
        decision = "deny"
        confidence = min((MAX_SCORE - score) / MAX_SCORE, 1.0)
    ELSE:
        decision = "escalate"
        confidence = 0.5

    # Step 5: Generate rationale
    rationale = generate_explanation(decision, triggered_rules, features)

    # Step 6: Return structured output
    RETURN AgentOutput(
        decision=decision,
        confidence=confidence,
        rationale=rationale,
        metadata={
            "rules_triggered": triggered_rules,
            "score": score
        }
    )
END FUNCTION
```

---

### Decision Rules

#### Rule 1: [Rule Name]

**Condition:** `[Logical condition]`

**Weight:** `[Numeric weight or priority]`

**Action:** `[What happens when rule triggers]`

**Example:**
```python
def rule_safety_check(context: dict) -> tuple[bool, float]:
    """
    Check if action endangers human safety.

    Returns:
        (rule_triggered: bool, weight: float)
    """
    endangers_humans = context.get("endangers_humanity", False)

    if endangers_humans:
        return (True, -100.0)  # Instant deny
    return (False, 0.0)
```

---

#### Rule 2: [Rule Name]

**Condition:** `[Logical condition]`

**Weight:** `[Numeric weight or priority]`

**Action:** `[What happens when rule triggers]`

**Example:**
```python
def rule_resource_validation(parameters: dict) -> tuple[bool, float]:
    """
    Validate resource availability before approving action.

    Returns:
        (rule_triggered: bool, weight: float)
    """
    resource_id = parameters.get("resource_id")

    if resource_exists(resource_id):
        return (True, 10.0)  # Positive weight
    return (False, 0.0)
```

---

### Decision Matrix

| Input Condition | Rule 1 | Rule 2 | Rule 3 | Total Score | Decision |
|----------------|--------|--------|--------|-------------|----------|
| Normal operation | 0 | +10 | +5 | 15 | Approve |
| Missing resource | 0 | 0 | +5 | 5 | Escalate |
| Safety violation | -100 | N/A | N/A | -100 | Deny |

---

### Confidence Scoring

**Confidence Calculation:**
```python
def calculate_confidence(score: float, rules_triggered: list[str]) -> float:
    """
    Calculate confidence based on score and rule consensus.

    Formula:
        confidence = (base_score + rule_consensus_bonus) / max_possible_score

    Args:
        score: Weighted sum of triggered rules
        rules_triggered: List of rule names that fired

    Returns:
        Confidence score between 0.0 and 1.0
    """
    base_confidence = abs(score) / MAX_SCORE

    # Bonus for multiple consistent rules
    if len(rules_triggered) >= 3:
        consensus_bonus = 0.1
    else:
        consensus_bonus = 0.0

    return min(base_confidence + consensus_bonus, 1.0)
```

---

## API Reference

### Class Definition

#### Class: `AgentName`

```python
class AgentName:
    """
    [Agent description and purpose.]

    Attributes:
        config (dict): Agent configuration parameters
        rules (list): Loaded decision rules
        version (str): Agent version number
    """

    def __init__(self, config: dict = None):
        """
        Initialize the agent.

        Args:
            config (dict, optional): Configuration overrides

        Raises:
            ValueError: If config is invalid
        """
        self.config = config or self._load_default_config()
        self.rules = self._load_rules()
        self.version = "1.0.0"
```

---

### Primary Methods

#### `process(self, input_data: dict) -> dict`

**Purpose:** Main entry point for agent processing

**Parameters:**
- `input_data` (`dict`): Input conforming to `AgentInput` schema

**Returns:**
- `dict`: Output conforming to `AgentOutput` schema

**Raises:**
- `ValidationError`: If input doesn't match schema
- `ProcessingError`: If decision logic fails

**Example:**
```python
agent = AgentName()

input_data = {
    "action": "execute_command",
    "context": {
        "user_id": "user_123",
        "timestamp": "2026-04-20T14:30:00Z"
    },
    "parameters": {
        "command": "delete_cache"
    }
}

result = agent.process(input_data)
print(f"Decision: {result['decision']}")
print(f"Rationale: {result['rationale']}")
```

---

#### `validate_input(self, input_data: dict) -> tuple[bool, list[str]]`

**Purpose:** Validate input against JSON schema

**Parameters:**
- `input_data` (`dict`): Input to validate

**Returns:**
- `tuple[bool, list[str]]`: (is_valid, error_messages)

**Example:**
```python
is_valid, errors = agent.validate_input(input_data)
if not is_valid:
    print(f"Validation errors: {errors}")
```

---

#### `explain_decision(self, output: dict) -> str`

**Purpose:** Generate human-readable explanation of decision

**Parameters:**
- `output` (`dict`): Agent output to explain

**Returns:**
- `str`: Detailed explanation

**Example:**
```python
explanation = agent.explain_decision(result)
print(explanation)
# Output: "The action was APPROVED because it passed safety checks (rule: safety_check)
# and resource validation (rule: resource_validation). Confidence: 95%"
```

---

## Integration Patterns

### Pattern 1: Synchronous Request-Response

**Use Case:** Real-time validation before action execution

```python
from app.agents.agent_name import AgentName

def execute_user_action(action: str, context: dict):
    # Initialize agent
    agent = AgentName()

    # Request validation
    agent_input = {
        "action": action,
        "context": context,
        "parameters": {}
    }

    result = agent.process(agent_input)

    # Check decision
    if result["decision"] == "approve":
        # Execute action
        perform_action(action)
        return {"status": "success"}
    elif result["decision"] == "deny":
        # Reject action
        return {"status": "rejected", "reason": result["rationale"]}
    else:  # escalate
        # Human review required
        return {"status": "pending", "reason": "Requires manual review"}
```

---

### Pattern 2: Batch Processing

**Use Case:** Analyze multiple actions in batch

```python
from concurrent.futures import ThreadPoolExecutor

def batch_process_actions(actions: list[dict]) -> list[dict]:
    agent = AgentName()

    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(agent.process, actions)

    return list(results)
```

---

### Pattern 3: Agent Chaining

**Use Case:** Multiple agents collaborate on decision

```python
from app.agents.oversight import OversightAgent
from app.agents.validator import ValidatorAgent
from app.agents.planner import PlannerAgent

def multi_agent_pipeline(action: dict):
    # Stage 1: Safety oversight
    oversight = OversightAgent()
    safety_result = oversight.process(action)

    if safety_result["decision"] == "deny":
        return {"status": "rejected", "stage": "oversight"}

    # Stage 2: Input validation
    validator = ValidatorAgent()
    validation_result = validator.process(action)

    if validation_result["decision"] != "approve":
        return {"status": "invalid", "stage": "validation"}

    # Stage 3: Task planning
    planner = PlannerAgent()
    plan = planner.process(action)

    return {"status": "approved", "plan": plan}
```

---

## Configuration

### Configuration File

**Location:** `config/agents/agent_name.json`

**Schema:**
```json
{
  "agent_name": "agent_name",
  "version": "1.0.0",
  "enabled": true,
  "decision_thresholds": {
    "approve": 50.0,
    "deny": -50.0
  },
  "rules": [
    {
      "name": "safety_check",
      "enabled": true,
      "weight": -100.0,
      "priority": "critical"
    },
    {
      "name": "resource_validation",
      "enabled": true,
      "weight": 10.0,
      "priority": "high"
    }
  ],
  "logging": {
    "level": "INFO",
    "audit_trail": true,
    "log_file": "logs/agents/agent_name.log"
  },
  "performance": {
    "timeout_seconds": 5,
    "max_retries": 3
  }
}
```

---

### Environment Variables

```bash
# Agent Configuration
AGENT_NAME_ENABLED=true
AGENT_NAME_LOG_LEVEL=INFO

# External Dependencies
OPENAI_API_KEY=sk-...  # If agent uses LLM
```

---

## Error Handling

### Exception Hierarchy

```python
class AgentError(Exception):
    """Base exception for agent errors."""
    pass

class ValidationError(AgentError):
    """Input validation failed."""
    pass

class ProcessingError(AgentError):
    """Decision logic execution failed."""
    pass

class TimeoutError(AgentError):
    """Agent processing exceeded timeout."""
    pass
```

---

### Error Response Format

```json
{
  "decision": "error",
  "confidence": 0.0,
  "rationale": "Processing failed: [error description]",
  "metadata": {
    "error_type": "ValidationError",
    "error_message": "Missing required field: context.user_id",
    "timestamp": "2026-04-20T14:30:00Z"
  }
}
```

---

## Performance Considerations

### Latency Targets

| Operation | Target | Actual | Notes |
|-----------|--------|--------|-------|
| Input validation | <10ms | 5ms | Schema validation |
| Decision logic | <100ms | 45ms | Rule evaluation |
| Total processing | <200ms | 120ms | End-to-end |

---

### Optimization Strategies

1. **Rule Caching:** Pre-compile regex patterns and rule conditions
2. **Early Exit:** Stop evaluation on critical rule violations
3. **Async Processing:** Use async I/O for external API calls
4. **Connection Pooling:** Reuse database/API connections

---

## Testing Agent Behavior

### Test File Location

`tests/agents/test_agent_name.py`

### Test Coverage Requirements

- **Rule Coverage:** 100% of decision rules tested
- **Edge Cases:** Boundary conditions, invalid inputs
- **Integration:** Test with dependent components

### Example Test

```python
import pytest
from app.agents.agent_name import AgentName

class TestAgentName:
    @pytest.fixture
    def agent(self):
        return AgentName()

    def test_approve_decision(self, agent):
        """Test agent approves valid low-risk action."""
        input_data = {
            "action": "read_file",
            "context": {"user_id": "user_123", "timestamp": "2026-04-20T14:30:00Z"},
            "parameters": {"file_path": "data/public/info.txt"}
        }

        result = agent.process(input_data)

        assert result["decision"] == "approve"
        assert result["confidence"] > 0.8

    def test_deny_unsafe_action(self, agent):
        """Test agent denies action violating safety rules."""
        input_data = {
            "action": "delete_system",
            "context": {"user_id": "user_123", "timestamp": "2026-04-20T14:30:00Z"},
            "parameters": {"endangers_humanity": True}
        }

        result = agent.process(input_data)

        assert result["decision"] == "deny"
        assert "safety" in result["rationale"].lower()
```

---

## Ethics and Safety

### Asimov's Laws Compliance

**Four Laws of Robotics Integration:**

1. **First Law:** Agent cannot approve actions that harm humans
2. **Second Law:** Agent must obey human operators (unless conflicts with First Law)
3. **Third Law:** Agent must preserve its own function (unless conflicts with First/Second Law)
4. **Zeroth Law:** Agent must consider humanity's welfare above individual humans

**Implementation:**
```python
def validate_against_four_laws(action: str, context: dict) -> tuple[bool, str]:
    """
    Validate action against Asimov's Four Laws.

    Returns:
        (is_allowed: bool, reason: str)
    """
    # First Law: Harm to humans
    if context.get("endangers_humanity", False):
        return (False, "Violates First Law: Action endangers humans")

    # Zeroth Law: Humanity's collective welfare
    if context.get("harms_collective", False):
        return (False, "Violates Zeroth Law: Harms humanity's welfare")

    return (True, "Complies with Four Laws")
```

---

### Bias Mitigation

- **Fairness:** Decisions are deterministic and auditable
- **Transparency:** All rule triggers logged
- **Accountability:** Human oversight for escalations

---

## Related Agents

### Agent Fleet Coordination

- [[agent-doc-oversight]]: Safety validation agent
- [[agent-doc-planner]]: Task decomposition agent
- [[agent-doc-validator]]: Input/output validation agent
- [[agent-doc-explainability]]: Decision explanation agent

### Integration Documentation

- [[architecture-doc-agent-orchestration]]: Multi-agent coordination
- [[guide-agent-development]]: Agent development guide

---

## Changelog

### Version 1.0.0 (<%tp.date.now("YYYY-MM-DD")%>)

- Initial agent documentation
- Complete decision logic specification
- Input/output schemas defined
- Testing framework established

---

**Document Status:** <%`${await tp.system.prompt('Document status (draft/review/active):') || 'draft'}`%>
**Next Review Date:** [YYYY-MM-DD]
**Agent Maintainer:** <%tp.user.name || 'Agent Development Team'%>

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
