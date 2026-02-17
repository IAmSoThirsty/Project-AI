# SuperKernel System Documentation

## Overview

The SuperKernel provides a unified orchestration layer for all subordinate kernels in Project-AI. It standardizes kernel interfaces, centralizes governance checks, and provides five-channel logging for forensic auditability.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        SuperKernel                          │
│                  (Unified Orchestration)                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │          Governance & RBAC Layer                    │  │
│  │  • Triumvirate Consensus                            │  │
│  │  • Four Laws Enforcement                            │  │
│  │  • RBAC Checks                                      │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐  │
│  │          Kernel Router                              │  │
│  │  • Route to appropriate subordinate kernel          │  │
│  │  • Pass through approved requests                   │  │
│  └─────────────────────────────────────────────────────┘  │
│                           │                                 │
│         ┌─────────────────┼─────────────────┐              │
│         │                 │                 │              │
│         ▼                 ▼                 ▼              │
│  ┌──────────┐      ┌──────────┐     ┌──────────┐         │
│  │Cognition │      │Reflection│     │  Memory  │         │
│  │ Kernel   │      │  Cycle   │     │  Engine  │         │
│  │(native)  │      │(adapter) │     │(adapter) │         │
│  └──────────┘      └──────────┘     └──────────┘         │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │          Five-Channel Logging                       │  │
│  │  1. Attempt   - What was tried                      │  │
│  │  2. Decision  - Governance outcome                  │  │
│  │  3. Result    - Actual outcome                      │  │
│  │  4. Reflection - Post-hoc insights                  │  │
│  │  5. Error     - Failure information                 │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. KernelType Enum

Defines the types of kernels in the system:

```python
from app.core.kernel_types import KernelType

# Available kernel types

KernelType.COGNITION    # CognitionKernel (actions, tools, agents)
KernelType.REFLECTION   # ReflectionCycle (self-reflection)
KernelType.MEMORY       # MemoryEngine (memory storage/retrieval)
KernelType.PERSPECTIVE  # PerspectiveEngine (personality management)
KernelType.IDENTITY     # Identity system (self-concept)
```

### 2. KernelInterface

Base interface that all kernels must implement:

```python
from app.core.kernel_types import KernelInterface

class MyKernel(KernelInterface):
    def process(self, input_data, **kwargs):

        # Process input and return result

        return {"result": "processed"}

    def route(self, task, *, source="agent", **kwargs):

        # Optional: handle agent-initiated tasks

        return self.process(task, source=source, **kwargs)

    def get_statistics(self):

        # Optional: return kernel statistics

        return {"operations": 100}
```

### 3. Kernel Adapters

Adapters wrap kernels with non-standard interfaces to make them compatible:

#### ReflectionCycleAdapter

```python
from app.core.kernel_adapters import ReflectionCycleAdapter
from app.core.reflection_cycle import ReflectionCycle

# Create ReflectionCycle

reflection = ReflectionCycle(data_dir="data/reflection")

# Wrap with adapter

adapter = ReflectionCycleAdapter(reflection)

# Use through standard interface

result = adapter.process(
    "daily",  # reflection type: "daily", "weekly", "triggered"
    memory_engine=memory_engine,
    perspective_engine=perspective_engine,
)
```

#### MemoryEngineAdapter

```python
from app.core.kernel_adapters import MemoryEngineAdapter
from app.core.memory_engine import MemoryEngine

# Create MemoryEngine

memory = MemoryEngine(data_dir="data/memory")

# Wrap with adapter

adapter = MemoryEngineAdapter(memory)

# Use through standard interface

# Search memories

results = adapter.process("search", query="test", limit=10)

# Get statistics

stats = adapter.process(None)

# Retrieve specific memory

memory = adapter.process("retrieve", memory_id="mem_123")
```

#### PerspectiveEngineAdapter

```python
from app.core.kernel_adapters import PerspectiveEngineAdapter
from app.core.perspective_engine import PerspectiveEngine

# Create PerspectiveEngine

perspective = PerspectiveEngine(data_dir="data/perspective")

# Wrap with adapter

adapter = PerspectiveEngineAdapter(perspective)

# Use through standard interface

# Get summary

summary = adapter.process("summary")

# Update from interaction

adapter.process(
    "update",
    interaction_type="conversation",
    sentiment=0.7,
    outcome="success",
)
```

### 4. SuperKernel

Main orchestration class that manages all subordinate kernels:

```python
from app.core.super_kernel import SuperKernel
from app.core.kernel_types import KernelType

# Create SuperKernel

super_kernel = SuperKernel(
    triumvirate=triumvirate,      # Optional: Triumvirate for governance
    governance=governance_system,  # Optional: Legacy governance
    rbac_system=rbac,              # Optional: RBAC system
)

# Register kernels

super_kernel.register_kernel(KernelType.COGNITION, cognition_kernel)
super_kernel.register_kernel(KernelType.REFLECTION, reflection_adapter)
super_kernel.register_kernel(KernelType.MEMORY, memory_adapter)

# Process through SuperKernel

result = super_kernel.process(
    input_data={"action": "solve_task"},
    kernel_type=KernelType.COGNITION,
    source="user",
    metadata={"user_id": "user123"},
)

# Route agent tasks

result = super_kernel.route(
    task={"operation": "search"},
    kernel_type=KernelType.MEMORY,
    source="agent",
)
```

## Bootstrap Functions

### Quick Setup

```python
from app.core.super_kernel_bootstrap import bootstrap_super_kernel
from app.core.cognition_kernel import CognitionKernel
from app.core.reflection_cycle import ReflectionCycle
from app.core.memory_engine import MemoryEngine
from app.core.perspective_engine import PerspectiveEngine

# Create subordinate kernels

cognition = CognitionKernel(
    identity_system=identity,
    memory_engine=memory,
    governance_system=governance,
    reflection_engine=reflection,
    triumvirate=triumvirate,
)

reflection = ReflectionCycle(data_dir="data/reflection")
memory = MemoryEngine(data_dir="data/memory")
perspective = PerspectiveEngine(data_dir="data/perspective")

# Bootstrap SuperKernel (automatically creates adapters)

super_kernel = bootstrap_super_kernel(
    cognition_kernel=cognition,
    reflection_cycle=reflection,
    memory_engine=memory,
    perspective_engine=perspective,
    triumvirate=triumvirate,
    governance=governance,
)

# Ready to use!

result = super_kernel.process(
    "user request",
    kernel_type=KernelType.COGNITION,
)
```

### Minimal Setup (Testing)

```python
from app.core.super_kernel_bootstrap import create_minimal_super_kernel

# Create minimal SuperKernel without governance

super_kernel = create_minimal_super_kernel(data_dir="data")

# Note: No governance - all operations auto-approved

```

## Usage Examples

### Example 1: Process User Action

```python

# User initiates an action through CognitionKernel

result = super_kernel.process(
    input_data={
        "action": "greet_user",
        "_action_callable": greet_function,
        "_action_args": ("Alice",),
    },
    kernel_type=KernelType.COGNITION,
    source="user",
    metadata={"user_id": "user123"},
)

print(f"Success: {result.success}")
print(f"Result: {result.result}")
```

### Example 2: Run Daily Reflection

```python

# Run daily reflection through ReflectionCycle

report = super_kernel.process(
    input_data="daily",
    kernel_type=KernelType.REFLECTION,
    memory_engine=memory_engine,
    perspective_engine=perspective_engine,
)

print(f"Insights: {len(report.insights)}")
print(f"Memories processed: {report.memories_processed}")
```

### Example 3: Search Memories

```python

# Search episodic memories

results = super_kernel.process(
    input_data="search",
    kernel_type=KernelType.MEMORY,
    query="user interactions",
    limit=10,
)

for memory in results:
    print(f"Memory: {memory.description}")
```

### Example 4: Update Perspective

```python

# Update perspective from interaction

result = super_kernel.process(
    input_data="update",
    kernel_type=KernelType.PERSPECTIVE,
    interaction_type="conversation",
    sentiment=0.8,
    outcome="success",
    traits_observed={"openness": 0.7},
)

print(f"Perspective updated: {result}")
```

## Governance Integration

The SuperKernel integrates with the Triumvirate and governance systems:

### Governance Flow

1. **Request arrives** at SuperKernel.process()
1. **Governance check** via `_check_governance()`:
   - Low-risk operations (MEMORY, PERSPECTIVE from system/agent): Auto-approve
   - High-risk operations: Check with Triumvirate
   - If no Triumvirate: Check with legacy governance
   - If no governance: Auto-approve with warning
1. **RBAC check** (if configured)
1. **Route to kernel** if approved
1. **Record in execution history** (including blocked actions)

### Governance Configuration

```python

# With Triumvirate

super_kernel = SuperKernel(triumvirate=triumvirate)

# With legacy governance

super_kernel = SuperKernel(governance=governance_system)

# With both (Triumvirate takes precedence)

super_kernel = SuperKernel(
    triumvirate=triumvirate,
    governance=governance_system,
)

# Without governance (auto-approve all)

super_kernel = SuperKernel()  # Warning logged
```

## Five-Channel Logging

Every execution is logged with five channels for forensic auditability:

```python

# Process something

super_kernel.process(input_data, kernel_type=KernelType.COGNITION)

# Get execution history

history = super_kernel.get_execution_history(limit=10)

for record in history:
    print(f"Execution: {record['execution_id']}")
    print(f"Attempt: {record['attempt']}")      # What was tried
    print(f"Decision: {record['decision']}")    # Governance outcome
    print(f"Result: {record['result']}")        # Actual result
    print(f"Reflection: {record['reflection']}")  # Post-hoc insights
    print(f"Error: {record['error']}")          # Error info (if failed)
```

## Statistics and Monitoring

### SuperKernel Statistics

```python
stats = super_kernel.get_statistics()

# {

#     "total_executions": 100,

#     "blocked_executions": 5,

#     "success_rate": 0.95,

#     "registered_kernels": ["COGNITION", "REFLECTION", "MEMORY"],

#     "history_size": 100,

# }

```

### Kernel-Specific Statistics

```python

# Get statistics for specific kernel

stats = super_kernel.get_kernel_statistics(KernelType.COGNITION)

# Returns kernel-specific statistics

# Or get from adapter directly

reflection_stats = reflection_adapter.get_statistics()
memory_stats = memory_adapter.get_statistics()
```

## Best Practices

1. **Use SuperKernel for all operations**: Don't bypass it to call kernels directly
1. **Register all kernels**: Use adapters for non-standard interfaces
1. **Configure governance**: Don't run without governance in production
1. **Monitor execution history**: Review blocked/failed operations
1. **Use kernel types consistently**: Don't mix kernel types
1. **Handle errors gracefully**: SuperKernel raises exceptions for failures
1. **Review statistics regularly**: Monitor success rates and performance

## Migration Guide

### From Direct Kernel Usage

**Before:**

```python

# Direct kernel usage

result = cognition_kernel.process(user_input)
reflection_cycle.perform_daily_reflection(memory_engine, perspective_engine)
memories = memory_engine.search_episodic_memories("query")
```

**After:**

```python

# Through SuperKernel

result = super_kernel.process(
    user_input,
    kernel_type=KernelType.COGNITION,
)

report = super_kernel.process(
    "daily",
    kernel_type=KernelType.REFLECTION,
    memory_engine=memory_engine,
    perspective_engine=perspective_engine,
)

memories = super_kernel.process(
    "search",
    kernel_type=KernelType.MEMORY,
    query="query",
)
```

### Benefits of Migration

- ✅ Centralized governance enforcement
- ✅ Unified logging and audit trail
- ✅ Consistent error handling
- ✅ RBAC integration
- ✅ Performance monitoring
- ✅ Extensibility (easy to add new kernels)

## Extending the System

### Adding a New Kernel Type

1. Add to KernelType enum:

```python
class KernelType(Enum):

    # ... existing types ...

    PLANNING = auto()  # New kernel type
```

2. Create kernel or adapter:

```python
class PlanningKernelAdapter(KernelInterface):
    def process(self, input_data, **kwargs):

        # Implement planning logic

        return planning_result
```

3. Register with SuperKernel:

```python
planning = PlanningKernelAdapter(planning_engine)
super_kernel.register_kernel(KernelType.PLANNING, planning)
```

4. Use it:

```python
plan = super_kernel.process(
    "create plan",
    kernel_type=KernelType.PLANNING,
)
```

## Testing

The SuperKernel system includes comprehensive tests:

```bash

# Run all SuperKernel tests

pytest tests/test_super_kernel.py -v

# Run specific test class

pytest tests/test_super_kernel.py::TestSuperKernel -v

# Run with coverage

pytest tests/test_super_kernel.py --cov=app.core.super_kernel
```

Test coverage includes:

- ✅ KernelType enum (2 tests)
- ✅ KernelInterface (3 tests)
- ✅ ReflectionCycleAdapter (7 tests)
- ✅ MemoryEngineAdapter (6 tests)
- ✅ PerspectiveEngineAdapter (5 tests)
- ✅ SuperKernel (13 tests)
- ✅ Bootstrap functions (3 tests)

**Total: 39 tests, all passing**

## Performance Considerations

- **Minimal overhead**: ~1-2ms per operation for governance and logging
- **Thread-safe**: SuperKernel uses thread-safe operations
- **Memory efficient**: Execution history has configurable limits
- **Scalable**: Can handle high throughput with proper configuration

## Troubleshooting

### Issue: Kernel not registered

**Error:** `RuntimeError: No kernel registered for COGNITION`

**Solution:** Register the kernel before using it:

```python
super_kernel.register_kernel(KernelType.COGNITION, cognition_kernel)
```

### Issue: Execution blocked by governance

**Error:** `PermissionError: Blocked by governance`

**Solution:** Check governance logs and adjust policies or provide required context

### Issue: Invalid kernel instance

**Error:** `TypeError: Kernel instance must implement KernelInterface`

**Solution:** Use an adapter for non-standard kernels:

```python
adapter = ReflectionCycleAdapter(reflection_cycle)
super_kernel.register_kernel(KernelType.REFLECTION, adapter)
```

## Related Documentation

- **CognitionKernel**: `src/app/core/cognition_kernel.py`
- **ReflectionCycle**: `src/app/core/reflection_cycle.py`
- **MemoryEngine**: `src/app/core/memory_engine.py`
- **PerspectiveEngine**: `src/app/core/perspective_engine.py`
- **Governance System**: `src/app/core/governance.py`
- **Test Suite**: `tests/test_super_kernel.py`
