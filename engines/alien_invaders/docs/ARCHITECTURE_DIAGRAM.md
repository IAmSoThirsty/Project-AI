# Planetary Defense Monolith - Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Project-AI Ecosystem                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      SimulationRegistry                                  │
│                   (with Projection Enforcement)                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  Read-Only Access (Default)          Mutable Access (Restricted)        │
│  ┌──────────────────┐                ┌──────────────────┐              │
│  │  Projection Mode │                │ Requires:        │              │
│  │  Always Granted  │                │ 1. from_monolith │              │
│  │                  │                │ 2. law_eval pass │              │
│  │  Returns:        │                │ 3. accountability│              │
│  │  - Scenarios     │                │                  │              │
│  │  - Projections   │                │ Returns:         │              │
│  │  - Alerts        │                │ - Mutable ref    │              │
│  └──────────────────┘                └──────────────────┘              │
│         ▲                                      ▲                         │
│         │                                      │                         │
│         └──────────────────┬───────────────────┘                        │
│                            │                                             │
└────────────────────────────┼─────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                 Planetary Defense Monolith                               │
│                  (Constitutional Kernel)                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐        │
│  │  Integration A  │  │  Integration B  │  │  Integration C  │        │
│  │                 │  │                 │  │                 │        │
│  │   Invariants    │  │  Causal Clock   │  │  Access Control │        │
│  │   as Laws       │  │  as Authority   │  │  Enforcement    │        │
│  │                 │  │                 │  │                 │        │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │        │
│  │  │ evaluate_ │  │  │  │ advance_  │  │  │  │authorize_ │  │        │
│  │  │ action()  │  │  │  │ time()    │  │  │  │registry_  │  │        │
│  │  │           │  │  │  │           │  │  │  │access()   │  │        │
│  │  │ • Checks  │  │  │  │ • Logical │  │  │  │           │  │        │
│  │  │   invaria │  │  │  │   time++  │  │  │  │ • Check   │  │        │
│  │  │   nts     │  │  │  │ • Record  │  │  │  │   context │  │        │
│  │  │ • Returns │  │  │  │   history │  │  │  │ • Generate│  │        │
│  │  │   verdict │  │  │  │ • Single  │  │  │  │   account │  │        │
│  │  │           │  │  │  │   source  │  │  │  │           │  │        │
│  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │        │
│  │                 │  │                 │  │                 │        │
│  │  ┌───────────┐  │  │  ┌───────────┐  │  │  ┌───────────┐  │        │
│  │  │CompositeIn│  │  │  │CausalClock│  │  │  │ Registry  │  │        │
│  │  │variant    │  │  │  │           │  │  │  │ Access    │  │        │
│  │  │Validator  │  │  │  │ logical_  │  │  │  │ Request   │  │        │
│  │  │           │  │  │  │ time: int │  │  │  │           │  │        │
│  │  └───────────┘  │  │  └───────────┘  │  │  └───────────┘  │        │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘        │
│                                                                           │
│  ┌───────────────────────────────────────────────────────────┐          │
│  │              Accountability & Auditing                      │          │
│  │                                                             │          │
│  │  action_log: List[(ActionRequest, ActionVerdict)]         │          │
│  │  access_log: List[(RegistryAccessRequest, bool)]          │          │
│  └───────────────────────────────────────────────────────────┘          │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
                             │
                             │ Controls
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   AlienInvadersEngine                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  tick() {                          inject_event() {                     │
│    1. monolith.advance_time()       1. logical_time = monolith.        │
│    2. Update day_number                advance_time()                   │
│    3. ActionRequest created          2. Create CausalEvent              │
│    4. verdict = monolith.            3. Queue for next tick             │
│       evaluate_action()              4. Return event_id                 │
│    5. If !verdict.allowed:         }                                    │
│         return False                                                    │
│    6. Process subsystems                                                │
│    7. Return True                                                       │
│  }                                                                      │
│                                                                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                    │
│  │ World State │  │  Event Queue│  │  Validation │                    │
│  │             │  │             │  │   History   │                    │
│  │ • Countries │  │ • Pending   │  │             │                    │
│  │ • Resources │  │ • Executed  │  │ • Per-tick  │                    │
│  │ • Population│  │ • Ordered   │  │ • Violations│                    │
│  └─────────────┘  └─────────────┘  └─────────────┘                    │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Action Evaluation Flow (Integration Point A)

```
┌─────────────┐
│   Engine    │
│   tick()    │
└──────┬──────┘
       │
       │ 1. Create ActionRequest
       ▼
┌────────────────────────────────────┐
│  Monolith.evaluate_action()        │
├────────────────────────────────────┤
│  2. Run invariant validation       │
│     - Resource → Economic          │
│     - Economic → Societal          │
│     - Societal → Political         │
│     - Political → AI Governance    │
│                                    │
│  3. Check violations               │
│     if violations found:           │
│       return ActionVerdict(        │
│         allowed=False,             │
│         reason="ILLEGAL",          │
│         violations=[...]           │
│       )                            │
│                                    │
│  4. Generate accountability        │
│     - action_id                    │
│     - requestor                    │
│     - logical_time                 │
│     - timestamp                    │
│                                    │
│  5. Log to action_log              │
└────────────┬───────────────────────┘
             │
             │ ActionVerdict
             ▼
       ┌───────────┐
       │  Verdict  │
       │  .allowed │
       │  .reason  │
       │.violations│
       └───────────┘
```

### Time Advancement Flow (Integration Point B)

```
┌────────────┐     ┌────────────┐     ┌────────────┐
│  Engine    │────▶│  Monolith  │────▶│   Causal   │
│  tick()    │     │advance_time│     │   Clock    │
└────────────┘     └────────────┘     └────────────┘
                                              │
                                              │ logical_time++
                                              ▼
                                       ┌────────────┐
                                       │  History   │
                                       │  Record    │
                                       └────────────┘

Timeline:
t=0 ────▶ tick() ────▶ t=1 ────▶ tick() ────▶ t=2 ────▶ ...
          ▲                       ▲
          │                       │
    Monolith only            Monolith only
```

### Registry Access Flow (Integration Point C)

```
┌──────────────┐
│  Requestor   │
└──────┬───────┘
       │
       │ 1. Request access
       ▼
┌─────────────────────────────┐
│   SimulationRegistry        │
│   .get(name, mutable=?)     │
└──────┬──────────────────────┘
       │
       │ 2. Check projection mode
       ▼
┌─────────────────────────────┐     ┌───────────┐
│  If mutable=True:           │────▶│ Monolith  │
│    Call monolith.authorize_ │     │ authorize_│
│    registry_access()        │     │ registry_ │
│                             │◀────│ access()  │
│  Else:                      │     └───────────┘
│    Grant read-only access   │            │
└─────────┬───────────────────┘            │
          │                                │
          │ 3. Return based on verdict    │
          ▼                                ▼
    ┌──────────┐                  ┌──────────────┐
    │Read-only │                  │   Mutable    │
    │projection│                  │(if approved) │
    └──────────┘                  └──────────────┘
```

## Key Invariants

### Time Invariants

- ✅ Logical time is monotonically increasing
- ✅ No entity can advance time except monolith
- ✅ All events are timestamped with logical time
- ✅ Event execution order is deterministic

### Law Invariants

- ✅ Physical coherence violations are illegal
- ✅ All actions pass through law evaluation
- ✅ Violations generate accountability records
- ✅ Action log is append-only

### Access Invariants

- ✅ Read-only access is default
- ✅ Mutable access requires monolith context
- ✅ Mutable access requires law evaluation
- ✅ All access generates audit trail

## Trust Boundaries

```
┌─────────────────────────────────────────────────────┐
│              Untrusted Zone                          │
│                                                       │
│  • External systems                                  │
│  • User-injected events                              │
│  • Registry read requests                            │
│                                                       │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Read-only projection
                 │ (always granted)
                 ▼
┌─────────────────────────────────────────────────────┐
│           Projection Layer                           │
│        (SimulationRegistry)                          │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Requires authorization
                 ▼
┌─────────────────────────────────────────────────────┐
│           Trusted Zone                               │
│     (Planetary Defense Monolith)                     │
│                                                       │
│  • Law evaluation                                    │
│  • Time authority                                    │
│  • Access control                                    │
│                                                       │
└────────────────┬────────────────────────────────────┘
                 │
                 │ Controlled execution
                 ▼
┌─────────────────────────────────────────────────────┐
│          Engine Zone                                 │
│     (AlienInvadersEngine)                            │
│                                                       │
│  • State updates                                     │
│  • Subsystem processing                              │
│  • Event execution                                   │
│                                                       │
└─────────────────────────────────────────────────────┘
```

## Accountability Chain

Every operation creates an immutable record:

```
Action Request → Law Evaluation → Verdict → Execution → State Change
      │               │              │          │            │
      └───────────────┴──────────────┴──────────┴────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Accountability │
                  │    Record      │
                  ├────────────────┤
                  │ • action_id    │
                  │ • requestor    │
                  │ • logical_time │
                  │ • timestamp    │
                  │ • verdict      │
                  │ • violations   │
                  └────────────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │   Audit Log    │
                  │ (append-only)  │
                  └────────────────┘
```

## Summary

The Planetary Defense Monolith creates a **three-layer security architecture**:

1. **Constitutional Layer** (Monolith): Enforces laws, controls time, manages access
2. **Projection Layer** (Registry): Provides read-only views by default
3. **Execution Layer** (Engine): Processes authorized actions with full accountability

This architecture ensures that **physical coherence is legally enforced**, **time is deterministically controlled**, and **access is earned through verification** - making the system fundamentally more correct, auditable, and secure.
