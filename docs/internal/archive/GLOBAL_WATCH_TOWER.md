## GLOBAL_WATCH_TOWER.md

Productivity: Out-Dated(archive)                                2026-03-01T08:58:15-07:00
>
> [!WARNING]
> **RELEVANCE STATUS**: ARCHIVED / HISTORICAL
> **CURRENT ROLE**: Architecture and usage guide for the Security Command Center (Cerberus) hub (Jan 2026).
> **LAST VERIFIED**: 2026-03-01

## Global Watch Tower System - Security Command Center

The Global Watch Tower System serves as the **Security Command Center** for Project-AI, operating under **Cerberus (Chief of Security)**. This centralized security hub provides system-wide monitoring, file verification, and coordinates all security agents and operations.

## Overview

The Watch Tower system implements a hierarchical security architecture with **Cerberus as Chief of Security**:

```
Cerberus (Chief of Security)
    ↓
Security Command Center (Global Watch Tower)
    ↓
    ┌──────────────┬─────────────────┬──────────────┬──────────────┐
    │              │                 │              │              │
Border Patrol    Active Defense    Red Team       Oversight &
Operations       Agents            Agents         Analysis
    │              │                 │              │
    ├ PortAdmin    ├ SafetyGuard     ├ RedTeam     ├ Oversight
    ├ WatchTower   ├ Constitutional  ├ CodeAdv     ├ Validator
    ├ GateGuardian ├ TarlProtector   ├ Jailbreak   └ Explainability
    └ VerifierAgent└ DepAuditor
```

### Security Authority Structure

- **Cerberus**: Chief of Security - Supreme security authority
- **Security Command Center (Global Watch Tower)**: Central coordination hub
- **Border Patrol Operations**: File verification, quarantine, threat detection
- **Active Defense Agents**: Real-time protection (Safety Guards, Constitutional Guardrails)
- **Red Team Agents**: Adversarial testing and vulnerability assessment
- **Oversight & Analysis**: Security monitoring, validation, and explainability

**All security agents and roles operate under Cerberus's command through the Security Command Center.**

## Quick Start

### Initialization

Initialize the global watch tower system once at application startup:

```python
from app.core.global_watch_tower import GlobalWatchTower

# Initialize with default settings

tower = GlobalWatchTower.initialize()

# Or with custom configuration

tower = GlobalWatchTower.initialize(
    num_port_admins=2,      # Number of port administrators
    towers_per_port=5,      # Watch towers per port
    gates_per_tower=3,      # Gate guardians per tower
    data_dir="data",        # Data directory for artifacts
    max_workers=2,          # Worker processes for sandboxing
    timeout=8,              # Sandbox timeout in seconds
)
```

### Basic Usage

#### Access Cerberus (Chief of Security)

```python
from app.core.global_watch_tower import get_global_watch_tower

tower = get_global_watch_tower()

# Get Cerberus (Chief of Security)

cerberus = tower.get_chief_of_security()
print(f"Chief of Security: {cerberus.title}")

# Get comprehensive security status

status = tower.get_security_status()
print(f"Chief: {status['chief_of_security']}")
print(f"Total incidents: {status['total_incidents']}")
print(f"Registered agents: {status['registered_agents']}")
```

#### Register External Security Agents

All security agents should register with Cerberus through the Security Command Center:

```python
from app.core.global_watch_tower import get_global_watch_tower

tower = get_global_watch_tower()

# Register active defense agents

tower.register_security_agent("active_defense", "safety_guard_1")
tower.register_security_agent("active_defense", "constitutional_guardrail_1")
tower.register_security_agent("active_defense", "tarl_protector_1")

# Register red team agents

tower.register_security_agent("red_team", "red_team_agent_1")
tower.register_security_agent("red_team", "code_adversary_1")
tower.register_security_agent("red_team", "jailbreak_tester_1")

# Register oversight agents

tower.register_security_agent("oversight", "oversight_agent_1")
tower.register_security_agent("oversight", "validator_agent_1")
tower.register_security_agent("oversight", "explainability_agent_1")

# Verify registration

status = tower.get_security_status()
print(f"Active Defense agents: {len(status['agent_details']['active_defense'])}")
print(f"Red Team agents: {len(status['agent_details']['red_team'])}")
print(f"Oversight agents: {len(status['agent_details']['oversight'])}")
```

#### Verify a File

```python
from app.core.global_watch_tower import get_global_watch_tower

tower = get_global_watch_tower()
result = tower.verify_file("/path/to/file.py")

if result["success"] and result["verdict"] == "clean":
    print("File is safe to use")
else:
    print("File may be suspicious")
```

#### Using Convenience Functions

```python
from app.core.global_watch_tower import verify_file_globally

result = verify_file_globally("/path/to/plugin.py")
print(f"Verdict: {result['verdict']}")
```

### Quarantine Workflow

For deferred processing:

```python
tower = get_global_watch_tower()

# Place file in quarantine

box = tower.quarantine_file("/path/to/suspicious.py")
print(f"Quarantined: {box.path}")

# Later: process the file

result = tower.process_quarantined(str(box.path))
print(f"Verdict: {result['verdict']}")
```

### Emergency Lockdown

Activate system-wide lockdown in case of critical threats:

```python
tower = get_global_watch_tower()
tower.activate_emergency_lockdown("Critical security breach detected")
```

This activates force fields on all gate guardians and signals Cerberus for emergency protocols.

## Statistics and Monitoring

### Get System Statistics

```python
stats = tower.get_stats()

print(f"Total verifications: {stats['total_verifications']}")
print(f"Total incidents: {stats['total_incidents']}")
print(f"Active quarantine: {stats['active_quarantine']}")
print(f"Cerberus incidents: {stats['cerberus_incidents']}")
```

### Access Specific Components

```python

# Get a specific watch tower

watch_tower = tower.get_tower_by_id("wt-0-1")
if watch_tower:
    print(f"Reports: {len(watch_tower.reports)}")

# Get a specific gate guardian

gate = tower.get_gate_by_id("gate-0-0-0")
if gate:
    print(f"Force field: {gate.force_field_active}")
```

### Monitor Cerberus Incidents

```python
incidents = tower.get_cerberus_incidents()
for incident in incidents:
    print(f"Incident: {incident}")
```

## Architecture Details

### Hierarchy

- **Cerberus**: Command center that records all incidents and can execute lockdowns
- **PortAdmin**: Regional coordinator managing multiple watch towers
- **WatchTower**: Monitoring station that receives reports from gates and escalates threats
- **GateGuardian**: Entry point that quarantines files and coordinates verification
- **VerifierAgent**: Performs actual file scanning and sandboxed execution

### Security Features

1. **Quarantine System**: Files are isolated before verification
1. **Sandboxed Execution**: Files are executed in isolated processes with timeout
1. **Dependency Analysis**: Scans for malicious imports and dependencies
1. **Threat Escalation**: Repeated attacks trigger automatic escalation
1. **Emergency Lockdown**: System-wide force field activation
1. **Incident Tracking**: All security events are logged to Cerberus

### Verification Process

When you verify a file:

1. File is placed in quarantine
1. Dependency analysis is performed (imports, pip packages)
1. File is executed in sandboxed environment
1. Results are evaluated and verdict is determined
1. If suspicious, incident is reported to watch tower
1. Watch tower may escalate to PortAdmin if repeated threats detected
1. PortAdmin notifies Cerberus for permanent record
1. File is released from quarantine after processing

## Integration Examples

See `examples/global_watch_tower_demo.py` for comprehensive examples including:

- Basic initialization and verification
- Quarantine workflow
- Statistics and monitoring
- Emergency lockdown procedures
- Convenience functions
- Component access

Run the examples:

```bash
python examples/global_watch_tower_demo.py
```

## Testing

The system includes a comprehensive test suite:

```bash
pytest tests/test_global_watch_tower.py -v
```

Test coverage includes:

- Singleton initialization
- File verification
- Quarantine workflow
- Emergency lockdown
- Statistics and monitoring
- Convenience functions

## Thread Safety

The GlobalWatchTower singleton is thread-safe:

- Initialization uses a lock to prevent race conditions
- Internal components (GateGuardian) use locks for quarantine operations
- Safe to use from multiple threads

## Best Practices

1. **Initialize Once**: Call `GlobalWatchTower.initialize()` once at startup
1. **Use Convenience Functions**: For simple verification, use `verify_file_globally()`
1. **Monitor Statistics**: Regularly check `get_stats()` for security metrics
1. **Handle Verdicts**: Always check the verdict and act accordingly
1. **Emergency Procedures**: Have a plan for handling lockdown events

## API Reference

### GlobalWatchTower

- `initialize(**config)` - Initialize the singleton (class method)
- `get_instance()` - Get the singleton instance (class method)
- `is_initialized()` - Check initialization status (class method)
- `reset()` - Reset singleton (for testing only) (class method)
- `verify_file(path)` - Verify a file
- `quarantine_file(path)` - Place file in quarantine
- `process_quarantined(path)` - Process quarantined file
- `activate_emergency_lockdown(reason)` - Activate system lockdown
- `get_stats()` - Get system statistics
- `get_cerberus_incidents()` - Get incident list
- `get_tower_by_id(id)` - Get specific watch tower
- `get_gate_by_id(id)` - Get specific gate guardian

### Convenience Functions

- `get_global_watch_tower()` - Get singleton instance
- `verify_file_globally(path)` - Quick file verification

## Related Documentation

- `src/app/agents/border_patrol.py` - Core border patrol classes
- `tests/test_global_watch_tower.py` - Test suite
- `examples/global_watch_tower_demo.py` - Usage examples

## Notes

- The sandbox execution uses ProcessPoolExecutor for isolation
- Default timeout is 8 seconds (configurable)
- Files are automatically released from quarantine after processing
- Force fields prevent new files from entering quarantined gates
- All incidents are persisted to `data/monitoring/cerberus_incidents.json`
