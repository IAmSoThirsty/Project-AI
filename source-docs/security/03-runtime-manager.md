# Runtime Manager - Multi-Language Runtime Health Verification

## Overview

The Runtime Manager handles runtime verification, health checks, and selection for Cerberus agents across 50+ programming language runtimes. It enables deterministic runtime selection with bias toward verified, healthy runtimes.

**Location:** [[src/app/core/cerberus_runtime_manager.py]] (`src/app/core/cerberus_runtime_manager.py`) (331 lines)

**Core Philosophy:** Verify before use, select intelligently, fail gracefully.

---

## Architecture

### Data Structures

```python
@dataclass
class RuntimeDescriptor:
    """Complete runtime metadata for agent execution"""
    language_key: str           # e.g., 'python', 'rust'
    name: str                   # e.g., 'Python', 'Rust'
    version: str                # e.g., '3.11+', '1.70+'
    exec_path: str              # e.g., 'python3', 'cargo'
    category: str               # interpreted, compiled, script
    health_check_cmd: str       # e.g., 'python3 --version'
    priority: int               # 1-10 (higher = preferred)
    verified: bool              # Manually verified runtime
    health_status: str          # healthy, degraded, unavailable
```

---

## API Reference

### Initialization

```python
from app.core.cerberus_runtime_manager import RuntimeManager

runtime_mgr = RuntimeManager(data_dir="data")

# Auto-loads from: data/cerberus/runtimes.json
# Creates fallback Python runtime if file missing
```

### Verify Runtime Health

```python
# Verify all runtimes at startup
summary = runtime_mgr.verify_runtimes(timeout=5)

print(f"""
Runtime Verification:
- Total runtimes: {summary['total_runtimes']}
- Healthy: {summary['healthy']}
- Degraded: {summary['degraded']}
- Unavailable: {summary['unavailable']}
- Healthy runtimes: {summary['healthy_runtimes']}
""")

# Example output:
# Total runtimes: 50
# Healthy: 12  (python, javascript, rust, go, java, ruby, ...)
# Degraded: 3  (haskell, erlang, prolog)
# Unavailable: 35  (not installed on system)
```

**Health Status:**
- **healthy:** Runtime available, health check passed (exit code 0)
- **degraded:** Runtime available, health check failed (exit code ≠ 0)
- **unavailable:** Runtime not found or timeout

### Get Runtime by Language

```python
# Get specific runtime
runtime = runtime_mgr.get_runtime('python')

print(f"""
Runtime: {runtime.name}
Version: {runtime.version}
Executable: {runtime.exec_path}
Category: {runtime.category}
Health: {runtime.health_status}
Priority: {runtime.priority}
Verified: {runtime.verified}
""")

# None if not found
unknown_runtime = runtime_mgr.get_runtime('nonexistent')  # None
```

### Select Random Runtime

```python
# Select with bias toward verified/healthy runtimes
runtime = runtime_mgr.get_random_runtime(
    category='interpreted',    # Optional: filter by category
    prefer_verified=True,      # Bias toward verified runtimes
    seed=12345                 # Optional: deterministic selection
)

# Weighting algorithm:
# - Base weight: 1
# - +3 if verified
# - +2 if healthy
# - +1 if degraded
# - +0 if unavailable

# Example: Verified + healthy runtime has weight 6 (1+3+2)
#          Unverified + unavailable has weight 1
```

**Categories:**
- **interpreted:** Python, Ruby, PHP, Perl, JavaScript, Lua
- **compiled:** Rust, Go, C, C++, Java, C#, Haskell
- **script:** Bash, PowerShell, AWK, Sed

### Get All Runtimes

```python
# Get all runtimes
all_runtimes = runtime_mgr.get_all_runtimes()

# Filter by health status
healthy_runtimes = runtime_mgr.get_all_runtimes(health_status='healthy')
degraded_runtimes = runtime_mgr.get_all_runtimes(health_status='degraded')
unavailable_runtimes = runtime_mgr.get_all_runtimes(health_status='unavailable')
```

### Health Summary

```python
summary = runtime_mgr.get_health_summary()

print(f"""
Health Summary:
- Total runtimes: {summary['total_runtimes']}
- By status:
  - Healthy: {summary['by_status']['healthy']}
  - Degraded: {summary['by_status']['degraded']}
  - Unavailable: {summary['by_status']['unavailable']}
  - Unknown: {summary['by_status']['unknown']}
- By category:
  - Interpreted: {summary['by_category']['interpreted']}
  - Compiled: {summary['by_category']['compiled']}
  - Script: {summary['by_category']['script']}
- Verified runtimes: {summary['verified_count']}
""")
```

---

## Runtime Configuration

### Configuration File

**Location:** `data/cerberus/runtimes.json`

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
    "javascript": {
      "name": "JavaScript (Node.js)",
      "version": "18+",
      "exec_path": "node",
      "category": "interpreted",
      "health_check_cmd": "node --version",
      "priority": 9,
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
    },
    "go": {
      "name": "Go",
      "version": "1.20+",
      "exec_path": "go",
      "category": "compiled",
      "health_check_cmd": "go version",
      "priority": 8,
      "verified": true
    },
    "ruby": {
      "name": "Ruby",
      "version": "3.0+",
      "exec_path": "ruby",
      "category": "interpreted",
      "health_check_cmd": "ruby --version",
      "priority": 7,
      "verified": false
    }
    // ... 45 more runtimes
  }
}
```

### Generate Runtimes Configuration

```bash
# Generate complete runtimes.json with 50+ languages
python scripts/generate_cerberus_languages.py
```

---

## Security Features

### Command Injection Prevention

```python
# Validates health check commands using regex
allowed_pattern = re.compile(r'^[a-zA-Z0-9\s\-_./|\'\"]+$')

if not allowed_pattern.match(cmd_str):
    logger.warning("Invalid characters in health check command")
    runtime.health_status = "unavailable"
    continue

# Always use shell=False with subprocess.run()
result = subprocess.run(
    cmd_list,           # List, not string
    shell=False,        # Prevent shell injection
    capture_output=True,
    timeout=timeout,
    text=True
)
```

### Timeout Protection

```python
# Each health check has timeout (default: 5s)
try:
    result = subprocess.run(
        cmd_list,
        shell=False,
        capture_output=True,
        timeout=5,  # Hard timeout
        text=True
    )
except subprocess.TimeoutExpired:
    runtime.health_status = "unavailable"
    logger.warning("Runtime health check timed out")
```

---

## Integration Patterns

### Cerberus Hydra Integration

```python
from app.core.cerberus_hydra import CerberusHydraDefense

hydra = CerberusHydraDefense(data_dir="data")

# Hydra uses runtime_manager internally
# Verify runtimes at startup
hydra._verify_runtimes()

# Select runtime for new agent
runtime = hydra.runtime_manager.get_random_runtime(
    prefer_verified=True,
    seed=agent_seed
)

# Use runtime to spawn agent
agent_process = AgentProcess(
    agent_id=agent_id,
    runtime_path=runtime.exec_path,
    script_path=agent_file
)
```

### Pre-Flight Runtime Checks

```python
def spawn_agent(language_key: str):
    """Spawn agent with runtime validation"""
    runtime = runtime_mgr.get_runtime(language_key)
    
    if not runtime:
        raise RuntimeError(f"Runtime {language_key} not found")
    
    if runtime.health_status == 'unavailable':
        raise RuntimeError(f"Runtime {language_key} unavailable")
    
    if runtime.health_status == 'degraded':
        logger.warning(f"Runtime {language_key} degraded, may fail")
    
    # Spawn with validated runtime
    process = AgentProcess(
        agent_id=f"agent-{uuid.uuid4().hex[:8]}",
        runtime_path=runtime.exec_path,
        script_path=generate_script(language_key)
    )
    process.spawn()
```

### Fallback Strategy

```python
def spawn_with_fallback(preferred_language: str):
    """Try preferred language, fallback to alternatives"""
    runtime = runtime_mgr.get_runtime(preferred_language)
    
    if runtime and runtime.health_status == 'healthy':
        return spawn_agent_with_runtime(runtime)
    
    # Fallback to any healthy runtime
    logger.warning(f"Preferred runtime {preferred_language} unavailable, selecting fallback")
    
    healthy_runtimes = runtime_mgr.get_all_runtimes(health_status='healthy')
    if not healthy_runtimes:
        raise RuntimeError("No healthy runtimes available")
    
    fallback = random.choice(healthy_runtimes)
    logger.info(f"Using fallback runtime: {fallback.name}")
    
    return spawn_agent_with_runtime(fallback)
```

---

## 50+ Supported Runtimes

### Interpreted Languages (Category: interpreted)

1. **Python** - `python3 --version`
2. **JavaScript (Node.js)** - `node --version`
3. **Ruby** - `ruby --version`
4. **PHP** - `php --version`
5. **Perl** - `perl --version`
6. **Lua** - `lua -v`
7. **R** - `Rscript --version`
8. **Julia** - `julia --version`

### Compiled Languages (Category: compiled)

9. **Rust** - `cargo --version`
10. **Go** - `go version`
11. **C** - `gcc --version`
12. **C++** - `g++ --version`
13. **C#** - `dotnet --version`
14. **Java** - `java -version`
15. **Kotlin** - `kotlinc -version`
16. **Swift** - `swift --version`
17. **Scala** - `scalac -version`
18. **Haskell** - `ghc --version`
19. **OCaml** - `ocaml -version`
20. **F#** - `fsharpc --version`
21. **Nim** - `nim --version`
22. **Crystal** - `crystal --version`
23. **Zig** - `zig version`
24. **D** - `dmd --version`
25. **Fortran** - `gfortran --version`
26. **Ada** - `gnatmake --version`
27. **Pascal** - `fpc -version`

### Scripting Languages (Category: script)

28. **Bash** - `bash --version`
29. **PowerShell** - `pwsh --version`
30. **Tcl** - `tclsh --version`
31. **AWK** - `awk --version`
32. **Sed** - `sed --version`

### Functional Languages

33. **Elixir** - `elixir --version`
34. **Erlang** - `erl -version`
35. **Clojure** - `clojure -version`
36. **Scheme** - `scheme --version`
37. **Racket** - `racket --version`
38. **Common Lisp** - `sbcl --version`

### Specialized Languages

39. **SQL** - `sqlite3 --version`
40. **Dart** - `dart --version`
41. **Groovy** - `groovy --version`
42. **MATLAB** - `matlab -batch "version"`
43. **Octave** - `octave --version`
44. **Assembly (x86)** - `nasm --version`
45. **VHDL** - `ghdl --version`
46. **Verilog** - `iverilog -V`
47. **Prolog** - `swipl --version`
48. **Smalltalk** - `gst --version`
49. **COBOL** - `cobc --version`
50. **TypeScript** - `tsc --version`

---

## Performance Considerations

### Startup Time

- **Runtime Verification:** ~5-10 seconds (parallel checks with 5s timeout)
- **Configuration Loading:** <100ms (JSON parse)
- **First Health Check:** Synchronous at startup
- **Subsequent Checks:** Cache health status, re-verify periodically

### Optimization Strategies

```python
# 1. Skip unavailable runtimes on subsequent checks
healthy_or_degraded = runtime_mgr.get_all_runtimes(health_status='healthy')
healthy_or_degraded.extend(runtime_mgr.get_all_runtimes(health_status='degraded'))

# Only re-check these runtimes
for runtime in healthy_or_degraded:
    verify_single_runtime(runtime)

# 2. Cache health status for 5 minutes
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def get_cached_health(language_key, timestamp):
    return runtime_mgr.get_runtime(language_key).health_status

# Use current time rounded to 5 min intervals
current_interval = int(time.time() / 300)
health = get_cached_health('python', current_interval)
```

---

## Troubleshooting

### Issue: All Runtimes Show as Unavailable

**Cause:** Runtimes not installed or not in PATH

**Solution:**
```bash
# Check which runtimes are installed
which python3  # /usr/bin/python3
which node     # /usr/local/bin/node
which cargo    # /home/user/.cargo/bin/cargo

# Add to PATH if needed
export PATH="/usr/local/bin:/home/user/.cargo/bin:$PATH"

# Or update runtimes.json with full paths
{
  "python": {
    "exec_path": "/usr/bin/python3",
    ...
  }
}
```

### Issue: Health Check Timeout

**Cause:** Slow runtime initialization or system load

**Solution:**
```python
# Increase timeout
summary = runtime_mgr.verify_runtimes(timeout=10)

# Or skip slow runtimes
# Mark as verified=false in runtimes.json
```

### Issue: Command Injection Warning

**Cause:** Invalid characters in health_check_cmd

**Solution:**
```json
// Use only allowed characters: a-zA-Z0-9\s\-_./|'\"
{
  "ruby": {
    "health_check_cmd": "ruby --version"  // ✓ Valid
  },
  "malicious": {
    "health_check_cmd": "ruby --version; rm -rf /"  // ✗ Rejected
  }
}
```

---

## Best Practices

1. **Verify at Startup:** Always run `verify_runtimes()` before spawning agents
2. **Use Verified Runtimes:** Set `verified=true` for manually tested runtimes
3. **Fallback Strategy:** Always have 2-3 healthy runtimes as fallback
4. **Monitor Health:** Periodically re-verify runtime health (every 5-10 minutes)
5. **Cache Results:** Cache health status to avoid repeated checks
6. **Graceful Degradation:** Allow agents to spawn even if preferred runtime unavailable
7. **Full Paths:** Use absolute paths in `exec_path` for production deployments

---


---

## 📁 Source Code References

This documentation references the following source files:

- [[src/app/core/cerberus_hydra.py]]
- [[src/app/core/cerberus_runtime_manager.py]]

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

- [01-cerberus-hydra-defense.md](01-cerberus-hydra-defense.md) - Uses RuntimeManager for agent spawning
- [03-agent-process-manager.md](03-agent-process-manager.md) - Uses runtime descriptors for spawning
- [04-observability-metrics.md](04-observability-metrics.md) - Runtime health metrics

---

## See Also

- [Multi-Language Support Design](../../docs/MULTI_LANGUAGE_SUPPORT.md)
- [Cerberus Agent Templates](../../data/cerberus/agent_templates/)
- [Runtime Installation Guide](../../docs/RUNTIME_SETUP.md)
