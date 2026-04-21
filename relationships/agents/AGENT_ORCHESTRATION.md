# Agent Orchestration Architecture

**Agent Systems:** Oversight, Planner, Validator, Explainability  
**Integration Layer:** CognitionKernel, CouncilHub, KernelIntegration  
**Authority Model:** Three-Tier Platform Architecture  

---

## 1. Core Orchestration Model

### 1.1 Centralized Kernel Architecture

All four agent systems route through **CognitionKernel** - there is NO direct agent-to-agent communication:

```
┌─────────────────────────────────────────────────────────────┐
│                     CognitionKernel                          │
│  (Central Processing Hub - Tier 1 Governance Authority)     │
│                                                              │
│  • Enforces Four Laws & Triumvirate consensus               │
│  • Tracks execution history & identity drift                │
│  • Routes all agent operations via kernel.route()           │
│  • Provides pre/post execution hooks                        │
│  • Logs blocked actions for auditability                    │
└──────────────┬─────────────┬─────────────┬─────────────────┘
               │             │             │
    ┌──────────▼──┐   ┌─────▼─────┐   ┌──▼──────────┐
    │  Oversight  │   │  Planner  │   │  Validator  │
    │   Agent     │   │   Agent   │   │   Agent     │
    │             │   │           │   │             │
    │ Risk: Med   │   │ Risk: Low │   │ Risk: Low   │
    └─────────────┘   └───────────┘   └─────────────┘
                              │
                       ┌──────▼──────────┐
                       │ Explainability  │
                       │     Agent       │
                       │                 │
                       │   Risk: Low     │
                       └─────────────────┘
```

**Key Principles:**

1. **Single Entry Point:** `kernel.process()` or `kernel.route()` - no bypasses
2. **Mutation Control:** All state changes go through `kernel.commit()`
3. **Governance First:** Execution never governs, Governance never executes
4. **Auditability:** Even blocked actions are logged
5. **Authority Flows Down:** Tier 1 → Tier 2 → Tier 3 (governance direction)
6. **Capability Flows Up:** Tier 3 → Tier 2 → Tier 1 (data/telemetry direction)

### 1.2 Agent Initialization Pattern

All kernel-routed agents inherit from **KernelRoutedAgent** base class:

```python
# From src/app/agents/oversight.py, validator.py, explainability.py
from app.core.kernel_integration import KernelRoutedAgent
from app.core.cognition_kernel import CognitionKernel, ExecutionType

class OversightAgent(KernelRoutedAgent):
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",  # Oversight has moderate risk
        )
        self.enabled: bool = False
        self.monitors: dict = {}

class ValidatorAgent(KernelRoutedAgent):
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",  # Validation is low risk
        )
        self.enabled: bool = False
        self.validators: dict = {}

class ExplainabilityAgent(KernelRoutedAgent):
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",  # Explanation is low risk
        )
        self.enabled: bool = False
        self.explanations: dict = {}
```

**Note:** `planner.py` (legacy) is NOT kernel-routed, but `planner_agent.py` IS kernel-routed:

```python
# planner_agent.py (production version)
class PlannerAgent(KernelRoutedAgent):
    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )
        self.queue: list[dict[str, Any]] = []
        self._lock = threading.Lock()
```

### 1.3 Execution Flow Pattern

Agents use `_execute_through_kernel()` for all operations:

```python
# From planner_agent.py
def schedule(self, task: dict[str, Any]) -> None:
    """Schedule a task for execution."""
    return self._execute_through_kernel(
        action=self._do_schedule,
        action_name="PlannerAgent.schedule",
        action_args=(task,),
        requires_approval=False,
        risk_level="low",
        metadata={"task_name": task.get("name"), "operation": "schedule"},
    )

def _do_schedule(self, task: dict[str, Any]) -> None:
    """Internal implementation of task scheduling."""
    with self._lock:
        self.queue.append(task)
    logger.info("Task scheduled: %s", task.get("name"))
```

**Pattern Components:**

- **Public Method** (`schedule`): Routes through kernel
- **Internal Method** (`_do_schedule`): Contains actual implementation
- **Metadata**: Tracks operation details for governance
- **Risk Level**: Informs kernel's approval requirements

---

## 2. CouncilHub Coordination

**CouncilHub** (`src/app/core/council_hub.py`) serves as the **Tier-3 Runtime Service** coordinating agents:

### 2.1 CouncilHub Architecture

```
┌────────────────────────────────────────────────────────┐
│                    CouncilHub                          │
│              (Tier-3 Runtime Service)                  │
│                                                        │
│  Responsibilities:                                     │
│  • Register head (Project-AI) and smaller agents      │
│  • Run autonomous learning loop for head              │
│  • Route messages between agents                      │
│  • Consult Cerberus for content safety                │
│  • Enforce shutdown/cut communication                 │
│                                                        │
│  CRITICAL: All operations → kernel.route()            │
└────────────────┬───────────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
  ┌─────▼─────┐     ┌────▼──────────────┐
  │ Project-AI│     │  Smaller Agents   │
  │   (PA)    │     │      (SA)         │
  │           │     │                   │
  │ • Persona │     │ • PlannerAgent    │
  │ • Memory  │     │ • OversightAgent  │
  │ • Learning│     │ • ValidatorAgent  │
  └───────────┘     │ • Explainability  │
                    │ • ExpertAgent     │
                    │ • RefactorAgent   │
                    │ • SafetyGuard     │
                    │ • DocGenerator    │
                    │ • +15 others      │
                    └───────────────────┘
```

### 2.2 Agent Registration Pattern

```python
# From council_hub.py (lines 130-145)
def _initialize_agents(self):
    """Initialize all smaller agents."""
    if self.kernel is None:
        logger.warning("No kernel available - agents will operate unmanaged")
        return

    # Initialize Planner Agent with kernel routing
    self._project["planner"] = PlannerAgent(kernel=self.kernel)
    
    # Additional agents initialized similarly:
    # - SafetyGuardAgent(kernel=self.kernel)
    # - RefactorAgent(kernel=self.kernel)
    # - DocGenerator(kernel=self.kernel)
    # - TestQAGenerator(kernel=self.kernel)
    # - CodeAdversaryAgent(kernel=self.kernel)
    # - All routed through kernel for governance
```

### 2.3 Three-Tier Platform Hierarchy

```
Tier 1: GOVERNANCE (Sovereign Authority)
├── CognitionKernel
├── Triumvirate (FourLaws, Persona, Memory)
├── Black Vault
└── Constitutional Framework
    │
    ▼ (Authority flows DOWN)
    
Tier 2: ORCHESTRATION (Policy Enforcement)
├── Policy Engines
├── Workflow Managers
└── Service Brokers
    │
    ▼ (Authority flows DOWN)
    
Tier 3: APPLICATION (Sandboxed Services)
├── CouncilHub ← Runtime Service
├── Agents (Oversight, Planner, Validator, Explainability)
├── Tools & Plugins
└── UI Components
    │
    ▲ (Capability/Telemetry flows UP)
```

**Authority Levels:**

- **Tier 1:** `AuthorityLevel.SOVEREIGN` - Cannot be overridden
- **Tier 2:** `AuthorityLevel.ENFORCED` - Controlled by Tier 1
- **Tier 3:** `AuthorityLevel.SANDBOXED` - Subordinate to governance

**Key Constraint:** Tier-3 agents (Oversight, Planner, Validator, Explainability) have **NO enforcement authority**. They can:
- Analyze data
- Generate recommendations
- Log compliance issues
- Request governance decisions

But they **CANNOT:**
- Override Tier-1/2 decisions
- Bypass kernel routing
- Directly modify system state
- Execute without governance approval

---

## 3. Inter-Agent Communication

### 3.1 No Direct Agent-to-Agent Calls

**PROHIBITED PATTERN:**
```python
# ❌ NEVER DO THIS
oversight = OversightAgent()
planner = PlannerAgent()
oversight.check_plan(planner.get_current_plan())  # BYPASS!
```

**CORRECT PATTERN:**
```python
# ✅ ALWAYS ROUTE THROUGH KERNEL
oversight = OversightAgent(kernel=kernel)
planner = PlannerAgent(kernel=kernel)

# Planner schedules task → kernel governance
planner.schedule(task)

# Oversight monitors → kernel routing
kernel.route(
    task="monitor_compliance",
    source="oversight",
    metadata={"target": "planner"}
)
```

### 3.2 Cross-Agent Coordination via Kernel

```
User Request
    │
    ▼
┌───────────────────┐
│ CognitionKernel   │ ← Entry point
│  .process()       │
└────────┬──────────┘
         │
         ├─→ 1. Route to ValidatorAgent
         │   └─→ Validate input/state
         │       └─→ Return validation result
         │
         ├─→ 2. Route to PlannerAgent
         │   └─→ Decompose task
         │       └─→ Return execution plan
         │
         ├─→ 3. Route to OversightAgent
         │   └─→ Check compliance
         │       └─→ Return approval/block
         │
         ├─→ 4. Execute approved actions
         │
         └─→ 5. Route to ExplainabilityAgent
             └─→ Generate reasoning trace
                 └─→ Return explanation
```

### 3.3 Agent Coordination Metadata

Agents coordinate via **metadata payloads** in kernel routing:

```python
# PlannerAgent signals coordination need
kernel.route(
    task="decompose_task",
    source="planner",
    metadata={
        "requires_validation": True,
        "requires_oversight": True,
        "coordination_agents": ["validator", "oversight"],
        "operation": "task_decomposition",
    }
)

# Kernel orchestrates the sequence:
# 1. ValidatorAgent.validate_task_structure()
# 2. OversightAgent.check_compliance()
# 3. PlannerAgent.finalize_plan()
# 4. ExplainabilityAgent.explain_decisions()
```

---

## 4. Operational Extensions

### 4.1 Authority Scopes

Defined in `src/app/core/agent_operational_extensions.py`:

**PlannerAgent Authority:**
- **Task Decomposition:** Autonomous (max 20 subtasks, depth 5)
- **Planning Horizon:** Supervised (7 days autonomous, 30 days with approval)
- **Cross-Agent Calls:** Supervised (max 5 agents per plan)
- **Resource Allocation:** Supervised (budget constraints enforced)

**OversightAgent Authority:**
- **Monitoring:** Autonomous (read-only system state)
- **Compliance Checking:** Autonomous (policy validation)
- **Alert Generation:** Supervised (critical alerts require approval)
- **Action Blocking:** Escalated (must route to Tier-1 governance)

**ValidatorAgent Authority:**
- **Schema Validation:** Autonomous (type/structure checks)
- **Integrity Checking:** Autonomous (data consistency)
- **Sanitization:** Autonomous (input cleaning)
- **Error Handling:** Supervised (critical errors escalate)

**ExplainabilityAgent Authority:**
- **Reasoning Trace:** Autonomous (read-only access)
- **Explanation Generation:** Autonomous (transparency requirement)
- **Decision Log Access:** Read-only (audit trail)
- **Explanation Depth:** User-configurable (minimal → exhaustive)

### 4.2 Tool Access Map

From `agent_operational_extensions.py` (lines 792-823):

```python
# PlannerAgent Tool Access
{
    "task_decomposer": ToolAccessLevel.FULL_ACCESS,
    "resource_allocator": ToolAccessLevel.FULL_ACCESS,
    "agent_coordinator": ToolAccessLevel.LIMITED_WRITE,
    "memory_system": ToolAccessLevel.READ_ONLY,
    "governance_system": ToolAccessLevel.READ_ONLY,
}

# OversightAgent Tool Access
{
    "monitoring_dashboard": ToolAccessLevel.READ_ONLY,
    "compliance_checker": ToolAccessLevel.FULL_ACCESS,
    "alert_system": ToolAccessLevel.FULL_ACCESS,
    "audit_logger": ToolAccessLevel.FULL_ACCESS,
    "governance_system": ToolAccessLevel.READ_ONLY,
}

# ValidatorAgent Tool Access
{
    "schema_validator": ToolAccessLevel.FULL_ACCESS,
    "type_checker": ToolAccessLevel.FULL_ACCESS,
    "integrity_checker": ToolAccessLevel.FULL_ACCESS,
    "sanitizer": ToolAccessLevel.FULL_ACCESS,
}

# ExplainabilityAgent Tool Access
{
    "reasoning_tracer": ToolAccessLevel.READ_ONLY,
    "explanation_generator": ToolAccessLevel.FULL_ACCESS,
    "decision_log": ToolAccessLevel.READ_ONLY,
    "audit_system": ToolAccessLevel.READ_ONLY,
}
```

**Access Levels:**
- `NO_ACCESS`: Cannot use tool
- `READ_ONLY`: Can query, cannot modify
- `LIMITED_WRITE`: Can modify within constraints
- `FULL_ACCESS`: Unrestricted use (still governed by kernel)

### 4.3 Explanation Obligations

All agents MUST provide explanations via **ExplainabilityAgent**:

```python
# After any decision/action
kernel.route(
    task="explain_decision",
    source="explainability",
    metadata={
        "decision_id": execution_context.execution_id,
        "agent": "planner",
        "action": "task_decomposition",
        "depth": ExplanationDepth.STANDARD,
    }
)
```

**Explanation Depth Levels:**
- **MINIMAL:** "Task decomposed into 5 subtasks"
- **STANDARD:** "Task decomposed because X, chosen approach Y over Z"
- **DETAILED:** "Decomposition rationale, alternatives considered, trade-offs"
- **EXHAUSTIVE:** "Complete reasoning trace with evidence and confidence scores"

---

## 5. Lifecycle & State Management

### 5.1 Agent Activation Sequence

From `src/app/main.py` (lines 407-460):

```python
# 1. Initialize Kernel (Tier 1)
kernel = CognitionKernel(
    four_laws=four_laws,
    persona=persona,
    memory=memory
)

# 2. Activate Oversight Agent
oversight = OversightAgent(kernel=kernel)
council_hub.register_agent("oversight", oversight)
logger.info("✅ OversightAgent activated")

# 3. Activate Validator Agent
validator = ValidatorAgent(kernel=kernel)
council_hub.register_agent("validator", validator)
logger.info("✅ ValidatorAgent activated")

# 4. Activate Explainability Agent
explainability = ExplainabilityAgent(kernel=kernel)
council_hub.register_agent("explainability", explainability)
logger.info("✅ ExplainabilityAgent activated")

# 5. PlannerAgent registered via CouncilHub
# (See council_hub._initialize_agents())
```

### 5.2 State Persistence

All agents maintain **disabled state by default** (enabled = False):

```python
# Current state (placeholder design)
self.enabled: bool = False
self.monitors: dict = {}  # or validators/explanations/tasks

# Future implementation will add:
# - Persistent state in data/agents/{agent_name}/
# - JSON serialization like other systems
# - State recovery on restart
```

**Design Rationale:** Agents are currently **stubs** awaiting full implementation. The disabled state prevents incomplete features from affecting production while maintaining API stability.

---

## 6. Governance Integration

### 6.1 ExecutionContext Tracking

Every agent operation creates an **ExecutionContext**:

```python
@dataclass
class ExecutionContext:
    execution_id: str  # UUID
    execution_type: ExecutionType  # AGENT_ACTION
    action: Action  # Proposed action
    user_id: str
    metadata: dict
    status: ExecutionStatus  # PENDING → APPROVED → EXECUTING → COMPLETED
    governance_decision: dict | None
    result: Any | None
    error: str | None
    created_at: datetime
    completed_at: datetime | None
```

### 6.2 Governance Decision Flow

```
Agent requests action
    │
    ▼
kernel.route(task, source, metadata)
    │
    ▼
Create ExecutionContext
    │
    ▼
Four Laws Validation ─────→ BLOCKED? → Log & return
    │ (Law 1-4 hierarchy)          (audit preserved)
    │
    ▼ ALLOWED
    │
Triumvirate Consensus ─────→ DENIED? → Log & return
    │ (Persona, Memory check)      (user notified)
    │
    ▼ APPROVED
    │
Execute action
    │
    ▼
Record result in ExecutionContext
    │
    ▼
Update audit log
    │
    ▼
Return to caller
```

### 6.3 Failure Handling

From `agent_operational_extensions.py` - **FailureSemantics**:

```python
class FailureMode(Enum):
    FAIL_FAST = "fail_fast"          # Abort immediately
    FAIL_GRACEFUL = "fail_graceful"  # Return error, log
    FAIL_SILENT = "fail_silent"      # Log, continue
    FAIL_RETRY = "fail_retry"        # Retry with backoff
    FAIL_ESCALATE = "fail_escalate"  # Route to Tier-1

# PlannerAgent failure handling
PlannerFailureSemantics:
    task_decomposition_failure: FAIL_GRACEFUL
    resource_allocation_failure: FAIL_RETRY (3 attempts)
    cross_agent_coordination_failure: FAIL_ESCALATE

# OversightAgent failure handling
OversightFailureSemantics:
    monitoring_failure: FAIL_SILENT
    compliance_check_failure: FAIL_FAST
    alert_system_failure: FAIL_ESCALATE

# ValidatorAgent failure handling
ValidatorFailureSemantics:
    validation_failure: FAIL_FAST (invalid input rejected)
    integrity_check_failure: FAIL_ESCALATE
    sanitization_failure: FAIL_GRACEFUL

# ExplainabilityAgent failure handling
ExplainabilityFailureSemantics:
    explanation_generation_failure: FAIL_GRACEFUL (minimal explanation)
    trace_access_failure: FAIL_SILENT
```

---

## 7. Future Integration Points

### 7.1 Planned Agent Capabilities

**OversightAgent (Future):**
- Real-time system health monitoring
- Policy compliance dashboards
- Anomaly detection (drift from Four Laws)
- Automated alert escalation

**PlannerAgent (Future):**
- Multi-agent task orchestration
- Resource optimization algorithms
- Dependency resolution
- Rollback/recovery planning

**ValidatorAgent (Future):**
- Schema validation (JSON, XML, Protocol Buffers)
- Type checking (Python, TypeScript)
- Data integrity verification (checksums, signatures)
- Input sanitization (XSS, SQL injection prevention)

**ExplainabilityAgent (Future):**
- LIME/SHAP integration for ML models
- Decision tree visualization
- Counterfactual explanations ("What if X was Y?")
- Confidence scoring for decisions

### 7.2 Integration with External Systems

```
CognitionKernel
    │
    ├─→ External AI Services (OpenAI, HuggingFace)
    │   └─→ Routed through kernel.route()
    │
    ├─→ Database Systems (PostgreSQL, SQLite)
    │   └─→ Validated by ValidatorAgent
    │
    ├─→ File Systems
    │   └─→ Monitored by OversightAgent
    │
    └─→ User Interfaces (PyQt6, React)
        └─→ Explained by ExplainabilityAgent
```

---

## 8. Security & Compliance

### 8.1 Agent Isolation

- **No Shared State:** Each agent has isolated state (monitors/validators/explanations/tasks)
- **Kernel-Mediated Access:** All data sharing via kernel routing
- **Read-Only Governance:** Agents can READ governance state, not WRITE
- **Audit Trail:** Every agent action logged in ExecutionContext

### 8.2 Privilege Escalation Prevention

```python
# BLOCKED: Agent attempts to modify governance
agent.kernel.four_laws.hierarchy[0] = "New Law"  # READ-ONLY
→ AttributeError: Cannot set attribute

# BLOCKED: Agent bypasses kernel
agent._direct_execute()  # No such method
→ AttributeError: Method not found

# BLOCKED: Agent modifies another agent
oversight.planner.queue.clear()  # No direct reference
→ AttributeError: Agent isolation enforced

# ALLOWED: Agent requests governance decision
kernel.route(
    task="modify_hierarchy",
    source="oversight",
    metadata={"justification": "Critical safety issue"}
)
→ Routed to Triumvirate for consensus
```

### 8.3 Audit Requirements

All agents MUST log:
- **What:** Action taken
- **Why:** Justification/reasoning
- **When:** Timestamp (UTC)
- **Who:** User ID + agent ID
- **Result:** Success/failure + error details
- **Governance:** Approval/denial decision

Audit logs stored in:
- `ExecutionContext.governance_decision`
- `data/audit_logs/agents/{agent_name}/`
- CognitionKernel execution history

---

## 9. Development Guidelines

### 9.1 Adding New Agent Operations

```python
# 1. Define public method with kernel routing
def new_operation(self, arg1: str, arg2: int) -> Result:
    """Public API - routes through kernel."""
    return self._execute_through_kernel(
        action=self._do_new_operation,
        action_name="AgentName.new_operation",
        action_args=(arg1, arg2),
        requires_approval=True,  # High-risk operations
        risk_level="medium",
        metadata={
            "arg1": arg1,
            "arg2": arg2,
            "operation": "new_operation",
        },
    )

# 2. Define internal implementation
def _do_new_operation(self, arg1: str, arg2: int) -> Result:
    """Internal implementation - no governance."""
    # Actual logic here
    result = perform_operation(arg1, arg2)
    logger.info("Operation completed: %s", result)
    return result
```

### 9.2 Testing Agent Operations

```python
# tests/test_agents.py
import pytest
from app.core.cognition_kernel import CognitionKernel
from app.agents.oversight import OversightAgent

def test_oversight_monitoring():
    kernel = CognitionKernel(...)
    oversight = OversightAgent(kernel=kernel)
    
    # Test kernel routing
    result = oversight.monitor_system_health()
    
    # Verify governance tracking
    assert kernel.execution_history[-1].execution_type == ExecutionType.AGENT_ACTION
    assert kernel.execution_history[-1].status == ExecutionStatus.COMPLETED
    
    # Verify result
    assert result["status"] == "healthy"
```

### 9.3 Agent Registration Checklist

- [ ] Inherit from `KernelRoutedAgent`
- [ ] Initialize with `kernel` parameter
- [ ] Set appropriate `execution_type` and `default_risk_level`
- [ ] Use `_execute_through_kernel()` for all public methods
- [ ] Implement internal `_do_*()` methods
- [ ] Register in `CouncilHub._initialize_agents()`
- [ ] Add tool access map in `agent_operational_extensions.py`
- [ ] Define decision authorities and failure semantics
- [ ] Export from `src/app/agents/__init__.py`
- [ ] Add tests for kernel integration
- [ ] Document in AGENT_ORCHESTRATION.md

---

## 10. Summary

**Agent Orchestration Principles:**

1. **Centralized Governance:** CognitionKernel is the ONLY execution path
2. **No Direct Communication:** Agents never call each other directly
3. **Metadata-Driven Coordination:** Coordination via kernel routing metadata
4. **Three-Tier Hierarchy:** Agents are Tier-3 (sandboxed, non-sovereign)
5. **Tool Access Control:** Fine-grained permissions per agent
6. **Explanation Obligation:** All decisions must be explainable
7. **Failure Handling:** Defined semantics per operation type
8. **Audit Requirement:** Every action logged in ExecutionContext
9. **Privilege Isolation:** Agents cannot bypass governance
10. **Future Extensibility:** Stub design allows gradual feature rollout

**Current State:**
- 4 core agents implemented as **stubs** (enabled=False)
- Full kernel integration architecture complete
- CouncilHub coordination layer operational
- Governance routing functional
- Production features deferred to future phases

**Next Steps:**
- Enable agents incrementally with feature flags
- Implement monitoring/validation/planning logic
- Add real-time dashboards for oversight
- Integrate external AI services for explainability
- Build testing infrastructure for agent orchestration

---

**File:** `relationships/agents/AGENT_ORCHESTRATION.md`  
**Version:** 1.0  
**Last Updated:** 2025-01-27  
**Related:** VALIDATION_CHAINS.md, PLANNING_HIERARCHIES.md, AGENT_TOOL_ACCESS.md

---

## 📁 Source Code References

This documentation references the following source files:

- [[src/app/agents/explainability.py]]
- [[src/app/agents/oversight.py]]
- [[src/app/agents/planner_agent.py]]
- [[src/app/agents/validator.py]]

---


---

## RELATED SYSTEMS

### GUI Integration ([[../gui/00_MASTER_INDEX|GUI Master Index]])

| GUI Component | Kernel Integration | Data Flow | Documentation |
|---------------|-------------------|-----------|---------------|
| [[../gui/03_HANDLER_RELATIONSHIPS\|DashboardHandlers]] | Desktop Adapter → Router → Kernel | All actions routed | Section 3 governance pattern |
| [[../gui/05_PERSONA_PANEL_RELATIONSHIPS\|PersonaPanel]] | Trait updates via kernel | Slider → adapter → kernel → [[../core-ai/02-AIPersona-Relationship-Map\|AIPersona]] | Section 3 signal flow |
| [[../gui/04_UTILS_RELATIONSHIPS\|AsyncWorker]] | Background kernel operations | QThread → kernel.process() → result signal | Section 3 async pattern |
| [[../gui/01_DASHBOARD_RELATIONSHIPS\|Dashboard]] | Message routing | UserChat → kernel → Intelligence | Section 2.1 message flow |
| [[../gui/06_IMAGE_GENERATION_RELATIONSHIPS\|ImageGeneration]] | Content validation | Prompt → kernel → Four Laws check | Section 4 safety pipeline |

### Core AI Integration ([[../core-ai/00-INDEX|Core AI Index]])

| Core System | Kernel Role | Integration | Documentation |
|-------------|-------------|-------------|---------------|
| [[../core-ai/01-FourLaws-Relationship-Map\|FourLaws]] | Ethics enforcement | kernel.process() → validate_action() | Section 6.2 governance flow |
| [[../core-ai/02-AIPersona-Relationship-Map\|AIPersona]] | Personality routing | CouncilHub shares traits with agents | Section 2.2 agent registration |
| [[../core-ai/03-MemoryExpansionSystem-Relationship-Map\|Memory]] | Decision history | ExecutionContext → Memory.log() | Section 5.2 state persistence |
| [[../core-ai/04-LearningRequestManager-Relationship-Map\|Learning]] | Approval workflow | Learning requests route via kernel | Section 6.2 governance flow |
| [[../core-ai/05-PluginManager-Relationship-Map\|Plugins]] | Plugin coordination | Plugins register with CouncilHub | Section 2.2 registration |
| [[../core-ai/06-CommandOverride-Relationship-Map\|Override]] | Bypass detection | ExecutionContext tracks override state | Section 6.1 context tracking |

### Orchestration Patterns

**GUI → Kernel → Core AI:**
```
[[../gui/03_HANDLER_RELATIONSHIPS|Handler Event]] → 
Desktop Adapter.execute() → 
Router.route_to_system() → 
CognitionKernel.process() → 
[[../core-ai/01-FourLaws-Relationship-Map|FourLaws Check]] → 
Core System → Response → 
[[../gui/01_DASHBOARD_RELATIONSHIPS|Dashboard Update]]
```

**Agent Coordination:**
```
PlannerAgent → CouncilHub.coordinate() → 
OversightAgent.monitor() → 
ValidatorAgent.check() → 
ExecutionContext.log() → 
[[../core-ai/03-MemoryExpansionSystem-Relationship-Map|Memory.persist()]]
```

---

**Enhanced by:** AGENT-078: GUI & Agent Cross-Links Specialist  
**Status:** ✅ Cross-linked with GUI and Core AI systems
