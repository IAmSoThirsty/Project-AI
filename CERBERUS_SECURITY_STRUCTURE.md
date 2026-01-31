# Cerberus - Chief of Security

**Complete Security Command Structure for Project-AI**

## Overview

**Cerberus** is the Chief of Security for Project-AI, commanding all security operations through the **Global Watch Tower Security Command Center**. All security agents and roles operate under Cerberus's unified command.

## Security Authority Structure

```
┌─────────────────────────────────────────────────────────┐
│         CERBERUS - CHIEF OF SECURITY                    │
│         (Supreme Security Authority)                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────┐
│    GLOBAL WATCH TOWER - SECURITY COMMAND CENTER         │
│    (Central Coordination Hub)                           │
└──────┬──────────┬──────────┬──────────┬────────────────┘
       │          │          │          │
       ↓          ↓          ↓          ↓
┌──────────┐ ┌─────────┐ ┌────────┐ ┌──────────────┐
│ Border   │ │ Active  │ │ Red    │ │ Oversight &  │
│ Patrol   │ │ Defense │ │ Team   │ │ Analysis     │
│ Ops      │ │ Agents  │ │ Agents │ │ Agents       │
└──────────┘ └─────────┘ └────────┘ └──────────────┘
```

## Security Categories

### 1. Border Patrol Operations

**Primary Function**: File verification, threat detection, quarantine management

**Components** (Automatically registered with Cerberus):
- **PortAdmin**: Regional security coordinators
- **WatchTower**: Monitoring stations for threat detection
- **GateGuardian**: Entry point security with force field activation
- **VerifierAgent**: File scanning and sandbox execution

**Hierarchy**:
```
PortAdmin → WatchTower → GateGuardian → VerifierAgent
```

**Pre-existing functionality**: ✅ All operational, now under Cerberus

### 2. Active Defense Agents

**Primary Function**: Real-time protection, content filtering, safety enforcement

**Agents** (Available for registration):
- **SafetyGuardAgent**: Content moderation and jailbreak detection using Llama-Guard-3-8B
- **ConstitutionalGuardrailAgent**: Ethical boundary enforcement and constitutional AI principles
- **TarlProtector**: TARL (Trusted Autonomous Reasoning Language) protection and validation
- **DependencyAuditor**: Dependency scanning and vulnerability detection

**Registration Example**:
```python
tower = GlobalWatchTower.get_instance()
tower.register_security_agent("active_defense", "safety_guard_1")
tower.register_security_agent("active_defense", "constitutional_guardrail_1")
```

**Pre-existing functionality**: ✅ All operational, now registrable under Cerberus

### 3. Red Team / Adversarial Testing

**Primary Function**: Security testing, vulnerability assessment, adversarial probing

**Agents** (Available for registration):
- **RedTeamAgent**: Comprehensive adversarial testing and attack simulation
- **RedTeamPersonaAgent**: Persona-based adversarial testing with multiple attack profiles
- **CodeAdversaryAgent**: Code-level adversarial testing and mutation analysis
- **JailbreakBenchAgent**: Jailbreak attempt testing and prompt injection detection

**Registration Example**:
```python
tower = GlobalWatchTower.get_instance()
tower.register_security_agent("red_team", "red_team_agent_1")
tower.register_security_agent("red_team", "code_adversary_1")
```

**Pre-existing functionality**: ✅ All operational, now registrable under Cerberus

### 4. Oversight & Analysis

**Primary Function**: Security monitoring, validation, decision transparency

**Agents** (Available for registration):
- **OversightAgent**: System health monitoring and compliance tracking
- **ValidatorAgent**: Input/output validation and data integrity checking
- **ExplainabilityAgent**: Decision transparency and reasoning trace generation

**Registration Example**:
```python
tower = GlobalWatchTower.get_instance()
tower.register_security_agent("oversight", "oversight_agent_1")
tower.register_security_agent("oversight", "validator_agent_1")
```

**Pre-existing functionality**: ✅ All operational, now registrable under Cerberus

## API Reference

### Accessing Cerberus (Chief of Security)

```python
from app.core.global_watch_tower import GlobalWatchTower

# Initialize the Security Command Center
tower = GlobalWatchTower.initialize()

# Access Cerberus directly
cerberus = tower.get_chief_of_security()
print(f"Chief of Security: {cerberus.title}")  # Output: "Chief of Security"

# Get comprehensive security status
status = tower.get_security_status()
print(f"Chief: {status['chief_of_security']}")  # Output: "Cerberus"
print(f"Total incidents: {status['total_incidents']}")
print(f"Registered agents: {status['registered_agents']}")
```

### Registering Security Agents

```python
from app.core.global_watch_tower import GlobalWatchTower

tower = GlobalWatchTower.get_instance()

# Register active defense agents
tower.register_security_agent("active_defense", "safety_guard_1")
tower.register_security_agent("active_defense", "constitutional_guardrail_1")
tower.register_security_agent("active_defense", "tarl_protector_1")
tower.register_security_agent("active_defense", "dependency_auditor_1")

# Register red team agents
tower.register_security_agent("red_team", "red_team_agent_1")
tower.register_security_agent("red_team", "red_team_persona_1")
tower.register_security_agent("red_team", "code_adversary_1")
tower.register_security_agent("red_team", "jailbreak_tester_1")

# Register oversight agents
tower.register_security_agent("oversight", "oversight_agent_1")
tower.register_security_agent("oversight", "validator_agent_1")
tower.register_security_agent("oversight", "explainability_agent_1")

# Verify registration
status = tower.get_security_status()
print(f"Border Patrol: {status['registered_agents']['border_patrol']}")
print(f"Active Defense: {status['registered_agents']['active_defense']}")
print(f"Red Team: {status['registered_agents']['red_team']}")
print(f"Oversight: {status['registered_agents']['oversight']}")
```

### Security Status Reporting

```python
# Get detailed security status from Cerberus
status = tower.get_security_status()

# Status structure:
{
    "chief_of_security": "Cerberus",
    "total_incidents": <count>,
    "registered_agents": {
        "border_patrol": <count>,
        "active_defense": <count>,
        "red_team": <count>,
        "oversight": <count>
    },
    "agent_details": {
        "border_patrol": [<agent_ids>],
        "active_defense": [<agent_ids>],
        "red_team": [<agent_ids>],
        "oversight": [<agent_ids>]
    }
}
```

### Incident Recording

```python
# Cerberus records all security incidents
cerberus = tower.get_chief_of_security()

# Record custom incident
cerberus.record_incident({
    "type": "security_alert",
    "severity": "high",
    "description": "Suspicious activity detected",
    "source": "active_defense_agent_1"
})

# Get all incidents
incidents = tower.get_cerberus_incidents()
for incident in incidents:
    print(incident)
```

### Emergency Lockdown

```python
# Activate emergency lockdown through Cerberus
tower.activate_emergency_lockdown("Critical security breach detected")

# Cerberus executes lockdown protocols:
# 1. Activates force fields on all gate guardians
# 2. Signals emergency to all port admins
# 3. Records lockdown incident
# 4. Escalates to all security categories
```

## GUI Access

The **Watch Tower Panel** provides visual access to the Security Command Center:

**Location**: Main Dashboard → 🏰 WATCH TOWER button

**Displays**:
- Chief of Security status (Cerberus)
- Operational statistics
- Border Patrol component counts
- Registered security agents by category
- Recent incident log
- Emergency lockdown controls

**Title**: "SECURITY COMMAND CENTER - CERBERUS CHIEF OF SECURITY"

## Integration Examples

### Example 1: Initialize Complete Security System

```python
from app.core.global_watch_tower import GlobalWatchTower

# Initialize Security Command Center
tower = GlobalWatchTower.initialize(
    num_port_admins=2,
    towers_per_port=10,
    gates_per_tower=5,
    data_dir="data/security"
)

# Register all active defense agents
tower.register_security_agent("active_defense", "safety_guard_main")
tower.register_security_agent("active_defense", "guardrail_main")
tower.register_security_agent("active_defense", "tarl_protector_main")
tower.register_security_agent("active_defense", "dep_auditor_main")

# Register all red team agents
tower.register_security_agent("red_team", "red_team_main")
tower.register_security_agent("red_team", "red_persona_main")
tower.register_security_agent("red_team", "code_adv_main")
tower.register_security_agent("red_team", "jailbreak_main")

# Register all oversight agents
tower.register_security_agent("oversight", "oversight_main")
tower.register_security_agent("oversight", "validator_main")
tower.register_security_agent("oversight", "explain_main")

# Verify complete security structure
status = tower.get_security_status()
print(f"✅ {status['chief_of_security']} is Chief of Security")
print(f"✅ {sum(status['registered_agents'].values())} total agents registered")
```

### Example 2: Security Monitoring Loop

```python
import time
from app.core.global_watch_tower import GlobalWatchTower

tower = GlobalWatchTower.get_instance()
cerberus = tower.get_chief_of_security()

while True:
    # Get current status
    status = tower.get_security_status()
    
    # Check for incidents
    if status['total_incidents'] > 0:
        print(f"⚠️ {status['total_incidents']} incidents recorded")
        recent = cerberus.incidents[-5:]  # Last 5 incidents
        for incident in recent:
            print(f"  - {incident}")
    
    # Verify all agents operational
    print(f"✅ Border Patrol: {status['registered_agents']['border_patrol']} agents")
    print(f"✅ Active Defense: {status['registered_agents']['active_defense']} agents")
    print(f"✅ Red Team: {status['registered_agents']['red_team']} agents")
    print(f"✅ Oversight: {status['registered_agents']['oversight']} agents")
    
    time.sleep(60)  # Check every minute
```

## Testing

Complete test coverage in `tests/test_global_watch_tower.py`:

```bash
# Run all watch tower tests
pytest tests/test_global_watch_tower.py -v

# Run Cerberus-specific tests
pytest tests/test_global_watch_tower.py::TestCerberusChiefOfSecurity -v
```

**Test Coverage**:
- ✅ Cerberus is Chief of Security
- ✅ Border patrol agents registered
- ✅ Active defense agent registration
- ✅ Red team agent registration
- ✅ Oversight agent registration
- ✅ Security status reporting
- ✅ Incident tracking
- ✅ Backward compatibility

**All 36 tests passing** (28 existing + 8 new Cerberus tests)

## Architecture Files

**Core Implementation**:
- `src/app/agents/border_patrol.py` - Cerberus class and border patrol hierarchy
- `src/app/core/global_watch_tower.py` - Security Command Center singleton
- `src/app/gui/watch_tower_panel.py` - GUI for Security Command Center

**Agent Implementations**:
- `src/app/agents/safety_guard_agent.py` - SafetyGuardAgent
- `src/app/agents/constitutional_guardrail_agent.py` - ConstitutionalGuardrailAgent
- `src/app/agents/tarl_protector.py` - TarlProtector
- `src/app/agents/dependency_auditor.py` - DependencyAuditor
- `src/app/agents/red_team_agent.py` - RedTeamAgent
- `src/app/agents/red_team_persona_agent.py` - RedTeamPersonaAgent
- `src/app/agents/code_adversary_agent.py` - CodeAdversaryAgent
- `src/app/agents/jailbreak_bench_agent.py` - JailbreakBenchAgent
- `src/app/agents/oversight.py` - OversightAgent
- `src/app/agents/validator.py` - ValidatorAgent
- `src/app/agents/explainability.py` - ExplainabilityAgent

**Documentation**:
- `GLOBAL_WATCH_TOWER.md` - Security Command Center guide
- `CERBERUS_SECURITY_STRUCTURE.md` - This document
- `GOD_TIER_INTELLIGENCE_SYSTEM.md` - Intelligence system (separate from security)

## Key Principles

1. **Unified Command**: All security operations under Cerberus
2. **Organized Structure**: 4 clear security categories
3. **Backward Compatible**: All pre-existing agents continue to operate
4. **Extensible**: Easy to add new security agents
5. **Comprehensive**: Complete visibility of security posture
6. **Operational**: All systems continue to run as before

## Summary

✅ **Cerberus is Chief of Security**
✅ **All security agents organized under Security Command Center**
✅ **Border Patrol operations under Cerberus command**
✅ **Active Defense agents ready for registration**
✅ **Red Team agents ready for registration**
✅ **Oversight agents ready for registration**
✅ **All pre-existing functionality preserved**
✅ **Complete testing coverage**
✅ **GUI displays security hierarchy**

**Status: OPERATIONAL - Security Command Structure Complete** 🛡️
