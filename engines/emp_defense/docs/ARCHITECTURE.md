# EMP Defense Engine - Architecture Diagram

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Project-AI Ecosystem                      │
│                                                              │
│  ┌────────────────────────────────────────────────────┐     │
│  │           Defense Engine Registry                  │     │
│  │  (Future Integration Point)                        │     │
│  └────────────────────────────────────────────────────┘     │
│                           │                                  │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │         EMP Defense Engine                         │     │
│  │                                                     │     │
│  │  Mandatory Interface (5 Methods):                  │     │
│  │  • init() → bool                                   │     │
│  │  • tick() → bool                                   │     │
│  │  • inject_event(type, params) → str                │     │
│  │  • observe(query) → dict                           │     │
│  │  • export_artifacts(dir) → bool                    │     │
│  └────────────────────────────────────────────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EMPDefenseEngine                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐   │
│  │  Configuration   │  │   World State    │  │   Events    │   │
│  │                  │  │                  │  │             │   │
│  │ • scenario       │  │ • simulation_day │  │ • type      │   │
│  │ • duration_years │  │ • population     │  │ • params    │   │
│  │ • grid_failure   │  │ • deaths         │  │ • timestamp │   │
│  │ • affected_pct   │  │ • grid_pct       │  │ • id        │   │
│  │                  │  │ • gdp            │  │             │   │
│  └──────────────────┘  └──────────────────┘  └─────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │              Core Simulation Loop                        │   │
│  │                                                          │   │
│  │  init() → _apply_emp_event()                            │   │
│  │    ↓                                                     │   │
│  │  tick() → _update_world_state()                         │   │
│  │    ↓                                                     │   │
│  │  observe() → state.to_dict()                            │   │
│  │    ↓                                                     │   │
│  │  export_artifacts() → JSON files                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

```
┌──────────────┐
│  User Code   │
└──────┬───────┘
       │
       │ 1. Create engine with config
       ▼
┌─────────────────────┐
│  EMPDefenseEngine   │
│  (uninitialized)    │
└──────┬──────────────┘
       │
       │ 2. init()
       ▼
┌─────────────────────┐
│  Initial EMP Event  │
│  - Grid failure     │
│  - Population calc  │
└──────┬──────────────┘
       │
       │ 3. tick() × N
       ▼
┌─────────────────────┐       ┌─────────────────┐
│  Week-by-Week       │──────▶│  State Updates  │
│  Simulation         │       │  - Day + 7      │
│                     │       │  - Grid recovery│
│                     │       │  - Deaths calc  │
└──────┬──────────────┘       │  - GDP update   │
       │                      └─────────────────┘
       │ 4. inject_event()
       ▼
┌─────────────────────┐
│  External Events    │
│  - Recovery efforts │
│  - Resources found  │
└──────┬──────────────┘
       │
       │ 5. observe()
       ▼
┌─────────────────────┐
│  State Dictionary   │
│  (read-only view)   │
└──────┬──────────────┘
       │
       │ 6. export_artifacts()
       ▼
┌─────────────────────┐
│  JSON Artifacts     │
│  - final_state.json │
│  - events.json      │
│  - summary.json     │
└─────────────────────┘
```

## State Transitions

```
[PRE-EMP] → [EMP EVENT] → [IMMEDIATE IMPACT] → [RECOVERY PHASE] → [NEW EQUILIBRIUM]
    │            │               │                    │                    │
    │            │               │                    │                    │
  Day 0       Day 0          Day 0-30           Day 30-365           Day 365+
    │            │               │                    │                    │
Grid: 100%   Grid: 10%      Grid: 10-11%        Grid: 11-14%        Grid: 14%+
Pop:  8B     Pop:  8B       Pop:  7.99B         Pop:  7.95B         Pop:  stable
GDP:  $100T  GDP:  $10T     GDP:  $10-11T       GDP:  $11-14T       GDP:  $14T+
```

## EMP Simulation Model

```
┌─────────────────────────────────────────────────────────┐
│                 EMP Event Impact                         │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
        ┌──────────────────────────────────┐
        │       Grid Failure               │
        │  (90% in standard scenario)      │
        └─────────┬────────────────────────┘
                  │
       ┏━━━━━━━━━━┻━━━━━━━━━━┓
       ▼                      ▼
┌─────────────┐      ┌─────────────────┐
│  Economic   │      │   Population    │
│  Collapse   │      │   Impact        │
│             │      │                 │
│ GDP drops   │      │ Deaths from:    │
│ to 10% of   │      │ • Grid loss     │
│ baseline    │      │ • Secondary     │
│             │      │   effects       │
└─────────────┘      └─────────────────┘
       │                      │
       └──────────┬───────────┘
                  ▼
        ┌─────────────────┐
        │ Slow Recovery   │
        │ +0.1% per week  │
        └─────────────────┘
```

## Time Step Model

```
Time Step: 7 days (weekly)

Week 0  (Day 0):    EMP event → 90% grid failure
Week 1  (Day 7):    Recovery begins → 10.1% grid
Week 2  (Day 14):   Slow progress → 10.2% grid
Week 4  (Day 28):   First month → 10.4% grid
Week 13 (Day 91):   Quarter → 11.3% grid
Week 52 (Day 364):  One year → 14.2% grid
```

## Configuration Options

```
┌────────────────────────────────────────────────────┐
│              SimulationConfig                      │
├────────────────────────────────────────────────────┤
│                                                    │
│  ┌───────────────┐          ┌──────────────────┐  │
│  │   Standard    │          │     Severe       │  │
│  │   Scenario    │          │     Scenario     │  │
│  ├───────────────┤          ├──────────────────┤  │
│  │ Grid: 90%     │          │ Grid: 98%        │  │
│  │ Affected: 35% │          │ Affected: 85%    │  │
│  │ Duration: 10y │          │ Duration: 30y    │  │
│  └───────────────┘          └──────────────────┘  │
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │           Custom Configuration                │ │
│  │  (User-defined parameters)                   │ │
│  └──────────────────────────────────────────────┘ │
│                                                    │
└────────────────────────────────────────────────────┘
```

## Future Integration Points

```
┌─────────────────────────────────────────────────────────┐
│         Planetary Defense Monolith                       │
│         (Future Integration)                             │
│                                                          │
│  • Constitutional Law Validation                         │
│  • Causal Clock Authority                                │
│  • Access Control Enforcement                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│         SimulationRegistry                               │
│         (Future Integration)                             │
│                                                          │
│  • Multi-scenario management                             │
│  • Cross-engine compatibility                            │
│  • Shared artifact generation                            │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│         EMP Defense Engine                               │
│         (Current Implementation)                         │
│                                                          │
│  • 5 mandatory methods ✅                                │
│  • Basic EMP modeling ✅                                 │
│  • Event system ✅                                       │
│  • Artifact generation ✅                                │
└─────────────────────────────────────────────────────────┘
```

## Directory Structure

```
engines/emp_defense/
│
├── __init__.py              # Package exports
│   └── EMPDefenseEngine, EMPScenario, SimulationConfig
│
├── engine.py                # Core simulation engine
│   ├── EMPDefenseEngine class
│   │   ├── init()
│   │   ├── tick()
│   │   ├── inject_event()
│   │   ├── observe()
│   │   └── export_artifacts()
│   └── Helper methods
│
├── schemas/
│   ├── __init__.py
│   └── config_schema.py     # Configuration classes
│       ├── EMPScenario enum
│       ├── SimulationConfig dataclass
│       └── load_scenario_preset()
│
├── modules/
│   ├── __init__.py
│   └── world_state.py       # State data structures
│       ├── WorldState dataclass
│       └── to_dict() / from_dict()
│
├── tests/
│   ├── __init__.py
│   ├── test_engine.py       # Pytest tests (20 tests)
│   └── manual_test.py       # Manual tests (8 tests)
│
├── docs/
│   ├── README.md            # User documentation
│   └── ARCHITECTURE.md      # This file
│
└── artifacts/               # Generated outputs
    ├── final_state.json
    ├── events.json
    └── summary.json
```

---

**Version**: 1.0.0  
**Status**: Core architecture complete  
**Last Updated**: 2026-02-03
