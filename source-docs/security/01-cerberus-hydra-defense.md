# Cerberus Hydra Defense System

## Overview

The Cerberus Hydra Defense is Project-AI's flagship exponential multi-implementation spawning mechanism for autonomous security breach response. Inspired by the mythological Hydra ("cut off one head, three more grow back"), the system automatically spawns 3 new defensive agents in random language combinations whenever a security agent is bypassed or disabled.

**Location:** [[src/app/core/cerberus_hydra.py]] (`src/app/core/cerberus_hydra.py`) (1,200+ lines)

**Core Philosophy:** Exponential resilience through polyglot diversification and progressive system lockdown.

---

## Architecture

### Key Components

1. **CerberusHydraDefense** - Main orchestration class
2. **RuntimeManager** - 50+ programming language runtime health verification
3. **TemplateRenderer** - Safe code generation with injection prevention
4. **LockdownController** - 25-stage progressive system lockdown
5. **AgentProcess** - Cross-language process lifecycle management

### Data Structures

```python
@dataclass
class AgentRecord:
    """Enhanced agent record with full lifecycle tracking"""
    agent_id: str
    spawn_time: str
    source_event: str
    programming_language: str      # e.g., 'python', 'rust'
    programming_language_name: str # e.g., 'Python 3.11'
    human_language: str            # e.g., 'en', 'ja'
    human_language_name: str       # e.g., 'English', 'Japanese'
    runtime_path: str              # e.g., 'python3', 'cargo run'
    locked_section: str            # One of 25 lockable sections
    generation: int                # Depth of spawning (0-5)
    lockdown_stage_at_spawn: int   # Lockdown stage when spawned
    parent_agent_id: str | None
    pid: int | None
    status: str                    # active, terminated, failed
    log_file: str | None
    process: AgentProcess | None

@dataclass
class BypassEvent:
    """Record of security bypass event"""
    event_id: str
    timestamp: str
    bypassed_agent_id: str
    bypass_type: str
    risk_score: float              # 0.0-1.0
    bypass_depth: int              # Number of layers bypassed
    attacker_signature: str | None
    spawned_agents: list[str]
    lockdown_stage: int
```

---

## Core Features

### 1. Exponential Spawning

**Spawn Factor:** 3x on each bypass (configurable via `SPAWN_FACTOR`)

**Mechanism:**
- When security agent bypassed → spawn 3 new agents
- Each new agent uses random language combination (50 human × 50 programming languages)
- Total possible implementations: 2,500+ unique combinations
- Deterministic language selection seeded by incident ID

**Generation Depth:** Maximum 5 generations (configurable via `max_spawn_depth`)

```python
# Example spawn cascade
Generation 0: 3 initial agents
↓ Bypass detected
Generation 1: 9 agents (3 × 3)
↓ Bypass detected
Generation 2: 27 agents (9 × 3)
↓ Bypass detected
Generation 3: 81 agents (27 × 3)
```

### 2. Multi-Language Implementation

**50 Human Languages** (from `data/cerberus/languages.json`):
- English, Spanish, French, German, Chinese, Japanese, Arabic, Russian, Portuguese, Hindi
- Bengali, Korean, Vietnamese, Thai, Turkish, Polish, Ukrainian, Romanian, Dutch, Czech
- Swedish, Hungarian, Greek, Finnish, Norwegian, Danish, Slovak, Bulgarian, Croatian, Serbian
- Slovenian, Lithuanian, Latvian, Estonian, Maltese, Irish, Welsh, Icelandic, Basque, Catalan
- Galician, Albanian, Macedonian, Bosnian, Montenegrin, Luxembourgish, Faroese, Greenlandic, Romansh, Breton

**50 Programming Languages** (verified at startup):
- Python, JavaScript, TypeScript, Rust, Go, Java, C++, C, C#, Ruby
- PHP, Swift, Kotlin, Scala, Haskell, Elixir, Erlang, Clojure, F#, OCaml
- R, Julia, Nim, Crystal, Zig, D, Lua, Perl, Shell (Bash), PowerShell
- Assembly (x86), Fortran, COBOL, Ada, Pascal, Prolog, Scheme, Racket, Common Lisp, Smalltalk
- VHDL, Verilog, Matlab, Octave, SQL, Dart, Groovy, Tcl, AWK, Sed

**Runtime Health Verification:**
```python
# At startup, verify all runtimes
summary = runtime_manager.verify_runtimes(timeout=5)
# Returns: {healthy, degraded, unavailable} counts
```

### 3. Progressive System Lockdown

**25 Lockable Sections:**
```python
LOCKABLE_SECTIONS = [
    "authentication",        # Stage 1
    "authorization",         # Stage 2
    "data_access",          # Stage 3
    "file_operations",      # Stage 4
    "network_egress",       # Stage 5
    "api_endpoints",        # Stage 6
    "admin_functions",      # Stage 7
    "user_sessions",        # Stage 8
    "encryption_keys",      # Stage 9
    "audit_logs",           # Stage 10
    "configuration",        # Stage 11
    "model_weights",        # Stage 12
    "training_data",        # Stage 13
    "inference_engine",     # Stage 14
    "memory_management",    # Stage 15
    "process_execution",    # Stage 16
    "system_calls",         # Stage 17
    "database_access",      # Stage 18
    "cache_operations",     # Stage 19
    "backup_systems",       # Stage 20
    "monitoring_systems",   # Stage 21
    "alert_systems",        # Stage 22
    "logging_systems",      # Stage 23
    "credential_storage",   # Stage 24
    "token_management",     # Stage 25 (full lockdown)
]
```

**Lockdown Stage Computation:**
```python
def compute_lockdown_stage(risk_score: float, bypass_depth: int) -> int:
    """
    Formula: stage = min(25, ceil(risk_score * 10) + bypass_depth)
    
    Examples:
    - risk_score=0.5, depth=1 → stage 6
    - risk_score=0.9, depth=2 → stage 11
    - risk_score=1.0, depth=5 → stage 15
    """
    stage = math.ceil(risk_score * 10) + bypass_depth
    return min(25, max(0, stage))
```

---

## API Reference

### Initialization

```python
from app.core.cerberus_hydra import CerberusHydraDefense

hydra = CerberusHydraDefense(
    data_dir="data",                     # Base data directory
    enable_polyglot_execution=True,      # Actually execute agents
    max_agents=50,                       # Max concurrent agents
    security_enforcer=asl3_security      # Optional ASL3Security integration
)
```

### Spawn Initial Agents

```python
agent_ids = hydra.spawn_initial_agents(count=3)
# Returns: ['cerberus-0-a1b2c3', 'cerberus-0-d4e5f6', 'cerberus-0-g7h8i9']
```

### Detect and Respond to Bypass

```python
# Method 1: Direct bypass detection
event_id = hydra.detect_bypass(
    agent_id="cerberus-0-a1b2c3",        # Bypassed agent
    bypass_type="authentication_bypass",  # Type of bypass
    attacker_signature="192.168.1.100",  # Optional attacker identifier
    risk_score=0.85,                     # Risk level (0.0-1.0)
    bypass_depth=2                       # Layers bypassed
)

# Method 2: Via bypass event
event_id = hydra.on_bypass_detected({
    "event_id": "bypass-001",
    "timestamp": datetime.now().isoformat(),
    "agent_id": "cerberus-0-a1b2c3",
    "bypass_type": "privilege_escalation",
    "risk_score": 0.92,
    "bypass_depth": 3,
    "attacker_signature": "user@malicious.com"
})
```

**Response Actions:**
1. Spawn 3 new agents (exponential spawning)
2. Each agent monitors different system section
3. Apply progressive lockdown (stage based on risk + depth)
4. Emit structured audit logs
5. Update agent registry with full lineage

### Anomaly Detection Integration

```python
# Handle anomaly from monitoring system
hydra.on_anomaly({
    "event_id": "anom-001",
    "timestamp": datetime.now().isoformat(),
    "anomaly_type": "unusual_data_access",
    "severity": "high",  # low, medium, high, critical
    "details": {
        "source": "192.168.1.50",
        "resource": "/admin/config",
        "attempts": 10
    }
})

# High/critical anomalies automatically trigger agent spawning
```

### Query Agent Status

```python
# Get all active agents
agents = hydra.get_agents(generation=1, status="active")

# Get specific agent
agent = hydra.agents["cerberus-1-x1y2z3"]
print(f"Agent: {agent.programming_language_name} / {agent.human_language_name}")
print(f"Locked section: {agent.locked_section}")
print(f"PID: {agent.pid}")

# Get bypass history
bypasses = hydra.bypass_events[-10:]  # Last 10 bypasses
for event in bypasses:
    print(f"Event {event.event_id}: {event.bypass_type} at stage {event.lockdown_stage}")
```

### Get System Statistics

```python
stats = hydra.get_statistics()
print(f"""
Cerberus Hydra Statistics:
- Total agents: {stats['total_agents']}
- Active agents: {stats['active_agents']}
- Total bypasses: {stats['total_bypasses']}
- Total spawns: {stats['total_spawns']}
- Avg generation: {stats['average_generation']}
- Languages used: {stats['unique_languages_used']}
- Current lockdown stage: {stats['current_lockdown_stage']}
- Lockdown percentage: {stats['lockdown_percentage']}%
""")
```

### Persist and Load State

```python
# State automatically persisted after each spawn/bypass
# Manual save:
hydra._save_state()

# State stored in: data/cerberus/registry/state.json
# Restored automatically on next initialization
```

---

## Security Patterns

### 1. Language Diversity Enforcement

**Rolling Window Tracking:**
```python
LANGUAGE_DIVERSITY_WINDOW = 20  # Track last N agents

# Prevents language clustering - ensures diverse implementations
recent_languages: deque = deque(maxlen=20)

# On each spawn, check diversity and prefer unused languages
```

### 2. Deterministic Language Selection

**Seeded by Incident ID:**
```python
# Same incident ID = same language selection order (reproducible)
seed = int(hashlib.sha256(incident_id.encode()).hexdigest()[:8], 16)
random.seed(seed)

# Enables forensic replay and audit trail analysis
```

### 3. Safe Template Rendering

**Injection Prevention:**
```python
from app.core.cerberus_template_renderer import TemplateRenderer

renderer = TemplateRenderer()

# Safe variable substitution - no arbitrary code execution
agent_code = renderer.render_agent_template(
    language="python",
    human_language="en",
    variables={
        "agent_id": agent_id,
        "locked_section": section,
        "monitoring_rules": rules
    }
)

# Blocks: eval(), exec(), __import__, subprocess in templates
```

### 4. Resource Exhaustion Prevention

**Hard Caps:**
```python
# Max concurrent agents (default: 50)
if len(active_agents) >= self.max_agents:
    logger.warning("Max agents reached, skipping spawn")
    return None

# Max generation depth (default: 5)
if generation >= 5:
    logger.warning("Max generation depth reached")
    return None
```

### 5. Process Isolation

**Each Agent Runs in Separate Process:**
```python
from app.core.cerberus_agent_process import AgentProcess

process = AgentProcess(
    agent_id=agent_id,
    runtime_path=runtime.exec_path,  # e.g., 'python3'
    script_path=agent_file,
    log_dir="data/cerberus/logs"
)

# Spawn isolated process
process.spawn(timeout=10)

# Monitor without blocking main thread
is_running = process.is_running()
output = process.read_output(max_lines=100)

# Terminate gracefully or forcefully
process.terminate(graceful=True, timeout=5)
```

---

## Integration Points

### ASL3Security Integration

```python
# Pass security enforcer for integration
hydra = CerberusHydraDefense(
    security_enforcer=asl3_security
)

# Hydra notifies security enforcer of bypasses
# Security enforcer can trigger hydra spawns
```

### Anomaly Detection Integration

```python
# From monitoring/anomaly detection systems
anomaly_detector.on_anomaly_callback = hydra.on_anomaly

# Automatic spawning on high/critical anomalies
```

### Observability Integration

```python
from app.core.cerberus_observability import CerberusObservability

obs = CerberusObservability(data_dir="data")

# Track agent timelines
obs.start_agent_timeline(agent_id)
obs.add_agent_task(agent_id, {"type": "monitor", "section": "auth"})

# Track incident graphs
obs.start_incident_graph(incident_id)
obs.add_agent_to_incident(incident_id, agent_id, node_data)

# Get SLO metrics
slo_report = obs.get_slo_report()
# Returns: detect_to_lockdown times, false positive rates, containment rates
```

---

## Configuration

### Language Database

**File:** `data/cerberus/languages.json`

```json
{
  "human_languages": {
    "en": {
      "name": "English",
      "alert_prefix": "SECURITY ALERT",
      "agent_spawned": "Defense agent spawned",
      "bypass_detected": "Security bypass detected"
    },
    "ja": {
      "name": "Japanese",
      "alert_prefix": "セキュリティ警告",
      "agent_spawned": "防御エージェントが生成されました",
      "bypass_detected": "セキュリティ侵害が検出されました"
    }
    // ... 48 more languages
  },
  "programming_languages": {
    "python": {
      "name": "Python",
      "executable": "python3",
      "extension": ".py",
      "installed": true
    },
    "rust": {
      "name": "Rust",
      "executable": "cargo run",
      "extension": ".rs",
      "installed": true
    }
    // ... 48 more languages
  }
}
```

### Runtime Configuration

**File:** `data/cerberus/runtimes.json`

```json
{
  "runtimes": {
    "python": {
      "name": "Python",
      "version": "3.11+",
      "exec_path": "python3",
      "category": "interpreted",
      "health_check_cmd": "python3 --version",
      "priority": 10,
      "verified": true
    },
    "rust": {
      "name": "Rust",
      "version": "1.70+",
      "exec_path": "cargo",
      "category": "compiled",
      "health_check_cmd": "cargo --version",
      "priority": 8,
      "verified": true
    }
    // ... 48 more runtimes
  }
}
```

---

## Performance Considerations

### Memory Usage

- **Per Agent:** ~50 MB (varies by language runtime)
- **50 Active Agents:** ~2.5 GB total
- **Process Isolation:** Each agent in separate OS process

### CPU Usage

- **Spawning:** ~100ms per agent (template rendering + process spawn)
- **Monitoring:** Minimal (agents mostly idle waiting for events)
- **Heavy Load:** Max 50 concurrent agents prevents CPU saturation

### Storage

- **Agent Scripts:** ~10 KB per agent × 50 = 500 KB
- **Logs:** ~100 KB per agent per hour
- **State Persistence:** ~20 KB (agent registry JSON)

---

## Audit Logging

### Structured Logs

All events emitted as structured JSON:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "event_type": "bypass_detected",
  "event_id": "bypass-001",
  "agent_id": "cerberus-0-a1b2c3",
  "bypass_type": "authentication_bypass",
  "risk_score": 0.85,
  "bypass_depth": 2,
  "lockdown_stage": 10,
  "spawned_agents": ["cerberus-1-x1y2z3", "cerberus-1-x4y5z6", "cerberus-1-x7y8z9"],
  "attacker_signature": "192.168.1.100"
}
```

### Log Locations

- **Agent Lifecycle:** `data/cerberus/logs/{agent_id}.jsonl`
- **Bypass Events:** `data/cerberus/registry/bypasses.jsonl`
- **System Logs:** Standard Python logging

---

## Testing

### Unit Tests

```bash
pytest tests/test_cerberus_hydra.py -v
```

**Coverage:**
- Agent spawning with language selection
- Bypass detection and response
- Lockdown stage computation
- State persistence and restoration
- Process lifecycle management

### Integration Tests

```bash
pytest tests/test_cerberus_behaviors.py -v
```

**Scenarios:**
- Multi-generation spawning cascade
- Anomaly detection integration
- Runtime verification
- Resource exhaustion prevention

---

## Troubleshooting

### Issue: No Agents Spawning

**Cause:** Runtimes not verified as healthy

**Solution:**
```python
summary = hydra.runtime_manager.verify_runtimes()
print(f"Healthy runtimes: {summary['healthy_runtimes']}")

# Check specific runtime
runtime = hydra.runtime_manager.get_runtime('python')
print(f"Status: {runtime.health_status}")
```

### Issue: Max Agents Reached

**Cause:** Too many concurrent agents

**Solution:**
```python
# Increase limit
hydra = CerberusHydraDefense(max_agents=100)

# Or terminate old agents
for agent_id, agent in list(hydra.agents.items()):
    if agent.status == "active" and agent.generation < 2:
        if agent.process:
            agent.process.terminate()
        agent.status = "terminated"
```

### Issue: Language Database Not Found

**Cause:** Missing `data/cerberus/languages.json`

**Solution:**
```bash
# Generate language database
python scripts/generate_cerberus_languages.py
```

---

## Best Practices

1. **Start Small:** Initialize with 3 agents, scale up as needed
2. **Monitor Resources:** Track CPU/memory usage, set appropriate `max_agents`
3. **Verify Runtimes:** Run health checks at startup to avoid spawn failures
4. **Review Logs:** Analyze bypass patterns in audit logs for threat intelligence
5. **Test Lockdown:** Ensure critical systems have lockdown handlers implemented
6. **Language Diversity:** Let system select languages automatically for maximum diversity
7. **Graceful Degradation:** Handle runtime failures gracefully, fallback to available languages

---


---


---


---

## 📚 Referenced In Relationship Maps

This implementation is referenced in:
- [[relationships/security/01_security_system_overview.md|Security System Overview]]
- [[relationships/security/02_threat_models.md|Threat Models]]
- [[relationships/security/03_defense_layers.md|Defense Layers]]
- [[relationships/security/04_incident_response_chains.md|Incident Response Chains]]
- [[relationships/security/05_cross_system_integrations.md|Cross-System Integrations]]
- [[relationships/security/06_data_flow_diagrams.md|Data Flow Diagrams]]
- [[relationships/security/07_security_metrics.md|Security Metrics]]

---
## Related Security Documentation

- [[source-docs\security\02-lockdown-controller.md|02 lockdown controller]]
- [[source-docs\security\03-runtime-manager.md|03 runtime manager]]
- [[source-docs\security\04-observability-metrics.md|04 observability metrics]]

---
## 📁 Source Code References

This documentation references the following source files:

- [[src/app/core/cerberus_agent_process.py]]
- [[src/app/core/cerberus_hydra.py]]
- [[src/app/core/cerberus_lockdown_controller.py]]
- [[src/app/core/cerberus_observability.py]]
- [[src/app/core/cerberus_runtime_manager.py]]
- [[src/app/core/cerberus_template_renderer.py]]
- [[src/app/core/security/auth.py]]
- [[utils/encryption/god_tier_encryption.py]]

---

---

## 🔗 Relationship Maps

This component is documented in the following relationship maps:
- [[relationships/security/01_security_system_overview.md|Security System Overview]]
- [[relationships/security/03_defense_layers.md|Defense Layers]]
- [[relationships/security/05_cross_system_integrations.md|Cross-System Integrations]]

---

---

## 📚 Referenced In Relationship Maps

This implementation is referenced in:
- [[relationships/security/01_security_system_overview.md|Security System Overview]]
- [[relationships/security/02_threat_models.md|Threat Models]]
- [[relationships/security/03_defense_layers.md|Defense Layers]]
- [[relationships/security/04_incident_response_chains.md|Incident Response Chains]]
- [[relationships/security/05_cross_system_integrations.md|Cross-System Integrations]]
- [[relationships/security/06_data_flow_diagrams.md|Data Flow Diagrams]]
- [[relationships/security/07_security_metrics.md|Security Metrics]]

---
## Related Documentation

- [02-lockdown-controller.md](02-lockdown-controller.md) - Progressive lockdown system
- [03-runtime-manager.md](03-runtime-manager.md) - Multi-language runtime health
- [04-observability-metrics.md](04-observability-metrics.md) - Telemetry and SLO tracking
- [05-security-monitoring.md](05-security-monitoring.md) - CloudWatch and SNS integration
- [06-agent-security.md](06-agent-security.md) - Agent encapsulation and protection
- [07-data-validation.md](07-data-validation.md) - Secure data parsing and validation
- [08-contrarian-firewall.md](08-contrarian-firewall.md) - Monolithic orchestration kernel

---

## See Also

- [Cerberus Hydra White Paper](../../docs/CERBERUS_HYDRA_WHITEPAPER.md)
- [Security Architecture Overview](../../PROGRAM_SUMMARY.md#security-architecture)
- [Governance Integration](../core/governance-system.md)
