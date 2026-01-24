# T.A.R.L. (Thirsty's Active Resistant Language) - Complete Architecture

**Version:** 1.0.0  
**Status:** Production Implementation  
**Date:** 2026-01-24

---

## Executive Summary

T.A.R.L. is a production-grade programming language implementation integrated into Project-AI. This document describes the complete monolithic architecture with sovereign subsystems, strict boundaries, zero circular dependencies, and canonical interfaces following Project-AI's maximal completeness standards.

---

## Architecture Principles

### 1. Monolithic Sovereignty
- All subsystems integrated through single root module (`tarl/__init__.py`)
- Strict initialization order enforces dependency contracts
- Configuration-driven architecture with central registry
- Zero circular dependencies across all subsystems

### 2. Production-Grade Requirements
- Full error handling with structured diagnostics
- Comprehensive logging and observability
- Security-first design with resource limits
- Complete test coverage (unit + integration)
- Rich developer documentation

### 3. Subsystem Boundaries
Each subsystem has:
- Explicit interface contracts
- Dependency declarations
- Initialization/shutdown lifecycle
- Status reporting capabilities
- Audit logging

---

## System Architecture

```
T.A.R.L. System Architecture
============================

┌─────────────────────────────────────────────────────────────┐
│                      TARLSystem (Root)                       │
│                    Monolithic Controller                     │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ Configuration│    │ Diagnostics  │    │   Standard   │
│   Registry   │───▶│    Engine    │◀───│   Library    │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   Compiler   │    │   Runtime    │    │     FFI      │
│   Frontend   │───▶│      VM      │◀───│    Bridge    │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────┐                        ┌──────────────┐
│    Module    │                        │ Development  │
│    System    │                        │   Tooling    │
└──────────────┘                        └──────────────┘
```

---

## Subsystems

### 1. Configuration Management (`tarl/config/`)

**Purpose:** Central configuration registry with hierarchical merging

**Responsibilities:**
- Load configuration from multiple sources (file, env, overrides)
- Validate configuration schema
- Provide immutable configuration views
- Support hot-reloading

**Dependencies:** None (foundation subsystem)

**Key Components:**
- `ConfigRegistry`: Main configuration controller
- Default configuration embedded
- TOML file support
- Environment variable parsing (TARL_* prefix)

**API Surface:**
```python
config = ConfigRegistry(config_path="config/tarl.toml")
config.load()
value = config.get("compiler.debug_mode", default=False)
config.set("runtime.enable_jit", True)
```

---

### 2. Diagnostics Engine (`tarl/diagnostics/`)

**Purpose:** Structured error reporting and diagnostic system

**Responsibilities:**
- Report errors, warnings, and info messages
- Track source locations with line/column precision
- Provide rich error context
- Generate formatted diagnostic reports
- Aggregate diagnostics for batch processing

**Dependencies:** Configuration

**Key Components:**
- `DiagnosticsEngine`: Main diagnostics controller
- `Diagnostic`: Structured diagnostic message
- `SourceLocation`: Source position tracking
- `Severity`: Error severity levels
- `DiagnosticCategory`: Error categorization

**API Surface:**
```python
diagnostics = DiagnosticsEngine(config)
diagnostics.report_error(
    code="E001",
    message="Undefined variable 'x'",
    location=SourceLocation("test.tarl", 5, 10),
    suggestions=["Did you mean 'y'?"]
)
```

---

### 3. Standard Library (`tarl/stdlib/`)

**Purpose:** Core built-in functions and types

**Responsibilities:**
- Provide built-in functions (print, len, type, etc.)
- Register standard library modules
- Manage namespace and globals
- Support FFI integration

**Dependencies:** Configuration, Diagnostics

**Key Components:**
- `StandardLibrary`: Main stdlib controller
- `BuiltInFunction`: Built-in function wrapper
- Core modules: collections, io, net, crypto

**Built-ins:**
- Core: print, len, type, str, int, float, bool
- Collections: list, dict, set, tuple
- Functional: map, filter, reduce
- I/O: open, read, write
- Utility: range, enumerate, zip, sorted, sum, min, max

**API Surface:**
```python
stdlib = StandardLibrary(config, diagnostics)
stdlib.load_builtins()
print_fn = stdlib.get_builtin("print")
stdlib.register_module("mymodule", module_obj)
```

---

### 4. FFI Bridge (`tarl/ffi/`)

**Purpose:** Foreign Function Interface for C/Python interop

**Responsibilities:**
- Register foreign functions
- Type marshaling and conversion
- Security validation
- Memory safety checks

**Dependencies:** Configuration, Diagnostics, Standard Library

**Key Components:**
- `FFIBridge`: Main FFI controller
- `ForeignFunction`: Foreign function wrapper
- Security mode enforcement
- Library allowlist

**API Surface:**
```python
ffi = FFIBridge(config, diagnostics, stdlib)
ffi.register_function("strlen", "libc", strlen_func)
result = ffi.call_function("strlen", "hello")
```

---

### 5. Compiler Frontend (`tarl/compiler/`)

**Purpose:** Source to bytecode compilation pipeline

**Responsibilities:**
- Lexical analysis (tokenization)
- Syntax parsing (AST construction)
- Semantic analysis (type checking)
- Code generation (bytecode emission)
- Optimization passes

**Dependencies:** Configuration, Diagnostics, Standard Library

**Pipeline Stages:**
1. **Lexer:** Source text → Token stream
2. **Parser:** Tokens → Abstract Syntax Tree
3. **Semantic Analyzer:** AST validation and type checking
4. **Code Generator:** AST → Bytecode

**Key Components:**
- `CompilerFrontend`: Main compiler controller
- `Lexer`: Tokenization
- `Parser`: Syntax analysis
- `SemanticAnalyzer`: Semantic validation
- `CodeGenerator`: Bytecode emission

**API Surface:**
```python
compiler = CompilerFrontend(config, diagnostics, stdlib)
compiler.initialize()
bytecode = compiler.compile("pour 'Hello, World!'")
```

---

### 6. Runtime VM (`tarl/runtime/`)

**Purpose:** Bytecode execution engine

**Responsibilities:**
- Execute compiled bytecode
- Manage execution context
- Garbage collection
- Memory management
- JIT compilation (hot paths)
- Resource limits and timeouts

**Dependencies:** Configuration, Diagnostics, Standard Library, FFI

**Key Components:**
- `RuntimeVM`: Main runtime controller
- `BytecodeVM`: Stack-based VM implementation
- `ExecutionContext`: Execution state management
- JIT compiler infrastructure
- Garbage collector

**API Surface:**
```python
runtime = RuntimeVM(config, diagnostics, stdlib, ffi)
runtime.initialize()
result = runtime.execute(bytecode, context={"var": 42})
```

---

### 7. Module System (`tarl/modules/`)

**Purpose:** Module loading and dependency management

**Responsibilities:**
- Resolve module imports
- Cache compiled modules
- Detect circular dependencies
- Manage module namespaces
- Package management

**Dependencies:** Configuration, Diagnostics, Compiler, Runtime

**Key Components:**
- `ModuleSystem`: Main module controller
- `ModuleLoader`: Module loading and caching
- `Module`: Module representation
- Dependency resolver
- Package manager

**API Surface:**
```python
modules = ModuleSystem(config, diagnostics, compiler, runtime)
modules.initialize()
module = modules.import_module("mymodule")
```

---

### 8. Development Tooling (`tarl/tooling/`)

**Purpose:** IDE integration and development tools

**Responsibilities:**
- Language Server Protocol (LSP) implementation
- Interactive REPL
- Source-level debugger
- Build system
- Code formatting and linting
- Profiling and performance analysis

**Dependencies:** All subsystems

**Key Components:**
- `DevelopmentTooling`: Main tooling controller
- `LSPServer`: LSP protocol implementation
- `REPL`: Interactive shell
- `Debugger`: Source-level debugger
- `BuildSystem`: Project build orchestration

**API Surface:**
```python
tooling = DevelopmentTooling(config, diagnostics, compiler, runtime, modules)
tooling.initialize()
tooling.start_lsp()  # Port 9898
tooling.start_repl()
tooling.start_debugger()  # Port 9899
```

---

## Initialization Sequence

**Strict dependency order ensures zero circular dependencies:**

```python
system = TARLSystem(config_path="config/tarl.toml")
system.initialize()

# Phase 1: Configuration (no dependencies)
config = ConfigRegistry()
config.load()

# Phase 2: Diagnostics (config only)
diagnostics = DiagnosticsEngine(config)
diagnostics.initialize()

# Phase 3: Standard Library (config, diagnostics)
stdlib = StandardLibrary(config, diagnostics)
stdlib.load_builtins()

# Phase 4: FFI Bridge (config, diagnostics, stdlib)
ffi = FFIBridge(config, diagnostics, stdlib)
ffi.initialize()

# Phase 5: Compiler Frontend (all above)
compiler = CompilerFrontend(config, diagnostics, stdlib)
compiler.initialize()

# Phase 6: Runtime VM (all above)
runtime = RuntimeVM(config, diagnostics, stdlib, ffi)
runtime.initialize()

# Phase 7: Module System (all above)
modules = ModuleSystem(config, diagnostics, compiler, runtime)
modules.initialize()

# Phase 8: Development Tooling (all subsystems)
tooling = DevelopmentTooling(config, diagnostics, compiler, runtime, modules)
tooling.initialize()
```

---

## Configuration Schema

**File:** `tarl/config/tarl.toml`

```toml
[compiler]
debug_mode = false
optimization_level = 2
target_version = "1.0"
strict_mode = true
emit_source_maps = true

[runtime]
stack_size = 1048576  # 1MB
heap_size = 16777216  # 16MB
gc_threshold = 0.75
enable_jit = true
jit_threshold = 100

[stdlib]
auto_import_builtins = true
enable_experimental = false
io_buffer_size = 8192

[modules]
search_paths = [".", "lib", "modules"]
enable_cache = true
cache_dir = ".tarl_cache"
package_registry = "https://registry.tarl-lang.org"

[diagnostics]
log_level = "INFO"
log_file = "tarl.log"
error_context_lines = 3
enable_warnings = true
warning_level = "default"

[ffi]
enable_ffi = true
allowed_libraries = []  # empty = allow all
security_mode = "strict"

[tooling]
enable_lsp = true
lsp_port = 9898
enable_debugger = true
debugger_port = 9899
repl_history_size = 1000

[security]
enable_sandbox = true
max_execution_time = 30.0
max_memory = 67108864  # 64MB
disable_file_io = false
disable_network_io = false
```

---

## Security Model

### 1. Sandboxing
- Resource limits (CPU, memory, I/O)
- Execution timeouts
- Capability-based security

### 2. FFI Security
- Library allowlist
- Type validation
- Memory bounds checking
- Security mode (permissive, default, strict)

### 3. Runtime Security
- Stack overflow protection
- Heap bounds checking
- Safe garbage collection
- No arbitrary code execution

---

## Integration with Project-AI

### 1. Cerberus Integration
- T.A.R.L. provides defensive compilation
- Cerberus detects threats → T.A.R.L. hardens code
- Bridge: `src/app/agents/cerberus_codex_bridge.py`

### 2. Codex Deus Maximus Integration
- Codex orchestrates T.A.R.L. upgrades
- Permanent integration of security features
- Logs to `data/tarl_protection/implementations.jsonl`

### 3. Security Features
- Threat detection via Thirsty-lang modules
- Code morphing and obfuscation
- Defensive compilation modes
- Active resistance capabilities

---

## Testing Strategy

### Unit Tests
- Each subsystem has isolated unit tests
- Mock dependencies for isolation
- Test all API surface methods
- Edge case validation

### Integration Tests
- Cross-subsystem interaction tests
- Full compilation pipeline
- End-to-end execution
- Error handling paths

### Conformance Tests
- Language specification compliance
- Bytecode format validation
- LSP protocol compliance
- Security constraint enforcement

---

## Performance Characteristics

- **Compilation:** O(n) single-pass with optional optimization
- **Runtime:** Stack-based VM with JIT for hot paths
- **Memory:** Automatic garbage collection, configurable heap
- **Startup:** Lazy subsystem initialization
- **Module Loading:** Cached compilation, O(1) cache lookup

---

## Observability

### Logging
- Structured logging with severity levels
- Per-subsystem logger namespaces
- Configurable log output (file, console, syslog)

### Metrics
- Compilation time
- Execution performance
- Memory usage
- GC statistics
- Module cache hit rate

### Diagnostics
- Rich error context
- Stack traces
- Source location tracking
- Suggestion engine

---

## Future Enhancements

1. **Advanced Optimizations**
   - Multi-pass optimization
   - Dead code elimination
   - Constant folding
   - Loop unrolling

2. **Enhanced JIT**
   - Profile-guided optimization
   - Tiered compilation
   - Adaptive optimization

3. **Concurrency**
   - Green threads
   - Async/await syntax
   - Actor model

4. **Native Compilation**
   - LLVM backend
   - AOT compilation
   - Binary distribution

---

## References

- **T.A.R.L. Documentation:** `TARL_TECHNICAL_DOCUMENTATION.md`
- **Thirsty-lang Integration:** `THIRSTY_LANG_INTEGRATION.md`
- **Project-AI Standards:** `.github/copilot_workspace_profile.md`
- **Security Features:** Thirsty-lang security modules

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-01-24  
**Authors:** Project-AI Team  
**License:** MIT
