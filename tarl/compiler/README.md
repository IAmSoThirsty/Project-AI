<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ # -->


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->

<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / README.md # -->
<!-- # ============================================================================ #

<!--                                         [2026-03-03 13:45] -->
<!--                                        Productivity: Active -->
# T.A.R.L. Compiler Frontend Subsystem

## Overview

The compiler frontend transforms T.A.R.L. source code into executable bytecode through a multi-stage pipeline.

## Architecture

### Pipeline Stages

```
Source Code
    ↓
┌─────────┐
│  Lexer  │ → Tokenization
└─────────┘
    ↓
┌─────────┐
│ Parser  │ → AST Construction
└─────────┘
    ↓
┌──────────────┐
│   Semantic   │ → Type Checking
│   Analyzer   │   Scope Resolution
└──────────────┘
    ↓
┌──────────────┐
│     Code     │ → Bytecode Emission
│  Generator   │   Optimization
└──────────────┘
    ↓
Bytecode
```

## Components

### Lexer (`lexer/`)

- Tokenizes source text
- Tracks source locations
- Reports lexical errors

### Parser (`parser/`)

- Builds Abstract Syntax Tree
- Error recovery
- Syntax validation

### Semantic Analyzer (`semantic/`)

- Type checking
- Scope resolution
- Symbol table management

### Code Generator (`codegen/`)

- Bytecode emission
- Optimization passes
- Source map generation

## Integration Contract

**Dependencies:**

- Configuration (for compiler settings)
- Diagnostics (for error reporting)
- Standard Library (for built-in types)

**Provides:**

- `CompilerFrontend.compile(source: str) -> bytes`
- Bytecode format compatible with Runtime VM

**Guarantees:**

- All errors reported through Diagnostics
- Deterministic compilation
- Thread-safe operation

## Usage

```python
from tarl.compiler import CompilerFrontend

compiler = CompilerFrontend(config, diagnostics, stdlib)
compiler.initialize()

# Compile source

bytecode = compiler.compile("pour 'Hello!'")

# Check status

status = compiler.get_status()
```

## Bytecode Format

```
Header: TARL_BYTECODE_V1\x00
Instructions: [opcode, operand, ...]
```

## Error Codes

- E001-E099: Lexical errors
- E100-E199: Syntax errors
- E200-E299: Semantic errors
- E300-E399: Type errors
