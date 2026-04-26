# Agent Security and Encapsulation

## Overview

Agent security module provides secure agent state management, numerical protections, runtime fuzzing, and memory isolation for hostile plugins. It implements defense-in-depth for adversarial control scenarios.

**Location:** `src/app/security/agent_security.py` (469 lines)

**Core Philosophy:** Defense-in-depth for agents operating in adversarial environments.

---

## Architecture

### Components

1. **AgentEncapsulation** - Secure state management with access control
2. **NumericalProtection** - Bounds checking for numerical operations
3. **PluginIsolation** - Memory isolation via multiprocessing
4. **RuntimeFuzzer** - Input fuzzing for resilience testing

---

## API Reference

### Agent Encapsulation

```python
from app.security.agent_security import AgentEncapsulation

# Initialize agent encapsulation
agent_enc = AgentEncapsulation(agent_id="agent-001")

# Set state with access control
agent_enc.set_state("confidence", 0.92, caller="inference_engine")
agent_enc.set_state("last_action", "monitor", caller="controller")

# Get state
confidence = agent_enc.get_state("confidence", caller="dashboard")

# Set permissions
agent_enc.set_permissions(
    read=True,
    write=True,
    execute=False  # Disabled by default
)

# Audit access log
access_log = agent_enc.get_access_log()
for entry in access_log[-10:]:
    print(f"{entry['timestamp']}: {entry['operation']} {entry['key']} by {entry['caller']}")
```

**Use Cases:**
- Prevent unauthorized state modification
- Track who accessed agent state
- Audit trail for compliance
- Isolation between agent components

### Numerical Protection

```python
from app.security.agent_security import NumericalProtection
import numpy as np

num_protect = NumericalProtection()

# Clip array to safe bounds
data = np.array([1e10, -1e10, 100, -200, 0])
safe_data = num_protect.clip_array(data, min_val=-1e6, max_val=1e6)
# Result: [1e6, -1e6, 100, -200, 0]

# Remove outliers using Z-score
data = np.array([1, 2, 3, 4, 5, 1000])  # 1000 is outlier
clean_data = num_protect.remove_outliers(data, threshold=3.0)
# Result: [1, 2, 3, 4, 5]  # 1000 removed

# Safe division (handles divide-by-zero)
numerator = np.array([10, 20, 30])
denominator = np.array([2, 0, 5])  # Contains zero
result = num_protect.safe_divide(numerator, denominator, default=0.0)
# Result: [5.0, 0.0, 6.0]  # Zero division → default

# Validate numerical input
is_valid = num_protect.validate_numerical_input([1, 2, 3, 4, 5])  # True
is_valid = num_protect.validate_numerical_input([1, 2, np.inf, 4])  # False (inf)
is_valid = num_protect.validate_numerical_input([1, 2, np.nan, 4])  # False (nan)
```

**Protection Features:**
- **Clipping:** Prevent overflow/underflow with bounds
- **Outlier Detection:** Remove statistical outliers
- **Zero Division:** Safe division with default fallback
- **Input Validation:** Detect NaN, Inf, out-of-bounds

### Plugin Isolation

```python
from app.security.agent_security import PluginIsolation

plugin_iso = PluginIsolation(timeout=30)  # 30 second timeout

# Define plugin function
def untrusted_plugin(data):
    """Untrusted plugin code - runs in isolated process"""
    # Potentially malicious code here
    result = process_data(data)
    return result

# Execute in isolated process
try:
    result = plugin_iso.execute_isolated(
        plugin_func=untrusted_plugin,
        args=([1, 2, 3, 4, 5],),
        kwargs={"option": "fast"}
    )
    print(f"Plugin result: {result}")
    
except TimeoutError:
    print("Plugin execution timed out - killed")
    
except RuntimeError as e:
    print(f"Plugin execution failed: {e}")
```

**Isolation Guarantees:**
- Separate process (memory isolation)
- Timeout enforcement (prevent infinite loops)
- Exception handling (crashes don't affect main process)
- Resource limits (via OS process limits)

**Use Cases:**
- Execute untrusted AI model code
- Run third-party plugins safely
- Test potentially buggy code
- Prevent memory corruption attacks

### Runtime Fuzzer

```python
from app.security.agent_security import RuntimeFuzzer

fuzzer = RuntimeFuzzer()

# Fuzz string inputs
base_input = "test"
fuzz_cases = fuzzer.fuzz_input(strategy="random_string", base_input=base_input)

print(f"Generated {len(fuzz_cases)} fuzz cases:")
for case in fuzz_cases[:5]:
    print(f"  - {repr(case[:50])}")

# Fuzz boundary values
fuzz_cases = fuzzer.fuzz_input(strategy="boundary_values", base_input=0)
# Returns: [0, -1, 1, 2^31-1, -2^31, 2^63-1, -2^63, inf, -inf, nan]

# Fuzz type confusion
fuzz_cases = fuzzer.fuzz_input(strategy="type_confusion", base_input="test")
# Returns: [None, True, False, 0, "", [], {}, set(), lambda x: x]

# Fuzz overflow
fuzz_cases = fuzzer.fuzz_input(strategy="overflow", base_input=[])
# Returns: [list(10000 items), dict(1000 items), string(1MB)]

# Test function resilience
def vulnerable_function(input_data):
    return len(input_data)

for strategy in ["random_string", "boundary_values", "type_confusion", "overflow"]:
    fuzz_cases = fuzzer.fuzz_input(strategy, base_input="test")
    
    for case in fuzz_cases:
        try:
            result = vulnerable_function(case)
        except Exception as e:
            print(f"FOUND BUG: {strategy} - {type(e).__name__}: {e}")
```

**Fuzzing Strategies:**
- **random_string:** Generate edge-case strings (empty, long, unicode, special chars)
- **boundary_values:** Test numeric boundaries (0, -1, max int, inf, nan)
- **type_confusion:** Test with unexpected types (None, bool, function)
- **overflow:** Test with large data structures (10K list, 1MB string)

---

## Integration Patterns

### Cerberus Agent Integration

```python
from app.core.cerberus_hydra import CerberusHydraDefense
from app.security.agent_security import AgentEncapsulation, NumericalProtection

class SecureAgent:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.encapsulation = AgentEncapsulation(agent_id)
        self.num_protect = NumericalProtection()
        
    def set_confidence(self, confidence, caller):
        # Validate numerical input
        if not self.num_protect.validate_numerical_input(confidence):
            raise ValueError("Invalid confidence value")
        
        # Clip to valid range [0, 1]
        confidence = np.clip(confidence, 0.0, 1.0)
        
        # Set with access control
        self.encapsulation.set_state("confidence", float(confidence), caller=caller)
    
    def process_sensor_data(self, sensor_readings):
        # Clip sensor readings to safe bounds
        safe_readings = self.num_protect.clip_array(
            np.array(sensor_readings),
            min_val=-1000,
            max_val=1000
        )
        
        # Remove outliers
        clean_readings = self.num_protect.remove_outliers(safe_readings)
        
        # Process clean data
        return np.mean(clean_readings)
```

### AI Model Input Validation

```python
from app.security.agent_security import NumericalProtection

num_protect = NumericalProtection()

def safe_model_inference(model, input_data):
    """Validate inputs before model inference"""
    
    # Validate numerical input
    if not num_protect.validate_numerical_input(input_data):
        raise ValueError("Invalid model input: contains NaN or Inf")
    
    # Clip to expected range
    safe_input = num_protect.clip_array(
        np.array(input_data),
        min_val=-10.0,
        max_val=10.0
    )
    
    # Run inference
    output = model.predict(safe_input)
    
    # Validate output
    if not num_protect.validate_numerical_input(output):
        raise RuntimeError("Model produced invalid output")
    
    return output
```

### Plugin System Integration

```python
from app.security.agent_security import PluginIsolation

class PluginManager:
    def __init__(self):
        self.isolation = PluginIsolation(timeout=60)
        self.plugins = {}
    
    def register_plugin(self, name, plugin_func):
        self.plugins[name] = plugin_func
    
    def execute_plugin(self, name, *args, **kwargs):
        if name not in self.plugins:
            raise ValueError(f"Plugin {name} not found")
        
        plugin_func = self.plugins[name]
        
        # Execute in isolated process
        try:
            result = self.isolation.execute_isolated(
                plugin_func=plugin_func,
                args=args,
                kwargs=kwargs
            )
            return {"success": True, "result": result}
            
        except TimeoutError:
            return {"success": False, "error": "Plugin timeout"}
            
        except RuntimeError as e:
            return {"success": False, "error": str(e)}
```

---

## Security Patterns

### 1. Layered Validation

```python
def secure_data_processing(data):
    """Multi-layer validation for critical operations"""
    
    # Layer 1: Type validation
    if not isinstance(data, (list, np.ndarray)):
        raise TypeError("Data must be list or array")
    
    data = np.array(data)
    
    # Layer 2: Numerical validation
    num_protect = NumericalProtection()
    if not num_protect.validate_numerical_input(data):
        raise ValueError("Data contains invalid values")
    
    # Layer 3: Bounds checking
    data = num_protect.clip_array(data, min_val=-1e6, max_val=1e6)
    
    # Layer 4: Outlier removal
    data = num_protect.remove_outliers(data, threshold=3.0)
    
    # Layer 5: Statistical validation
    if np.std(data) > 1000:
        raise ValueError("Data variance too high")
    
    # Safe to process
    return process_validated_data(data)
```

### 2. Fail-Safe Defaults

```python
def safe_get_agent_state(agent_enc, key, default=None):
    """Get agent state with fail-safe default"""
    try:
        return agent_enc.get_state(key, caller="system")
    except (KeyError, PermissionError):
        return default

# Usage
confidence = safe_get_agent_state(agent_enc, "confidence", default=0.5)
```

### 3. Timeout Everything

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    """Context manager for operation timeout"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds}s")
    
    # Set signal handler
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        signal.alarm(0)  # Cancel alarm

# Usage
try:
    with timeout(10):
        result = potentially_slow_operation()
except TimeoutError:
    result = None
    logger.warning("Operation timed out, using default")
```

### 4. Audit All Access

```python
def audit_wrapper(func):
    """Decorator to audit all state access"""
    def wrapper(self, key, caller, *args, **kwargs):
        # Log access attempt
        logger.info(f"State access: {caller} -> {func.__name__}({key})")
        
        try:
            result = func(self, key, caller, *args, **kwargs)
            logger.info(f"State access succeeded: {caller} -> {key}")
            return result
        except Exception as e:
            logger.error(f"State access failed: {caller} -> {key}: {e}")
            raise
    
    return wrapper

# Apply to all state access methods
class AuditedAgentEncapsulation(AgentEncapsulation):
    @audit_wrapper
    def get_state(self, key, caller):
        return super().get_state(key, caller)
    
    @audit_wrapper
    def set_state(self, key, value, caller):
        return super().set_state(key, value, caller)
```

---

## Testing and Validation

### Fuzz Testing Framework

```python
from app.security.agent_security import RuntimeFuzzer

fuzzer = RuntimeFuzzer()

def fuzz_test_function(target_func, strategies=None):
    """Comprehensive fuzz testing"""
    strategies = strategies or ["random_string", "boundary_values", "type_confusion", "overflow"]
    
    bugs_found = []
    
    for strategy in strategies:
        fuzz_cases = fuzzer.fuzz_input(strategy, base_input="test")
        
        for i, case in enumerate(fuzz_cases):
            try:
                result = target_func(case)
            except Exception as e:
                bugs_found.append({
                    "strategy": strategy,
                    "case_index": i,
                    "input": repr(case)[:100],
                    "exception": type(e).__name__,
                    "message": str(e)
                })
    
    return bugs_found

# Test agent functions
bugs = fuzz_test_function(agent.process_input)

if bugs:
    print(f"Found {len(bugs)} bugs:")
    for bug in bugs:
        print(f"  - {bug['strategy']}: {bug['exception']} with input {bug['input']}")
```

### Unit Tests

```bash
pytest tests/test_agent_security.py -v
```

**Coverage:**
- AgentEncapsulation (state access, permissions, audit log)
- NumericalProtection (clipping, outliers, validation)
- PluginIsolation (timeout, isolation, exception handling)
- RuntimeFuzzer (all fuzzing strategies)

---

## Performance Considerations

### Memory Overhead

- **AgentEncapsulation:** ~10 KB per agent (state + access log)
- **NumericalProtection:** Negligible (stateless)
- **PluginIsolation:** ~50 MB per isolated process
- **RuntimeFuzzer:** ~1 KB (strategy functions)

### Optimization Tips

```python
# 1. Reuse NumericalProtection instances
num_protect = NumericalProtection()  # Create once
# Use repeatedly for all validations

# 2. Limit access log size
if len(agent_enc._access_log) > 1000:
    agent_enc._access_log = agent_enc._access_log[-1000:]

# 3. Use in-place NumPy operations
data = np.clip(data, -1e6, 1e6)  # In-place clipping

# 4. Batch plugin executions
# Execute multiple plugins in parallel processes
```

---

## Best Practices

1. **Validate Everything:** Never trust input data, always validate
2. **Clip Numerics:** Use clipping for all external numerical inputs
3. **Isolate Untrusted Code:** Use PluginIsolation for third-party code
4. **Fuzz Critical Functions:** Regularly fuzz-test agent functions
5. **Audit State Access:** Log all agent state modifications
6. **Set Timeouts:** Always set timeouts for potentially slow operations
7. **Remove Outliers:** Clean sensor/external data before processing
8. **Fail Safe:** Provide safe defaults for all operations

---


---

## 📁 Source Code References

This documentation references the following source files:

- [[src/app/core/cerberus_hydra.py]]

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

- [01-cerberus-hydra-defense.md](01-cerberus-hydra-defense.md) - Secure agent spawning
- [07-data-validation.md](07-data-validation.md) - Input validation and parsing
- [08-contrarian-firewall.md](08-contrarian-firewall.md) - System-level security

---

## See Also

- [Agent Security Best Practices](../../docs/AGENT_SECURITY.md)
- [Adversarial Defense Strategies](../../docs/ADVERSARIAL_DEFENSE.md)
- [Fuzzing Guide](../../docs/FUZZING_GUIDE.md)
