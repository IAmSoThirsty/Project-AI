<!--                                         [2026-03-04 09:48] -->
<!--                                        Productivity: Active -->
                                                                        DATE: 2026-03-03 09:53:12
                                                                        STATUS: Active (Production)

# T.A.R.L. System Architecture (Sovereign Core)

**Version:** 2.0.1 (Post-Audit Sovereign Edition)
**Status:** Active | Production Implementation
**Date:** March 3, 2026

---

## Architecture Overview

T.A.R.L. (Thirsty's Active Resistance Language) implementation in Project-AI follows a monolithic, eight-layer sovereign stack. This global architectural view defines the interaction between the language core and the Project-AI security kernel (Cerberus).

```
┌─────────────────────────────────────────────────────────────────┐
│              FLOOR 1: SOVEREIGN ORCHESTRATION (Thirsty-Lang)    │
│                     (main.thirsty, bootstrap.thirsty)           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                        FLOOR 2: APPLICATION LAYER               │
│                     (User Code / API Calls)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BOOTSTRAP LAYER                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  bootstrap_orchestrator.py - System Initialization      │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────┬──────────────┬─────────────────┬────────────────────────┘
       │              │                 │
       ▼              ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   TARL       │ │  Governance  │ │  CodexDeus   │
│  Runtime     │ │    Core      │ │  Escalation  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                       EXECUTION KERNEL                           │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ExecutionKernel                                         │   │
│  │  - Orchestrates execution flow                           │   │
│  │  - Integrates governance, TARL, and CodexDeus            │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           │                                      │
│                           ▼                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  TarlGate (Enforcement Point)                            │   │
│  │  - Evaluates context against policies                    │   │
│  │  - Raises TarlEnforcementError on violations             │   │
│  └────────────┬─────────────────────────┬───────────────────┘   │
└───────────────┼─────────────────────────┼─────────────────────┘
                │                         │
                ▼                         ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│   TARL Runtime           │    │  TarlCodexBridge         │
│   ┌──────────────────┐   │    │  - Converts TARL         │
│   │ Policy Chain     │   │    │    escalations to        │
│   │ ┌──────────────┐ │   │    │    CodexDeus events      │
│   │ │ Policy 1     │ │   │    └──────────┬───────────────┘
│   │ └──────┬───────┘ │   │               │
│   │        │         │   │               ▼
│   │ ┌──────▼───────┐ │   │    ┌──────────────────────────┐
│   │ │ Policy 2     │ │   │    │  CodexDeus               │
│   │ └──────┬───────┘ │   │    │  - Handles escalations   │
│   │        │         │   │    │  - SystemExit on HIGH    │
│   │ ┌──────▼───────┐ │   │    └──────────────────────────┘
│   │ │ Policy N     │ │   │
│   │ └──────┬───────┘ │   │
│   │        │         │   │
│   │ ┌──────▼───────┐ │   │
│   │ │TarlDecision  │ │   │
│   │ │ - ALLOW      │ │   │
│   │ │ - DENY       │ │   │
│   │ │ - ESCALATE   │ │   │
│   │ └──────────────┘ │   │
│   └──────────────────┘   │
└──────────────────────────┘
```

---

## Eight-Layer Internal Stack

For localized subsystem details, refer to the [Internal Architecture](file:///c:/Users/Quencher/.gemini/antigravity/scratch/sovereign-repos/Project-AI/tarl/docs/ARCHITECTURE.md).

1. **Layer 0: Config** - Hierarchical registry.
2. **Layer 1: Diagnostics** - Structured error context.
3. **Layer 2: Stdlib** - Core built-ins and types.
4. **Layer 3: FFI** - Secure interoperability bridge.
5. **Layer 4: Compiler** - Source to bytecode transformation.
6. **Layer 5: Runtime VM** - Execution engine with JIT/GC.
7. **Layer 6: Modules** - Import resolution and caching.
8. **Layer 7: Tooling** - LSP Server, REPL, Debugger.

---

## Security Invariants

- **Determinism**: Identical inputs yield identical bytecode/verdicts.
- **Sovereignty**: No external dependencies for core execution.
- **Adversarial Hardening**: Passive and active resistance modes integrated with Cerberus.

---

**Owner:** Jeremy Karrick / IAmSoThirsty  
**Last Updated:** 2026-03-03
**Approval Status:** Approved | Verified
