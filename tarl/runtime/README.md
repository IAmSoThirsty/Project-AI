# T.A.R.L. Runtime VM Subsystem

## Overview

Stack-based bytecode virtual machine with JIT compilation, garbage collection, and security sandboxing.

## Architecture

```
┌──────────────────────────────────┐
│        Bytecode VM               │
│  ┌────────────┐  ┌────────────┐ │
│  │ Interpreter│  │    JIT     │ │
│  └────────────┘  └────────────┘ │
│  ┌────────────┐  ┌────────────┐ │
│  │   Memory   │  │     GC     │ │
│  │  Manager   │  │ Collector  │ │
│  └────────────┘  └────────────┘ │
└──────────────────────────────────┘
```

## Components

### Bytecode VM (`vm/`)

- Stack-based architecture
- Instruction dispatch
- Call stack management

### Interpreter (`interpreter/`)

- Bytecode interpretation
- Instruction execution
- Native call interface

### JIT Compiler (`jit/`)

- Profile-guided optimization
- Hot path compilation
- Native code generation

### Memory Manager (`memory/`)

- Heap allocation
- Stack management
- Resource tracking

### Garbage Collector (`gc/`)

- Mark-and-sweep collection
- Generational GC
- Incremental collection

## Integration Contract

**Dependencies:**

- Configuration (for VM settings)
- Diagnostics (for runtime errors)
- Standard Library (for built-ins)
- FFI Bridge (for foreign calls)

**Provides:**

- `RuntimeVM.execute(bytecode: bytes, context: dict) -> Any`
- Execution context management
- Resource limit enforcement

**Guarantees:**

- Memory safety
- Execution timeouts
- Resource limit enforcement
- No arbitrary code execution

## Usage

```python
from tarl.runtime import RuntimeVM

runtime = RuntimeVM(config, diagnostics, stdlib, ffi)
runtime.initialize()

# Execute bytecode

result = runtime.execute(bytecode, context={"var": 42})

# Check status

status = runtime.get_status()
```

## Configuration

```toml
[runtime]
stack_size = 1048576        # 1MB
heap_size = 16777216        # 16MB
gc_threshold = 0.75         # 75%
enable_jit = true
jit_threshold = 100         # execution count
```

## Security

- Stack overflow protection
- Heap bounds checking
- Execution timeouts
- Resource limits
- Capability-based security
