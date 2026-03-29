<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / ARCHITECTURE.md # -->
<!-- # ============================================================================ # -->


<!-- # COMPLIANCE: Sovereign Substrate / ARCHITECTURE.md # -->

<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / ARCHITECTURE.md # -->
<!-- # ============================================================================ #

<!--                                         [2026-03-03 13:45] -->
<!--                                        Productivity: Active -->
                                                                        DATE: 2026-03-03 09:47:12
                                                                        STATUS: Active (Production)

# T.A.R.L. (Thirsty's Active Resistance Language) - Complete Architecture

**Version:** 2.0.1 (Post-Audit Sovereign Edition)
**Status:** Active | Production Implementation
**Date:** March 3, 2026

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

## System Architecture: Eight-Layer Subsystem Stack

T.A.R.L. consists of 8 integrated subsystems arranged in a strict dependency hierarchy:

```
Layer 7: Development Tooling (LSP, REPL, Debugger)
         │
         ▼
Layer 6: Module System (Import Resolution, Caching)
         │
         ▼
Layer 5: Runtime VM (Bytecode Execution, JIT, GC)
         │
         ▼
Layer 4: Compiler Frontend (Lexer, Parser, Codegen)
         │
         ▼
Layer 3: FFI Bridge (Foreign Function Interface)
         │
         ▼
Layer 2: Standard Library (Built-in Functions)
         │
         ▼
Layer 1: Diagnostics Engine (Error Reporting)
         │
         ▼
Layer 0: Configuration Registry (Foundation)
```

**Key Properties**:

- Each layer depends **only** on layers below it
- Zero circular dependencies across all layers
- Deterministic initialization: Layer 0 → Layer 7
- Graceful shutdown: Layer 7 → Layer 0

---

## Subsystems Detail

### Layer 0: Configuration Registry (`tarl/config/`)

Central configuration registry with hierarchical merging (defaults → file → env → overrides).
**API**: `ConfigRegistry.get(key, default)`

### Layer 1: Diagnostics Engine (`tarl/diagnostics/`)

Structured error reporting with source location tracking and rich context snippets.
**API**: `DiagnosticsEngine.report_error(code, message, location)`

### Layer 2: Standard Library (`tarl/stdlib/`)

Core built-in functions (30+) and types. Includes safe I/O and collection management.
**Status**: 100% Audited for Resource Safety.

### Layer 3: FFI Bridge (`tarl/ffi/`)

Security-hardened Foreign Function Interface for C/Python interop.
**Security Modes**: Permissive, Default, Strict.

### Layer 4: Compiler Frontend (`tarl/compiler/`)

Multi-stage pipeline: Lexer → Parser → Semantic Analyzer → Code Generator.
**Output**: TARL_BYTECODE_V2.

### Layer 5: Runtime VM (`tarl/runtime/`)

Stack-based VM with JIT compilation and Generational Garbage Collection.
**Enforcement**: CPU, Memory, and FD limits.

### Layer 6: Module System (`tarl/modules/`)

Import resolution, bytecode caching, and circular dependency detection.

### Layer 7: Development Tooling (`tarl/tooling/`)

LSP Server (Port 9898), REPL, and Debugger (Port 9899).

---

## Initialization Sequence

Strict dependency order ensures zero circular dependencies:

1. `ConfigRegistry`
2. `DiagnosticsEngine`
3. `StandardLibrary`
4. `FFIBridge`
5. `CompilerFrontend`
6. `RuntimeVM`
7. `ModuleSystem`
8. `DevelopmentTooling`

---

## Security Model

### 1. Sandboxing

- CPU time limits (30s)
- Memory limits (64MB)
- Process isolation

### 2. FFI Security

- Mandatory allowlists
- Type validation
- Memory bounds checking

---

## Integration with Project-AI

- **Cerberus**: Defensive compilation based on threat severity.
- **Codex Deus Maximus**: Persistent security upgrades and orchestration.
- **Bridge**: `src/app/agents/cerberus_codex_bridge.py`.

---

**Document Version:** 2.0.1
**Last Updated:** 2026-03-03
**Copyright:** (c) 2026 Jeremy Karrick / IAmSoThirsty
