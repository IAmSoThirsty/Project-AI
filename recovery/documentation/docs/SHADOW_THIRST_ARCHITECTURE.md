# Shadow Thirst Architecture

## Overview

The `src/shadow_thirst` module implements the ThirstyLang compiler, virtual machine, and runtime environment. It provides a domain-specific language (DSL) for expressing sovereign governance, constitutional policies, and resource management with built-in safety guarantees.

**Purpose**: Provide a specialized programming language for expressing governance policies, constitutional rules, and resource constraints with formal verification capabilities.

**Scope**: ThirstyLang compiler, bytecode VM, type system, static analysis, and runtime environment.

## Components

### Compiler Pipeline

- **lexer.py**: Lexical analysis (tokenization)
  - Token generation from source
  - Character stream processing
  - Keyword recognition
  - Operator tokenization

- **parser.py**: Syntax analysis (parsing)
  - Abstract Syntax Tree (AST) generation
  - Grammar rule enforcement
  - Syntax error detection
  - Parse tree construction

- **ast_nodes.py**: AST node definitions
  - Node type hierarchy
  - Node attributes
  - Visitor pattern support
  - AST manipulation utilities

- **type_system.py**: Type checking and inference
  - Static type checking
  - Type inference
  - Type compatibility checking
  - Generic type support

- **static_analysis.py**: Static code analysis
  - Dead code detection
  - Unreachable code detection
  - Resource leak detection
  - Security vulnerability scanning

- **ir_generator.py**: Intermediate representation generation
  - High-level IR from AST
  - Optimization opportunities
  - Platform-independent representation

- **ir.py**: IR data structures
  - IR instruction definitions
  - Control flow graph
  - Data flow analysis

- **compiler.py**: Main compiler orchestration
  - Pipeline coordination
  - Compilation phases
  - Error aggregation
  - Output generation

### Runtime System

- **vm.py**: Virtual machine implementation
  - Bytecode interpreter
  - Stack machine
  - Instruction execution
  - Runtime type checking
  - Resource management
  - Sandboxed execution

- **bytecode.py**: Bytecode definitions and operations
  - Instruction set architecture
  - Bytecode encoding/decoding
  - Optimization passes

### Constitutional Framework

- **constitutional.py**: Constitutional policy DSL
  - Constitutional rule definitions
  - Policy enforcement
  - Governance integration
  - Jurisdictional boundaries

### Resource Management

- **resource_limiter.thirsty**: Resource limitation policies
  - Memory limits
  - CPU time limits
  - Network limits
  - Storage limits

### Examples and Demos

- **demo.py**: ThirstyLang demonstration
  - Example programs
  - Feature showcase
  - Tutorial code

- **legion.modelfile.thirsty**: Model configuration example
  - AI model policies
  - Resource allocation
  - Safety boundaries

### Module Structure

```
shadow_thirst/
├── README.md                      # Module documentation
├── __init__.py                    # Module initialization
├── lexer.py                       # Lexical analyzer
├── parser.py                      # Parser
├── ast_nodes.py                   # AST definitions
├── type_system.py                 # Type system
├── static_analysis.py             # Static analyzer
├── ir_generator.py                # IR generator
├── ir.py                          # IR definitions
├── compiler.py                    # Compiler
├── vm.py                          # Virtual machine
├── bytecode.py                    # Bytecode definitions
├── constitutional.py              # Constitutional DSL
├── resource_limiter.thirsty       # Resource policies
├── demo.py                        # Demonstrations
├── legion.modelfile.thirsty       # Model configuration
└── __pycache__/                   # Python cache
```

## Dependencies

### Internal Dependencies

- `src.governance`: Governance policy enforcement
- `src.security`: Security validation
- `src.app.core`: Core system integration

### External Dependencies

- **logging**: Compiler diagnostics
- **dataclasses**: AST node definitions
- **enum**: Token and node types
- **typing**: Type system implementation

## Data Flow

### Compilation Flow

```
ThirstyLang Source Code (.thirsty)
  ↓
Lexer (tokenization)
  ↓
Parser (AST generation)
  ↓
Type Checker (type validation)
  ↓
Static Analyzer (security/optimization)
  ↓
IR Generator (intermediate representation)
  ↓
Compiler (bytecode generation)
  ↓
Bytecode (.thirstyc)
```

### Execution Flow

```
Bytecode
  ↓
VM Loader
  ↓
VM Initialization
  ↓
Instruction Execution (stack-based)
  ↓
Resource Monitoring
  ↓
Runtime Type Checking
  ↓
Result or Exception
```

### Constitutional Policy Flow

```
Constitutional Source (.thirsty)
  ↓
Compilation
  ↓
Policy Bytecode
  ↓
VM Execution
  ↓
Governance Integration
  ↓
Policy Enforcement
```

## Integration Points

### APIs

- `ThirstyCompiler.compile()`: Compile source to bytecode
- `ThirstyVM.execute()`: Execute bytecode
- `TypeChecker.check()`: Type checking
- `StaticAnalyzer.analyze()`: Static analysis
- `Constitutional.load_policy()`: Load constitutional policies

### Events

- Compilation events (start/complete/error)
- Execution events
- Type error events
- Resource limit events
- Policy violation events

### Hooks

- Pre-compilation hooks
- Post-compilation hooks
- Runtime hooks (instruction execution)
- Resource limit hooks
- Policy enforcement hooks

## Deployment

### Compilation

```python
from src.shadow_thirst.compiler import ThirstyCompiler

compiler = ThirstyCompiler()
bytecode = compiler.compile_file("policy.thirsty")
bytecode.save("policy.thirstyc")
```

### Execution

```python
from src.shadow_thirst.vm import ThirstyVM

vm = ThirstyVM(resource_limits={
    "max_memory": 1024 * 1024,  # 1MB
    "max_time": 10.0,            # 10 seconds
    "max_stack_depth": 1000
})
result = vm.execute(bytecode)
```

### Production Deployment

- Compiled bytecode in production (not source)
- AOT (Ahead-Of-Time) compilation
- Bytecode signing and verification
- Resource limits enforced by VM
- Sandboxed execution

## Architecture Patterns

### Compiler Design

- Multi-pass compilation
- AST-based transformation
- Intermediate representation
- Optimization passes
- Error recovery

### VM Design

- Stack-based architecture
- Bytecode interpreter
- Sandboxed execution
- Resource monitoring
- Safe memory management

### Type System

- Static type checking
- Type inference
- Generic types
- Union types
- Type safety guarantees

### DSL Design

- Domain-specific syntax for governance
- Declarative policy expression
- Formal verification support
- Composable policies

## Security Considerations

- Sandboxed VM execution
- Resource limits enforced
- No unsafe operations
- Bytecode verification
- Static analysis for vulnerabilities
- Constitutional policy validation
- Memory safety guarantees
- No arbitrary code execution

## Performance Characteristics

- Fast compilation (optimized for policy size)
- Efficient bytecode interpretation
- Minimal VM overhead
- Optimized instruction set
- Resource tracking overhead minimal
- Cached compilation results

## Monitoring and Observability

- Compilation metrics (time, errors)
- VM execution metrics
- Resource usage tracking
- Instruction execution counts
- Policy enforcement metrics
- Error rate tracking

## Error Handling

- Compilation errors with source location
- Runtime exceptions with stack trace
- Type errors with detailed messages
- Resource limit violations
- Policy violation exceptions
- Recovery mechanisms

## Testing Strategy

- Lexer unit tests
- Parser unit tests
- Type system tests
- Static analysis tests
- VM instruction tests
- Integration tests (compile + execute)
- Policy enforcement tests
- Resource limit tests
- Adversarial input tests (fuzzing)

## ThirstyLang Language Features

### Syntax

- C-like syntax with governance extensions
- Strong static typing
- First-class functions
- Pattern matching
- Algebraic data types

### Governance Constructs

- Constitutional rules
- Policy declarations
- Jurisdictional boundaries
- Resource constraints
- Safety invariants

### Built-in Types

- Integers, floats, strings
- Booleans
- Arrays and tuples
- Records (structs)
- Option types
- Result types (for errors)

### Control Flow

- if/else conditionals
- while/for loops
- Pattern matching
- Early returns
- Exception handling

### Safety Features

- No null pointers
- Bounds checking
- Type safety
- Resource limits
- Memory safety

## Future Extensions

- JIT compilation for hot paths
- LLVM backend for native code
- Formal verification integration
- Proof-carrying code
- Advanced optimizations
- Debugger integration
- IDE support (LSP server)
- Package manager
- Standard library expansion
- Multi-threading support
- Async/await syntax
- Macros and metaprogramming
- Foreign function interface (FFI)

## Example ThirstyLang Code

```thirsty
// Constitutional policy example
constitutional_policy AccessControl {
    jurisdiction: Sovereign;
    
    rule CanAccessData(user: User, resource: Resource) -> Bool {
        return user.has_permission(resource.required_permission)
            && resource.jurisdiction.allows(user.jurisdiction);
    }
    
    invariant NoPrivacyViolation(action: Action) -> Bool {
        return !action.accesses_pii() || action.has_consent();
    }
}

// Resource limiter example
resource_limits ApiService {
    max_memory: 1GB;
    max_cpu_time: 10s;
    max_concurrent_requests: 100;
    max_request_rate: 1000/minute;
}
```

## Research Integration

- Programming language theory
- Formal verification research
- Type system research
- VM optimization research
- Security research
- DSL design patterns
