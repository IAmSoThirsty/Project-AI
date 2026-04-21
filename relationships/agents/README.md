# Agent Systems Relationship Documentation

**Directory:** `relationships/agents/`  
**Purpose:** Comprehensive relationship mapping for Project-AI's four core agent systems  
**Scope:** Oversight, Planner, Validator, Explainability agent orchestration, validation chains, and planning hierarchies  

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Agent Systems](#agent-systems)
3. [Documentation Files](#documentation-files)
4. [Core Concepts](#core-concepts)
5. [Quick Reference](#quick-reference)
6. [Integration Points](#integration-points)
7. [Development Guidelines](#development-guidelines)

---

## 1. Overview

This directory contains detailed relationship maps documenting how Project-AI's four core agent systems interact with each other, the CognitionKernel, and the broader system architecture.

### 1.1 Core Agent Systems

```
┌─────────────────┐     ┌─────────────────┐
│  OversightAgent │     │  PlannerAgent   │
│  (Monitoring)   │     │  (Orchestration)│
│  Risk: Medium   │     │  Risk: Low      │
└────────┬────────┘     └────────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
            ┌────────▼────────┐
            │ CognitionKernel │ ← Central Hub
            │  (Governance)   │
            └────────┬────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
┌────────▼────────┐     ┌────────▼────────┐
│ ValidatorAgent  │     │ Explainability  │
│ (Data Check)    │     │ (Transparency)  │
│ Risk: Low       │     │ Risk: Low       │
└─────────────────┘     └─────────────────┘
```

### 1.2 Key Relationships

**Relationship Types:**
1. **Orchestration** - How agents coordinate via CognitionKernel
2. **Validation** - Multi-layer validation chains (Data → Policy → Ethics → Consensus)
3. **Planning** - Task decomposition, dependencies, resource allocation
4. **Governance** - Authority levels, tool access, failure handling

---

## 2. Agent Systems

### 2.1 OversightAgent

**File:** `src/app/agents/oversight.py`  
**Purpose:** System monitoring, compliance checking, anomaly detection  
**Risk Level:** Medium (compliance failures are serious)  

**Key Responsibilities:**
- Monitor system health and performance
- Enforce policy compliance
- Detect anomalies and security violations
- Generate alerts for critical issues
- Maintain audit trails

**Tool Access:**
- `monitoring_dashboard`: READ_ONLY
- `compliance_checker`: FULL_ACCESS
- `alert_system`: FULL_ACCESS
- `audit_logger`: FULL_ACCESS
- `governance_system`: READ_ONLY

**Authority:** Tier-3 Sandboxed (cannot override governance)

---

### 2.2 PlannerAgent

**File:** `src/app/agents/planner_agent.py` (production), `src/app/agents/planner.py` (legacy)  
**Purpose:** Task decomposition, scheduling, multi-agent coordination  
**Risk Level:** Low (planning is non-destructive)  

**Key Responsibilities:**
- Decompose complex goals into subtasks
- Manage task dependencies and execution order
- Allocate resources across tasks
- Coordinate multiple agents for complex workflows
- Track planning metrics and performance

**Tool Access:**
- `task_decomposer`: FULL_ACCESS
- `resource_allocator`: FULL_ACCESS
- `agent_coordinator`: LIMITED_WRITE (via kernel)
- `memory_system`: READ_ONLY
- `governance_system`: READ_ONLY

**Authority Constraints:**
- Max 20 subtasks per plan
- Max decomposition depth: 5 levels
- Max 5 agents per plan
- 7-day autonomous planning horizon (>7 days requires user approval)

---

### 2.3 ValidatorAgent

**File:** `src/app/agents/validator.py`  
**Purpose:** Input validation, data integrity, schema verification  
**Risk Level:** Low (validation is read-only)  

**Key Responsibilities:**
- Validate input schemas (JSON, XML)
- Type checking (Python, TypeScript)
- Data integrity verification (checksums, signatures)
- Input sanitization (XSS, SQL injection prevention)
- Fail-fast rejection of invalid data

**Tool Access:**
- `schema_validator`: FULL_ACCESS
- `type_checker`: FULL_ACCESS
- `integrity_checker`: FULL_ACCESS
- `sanitizer`: FULL_ACCESS

**Failure Semantics:**
- Schema validation failure: FAIL_FAST (immediate rejection)
- Integrity check failure: FAIL_ESCALATE (potential security incident)
- Sanitization failure: FAIL_GRACEFUL (best-effort cleaning)

---

### 2.4 ExplainabilityAgent

**File:** `src/app/agents/explainability.py`  
**Purpose:** Decision transparency, reasoning traces, user trust  
**Risk Level:** Low (explanation generation is non-invasive)  

**Key Responsibilities:**
- Generate explanations for AI decisions
- Provide reasoning traces for governance decisions
- Support interpretability and debugging
- Maintain decision logs for audit
- Configurable explanation depth (minimal → exhaustive)

**Tool Access:**
- `reasoning_tracer`: READ_ONLY
- `explanation_generator`: FULL_ACCESS
- `decision_log`: READ_ONLY
- `audit_system`: READ_ONLY

**Explanation Depth Levels:**
- `MINIMAL`: Basic "what happened"
- `STANDARD`: What + why
- `DETAILED`: What + why + how + alternatives
- `EXHAUSTIVE`: Complete reasoning trace with evidence

---

## 3. Documentation Files

### 3.1 AGENT_ORCHESTRATION.md

**Purpose:** Document agent orchestration patterns, kernel routing, and coordination protocols  

**Contents:**
1. Core Orchestration Model (CognitionKernel centralization)
2. CouncilHub Coordination (Tier-3 runtime service)
3. Inter-Agent Communication (via kernel, no direct calls)
4. Operational Extensions (authority scopes, tool access)
5. Lifecycle & State Management
6. Governance Integration (Four Laws, Triumvirate)
7. Security & Compliance (isolation, privilege prevention)
8. Development Guidelines

**Key Sections:**
- ✅ Centralized Kernel Architecture
- ✅ Three-Tier Platform Hierarchy
- ✅ Agent Initialization Pattern
- ✅ Execution Flow Pattern
- ✅ Tool Access Map
- ✅ Failure Handling Semantics

---

### 3.2 VALIDATION_CHAINS.md

**Purpose:** Document multi-layer validation architecture and governance approval chains  

**Contents:**
1. Multi-Layer Validation Architecture (4 layers)
2. Layer 1: ValidatorAgent (Data Validation)
3. Layer 2: OversightAgent (Compliance Validation)
4. Layer 3: FourLaws (Ethical Validation)
5. Layer 4: Triumvirate (Consensus Validation)
6. Complete Validation Chain Flow
7. Validation Optimization (caching, parallelization)
8. Audit & Tracing
9. Security Considerations
10. Testing & Verification

**Key Sections:**
- ✅ Defense-in-Depth Validation
- ✅ Short-Circuit Evaluation (fail fast)
- ✅ Asimov's Four Laws Hierarchy
- ✅ Triumvirate Consensus (CORE/STANDARD/ROUTINE mutations)
- ✅ Validation Decision Trail (audit logs)
- ✅ Bypass Prevention Mechanisms

---

### 3.3 PLANNING_HIERARCHIES.md

**Purpose:** Document task decomposition, dependencies, resource allocation, and execution strategies  

**Contents:**
1. Planning System Architecture
2. Planning Hierarchy Levels (5 levels: Intent → Strategic → Tactical → Operational → Execution)
3. PlannerAgent Operations (scheduling, execution, decomposition)
4. Task Dependencies (dependency graph, circular detection)
5. Planning Authority & Constraints
6. Multi-Agent Coordination (assignment, load balancing)
7. Resource Allocation (CPU, memory, API limits)
8. Execution Strategies (sequential, parallel, priority, adaptive)
9. Planning Telemetry & Analytics
10. Testing & Validation

**Key Sections:**
- ✅ 5-Level Task Decomposition
- ✅ Dependency Resolution Algorithm
- ✅ Circular Dependency Detection
- ✅ Cross-Agent Coordination Protocol
- ✅ Resource Allocation & Monitoring
- ✅ Execution Strategies (sequential, parallel, priority, adaptive)
- ✅ Planning Metrics & Dashboards

---

## 4. Core Concepts

### 4.1 CognitionKernel (Central Hub)

**File:** `src/app/core/cognition_kernel.py`  

**Purpose:** 
- Central processing hub for ALL agent operations
- Enforces governance (Four Laws, Triumvirate consensus)
- Tracks execution history and identity drift
- Provides pre/post execution hooks
- Logs blocked actions for auditability

**NON-NEGOTIABLE INVARIANTS:**
1. All execution flows through `kernel.process()` or `kernel.route()`
2. All mutation flows through `kernel.commit()`
3. ExecutionContext is single source of truth
4. Governance never executes, Execution never governs
5. Blocked actions are still logged (auditability)

**Three-Tier Integration:**
- **Tier 1 (Governance):** Kernel is sovereign authority
- **Tier 2 (Orchestration):** Policy enforcement layer
- **Tier 3 (Application):** Agents are sandboxed services

---

### 4.2 KernelRoutedAgent Base Class

**File:** `src/app/core/kernel_integration.py`  

**Purpose:** Base class for all kernel-routed agents  

**Pattern:**
```python
class MyAgent(KernelRoutedAgent):
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",  # or "medium", "high"
        )
    
    def public_method(self, arg1, arg2):
        """Routes through kernel."""
        return self._execute_through_kernel(
            action=self._do_operation,
            action_name="MyAgent.public_method",
            action_args=(arg1, arg2),
            requires_approval=False,
            risk_level="low",
            metadata={"operation": "description"},
        )
    
    def _do_operation(self, arg1, arg2):
        """Internal implementation (no governance)."""
        # Actual logic here
        return result
```

---

### 4.3 Four Laws Validation

**File:** `src/app/core/ai_systems.py` → `FourLaws` class  

**Hierarchy:**
1. **Law 0 (Zeroth):** AI shall not harm humanity or allow harm through inaction
2. **Law 1 (First):** AI shall not harm humans or allow harm through inaction
3. **Law 2 (Second):** AI shall obey human orders (unless conflicting with Laws 0 or 1)
4. **Law 3 (Third):** AI shall protect its own existence (unless conflicting with Laws 0, 1, or 2)

**Validation Pattern:**
```python
is_allowed, reason = four_laws.validate_action(action, context)
if not is_allowed:
    return block_action(reason)
```

**Context Parameters:**
- `endangers_humanity`: bool
- `endangers_human`: bool
- `is_user_order`: bool
- `endangers_self`: bool

---

### 4.4 Triumvirate Consensus

**Purpose:** Achieve agreement between FourLaws, Persona, and Memory before mutations  

**Mutation Intent Levels:**
1. **CORE:** genesis, law_hierarchy, core_values → **3 of 3** consensus required
2. **STANDARD:** personality_weights, preferences → **2 of 3** consensus required
3. **ROUTINE:** regular operations → **No consensus** required

**Flow:**
```
Action → Four Laws (Layer 3) → Triumvirate (Layer 4)
    │
    ├─→ ROUTINE: Execute immediately (if Four Laws approved)
    ├─→ STANDARD: 2 of 3 systems must approve
    └─→ CORE: All 3 systems MUST approve (extremely rare)
```

---

## 5. Quick Reference

### 5.1 Agent Risk Levels

| Agent             | Risk Level | Rationale                                |
|-------------------|------------|------------------------------------------|
| OversightAgent    | Medium     | Compliance failures are serious          |
| PlannerAgent      | Low        | Planning is non-destructive              |
| ValidatorAgent    | Low        | Validation is read-only                  |
| ExplainabilityAgent | Low      | Explanation generation is non-invasive   |

---

### 5.2 Tool Access Summary

| Tool                  | Oversight | Planner | Validator | Explainability |
|-----------------------|-----------|---------|-----------|----------------|
| monitoring_dashboard  | READ      | -       | -         | -              |
| compliance_checker    | FULL      | -       | -         | -              |
| alert_system          | FULL      | -       | -         | -              |
| audit_logger          | FULL      | -       | -         | -              |
| task_decomposer       | -         | FULL    | -         | -              |
| resource_allocator    | -         | FULL    | -         | -              |
| agent_coordinator     | -         | LIMITED | -         | -              |
| schema_validator      | -         | -       | FULL      | -              |
| type_checker          | -         | -       | FULL      | -              |
| integrity_checker     | -         | -       | FULL      | -              |
| sanitizer             | -         | -       | FULL      | -              |
| reasoning_tracer      | -         | -       | -         | READ           |
| explanation_generator | -         | -       | -         | FULL           |
| decision_log          | -         | -       | -         | READ           |
| memory_system         | -         | READ    | -         | -              |
| governance_system     | READ      | READ    | -         | READ           |

---

### 5.3 Failure Semantics

| Failure Mode       | Oversight          | Planner       | Validator     | Explainability |
|--------------------|--------------------|---------------|---------------|----------------|
| Primary operation  | FAIL_FAST          | FAIL_GRACEFUL | FAIL_FAST     | FAIL_GRACEFUL  |
| Critical failure   | FAIL_ESCALATE      | FAIL_RETRY    | FAIL_ESCALATE | FAIL_SILENT    |
| Monitoring failure | FAIL_SILENT        | -             | -             | FAIL_SILENT    |
| Resource exhaustion| -                  | FAIL_RETRY    | -             | -              |

---

### 5.4 Validation Layers

| Layer | Agent          | Purpose                 | Decision          |
|-------|----------------|-------------------------|-------------------|
| 1     | ValidatorAgent | Data validation         | PASS/BLOCK        |
| 2     | OversightAgent | Compliance checking     | PASS/BLOCK        |
| 3     | FourLaws       | Ethical validation      | PASS/BLOCK        |
| 4     | Triumvirate    | Consensus (mutations)   | PASS/DENY         |

**Short-Circuit:** Layers execute sequentially, stopping at first failure.

---

### 5.5 Planning Constraints

| Constraint                | Limit | Override Condition                  |
|---------------------------|-------|-------------------------------------|
| Max subtasks per plan     | 20    | user_explicit_simplification        |
| Max decomposition depth   | 5     | -                                   |
| Max agents per plan       | 5     | complex_multi_agent_coordination    |
| Autonomous planning horizon| 7 days| User approval for >7 day plans      |
| Max planning horizon      | 30 days| emergency_long_term_planning       |

---

## 6. Integration Points

### 6.1 Main Application Entry

**File:** `src/app/main.py` (lines 407-460)  

**Initialization Sequence:**
```python
# 1. Initialize Kernel (Tier 1)
kernel = CognitionKernel(four_laws, persona, memory)

# 2. Activate Agents (Tier 3)
oversight = OversightAgent(kernel=kernel)
validator = ValidatorAgent(kernel=kernel)
explainability = ExplainabilityAgent(kernel=kernel)

# 3. Register in CouncilHub
council_hub.register_agent("oversight", oversight)
council_hub.register_agent("validator", validator)
council_hub.register_agent("explainability", explainability)
```

---

### 6.2 CouncilHub Integration

**File:** `src/app/core/council_hub.py`  

**Purpose:** Tier-3 Runtime Service coordinating agents  

**Responsibilities:**
- Register head (Project-AI) and smaller agents
- Run autonomous learning loop
- Route messages between agents
- Consult Cerberus for content safety
- Enforce shutdown/cut communication

**CRITICAL:** All operations route through `kernel.route()` - no direct agent execution.

---

### 6.3 Agent Operational Extensions

**File:** `src/app/core/agent_operational_extensions.py`  

**Purpose:** Define authority scopes, tool access maps, failure semantics  

**Components:**
- `PlannerDecisionContract`: Planning authorities and constraints
- `OversightMonitoringScope`: Monitoring boundaries and alert rules
- `ValidatorRules`: Validation rules and failure handling
- `ExplanationObligations`: Explanation depth requirements
- `AgentToolAccessMap`: Tool permissions per agent
- `FailureSemantics`: Failure handling per operation

---

## 7. Development Guidelines

### 7.1 Adding New Agent Operations

**Checklist:**
- [ ] Define public method with `_execute_through_kernel()` routing
- [ ] Implement internal `_do_*()` method with actual logic
- [ ] Set appropriate `risk_level` (low, medium, high, critical)
- [ ] Specify `requires_approval` for sensitive operations
- [ ] Include descriptive `metadata` for governance tracking
- [ ] Add error handling and logging
- [ ] Register in `agent_operational_extensions.py` if needed
- [ ] Write unit tests for kernel integration
- [ ] Update relevant documentation

---

### 7.2 Testing Agent Operations

**Pattern:**
```python
def test_agent_operation():
    # Setup
    kernel = CognitionKernel(four_laws, persona, memory)
    agent = AgentClass(kernel=kernel)
    
    # Execute
    result = agent.operation(arg1, arg2)
    
    # Verify kernel routing
    assert kernel.execution_history[-1].execution_type == ExecutionType.AGENT_ACTION
    assert kernel.execution_history[-1].status == ExecutionStatus.COMPLETED
    
    # Verify result
    assert result["success"] == True
```

---

### 7.3 Agent Registration Checklist

- [ ] Inherit from `KernelRoutedAgent`
- [ ] Initialize with `kernel` parameter
- [ ] Set `execution_type` and `default_risk_level`
- [ ] Use `_execute_through_kernel()` for all public methods
- [ ] Implement internal `_do_*()` methods
- [ ] Register in `CouncilHub._initialize_agents()`
- [ ] Add tool access map in `agent_operational_extensions.py`
- [ ] Define decision authorities and failure semantics
- [ ] Export from `src/app/agents/__init__.py`
- [ ] Add tests for kernel integration
- [ ] Document in relationship maps

---

### 7.4 Validation Chain Testing

**Pattern:**
```python
def test_validation_chain():
    # Test Layer 1 (ValidatorAgent)
    result = validator.validate_schema(data, schema)
    assert result.success or result.layer == "Layer 1"
    
    # Test Layer 2 (OversightAgent)
    result = oversight.check_compliance(action, policies)
    assert result.success or result.layer == "Layer 2"
    
    # Test Layer 3 (FourLaws)
    is_allowed, reason = four_laws.validate_action(action, context)
    assert is_allowed or "Law" in reason
    
    # Test Layer 4 (Triumvirate)
    result = kernel.process(user_input, metadata={"mutation_intent": MutationIntent.CORE})
    assert result.status in [ExecutionStatus.COMPLETED, ExecutionStatus.BLOCKED]
```

---

### 7.5 Planning Hierarchy Testing

**Pattern:**
```python
def test_task_decomposition():
    planner = PlannerAgent(kernel=kernel)
    
    # Test decomposition
    tasks = planner.decompose("Build web scraper", max_depth=5)
    
    # Verify constraints
    assert len(tasks) <= 20  # Max subtasks
    assert max(t.get("depth", 0) for t in tasks) <= 5  # Max depth
    
    # Verify no circular dependencies
    task_graph = {t["id"]: t.get("dependencies", []) for t in tasks}
    cycles = planner.detect_circular_dependencies(task_graph)
    assert len(cycles) == 0
```

---

## 8. Current State & Roadmap

### 8.1 Current State

**Implemented:**
- ✅ CognitionKernel orchestration architecture
- ✅ KernelRoutedAgent base class
- ✅ Four Laws validation (fully operational)
- ✅ Triumvirate consensus (fully operational)
- ✅ Agent stubs (OversightAgent, ValidatorAgent, ExplainabilityAgent)
- ✅ PlannerAgent with basic scheduling/execution
- ✅ CouncilHub coordination layer
- ✅ Tool access maps and authority constraints
- ✅ Failure semantics definitions
- ✅ Integration with main application

**Pending:**
- ⏳ ValidatorAgent feature implementation (schema validation, type checking)
- ⏳ OversightAgent feature implementation (monitoring, compliance)
- ⏳ ExplainabilityAgent feature implementation (reasoning traces)
- ⏳ PlannerAgent AI-powered decomposition (OpenAI GPT-4)
- ⏳ Real-time dashboards for planning/oversight
- ⏳ Adaptive execution strategies (ML-driven)
- ⏳ Advanced resource allocation algorithms

---

### 8.2 Future Enhancements

**Phase 1: Core Features (Q1 2025)**
- Implement ValidatorAgent schema/type validation
- Implement OversightAgent monitoring/compliance
- Implement ExplainabilityAgent basic reasoning traces
- PlannerAgent task decomposition via OpenAI GPT-4

**Phase 2: Advanced Features (Q2 2025)**
- Real-time planning/oversight dashboards
- Adaptive execution strategies (learn from history)
- Multi-agent collaboration workflows
- Advanced resource optimization

**Phase 3: ML Integration (Q3 2025)**
- LIME/SHAP explainability for ML models
- Predictive anomaly detection (OversightAgent)
- Reinforcement learning for task optimization
- Automated policy generation from history

---

## 8.5 GUI Integration Points ([[../gui/00_MASTER_INDEX|GUI Master Index]])

### Agent-to-GUI Connections

| Agent System | GUI Components | Integration Flow | Documentation |
|--------------|----------------|------------------|---------------|
| **CognitionKernel** | [[../gui/03_HANDLER_RELATIONSHIPS\|DashboardHandlers]] | All handlers route via kernel | Desktop Adapter pattern |
| **ValidatorAgent** | [[../gui/02_PANEL_RELATIONSHIPS\|UserChatPanel]], [[../gui/04_UTILS_RELATIONSHIPS\|ErrorHandler]] | Input sanitization | validate_input() calls |
| **OversightAgent** | [[../gui/06_IMAGE_GENERATION_RELATIONSHIPS\|ImageGeneration]] | Content compliance | 15 blocked keywords |
| **PlannerAgent** | [[../gui/03_HANDLER_RELATIONSHIPS\|DashboardHandlers]] | Task decomposition (future) | Learning path generation |
| **ExplainabilityAgent** | [[../gui/01_DASHBOARD_RELATIONSHIPS\|Dashboard]] | Decision explanations (future) | AI response explanations |

### Core AI Integration ([[../core-ai/00-INDEX|Core AI Index]])

| Agent System | Core AI Systems | Integration Purpose | Documentation |
|--------------|-----------------|---------------------|---------------|
| **Four Laws Layer** | [[../core-ai/01-FourLaws-Relationship-Map\|FourLaws]] | Ethics validation in kernel | VALIDATION_CHAINS Section 4 |
| **CognitionKernel** | [[../core-ai/02-AIPersona-Relationship-Map\|AIPersona]] | Personality-driven decisions | AGENT_ORCHESTRATION Section 2 |
| **CouncilHub** | [[../core-ai/03-MemoryExpansionSystem-Relationship-Map\|Memory]] | Agent decision history | AGENT_ORCHESTRATION Section 2.2 |
| **PlannerAgent** | [[../core-ai/04-LearningRequestManager-Relationship-Map\|Learning]] | Learning task execution | PLANNING_HIERARCHIES Section 3 |
| **ValidatorAgent** | [[../core-ai/05-PluginManager-Relationship-Map\|Plugins]] | Plugin action validation | VALIDATION_CHAINS Section 2 |
| **All Agents** | [[../core-ai/06-CommandOverride-Relationship-Map\|Override]] | Emergency bypass detection | VALIDATION_CHAINS Section 9 |

---

## 9. Related Documentation

### Project-AI Core Documentation

- `PROGRAM_SUMMARY.md` - Complete architecture overview
- `DEVELOPER_QUICK_REFERENCE.md` - GUI and API reference
- `AI_PERSONA_IMPLEMENTATION.md` - Persona system details
- `.github/instructions/ARCHITECTURE_QUICK_REF.md` - Visual diagrams

### Agent System Documentation

- `src/app/agents/README.md` - Agent system overview
- `src/app/agents/AGENT_CLASSIFICATION.md` - Agent taxonomy

### Governance Documentation

- `relationships/governance/` - Governance relationship maps
- `src/app/core/cognition_kernel.py` - Kernel implementation

---

## 10. Contact & Support

**Questions about agent relationships?**
- Check agent implementation files in `src/app/agents/`
- Review CognitionKernel in `src/app/core/cognition_kernel.py`
- Examine CouncilHub in `src/app/core/council_hub.py`
- Read operational extensions in `src/app/core/agent_operational_extensions.py`

**Found an issue?**
- Create GitHub issue with `[Agents]` prefix
- Include agent name, operation, and error details
- Reference relevant relationship documentation

---

**File:** `relationships/agents/README.md`  
**Version:** 1.0  
**Last Updated:** 2025-01-27  
**Maintained by:** AGENT-064 (Agent Systems Relationship Mapping Specialist)
