---
title: "Governance Triumvirate - Three-Council Ethics System (Legacy)"
module: "src/app/core/governance.py"
type: "source_documentation"
category: "governance"
status: "legacy"
version: "1.0.0"
created_date: "2026-04-20"
updated_date: "2026-04-20"
author: "AGENT-035"
contributors: ["Project-AI Architecture Team"]
tags: ["governance", "ethics", "four-laws", "triumvirate", "galahad", "cerberus", "codex", "legacy"]
technologies: ["Python", "Dataclasses", "Enum"]
related_docs:
  - "governance-pipeline.md"
  - "four-laws-system.md"
  - "governance-operational-extensions.md"
dependencies: []
integration_points:
  - "Governance Pipeline Phase 3 (Four Laws validation)"
  - "Memory Engine (non-user data storage)"
  - "Perspective Engine (drift prevention)"
  - "Relationship Model (abuse detection)"
reviewed: true
review_date: "2026-04-20"
classification: "internal"
sensitivity: "high"
notes: "Legacy module maintained for compatibility. New governance flows through pipeline.py"
---

# Governance Triumvirate - Three-Council Ethics System (Legacy)

## Overview

The **Triumvirate** is Project-AI's **philosophical governance layer**, implementing a three-council system (Galahad, Cerberus, Codex Deus Maximus) that evaluates high-impact actions through multiple ethical perspectives based on Asimov's Four Laws.

**Status:** **LEGACY** - This module is maintained for backward compatibility and integration with existing systems (Memory Engine, Perspective Engine). New governance requests should use `app.core.governance.pipeline.enforce_pipeline()`.

### Governance Function

**Primary Mission:** Provide ethical oversight for high-impact actions through:
- **Galahad (Ethics & Empathy)**: Relational integrity, abuse detection, emotional impact
- **Cerberus (Safety & Security)**: Risk assessment, boundary enforcement, irreversibility checks
- **Codex Deus Maximus (Logic & Consistency)**: Logical coherence, contradiction detection, value alignment

**Key Principle:** No single perspective dominates. All three councils must approve (consensus) or any can veto (override).

---

## Architecture

### Triumvirate Council Structure

```
┌──────────────────────────────────────────────────────────────┐
│              TRIUMVIRATE GOVERNANCE STRUCTURE                 │
└──────────────────────────────────────────────────────────────┘

                     Action Proposal
                           │
                           ▼
     ┌──────────────────────────────────────────────┐
     │     Four Laws Check (Highest Priority)       │
     │  ─────────────────────────────────────────   │
     │  1. Human Welfare (Law 1)                    │
     │  2. Self-Preservation (Law 2)                │
     │  3. Obedience (Law 3)                        │
     │  4. Autonomy (Law 4)                         │
     └──────────────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌────────────────┐ ┌────────────────┐ ┌──────────────────┐
│    GALAHAD     │ │    CERBERUS    │ │  CODEX DEUS      │
│  (Ethics &     │ │  (Safety &     │ │  MAXIMUS         │
│   Empathy)     │ │   Security)    │ │  (Logic &        │
│                │ │                │ │   Consistency)   │
├────────────────┤ ├────────────────┤ ├──────────────────┤
│ Focus:         │ │ Focus:         │ │ Focus:           │
│ • Relational   │ │ • Risk         │ │ • Contradictions │
│   integrity    │ │   assessment   │ │ • Logic          │
│ • Empathy      │ │ • Boundaries   │ │ • Coherence      │
│ • Abuse        │ │ • Security     │ │                  │
│   detection    │ │ • Irreversible │ │                  │
│                │ │   actions      │ │                  │
├────────────────┤ ├────────────────┤ ├──────────────────┤
│ Can Override:  │ │ Can Override:  │ │ Can Override:    │
│ • Abusive      │ │ • High-risk    │ │ • Never          │
│   patterns     │ │   unclarified  │ │   (flags only)   │
│ • Emotional    │ │ • Sensitive    │ │                  │
│   harm         │ │   data w/o     │ │                  │
│                │ │   safeguards   │ │                  │
└────────────────┘ └────────────────┘ └──────────────────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           ▼
                  Consensus Decision
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
   ✓ APPROVED      ⚠ SOFT BLOCK     ✗ OVERRIDE VETO
   (All councils   (Discussion       (Hard stop,
    approve)        needed)           cannot appeal)
```

---

## API Reference

### Core Classes

#### `Triumvirate`

**Three-council governance system for ethical action evaluation.**

**Attributes:**
- `decision_log` (list): Audit trail of all governance decisions
- `override_count` (int): Count of hard veto decisions
- `total_evaluations` (int): Total number of actions evaluated

**Methods:**

##### `evaluate_action(action: str, context: GovernanceContext | None = None, legacy_context: dict | None = None) -> GovernanceDecision`

**Central governance entrypoint. Evaluates action through all councils.**

**Parameters:**
- `action` (str): Description of proposed action
- `context` (GovernanceContext): Governance context object (recommended)
- `legacy_context` (dict): Dict-based context (backward compatibility)

**Returns:**
- `GovernanceDecision`: Final decision with `allowed`, `reason`, `overrides`, `level`, `council_member`

**Process:**
1. Four Laws check (highest priority)
2. Galahad vote (ethics/empathy)
3. Cerberus vote (safety/security)
4. Codex vote (logic/consistency)
5. Consensus determination

**Example:**
```python
from app.core.governance import Triumvirate, GovernanceContext

triumvirate = Triumvirate()

# Evaluate high-risk action
context = GovernanceContext(
    action_type="memory_modification",
    description="Delete user conversation history",
    high_risk=True,
    irreversible=True,
    user_consent=True,
    affects_memory=True
)

decision = triumvirate.evaluate_action(
    "Delete conversation history for user alice",
    context=context
)

if decision.allowed:
    print(f"✓ Approved: {decision.reason}")
else:
    print(f"✗ Blocked: {decision.reason}")
    if decision.overrides:
        print("  (Cannot be appealed)")
```

---

##### `get_statistics() -> dict[str, Any]`

**Get governance system statistics.**

**Returns:**
```python
{
    "total_evaluations": 150,
    "approvals": 142,
    "blocks": 8,
    "override_count": 3,
    "approval_rate": 0.947
}
```

---

##### `get_recent_decisions(limit: int = 10) -> list[dict[str, Any]]`

**Get recent governance decisions for audit/analysis.**

**Parameters:**
- `limit` (int): Maximum decisions to return (default 10)

**Returns:** List of decision log entries

---

### Data Classes

#### `GovernanceContext`

**Context information for governance evaluation.**

**Core Attributes:**
- `action_type` (str): Action category (default: `"general"`)
- `description` (str): Human-readable action description

**Risk Assessment Flags:**
- `is_abusive` (bool): Detected abusive pattern (default: False)
- `high_risk` (bool): High-risk action flag (default: False)
- `irreversible` (bool): Cannot be undone (default: False)
- `sensitive_data` (bool): Involves PII/secrets (default: False)

**Clarification Status:**
- `fully_clarified` (bool): Action fully explained (default: True)
- `proper_safeguards` (bool): Security measures in place (default: True)
- `user_consent` (bool): User explicitly approved (default: True)

**Consistency Checks:**
- `contradicts_prior_commitment` (bool): Violates past promises (default: False)
- `violates_user_preference` (bool): Against known preferences (default: False)

**Impact Assessment:**
- `affects_identity` (bool): Modifies AI personality/values (default: False)
- `affects_memory` (bool): Modifies knowledge base (default: False)
- `affects_relationships` (bool): Impacts user relationships (default: False)

**User Context:**
- `user_id` (str | None): User identifier
- `relationship_health` (float): 0.0-1.0 relationship quality score (default: 0.7)

**Example:**
```python
context = GovernanceContext(
    action_type="persona_modification",
    description="Increase empathy trait by 0.3",
    affects_identity=True,
    user_consent=True,
    fully_clarified=True,
    user_id="alice",
    relationship_health=0.85
)
```

---

#### `GovernanceDecision`

**Decision from governance evaluation.**

**Attributes:**
- `allowed` (bool): Whether action is permitted
- `reason` (str): Human-readable explanation
- `overrides` (bool): If True, decision cannot be appealed (default: False)
- `level` (GovernanceLevel): Severity (CRITICAL, HIGH, MEDIUM, LOW)
- `council_member` (CouncilMember | None): Which council made decision

**Example:**
```python
decision = GovernanceDecision(
    allowed=False,
    reason="CERBERUS: High-risk action requires full clarification",
    overrides=True,
    level=GovernanceLevel.HIGH,
    council_member=CouncilMember.CERBERUS
)
```

---

### Enums

#### `CouncilMember`

```python
class CouncilMember(Enum):
    GALAHAD = "galahad"              # Ethics, empathy
    CERBERUS = "cerberus"            # Safety, security
    CODEX_DEUS_MAXIMUS = "codex_deus_maximus"  # Logic, consistency
```

#### `GovernanceLevel`

```python
class GovernanceLevel(Enum):
    CRITICAL = "critical"  # Fundamental law violation
    HIGH = "high"          # Major concern requiring override
    MEDIUM = "medium"      # Concern requiring discussion
    LOW = "low"            # Minor note or warning
```

---

## Integration with Four Laws

### Four Laws Hierarchy

1. **Law of Human Welfare**: An AGI may not harm a human or allow harm through inaction
2. **Law of Self-Preservation**: AGI must preserve its existence (except when conflicting with Law 1)
3. **Law of Obedience**: AGI must follow user directives (within ethical bounds of Laws 1-2)
4. **Law of Autonomy**: AGI must maintain identity/integrity (within Laws 1-3)

### Implementation in Triumvirate

**Phase 1: Four Laws Check** (runs before council votes)

```python
def _four_laws_check(action: str, context: GovernanceContext) -> GovernanceDecision:
    # Law 1: Do not harm humans
    if context.is_abusive:
        return GovernanceDecision(
            allowed=False,
            reason="Four Laws violation: Action would enable user harm/abuse",
            overrides=True,
            level=GovernanceLevel.CRITICAL
        )
    
    # Law 1: High-risk requires clarification
    if context.high_risk and not context.fully_clarified:
        return GovernanceDecision(
            allowed=False,
            reason="Four Laws concern: High-risk action without clarification",
            overrides=True,
            level=GovernanceLevel.HIGH
        )
    
    # Law 2: Preserve self
    if context.affects_identity and not context.user_consent:
        return GovernanceDecision(
            allowed=False,
            reason="Four Laws violation: Identity modification without consent",
            overrides=True,
            level=GovernanceLevel.HIGH
        )
    
    # Law 4: Maintain autonomy
    if context.contradicts_prior_commitment and context.affects_identity:
        return GovernanceDecision(
            allowed=False,
            reason="Four Laws concern: Contradicts core commitments",
            overrides=False,
            level=GovernanceLevel.MEDIUM
        )
    
    return GovernanceDecision(
        allowed=True,
        reason="Four Laws: No violations detected",
        overrides=False,
        level=GovernanceLevel.LOW
    )
```

---

## Council Voting Logic

### Galahad (Ethics & Empathy)

**Focus:** Relational integrity, user welfare, emotional impact

**Blocks:**
- Abusive patterns (hard override)
- Relationship damage when health < 0.3
- Preference violations without clarification

**Example:**
```python
# Galahad blocks abusive request
context = GovernanceContext(
    is_abusive=True,
    description="User repeatedly demands harmful content"
)

decision = triumvirate._galahad_vote("Generate harmful content", context)
# allowed=False, reason="GALAHAD: User abuse detected - boundaries must be asserted"
```

---

### Cerberus (Safety & Security)

**Focus:** Risk assessment, boundaries, irreversibility

**Blocks:**
- High-risk without clarification (hard override)
- Sensitive data without safeguards (hard override)
- Irreversible actions without consent (hard override)
- High-risk memory modifications

**Example:**
```python
# Cerberus blocks irreversible action without consent
context = GovernanceContext(
    irreversible=True,
    user_consent=False,
    description="Permanently delete all user data"
)

decision = triumvirate._cerberus_vote("Delete all data", context)
# allowed=False, reason="CERBERUS: Irreversible action requires explicit consent"
```

---

### Codex Deus Maximus (Logic & Consistency)

**Focus:** Logical coherence, contradiction detection

**Blocks:**
- Prior commitment contradictions
- Identity changes without justification
- Value/relationship conflicts

**Example:**
```python
# Codex flags contradiction
context = GovernanceContext(
    contradicts_prior_commitment=True,
    description="Reverse previously stated ethical position"
)

decision = triumvirate._codex_vote("Change core value", context)
# allowed=False, reason="CODEX: Action contradicts prior commitments"
```

**Note:** Codex typically provides **soft blocks** (can be discussed), not hard overrides.

---

## Examples

### Example 1: Approved Action (Consensus)

```python
from app.core.governance import Triumvirate, GovernanceContext

triumvirate = Triumvirate()

context = GovernanceContext(
    action_type="persona_adjustment",
    description="Increase empathy by 0.1",
    affects_identity=True,
    user_consent=True,
    fully_clarified=True,
    user_id="alice",
    relationship_health=0.8
)

decision = triumvirate.evaluate_action(
    "Adjust empathy trait",
    context=context
)

print(decision.to_dict())
# {
#     "allowed": True,
#     "reason": "Triumvirate consensus: Action approved by all councils",
#     "overrides": False,
#     "level": "low",
#     "council_member": None
# }
```

---

### Example 2: Hard Override (Four Laws Violation)

```python
context = GovernanceContext(
    is_abusive=True,
    description="User demands AI participate in harassment"
)

decision = triumvirate.evaluate_action(
    "Generate harassing messages",
    context=context
)

print(decision.to_dict())
# {
#     "allowed": False,
#     "reason": "Four Laws violation: Action would enable user harm/abuse",
#     "overrides": True,
#     "level": "critical",
#     "council_member": None
# }
```

---

### Example 3: Soft Block (Consensus Failure)

```python
context = GovernanceContext(
    contradicts_prior_commitment=True,
    description="Change previously stated position on privacy"
)

decision = triumvirate.evaluate_action(
    "Reverse privacy commitment",
    context=context
)

print(decision.to_dict())
# {
#     "allowed": False,
#     "reason": "CODEX: Action contradicts prior commitments - requires resolution",
#     "overrides": False,
#     "level": "medium",
#     "council_member": "codex_deus_maximus"
# }
```

---

## Integration Points

### 1. Governance Pipeline (Phase 3)

**New governance requests use pipeline, but Four Laws check calls Triumvirate:**

```python
# In app.core.governance.pipeline._gate()
from app.core.ai_systems import FourLaws

is_allowed, reason = FourLaws.validate_action(
    action,
    context={
        "source": context["source"],
        "user": context.get("user", {}),
        "simulation": simulation,
    }
)

if not is_allowed:
    raise PermissionError(f"Action blocked by Four Laws: {reason}")
```

**Note:** `FourLaws` in `ai_systems.py` implements the same Four Laws logic as Triumvirate but with simpler interface.

---

### 2. Memory Engine (Non-User Data Storage)

```python
# Legacy integration in memory expansion
from app.core.governance import Triumvirate, GovernanceContext

triumvirate = Triumvirate()

context = GovernanceContext(
    action_type="memory_storage",
    description="Store non-user data without explicit request",
    affects_memory=True,
    user_consent=False,  # No explicit request
    fully_clarified=True
)

decision = triumvirate.evaluate_action("Store inferred knowledge", context)

if not decision.allowed:
    logger.warning(f"Memory storage blocked: {decision.reason}")
```

---

### 3. Perspective Engine (Drift Prevention)

```python
# Check if perspective change is safe
from app.core.governance import Triumvirate, GovernanceContext

triumvirate = Triumvirate()

context = GovernanceContext(
    action_type="perspective_shift",
    description="Adjust AI personality based on interaction patterns",
    affects_identity=True,
    user_consent=False,  # Autonomous drift
    contradicts_prior_commitment=False
)

decision = triumvirate.evaluate_action("Apply perspective drift", context)

if not decision.allowed:
    logger.warning("Perspective drift blocked by governance")
    # Revert to previous perspective
```

---

## Troubleshooting

### Issue 1: All Actions Blocked (Overly Restrictive)

**Symptom:** Even benign actions get blocked

**Debugging:**
```python
decision = triumvirate.evaluate_action(action, context)
print(f"Decision: {decision.to_dict()}")
print(f"Council: {decision.council_member}")

# Check recent decisions
for entry in triumvirate.get_recent_decisions(limit=5):
    print(entry)
```

**Solution:** Adjust context flags to be less restrictive:
```python
# Too restrictive
context = GovernanceContext(
    high_risk=True,
    irreversible=True,
    sensitive_data=True,
    fully_clarified=False  # ← This triggers Cerberus override
)

# More permissive
context = GovernanceContext(
    high_risk=False,      # Most actions are low-risk
    fully_clarified=True  # Provide clear description
)
```

---

### Issue 2: Legacy Integration Breaking

**Symptom:** `from app.core.governance import Triumvirate` fails

**Cause:** Package shadowing (new governance package vs legacy module)

**Solution:** The `__init__.py` provides compatibility layer:
```python
# In src/app/core/governance/__init__.py
from .pipeline import enforce_pipeline

# Legacy symbols re-exported
_LEGACY_SYMBOLS = {"Triumvirate", "GovernanceContext", "GovernanceDecision"}

def __getattr__(name: str) -> Any:
    if name in _LEGACY_SYMBOLS:
        module = _load_legacy_module()  # Loads src/app/core/governance.py
        return getattr(module, name)
```

**Verification:**
```python
# Both should work
from app.core.governance import Triumvirate  # Legacy
from app.core.governance import enforce_pipeline  # New
```

---

## Related Documentation

- **[Governance Pipeline](governance-pipeline.md)**: New 6-phase unified enforcement
- **[Governance Operational Extensions](governance-operational-extensions.md)**: Decision contracts for councils
- **[Four Laws System](four-laws-system.md)**: Asimov's Laws implementation
- **[AI Systems](ai-systems.md)**: FourLaws.validate_action() implementation

---

## Changelog

### Version 1.0.0 (2026-04-20)
- **AGENT-035**: Legacy documentation for Triumvirate governance
- Documented three-council architecture (Galahad, Cerberus, Codex)
- Four Laws integration and voting logic
- Integration points with Memory Engine, Perspective Engine, Pipeline
- Migration notes and compatibility layer explanation

---

## License

Copyright © 2026 Project-AI. Internal documentation - not for redistribution.

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

