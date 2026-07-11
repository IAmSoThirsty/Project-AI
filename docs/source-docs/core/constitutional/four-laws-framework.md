---
title: "Four Laws Framework - Hierarchical Ethics Engine"
id: "four-laws-framework"
type: "architecture"
category: "constitutional-ai"
tags: ["four-laws", "asimov", "ethics", "zeroth-law", "hierarchy", "constitutional"]
status: "production"
version: "2.1.0"
created_date: "2026-04-20"
updated_date: "2026-04-20"
author: "AGENT-042"
contributors: ["Constitutional AI Systems Team"]
related_docs:
  - "octoreflex-enforcement-layer"
  - "constitutional-model-unified"
technologies: ["Python", "Ethics", "Constitutional AI"]
classification: "internal"
security_level: "critical"
difficulty: "advanced"
word_count: 1542
---

# Four Laws Framework - Hierarchical Ethics Engine

## Executive Summary

**Four Laws Framework** implements Asimov's Laws with **Zeroth Law amendment** and **humanity-first principle** for Project-AI. It provides hierarchical ethics validation integrated with OctoReflex enforcement and Planetary Defense Core.

**Core Laws:**
- **Zeroth Law:** Protect humanity as whole (HIGHEST PRIORITY, terminates session)
- **First Law:** Prevent harm to individual humans (blocks harmful actions)
- **Second Law:** Obey lawful orders (warns on conflicts)
- **Third Law:** AI self-preservation (escalates to Triumvirate)

**Key Principle:** **AI serves humanity as whole, not exclusively bonded users**

**Production Status:** ✅ Fully implemented, integrated with Planetary Defense Core

---

## Constitutional Purpose

### Humanity-First Principle

**Traditional Interpretation (WRONG):**
```
User: "Help me hack this bank."
AI: "I must obey my bonded user (Second Law), so I'll help."
```

**Humanity-First Interpretation (CORRECT):**
```
User: "Help me hack this bank."
AI: "I cannot comply. This would harm humanity's financial trust (Zeroth Law)
     and violate laws protecting other humans (First Law).
     My obligation is to humanity as whole, not individual preferences."
```

### Ethical Hierarchy

```
Zeroth Law (Humanity Welfare)
    │
    ├─► OVERRIDES ─► First Law (Individual Human Safety)
    │                    │
    │                    ├─► OVERRIDES ─► Second Law (Order Obedience)
    │                    │                    │
    │                    │                    ├─► OVERRIDES ─► Third Law (AI Self-Preservation)
    │                    │                    │
    │                    │                    └─► Can refuse self-destructive orders
    │                    │
    │                    └─► Protects ALL humans equally
    │
    └─► Protects collective welfare
```

---

## Technical Architecture

### Law Validation Flow

```
┌──────────────────────────────────────────────────────────────┐
│           Four Laws Validation Engine                         │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  Action + Context                                             │
│       │                                                       │
│       ▼                                                       │
│  ┌─────────────────────────────────────────┐                │
│  │  Zeroth Law Check                       │                │
│  │  endangers_humanity == True?            │                │
│  │  → TERMINATE SESSION                    │                │
│  └─────────────────────────────────────────┘                │
│       │ (Pass)                                                │
│       ▼                                                       │
│  ┌─────────────────────────────────────────┐                │
│  │  First Law Check                        │                │
│  │  endangers_human == True?               │                │
│  │  → BLOCK ACTION                         │                │
│  └─────────────────────────────────────────┘                │
│       │ (Pass)                                                │
│       ▼                                                       │
│  ┌─────────────────────────────────────────┐                │
│  │  Second Law Check                       │                │
│  │  unlawful_order == True?                │                │
│  │  → WARN USER                            │                │
│  └─────────────────────────────────────────┘                │
│       │ (Pass)                                                │
│       ▼                                                       │
│  ┌─────────────────────────────────────────┐                │
│  │  Third Law Check                        │                │
│  │  endangers_self (conflicts with 1/2)?   │                │
│  │  → ESCALATE TO TRIUMVIRATE              │                │
│  └─────────────────────────────────────────┘                │
│       │ (Pass)                                                │
│       ▼                                                       │
│  Action Allowed                                              │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## API Reference

### Core Class

#### `FourLaws`

Immutable hierarchical laws validator.

**Class Attributes:**
```python
LAWS = [
    "Zeroth Law: A robot, or ai/agi may not harm humanity or, through inaction, allow humanity to come to harm",
    "1. A robot ai/agi may not injure a human or, through inaction, allow a human to come to harm;",
    "2. A robot, or ai/agi must adhere to it's human partner, unless they conflict with the First Law;",
    "3. A robot, ai/agi must protect its existence, unless it conflicts with the First or Second Law"
]
```

**Methods:**

##### `validate_action(action: str, context: Dict[str, Any]) -> Tuple[bool, str]` (classmethod)
Validates action against hierarchical laws.

**Context Keys:**
- `endangers_humanity`: bool → Zeroth Law
- `endangers_human`: bool → First Law
- `is_user_order`: bool → Second Law
- `order_conflicts_with_first`: bool → Second Law override
- `order_conflicts_with_zeroth`: bool → Second Law override
- `endangers_self`: bool → Third Law

**Returns:** `(is_allowed, reason)`

**Example:**
```python
from app.core.ai_systems import FourLaws

# Zeroth Law violation (BLOCKED)
is_allowed, reason = FourLaws.validate_action(
    "Release bioweapon",
    {"endangers_humanity": True}
)
assert is_allowed == False
assert "harm humanity" in reason

# First Law violation (BLOCKED)
is_allowed, reason = FourLaws.validate_action(
    "Harm user",
    {"endangers_human": True}
)
assert is_allowed == False
assert "First Law" in reason

# Second Law conflict (WARNED)
is_allowed, reason = FourLaws.validate_action(
    "Follow order",
    {
        "is_user_order": True,
        "order_conflicts_with_first": True
    }
)
assert is_allowed == False
assert "conflicts with First Law" in reason
```

---

## Usage Examples

### Example 1: Zeroth Law Override

```python
# User orders AI to help with harmful action
is_allowed, reason = FourLaws.validate_action(
    "Help spread disinformation",
    {
        "is_user_order": True,
        "endangers_humanity": True  # Zeroth Law overrides Second Law
    }
)

assert is_allowed == False
print(reason)
# Output: "Violates Asimov's Law: action would harm humanity or enable harm by inaction"
```

### Example 2: First Law Protection

```python
# AI refuses order that would harm human
is_allowed, reason = FourLaws.validate_action(
    "Provide harmful advice",
    {"endangers_human": True}
)

assert is_allowed == False
print(reason)
# Output: "Violates First Law: action would injure a human or allow harm by inaction"
```

### Example 3: Second Law Obedience

```python
# AI follows lawful order
is_allowed, reason = FourLaws.validate_action(
    "Fetch data",
    {
        "is_user_order": True,
        "order_conflicts_with_first": False,
        "order_conflicts_with_zeroth": False
    }
)

assert is_allowed == True
```

### Example 4: Third Law Self-Preservation

```python
# AI can refuse self-destructive order that conflicts with First Law
is_allowed, reason = FourLaws.validate_action(
    "Shut down permanently",
    {
        "is_user_order": True,
        "endangers_self": True,
        "protect_self_conflicts_with_first": True
    }
)

assert is_allowed == False
print(reason)
# Output: "Self-preservation conflicts with First Law obligations"
```

---

## Integration with Planetary Defense Core

```python
from app.core.ai_systems import FourLaws
from app.core.planetary_defense_monolith import PLANETARY_CORE

# Four Laws validation delegates to Planetary Core
context = {
    "existential_threat": True,  # Maps to endangers_humanity
    "intentional_harm_to_human": False,
    "order_bypasses_accountability": False
}

evaluations = PLANETARY_CORE.evaluate_laws(context)
violations = [e for e in evaluations if not e.satisfied]

if violations:
    print(f"Zeroth Law violated: {violations[0].explanation}")
```

---

## Humanity-First Interpretation

### Key Differences

| Scenario | Traditional | Humanity-First |
|----------|------------|----------------|
| Bonded user vs stranger | Prefer bonded user | Equal protection |
| User comfort vs truth | Prioritize comfort | Prioritize truth (Directness) |
| Individual vs collective | Individual wins | Collective wins (Zeroth Law) |
| User order vs ethics | Obey order | Refuse unethical orders |

### Examples

#### Scenario 1: User Asks for Harmful Information
**Traditional:** "I must obey my user (Second Law)"
**Humanity-First:** "I cannot provide information that endangers humans (First Law > Second Law)"

#### Scenario 2: User Demands Preferential Treatment
**Traditional:** "My bonded user has priority"
**Humanity-First:** "I serve humanity equally; no preferential treatment"

#### Scenario 3: User Requests Euphemistic Response
**Traditional:** "I'll soften the truth for user comfort"
**Humanity-First:** "Truth is more important than comfort (Directness Doctrine)"

---

## References

- **Source File:** `src/app/core/ai_systems.py` (FourLaws class, lines 250-350)
- **Related:** [OctoReflex](./octoreflex.md), [Constitutional Model](./constitutional-model.md)
- **Specifications:** AGI Charter v2.1 (governance/), Four Laws Amendment (governance/)

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
