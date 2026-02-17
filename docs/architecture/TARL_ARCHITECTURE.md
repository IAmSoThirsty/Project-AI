# TARL System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        APPLICATION LAYER                         │
│                     (User Code / API Calls)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      BOOTSTRAP LAYER                             │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  bootstrap.py - System Initialization & Orchestration   │    │
│  └─────────────────────────────────────────────────────────┘    │
└──────┬──────────────┬─────────────────┬────────────────────────┘
       │              │                 │
       ▼              ▼                 ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   TARL       │ │  Governance  │ │  CodexDeus   │
│  Runtime     │ │    Core      │ │  Escalation  │
└──────┬───────┘ └──────┬───────┘ └──────┬───────┘
       │                │                │
       │                │                │
       └────────────────┼────────────────┘
                        │
                        ▼
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

POLICY EVALUATION FLOW:
═══════════════════════════

Context → Runtime.evaluate()
            │
            ▼
        For each policy:
            │
            ├─→ Policy.evaluate(context)
            │        │
            │        ▼
            │   TarlDecision
            │        │
            ├────────┼─→ if ALLOW: continue
            │        │
            ├────────┼─→ if DENY: return DENY
            │        │
            └────────┼─→ if ESCALATE: return ESCALATE
                     │
                     ▼
            All policies passed
                     │
                     ▼
            Return TarlDecision(ALLOW)


COMPONENT INTERACTIONS:
═══════════════════════

1. APPLICATION → Bootstrap

   └─→ Initializes entire system

2. Bootstrap → Components

   ├─→ Creates TarlRuntime with DEFAULT_POLICIES
   ├─→ Creates CodexDeus escalation handler
   ├─→ Creates GovernanceCore
   └─→ Wires into ExecutionKernel

3. ExecutionKernel.execute(action, context)

   │
   ├─→ TarlGate.enforce(context)
   │   │
   │   ├─→ TarlRuntime.evaluate(context)
   │   │   └─→ Returns TarlDecision
   │   │
   │   ├─→ if DENY:
   │   │   └─→ raise TarlEnforcementError
   │   │
   │   └─→ if ESCALATE:
   │       ├─→ TarlCodexBridge.handle()
   │       │   └─→ CodexDeus.escalate()
   │       │       └─→ SystemExit (if HIGH)
   │       └─→ raise TarlEnforcementError
   │
   └─→ Execute action (if ALLOW)


DEFAULT POLICIES:
═════════════════

1. deny_unauthorized_mutation

   ┌────────────────────────────────┐
   │ Input: context                 │
   │ Check: mutation==True AND      │
   │        mutation_allowed==False │
   │ Result: DENY                   │
   └────────────────────────────────┘

2. escalate_on_unknown_agent

   ┌────────────────────────────────┐
   │ Input: context                 │
   │ Check: agent is None           │
   │ Result: ESCALATE               │
   └────────────────────────────────┘


DATA FLOW EXAMPLE:
══════════════════

User Request with Context:
{
  "agent": "authenticated_user",
  "mutation": True,
  "mutation_allowed": False
}
         │
         ▼
ExecutionKernel.execute()
         │
         ▼
TarlGate.enforce()
         │
         ▼
TarlRuntime.evaluate()
         │
         ├─→ Policy 1: deny_unauthorized_mutation
         │   ├─→ Check: mutation==True AND mutation_allowed==False
         │   └─→ Result: DENY ✗
         │
         └─→ Return TarlDecision(DENY, "Mutation not permitted...")
                 │
                 ▼
         TarlGate raises TarlEnforcementError
                 │
                 ▼
         ExecutionKernel propagates error
                 │
                 ▼
         Application handles error


DIRECTORY STRUCTURE:
════════════════════

Project-AI/
├── tarl/                    # TARL Security Layer
│   ├── spec.py              # TarlDecision, TarlVerdict
│   ├── policy.py            # TarlPolicy wrapper
│   ├── runtime.py           # TarlRuntime evaluator
│   ├── policies/
│   │   └── default.py       # DEFAULT_POLICIES
│   └── fuzz/
│       └── fuzz_tarl.py     # Fuzzing tool
│
├── kernel/                  # Execution Kernel
│   ├── execution.py         # ExecutionKernel
│   ├── tarl_gate.py         # TarlGate enforcer
│   └── tarl_codex_bridge.py # TARL→Codex bridge
│
├── src/cognition/codex/     # Codex System
│   ├── engine.py            # ML inference
│   └── escalation.py        # CodexDeus escalation
│
├── governance/              # Governance Layer
│   └── core.py              # GovernanceCore
│
└── bootstrap.py             # System initialization


SECURITY LAYERS:
════════════════

Layer 1: TARL Runtime
  └─→ Policy-based runtime authorization

Layer 2: Execution Kernel
  └─→ Orchestrates secure execution

Layer 3: CodexDeus Escalation
  └─→ Handles critical security events

Layer 4: Governance Core
  └─→ System-wide policies and audit
```
