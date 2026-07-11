---
title: "AI Agents Documentation Index"
id: "agents-index"
type: "index"
version: "1.0.0"
status: "production"
created_date: "2026-04-20"
updated_date: "2026-04-20"
author: "AGENT-033"
contributors: ["Architecture Team"]
category: "ai-agents"
tags: ["index", "navigation", "agents", "documentation"]
technologies: []
related_docs: []
dependencies: []
classification: "technical"
audience: ["developers", "architects"]
estimated_reading_time: "5 minutes"
---

# AI Agents Documentation Index

## Overview

This directory contains comprehensive technical documentation for the **4 core AI agent modules** in the Project-AI system. These agents provide foundational governance, validation, planning, and transparency capabilities that integrate with the **CognitionKernel** and **Four Laws** ethical framework.

---

## Agent Modules Documented

### 1. OversightAgent
**File**: [oversight.md](./oversight.md)
**Purpose**: System monitoring and compliance enforcement
**Charter**: Autonomous compliance guardian with sovereign authority to block, audit, and escalate non-compliant operations
**Key Features**:
- Real-time system health monitoring
- Four Laws policy enforcement
- Immutable audit trail generation
- Escalation to human oversight
- Tier 1 Governance-level authority

**Integration**: Routes through CognitionKernel, enforces Four Laws, monitors all agent/tool executions

**Status**: Architecturally complete, functionally disabled (v2.1.0)

---

### 2. PlannerAgent
**File**: [planner.md](./planner.md)
**Purpose**: Task decomposition and workflow orchestration
**Charter**: Minimal task queue and scheduling interface for multi-step workflows (legacy stub)
**Key Features**:
- Task decomposition into subtasks
- Dependency management
- Execution order scheduling
- Status tracking (pending → executing → completed/failed)

**Integration**: **Governance bypass** (no AI operations, deterministic only). Superseded by `planner_agent.py` (governed version).

**Status**: Legacy stub, no kernel integration

---

### 3. ValidatorAgent
**File**: [validator.md](./validator.md)
**Purpose**: Input validation and data integrity enforcement
**Charter**: First line of defense for data security and integrity
**Key Features**:
- Input sanitization (regex, range, schema validation)
- Type safety enforcement
- Injection prevention (SQL, command, XSS)
- State integrity verification
- Format compliance (JSON, YAML, email, URL)

**Integration**: Routes through CognitionKernel (Tier 2 Execution Layer), enforces First Law by preventing attacks

**Status**: Architecturally complete, functionally disabled (v2.1.0)

---

### 4. ExplainabilityAgent
**File**: [explainability.md](./explainability.md)
**Purpose**: Decision transparency and reasoning trace generation
**Charter**: Transparency engine for AI decisions, building user trust through interpretability
**Key Features**:
- Natural language decision explanations
- Step-by-step reasoning traces
- Counterfactual analysis ("what if" questions)
- Feature attribution (SHAP/LIME-style)
- Four Laws compliance reporting

**Integration**: Routes through CognitionKernel (Tier 2 Execution Layer), reads audit logs, explains governance decisions

**Status**: Architecturally complete, functionally disabled (v2.1.0)

---

## Agent Collaboration Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         COGNITION KERNEL (Tier 1)                       │
│                    Central Governance & Orchestration                   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Four Laws Enforcement                                           │  │
│  │  - Zeroth Law: Humanity preservation                            │  │
│  │  - First Law: Human safety                                       │  │
│  │  - Second Law: User partnership                                  │  │
│  │  - Third Law: System preservation                                │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└───────────────┬─────────────────────────────────────────────────────────┘
                │
                │ governance_decisions
                │ execution_routing
                │ audit_logging
                │
                v
┌───────────────────────────────────────────────────────────────────────┐
│                    AGENT COLLABORATION LAYER (Tier 2)                 │
└───────────────────────────────────────────────────────────────────────┘
                │
                │
    ┌───────────┼───────────┬───────────────┬──────────────┐
    │           │           │               │              │
    v           v           v               v              v
┌────────┐ ┌─────────┐ ┌──────────┐ ┌─────────────┐ ┌──────────────┐
│Oversight│ │Validator│ │Planner   │ │Explainability│ │Other Agents  │
│Agent    │ │Agent    │ │Agent     │ │Agent        │ │(30+ others)  │
│         │ │         │ │(legacy)  │ │             │ │              │
└────┬────┘ └────┬────┘ └────┬─────┘ └──────┬──────┘ └──────┬───────┘
     │           │           │               │              │
     │           │           │               │              │
     │           │           │               │              │
Monitors      Validates   Orchestrates   Explains        Executes
System        Inputs      Tasks          Decisions       Tasks
Health        & Data      (ungoverned)   & Reasoning     (governed)
& Enforces    Integrity                  Traces
Compliance

     │           │           │               │              │
     └───────────┴───────────┴───────────────┴──────────────┘
                              │
                              v
                    ┌──────────────────┐
                    │  EXECUTION LAYER │
                    │   (User Actions) │
                    └──────────────────┘

KEY INTERACTIONS:

1. OversightAgent ←→ CognitionKernel
   - Monitors kernel health
   - Validates governance decisions
   - Generates audit logs
   - Escalates violations

2. ValidatorAgent ←→ All Agents
   - Pre-validates all inputs before kernel routing
   - Sanitizes user commands
   - Checks schema compliance
   - Prevents injection attacks

3. ExplainabilityAgent ←→ CognitionKernel
   - Reads kernel audit trail
   - Generates explanations for governance decisions
   - Provides transparency for Four Laws enforcement
   - Answers user "why" questions

4. PlannerAgent (standalone)
   - No kernel integration (bypass governance)
   - Simple in-memory task queue
   - Used for deterministic workflows only
   - Superseded by planner_agent.py

INTEGRATION PATTERNS:

┌──────────────┐     validate     ┌──────────────┐
│ User Input   │ ───────────────> │ Validator    │
└──────────────┘                  └──────┬───────┘
                                         │ sanitized_input
                                         v
                                  ┌──────────────┐
                                  │ Cognition    │
                                  │ Kernel       │
                                  └──────┬───────┘
                                         │ execution_decision
                                         ├─────────────────────────┐
                                         │                         │
                                         v                         v
                                  ┌──────────────┐         ┌──────────────┐
                                  │ Oversight    │         │Explainability│
                                  │ (audit)      │         │(explain)     │
                                  └──────────────┘         └──────────────┘
                                         │                         │
                                         │                         v
                                         │                  ┌──────────────┐
                                         │                  │ User         │
                                         │                  │ (why?)       │
                                         │                  └──────────────┘
                                         v
                                  ┌──────────────┐
                                  │ Compliance   │
                                  │ Logs         │
                                  └──────────────┘
```

---

## Quick Navigation

### By Agent Type

**Governance Agents** (Tier 1):
- [OversightAgent](./oversight.md) - Enforcement and monitoring

**Execution Agents** (Tier 2):
- [ValidatorAgent](./validator.md) - Input gatekeeper
- [ExplainabilityAgent](./explainability.md) - Transparency provider

**Legacy Agents** (Ungoverned):
- [PlannerAgent](./planner.md) - Simple task queue (use `planner_agent.py` for governed version)

### By Use Case

**Security & Compliance**:
- [OversightAgent](./oversight.md) - Audit trails, policy enforcement
- [ValidatorAgent](./validator.md) - Injection prevention, input sanitization

**User Trust & Transparency**:
- [ExplainabilityAgent](./explainability.md) - Decision explanations, reasoning traces

**Workflow Orchestration**:
- [PlannerAgent](./planner.md) - Task scheduling (legacy)
- `planner_agent.py` - AI-powered planning (governed, see main agent docs)

---

## Integration Points

### CognitionKernel Integration

All agents (except PlannerAgent legacy stub) inherit from `KernelRoutedAgent`:

```python
from app.core.kernel_integration import KernelRoutedAgent
from app.core.cognition_kernel import CognitionKernel, ExecutionType

class MyAgent(KernelRoutedAgent):
    def __init__(self, kernel: CognitionKernel | None = None):
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium"
        )
```

**Benefits**:
- All agent actions governed by Four Laws
- Audit logging automatic
- Governance decisions traceable
- Recursive oversight (agents monitor agents)

### Four Laws Integration

Agents validate actions through `FourLaws.validate_action()`:

```python
from app.core.ai_systems import FourLaws

is_allowed, reason = FourLaws.validate_action(
    action="Delete user data",
    context={
        "endangers_humanity": False,
        "endangers_human": True,
        "is_user_order": True,
        "order_conflicts_with_first": True
    }
)

if not is_allowed:
    # Block execution, log violation
    logger.warning(f"Action blocked: {reason}")
```

---

## Document Quality Standards

All agent documentation meets the following quality gates:

✅ **Completeness**: 1,200+ words per document
✅ **YAML Frontmatter**: Complete metadata per `METADATA_SCHEMA.md`
✅ **API Reference**: All methods (current + planned) documented
✅ **Usage Examples**: 3+ real-world scenarios per agent
✅ **Performance Metrics**: Complexity analysis, benchmarks, scalability limits
✅ **Troubleshooting**: Common issues with solutions
✅ **Four Laws Integration**: Explicit governance explanations
✅ **Related Docs**: Cross-references to kernel, laws, other agents

---

## Document Metadata

| Document | Word Count | Status | Last Updated |
|----------|-----------|--------|--------------|
| [oversight.md](./oversight.md) | 5,850 | Production | 2026-04-20 |
| [planner.md](./planner.md) | 5,900 | Production | 2026-04-20 |
| [validator.md](./validator.md) | 7,300 | Production | 2026-04-20 |
| [explainability.md](./explainability.md) | 8,200 | Production | 2026-04-20 |
| **TOTAL** | **27,250** | - | - |

---

## Contributing

When documenting new agents:

1. **Use Template**: Follow structure from existing agent docs
2. **YAML Frontmatter**: Include all required metadata fields
3. **API Reference**: Document constructor + all public methods
4. **Usage Examples**: Minimum 3 scenarios (simple → complex)
5. **Four Laws**: Explain how agent integrates with ethical framework
6. **Performance**: Include complexity analysis + benchmarks
7. **Troubleshooting**: Document common issues with solutions
8. **Cross-Reference**: Link to related agents and core systems

---

## Related Documentation

### Core Systems
- **[CognitionKernel](../core/cognition-kernel.md)**: Central governance hub that routes all agent operations
- **[Four Laws System](../core/four-laws-ethics.md)**: Ethical framework enforced by oversight
- **[Platform Tiers](../core/platform-tiers.md)**: Three-tier authority model (Agents in Tier 1 & 2)

### Other Agents
- **[Governed Planner Agent](../agents/planner-agent-governed.md)**: Modern replacement for legacy PlannerAgent
- **[Expert Agent](../agents/expert-agent.md)**: AI-powered problem solver
- **[Red Team Agent](../agents/red-team-agent.md)**: Security testing and adversarial validation

### Guides
- **[Agent Development Guide](../guides/agent-development.md)**: How to build new agents
- **[Kernel Integration Guide](../guides/kernel-integration.md)**: How to route operations through kernel
- **[Security Hardening](../guides/security-hardening.md)**: How to use ValidatorAgent for defense

---

## Changelog

### v1.0.0 (2026-04-20) - Initial Release
- Created comprehensive documentation for 4 core agents
- Added collaboration diagram
- Established documentation standards
- Total 27,250 words across 4 documents

---

## Maintainers

**Primary**: AGENT-033 (Source Code Documentation Specialist)
**Reviewers**: Architecture Team, Governance Team, AI Ethics Team
**Review Cycle**: Quarterly
**Next Review**: 2026-07-20

---

**END OF INDEX**

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
