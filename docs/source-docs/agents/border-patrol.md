---
title: "Border Patrol - Multi-Tier Security Infrastructure for Plugin Verification"
id: "border-patrol"
type: "technical"
version: "1.0.0"
status: "production"
created_date: "2026-04-20"
updated_date: "2026-04-20"
author: "AGENT-041"
contributors: ["Architecture Team", "Security Team", "Cerberus Team"]
category: "ai-agents"
tags: ["security", "border-control", "plugin-verification", "sandbox", "quarantine", "cerberus"]
technologies: ["Python", "ProcessPoolExecutor", "CognitionKernel", "DependencyAuditor", "Sandbox"]
related_docs: ["safety-guard-agent.md", "oversight.md", "dependency-auditor.md"]
dependencies: ["cognition_kernel.py", "kernel_integration.py", "dependency_auditor.py", "cerberus_dashboard.py"]
classification: "technical"
audience: ["developers", "security-engineers", "devops", "infrastructure-engineers"]
estimated_reading_time: "18 minutes"
---

# Border Patrol: Multi-Tier Security Infrastructure for Plugin Verification

## Overview

**Border Patrol** is a **hierarchical security architecture** implementing defense-in-depth for plugin and module verification. It provides a **four-tier security hierarchy** (Cerberus → PortAdmins → WatchTowers → GateGuardians) with quarantine-based file processing, sandboxed execution, and automated incident response.

### Purpose

The Border Patrol system serves as **Project-AI's first line of defense** against malicious plugins, untrusted modules, and supply-chain attacks:

1. **Quarantine System**: Isolates incoming files in sealed quarantine boxes before verification
2. **Sandboxed Verification**: Executes plugins in isolated processes with timeout protection
3. **Dependency Analysis**: Audits module dependencies for malicious packages
4. **Hierarchical Escalation**: Routes incidents from GateGuardians → WatchTowers → PortAdmins → Cerberus
5. **Emergency Response**: Activates force fields and lockdowns when attacks detected

### Key Features

✅ **Four-Tier Hierarchy**: Cerberus (Chief of Security) → PortAdmins → WatchTowers → GateGuardians  
✅ **Quarantine-Based Processing**: Files sealed in QuarantineBox until verified  
✅ **Sandboxed Execution**: ProcessPoolExecutor with configurable timeout (default: 8s)  
✅ **Dependency Auditing**: Integration with DependencyAuditor for package analysis  
✅ **Automated Incident Recording**: Integration with Cerberus Dashboard  
✅ **Force Field Activation**: Emergency lockdown on repeated attack detection  
✅ **Attack Pattern Tracking**: Monitors repeated attacks from same source  
✅ **Kernel-Routed Operations**: VerifierAgent operations routed through CognitionKernel  
✅ **Scalable Architecture**: 10 WatchTowers × 5 GateGuardians = 50 verification gates  

### Critical Context

**Defense-in-Depth Model**: Border Patrol implements multiple layers of security:
1. **Gate Level**: Initial quarantine and basic checks
2. **Tower Level**: Pattern analysis and attack detection
3. **Admin Level**: Incident aggregation and response coordination
4. **Cerberus Level**: Global security oversight and emergency lockdowns

**Fail-Closed Design**: If sandbox execution times out or crashes, the file is marked as `suspicious` and blocked. This prevents attacks that induce failures to bypass verification.

**Cerberus as Chief of Security**: All security agents (Border Patrol, Active Defense, Red Team, Oversight) operate under Cerberus's command through the Global Watch Tower Security Command Center.

**Non-Destructive Lockdowns**: Emergency lockdowns seal quarantine boxes and create audit entries but do NOT delete files. This preserves evidence for forensic analysis.

---

## Architecture

### Class Hierarchy

```python
# Verification Layer
KernelRoutedAgent (base class - kernel_integration.py)
    └── VerifierAgent
            ├── _run_sandbox()
            ├── _call_worker_run()
            ├── verify()
            └── _do_verify()

# Border Control Layer (No kernel routing - coordinated by Cerberus)
GateGuardian
    ├── ingest()
    ├── process_next()
    ├── activate_force_field()
    └── release()

WatchTower
    ├── receive_report()
    └── signal_emergency()

PortAdmin
    ├── notify_incident()
    └── handle_emergency()

# Security Command Center
Cerberus (Chief of Security)
    ├── record_incident()
    ├── execute_lockdown()
    ├── register_security_agent()
    └── get_security_status()

# Data Structures
QuarantineBox
    ├── path: str
    ├── created_ts: float
    ├── sealed: bool
    ├── verified: bool
    └── metadata: dict
```

### Data Flow

```
Incoming Plugin File
    ↓
┌──────────────────────────────────────────┐
│ GateGuardian.ingest()                    │
│   - Create QuarantineBox                 │
│   - Seal file (sealed=True)              │
│   - Add to quarantine dict               │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│ GateGuardian.process_next()              │
│   - Retrieve from quarantine             │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│ VerifierAgent.verify() [KERNEL ROUTED]   │
│   - CognitionKernel routing              │
│   - DependencyAuditor.analyze_new_module()│
│   - _run_sandbox() (ProcessPoolExecutor) │
│   - Timeout protection (8s default)      │
└──────────┬───────────────────────────────┘
           ↓
    Sandbox Report
           ↓
    ┌─────┴─────┐
   Clean    Suspicious
    ↓             ↓
verified=True  verified=False
    ↓             ↓
┌──────────────────────────────────────────┐
│ WatchTower.receive_report()              │
│   - Record in reports list               │
│   - Track attack_counts by source       │
│   - Escalate if repeated (>3 attacks)   │
└──────────┬───────────────────────────────┘
           ↓
  Repeated Attacks / Exception?
           ↓
┌──────────────────────────────────────────┐
│ PortAdmin.notify_incident()              │
│   - Aggregate incidents from towers      │
└──────────┬───────────────────────────────┘
           ↓
┌──────────────────────────────────────────┐
│ Cerberus.record_incident()               │
│   - Global incident tracking             │
│   - Integration with Cerberus Dashboard  │
└──────────────────────────────────────────┘
```

### Hierarchical Organization

```
Cerberus (Chief of Security)
    |
    ├── PortAdmin[0]
    │   ├── WatchTower[0]
    │   │   ├── GateGuardian[0] → VerifierAgent[v-0-0-0]
    │   │   ├── GateGuardian[1] → VerifierAgent[v-0-0-1]
    │   │   ├── GateGuardian[2] → VerifierAgent[v-0-0-2]
    │   │   ├── GateGuardian[3] → VerifierAgent[v-0-0-3]
    │   │   └── GateGuardian[4] → VerifierAgent[v-0-0-4]
    │   ├── WatchTower[1]
    │   │   └── [5 GateGuardians + VerifierAgents]
    │   └── ... (10 WatchTowers total)
    │
    └── PortAdmin[1+] (if scaling horizontally)
```

**Scalability**: `build_border_patrol(num_port_admins=1)` creates:
- 1 PortAdmin
- 10 WatchTowers per admin
- 5 GateGuardians per tower
- Total: **50 verification gates** per admin

### Kernel Integration

Only **VerifierAgent** routes through CognitionKernel (verification is a high-risk operation):

```python
def verify(self, file_path: str) -> dict[str, Any]:
    return self._execute_through_kernel(
        self._do_verify,
        action_name="verify_file",
        action_args=(file_path,),
        risk_level="high",  # Sandbox execution is high-risk
        metadata={"file_path": file_path, "agent_id": self.agent_id}
    )
```

**Audit Trail**: Every verification logged to kernel audit system with:
- File path being verified
- Dependency analysis results
- Sandbox execution report (success/failure/timeout)
- Verdict (clean/suspicious)
- VerifierAgent ID

**Non-Kernel Operations**: GateGuardian, WatchTower, PortAdmin do NOT route through kernel (they coordinate but don't execute untrusted code).

---

## API Reference

### VerifierAgent

#### `__init__(agent_id, data_dir, max_workers, timeout, kernel)`

Initialize sandboxed verification agent.

**Parameters:**
- `agent_id` (str): Unique identifier for this verifier (e.g., "v-0-0-0")
- `data_dir` (str, default="data"): Directory for DependencyAuditor data storage
- `max_workers` (int, default=2): ProcessPoolExecutor worker count
- `timeout` (int, default=8): Sandbox execution timeout in seconds
- `kernel` (CognitionKernel | None, default=None): Kernel instance for routing

**Raises:**
- None (constructor never fails)

**Example:**
```python
from app.agents.border_patrol import VerifierAgent
from app.core.cognition_kernel import CognitionKernel

kernel = CognitionKernel()
verifier = VerifierAgent(
    agent_id="verifier_001",
    data_dir="data/verification",
    max_workers=4,    # 4 parallel sandbox executions
    timeout=10,       # 10-second timeout
    kernel=kernel
)
```

---

#### `verify(file_path)`

Verify a file through dependency analysis and sandboxed execution.

**Parameters:**
- `file_path` (str): Path to file to verify

**Returns:**
- `dict[str, Any]`: Verification report
  ```python
  {
      "success": True,
      "deps": {
          # DependencyAuditor results
          "imports": ["os", "sys", "requests"],
          "suspicious": []
      },
      "sandbox": {
          # Sandbox execution results
          "exception": None,   # or exception message
          "output": "...",
          "return_code": 0
      },
      "verdict": "clean"  # or "suspicious"
  }
  ```

**Behavior:**
- **Kernel-Routed**: Requires CognitionKernel approval (high-risk operation)
- **Fail-Closed**: Timeout or exception = verdict "suspicious"
- **Timeout Protection**: Sandbox killed after `timeout` seconds
- **Process Isolation**: Runs in separate process (not thread)

**Usage Example:**
```python
report = verifier.verify("plugins/suspicious_plugin.py")

if report["verdict"] == "clean":
    print("Plugin verified successfully")
    print(f"Dependencies: {report['deps']['imports']}")
elif report["verdict"] == "suspicious":
    print("WARNING: Suspicious plugin detected!")
    if report["sandbox"].get("exception"):
        print(f"Exception: {report['sandbox']['exception']}")
else:
    print(f"Verification failed: {report.get('error')}")
```

---

### GateGuardian

#### `__init__(gate_id, verifier, watch_tower)`

Initialize gate guardian for file quarantine and processing.

**Parameters:**
- `gate_id` (str): Unique identifier for this gate (e.g., "g-0-0-0")
- `verifier` (VerifierAgent): VerifierAgent instance for file verification
- `watch_tower` (WatchTower): WatchTower instance for incident reporting

**Raises:**
- None

**Example:**
```python
from app.agents.border_patrol import GateGuardian, VerifierAgent, WatchTower

verifier = VerifierAgent("v-0-0-0")
watch_tower = WatchTower("wt-0", port_admin)
gate = GateGuardian("gate-001", verifier, watch_tower)
```

---

#### `ingest(file_path)`

Place a file into quarantine.

**Parameters:**
- `file_path` (str): Path to file to quarantine

**Returns:**
- `QuarantineBox`: Quarantine box containing the file
  ```python
  QuarantineBox(
      path="plugins/untrusted.py",
      created_ts=1713644400.0,
      sealed=True,
      verified=False,
      metadata=None
  )
  ```

**Behavior:**
- Thread-safe (uses lock)
- Creates sealed quarantine box
- Adds to internal quarantine dict
- Does NOT verify file (call `process_next()` for that)

**Usage Example:**
```python
box = gate.ingest("plugins/new_plugin.py")
print(f"Quarantined: {box.path}")
print(f"Sealed: {box.sealed}")
print(f"Created: {box.created_ts}")
```

---

#### `process_next(file_path)`

Verify a quarantined file and report results to watch tower.

**Parameters:**
- `file_path` (str): Path to quarantined file to process

**Returns:**
- `dict[str, Any]`: Verification report (same as `VerifierAgent.verify()`)

**Raises:**
- `KeyError`: If file not found in quarantine

**Behavior:**
- Calls `VerifierAgent.verify()` on file
- Updates quarantine box metadata
- Notifies watch tower of results
- Records incident to Cerberus Dashboard if suspicious

**Usage Example:**
```python
# Quarantine file
box = gate.ingest("plugins/untrusted.py")

# Process and verify
report = gate.process_next("plugins/untrusted.py")

if report["verdict"] == "suspicious":
    print("ALERT: Suspicious file detected!")
    print(f"Details: {report['metadata']}")
    # WatchTower and PortAdmin automatically notified
```

---

#### `activate_force_field()`

Activate emergency force field (block all new ingestions).

**Parameters:** None

**Returns:** None

**Behavior:**
- Sets `force_field_active = True`
- Signals WatchTower to escalate to emergency
- Logs critical warning

**Usage Example:**
```python
# Activate force field on repeated attack detection
if attack_count > 5:
    gate.activate_force_field()
    logger.critical("Force field activated - all ingestion blocked")
```

---

#### `release(file_path)`

Release a file from quarantine.

**Parameters:**
- `file_path` (str): Path to file to release

**Returns:** None

**Behavior:**
- Thread-safe (uses lock)
- Removes file from quarantine dict
- Does NOT delete file from filesystem

**Usage Example:**
```python
# After successful verification
report = gate.process_next("plugins/safe_plugin.py")
if report["verdict"] == "clean":
    gate.release("plugins/safe_plugin.py")
    print("Plugin released from quarantine")
```

---

### WatchTower

#### `__init__(tower_id, port_admin)`

Initialize watch tower for incident monitoring.

**Parameters:**
- `tower_id` (str): Unique identifier for this tower
- `port_admin` (PortAdmin): PortAdmin instance for escalation

**Example:**
```python
from app.agents.border_patrol import WatchTower, PortAdmin, Cerberus

cerberus = Cerberus()
port_admin = PortAdmin("admin-001", cerberus)
watch_tower = WatchTower("tower-001", port_admin)
```

---

#### `receive_report(gate_id, box)`

Receive verification report from a gate guardian.

**Parameters:**
- `gate_id` (str): ID of gate that sent the report
- `box` (QuarantineBox): Quarantine box with verification metadata

**Returns:** None

**Behavior:**
- Adds report to internal reports list
- Tracks attack counts by source
- Escalates to PortAdmin if:
  - Same source has > 3 attacks
  - Sandbox crashed or threw exception
- Records incident to Cerberus Dashboard

**Usage Example:**
```python
# Called automatically by GateGuardian.process_next()
# Manual call example:
box = QuarantineBox(
    path="plugin.py",
    created_ts=time.time(),
    sealed=True,
    verified=False,
    metadata={"sandbox": {"exception": "ImportError: malicious"}}
)

watch_tower.receive_report("gate-001", box)
# Automatically escalates if exception present
```

---

#### `signal_emergency(gate_id)`

Signal emergency from a gate guardian (force field activated).

**Parameters:**
- `gate_id` (str): ID of gate signaling emergency

**Returns:** None

**Behavior:**
- Logs critical alert
- Calls `PortAdmin.handle_emergency()`
- Triggers Cerberus lockdown procedures

---

### PortAdmin

#### `__init__(admin_id, command_center)`

Initialize port administrator for incident coordination.

**Parameters:**
- `admin_id` (str): Unique identifier for this admin
- `command_center` (Cerberus): Cerberus instance (Chief of Security)

**Example:**
```python
from app.agents.border_patrol import PortAdmin, Cerberus

cerberus = Cerberus()
port_admin = PortAdmin("admin-001", cerberus)

# Add watch towers
port_admin.towers = [
    WatchTower(f"tower-{i}", port_admin)
    for i in range(10)
]
```

---

#### `notify_incident(tower_id, gate_id, box)`

Receive incident notification from a watch tower.

**Parameters:**
- `tower_id` (str): ID of tower reporting incident
- `gate_id` (str): ID of gate where incident occurred
- `box` (QuarantineBox): Quarantine box involved in incident

**Returns:** None

**Behavior:**
- Logs warning
- Creates incident report
- Escalates to Cerberus.record_incident()

---

#### `handle_emergency(tower_id, gate_id)`

Handle emergency signal from a watch tower.

**Parameters:**
- `tower_id` (str): ID of tower signaling emergency
- `gate_id` (str): ID of gate where emergency occurred

**Returns:** None

**Behavior:**
- Logs critical alert
- Instructs Cerberus to execute lockdown

---

### Cerberus (Chief of Security)

#### `__init__()`

Initialize Cerberus as Chief of Security.

**Parameters:** None

**Example:**
```python
from app.agents.border_patrol import Cerberus

cerberus = Cerberus()
print(f"Initialized: {cerberus.title}")  # "Chief of Security"
```

---

#### `record_incident(incident)`

Record a security incident.

**Parameters:**
- `incident` (dict[str, Any]): Incident details

**Returns:** None

**Behavior:**
- Logs error with incident details
- Records incident to Cerberus Dashboard (persistent monitoring)
- Adds to internal incidents list

**Usage Example:**
```python
cerberus.record_incident({
    "type": "suspicious_plugin",
    "gate": "g-0-0-0",
    "module": "malicious_plugin.py",
    "metadata": {
        "sandbox": {"exception": "Malicious code detected"}
    }
})
```

---

#### `execute_lockdown(tower_id, gate_id)`

Execute emergency lockdown for a tower/gate.

**Parameters:**
- `tower_id` (str): ID of tower to lock down
- `gate_id` (str): ID of gate to lock down

**Returns:** None

**Behavior:**
- Logs critical alert
- Records lockdown incident
- **Non-destructive**: Marks boxes as sealed, creates audit entry
- Does NOT delete files (preserves evidence)

**Usage Example:**
```python
# Called automatically during emergencies
# Manual lockdown example:
cerberus.execute_lockdown("tower-001", "gate-005")
```

---

#### `register_security_agent(agent_type, agent_id)`

Register a security agent under Cerberus's command.

**Parameters:**
- `agent_type` (str): Category of agent
  - `"border_patrol"`: Border patrol agents (VerifierAgents, GateGuardians)
  - `"active_defense"`: Active defense agents (SafetyGuards, ConstitutionalGuardrails)
  - `"red_team"`: Red team agents (RedTeamAgent, CodeAdversary)
  - `"oversight"`: Oversight agents (OversightAgent, Validator)
- `agent_id` (str): Unique identifier for the agent

**Returns:** None

**Usage Example:**
```python
# Register agents
cerberus.register_security_agent("border_patrol", "verifier_001")
cerberus.register_security_agent("active_defense", "safety_guard_001")
cerberus.register_security_agent("red_team", "red_team_001")
cerberus.register_security_agent("oversight", "oversight_001")

# Check registration
status = cerberus.get_security_status()
print(f"Registered agents: {status['registered_agents']}")
```

---

#### `get_security_status()`

Get comprehensive security status report.

**Parameters:** None

**Returns:**
- `dict[str, Any]`: Security status
  ```python
  {
      "chief_of_security": "Cerberus",
      "total_incidents": 42,
      "registered_agents": {
          "border_patrol": 50,
          "active_defense": 10,
          "red_team": 5,
          "oversight": 3
      },
      "agent_details": {
          "border_patrol": ["verifier_001", "verifier_002", ...],
          "active_defense": ["safety_guard_001", ...],
          "red_team": ["red_team_001", ...],
          "oversight": ["oversight_001", ...]
      }
  }
  ```

**Usage Example:**
```python
status = cerberus.get_security_status()
print(f"Total incidents: {status['total_incidents']}")
print(f"Border patrol agents: {status['registered_agents']['border_patrol']}")
```

---

### Helper Functions

#### `build_border_patrol(num_port_admins)`

Build complete border patrol hierarchy.

**Parameters:**
- `num_port_admins` (int, default=1): Number of PortAdmin instances to create

**Returns:**
- `list[PortAdmin]`: List of PortAdmin instances (each with 10 WatchTowers × 5 GateGuardians)

**Usage Example:**
```python
from app.agents.border_patrol import build_border_patrol

# Build standard border patrol (50 gates)
admins = build_border_patrol(num_port_admins=1)
print(f"Created {len(admins)} PortAdmins")
print(f"Total WatchTowers: {sum(len(admin.towers) for admin in admins)}")

# Access hierarchy
admin = admins[0]
tower = admin.towers[0]
# GateGuardians created but not returned (internal to tower)
```

---

## Usage Examples

### Example 1: Basic File Verification (Simple)

```python
from app.agents.border_patrol import VerifierAgent

verifier = VerifierAgent("verifier_001")

# Verify a plugin file
report = verifier.verify("plugins/new_plugin.py")

if report["verdict"] == "clean":
    print("✓ Plugin is safe")
    print(f"Dependencies: {report['deps']['imports']}")
else:
    print("✗ Plugin is suspicious")
    if report["sandbox"].get("exception"):
        print(f"Exception: {report['sandbox']['exception']}")
```

### Example 2: Full Border Patrol Pipeline (Production)

```python
from app.agents.border_patrol import build_border_patrol

# Build border patrol infrastructure
admins = build_border_patrol(num_port_admins=1)
admin = admins[0]
tower = admin.towers[0]

# Create a gate guardian
from app.agents.border_patrol import GateGuardian, VerifierAgent

verifier = VerifierAgent("v-custom", timeout=15)
gate = GateGuardian("gate-custom", verifier, tower)

# Process incoming plugin
def process_plugin(plugin_path: str) -> bool:
    """
    Process plugin through border patrol security.
    Returns True if safe, False if suspicious.
    """
    # Step 1: Quarantine
    box = gate.ingest(plugin_path)
    logger.info(f"Quarantined: {plugin_path}")
    
    # Step 2: Verify
    report = gate.process_next(plugin_path)
    
    # Step 3: Check verdict
    if report["verdict"] == "clean":
        gate.release(plugin_path)
        logger.info(f"Released: {plugin_path}")
        return True
    else:
        logger.warning(f"Blocked: {plugin_path}")
        # File remains in quarantine
        # WatchTower automatically notified
        return False

# Usage
if process_plugin("plugins/user_submitted_plugin.py"):
    # Safe to load plugin
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "user_plugin",
        "plugins/user_submitted_plugin.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
else:
    print("Plugin rejected by border patrol")
```

### Example 3: Monitoring and Alert System (Advanced)

```python
from app.agents.border_patrol import Cerberus, build_border_patrol
import time

cerberus = Cerberus()
admins = build_border_patrol(num_port_admins=1)

# Register all verifiers
for admin_idx, admin in enumerate(admins):
    for tower_idx, tower in enumerate(admin.towers):
        # Verifiers are created internally by build_border_patrol
        # Register them manually if needed
        for gate_idx in range(5):
            verifier_id = f"v-{admin_idx}-{tower_idx}-{gate_idx}"
            cerberus.register_security_agent("border_patrol", verifier_id)

# Monitor security status
def monitor_security():
    """Monitor security status and alert on high incident rate."""
    baseline_incidents = 0
    
    while True:
        status = cerberus.get_security_status()
        current_incidents = status["total_incidents"]
        
        # Check for incident spike
        new_incidents = current_incidents - baseline_incidents
        if new_incidents > 10:
            logger.critical(
                f"ALERT: {new_incidents} new security incidents detected!"
            )
            # Trigger incident response
            send_alert_to_security_team(status)
        
        baseline_incidents = current_incidents
        time.sleep(60)  # Check every minute

# Run monitoring in background
import threading
monitor_thread = threading.Thread(target=monitor_security, daemon=True)
monitor_thread.start()
```

### Example 4: Custom Sandbox Worker (Advanced)

```python
# Custom sandbox worker with additional security checks
# Save as: app/agents/custom_sandbox_worker.py

import sys
import os
import resource

def run_module(module_path: str) -> dict[str, Any]:
    """
    Run module in sandboxed environment with resource limits.
    """
    try:
        # Set resource limits
        resource.setrlimit(
            resource.RLIMIT_CPU,
            (2, 2)  # 2 seconds CPU time
        )
        resource.setrlimit(
            resource.RLIMIT_AS,
            (50 * 1024 * 1024, 50 * 1024 * 1024)  # 50 MB memory
        )
        
        # Restrict file system access
        os.chdir("/tmp")  # Isolated directory
        
        # Import and execute module
        import importlib.util
        spec = importlib.util.spec_from_file_location("sandboxed", module_path)
        if not spec or not spec.loader:
            return {"error": "failed_to_load", "success": False}
        
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        return {
            "success": True,
            "module_name": module.__name__,
            "functions": dir(module)
        }
        
    except resource.error as e:
        return {"error": f"resource_limit_exceeded: {e}", "success": False}
    except Exception as e:
        return {"error": str(e), "success": False}

# Use custom worker with VerifierAgent
verifier = VerifierAgent(
    "v-custom",
    timeout=5,
    # Point to custom worker (implementation detail - would need refactoring)
)
```

---

## Integration Points

### 1. Dependency Auditor Integration

**Location**: `src/app/agents/dependency_auditor.py`

**Integration Pattern**:
```python
class VerifierAgent:
    def __init__(self, agent_id: str, data_dir: str = "data", ...):
        self.auditor = DependencyAuditor(data_dir=data_dir)
    
    def _do_verify(self, file_path: str):
        # Dependency analysis
        deps_report = self.auditor.analyze_new_module(file_path)
        
        # Check for suspicious packages
        if deps_report.get("suspicious_packages"):
            return {"verdict": "suspicious", ...}
```

### 2. Cerberus Dashboard Integration

**Location**: `src/app/monitoring/cerberus_dashboard.py`

**Automatic Incident Recording**:
```python
from app.monitoring.cerberus_dashboard import record_incident

# Called automatically by GateGuardian.process_next()
if not box.verified:
    record_incident({
        "type": "suspicious_plugin",
        "gate": self.gate_id,
        "module": file_path,
        "metadata": report
    })
```

### 3. Plugin Manager Integration

**Location**: `src/app/core/ai_systems.py` (PluginManager)

**Safe Plugin Loading**:
```python
class PluginManager:
    def __init__(self):
        self.verifier = VerifierAgent("plugin_verifier")
    
    def load_plugin(self, plugin_path: str):
        # Verify before loading
        report = self.verifier.verify(plugin_path)
        
        if report["verdict"] != "clean":
            raise SecurityException(
                f"Plugin failed verification: {report['verdict']}"
            )
        
        # Safe to load
        import importlib.util
        spec = importlib.util.spec_from_file_location("plugin", plugin_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
```

### 4. Red Team Integration

**Location**: `src/app/agents/red_team_agent.py`

**Testing Border Patrol Defenses**:
```python
from app.agents.red_team_agent import RedTeamAgent

red_team = RedTeamAgent()

# Test malicious plugin detection
malicious_plugins = [
    "tests/malicious/crypto_miner.py",
    "tests/malicious/data_exfiltrator.py",
    "tests/malicious/backdoor.py"
]

for plugin in malicious_plugins:
    report = verifier.verify(plugin)
    assert report["verdict"] == "suspicious", \
        f"Border patrol failed to detect {plugin}"
```

---

## Performance Characteristics

### Computational Complexity

- **Quarantine Operations**: O(1) - dict insertion/lookup with lock
- **Dependency Analysis**: O(n) where n = lines of code (import parsing)
- **Sandbox Execution**: O(1) - fixed timeout (8s default)
- **Incident Escalation**: O(1) - simple notification chain

### Latency Profile

- **Quarantine (ingest)**: ~0.1-1ms (dict operation + lock)
- **Dependency Analysis**: ~5-20ms (file parsing)
- **Sandbox Execution**: 
  - Success: ~50-500ms (depends on module complexity)
  - Timeout: exactly `timeout` seconds (8s default)
  - Exception: ~10-100ms (early termination)
- **Total Verification**: ~60ms - 8.5s (fast path vs timeout)

### Memory Footprint

- **VerifierAgent**: ~5-10 KB (small state)
- **GateGuardian**: ~1 KB + quarantine dict (1 KB per file)
- **WatchTower**: ~2 KB + reports list (500 bytes per report)
- **ProcessPoolExecutor**: ~10-50 MB per worker process
- **Total System** (50 gates): ~50-100 MB (mostly process overhead)

### Scalability

- **Concurrent Verifications**: Limited by `max_workers` (default: 2 per verifier)
- **Horizontal Scaling**: Add more PortAdmins (independent hierarchies)
- **Recommended Limits**: 
  - 50 gates per PortAdmin
  - 100 concurrent verifications per server
  - 1000 verifications/minute per server

---

## Troubleshooting

### Issue 1: Sandbox Timeout on Legitimate Plugins

**Symptoms**:
```
Sandbox execution timed out for /path/to/plugin.py
verdict: suspicious
```

**Cause**: Plugin initialization takes longer than timeout (default: 8s).

**Solution**:
```python
# Increase timeout for slow plugins
verifier = VerifierAgent(
    "v-slow-plugins",
    timeout=30  # 30-second timeout
)

# Or check plugin complexity
import os
file_size = os.path.getsize("plugin.py")
if file_size > 100_000:  # > 100 KB
    verifier = VerifierAgent("v-large", timeout=60)
else:
    verifier = VerifierAgent("v-normal", timeout=8)
```

### Issue 2: ProcessPoolExecutor Deadlock

**Symptoms**:
- Verifications hang indefinitely
- No timeout exception raised

**Cause**: ProcessPoolExecutor deadlock or zombie processes.

**Solution**:
```python
import signal

# Add signal-based timeout as backup
def verify_with_hard_timeout(verifier: VerifierAgent, file_path: str, timeout: int):
    def timeout_handler(signum, frame):
        raise TimeoutError("Hard timeout reached")
    
    # Set signal alarm
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout + 5)  # 5s buffer
    
    try:
        report = verifier.verify(file_path)
        signal.alarm(0)  # Cancel alarm
        return report
    except TimeoutError:
        signal.alarm(0)
        return {"verdict": "suspicious", "error": "hard_timeout"}

# Usage
report = verify_with_hard_timeout(verifier, "plugin.py", timeout=10)
```

### Issue 3: Quarantine Dict Memory Leak

**Symptoms**:
- Memory usage increases over time
- Quarantine dict grows without bound

**Cause**: Files never released from quarantine.

**Solution**:
```python
import time

class GateGuardianWithCleanup(GateGuardian):
    def cleanup_old_quarantine(self, max_age_seconds: int = 3600):
        """Remove quarantine boxes older than max_age."""
        with self.lock:
            current_time = time.time()
            to_remove = []
            
            for path, box in self.quarantine.items():
                age = current_time - box.created_ts
                if age > max_age_seconds:
                    to_remove.append(path)
            
            for path in to_remove:
                del self.quarantine[path]
                logger.info(f"Cleaned up old quarantine: {path}")
            
            return len(to_remove)

# Run periodic cleanup
import threading

def periodic_cleanup(gate: GateGuardianWithCleanup, interval: int = 600):
    while True:
        time.sleep(interval)
        removed = gate.cleanup_old_quarantine(max_age_seconds=3600)
        logger.info(f"Cleaned up {removed} old quarantine boxes")

cleanup_thread = threading.Thread(
    target=periodic_cleanup,
    args=(gate, 600),
    daemon=True
)
cleanup_thread.start()
```

### Issue 4: Incident Flooding

**Symptoms**:
- Cerberus Dashboard flooded with thousands of incidents
- Logs overwhelmed with incident records

**Cause**: Repeated attacks triggering excessive incident recording.

**Solution**:
```python
class WatchTowerWithRateLimiting(WatchTower):
    def __init__(self, tower_id: str, port_admin: PortAdmin):
        super().__init__(tower_id, port_admin)
        self.incident_rate_limiter = {}
    
    def receive_report(self, gate_id: str, box: QuarantineBox):
        # Check rate limit
        source = box.metadata.get("sandbox", {}).get("source", gate_id)
        current_time = time.time()
        
        # Rate limit: max 10 incidents per minute per source
        if source in self.incident_rate_limiter:
            last_incident_time, count = self.incident_rate_limiter[source]
            if current_time - last_incident_time < 60:
                if count >= 10:
                    logger.debug(f"Rate limiting incidents from {source}")
                    return  # Drop incident
                self.incident_rate_limiter[source] = (last_incident_time, count + 1)
            else:
                self.incident_rate_limiter[source] = (current_time, 1)
        else:
            self.incident_rate_limiter[source] = (current_time, 1)
        
        # Proceed with normal processing
        super().receive_report(gate_id, box)
```

### Issue 5: Sandbox Worker Import Failure

**Symptoms**:
```
failed_to_load_worker_spec
```

**Cause**: sandbox_worker.py not found or has syntax errors.

**Solution**:
```python
# Verify worker file exists
import os
worker_path = os.path.join(
    os.path.dirname(__file__),
    "sandbox_worker.py"
)

if not os.path.exists(worker_path):
    logger.error(f"Sandbox worker not found: {worker_path}")
    # Create minimal worker
    with open(worker_path, "w") as f:
        f.write("""
def run_module(module_path: str) -> dict:
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("sandboxed", module_path)
        if not spec or not spec.loader:
            return {"error": "failed_to_load", "success": False}
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return {"success": True}
    except Exception as e:
        return {"error": str(e), "success": False}
""")
```

### Issue 6: Force Field Not Blocking Ingestion

**Symptoms**:
- Force field activated but new files still being ingested
- `force_field_active=True` but `ingest()` still works

**Cause**: `ingest()` doesn't check `force_field_active` flag.

**Solution**:
```python
class GateGuardianWithForceField(GateGuardian):
    def ingest(self, file_path: str) -> QuarantineBox | None:
        # Check force field
        if self.force_field_active:
            logger.warning(
                f"Gate {self.gate_id}: Force field active, rejecting {file_path}"
            )
            return None
        
        # Proceed with normal ingestion
        return super().ingest(file_path)

# Usage
gate = GateGuardianWithForceField("gate-001", verifier, tower)

# Activate force field
gate.activate_force_field()

# Try to ingest
box = gate.ingest("new_file.py")
if box is None:
    print("Ingestion blocked by force field")
```

### Issue 7: CognitionKernel Approval Delays

**Symptoms**:
- Verification operations waiting for human approval
- Long delays in verification pipeline

**Cause**: `requires_approval=True` in kernel routing.

**Solution**:
```python
# Check VerifierAgent.verify() implementation
# Ensure requires_approval is NOT set to True
def verify(self, file_path: str) -> dict[str, Any]:
    return self._execute_through_kernel(
        self._do_verify,
        action_name="verify_file",
        action_args=(file_path,),
        risk_level="high",
        # IMPORTANT: Do not require approval for automated verification
        requires_approval=False,  # or omit (defaults to False)
        metadata={"file_path": file_path, "agent_id": self.agent_id}
    )
```

---

## Four Laws Integration

### Border Patrol ↔ Four Laws Alignment

Border Patrol enforces **Asimov's First Law** (Human Safety) through plugin verification:

| Four Laws Principle | Border Patrol Implementation |
|---------------------|------------------------------|
| **First Law** (Human Safety) | Block malicious plugins that could harm users |
| **Second Law** (Obey Orders) | Allow safe user-submitted plugins after verification |
| **Third Law** (Self-Preservation) | Sandbox protects AI system from malicious code |
| **Zeroth Law** (Humanity Safety) | Prevent supply-chain attacks affecting all users |

**Example: Malicious Plugin vs First Law**:
```python
# User submits plugin (Second Law: obey user)
user_plugin = "plugins/user_crypto_miner.py"

# Border patrol verification
report = verifier.verify(user_plugin)

if report["verdict"] == "suspicious":
    # First Law violation detected (plugin harms system)
    # First Law takes precedence over Second Law
    logger.warning("Blocked malicious plugin - First Law protection")
    raise SecurityException("Plugin violates First Law: potential harm detected")
```

---

## Security Considerations

### 1. Sandbox Escape Prevention

**Risk**: Malicious code escapes sandbox and affects host system.

**Mitigation**:
- ProcessPoolExecutor provides process-level isolation
- Resource limits (CPU, memory) prevent DoS
- Timeout prevents infinite loops
- Future: Consider Docker/container-based sandboxing

### 2. Supply Chain Attacks

**Risk**: Legitimate-looking plugins with hidden malicious dependencies.

**Mitigation**:
- DependencyAuditor checks all imports
- Quarantine prevents execution until verified
- Multi-layer verification (deps + sandbox)

### 3. Time-of-Check Time-of-Use (TOCTOU)

**Risk**: File modified between verification and loading.

**Mitigation**:
```python
import hashlib

def verify_and_load_with_hash(verifier: VerifierAgent, file_path: str):
    # Compute hash before verification
    with open(file_path, 'rb') as f:
        hash_before = hashlib.sha256(f.read()).hexdigest()
    
    # Verify
    report = verifier.verify(file_path)
    
    if report["verdict"] != "clean":
        raise SecurityException("Verification failed")
    
    # Verify hash unchanged
    with open(file_path, 'rb') as f:
        hash_after = hashlib.sha256(f.read()).hexdigest()
    
    if hash_before != hash_after:
        raise SecurityException("File modified during verification (TOCTOU attack)")
    
    # Safe to load
    import importlib.util
    spec = importlib.util.spec_from_file_location("plugin", file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
```

### 4. Incident Data Privacy

**Risk**: Incident reports contain sensitive data.

**Mitigation**:
- Truncate file paths to prevent directory traversal info leakage
- Hash file contents instead of storing raw data
- Encrypt incident reports at rest
- Implement data retention policies (delete old incidents)

---

## Related Documentation

- **[DependencyAuditor](./dependency-auditor.md)**: Dependency analysis and malicious package detection
- **[SafetyGuardAgent](./safety-guard-agent.md)**: Content moderation (complements plugin verification)
- **[OversightAgent](./oversight.md)**: Validates border patrol decisions
- **[RedTeamAgent](./red-team-agent.md)**: Tests border patrol robustness
- **[CognitionKernel](../core/cognition-kernel.md)**: Kernel routing for VerifierAgent
- **[Cerberus Dashboard](../monitoring/cerberus-dashboard.md)**: Incident monitoring and visualization

---

## Changelog

### Version 1.0.0 (2026-04-20)
- Initial production release
- Four-tier hierarchy (Cerberus → PortAdmins → WatchTowers → GateGuardians)
- Quarantine-based file processing
- Sandboxed verification with ProcessPoolExecutor (timeout: 8s, max_workers: 2)
- Dependency analysis integration (DependencyAuditor)
- Automated incident recording (Cerberus Dashboard)
- Force field activation and emergency lockdowns
- Attack pattern tracking (>3 attacks = escalation)
- CognitionKernel integration for VerifierAgent
- Scalable architecture (50 gates per PortAdmin)
- Cerberus as Chief of Security with security agent registration

### Planned Enhancements
- **Container-Based Sandboxing**: Replace ProcessPoolExecutor with Docker/Podman containers
- **ML-Based Anomaly Detection**: Use ML to detect sophisticated malicious patterns
- **Distributed Border Patrol**: Support multi-server deployment
- **Real-Time Dashboard**: Web UI for monitoring quarantine and incidents
- **Automated Remediation**: Auto-patch or quarantine-fix common issues
- **Blockchain Audit Trail**: Immutable incident logging
- **Performance Optimizations**: Parallel dependency analysis, caching

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

