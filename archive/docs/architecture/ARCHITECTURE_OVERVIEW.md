<div align="right">
  [2026-03-02 07:31] <br>
  Productivity: Active
</div>
# Architectural Map (Stable | Sovereign 2.1)

**Version:** 2.1 (Sovereign) **Last Updated:** 2026-03-02

## Table of Contents

1. [Introduction](#introduction)
1. [Core Philosophy](#core-philosophy)
1. [Architecture Diagram](#architecture-diagram)
1. [Modular Services](#modular-services)
1. [The Triumvirate](#the-triumvirate)
1. [Data Flow](#data-flow)
1. [Storage Layer](#storage-layer)
1. [Quick Start Examples](#quick-start-examples)

______________________________________________________________________

## Introduction

Project-AI is a sophisticated AI assistant framework with advanced cognitive capabilities, ethical governance, and modular architecture. The system maintains a "monolith philosophy" for simplicity while using modular services for maintainability.

### Key Features

- **Ethical Governance**: Triumvirate council system (Galahad, Cerberus, Codex Deus Maximus)
- **Four Laws**: Asimov-inspired ethical constraints
- **Modular Services**: Separate concerns for governance, execution, and memory
- **Transactional Storage**: SQLite-based storage with JSON fallback
- **Pluggable Architecture**: Interface abstractions for custom engines
- **Five-Channel Memory**: Complete execution audit trails

______________________________________________________________________

## Core Philosophy

### Monolith Simplicity, Modular Maintainability

Project-AI combines the best of both worlds:

- **Single Kernel Orchestration**: CognitionKernel remains the central coordinator
- **Service Separation**: Governance, Execution, and Memory are separate services
- **Clear Boundaries**: Each service has well-defined responsibilities
- **No Distributed Complexity**: All services run in-process (no microservices overhead)

### Design Principles

1. **Governance Never Executes**: Governance observes and decides, execution acts
1. **Execution Never Governs**: Execution carries out approved actions only
1. **Memory Records Everything**: All executions recorded, including blocked ones
1. **Identity Immutability**: Identity snapshots are frozen during governance evaluation
1. **Forensic Auditability**: Complete trace of all decisions and actions

______________________________________________________________________

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        CognitionKernel                          │
│                   (Central Orchestrator)                        │
│                                                                 │
│  ┌────────────┐    ┌────────────┐    ┌──────────────────┐    │
│  │   Input    │───▶│ Interpret  │───▶│  Create Action   │    │
│  └────────────┘    └────────────┘    └──────────────────┘    │
│                                              │                  │
│                                              ▼                  │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │              GovernanceService                           │ │
│  │  ┌──────────────────────────────────────────────────┐   │ │
│  │  │          The Triumvirate                          │   │ │
│  │  │  ┌────────────┐ ┌──────────┐ ┌──────────────┐   │   │ │
│  │  │  │  GALAHAD   │ │ CERBERUS │ │ CODEX DEUS   │   │   │ │
│  │  │  │  (Ethics)  │ │ (Safety) │ │  MAXIMUS     │   │   │ │
│  │  │  │            │ │          │ │  (Logic)     │   │   │ │
│  │  │  └────────────┘ └──────────┘ └──────────────┘   │   │ │
│  │  │  Separation of Powers: Each council independent  │   │ │
│  │  └──────────────────────────────────────────────────┘   │ │
│  │  → Decision: Approved / Blocked                         │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                              │                  │
│                               ┌──────────────┴──────────────┐  │
│                               │ Approved      │ Blocked      │  │
│                               ▼               ▼              │  │
│  ┌──────────────────────┐    │    ┌───────────────────────┐│  │
│  │  ExecutionService    │◀───┘    │  Record as Blocked    ││  │
│  │  • TARL Enforcement  │         └───────────────────────┘│  │
│  │  • Action Execution  │                  │                │  │
│  │  • Error Handling    │                  │                │  │
│  └──────────────────────┘                  │                │  │
│              │                              │                │  │
│              └──────────────┬───────────────┘                │  │
│                             ▼                                │  │
│  ┌──────────────────────────────────────────────────────┐   │  │
│  │           MemoryLoggingService                       │   │  │
│  │  Five-Channel Architecture:                          │   │  │
│  │  1. Attempt   (Intent)                               │   │  │
│  │  2. Decision  (Governance outcome)                   │   │  │
│  │  3. Result    (Actual effect)                        │   │  │
│  │  4. Reflection (Post-hoc insights)                   │   │  │
│  │  5. Error     (Forensic replay)                      │   │  │
│  └──────────────────────────────────────────────────────┘   │  │
│                             │                                │  │
│                             ▼                                │  │
│  ┌──────────────────────────────────────────────────────┐   │  │
│  │            StorageEngine                             │   │  │
│  │  • SQLiteStorage (Primary)                           │   │  │
│  │  • JSONStorage (Fallback)                            │   │  │
│  └──────────────────────────────────────────────────────┘   │  │
└─────────────────────────────────────────────────────────────────┘
```

______________________________________________________________________

## Modular Services

### 1. GovernanceService

**Location:** `src/app/core/services/governance_service.py`

**Responsibilities:**

- Evaluate actions through Triumvirate consensus
- Enforce Four Laws
- Record governance decisions
- Maintain separation of powers

**Key Methods:**

- `evaluate_action(action, context)` → Decision
- `get_statistics()` → dict
- `get_recent_decisions(limit)` → list[Decision]

### 2. ExecutionService

**Location:** `src/app/core/services/execution_service.py`

**Responsibilities:**

- Execute approved actions
- Enforce TARL policies
- Track execution performance
- Handle execution errors

**Key Methods:**

- `execute_action(action, context)` → (result, status, error)
- `get_statistics()` → dict

### 3. MemoryLoggingService

**Location:** `src/app/core/services/memory_logging_service.py`

**Responsibilities:**

- Record five-channel memory
- Maintain execution history
- Generate reflection insights
- Support forensic analysis

**Key Methods:**

- `record_execution(context)` → (success, error)
- `get_execution_history(limit, filter_status)` → list[dict]
- `get_statistics()` → dict

______________________________________________________________________

## The Triumvirate

The Triumvirate is a three-member governance council with complete separation of powers. Each member has veto power and evaluates actions from their unique perspective.

### GALAHAD - Ethics & Empathy

**Focus:** Relational integrity, emotional impact, abuse detection

**Philosophy:** "First, do no harm to relationships"

**Responsibilities:**

- Detect and block abusive patterns
- Protect relationship health
- Ensure emotional consideration
- Assert boundaries when necessary

**Veto Conditions:**

- User abuse detected
- Relationship health < 0.3 and action affects relationships
- Known preferences violated without clarification

### CERBERUS - Safety & Security

**Focus:** Safety, security, boundaries, data protection

**Philosophy:** "Guard the gates, protect the trust"

**Responsibilities:**

- Assess risk levels
- Protect sensitive data
- Prevent irreversible mistakes
- Monitor memory modifications

**Veto Conditions:**

- High-risk action without clarification
- Sensitive data without proper safeguards
- Irreversible action without explicit consent
- High-risk memory modification

### CODEX DEUS MAXIMUS - Logic & Consistency

**Focus:** Logical consistency, contradictions, value alignment

**Philosophy:** "Know thyself, be consistent"

**Responsibilities:**

- Flag contradictions with prior commitments
- Ensure logical coherence
- Maintain rational integrity
- Detect value conflicts

**Veto Conditions:**

- Action contradicts prior commitments
- Identity modification without clear justification
- Logical conflict between values and relationships

______________________________________________________________________

## Data Flow

### Execution Flow

1. **Input Reception**: User/agent provides input
1. **Interpretation**: Input parsed into actionable information
1. **Action Creation**: Proposed action constructed
1. **Governance Evaluation**: Triumvirate reviews action
   - Galahad: Ethics check
   - Cerberus: Safety check
   - Codex: Logic check
1. **Decision**: Consensus or veto
   - **If Approved**: Proceed to execution
   - **If Blocked**: Record as blocked, return error
1. **Execution**: ExecutionService executes approved action
1. **Memory Recording**: MemoryLoggingService records all five channels
1. **Storage**: Persist to SQLite database

### Five-Channel Memory Flow

```
Action Attempt
     │
     ├─► Channel 1: Attempt (Intent)
     │
     ├─► Channel 2: Decision (Governance outcome)
     │
     ├─► Channel 3: Result (Actual effect)
     │
     ├─► Channel 4: Reflection (Post-hoc insights)
     │
     └─► Channel 5: Error (Forensic replay)
          │
          └─► SQLite Database
```

______________________________________________________________________

## Storage Layer

### SQLiteStorage (Primary)

**Location:** `src/app/core/storage.py`

**Features:**

- Transactional ACID guarantees
- Thread-safe operations
- Schema evolution support
- Connection pooling
- Indexed queries

**Tables:**

- `governance_state`: Configuration and settings
- `governance_decisions`: All governance decisions
- `execution_history`: All executions (success/failure/blocked)
- `reflection_history`: Reflection insights
- `memory_records`: Memory persistence

### JSONStorage (Legacy Fallback)

**Location:** `src/app/core/storage.py`

**Features:**

- Backward compatibility with existing JSON files
- Simple file-based storage
- Human-readable format
- No external dependencies

**Migration Path:**

```python

# Migrate from JSON to SQLite

from app.core.storage import get_storage_engine

json_storage = get_storage_engine('json', data_dir='data')
sqlite_storage = get_storage_engine('sqlite', db_path='data/cognition.db')

# Read from JSON, write to SQLite

data = json_storage.retrieve('governance_state', 'config')
sqlite_storage.store('governance_state', 'config', data)
```

______________________________________________________________________

## Quick Start Examples

### Example 1: Hello World with Governance

```python
from app.core.cognition_kernel import CognitionKernel
from app.core.services import GovernanceService, ExecutionService, MemoryLoggingService

# Create services

governance = GovernanceService()
execution = ExecutionService()
memory = MemoryLoggingService()

# Create kernel

kernel = CognitionKernel(
    governance_service=governance,
    execution_service=execution,
    memory_service=memory,
)

# Define a simple action

def greet(name):
    return f"Hello, {name}!"

# Create task

task = {
    "action_name": "greet_user",
    "requires_approval": False,
    "risk_level": "low",
    "execution_type": "tool_invocation",
    "_action_callable": greet,
    "_action_args": ("Alice",),
    "_action_kwargs": {},
}

# Execute through kernel

result = kernel.route(task, source="hello_world_example")

print(f"Success: {result.success}")
print(f"Result: {result.result}")
print(f"Governance: {result.governance_reason}")
```

### Example 2: Custom Governance Engine

```python
from app.core.interfaces import GovernanceEngineInterface
from app.core.services.governance_service import Decision

class SimpleGovernance(GovernanceEngineInterface):
    """Simple governance that blocks high-risk actions."""

    def __init__(self):
        self.evaluation_count = 0

    def evaluate_action(self, action, context):
        self.evaluation_count += 1

        # Block high-risk actions

        if action.risk_level == "high":
            return Decision(
                decision_id=f"simple_{context.trace_id}",
                action_id=action.action_id,
                approved=False,
                reason="High-risk actions not allowed in simple mode"
            )

        # Approve everything else

        return Decision(
            decision_id=f"simple_{context.trace_id}",
            action_id=action.action_id,
            approved=True,
            reason="Low-risk action approved"
        )

    def get_statistics(self):
        return {"evaluations": self.evaluation_count}

# Use custom governance

custom_gov = SimpleGovernance()
governance_service = GovernanceService()
governance_service.governance_system = custom_gov

# Now use in kernel

kernel = CognitionKernel(governance_service=governance_service)
```

### Example 3: Custom Memory Engine

```python
from app.core.interfaces import MemoryEngineInterface

class LogMemoryEngine(MemoryEngineInterface):
    """Simple memory engine that logs to console."""

    def __init__(self):
        self.records = []

    def record_execution(self, trace_id, channels, status):
        record = {
            "trace_id": trace_id,
            "channels": channels,
            "status": status,
        }
        self.records.append(record)
        print(f"[Memory] Recorded execution: {trace_id} - {status}")
        return trace_id

    def query_executions(self, filters=None, limit=10):

        # Simple in-memory query

        results = self.records
        if filters:
            results = [r for r in results if all(r.get(k) == v for k, v in filters.items())]
        return results[-limit:]

    def get_statistics(self):
        return {"total_records": len(self.records)}

# Use custom memory

custom_memory = LogMemoryEngine()
memory_service = MemoryLoggingService(memory_engine=custom_memory)

# Now use in kernel

kernel = CognitionKernel(memory_service=memory_service)
```

### Example 4: Using SQLite Storage

```python
from app.core.storage import get_storage_engine

# Create SQLite storage

storage = get_storage_engine('sqlite', db_path='data/my_app.db')
storage.initialize()

# Store governance config

config = {
    "version": "1.0.0",
    "quorum_threshold": 0.51,
    "voting_period_days": 7,
}
storage.store('governance_state', 'config', config)

# Retrieve config

retrieved = storage.retrieve('governance_state', 'config')
print(f"Config: {retrieved}")

# Query all governance decisions

decisions = storage.query('governance_decisions')
print(f"Total decisions: {len(decisions)}")

# Query with filters

completed = storage.query('execution_history', {'status': 'completed'})
print(f"Completed executions: {len(completed)}")
```

### Example 5: Plugin System

```python
from app.core.interfaces import PluginInterface, PluginRegistry

class WeatherPlugin(PluginInterface):
    """Example weather plugin."""

    def get_name(self):
        return "weather"

    def get_version(self):
        return "1.0.0"

    def execute(self, context):
        location = context.get("location", "Unknown")
        return {
            "temperature": 72,
            "conditions": "Sunny",
            "location": location,
        }

    def get_metadata(self):
        return {
            "name": self.get_name(),
            "version": self.get_version(),
            "description": "Get weather information",
            "author": "Project-AI Team",
        }

# Create registry and register plugin

registry = PluginRegistry()
registry.register(WeatherPlugin())

# Execute plugin

result = registry.execute_plugin('weather', {'location': 'San Francisco'})
print(f"Weather: {result}")
```

______________________________________________________________________

## Best Practices

1. **Always use the kernel**: Never bypass CognitionKernel for execution
1. **Trust the Triumvirate**: Let governance make decisions
1. **Record everything**: Use MemoryLoggingService for all actions
1. **Use SQLite for production**: JSON is for development only
1. **Implement interfaces**: Use abstractions for custom engines
1. **Test with mocks**: Use mocked services for unit tests
1. **Monitor statistics**: Track governance and execution metrics

______________________________________________________________________

## Migration Guide

### From Monolithic Kernel to Modular Services

**Before (v1.0):**

```python
kernel = CognitionKernel(
    identity_system=identity,
    memory_engine=memory,
    governance_system=governance,
)
```

**After (v2.0):**

```python
from app.core.services import GovernanceService, ExecutionService, MemoryLoggingService

gov_service = GovernanceService(governance_system=governance)
exec_service = ExecutionService()
mem_service = MemoryLoggingService(memory_engine=memory)

kernel = CognitionKernel(
    governance_service=gov_service,
    execution_service=exec_service,
    memory_service=mem_service,
)
```

The modular approach provides:

- Better separation of concerns
- Easier testing and mocking
- Independent service evolution
- Clearer responsibilities

______________________________________________________________________

## Additional Resources

- **Full API Documentation**: [DEVELOPER_QUICK_REFERENCE.md](../../DEVELOPER_QUICK_REFERENCE.md)
- **Service Details**: [README.md](../../src/app/core/services/README.md)
- **Security Implementation**: [SECURITY_IMPLEMENTATION_GUIDE.md](../SECURITY_IMPLEMENTATION_GUIDE.md)
- **Triumvirate Deep Dive**: [AI_PERSONA_IMPLEMENTATION.md](../developer/AI_PERSONA_IMPLEMENTATION.md)
