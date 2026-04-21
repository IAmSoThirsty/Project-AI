# Kernel Types & Interfaces

## Overview

The Kernel Types module (`src/app/core/kernel_types.py`) defines the foundational type system and base interfaces for the SuperKernel architecture, enabling consistent interaction patterns across all cognitive subsystems.

**Location**: `src/app/core/kernel_types.py`  
**Lines of Code**: 98  
**Purpose**: Define kernel taxonomy and ensure uniform interfaces  
**Dependencies**: abc, enum, typing

---

## Architecture Philosophy

### SuperKernel System

The SuperKernel architecture divides cognitive processing into specialized subordinate kernels, each handling a specific domain:

```
SuperKernel
    ├── CognitionKernel (actions, tools, agents)
    ├── ReflectionKernel (self-reflection, insights)
    ├── MemoryKernel (storage, retrieval)
    ├── PerspectiveKernel (personality, worldview)
    └── IdentityKernel (self-concept, identity)
```

---

## Core Components

### 1. KernelType Enum

```python
class KernelType(Enum):
    """
    Types of kernels in the system.
    
    Each kernel type represents a specific domain of cognitive processing.
    """
    COGNITION = auto()      # General cognitive processing
    REFLECTION = auto()     # Self-reflection and insight generation
    MEMORY = auto()         # Memory storage and retrieval
    PERSPECTIVE = auto()    # Personality and worldview management
    IDENTITY = auto()       # Identity and self-concept management
```

**Purpose**: Provides a taxonomy for kernel classification and routing.

**Example**:
```python
from app.core.kernel_types import KernelType

# Identify kernel type
kernel_type = KernelType.COGNITION
print(kernel_type.name)  # "COGNITION"
print(kernel_type.value)  # 1

# Use in routing
def route_request(request, kernel_type: KernelType):
    if kernel_type == KernelType.COGNITION:
        return cognition_kernel.process(request)
    elif kernel_type == KernelType.MEMORY:
        return memory_kernel.process(request)
    # ...
```

---

### 2. KernelInterface (Abstract Base Class)

```python
class KernelInterface(ABC):
    """
    Base interface that all kernels must implement.
    
    Ensures consistent interaction patterns across all subordinate
    kernels in the SuperKernel system.
    """
    
    @abstractmethod
    def process(self, input_data: Any, **kwargs) -> Any:
        """Primary entrypoint for kernel operations."""
        pass
    
    def route(self, task: Any, *, source: str = "agent", **kwargs) -> Any:
        """Optional routing method for agent-initiated tasks."""
        return self.process(task, source=source, **kwargs)
    
    def get_statistics(self) -> dict[str, Any]:
        """Get kernel statistics (optional)."""
        return {}
```

---

#### process() - Primary Entry Point

```python
@abstractmethod
def process(self, input_data: Any, **kwargs) -> Any:
    """
    Process input data and return result.
    
    Args:
        input_data: Input data to process (type depends on kernel)
        **kwargs: Additional keyword arguments for processing
    
    Returns:
        Processing result (type depends on kernel)
    
    Raises:
        RuntimeError: If processing fails
    """
```

**Example Implementations**:
```python
# CognitionKernel
class CognitionKernel(KernelInterface):
    def process(self, action: str, **kwargs) -> dict:
        """Process an action request."""
        result = self.execute_action(action, **kwargs)
        return {"status": "success", "result": result}

# MemoryKernel
class MemoryKernel(KernelInterface):
    def process(self, query: str, **kwargs) -> list:
        """Process a memory query."""
        memories = self.search_memories(query, **kwargs)
        return memories

# ReflectionKernel
class ReflectionKernel(KernelInterface):
    def process(self, event: dict, **kwargs) -> str:
        """Generate reflection on an event."""
        insight = self.reflect_on_event(event)
        return insight
```

---

#### route() - Agent Routing

```python
def route(self, task: Any, *, source: str = "agent", **kwargs) -> Any:
    """
    Optional routing method for agent-initiated tasks.
    
    Provides an alternative entrypoint similar to CognitionKernel.route().
    Default implementation delegates to process().
    
    Args:
        task: Task to route
        source: Source of the task (default: "agent")
        **kwargs: Additional keyword arguments
    
    Returns:
        Task result
    """
```

**Example**:
```python
class AdvancedKernel(KernelInterface):
    def process(self, input_data: Any, **kwargs) -> Any:
        """Standard processing."""
        return self._process_sync(input_data, **kwargs)
    
    def route(self, task: Any, *, source: str = "agent", **kwargs) -> Any:
        """Agent-specific routing with prioritization."""
        if source == "agent":
            # High priority for agent tasks
            return self._process_priority(task, **kwargs)
        else:
            # Standard processing for others
            return self.process(task, **kwargs)
```

---

#### get_statistics() - Observability

```python
def get_statistics(self) -> dict[str, Any]:
    """
    Get kernel statistics (optional).
    
    Returns:
        Dictionary with kernel statistics
    """
```

**Example Implementation**:
```python
class MonitoredKernel(KernelInterface):
    def __init__(self):
        self.process_count = 0
        self.error_count = 0
        self.total_process_time = 0.0
    
    def process(self, input_data: Any, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = self._do_process(input_data, **kwargs)
            self.process_count += 1
            return result
        except Exception as e:
            self.error_count += 1
            raise
        finally:
            self.total_process_time += time.time() - start_time
    
    def get_statistics(self) -> dict[str, Any]:
        return {
            "process_count": self.process_count,
            "error_count": self.error_count,
            "avg_process_time": (
                self.total_process_time / self.process_count
                if self.process_count > 0 else 0
            ),
            "error_rate": (
                self.error_count / self.process_count
                if self.process_count > 0 else 0
            )
        }

# Usage
kernel = MonitoredKernel()
# ... process many tasks ...
stats = kernel.get_statistics()
print(f"Processed {stats['process_count']} tasks")
print(f"Error rate: {stats['error_rate']:.2%}")
print(f"Avg time: {stats['avg_process_time']:.3f}s")
```

---

## Usage Patterns

### Pattern 1: SuperKernel Registry

```python
class SuperKernel:
    """Central kernel that coordinates all subordinate kernels."""
    
    def __init__(self):
        self.kernels: dict[KernelType, KernelInterface] = {}
        self._register_kernels()
    
    def _register_kernels(self):
        """Register all subordinate kernels."""
        self.kernels[KernelType.COGNITION] = CognitionKernel()
        self.kernels[KernelType.REFLECTION] = ReflectionKernel()
        self.kernels[KernelType.MEMORY] = MemoryKernel()
        self.kernels[KernelType.PERSPECTIVE] = PerspectiveKernel()
        self.kernels[KernelType.IDENTITY] = IdentityKernel()
    
    def process(self, kernel_type: KernelType, input_data: Any, **kwargs) -> Any:
        """Route processing to appropriate kernel."""
        if kernel_type not in self.kernels:
            raise ValueError(f"Unknown kernel type: {kernel_type}")
        
        kernel = self.kernels[kernel_type]
        return kernel.process(input_data, **kwargs)
    
    def get_all_statistics(self) -> dict[str, dict]:
        """Get statistics from all kernels."""
        return {
            kernel_type.name: kernel.get_statistics()
            for kernel_type, kernel in self.kernels.items()
        }

# Usage
super_kernel = SuperKernel()

# Route to cognition kernel
result = super_kernel.process(
    KernelType.COGNITION,
    "execute_action",
    action="search_web",
    query="latest AI news"
)

# Route to memory kernel
memories = super_kernel.process(
    KernelType.MEMORY,
    "recall",
    topic="previous searches"
)

# Get system-wide statistics
all_stats = super_kernel.get_all_statistics()
for kernel_name, stats in all_stats.items():
    print(f"{kernel_name}: {stats}")
```

---

### Pattern 2: Kernel Adapter

**Problem**: Existing classes don't implement `KernelInterface`

**Solution**: Create adapter wrappers

```python
class LegacySystem:
    """Legacy system that doesn't implement KernelInterface."""
    
    def execute(self, command: str):
        # Legacy execution method
        return f"Executed: {command}"

class LegacySystemAdapter(KernelInterface):
    """Adapter to make LegacySystem compatible with KernelInterface."""
    
    def __init__(self, legacy_system: LegacySystem):
        self.legacy_system = legacy_system
        self.call_count = 0
    
    def process(self, input_data: Any, **kwargs) -> Any:
        """Adapt process() to legacy execute()."""
        self.call_count += 1
        command = str(input_data)
        return self.legacy_system.execute(command)
    
    def get_statistics(self) -> dict[str, Any]:
        return {"call_count": self.call_count}

# Usage
legacy = LegacySystem()
adapter = LegacySystemAdapter(legacy)

# Now works with SuperKernel
super_kernel.kernels[KernelType.COGNITION] = adapter
```

---

### Pattern 3: Kernel Middleware

```python
class MiddlewareKernel(KernelInterface):
    """Kernel with middleware support for cross-cutting concerns."""
    
    def __init__(self, base_kernel: KernelInterface):
        self.base_kernel = base_kernel
        self.middleware_stack = []
    
    def add_middleware(self, middleware: Callable):
        """Add middleware function."""
        self.middleware_stack.append(middleware)
    
    def process(self, input_data: Any, **kwargs) -> Any:
        """Process with middleware chain."""
        # Build middleware chain
        def execute():
            return self.base_kernel.process(input_data, **kwargs)
        
        # Apply middleware in reverse order
        for middleware in reversed(self.middleware_stack):
            original_execute = execute
            execute = lambda: middleware(original_execute, input_data, **kwargs)
        
        return execute()

# Middleware examples
def logging_middleware(next_handler, input_data, **kwargs):
    """Log all kernel operations."""
    logger.info(f"Processing: {input_data}")
    try:
        result = next_handler()
        logger.info(f"Success: {result}")
        return result
    except Exception as e:
        logger.error(f"Error: {e}")
        raise

def timing_middleware(next_handler, input_data, **kwargs):
    """Measure execution time."""
    start = time.time()
    result = next_handler()
    duration = time.time() - start
    logger.info(f"Duration: {duration:.3f}s")
    return result

def caching_middleware(next_handler, input_data, **kwargs):
    """Cache results."""
    cache_key = str(input_data)
    if cache_key in cache:
        logger.info("Cache hit")
        return cache[cache_key]
    
    result = next_handler()
    cache[cache_key] = result
    return result

# Usage
base_kernel = CognitionKernel()
kernel_with_middleware = MiddlewareKernel(base_kernel)

kernel_with_middleware.add_middleware(logging_middleware)
kernel_with_middleware.add_middleware(timing_middleware)
kernel_with_middleware.add_middleware(caching_middleware)

# All processing now goes through middleware
result = kernel_with_middleware.process("action")
```

---

### Pattern 4: Kernel Pool

```python
import threading
from queue import Queue

class KernelPool:
    """Pool of kernel instances for parallel processing."""
    
    def __init__(
        self,
        kernel_class: type[KernelInterface],
        pool_size: int = 4
    ):
        self.pool = Queue(maxsize=pool_size)
        
        # Create kernel instances
        for _ in range(pool_size):
            kernel = kernel_class()
            self.pool.put(kernel)
    
    def process(self, input_data: Any, **kwargs) -> Any:
        """Process using an available kernel from pool."""
        kernel = self.pool.get()  # Block until kernel available
        try:
            return kernel.process(input_data, **kwargs)
        finally:
            self.pool.put(kernel)  # Return to pool

# Usage
kernel_pool = KernelPool(CognitionKernel, pool_size=4)

# Process multiple tasks in parallel
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [
        executor.submit(kernel_pool.process, f"task_{i}")
        for i in range(100)
    ]
    
    results = [f.result() for f in futures]
```

---

## Advanced Patterns

### 1. Kernel Chain

```python
class KernelChain(KernelInterface):
    """Chain multiple kernels for sequential processing."""
    
    def __init__(self, *kernels: KernelInterface):
        self.kernels = list(kernels)
    
    def process(self, input_data: Any, **kwargs) -> Any:
        """Process through kernel chain."""
        result = input_data
        
        for kernel in self.kernels:
            result = kernel.process(result, **kwargs)
        
        return result

# Usage
chain = KernelChain(
    PreprocessingKernel(),
    CognitionKernel(),
    PostprocessingKernel()
)

final_result = chain.process(raw_input)
```

---

### 2. Conditional Kernel Router

```python
class ConditionalRouter(KernelInterface):
    """Route to different kernels based on conditions."""
    
    def __init__(self):
        self.routes = []  # List of (condition, kernel) pairs
    
    def add_route(
        self,
        condition: Callable[[Any], bool],
        kernel: KernelInterface
    ):
        """Add conditional route."""
        self.routes.append((condition, kernel))
    
    def process(self, input_data: Any, **kwargs) -> Any:
        """Route to first matching kernel."""
        for condition, kernel in self.routes:
            if condition(input_data):
                return kernel.process(input_data, **kwargs)
        
        raise ValueError("No matching route found")

# Usage
router = ConditionalRouter()

# Add routes
router.add_route(
    lambda data: isinstance(data, str),
    TextProcessingKernel()
)
router.add_route(
    lambda data: isinstance(data, dict),
    StructuredDataKernel()
)
router.add_route(
    lambda data: hasattr(data, '__iter__'),
    BatchProcessingKernel()
)

# Auto-route based on data type
result = router.process(my_data)
```

---

### 3. Kernel with Fallback

```python
class FallbackKernel(KernelInterface):
    """Kernel with fallback on failure."""
    
    def __init__(
        self,
        primary: KernelInterface,
        fallback: KernelInterface
    ):
        self.primary = primary
        self.fallback = fallback
        self.fallback_count = 0
    
    def process(self, input_data: Any, **kwargs) -> Any:
        """Try primary, fallback on error."""
        try:
            return self.primary.process(input_data, **kwargs)
        except Exception as e:
            logger.warning(f"Primary kernel failed: {e}. Using fallback.")
            self.fallback_count += 1
            return self.fallback.process(input_data, **kwargs)
    
    def get_statistics(self) -> dict[str, Any]:
        primary_stats = self.primary.get_statistics()
        fallback_stats = self.fallback.get_statistics()
        
        return {
            "fallback_count": self.fallback_count,
            "primary": primary_stats,
            "fallback": fallback_stats
        }

# Usage
kernel = FallbackKernel(
    primary=GPT4Kernel(),
    fallback=GPT35TurboKernel()
)

# Uses GPT-4, falls back to GPT-3.5-Turbo on error
result = kernel.process("complex_query")
```

---

## Testing

```python
import unittest

class MockKernel(KernelInterface):
    """Mock kernel for testing."""
    
    def __init__(self):
        self.process_calls = []
    
    def process(self, input_data: Any, **kwargs) -> Any:
        self.process_calls.append((input_data, kwargs))
        return f"Processed: {input_data}"

class TestKernelInterface(unittest.TestCase):
    def test_process_required(self):
        """Test that process() must be implemented."""
        with self.assertRaises(TypeError):
            # Cannot instantiate without implementing process()
            class IncompleteKernel(KernelInterface):
                pass
            
            kernel = IncompleteKernel()
    
    def test_route_default_behavior(self):
        """Test default route() delegates to process()."""
        kernel = MockKernel()
        
        result = kernel.route("task", source="agent")
        
        self.assertEqual(len(kernel.process_calls), 1)
        self.assertEqual(kernel.process_calls[0][0], "task")
    
    def test_kernel_type_enum(self):
        """Test KernelType enum."""
        self.assertEqual(KernelType.COGNITION.name, "COGNITION")
        self.assertIsInstance(KernelType.MEMORY, KernelType)
```

---

## Related Documentation

- **SuperKernel Architecture**: `source-docs/core/super-kernel.md`
- **Cognition Kernel**: `source-docs/core/cognition-kernel.md`
- **Memory Kernel**: `source-docs/core/memory-kernel.md`

---

**Last Updated**: 2025-01-24  
**Status**: Stable - Production Ready  
**Maintainer**: Core Architecture Team
