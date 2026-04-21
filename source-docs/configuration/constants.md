# Constants Module

**Module**: `config/constants.py`  
**Purpose**: System-wide constants for governance, TARL, and API  
**Classification**: Core Constants  
**Priority**: P0 - Core System

---

## Overview

The Constants module provides immutable system-wide constants organized into classes for actor types, action types, verdict types, pillars, risk levels, HTTP status codes, API endpoints, and system messages. It ensures consistent values across the Project-AI system.

### Key Characteristics

- **Organization**: Class-based constant grouping
- **Immutability**: Read-only constants
- **Coverage**: Governance, TARL, API, messaging
- **Introspection**: `.all()` methods for iteration

---

## Constant Classes

### Actor Types

```python
class ActorType:
    HUMAN = "human"
    AGENT = "agent"
    SYSTEM = "system"
    
    @classmethod
    def all(cls):
        return [cls.HUMAN, cls.AGENT, cls.SYSTEM]
```

**Purpose**: Identify who initiates actions in the system

**Values**:
- `HUMAN`: Human user actions
- `AGENT`: AI agent actions
- `SYSTEM`: Automated system actions

**Usage**:
```python
from config.constants import ActorType

if actor == ActorType.HUMAN:
    # Human-initiated action
    require_confirmation()
```

### Action Types

```python
class ActionType:
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    MUTATE = "mutate"
    
    @classmethod
    def all(cls):
        return [cls.READ, cls.WRITE, cls.EXECUTE, cls.MUTATE]
```

**Purpose**: Classify action types for permission checking

**Values**:
- `READ`: Read-only operations
- `WRITE`: Data modification
- `EXECUTE`: Command execution
- `MUTATE`: State mutation

**Usage**:
```python
from config.constants import ActionType

def check_permission(action_type: str, actor: str):
    if action_type == ActionType.EXECUTE:
        # Execute requires elevated permissions
        return actor == ActorType.HUMAN
```

### Verdict Types

```python
class VerdictType:
    ALLOW = "allow"
    DENY = "deny"
    DEGRADE = "degrade"
    
    @classmethod
    def all(cls):
        return [cls.ALLOW, cls.DENY, cls.DEGRADE]
```

**Purpose**: Governance decision outcomes

**Values**:
- `ALLOW`: Action permitted
- `DENY`: Action forbidden
- `DEGRADE`: Action permitted with limitations

**Usage**:
```python
from config.constants import VerdictType

verdict = governance.evaluate(action)
if verdict == VerdictType.DENY:
    raise PermissionError("Governance denied action")
elif verdict == VerdictType.DEGRADE:
    apply_rate_limit()
```

### Pillar Names

```python
class Pillar:
    GALAHAD = "Galahad"
    CERBERUS = "Cerberus"
    CODEX_DEUS = "CodexDeus"
    
    @classmethod
    def all(cls):
        return [cls.GALAHAD, cls.CERBERUS, cls.CODEX_DEUS]
```

**Purpose**: Three governance pillars of the Triumvirate

**Pillars**:
- `GALAHAD`: Human-centric ethics, safety
- `CERBERUS`: Security, threat detection
- `CODEX_DEUS`: AI autonomy, capability

**Usage**:
```python
from config.constants import Pillar

def route_to_pillar(action):
    if is_security_related(action):
        return Pillar.CERBERUS
    elif is_ethical_concern(action):
        return Pillar.GALAHAD
    else:
        return Pillar.CODEX_DEUS
```

### Risk Levels

```python
class RiskLevel:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
    @classmethod
    def all(cls):
        return [cls.LOW, cls.MEDIUM, cls.HIGH, cls.CRITICAL]
```

**Purpose**: Classify risk severity

**Levels**:
- `LOW`: Minimal risk
- `MEDIUM`: Moderate risk
- `HIGH`: Elevated risk
- `CRITICAL`: Severe risk

**Usage**:
```python
from config.constants import RiskLevel

def assess_risk(action) -> str:
    if involves_data_deletion(action):
        return RiskLevel.CRITICAL
    elif involves_external_api(action):
        return RiskLevel.MEDIUM
    return RiskLevel.LOW
```

### HTTP Status Codes

```python
class HttpStatus:
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500
```

**Purpose**: Standard HTTP response codes

**Usage**:
```python
from config.constants import HttpStatus

@app.route("/api/resource")
def create_resource():
    try:
        result = create()
        return result, HttpStatus.CREATED
    except ValidationError:
        return {"error": "Invalid input"}, HttpStatus.BAD_REQUEST
```

### API Endpoints

```python
class Endpoints:
    HEALTH = "/health"
    TARL = "/tarl"
    AUDIT = "/audit"
    INTENT = "/intent"
    EXECUTE = "/execute"
```

**Purpose**: Standard API endpoint paths

**Usage**:
```python
from config.constants import Endpoints

@app.route(Endpoints.HEALTH)
def health_check():
    return {"status": "healthy"}

@app.route(Endpoints.TARL, methods=["POST"])
def evaluate_tarl():
    return tarl_service.evaluate(request.json)
```

### Messages

```python
class Messages:
    GOVERNANCE_DENIED = "Governance denied this request"
    INTENT_ACCEPTED = "Intent accepted under governance"
    EXECUTION_DENIED = "Execution denied by governance"
    EXECUTION_COMPLETED = "Execution completed under governance"
    NO_TARL_RULE = "No TARL rule – execution denied"
```

**Purpose**: Standardized system messages

**Usage**:
```python
from config.constants import Messages

def execute_action(action):
    verdict = governance.evaluate(action)
    if verdict == VerdictType.DENY:
        return {"error": Messages.GOVERNANCE_DENIED}
    
    result = perform_action(action)
    return {"message": Messages.EXECUTION_COMPLETED, "result": result}
```

---

## Usage Patterns

### Pattern 1: Type Safety with Constants

```python
from config.constants import ActorType, ActionType, VerdictType

def evaluate_action(actor: str, action: str) -> str:
    """Type-safe action evaluation."""
    # Validate inputs
    assert actor in ActorType.all(), f"Invalid actor: {actor}"
    assert action in ActionType.all(), f"Invalid action: {action}"
    
    # Evaluation logic
    if actor == ActorType.SYSTEM and action == ActionType.MUTATE:
        return VerdictType.DENY
    
    return VerdictType.ALLOW
```

### Pattern 2: Pillar Routing

```python
from config.constants import Pillar

class GovernanceRouter:
    def route(self, action):
        pillar = self.determine_pillar(action)
        
        if pillar == Pillar.GALAHAD:
            return self.galahad_engine.evaluate(action)
        elif pillar == Pillar.CERBERUS:
            return self.cerberus_engine.evaluate(action)
        elif pillar == Pillar.CODEX_DEUS:
            return self.codex_engine.evaluate(action)
```

### Pattern 3: Risk-Based Handling

```python
from config.constants import RiskLevel

def handle_action(action, risk_level: str):
    if risk_level == RiskLevel.CRITICAL:
        # Require human approval
        require_approval(action)
    elif risk_level == RiskLevel.HIGH:
        # Require two-factor authentication
        require_2fa()
    elif risk_level == RiskLevel.MEDIUM:
        # Log action
        audit_log(action)
    # LOW risk: proceed normally
```

### Pattern 4: API Response Standardization

```python
from config.constants import HttpStatus, Messages

class APIResponse:
    @staticmethod
    def success(data=None):
        return {"data": data}, HttpStatus.OK
    
    @staticmethod
    def governance_denied():
        return {"error": Messages.GOVERNANCE_DENIED}, HttpStatus.FORBIDDEN
    
    @staticmethod
    def no_tarl_rule():
        return {"error": Messages.NO_TARL_RULE}, HttpStatus.BAD_REQUEST
```

### Pattern 5: Introspection

```python
from config.constants import ActorType, VerdictType

# Get all possible values
all_actors = ActorType.all()
all_verdicts = VerdictType.all()

# Validate against all possible values
def validate_actor(actor: str) -> bool:
    return actor in ActorType.all()

# Generate documentation
def document_types():
    return {
        "actors": ActorType.all(),
        "verdicts": VerdictType.all()
    }
```

---

## Integration Patterns

### Pattern 1: TARL Rule Definition

```python
from config.constants import ActorType, ActionType, VerdictType

tarl_rule = {
    "intent": "delete_data",
    "actor": ActorType.HUMAN,
    "action": ActionType.MUTATE,
    "verdict": VerdictType.ALLOW,
    "conditions": ["requires_confirmation"]
}
```

### Pattern 2: Governance Decision

```python
from config.constants import Pillar, VerdictType, Messages

def triumvirate_decision(action):
    votes = {
        Pillar.GALAHAD: evaluate_galahad(action),
        Pillar.CERBERUS: evaluate_cerberus(action),
        Pillar.CODEX_DEUS: evaluate_codex(action)
    }
    
    # Unanimous ALLOW required
    if all(v == VerdictType.ALLOW for v in votes.values()):
        return VerdictType.ALLOW, Messages.INTENT_ACCEPTED
    
    return VerdictType.DENY, Messages.GOVERNANCE_DENIED
```

### Pattern 3: Audit Logging

```python
from config.constants import ActorType, ActionType, RiskLevel

def audit_action(actor, action_type, risk):
    log_entry = {
        "timestamp": time.time(),
        "actor": actor,
        "actor_type": ActorType.HUMAN if actor.startswith("user_") else ActorType.AGENT,
        "action_type": action_type,
        "risk_level": risk
    }
    audit_log.append(log_entry)
```

---

## Testing

### Unit Testing

```python
import pytest
from config.constants import (
    ActorType, ActionType, VerdictType,
    Pillar, RiskLevel
)

def test_actor_types():
    assert ActorType.HUMAN == "human"
    assert ActorType.AGENT == "agent"
    assert ActorType.SYSTEM == "system"
    
    all_actors = ActorType.all()
    assert len(all_actors) == 3
    assert ActorType.HUMAN in all_actors

def test_verdict_types():
    all_verdicts = VerdictType.all()
    assert len(all_verdicts) == 3
    assert VerdictType.ALLOW in all_verdicts
    assert VerdictType.DENY in all_verdicts
    assert VerdictType.DEGRADE in all_verdicts

def test_pillars():
    all_pillars = Pillar.all()
    assert len(all_pillars) == 3
    assert Pillar.GALAHAD in all_pillars
    assert Pillar.CERBERUS in all_pillars
    assert Pillar.CODEX_DEUS in all_pillars

def test_risk_levels():
    all_risks = RiskLevel.all()
    assert len(all_risks) == 4
    assert RiskLevel.LOW in all_risks
    assert RiskLevel.CRITICAL in all_risks

def test_messages():
    assert Messages.GOVERNANCE_DENIED == "Governance denied this request"
    assert Messages.NO_TARL_RULE == "No TARL rule – execution denied"
```

---

## Best Practices

1. **Use Constants**: Never hardcode string values
2. **Import Specific**: `from config.constants import ActorType` not `import config.constants`
3. **Type Hints**: Use constants in type hints for clarity
4. **Validation**: Use `.all()` for validation
5. **Immutability**: Never reassign constant values
6. **Documentation**: Document constant meanings
7. **Exhaustive Handling**: Handle all possible constant values
8. **Case Sensitivity**: Constants are case-sensitive
9. **Introspection**: Use `.all()` for dynamic behavior
10. **Migration**: Update all code when adding new constants

---

## Adding New Constants

### Pattern for Extension

```python
# 1. Add to class
class ActorType:
    HUMAN = "human"
    AGENT = "agent"
    SYSTEM = "system"
    EXTERNAL = "external"  # NEW
    
    @classmethod
    def all(cls):
        return [cls.HUMAN, cls.AGENT, cls.SYSTEM, cls.EXTERNAL]  # Include NEW

# 2. Update all usage sites
def handle_actor(actor_type: str):
    if actor_type == ActorType.EXTERNAL:
        # Handle external actors
        pass

# 3. Update tests
def test_new_actor_type():
    assert ActorType.EXTERNAL == "external"
    assert ActorType.EXTERNAL in ActorType.all()

# 4. Update documentation
```

---

## Related Modules

- **Settings**: `config/settings.py` - Configuration values
- **TARL API**: `api/tarl.py` - Uses verdict types
- **Governance**: `src/cognition/triumvirate.py` [[src/cognition/triumvirate.py]] - Uses pillars
- **Audit**: `audit/` - Uses risk levels

---

## Future Enhancements

1. **Enum Support**: Convert to Python `Enum` for type safety
2. **Validation Decorators**: Automatic constant validation
3. **Constant Registry**: Central registry for all constants
4. **Internationalization**: Multi-language messages
5. **Constant Deprecation**: Mark constants as deprecated
6. **Constant Documentation**: Auto-generate docs from constants
7. **Constant Freezing**: Prevent runtime modification
8. **Constant Versioning**: Track constant changes over time
9. **IDE Support**: Enhanced IDE autocomplete
10. **Constant Testing**: Automated constant consistency checks


---

## Related Documentation

- **Relationship Map**: [[relationships\configuration\README.md]]


---

## Source Code References

- **Primary Module**: [[config/constants.py]]
