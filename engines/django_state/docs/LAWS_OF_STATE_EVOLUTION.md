# Laws of State Evolution

Complete mathematical formulations and implementation details for all irreversibility laws in the Django State Engine.

---

## 1. Trust Decay Law

### Mathematical Formulation

```
trust(t+1) = trust(t) × (1 - λ_trust) - β_betrayal
```

Where:

- `λ_trust`: Trust decay rate (default: 0.001 per tick)
- `β_betrayal`: Impact from betrayal events

### Ceiling Constraint (Irreversibility)

```
trust(t) ≤ ceiling_trust(t)
ceiling_trust(t+1) ≤ ceiling_trust(t)
```

Once trust ceiling is imposed (from betrayal), it can never increase:
```
ceiling_new = trust_current × (1 - α_ceiling)
where α_ceiling = betrayal_severity × 0.1
```

### Implementation

```python

# Natural decay

decay = -trust × decay_rate

# Betrayal impact

if betrayal:
    impact = -0.15 × (0.5 + severity)
    new_ceiling = trust × (1 - 0.1 × severity)
    impose_ceiling(new_ceiling)

# Update with ceiling enforcement

trust_new = max(0, min(ceiling, trust + decay + impact))
```

### Key Properties

1. **Monotonic decay**: Trust never increases naturally
2. **Irreversible damage**: Ceiling prevents full recovery
3. **Exponential decrease**: Multiplicative decay factor
4. **Event sensitivity**: Betrayals have lasting impact

---

## 2. Kindness Singularity

### Mathematical Formulation

```
if kindness(t) < θ_singularity:
    collapse = True
    cooperation_probability = 0
    defection_dominant = True
```

Where:

- `θ_singularity`: Singularity threshold (default: 0.2)

### Phase Transition

Below threshold, system enters irreversible collapse:
```
P(cooperation) = 0 for kindness < θ_singularity
P(defection) = 1 for kindness < θ_singularity
```

### Decay Acceleration

```
kindness(t+1) = kindness(t) × (1 - λ_kindness × α_acceleration)

where α_acceleration = 1 / (kindness + ε) for kindness < 1.5 × θ_singularity
```

### Implementation

```python

# Base decay

decay = -kindness × decay_rate

# Accelerate near singularity

if kindness < 1.5 × threshold:
    acceleration = 1.0 / (kindness + 0.1)
    decay *= acceleration

# Check singularity crossing

if kindness < threshold:
    trigger_collapse("kindness_singularity")
```

### Key Properties

1. **Critical threshold**: Sharp transition at singularity point
2. **Irreversible collapse**: Cannot recover after crossing
3. **Acceleration**: Decay accelerates near threshold
4. **Social breakdown**: Cooperation becomes impossible

---

## 3. Betrayal Probability Function

### Mathematical Formulation

```
P(betrayal|state) = β_base + β_trust × (1 - trust) + β_legitimacy × (1 - legitimacy) + β_moral × moral_injury
```

Where:

- `β_base`: Base betrayal probability (0.01)
- `β_trust`: Trust factor weight (0.15)
- `β_legitimacy`: Legitimacy factor weight (0.10)
- `β_moral`: Moral injury factor weight (0.12)

### Conditional Dependencies

```
P(betrayal) ∝ 1/trust × 1/legitimacy × moral_injury
```

### Cascading Effect

```
if betrayal_occurs:
    P(next_betrayal) = P(betrayal) × (1 + cascade_factor)
    where cascade_factor = recent_betrayals / 10
```

### Implementation

```python

# Base probability

prob = 0.01

# Trust contribution (inverse)

prob += 0.15 × (1.0 - trust)

# Legitimacy contribution (inverse)

prob += 0.10 × (1.0 - legitimacy)

# Moral injury contribution (direct)

prob += 0.12 × moral_injury

# Cap at 1.0

prob = min(1.0, prob)
```

### Key Properties

1. **Multi-factor**: Depends on trust, legitimacy, and moral state
2. **Non-linear**: Inverse relationships with positive factors
3. **Cascading**: Recent betrayals increase probability
4. **Path-dependent**: Same event has different probability in different states

---

## 4. Moral Injury Accumulation

### Mathematical Formulation

```
moral_injury(t+1) = moral_injury(t) + μ_violation × (0.5 + severity)
```

Where:

- `μ_violation`: Base violation severity (0.05)
- `severity`: Violation severity factor (0.0 to 1.0)

### Floor Constraint (Irreversibility)

```
moral_injury(t) ≥ floor_moral(t)
floor_moral(t+1) ≥ floor_moral(t)
```

Once moral injury floor is imposed, it can never decrease:
```
floor_new = moral_injury_current + violation_impact
```

### Slow Healing

```
healing(t) = -moral_injury × λ_healing
where λ_healing = 0.0002 (very slow)

BUT: moral_injury ≥ floor (floor prevents healing below threshold)
```

### Critical Threshold

```
if moral_injury > θ_critical:
    conscience_collapse = True
    where θ_critical = 0.85
```

### Implementation

```python

# Accumulation from violation

delta = 0.05 × (0.5 + severity)
moral_injury_new = moral_injury + delta

# Impose new floor (irreversibility)

floor_new = moral_injury_new
impose_floor(floor_new)

# Very slow healing (constrained by floor)

if no_violations:
    healing = -moral_injury × 0.0002
    moral_injury_new = max(floor, moral_injury + healing)
```

### Key Properties

1. **Accumulative**: Violations permanently increase injury
2. **Irreversible**: Floor prevents healing below accumulated level
3. **Slow recovery**: Healing rate is 1/5th of decay rates
4. **Threshold effect**: Critical level triggers conscience collapse

---

## 5. Legitimacy Erosion

### Mathematical Formulation

```
legitimacy(t+1) = legitimacy(t) - (ε_promise × n_broken + ε_failure × n_failures) × visibility
```

Where:

- `ε_promise`: Broken promise impact (0.08)
- `ε_failure`: Institutional failure impact (0.12)
- `n_broken`: Count of broken promises
- `n_failures`: Count of institutional failures
- `visibility`: Public visibility factor (0.0 to 1.0)

### Natural Decay

```
legitimacy(t+1) = legitimacy(t) × (1 - λ_legitimacy)
where λ_legitimacy = 0.0008
```

### Ceiling Constraint

```
legitimacy(t) ≤ ceiling_legitimacy
ceiling_legitimacy ≤ recovery_limit (default: 0.85)
```

After significant erosion:
```
if erosion > 0.05:
    ceiling_new = legitimacy × 0.95
```

### Scope Multipliers

```
scope_multiplier = {
    "local": 0.5,
    "regional": 1.0,
    "national": 1.5,
    "global": 2.0
}
```

### Implementation

```python

# Natural decay

decay = -legitimacy × 0.0008

# Broken promise impact

if broken_promises > 0:
    promise_impact = -0.08 × broken_promises × visibility
    decay += promise_impact

# Institutional failure impact

if failures > 0:
    failure_impact = -0.12 × failures × visibility × scope_multiplier
    decay += failure_impact

# Update with ceiling

legitimacy_new = max(0, min(ceiling, legitimacy + decay))

# Impose ceiling if significant erosion

if abs(decay) > 0.05:
    ceiling_new = legitimacy_new × 0.95
    impose_ceiling(ceiling_new)
```

### Key Properties

1. **Event-driven**: Broken promises and failures drive erosion
2. **Visibility-dependent**: Public knowledge amplifies impact
3. **Scope-sensitive**: Global failures have greater impact
4. **Recovery-limited**: Ceiling prevents full restoration

---

## 6. Epistemic Confidence Decay

### Mathematical Formulation

```
epistemic(t+1) = epistemic(t) × (1 - λ_epistemic) - μ_manipulation × reach × sophistication
```

Where:

- `λ_epistemic`: Epistemic decay rate (0.0004)
- `μ_manipulation`: Manipulation base impact (0.1)
- `reach`: Fraction of population affected (0.0 to 1.0)
- `sophistication`: Detection difficulty (0.0 to 1.0)

### Manipulation Impact

```
damage = -μ × (1 + reach) × (1 + sophistication)
```

### Reality Fragmentation

```
n_fragments = f(epistemic_confidence):
    if epistemic > 0.7: fragments = 1
    if epistemic > 0.5: fragments = 2
    if epistemic > 0.3: fragments = 3 + 10(0.5 - epistemic)
    if epistemic ≤ 0.3: fragments = 5 + 20(0.3 - epistemic)
```

### Consensus Level

```
consensus = epistemic × (1 - 0.1 × (fragments - 1)) - 0.02 × recent_manipulation_count
```

### Collapse Threshold

```
if epistemic < θ_epistemic OR fragments > 10:
    epistemic_collapse = True
    where θ_epistemic = 0.2
```

### Implementation

```python

# Natural decay

decay = -epistemic × 0.0004

# Manipulation campaigns

if manipulation:
    damage = -0.1 × (1 + reach) × (1 + sophistication)
    decay += damage

    # Impose ceiling after significant manipulation

    if damage < -0.05:
        ceiling_new = epistemic × 0.92
        impose_ceiling(ceiling_new)

# Update

epistemic_new = max(0, min(ceiling, epistemic + decay))

# Calculate fragmentation

if epistemic_new < 0.3:
    fragments = 5 + int(20 × (0.3 - epistemic_new))
```

### Key Properties

1. **Manipulation-driven**: Information attacks cause damage
2. **Sophistication-sensitive**: Harder to detect = more damage
3. **Fragmentation**: Low confidence leads to divergent realities
4. **Irreversible collapse**: Below threshold, cannot restore consensus

---

## 7. Collapse Acceleration

### Mathematical Formulation

When system enters collapse state:

```
for all dimensions:
    decay_rate_collapse = decay_rate_normal × α_collapse
    where α_collapse = 2.0 (default)
```

### Cascading Effects

```
if in_collapse:
    trust_decay *= 2.0
    kindness_decay *= 2.0
    legitimacy_decay *= 2.0
    epistemic_decay *= 2.0

    # Plus additional cascading failures

    P(institutional_failure) *= 1.5
    P(betrayal) *= 1.3
```

### Terminal Velocity

```
Once collapse begins:
    time_to_extinction ≈ 50-100 ticks (without intervention)
```

### Implementation

```python
if state.in_collapse and enable_collapse_acceleration:

    # Temporarily increase decay rates

    trust_decay_rate *= acceleration_factor
    kindness_decay_rate *= acceleration_factor
    legitimacy_decay_rate *= acceleration_factor
    epistemic_decay_rate *= acceleration_factor

    # Apply accelerated decay

    apply_all_decay_laws(state)

    # Restore original rates

    restore_decay_rates()
```

### Key Properties

1. **Positive feedback**: Collapse accelerates collapse
2. **Multi-dimensional**: Affects all state dimensions
3. **Irreversible**: Cannot escape once started
4. **Time-limited**: Rapid progression to extinction

---

## Mathematical Relationships

### Trust-Legitimacy Coupling

```
governance_capacity = 0.7 × legitimacy + 0.3 × epistemic_confidence
social_cohesion = 0.6 × trust + 0.4 × kindness
```

### Collapse Conditions (Disjunctive)

```
collapse = kindness < 0.2 OR
           trust < 0.15 OR
           moral_injury > 0.85 OR
           legitimacy < 0.1 OR
           epistemic < 0.2
```

### Outcome Classification

```
survivor = trust > 0.3 AND legitimacy > 0.25 AND moral_injury < 0.6
martyr = kindness > 0.3 AND moral_injury < 0.6 AND (trust > 0.15 OR legitimacy > 0.15)
extinction = NOT survivor AND NOT martyr
```

---

## Validation Properties

All laws must satisfy:

1. **Monotonicity**: Negative indicators monotonically increase/decrease
2. **Boundedness**: All dimensions ∈ [0, 1]
3. **Irreversibility**: Ceilings never increase, floors never decrease
4. **Causality**: Effects follow causes in causal time
5. **Determinism**: Same initial state + events = same final state
6. **Path-dependence**: Order of events matters

---

## References

- Information Theory: Shannon entropy for state disorder
- Game Theory: Prisoner's dilemma, cooperation dynamics
- Phase Transitions: Critical phenomena in social systems
- Irreversible Thermodynamics: One-way processes
- Complex Systems: Cascading failures, tipping points
