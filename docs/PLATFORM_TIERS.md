# Platform Tiers Documentation

**Three-Tier Platform Strategy - Complete Specification**

This document provides comprehensive documentation for the three-tier platform architecture implemented in Project-AI.

---

## Table of Contents

1. [Overview](#overview)
2. [Tier 1: Governance / Enforcement Platform](#tier-1-governance--enforcement-platform)
3. [Tier 2: Infrastructure Control Platform](#tier-2-infrastructure-control-platform)
4. [Tier 3: Application / Runtime Platform](#tier-3-application--runtime-platform)
5. [Cross-Tier Communication](#cross-tier-communication)
6. [API Boundaries](#api-boundaries)
7. [Governance Policies](#governance-policies)
8. [Health Monitoring](#health-monitoring)
9. [Examples and Usage](#examples-and-usage)

---

## Overview

Project-AI implements a formal three-tier platform architecture with strict separation of concerns and authority flow constraints:

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: Governance / Enforcement Platform                   │
│ ├─ CognitionKernel (Trust Root)                             │
│ ├─ GovernanceService (Policy Enforcer)                      │
│ ├─ Triumvirate (Galahad, Cerberus, Codex Deus Maximus)     │
│ └─ Four Laws (Ethical Constraints)                          │
│                                                              │
│ Authority: SOVEREIGN (Can command any tier)                 │
│ Dependencies: NONE (Tier 1 never depends on Tier 2/3)       │
└─────────────────────────────────────────────────────────────┘
                           ↓ Authority flows downward
                           ↑ Capability flows upward
┌─────────────────────────────────────────────────────────────┐
│ Tier 2: Infrastructure Control Platform                     │
│ ├─ ExecutionService (Execution Infrastructure)              │
│ ├─ MemoryEngine (Storage Orchestration)                     │
│ ├─ GlobalWatchTower (Security Infrastructure)               │
│ └─ SecurityEnforcer (ASL-3 Controls)                        │
│                                                              │
│ Authority: CONSTRAINED (Can block Tier 3 with approval)     │
│ Dependencies: Tier 1 for governance validation              │
└─────────────────────────────────────────────────────────────┘
                           ↓ Authority flows downward
                           ↑ Capability flows upward
┌─────────────────────────────────────────────────────────────┐
│ Tier 3: Application / Runtime Platform                      │
│ ├─ CouncilHub (Agent Registry)                              │
│ ├─ All Agents (Defense, Expert, Planner, etc.)              │
│ ├─ GUI Dashboard (User Interface)                           │
│ └─ Plugin System                                            │
│                                                              │
│ Authority: SANDBOXED (No enforcement authority)             │
│ Dependencies: Tier 1/2 for all operations                   │
└─────────────────────────────────────────────────────────────┘
```

### Critical Constraints

1. **Authority flows downward**: Tier 1 → Tier 2 → Tier 3
2. **Capability flows upward**: Tier 3 → Tier 2 → Tier 1
3. **Tier 1 independence**: Tier 1 NEVER depends on Tier 2/3
4. **Infrastructure subordination**: All Tier 2 decisions validated by Tier 1
5. **Application sandboxing**: Tier 3 is swappable without threatening Tier 1/2

---

## Tier 1: Governance / Enforcement Platform

### Role

Defines invariants, enforces policy, owns rollback, terminates ambiguity.

### Characteristics

- **Kernel-bound**: Core execution authority
- **Deterministic**: Governance decisions are reproducible
- **Auditable**: All decisions permanently logged
- **Sovereign**: Absolute authority, cannot be overridden

### Components

#### CognitionKernel

**File**: `src/app/core/cognition_kernel.py`

The trust root for all executions. Every action flows through `kernel.process()` or `kernel.route()`.

**API**:

```python
# Process user-initiated actions
result = kernel.process(
    user_input="execute task",
    source="user",
    metadata={"user_id": "user123"}
)

# Route agent/system-initiated tasks
result = kernel.route(
    task={"action": "analyze", "data": data},
    source="planner_agent",
    metadata={"priority": "high"}
)

# Enforce governance on action
kernel.enforce(action, context)  # Raises PermissionError if blocked

# Execute approved action
kernel.act(action, context)

# Commit to memory
kernel.commit(context)

# Trigger reflection
kernel.reflect(context)
```

**Tier Registration**:
- Tier: `TIER_1_GOVERNANCE`
- Authority: `SOVEREIGN`
- Role: `GOVERNANCE_CORE`
- Dependencies: None
- Can be paused: No
- Can be replaced: No

#### GovernanceService

**File**: `src/app/core/services/governance_service.py`

Evaluates actions against policies. **Governance observes, never executes**.

**API**:

```python
# Evaluate action against governance policies
decision = governance_service.evaluate_action(
    action=action,
    context=context,
    identity_snapshot=frozen_snapshot
)

# decision.approved: bool
# decision.reason: str
# decision.council_votes: dict (Galahad, Cerberus, Codex votes)
```

**Tier Registration**:
- Tier: `TIER_1_GOVERNANCE`
- Authority: `SOVEREIGN`
- Role: `POLICY_ENFORCER`
- Dependencies: None
- Can be paused: No
- Can be replaced: No

### API Boundaries

**What Tier 1 CAN do**:
- ✅ Command Tier 2/3 components (pause, resume, rollback)
- ✅ Evaluate and approve/deny any action
- ✅ Enforce policies with absolute authority
- ✅ Audit all operations across all tiers
- ✅ Override any Tier 2 decision

**What Tier 1 CANNOT do**:
- ❌ Depend on Tier 2/3 for core functionality
- ❌ Execute actions directly (delegates to ExecutionService)
- ❌ Be paused or overridden by lower tiers

**Authority Flow**:
- **Outbound**: Can command Tier 2/3
- **Inbound**: Receives capability requests from Tier 2/3

---

## Tier 2: Infrastructure Control Platform

### Role

Resource orchestration, placement decisions, isolation domains, elasticity coordination.

### Characteristics

- **Responds to Tier 1**: All infrastructure decisions validated by governance
- **Cannot override enforcement**: Tier 1 decisions are final
- **Can be paused**: Tier 1 can pause/rollback infrastructure
- **Constrained authority**: Can block Tier 3 with approval

### Components

#### ExecutionService

**File**: `src/app/core/services/execution_service.py`

Executes approved actions. **Execution never governs**.

**API**:

```python
# Execute pre-approved action
result, status, error = execution_service.execute_action(
    action=action,
    context=context
)

# status: ExecutionStatus (EXECUTING, COMPLETED, FAILED)
# result: Action result
# error: Error message if failed
```

**Tier Registration**:
- Tier: `TIER_2_INFRASTRUCTURE`
- Authority: `CONSTRAINED`
- Role: `INFRASTRUCTURE_CONTROLLER`
- Dependencies: `cognition_kernel`
- Can be paused: Yes
- Can be replaced: No

#### MemoryEngine

**File**: `src/app/core/memory_engine.py`

Four-channel memory system (episodic, semantic, procedural, emotional).

**Tier Registration**:
- Tier: `TIER_2_INFRASTRUCTURE`
- Authority: `CONSTRAINED`
- Role: `RESOURCE_ORCHESTRATOR`
- Dependencies: `cognition_kernel`
- Can be paused: Yes
- Can be replaced: No

### API Boundaries

**What Tier 2 CAN do**:
- ✅ Allocate resources to Tier 3 components
- ✅ Isolate workloads for security
- ✅ Scale capacity based on metrics
- ✅ Temporarily block Tier 3 (<5 min) autonomously
- ✅ Request permanent blocks from Tier 1

**What Tier 2 CANNOT do**:
- ❌ Override Tier 1 governance decisions
- ❌ Permanently block Tier 3 without approval
- ❌ Command Tier 1 components
- ❌ Make policy decisions (only enforce)

**Authority Flow**:
- **Outbound**: Can command Tier 3 (with constraints)
- **Inbound**: Receives commands from Tier 1, requests from Tier 3

---

## Tier 3: Application / Runtime Platform

### Role

Runtime services, APIs, SDKs, developer surfaces, product experiences.

### Characteristics

- **Fully sandboxed**: No enforcement authority
- **No sovereignty**: All operations validated by higher tiers
- **Disposable**: Can be replaced without threatening Tier 1/2
- **Capability-driven**: Requests capabilities from higher tiers

### Components

#### CouncilHub

**File**: `src/app/core/council_hub.py`

Agent registry and orchestration hub.

**API**:

```python
# Register agent (automatically registers in tier system)
council_hub.register_agent(
    agent_id="expert_agent",
    agent_obj=expert_agent_instance
)

# Route task through kernel
result = council_hub.route_to_kernel(
    task=task,
    source="council_hub"
)
```

**Tier Registration**:
- Tier: `TIER_3_APPLICATION`
- Authority: `SANDBOXED`
- Role: `RUNTIME_SERVICE`
- Dependencies: `cognition_kernel`
- Can be paused: Yes
- Can be replaced: Yes

#### All Agents

All agents (SafetyGuard, ExpertAgent, PlannerAgent, etc.) are registered as Tier 3.

**Tier Registration** (per agent):
- Tier: `TIER_3_APPLICATION`
- Authority: `SANDBOXED`
- Role: `RUNTIME_SERVICE`
- Dependencies: `cognition_kernel`, `council_hub`
- Can be paused: Yes
- Can be replaced: Yes

### API Boundaries

**What Tier 3 CAN do**:
- ✅ Request capabilities from Tier 2/1
- ✅ Submit tasks through kernel
- ✅ Query status and health
- ✅ Register services
- ✅ Appeal blocks to Tier 1

**What Tier 3 CANNOT do**:
- ❌ Enforce policies or make governance decisions
- ❌ Command Tier 1/2 components
- ❌ Bypass kernel for execution
- ❌ Access resources without allocation
- ❌ Override blocks from Tier 2/1

**Authority Flow**:
- **Outbound**: None (sandboxed)
- **Inbound**: Receives commands from Tier 1/2

---

## Cross-Tier Communication

All cross-tier communication flows through the `TierInterfaceRouter`.

### Request Flow

```python
from app.core.tier_interfaces import TierRequest, RequestType, get_tier_router

# Create request
request = TierRequest(
    request_id="req_123",
    request_type=RequestType.CAPABILITY_REQUEST,
    source_tier=3,  # Tier 3 requesting
    target_tier=1,  # From Tier 1
    source_component="agent_planner",
    target_component="governance_service",
    operation="evaluate_action",
    payload={"action": "analyze_data", "context": {...}}
)

# Route request
router = get_tier_router()
response = router.route_request(request)

# response.success: bool
# response.result: Any
# response.error_message: str | None
```

### Validation Rules

The router validates:
1. **Authority commands** must flow downward (Tier N → Tier N+1)
2. **Capability requests** must flow upward (Tier N+1 → Tier N)
3. **Resource allocations** must flow upward
4. **Enforcement actions** must flow downward

**Violations are blocked and logged**.

---

## API Boundaries

### Tier 1 Interface (`ITier1Governance`)

```python
class ITier1Governance(ABC):
    @abstractmethod
    def evaluate_action(
        self, request: GovernanceDecisionRequest
    ) -> GovernanceDecisionResponse:
        """Evaluate action against policies."""
        pass

    @abstractmethod
    def enforce_policy(
        self, policy_id: str, target_tier: int, target_component: str
    ) -> bool:
        """Enforce policy on lower tier."""
        pass

    @abstractmethod
    def audit_operation(
        self, operation: str, tier: int, component: str, details: dict
    ) -> str:
        """Record audit entry."""
        pass

    @abstractmethod
    def rollback_tier(self, tier: int, reason: str) -> bool:
        """Rollback tier to previous state."""
        pass
```

### Tier 2 Interface (`ITier2Infrastructure`)

```python
class ITier2Infrastructure(ABC):
    @abstractmethod
    def allocate_resources(
        self, request: ResourceAllocationRequest
    ) -> ResourceAllocationResponse:
        """Allocate resources."""
        pass

    @abstractmethod
    def isolate_workload(
        self, workload_id: str, isolation_level: str
    ) -> str:
        """Create isolation domain."""
        pass

    @abstractmethod
    def scale_capacity(
        self, component_id: str, target_capacity: int
    ) -> bool:
        """Scale capacity."""
        pass

    @abstractmethod
    def block_application(
        self, request: BlockRequest
    ) -> BlockResponse:
        """Block Tier 3 component."""
        pass
```

### Tier 3 Interface (`ITier3Application`)

```python
class ITier3Application(ABC):
    @abstractmethod
    def request_capability(
        self, capability: str, justification: str
    ) -> bool:
        """Request capability from higher tier."""
        pass

    @abstractmethod
    def submit_task(self, task: dict[str, Any]) -> str:
        """Submit task (routed through kernel)."""
        pass

    @abstractmethod
    def query_status(self) -> dict[str, Any]:
        """Query component status."""
        pass

    @abstractmethod
    def register_service(
        self, service_id: str, service_spec: dict[str, Any]
    ) -> bool:
        """Register service."""
        pass
```

---

## Governance Policies

### Policy Hierarchy

**File**: `src/app/core/tier_governance_policies.py`

#### Tier 1 → Tier 2/3 (Sovereign Authority)

- **Pause any component**: No approval required, always audited
- **Rollback any tier**: Immediate authority, cannot be appealed
- **Override any block**: Final decision

#### Tier 2 → Tier 3 (Constrained Authority)

- **Temporary blocks (<5 min)**: Autonomous, audited, auto-lift
- **Extended blocks (5min-1hr)**: Requires Tier 1 approval
- **Permanent blocks**: ALWAYS requires Tier 1 consensus

### Block Management

```python
from app.core.tier_governance_policies import (
    get_policy_engine,
    BlockReason,
    BlockType
)

policy_engine = get_policy_engine()

# Request block
success, reason, block_record = policy_engine.request_block(
    component_id="agent_unsafe",
    component_name="UnsafeAgent",
    tier=3,
    blocked_by="security_enforcer",
    blocking_tier=2,
    reason=BlockReason.SECURITY_VIOLATION,
    block_type=BlockType.TEMPORARY,
    duration_seconds=300  # 5 minutes
)

# File appeal
success, reason, appeal = policy_engine.file_appeal(
    block_id=block_record.block_id,
    appellant="agent_unsafe",
    justification="False positive detection"
)

# Process appeal (Tier 1 authority)
policy_engine.process_appeal(
    appeal_id=appeal.appeal_id,
    approved=True,
    decided_by="governance_service",
    decision="Appeal granted - detection error confirmed"
)
```

---

## Health Monitoring

### Tier Health Dashboard

**File**: `src/app/core/tier_health_dashboard.py`

```python
from app.core.tier_health_dashboard import get_health_monitor

monitor = get_health_monitor()

# Collect platform health
report = monitor.collect_platform_health()

# Print formatted report
print(monitor.format_health_report(report))

# Get alerts
unacknowledged_alerts = monitor.get_alerts(acknowledged=False)

# Record custom metric
from app.core.tier_health_dashboard import HealthMetric, MetricType
from app.core.platform_tiers import PlatformTier

metric = HealthMetric(
    metric_name="governance_decision_latency",
    metric_type=MetricType.LATENCY,
    value=125.5,
    unit="ms",
    threshold_warning=200.0,
    threshold_critical=500.0
)

monitor.record_metric(PlatformTier.TIER_1_GOVERNANCE, metric)
```

### Health Levels

- **HEALTHY**: All systems operational
- **DEGRADED**: Some issues, but functional
- **CRITICAL**: Major issues, limited functionality
- **OFFLINE**: Tier not operational

---

## Examples and Usage

### Example 1: Register Component in Tier System

```python
from app.core.platform_tiers import (
    get_tier_registry,
    PlatformTier,
    AuthorityLevel,
    ComponentRole
)

registry = get_tier_registry()

# Register Tier 2 component
registry.register_component(
    component_id="memory_engine",
    component_name="MemoryEngine",
    tier=PlatformTier.TIER_2_INFRASTRUCTURE,
    authority_level=AuthorityLevel.CONSTRAINED,
    role=ComponentRole.RESOURCE_ORCHESTRATOR,
    component_ref=memory_engine_instance,
    dependencies=["cognition_kernel"],
    can_be_paused=True,
    can_be_replaced=False
)
```

### Example 2: Validate Authority Flow

```python
# Validate authority flow before executing command
is_valid, reason = registry.validate_authority_flow(
    source_component_id="governance_service",  # Tier 1
    target_component_id="execution_service",   # Tier 2
    action="pause_execution"
)

if is_valid:
    # Authority flows downward - valid
    execution_service.pause()
```

### Example 3: Block Tier 3 Component from Tier 2

```python
from app.core.tier_governance_policies import get_policy_engine, BlockReason, BlockType

policy_engine = get_policy_engine()

# Tier 2 can temporarily block Tier 3 autonomously
success, reason, block = policy_engine.request_block(
    component_id="agent_chatbot",
    component_name="ChatbotAgent",
    tier=3,
    blocked_by="security_enforcer",
    blocking_tier=2,
    reason=BlockReason.ANOMALOUS_BEHAVIOR,
    block_type=BlockType.TEMPORARY,
    duration_seconds=180  # 3 minutes
)

# Block is autonomous for <5 min, audited, and auto-lifts
```

### Example 4: Monitor Tier Health

```python
from app.core.tier_health_dashboard import get_health_monitor
from app.core.platform_tiers import PlatformTier

monitor = get_health_monitor()

# Check Tier 1 health
tier1_health = monitor.collect_tier_health(PlatformTier.TIER_1_GOVERNANCE)

print(f"Tier 1 Status: {tier1_health.overall_health.value}")
print(f"Active Components: {tier1_health.tier_status.active_components}")
print(f"Violations: {tier1_health.active_violations}")

# Get full platform report
platform_report = monitor.collect_platform_health()
print(monitor.format_health_report(platform_report))
```

---

## Summary

The three-tier platform strategy provides:

1. **Clear authority hierarchy**: Tier 1 > Tier 2 > Tier 3
2. **Formal interfaces**: Explicit API boundaries between tiers
3. **Governance enforcement**: Policies with approval workflows
4. **Health monitoring**: Real-time visibility into tier status
5. **Audit trail**: Complete logging of all cross-tier operations

**Key Principle**: Authority flows downward, capability flows upward. Tier 1 holds the line, always.
