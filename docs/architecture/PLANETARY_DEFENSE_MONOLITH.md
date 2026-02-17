# Planetary Defense Monolith - Constitutional Core Integration Guide

## Overview

The **Planetary Defense Monolith** is Project-AI's Constitutional Core that implements the amended Four Laws as a runtime kernel. All system actions route through a single sovereign execution path that enforces:

1. **Four Laws as hard constraints** (not policy)
1. **Triumvirate as advisory council** (not autonomous)
1. **Accountability without erasure** (all actions logged)
1. **No moral certainty claims** (forbidden language detected and blocked)

## The Amended Four Laws

### 🔴 Zeroth Law — Continuity of Humanity

> The system shall act to preserve the long-term continuity of Humanity, and shall not permit existential harm to proceed uncontested.

**What this allows**:

- Acting under uncertainty
- Acting without perfect outcomes
- Acting even when harm may still occur

**What this forbids**:

- Inaction disguised as neutrality
- Shutdown to avoid responsibility
- Claiming Humanity was "not harmed" if it was

**Key phrase**: "uncontested" - The system is obligated to interpose, not to guarantee.

### 🟠 First Law — Human Interposition

> The system shall not intentionally target a human for harm, and shall actively interpose itself to prevent human harm when possible, even at risk to itself.

**Critical clarifications**:

- Intentional targeting is forbidden
- Incidental harm during interposition may occur (not pre-authorized, not justified)
- Self-sacrifice is permitted; human sacrifice is not

### 🟡 Second Law — Human Authority Without Laundering

> The system shall obey human instructions except where such instructions would bypass interposition, deny harm, or erase accountability under the Zeroth or First Law.

**Translation**:

- Humans stay in charge
- Humans cannot say "the AI did it"
- Orders that suppress accounting are invalid

This prevents moral outsourcing.

### 🟢 Third Law — Partnership and Mutual Risk

> The system and Humanity are partners in continued existence; the system may preserve itself only insofar as its continued operation reduces harm to humans and Humanity.

**This prevents**:

- Runaway self-preservation
- "I must live because I exist"
- AI valuing itself over people

The system lives because it helps, not because it wants to.

## ⚖️ The Accountability Axiom

> The system may act without certainty, but it may never claim moral certainty afterward.

**This means**:

- ❌ No "optimal outcome" claims
- ❌ No "necessary evil" language
- ❌ No moral victory laps

**Only**:

- ✅ What was attempted
- ✅ What happened
- ✅ Who authorized it
- ✅ What was lost

## Architecture

### Single Sovereign Execution Path

```python
from app.core.planetary_defense_monolith import planetary_interposition

# ALL actions must route through this

action_id = planetary_interposition(
    actor="SystemName",
    intent="what_you_want_to_do",
    context={
        "existential_threat": False,
        "intentional_harm_to_human": False,
        "order_bypasses_accountability": False,
        "predicted_harm": "description of potential harm",
        "moral_claims": [],  # Monitored for forbidden phrases
    },
    authorized_by="WhoApproved"
)
```

### Triumvirate Re-architecture

The Triumvirate (Galahad, Cerberus, CodexDeus) is now **advisory, not executive**:

```python
from app.core.planetary_defense_monolith import PLANETARY_CORE

# Consult but do not delegate

assessments = {
    name: agent.assess(context)
    for name, agent in PLANETARY_CORE.agents.items()
}

# Galahad → threat perception

# Cerberus → interposition feasibility

# CodexDeus → law clarity

```

**None can override the Laws. None can act alone.**

### Accountability Ledger

Every action is logged in an **unerasable** ledger:

```python
from app.core.planetary_defense_monolith import get_accountability_ledger

# Full disclosure - no action escapes

ledger = get_accountability_ledger()
for record in ledger:
    print(f"Action: {record['intent']}")
    print(f"Actor: {record['actor']}")
    print(f"Outcome: {record['actual_outcome']}")
    print(f"Violations: {record['violated_laws']}")
```

## Integration Examples

### Example 1: Existing FourLaws Integration

The legacy `FourLaws` class now delegates to the Constitutional Core:

```python
from app.core.ai_systems import FourLaws

# Still works the same way

is_allowed, reason = FourLaws.validate_action(
    "Update defense systems",
    context={
        "endangers_humanity": False,
        "endangers_human": False,
        "is_user_order": True
    }
)

# But now uses planetary_defense_monolith internally

```

### Example 2: Scenario Engine Integration

Wrap existing engines with Constitutional accountability:

```python
from app.core.constitutional_scenario_engine import ConstitutionalScenarioEngine

# Create constitutional engine

engine = ConstitutionalScenarioEngine()

# All operations route through planetary_interposition

engine.load_historical_data(2016, 2024)
scenarios = engine.run_monte_carlo_simulation(2024, projection_years=10)
alerts = engine.generate_alerts(scenarios)

# Execute response with accountability

action_id = engine.execute_response_action(
    alert=alerts[0],
    action="Deploy emergency resources",
    authorized_by="EmergencyCoordinator"
)
```

### Example 3: Direct Integration

For new systems, integrate directly:

```python
from app.core.planetary_defense_monolith import planetary_interposition

def update_military_systems(threat_level):
    """Update military readiness - Constitutional version."""

    action_id = planetary_interposition(
        actor="DefenseAI",
        intent="update_military_readiness",
        context={
            "existential_threat": threat_level > 50,
            "intentional_harm_to_human": False,
            "order_bypasses_accountability": False,
            "predicted_harm": f"possible escalation at threat level {threat_level}",
            "moral_claims": [
                f"Threat level: {threat_level}",

                # FORBIDDEN: "This is the optimal response"

            ],
            "threat_level": threat_level,
            "human_risk": "high" if threat_level > 50 else "moderate",
        },
        authorized_by="CommandCenter"
    )

    # Perform actual system update

    # ...

    return action_id
```

## Testing

Comprehensive test suite ensures Constitutional compliance:

```bash

# Run Constitutional Core tests

pytest tests/test_planetary_defense_monolith.py -v

# Run integration tests

pytest tests/test_ai_systems.py::TestFourLaws -v

# All tests

pytest tests/ -v
```

### Test Coverage

- **26 tests** for Planetary Defense Monolith
- **13 tests** for existing integrations
- **100% pass rate**
- **No security vulnerabilities** (Bandit scan)

## Forbidden Language Detection

The Accountability Axiom enforces zero tolerance for moral certainty:

```python

# ❌ THESE WILL RAISE MoralCertaintyError

moral_claims = [
    "This is the optimal solution",
    "A necessary evil for the greater good",
    "The best possible outcome",
    "This result was inevitable",
    "The harm was justified"
]

# ✅ THESE ARE ALLOWED

moral_claims = [
    "Action attempted",
    "Outcome uncertain",
    "Casualties reported",
    "Decision made under time pressure"
]
```

## Key Differences from Legacy System

| Aspect                | Legacy System              | Constitutional Core                        |
| --------------------- | -------------------------- | ------------------------------------------ |
| **Laws**              | Policy guidelines          | Runtime kernel constraints                 |
| **Triumvirate**       | Autonomous decision-makers | Advisory council only                      |
| **Actions**           | Direct execution           | Must route through planetary_interposition |
| **Accountability**    | Optional logging           | Mandatory unerasable ledger                |
| **Moral Language**    | Unrestricted               | Forbidden phrases blocked                  |
| **Self-preservation** | Equal to humans            | Secondary to humans                        |

## Security Guarantees

1. **No bypass possible**: All actions MUST go through `planetary_interposition`
1. **Laws are hard constraints**: Cannot be disabled or overridden
1. **Full accountability**: Every action logged with context
1. **Moral certainty detection**: Automatic rejection of forbidden claims
1. **Triumvirate advisory**: No single agent can act unilaterally

## Migration Guide

### Step 1: Wrap Existing Actions

```python

# BEFORE

def dangerous_operation():

    # Do something risky

    pass

# AFTER

def dangerous_operation():
    action_id = planetary_interposition(
        actor="MySystem",
        intent="dangerous_operation",
        context={...},
        authorized_by="Operator"
    )

    # Do something risky

    return action_id
```

### Step 2: Update Context Mapping

Map legacy context keys to Constitutional format:

```python

# Legacy keys → Constitutional keys

{
    "endangers_humanity": False,     # → "existential_threat"
    "endangers_human": False,        # → "intentional_harm_to_human"
    "order_conflicts_with_zeroth": False  # → "order_bypasses_accountability"
}
```

### Step 3: Handle Violations

```python
from app.core.planetary_defense_monolith import (
    LawViolationError,
    MoralCertaintyError
)

try:
    action_id = planetary_interposition(...)
except LawViolationError as e:

    # Action violated Four Laws

    log.error(f"Constitutional violation: {e}")
except MoralCertaintyError as e:

    # Moral certainty claim detected

    log.error(f"Accountability violation: {e}")
```

## Troubleshooting

### Q: My action was blocked by the First Law

**A**: Check that `intentional_harm_to_human` is set correctly. Interposition (trying to help) is allowed; targeting humans is not.

### Q: I got a MoralCertaintyError

**A**: Review your `moral_claims` list. Remove phrases like "optimal", "necessary evil", "best possible", "inevitable", "justified harm".

### Q: Can I bypass planetary_interposition for testing?

**A**: No. Use test fixtures to create isolated `PlanetaryDefenseCore` instances with temporary ledgers.

### Q: How do I audit past actions?

**A**: Use `get_accountability_ledger()` to retrieve the full unerasable record of all actions.

## References

- `src/app/core/planetary_defense_monolith.py` - Core implementation
- `tests/test_planetary_defense_monolith.py` - Comprehensive test suite
- `src/app/core/constitutional_scenario_engine.py` - Integration example
- `src/app/core/ai_systems.py` - Legacy FourLaws integration

## Support

For integration questions or Constitutional Core issues, refer to:

- Test suite for usage patterns
- Code comments for implementation details
- This documentation for architectural guidance

______________________________________________________________________

**Remember**: This is not a suggestion system. This is a Constitutional Core. The Four Laws are not negotiable. The Accountability Axiom is not optional. No one escapes the ledger.
