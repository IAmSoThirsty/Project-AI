# Core Services

This directory contains the modular services extracted from the CognitionKernel to improve maintainability.

## Services

### GovernanceService
**File:** `governance_service.py`

Handles all governance evaluation and decision-making:
- Triumvirate consensus (Galahad, Cerberus, Codex Deus Maximus)
- Four Laws enforcement
- Decision recording and audit trails
- Identity snapshot integration

**Key Principle:** "Governance observes, never executes"

### ExecutionService
**File:** `execution_service.py`

Manages action execution with runtime enforcement:
- Executes pre-approved actions
- TARL policy enforcement
- Performance tracking and metrics
- Error handling and recovery

**Key Principle:** "Execution never governs"

### MemoryLoggingService
**File:** `memory_logging_service.py`

Records all executions in five-channel memory:
1. **Attempt**: Intent and action proposal
2. **Decision**: Governance outcome
3. **Result**: Actual execution effect
4. **Reflection**: Post-hoc insights
5. **Error**: Runtime exceptions for forensic replay

**Key Principle:** "All executions recorded, including blocked ones"

## Design Philosophy

### Separation of Concerns

Each service has a single, well-defined responsibility:
- **GovernanceService** decides what can be done
- **ExecutionService** does what was approved
- **MemoryLoggingService** records what was done

### Clear Boundaries

Services communicate through well-defined interfaces:
- Input: Action objects with metadata
- Output: Structured results (Decision, Status, Records)
- No circular dependencies

### Composable Architecture

Services can be:
- Tested independently
- Replaced with custom implementations
- Configured per deployment
- Monitored separately

## Usage Example

```python
from app.core.services import (
    GovernanceService,
    ExecutionService,
    MemoryLoggingService,
)

# Create services
governance = GovernanceService(triumvirate=triumvirate)
execution = ExecutionService(tarl_gate=tarl)
memory = MemoryLoggingService(memory_engine=engine)

# Use in kernel
kernel = CognitionKernel(
    governance_service=governance,
    execution_service=execution,
    memory_service=memory,
)

# Services work together through kernel orchestration
result = kernel.route(task)
```

## Testing

Each service has comprehensive unit tests in `tests/test_modular_services.py`:
- 8 tests for GovernanceService
- 6 tests for ExecutionService
- 6 tests for MemoryLoggingService

Run tests:
```bash
pytest tests/test_modular_services.py -v
```

## Extension Points

### Custom Governance

Implement `GovernanceEngineInterface` from `../interfaces.py`:

```python
from app.core.interfaces import GovernanceEngineInterface

class MyGovernance(GovernanceEngineInterface):
    def evaluate_action(self, action, context):
        # Custom logic
        return Decision(approved=True, reason="Custom")
```

### Custom Memory

Implement `MemoryEngineInterface` from `../interfaces.py`:

```python
from app.core.interfaces import MemoryEngineInterface

class MyMemory(MemoryEngineInterface):
    def record_execution(self, trace_id, channels, status):
        # Custom logic
        return trace_id
```

## Statistics and Monitoring

Each service provides statistics:

```python
# Governance statistics
gov_stats = governance_service.get_statistics()
# {
#   "total_decisions": 100,
#   "approvals": 85,
#   "blocks": 15,
#   "approval_rate": 0.85,
#   "triumvirate_active": True
# }

# Execution statistics
exec_stats = execution_service.get_statistics()
# {
#   "total_executions": 85,
#   "successful": 80,
#   "failed": 5,
#   "success_rate": 0.94,
#   "average_execution_time_ms": 12.5
# }

# Memory statistics
mem_stats = memory_service.get_statistics()
# {
#   "total_recordings": 100,
#   "successful_recordings": 98,
#   "failed_recordings": 2,
#   "history_size": 100,
#   "memory_engine_active": True
# }
```

## Performance Considerations

### GovernanceService
- Lightweight evaluation (< 1ms typically)
- Triumvirate calls are fast (in-memory)
- Decision log kept in memory (limit: 1000 recent)

### ExecutionService
- Execution time depends on action
- TARL enforcement adds ~0.5ms
- Statistics updated atomically

### MemoryLoggingService
- Memory recording is async-friendly
- Circular buffer limits memory usage
- Persistence delegated to MemoryEngine

## Migration Notes

### From Monolithic Kernel (v1.0)

**Before:**
```python
# All logic in CognitionKernel
kernel = CognitionKernel(
    governance_system=gov,
    memory_engine=mem,
)
```

**After (v2.0):**
```python
# Services extracted
governance = GovernanceService(governance_system=gov)
memory = MemoryLoggingService(memory_engine=mem)
execution = ExecutionService()

kernel = CognitionKernel(
    governance_service=governance,
    execution_service=execution,
    memory_service=memory,
)
```

**Benefits:**
- Better testability
- Clearer responsibilities
- Easier to extend
- Independent evolution

## Related Documentation

- **Architecture Overview**: `../../ARCHITECTURE_OVERVIEW.md`
- **Interface Abstractions**: `../interfaces.py`
- **Storage Layer**: `../storage.py`
- **Test Suite**: `../../tests/test_modular_services.py`
