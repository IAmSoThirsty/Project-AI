# Irreversibility Formalization: From Warnings to Physics

## Overview

The HYDRA-50 Contingency Plan Engine now enforces irreversibility as **physics**, not warnings. Once a scenario crosses the point of no return, state locks create permanent constraints on the system. This prevents unrealistic recovery assumptions and models true collapse dynamics.

## Core Concept

**Traditional Systems**: Detect irreversibility, log warnings, hope humans notice.

**HYDRA-50**: Detect irreversibility, **enforce state locks**, make recovery physically impossible.

### The Three Pillars of State Locks

1. **Variable Constraints** - Certain metrics can never increase again
2. **Disabled Recovery Events** - Certain interventions permanently blocked
3. **Governance Ceilings** - Legitimacy/capacity capped forever

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    IRREVERSIBILITY DETECTOR                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  assess_irreversibility()                                   │ │
│  │    ↓                                                        │ │
│  │  IF irreversibility_score > 0.7:                           │ │
│  │    ↓                                                        │ │
│  │  create_state_lock()                                       │ │
│  │    ├─> Generate variable constraints                       │ │
│  │    ├─> Disable recovery events                             │ │
│  │    └─> Lower governance ceilings                           │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      IRREVERSIBILITY LOCK                        │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Lock ID: S01_LOCK_a3f7e9b2                                │ │
│  │  Scenario: AI Reality Flood (S01)                          │ │
│  │  Score: 0.85 (High Irreversibility)                        │ │
│  │  Created: 2026-02-03T19:45:00Z                             │ │
│  │                                                             │ │
│  │  Variable Constraints (3):                                 │ │
│  │    ├─ verification_capacity [CEILING=0.5, NEVER↑]         │ │
│  │    ├─ public_trust_score [CEILING=0.3, NEVER↑]            │ │
│  │    └─ synthetic_content_ratio [FLOOR=0.8, NEVER↓]         │ │
│  │                                                             │ │
│  │  Disabled Recovery Events (2):                             │ │
│  │    ├─ centralized_fact_checking (reason: trust collapse)  │ │
│  │    └─ blockchain_verification_theater (recovery poison)   │ │
│  │                                                             │ │
│  │  Governance Ceilings (4):                                  │ │
│  │    ├─ democratic_legitimacy: 1.0 → 0.48 (52% reduction)   │ │
│  │    ├─ institutional_trust: 1.0 → 0.48 (52% reduction)     │ │
│  │    ├─ policy_effectiveness: 1.0 → 0.48 (52% reduction)    │ │
│  │    └─ fiscal_capacity: 1.0 → 0.34 (66% reduction)         │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        ENFORCEMENT                               │
│                                                                  │
│  update_metrics({"verification_capacity": 0.8})                │
│    → ValueError: verification_capacity can never increase       │
│                                                                  │
│  attempt_recovery("centralized_fact_checking")                 │
│    → BLOCKED: Recovery event permanently disabled              │
│                                                                  │
│  check_governance_ceiling("democratic_legitimacy")             │
│    → 0.48 (original: 1.0)                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Models

### 1. VariableConstraint

Enforces hard limits on variable values.

```python
@dataclass
class VariableConstraint:
    variable_name: str
    constraint_type: str  # "ceiling" or "floor"
    locked_value: float
    locked_at: datetime
    reason: str
    can_never_increase: bool = False
    can_never_decrease: bool = False
```

**Validation Logic:**

```python
def validate(self, new_value: float) -> Tuple[bool, str]:
    # Priority 1: can_never constraints
    if self.can_never_increase and new_value > self.locked_value:
        return False, "can never increase (irreversible degradation)"
    
    # Priority 2: ceiling/floor constraints
    if self.constraint_type == "ceiling" and new_value > self.locked_value:
        return False, "cannot exceed ceiling"
    
    return True, ""
```

**Examples by Category:**

| Category | Variable | Constraint | Reason |
|----------|----------|------------|--------|
| Digital/Cognitive | `verification_capacity` | Ceiling, Never↑ | Epistemic collapse |
| Economic | `currency_confidence` | Ceiling, Never↑ | Trust destruction |
| Infrastructure | `infrastructure_capacity` | Ceiling, Never↑ | Physical damage |
| Biological | `ecosystem_health` | Ceiling, Never↑ | Biodiversity loss |
| Societal | `social_cohesion` | Ceiling, Never↑ | Fracture irreversible |

### 2. DisabledRecoveryEvent

Permanently blocks recovery actions.

```python
@dataclass
class DisabledRecoveryEvent:
    event_name: str
    disabled_at: datetime
    reason: str
    scenario_id: str
    alternative_actions: List[str]
```

**Automatic Disabling:**

1. **Recovery Poisons** - All recovery poisons automatically disabled (they were traps)
2. **Category-Specific Events:**
   - Digital/Cognitive: `centralized_fact_checking` (trust collapse)
   - Economic: `monetary_policy_intervention` (currency confidence destroyed)
   - Societal: `institutional_reform` (legitimacy lost)

**Usage:**

```python
# Check if recovery allowed
is_allowed, reason = scenario.check_recovery_event_allowed("centralized_fact_checking")

if not is_allowed:
    logger.error(f"Recovery blocked: {reason}")
    # reason: "Trust collapse: centralized authorities no longer credible"
```

### 3. GovernanceCeiling

Permanently lowers governance capacity.

```python
@dataclass
class GovernanceCeiling:
    domain: str
    original_ceiling: float
    lowered_ceiling: float
    lowered_at: datetime
    reason: str
    multiplier: float  # Compound reduction
```

**Ceiling Calculation:**

```python
effective_ceiling = lowered_ceiling * multiplier
```

**Universal Reductions (All Scenarios):**

| Domain | Original | Reduction | Final |
|--------|----------|-----------|-------|
| `democratic_legitimacy` | 1.0 | 20-60% | 0.4-0.8 |
| `institutional_trust` | 1.0 | 20-60% | 0.4-0.8 |
| `policy_effectiveness` | 1.0 | 20-60% | 0.4-0.8 |

**Category-Specific Reductions:**

- **Economic**: `fiscal_capacity` (extra 30% reduction)
- **Societal**: `social_mandate` (extra 40% reduction)

**Reduction Tiers by Irreversibility Score:**

| Score | Multiplier | Meaning |
|-------|------------|---------|
| 0.7-0.8 | 0.8 | Moderate collapse |
| 0.8-0.9 | 0.6 | Severe collapse |
| 0.9-1.0 | 0.4 | Catastrophic collapse |

---

## Enforcement Mechanisms

### 1. Metric Update Enforcement

**Before State Locks:**
```python
scenario.update_metrics({"verification_capacity": 0.8})
# ✓ Success
```

**After State Locks:**
```python
scenario.update_metrics({"verification_capacity": 0.8})
# ✗ ValueError: verification_capacity can never increase (irreversible degradation)
```

**Implementation:**

```python
def update_metrics(self, metrics: Dict[str, float]) -> None:
    # Validate against active locks
    for lock in self.active_locks:
        for constraint in lock.variable_constraints:
            if constraint.variable_name in metrics:
                is_valid, reason = constraint.validate(metrics[constraint.variable_name])
                if not is_valid:
                    raise ValueError(f"Irreversibility constraint violated: {reason}")
    
    # Update only if all constraints pass
    self.metrics.update(metrics)
```

### 2. Recovery Event Blocking

**Engine-Level Attempt:**

```python
result = engine.attempt_recovery_action(
    scenario_id="S01",
    recovery_action="centralized_fact_checking",
    user_id="analyst_42"
)

# Result:
{
    "success": False,
    "blocked": True,
    "reason": "Recovery event permanently disabled: Trust collapse",
    "alternative_actions": ["distributed_verification", "community_consensus"]
}
```

**Event Sourcing:**

All blocked attempts are logged in the event log:

```python
EventRecord(
    event_type="recovery_attempt_blocked",
    scenario_id="S01",
    data={"recovery_action": "centralized_fact_checking", "block_reason": "..."},
    timestamp=datetime.utcnow()
)
```

### 3. Governance Ceiling Queries

**Check Effective Ceiling:**

```python
ceiling = scenario.get_governance_ceiling("democratic_legitimacy")
# Returns: 0.48 (if locked)
# Returns: None (if not locked)
```

**With Multiple Locks:**

If multiple locks affect the same domain, the **lowest (most restrictive) ceiling** is returned:

```python
lock1.governance_ceilings = [GovernanceCeiling(domain="trust", lowered_ceiling=0.7, ...)]
lock2.governance_ceilings = [GovernanceCeiling(domain="trust", lowered_ceiling=0.5, ...)]

scenario.get_governance_ceiling("trust")
# Returns: 0.5 (lowest)
```

---

## Lock Creation Flow

### Automatic Creation During Tick

```python
def run_tick(self) -> Dict[str, Any]:
    for scenario in active_scenarios:
        # Assess irreversibility
        assessment = self.irreversibility_detector.assess_irreversibility(
            scenario, time_elapsed
        )
        
        if assessment["irreversible"]:
            # Check if not already locked
            if not self._has_lock(scenario):
                # Create and enforce state lock
                lock = self.irreversibility_detector.create_state_lock(
                    scenario=scenario,
                    irreversibility_score=assessment["score"],
                    triggered_collapses=assessment["triggered_collapses"]
                )
                
                logger.critical(
                    f"STATE LOCK ENFORCED: {scenario.name} - "
                    f"Physics now prevents: {len(lock.variable_constraints)} variables, "
                    f"{len(lock.disabled_recovery_events)} events disabled, "
                    f"{len(lock.governance_ceilings)} ceilings lowered"
                )
```

### Lock Generation Logic

**Step 1: Generate Variable Constraints**

```python
def _generate_variable_constraints(scenario, irreversibility_score, triggered_collapses):
    constraints = []
    
    # Category-specific logic
    if scenario.category == ScenarioCategory.DIGITAL_COGNITIVE:
        if "epistemic_collapse" in triggered_collapses:
            constraints.append(
                VariableConstraint(
                    variable_name="verification_capacity",
                    constraint_type="ceiling",
                    locked_value=scenario.metrics.get("verification_capacity", 0.5),
                    reason="Epistemic collapse: verification infrastructure permanently degraded",
                    can_never_increase=True
                )
            )
    
    # ... similar logic for other categories
    return constraints
```

**Step 2: Disable Recovery Events**

```python
def _generate_disabled_recovery_events(scenario, triggered_collapses):
    disabled = []
    
    # Disable all recovery poisons (they were traps anyway)
    for poison in scenario.recovery_poisons:
        disabled.append(DisabledRecoveryEvent(
            event_name=poison.name,
            reason=f"Recovery poison detected: {poison.hidden_damage}",
            scenario_id=scenario.scenario_id
        ))
    
    # Category-specific disabled events
    if scenario.category == ScenarioCategory.DIGITAL_COGNITIVE:
        if "epistemic_collapse" in triggered_collapses:
            disabled.append(DisabledRecoveryEvent(
                event_name="centralized_fact_checking",
                reason="Trust collapse: centralized authorities no longer credible",
                alternative_actions=["distributed_verification"]
            ))
    
    return disabled
```

**Step 3: Lower Governance Ceilings**

```python
def _generate_governance_ceilings(scenario, irreversibility_score):
    ceilings = []
    
    # Calculate ceiling multiplier based on score
    if irreversibility_score >= 0.9:
        ceiling_multiplier = 0.4
    elif irreversibility_score >= 0.8:
        ceiling_multiplier = 0.6
    else:
        ceiling_multiplier = 0.8
    
    # Universal ceilings (all scenarios)
    ceilings.append(GovernanceCeiling(
        domain="democratic_legitimacy",
        original_ceiling=1.0,
        lowered_ceiling=1.0 * ceiling_multiplier,
        reason="Public faith in democratic processes permanently reduced",
        multiplier=ceiling_multiplier
    ))
    
    # Category-specific additional reductions
    if scenario.category == ScenarioCategory.ECONOMIC:
        ceilings.append(GovernanceCeiling(
            domain="fiscal_capacity",
            lowered_ceiling=1.0 * ceiling_multiplier * 0.7,  # Extra 30% reduction
            multiplier=ceiling_multiplier * 0.7
        ))
    
    return ceilings
```

---

## Usage Examples

### Example 1: Digital Cognitive Collapse

```python
# Scenario: AI Reality Flood (S01)
scenario = engine.scenarios["S01"]
scenario.activation_time = datetime.utcnow() - timedelta(days=1000)

# Metrics degrade over time
scenario.update_metrics({
    "verification_capacity": 0.5,
    "public_trust_score": 0.3,
    "synthetic_content_ratio": 0.8
})

# Tick detects irreversibility
result = engine.run_tick()

# Lock created automatically
lock = scenario.active_locks[0]
print(f"Constraints: {len(lock.variable_constraints)}")
# Output: Constraints: 2

print(f"Disabled events: {len(lock.disabled_recovery_events)}")
# Output: Disabled events: 2

# Try to improve verification capacity
try:
    scenario.update_metrics({"verification_capacity": 0.7})
except ValueError as e:
    print(e)
    # Output: verification_capacity can never increase (irreversible degradation)

# Check governance ceiling
ceiling = scenario.get_governance_ceiling("democratic_legitimacy")
print(f"Democratic legitimacy ceiling: {ceiling}")
# Output: Democratic legitimacy ceiling: 0.48
```

### Example 2: Economic Collapse

```python
# Scenario: Sovereign Debt Cascade (S11)
scenario = engine.scenarios["S11"]
scenario.activation_time = datetime.utcnow() - timedelta(days=900)

scenario.update_metrics({
    "currency_confidence": 0.4,
    "market_liquidity": 0.5,
    "debt_ratio": 2.5
})

# Run tick - creates lock
result = engine.run_tick()

# Try monetary policy intervention
recovery_result = engine.attempt_recovery_action(
    scenario_id="S11",
    recovery_action="monetary_policy_intervention",
    user_id="central_bank"
)

print(recovery_result)
# Output:
# {
#     "success": False,
#     "blocked": True,
#     "reason": "Currency confidence destroyed: monetary policy lost effectiveness",
#     "alternative_actions": ["alternative_currencies", "barter_systems"]
# }

# Check fiscal capacity ceiling
fiscal_ceiling = scenario.get_governance_ceiling("fiscal_capacity")
print(f"Fiscal capacity: {fiscal_ceiling}")
# Output: Fiscal capacity: 0.252 (75% reduction)
```

### Example 3: Querying Lock State

```python
# Get all active locks
summary = engine.get_state_lock_summary()

print(summary["summary"])
# Output: "3 irreversibility locks active, enforcing 8 variable constraints, 
#          6 recovery events disabled, 12 governance ceilings lowered"

# Get specific lock details
lock_details = engine.irreversibility_detector.get_lock_summary("S01_LOCK_a3f7e9b2")

print(lock_details["variable_constraints"])
# Output:
# [
#     {
#         "variable_name": "verification_capacity",
#         "constraint_type": "ceiling",
#         "locked_value": 0.5,
#         "can_never_increase": True,
#         "reason": "Epistemic collapse"
#     },
#     ...
# ]

# Dashboard view
dashboard = engine.get_dashboard_state()
print(f"Locked scenarios: {dashboard['locked_count']}")
print(f"Active state locks: {dashboard['active_state_locks']}")
```

---

## Integration with Existing Systems

### 1. Event Sourcing

All lock-related events are recorded in the event log:

```python
# Lock creation event
EventRecord(
    event_type="state_lock_created",
    scenario_id="S01",
    data={
        "lock_id": "S01_LOCK_a3f7e9b2",
        "irreversibility_score": 0.85,
        "constraints": 2,
        "disabled_events": 2,
        "ceilings": 4
    }
)

# Constraint violation event (via update_metrics exception)
EventRecord(
    event_type="constraint_violation_attempted",
    scenario_id="S01",
    data={
        "variable": "verification_capacity",
        "attempted_value": 0.8,
        "constraint_value": 0.5
    }
)
```

### 2. State Snapshots

State snapshots now include active lock IDs:

```python
@dataclass
class ScenarioState:
    scenario_id: str
    timestamp: datetime
    status: ScenarioStatus
    escalation_level: EscalationLevel
    active_triggers: List[str]
    metrics: Dict[str, float]
    coupled_scenarios: List[str]
    active_locks: List[str]  # Lock IDs
```

### 3. Time-Travel Replay

Locks are reconstructed during replay:

```python
# Replay to specific timestamp
engine.replay_to_timestamp(target_time)

# Locks are automatically recreated when:
# 1. Irreversibility assessments return True
# 2. Lock creation events are replayed
```

### 4. Counterfactual Branching

Locks persist in branches unless explicitly removed:

```python
# Create what-if scenario
branch = engine.create_counterfactual_branch(
    branch_name="optimistic_recovery",
    branch_point=datetime.utcnow() - timedelta(days=500),
    alternate_events=[
        {"scenario_id": "S01", "metrics": {"verification_capacity": 0.6}}
    ]
)

# Branch will fail if trying to violate existing locks
# This demonstrates why recovery is impossible
```

---

## Testing

### Test Coverage

31 comprehensive tests covering:

1. **Data Model Tests** (10 tests)
   - Constraint validation logic
   - Disabled event serialization
   - Governance ceiling calculation

2. **Enforcement Tests** (9 tests)
   - Metric update blocking
   - Recovery event blocking
   - Governance ceiling queries

3. **Integration Tests** (7 tests)
   - Lock creation during tick
   - Dashboard integration
   - State snapshot inclusion

4. **Category-Specific Tests** (5 tests)
   - Digital/Cognitive constraints
   - Economic constraints
   - Infrastructure constraints
   - Biological/Environmental constraints
   - Societal constraints

### Running Tests

```bash
# Run all irreversibility tests
pytest tests/test_irreversibility_locks.py -v

# Run specific test class
pytest tests/test_irreversibility_locks.py::TestVariableConstraints -v

# Run with coverage
pytest tests/test_irreversibility_locks.py --cov=app.core.hydra_50_engine
```

---

## Performance Considerations

### Lock Creation Overhead

Lock creation is **one-time per scenario** when irreversibility threshold crossed:

- Variable constraint generation: O(n) where n = number of metrics
- Recovery event disabling: O(m) where m = number of recovery poisons
- Governance ceiling generation: O(1) (fixed number of domains)

**Optimization**: Locks are cached in `IrreversibilityDetector.active_locks` dict for O(1) lookup.

### Validation Overhead

Metric updates check all active locks:

- Per-scenario validation: O(c) where c = number of constraints in active locks
- Typical: 2-5 constraints per lock, 1-3 locks per scenario
- Impact: Negligible (<1ms per update)

**Optimization**: Early exit on first constraint violation.

### Memory Footprint

Each lock occupies approximately:

- Base lock: ~200 bytes
- Per constraint: ~150 bytes
- Per disabled event: ~200 bytes
- Per governance ceiling: ~180 bytes

**Typical lock**: 2KB-5KB

**100 active locks**: 200KB-500KB (negligible)

---

## Future Enhancements

### 1. Lock Strength Degradation

Currently locks are permanent. Future: locks can weaken over extremely long timescales (decades):

```python
class IrreversibilityLock:
    strength_half_life: timedelta  # e.g., 50 years
    
    def get_current_strength(self) -> float:
        elapsed = datetime.utcnow() - self.locked_at
        half_lives = elapsed / self.strength_half_life
        return 0.5 ** half_lives
```

### 2. Lock Cascades

Currently locks are per-scenario. Future: locks can propagate across coupled scenarios:

```python
def propagate_lock(source_lock: IrreversibilityLock, target_scenario: BaseScenario):
    # Attenuated constraint propagation
    for constraint in source_lock.variable_constraints:
        if constraint.variable_name in target_scenario.metrics:
            target_constraint = VariableConstraint(
                variable_name=constraint.variable_name,
                locked_value=constraint.locked_value * 1.2,  # 20% more lenient
                reason=f"Propagated from {source_lock.scenario_id}"
            )
            target_lock.variable_constraints.append(target_constraint)
```

### 3. Partial Lock Release

Currently all-or-nothing. Future: emergency overrides with accountability:

```python
def emergency_release_lock(
    lock_id: str,
    user_id: str,
    authorization_code: str,
    override_reason: str
) -> bool:
    # Requires multi-party cryptographic authorization
    # Creates permanent audit record
    # Weakens but does not remove lock
```

---

## References

- [HYDRA-50 Architecture Documentation](HYDRA_50_ARCHITECTURE.md)
- [Scenario Engine API Reference](HYDRA_50_API_REFERENCE.md)
- [Planetary Defense Integration](PLANETARY_DEFENSE_MONOLITH.md)
- [Event Sourcing Guide](../docs/guides/event_sourcing.md)

---

## Summary

Irreversibility formalization transforms HYDRA-50 from a simulation engine into a **physics engine for collapse dynamics**. Once a scenario crosses the point of no return:

✅ **Variables locked** - Can't magically recover capacity  
✅ **Recovery events disabled** - Can't deploy known traps  
✅ **Governance capped** - Can't rebuild trust/legitimacy  

This creates **realistic collapse modeling** where:

- Epistemic collapse means verification capacity never fully recovers
- Currency collapse means monetary policy loses effectiveness forever
- Social fracture means cohesion can't be rebuilt to pre-collapse levels
- Infrastructure damage means capacity is permanently reduced

**The physics is the message**: Some things, once broken, stay broken.
