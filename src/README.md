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

<!--                                        [2026-03-04 14:24]  -->
<!--                                       Productivity: Active  -->

# `src/` — Source Modules

> **The living core of Project-AI.** Everything below this directory is implementation code — interpreters, security services, shadow architecture, and the PSIA framework.

## Directory Map

| Module | Purpose | Key Files |
|---|---|---|
| **`thirsty_lang/`** | Thirsty-Lang interpreter, CLI, transpiler, VS Code extension | `src/index.js`, `thirsty-cli.js`, VS Code extension |
| **`shadow_thirst/`** | Shadow Thirst dual-plane execution engine | `shadow_vm.py`, `dual_plane.py`, `containment.py` |
| **`psia/`** | Project-AI Sovereign Intelligence Architecture | 48 modules — the backbone of sovereign reasoning |
| **`security/`** | Security tooling and hardening | `cerberus_guard.py`, threat models |
| **`plugins/`** | Plugin subsystem for extensibility | Plugin loaders, registry |
| **`interpreter/`** | Core runtime interpreter bridge | `index.js`, execution engine |
| **`shared/`** | Shared utilities across `src/` modules | Constants, helpers |

## Module Details

### `thirsty_lang/` — The Language Family

The Thirsty-Lang interpreter and toolchain. Contains:

- **Interpreter** (`src/index.js`) — Lexer, parser, and evaluator for Thirsty-Lang
- **CLI** (`thirsty-cli.js`) — Command-line interface for running `.thirsty` files
- **VS Code Extension** (`vscode-extension/`) — Syntax highlighting for all 6 UTF family members
- **Examples** (`examples/`) — Showcase files for `.thirsty`, `.tog`, `.tarl`, `.shadow`, `.tscg`, `.tscgb`
- **Security** (`src/security/`) — Input validation, sandbox policies

### `shadow_thirst/` — Dual-Plane Architecture

Shadow Thirst provides a deterministic virtual machine with dual-plane execution:

- **Primary Plane** — Normal execution
- **Shadow Plane** — Isolated containment for untrusted code
- **Bytecode Instructions** — `PUSH`, `LOAD`, `STORE`, `CALL`, `GUARD`, `HALT`, `RETURN`
- **Containment** — Stack overflow protection, max instruction limits

### `psia/` — Sovereign Intelligence Architecture

The PSIA (Project Sovereign Intelligence Architecture) framework contains:

- Constitutional reasoning modules
- Invariant verification
- Policy enforcement pipelines
- Agent lifecycle management
- Episodic memory integration

### `security/` — Security Subsystem

Cerberus-level security hardening:

- Threat model definitions
- Attack surface analysis
- Runtime guard implementations

## Running

```bash
# Run a Thirsty-Lang file
node src/thirsty_lang/src/index.js examples/hello.thirsty

# Run the CLI
node src/thirsty_lang/thirsty-cli.js run examples/hello.thirsty
```

## Dependencies

- **Node.js** ≥ 18 — For interpreter and CLI
- **Python** ≥ 3.12 — For PSIA and Shadow Thirst modules
