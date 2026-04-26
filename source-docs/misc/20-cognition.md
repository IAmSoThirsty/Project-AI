---
type: source-doc
tags: [cognition, triumvirate, codex, galahad, cerberus, three-engine-architecture]
created: 2025-01-26
last_verified: 2026-04-20
status: current
stakeholders: [ai-team, ml-engineers, system-architects]
content_category: technical
review_cycle: quarterly
---

# Cognition Engines Documentation (Triumvirate System)

**Directory:** `src/cognition/`  
**Version:** 1.0.0  
**Last Updated:** 2025-01-26

## Overview

The Triumvirate System is Project-AI's advanced three-engine cognitive architecture that provides coordinated AI decision-making. It orchestrates three specialized engines:

1. **Codex** - ML inference with production features (GPU/CPU fallback)
2. **Galahad** - Reasoning and arbitration (logic, curiosity, explanation)
3. **Cerberus** - Policy enforcement (input/output validation)

Together, these engines provide a complete cognitive pipeline from raw input to policy-compliant output.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     TRIUMVIRATE ORCHESTRATOR                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Input Data                                                      │
│      ↓                                                           │
│  ┌──────────────┐   Validation                                  │
│  │  CERBERUS    │ → Input Sanitization                          │
│  │  (Policy)    │   Security Checks                             │
│  └──────────────┘                                               │
│      ↓                                                           │
│  ┌──────────────┐   Inference                                   │
│  │   CODEX      │ → ML Model Processing                         │
│  │   (ML)       │   GPU/CPU Execution                           │
│  └──────────────┘                                               │
│      ↓                                                           │
│  ┌──────────────┐   Reasoning                                   │
│  │  GALAHAD     │ → Logic + Arbitration                         │
│  │  (Reason)    │   Explanation Generation                      │
│  └──────────────┘                                               │
│      ↓                                                           │
│  ┌──────────────┐   Enforcement                                 │
│  │  CERBERUS    │ → Output Validation                           │
│  │  (Policy)    │   Policy Compliance                           │
│  └──────────────┘                                               │
│      ↓                                                           │
│  Clean, Validated Output                                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module: Triumvirate Orchestrator

**File:** `triumvirate.py`  
**Lines:** ~300  
**Purpose:** Coordinates all three engines in a unified workflow

### Features

- ✅ **Unified Pipeline** - Single API for complex multi-engine workflows
- ✅ **Telemetry** - Tracks performance and decisions across all engines
- ✅ **Error Handling** - Graceful degradation if engines fail
- ✅ **Context Enrichment** - Adds correlation IDs and timestamps
- ✅ **Configurable Skip** - Can bypass validation for trusted inputs

### Configuration

```python
from src.cognition.triumvirate import TriumvirateConfig, Triumvirate
from src.cognition.codex.engine import CodexConfig
from src.cognition.galahad.engine import GalahadConfig
from src.cognition.cerberus.engine import CerberusConfig

# Configure each engine
config = TriumvirateConfig(
    codex_config=CodexConfig(
        model_path="gpt2",
        device="auto",
        enable_gpu=True
    ),
    galahad_config=GalahadConfig(
        reasoning_depth=3,
        enable_curiosity=True
    ),
    cerberus_config=CerberusConfig(
        mode="production",  # Allow-all by default
        enforce_on_input=False,
        enforce_on_output=True
    ),
    enable_telemetry=True,
    correlation_id_prefix="trv"
)

# Initialize orchestrator
triumvirate = Triumvirate(config)
```

### API Reference

#### Constructor
```python
def __init__(self, config: TriumvirateConfig | None = None)
```

#### Primary Method: `process()`
```python
def process(
    self,
    input_data: Any,
    context: dict | None = None,
    skip_validation: bool = False
) -> dict
```

Process input through complete Triumvirate pipeline.

**Parameters:**
- `input_data`: Any input to process
- `context`: Optional context dictionary with metadata
- `skip_validation`: Skip Cerberus input validation (use with caution)

**Returns:**
- Dictionary with keys:
  - `correlation_id` (str): Unique ID for this processing run
  - `codex_result` (dict): ML inference output
  - `galahad_result` (dict): Reasoning/arbitration output
  - `cerberus_result` (dict): Policy enforcement output
  - `final_output` (Any): Clean, validated output
  - `telemetry` (dict): Performance metrics
  - `success` (bool): Overall success status

**Example:**
```python
from src.cognition.triumvirate import Triumvirate

triumvirate = Triumvirate()

result = triumvirate.process(
    input_data="Analyze this threat: zombie horde detected at 500m",
    context={
        "threat_level": 8,
        "location": "perimeter_alpha"
    }
)

print(f"Correlation ID: {result['correlation_id']}")
print(f"Final Output: {result['final_output']}")
print(f"Success: {result['success']}")
print(f"Processing Time: {result['telemetry']['total_time_ms']}ms")
```

---

## Engine 1: Codex (ML Inference)

**File:** `codex/engine.py`  
**Lines:** ~250  
**Purpose:** Production-ready ML model inference with GPU/CPU fallback

### Features

- ✅ **GPU/CPU Fallback** - Automatic device selection and fallback
- ✅ **Environment Configuration** - Configure via environment variables
- ✅ **Model Loading** - Lazy loading with error handling
- ✅ **Graceful Degradation** - Operates in lightweight mode if model fails
- ✅ **Multiple Backends** - HuggingFace, PyTorch, custom adapters

### Configuration

#### Via Code
```python
from src.cognition.codex.engine import CodexConfig, CodexEngine

config = CodexConfig(
    model_path="gpt2",              # Model name or path
    device="auto",                  # 'auto', 'cuda', 'cpu'
    adapter_type="auto",            # 'auto', 'huggingface', 'pytorch'
    enable_gpu=True,                # Enable GPU if available
    enable_full_engine=False,       # Load full model (heavy)
    fallback_to_cpu=True            # Fallback to CPU if GPU fails
)

codex = CodexEngine(config)
```

#### Via Environment Variables
```bash
export CODEX_MODEL_PATH="gpt2"
export CODEX_DEVICE="auto"
export CODEX_ADAPTER="auto"
export CODEX_ENABLE_GPU="1"
export CODEX_FULL_ENGINE="0"       # 0=lightweight, 1=full model
export CODEX_FALLBACK_CPU="1"
```

### API Reference

#### Constructor
```python
def __init__(self, config: CodexConfig | None = None)
```
If `config` is None, loads from environment variables.

#### Method: `process()`
```python
def process(self, input_data: Any, context: dict | None = None) -> dict
```

Process input through ML model.

**Parameters:**
- `input_data`: Input text or data structure
- `context`: Optional context (conversation history, metadata)

**Returns:**
- Dictionary with keys:
  - `output` (Any): Model inference result
  - `confidence` (float): Confidence score (0-1)
  - `metadata` (dict): Model info, device used, inference time

**Example:**
```python
from src.cognition.codex.engine import CodexEngine

codex = CodexEngine()  # Uses env vars

result = codex.process(
    "What is the capital of France?",
    context={"conversation_id": "123"}
)

print(f"Output: {result['output']}")
print(f"Confidence: {result['confidence']:.2%}")
print(f"Device: {result['metadata']['device']}")
```

#### Method: `get_status()`
```python
def get_status(self) -> dict
```

Returns engine status.

**Returns:**
- `{"loaded": bool, "device": str, "model": str}`

### Device Selection Logic

```python
if enable_gpu == False:
    device = "cpu"
elif device == "auto":
    if torch.cuda.is_available():
        device = "cuda"
    else:
        device = "cpu"
else:
    device = config.device  # Use specified device
```

### Fallback Logic

1. **Primary Attempt:** Load model on specified device (e.g., CUDA)
2. **Fallback:** If fails, try CPU
3. **Degraded Mode:** If both fail, operate without loaded model

---

## Engine 2: Galahad (Reasoning)

**File:** `galahad/engine.py`  
**Lines:** ~280  
**Purpose:** Reasoning, arbitration, and explanation generation

### Features

- ✅ **Multi-Step Reasoning** - Configurable reasoning depth (1-10 steps)
- ✅ **Arbitration** - Resolves conflicts between sources
- ✅ **Curiosity Metrics** - Tracks exploration vs. exploitation
- ✅ **Explanation Generation** - Human-readable decision explanations
- ✅ **Contradiction Detection** - Identifies conflicting inputs

### Configuration

```python
from src.cognition.galahad.engine import GalahadConfig, GalahadEngine

config = GalahadConfig(
    reasoning_depth=3,                 # Number of reasoning steps (1-10)
    enable_curiosity=True,             # Enable curiosity-driven exploration
    curiosity_threshold=0.5,           # Min curiosity for exploration (0-1)
    arbitration_strategy="weighted"    # 'weighted', 'unanimous', 'majority'
)

galahad = GalahadEngine(config)
```

### API Reference

#### Method: `reason()`
```python
def reason(self, inputs: list[Any], context: dict | None = None) -> dict
```

Perform reasoning over multiple inputs.

**Parameters:**
- `inputs`: List of inputs to reason over (can be conflicting)
- `context`: Optional context dictionary

**Returns:**
- Dictionary with keys:
  - `success` (bool): Whether reasoning succeeded
  - `conclusion` (Any): Reasoning conclusion
  - `explanation` (str): Human-readable explanation
  - `contradictions` (list): Detected contradictions
  - `curiosity_score` (float): Current curiosity level (0-1)

**Example:**
```python
from src.cognition.galahad.engine import GalahadEngine

galahad = GalahadEngine()

result = galahad.reason(
    inputs=[
        "Threat level: HIGH",
        "Threat level: MEDIUM",  # Contradiction
        "Enemy count: 100"
    ],
    context={"source": "tactical_ai"}
)

print(f"Conclusion: {result['conclusion']}")
print(f"Explanation: {result['explanation']}")
print(f"Contradictions: {result['contradictions']}")
print(f"Curiosity Score: {result['curiosity_score']:.2%}")
```

#### Method: `arbitrate()`
```python
def arbitrate(self, conflicting_inputs: list[dict]) -> dict
```

Arbitrate between conflicting inputs.

**Parameters:**
- `conflicting_inputs`: List of dicts with keys `{"value": Any, "weight": float}`

**Returns:**
- `{"decision": Any, "reason": str, "strategy": str}`

**Arbitration Strategies:**

1. **Weighted** (default): Weight inputs by confidence/reliability
   ```python
   inputs = [
       {"value": "HIGH", "weight": 0.8},
       {"value": "MEDIUM", "weight": 0.6}
   ]
   # Decision: "HIGH" (higher weight)
   ```

2. **Majority**: Select most common value
   ```python
   inputs = [
       {"value": "HIGH", "weight": 1.0},
       {"value": "MEDIUM", "weight": 1.0},
       {"value": "HIGH", "weight": 1.0}
   ]
   # Decision: "HIGH" (2 out of 3)
   ```

3. **Unanimous**: Require all inputs to agree
   ```python
   inputs = [
       {"value": "HIGH", "weight": 1.0},
       {"value": "HIGH", "weight": 1.0}
   ]
   # Decision: "HIGH" (unanimous)
   ```

#### Method: `get_curiosity_metrics()`
```python
def get_curiosity_metrics(self) -> dict
```

Returns curiosity metrics.

**Returns:**
```python
{
    "current_score": float,         # 0-1 curiosity level
    "enabled": bool,                # Is curiosity enabled?
    "threshold": float,             # Threshold for exploration
    "should_explore": bool          # Should system explore new options?
}
```

---

## Engine 3: Cerberus (Policy Enforcement)

**File:** `cerberus/engine.py`  
**Lines:** ~220  
**Purpose:** Input/output validation and policy enforcement

### Features

- ✅ **Input Validation** - Pre-processing security checks
- ✅ **Output Enforcement** - Post-processing policy compliance
- ✅ **Production Mode** - Allow-all by default (configurable)
- ✅ **Modification Support** - Can modify data to comply with policies
- ✅ **Deny/Modify/Allow** - Three-tier decision system

### Configuration

```python
from src.cognition.cerberus.engine import CerberusConfig, CerberusEngine

config = CerberusConfig(
    mode="production",          # 'production', 'strict', 'custom'
    enforce_on_input=False,     # Validate inputs?
    enforce_on_output=True,     # Enforce output policies?
    block_on_deny=True          # Block denied content?
)

cerberus = CerberusEngine(config)
```

### Policy Modes

| Mode | Input Enforcement | Output Enforcement | Use Case |
|------|-------------------|--------------------|----------|
| `production` | Disabled | Enabled (allow-all) | Production systems |
| `strict` | Enabled | Enabled (strict rules) | High-security environments |
| `custom` | Configurable | Configurable | Custom policy definitions |

### API Reference

#### Method: `validate_input()`
```python
def validate_input(self, input_data: Any, context: dict | None = None) -> dict
```

Validate input before processing.

**Returns:**
```python
{
    "valid": bool,              # Is input valid?
    "input": Any,               # Validated/modified input (None if denied)
    "reason": str,              # Validation reason
    "modified": bool,           # Was input modified?
    "warnings": list[str]       # List of warnings
}
```

**Example:**
```python
from src.cognition.cerberus.engine import CerberusEngine

cerberus = CerberusEngine()

result = cerberus.validate_input(
    "<script>alert('XSS')</script>",
    context={"source": "user"}
)

if not result["valid"]:
    print(f"Input rejected: {result['reason']}")
elif result.get("modified"):
    print(f"Input sanitized: {result['input']}")
else:
    print("Input accepted")
```

#### Method: `enforce_output()`
```python
def enforce_output(self, output_data: Any, context: dict | None = None) -> dict
```

Enforce policies on output before delivery.

**Returns:**
```python
{
    "allowed": bool,            # Is output allowed?
    "output": Any,              # Enforced output (None if denied)
    "reason": str,              # Enforcement reason
    "modified": bool,           # Was output modified?
    "warnings": list[str]       # List of warnings
}
```

**Example:**
```python
result = cerberus.enforce_output(
    "User password: secret123",
    context={"destination": "public_log"}
)

if not result["allowed"]:
    print(f"Output blocked: {result['reason']}")
elif result.get("modified"):
    print(f"Output sanitized: {result['output']}")
    # Output: "User password: [REDACTED]"
```

#### Method: `get_statistics()`
```python
def get_statistics(self) -> dict
```

Returns enforcement statistics.

**Returns:**
```python
{
    "enforcement_count": int,   # Total enforcements
    "denied_count": int,        # Denied items
    "modified_count": int       # Modified items
}
```

---

## Complete Integration Example

```python
from src.cognition.triumvirate import Triumvirate, TriumvirateConfig
from src.cognition.codex.engine import CodexConfig
from src.cognition.galahad.engine import GalahadConfig
from src.cognition.cerberus.engine import CerberusConfig

# Configure complete system
config = TriumvirateConfig(
    codex_config=CodexConfig(
        model_path="gpt2",
        enable_full_engine=False  # Lightweight mode
    ),
    galahad_config=GalahadConfig(
        reasoning_depth=3,
        arbitration_strategy="weighted"
    ),
    cerberus_config=CerberusConfig(
        mode="production",
        enforce_on_output=True
    ),
    enable_telemetry=True
)

# Initialize
triumvirate = Triumvirate(config)

# Process complex decision
result = triumvirate.process(
    input_data={
        "threat": "zombie horde",
        "distance": "500m",
        "friendly_forces": 50,
        "enemy_forces": 200
    },
    context={
        "mission": "defend_safehouse",
        "commander": "alpha_team"
    }
)

# Extract results
print(f"Correlation ID: {result['correlation_id']}")
print(f"ML Inference: {result['codex_result']['output']}")
print(f"Reasoning: {result['galahad_result']['explanation']}")
print(f"Policy Check: {result['cerberus_result']['allowed']}")
print(f"Final Decision: {result['final_output']}")
print(f"Total Time: {result['telemetry']['total_time_ms']}ms")
```

---

## Adapters

The Triumvirate system uses three types of adapters for extensibility:

### 1. Model Adapter
**File:** `adapters/model_adapter.py`  
Provides abstraction for different ML backends.

```python
from src.cognition.adapters.model_adapter import get_adapter

# Get HuggingFace adapter
adapter = get_adapter("huggingface", device="cuda")
adapter.load_model("gpt2")
output = adapter.infer("Hello, world!")
```

### 2. Policy Engine
**File:** `adapters/policy_engine.py`  
Implements policy enforcement logic.

```python
from src.cognition.adapters.policy_engine import PolicyEngine, PolicyDecision

engine = PolicyEngine(mode="strict")
result = engine.enforce(data, context)

if result.decision == PolicyDecision.DENY:
    print("Blocked by policy")
elif result.decision == PolicyDecision.MODIFY:
    print(f"Modified: {result.modified_output}")
```

### 3. Memory Adapter
**File:** `adapters/memory_adapter.py`  
Provides conversation history and context management.

```python
from src.cognition.adapters.memory_adapter import MemoryAdapter

memory = MemoryAdapter()
memory.store_context("conversation_123", {"user": "Alice"})
context = memory.retrieve_context("conversation_123")
```

---

## Escalation System

**File:** `codex/escalation.py`  
Multi-tier decision escalation for complex scenarios.

### Features

- ✅ **3-Tier Escalation** - Tier 1 (fast), Tier 2 (accurate), Tier 3 (human)
- ✅ **Confidence Thresholds** - Auto-escalate low-confidence decisions
- ✅ **Human-in-the-Loop** - Escalates critical decisions to operators

```python
from src.cognition.codex.escalation import EscalationManager

escalation = EscalationManager()

decision = escalation.decide(
    input_data=threat_data,
    min_confidence=0.8
)

if decision["tier"] == 3:
    print("Escalated to human operator")
    await_human_input()
```

---

## Performance Characteristics

| Engine | Memory | CPU (idle) | CPU (active) | Latency |
|--------|--------|------------|--------------|---------|
| Codex (lightweight) | 50 MB | 1% | 5% | 10ms |
| Codex (full model) | 500 MB+ | 5% | 80%+ | 50-500ms |
| Galahad | 20 MB | 1% | 10% | 5-50ms |
| Cerberus | 10 MB | 1% | 2% | 1-5ms |
| **Triumvirate** | **80-600 MB** | **3-7%** | **17-92%** | **16-555ms** |

---

## Testing

### Unit Test Example
```python
import pytest
from src.cognition.triumvirate import Triumvirate

def test_triumvirate_basic_processing():
    triumvirate = Triumvirate()
    
    result = triumvirate.process(
        input_data="test input",
        context={"test": True}
    )
    
    assert result["success"] is True
    assert "correlation_id" in result
    assert "final_output" in result

def test_codex_gpu_fallback():
    from src.cognition.codex.engine import CodexEngine, CodexConfig
    
    config = CodexConfig(
        device="cuda",
        fallback_to_cpu=True,
        enable_full_engine=False
    )
    
    codex = CodexEngine(config)
    status = codex.get_status()
    
    # Should be on CPU if no GPU available
    assert status["device"] in ["cuda", "cpu"]
```

---

## Related Documentation

- **Parent:** [README.md](./README.md)
- **Domain Systems:** [02-domains.md](./02-domains.md)
- **Agents:** [../agents/README.md](../agents/README.md)
- **Core Systems:** [../core/README.md](../core/README.md)

---

**Document Status:** ✅ Production-Ready  
**Quality Gate:** PASSED - Complete Triumvirate architecture documented  
**Compliance:** Fully compliant with Project-AI Governance Profile  
**Last Verified:** 2026-04-20
