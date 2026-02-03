# Bio-Inspired Brain Mapping AI Subsystem Architecture

## Table of Contents
1. [Overview](#overview)
2. [Architectural Components](#architectural-components)
3. [RSGN (Resonant Sparse Geometry Network)](#rsgn)
4. [Bio-Modular Representation](#bio-modular-representation)
5. [Configuration Guide](#configuration-guide)
6. [API Reference](#api-reference)
7. [Usage Examples](#usage-examples)
8. [Integration with Project-AI](#integration-with-project-ai)
9. [Performance and Scaling](#performance-and-scaling)
10. [Future Extensions](#future-extensions)

---

## Overview

The Bio-Inspired Brain Mapping AI Subsystem is a sophisticated, geometry-driven, modular neural architecture that emulates biological cortical processing. It integrates two complementary components:

1. **Resonant Sparse Geometry Network (RSGN)**: A hyperbolic geometry-based network with sparse connectivity and two-timescale learning
2. **Bio-Modular Representation**: A hierarchical cortical architecture with sparse activation and lateral inhibition

### Key Features

- **Production-Ready**: No placeholders or stubs—complete, tested implementations
- **Biologically Inspired**: Reflects cortical hierarchy, sparse coding, and Hebbian plasticity
- **Geometrically Sophisticated**: Uses hyperbolic geometry (Poincaré ball) for hierarchical embeddings
- **Two-Timescale Learning**: Fast gradient-based + slow Hebbian plasticity
- **Highly Configurable**: YAML-based configuration with multiple presets
- **Observable**: Built-in diagnostics and visualization hooks
- **Production Integrated**: Seamlessly integrated with CognitionKernel and governance systems

### Biological Inspiration

The architecture draws from neuroscience principles:

- **Cortical Hierarchy**: Feedforward V1 → V2 → V4 → IT → PFC pathway
- **Sparse Coding**: Energy-efficient k-winner-take-all activation
- **Lateral Inhibition**: Mexican hat profiles for contrast enhancement
- **Hebbian Learning**: "Cells that fire together wire together"
- **Oscillatory Resonance**: Gamma-band (40 Hz) synchronization
- **Hyperbolic Geometry**: Natural representation of tree-like semantic hierarchies

---

## Architectural Components

```
┌─────────────────────────────────────────────────────────────────┐
│                   BioBrainMappingSystem                          │
│                     (Orchestrator)                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────┐    ┌────────────────────────────┐  │
│  │ Resonant Sparse        │    │ Bio-Modular                │  │
│  │ Geometry Network       │    │ Representation             │  │
│  │ (RSGN)                 │    │                            │  │
│  ├────────────────────────┤    ├────────────────────────────┤  │
│  │ • Hyperbolic Embeddings│    │ • V1: Low-level features   │  │
│  │ • Sparse Connectivity  │    │ • V2: Contours, textures   │  │
│  │ • Local Inhibition     │    │ • V4: Shapes, objects      │  │
│  │ • Fast Learning (BP)   │    │ • IT: Object recognition   │  │
│  │ • Slow Learning (Hebb) │    │ • PFC: Executive control   │  │
│  │ • Resonant Modulation  │    │ • Sparse Activation (k-WTA)│  │
│  └────────────────────────┘    │ • Lateral Inhibition       │  │
│                                 │ • Hebbian Plasticity       │  │
│                                 └────────────────────────────┘  │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│  Common Infrastructure:                                          │
│  • JSON persistence with atomic writes                           │
│  • Memory consolidation (weight normalization, pruning)          │
│  • Diagnostic interfaces (activation patterns, weight stats)     │
│  • Visualization hooks (embeddings, activations, resonance)      │
│  • CognitionKernel integration (governance, Four Laws)           │
└─────────────────────────────────────────────────────────────────┘
```

---

## RSGN (Resonant Sparse Geometry Network)

### Mathematical Foundation

The RSGN operates in hyperbolic space (Poincaré ball model):

**Poincaré Ball**: B^n = {x ∈ R^n : ||x|| < 1}

**Metric**: ds² = 4/(1 - ||x||²)² * ||dx||²

**Key Operations**:
- **Möbius Addition**: x ⊕ y = ((1 + 2⟨x,y⟩ + ||y||²)x + (1 − ||x||²)y) / (1 + 2⟨x,y⟩ + ||x||²||y||²)
- **Exponential Map**: exp_x(v) = x ⊕ tanh(λ_x ||v||) * v/||v||
- **Distance**: d(x,y) = arcosh(1 + 2||x−y||²/((1−||x||²)(1−||y||²)))

### Network Architecture

```
Input Layer (e.g., 128 dim)
    ↓
[Hyperbolic Embedding] → [Sparse Mask] → [Linear Transform]
    ↓
[ReLU] → [Local Inhibition] → [k-WTA Sparsification]
    ↓
[Resonant Modulation: cos(2πft)]
    ↓
Hidden Layer (e.g., 256 dim)
    ↓
[Repeat through n_layers]
    ↓
Output Layer
```

### Two-Timescale Learning

**Fast Learning (Gradient-Based)**:
- Standard backpropagation
- Learning rate: ~0.001
- Updates: weights_fast

**Slow Learning (Hebbian)**:
- Δw_ij = η_slow * (α * pre_i * post_j - β * w_ij)
- Learning rate: ~0.0001
- Updates: weights_slow
- α (potentiation): 0.1
- β (decay): 0.01

**Combined Forward Pass**:
- Mode "fast": Uses weights_fast
- Mode "slow": Uses weights_slow
- Mode "both": Uses (weights_fast + weights_slow) / 2

### Sparse Connectivity

Connection probability based on hyperbolic distance:

```
P(i → j) ∝ exp(-d(x_i, x_j)² / σ²)
```

Target sparsity (e.g., 10%) achieved by sampling connections proportional to probability.

### Local Inhibition (Mexican Hat)

Lateral interaction kernel:

```
w(r) = A_exc * exp(-r²/σ_exc²) - A_inh * exp(-r²/σ_inh²)
```

Parameters:
- σ_exc = 1.0 (excitation radius)
- σ_inh = 3.0 (inhibition radius)
- A_exc = 1.0 (excitation strength)
- A_inh = 0.5 (inhibition strength)

---

## Bio-Modular Representation

### Cortical Hierarchy

Five-level hierarchy mimicking visual cortex:

| Module | Function | Input Source | Output Dim | Key Features |
|--------|----------|--------------|------------|--------------|
| **V1** | Edge detection, Gabor-like | Raw input | 256 | Low-level feature extraction |
| **V2** | Contours, textures | V1 | 256 | Intermediate features |
| **V4** | Shapes, object parts | V2 | 512 | High-level features |
| **IT** | Object recognition | V4 | 512 | Invariant object representations |
| **PFC** | Executive control, reasoning | IT | 256 | Abstract, task-relevant features |

### Sparse Activation (k-WTA)

Each module maintains sparse activation:
- **k-winner-take-all**: Only top-k neurons active
- Default: k=20 out of 256-512 neurons (~4-8% sparsity)
- Metabolically efficient, biologically plausible

### Lateral Inhibition

Within-module competition:
```python
activation = feedforward_input - 0.5 * lateral_inhibition
```

Lateral weights initialized to small random values, updated via Hebbian learning.

### Hebbian Plasticity

```
Δw_ij = η * (pre_i * post_j - 0.01 * w_ij)
```

- Correlation-based weight updates
- Automatic weight decay prevents runaway growth
- Unsupervised adaptation to input statistics

### Resonant Propagation

Oscillatory modulation at gamma frequency (40 Hz):

```
activation = activation * (1 + γ * cos(2πft))
```

- Synchronizes processing across modules
- Enhances phase-locked signals
- Mimics cortical gamma-band oscillations

---

## Configuration Guide

### Configuration File: `config/bio_brain_mapping.yaml`

#### RSGN Configuration

```yaml
rsgn:
  n_layers: 3                      # Number of RSGN layers
  layer_sizes: [128, 256, 512, 256] # Dimensions: input → hidden1 → hidden2 → output
  sparsity: 0.1                    # Connection density (10%)
  hyperbolic_dim: 64               # Dimensionality of Poincaré ball
  curvature: 1.0                   # Hyperbolic curvature parameter
```

#### Learning Configuration

```yaml
learning:
  fast_lr: 0.001                   # Gradient-based learning rate
  slow_lr: 0.0001                  # Hebbian learning rate
  hebb_potentiation: 0.1           # α: Potentiation rate
  hebb_decay: 0.01                 # β: Weight decay rate
  weight_decay: 0.0001             # L2 regularization
```

#### Inhibition Configuration

```yaml
inhibition:
  excitation_radius: 1.0           # σ_exc: Excitatory reach
  inhibition_radius: 3.0           # σ_inh: Inhibitory reach
  excitation_strength: 1.0         # A_exc: Excitatory amplitude
  inhibition_strength: 0.5         # A_inh: Inhibitory amplitude
  kwta_k: 10                       # k in k-winner-take-all
```

#### Module Configuration

```yaml
modules:
  input_dim: 128
  v1_dim: 256
  v2_dim: 256
  v4_dim: 512
  it_dim: 512
  pfc_dim: 256
  sparsity_k: 20                   # Active neurons per module
  learning_rate: 0.0001            # Hebbian rate
  resonance_freq: 40.0             # Hz (gamma band)
```

### Presets

Three built-in presets:

**Development** (fast prototyping):
```yaml
active_preset: "development"
# Smaller network, higher learning rate, frequent consolidation
```

**Production** (balanced):
```yaml
active_preset: "production"
# Default configuration (shown above)
```

**Research** (large-scale):
```yaml
active_preset: "research"
# Larger network, careful learning, less frequent consolidation
```

---

## API Reference

### BioBrainMappingSystem

Main orchestrator class.

#### Initialization

```python
from app.core.bio_brain_mapper import BioBrainMappingSystem

# With default config
system = BioBrainMappingSystem(data_dir="data")

# With custom config
system = BioBrainMappingSystem(
    config=custom_config_dict,
    data_dir="data"
)
```

#### Processing

```python
import numpy as np

# Create input (batch_size, input_dim)
x = np.random.randn(4, 128).astype(np.float32)

# Process with learning
result = system.process(
    x,
    learning_mode=LearningMode.BOTH,
    update_weights=True
)

# Access outputs
rsgn_output = result["rsgn_output"]          # RSGN final layer
module_activations = result["module_activations"]  # Dict[ModuleType, ndarray]
diagnostics = result["rsgn_diagnostics"]     # Diagnostic info
```

#### Memory Consolidation

```python
# Manual consolidation
system.consolidate_memory()

# Auto-consolidation (triggered after N learning steps)
# Controlled by config['consolidation']['interval_steps']
```

#### Diagnostics

```python
diagnostics = system.get_diagnostics()

print(diagnostics)
# {
#   'network_id': '...',
#   'rsgn_layers': 3,
#   'rsgn_sparsity': 0.1,
#   'module_count': 5,
#   'learning_events': 1234,
#   'consolidation_count': 2,
#   'last_consolidation': '2026-01-29T12:34:56',
#   'bio_modules_time': 123.45
# }
```

#### State Persistence

```python
# Save state
system.save_state()

# Load state
system.load_state(network_id="...")
```

### ResonantSparseGeometryNetwork

Low-level RSGN interface.

```python
from app.core.bio_brain_mapper import (
    ResonantSparseGeometryNetwork,
    NetworkTopology,
    LearningParameters,
    InhibitionParameters,
    ResonanceParameters
)

topology = NetworkTopology(
    n_layers=2,
    layer_sizes=[64, 128, 64],
    sparsity=0.2,
    hyperbolic_dim=32,
    curvature=1.0
)

learning_params = LearningParameters(
    fast_lr=0.01,
    slow_lr=0.001
)

inhibition_params = InhibitionParameters(
    excitation_radius=1.0,
    inhibition_radius=3.0,
    kwta_k=10
)

resonance_params = ResonanceParameters(
    frequency=40.0,
    modulation_depth=0.1
)

rsgn = ResonantSparseGeometryNetwork(
    topology=topology,
    learning_params=learning_params,
    inhibition_params=inhibition_params,
    resonance_params=resonance_params
)

# Forward pass
output, diagnostics = rsgn.forward(x, learning_mode=LearningMode.FAST)

# Hebbian update
rsgn.update_weights_hebbian(layer_idx=0, pre_activation=pre, post_activation=post)
```

### BioModularRepresentation

Low-level modular interface.

```python
from app.core.bio_brain_mapper import BioModularRepresentation, ModuleType

module_dims = {
    ModuleType.V1: 128,
    ModuleType.V2: 128,
    ModuleType.V4: 256,
    ModuleType.IT: 256,
    ModuleType.PFC: 128
}

bio_modules = BioModularRepresentation(
    input_dim=64,
    module_dims=module_dims,
    sparsity_k=10,
    learning_rate=0.001,
    resonance_freq=40.0
)

# Forward pass
activations = bio_modules.forward(x)

# Access module outputs
v1_activation = activations[ModuleType.V1]
pfc_activation = activations[ModuleType.PFC]

# Hebbian update
bio_modules.update_hebbian(x, activations)
```

### HyperbolicOps

Hyperbolic geometry utilities.

```python
from app.core.bio_brain_mapper import HyperbolicOps
import numpy as np

hyp = HyperbolicOps(curvature=1.0)

# Clip to Poincaré ball
x = np.array([[2.0, 2.0]], dtype=np.float32)
x_clipped = hyp.clip_to_ball(x)

# Möbius addition
x = np.array([[0.1, 0.2]], dtype=np.float32)
y = np.array([[0.3, 0.1]], dtype=np.float32)
z = hyp.mobius_add(x, y)

# Exponential map (tangent → manifold)
v = np.array([[0.05, 0.03]], dtype=np.float32)
y = hyp.exp_map(x, v)

# Logarithmic map (manifold → tangent)
v_recovered = hyp.log_map(x, y)

# Distance
dist = hyp.distance(x, y)
```

---

## Usage Examples

### Example 1: Basic Processing

```python
import numpy as np
from app.core.bio_brain_mapper import BioBrainMappingSystem, LearningMode

# Initialize system
system = BioBrainMappingSystem(data_dir="data")

# Generate sample input (batch_size=8, input_dim=128)
x = np.random.randn(8, 128).astype(np.float32)

# Process with two-timescale learning
result = system.process(x, learning_mode=LearningMode.BOTH, update_weights=True)

# Extract outputs
rsgn_output = result["rsgn_output"]
module_activations = result["module_activations"]

print(f"RSGN output shape: {rsgn_output.shape}")
print(f"PFC activation shape: {module_activations[ModuleType.PFC].shape}")
```

### Example 2: Custom Configuration

```python
custom_config = {
    "rsgn": {
        "n_layers": 4,
        "layer_sizes": [256, 512, 1024, 512, 256],
        "sparsity": 0.05,
        "hyperbolic_dim": 128
    },
    "learning": {
        "fast_lr": 0.0005,
        "slow_lr": 0.00005
    },
    "modules": {
        "input_dim": 256,
        "v1_dim": 512,
        "v2_dim": 512,
        "v4_dim": 1024,
        "it_dim": 1024,
        "pfc_dim": 512,
        "sparsity_k": 30
    },
    "consolidation": {
        "interval_steps": 2000
    }
}

system = BioBrainMappingSystem(config=custom_config, data_dir="data")
```

### Example 3: Online Continual Learning

```python
# Simulate continuous learning over time
for epoch in range(100):
    # Generate batch
    x = generate_data_batch()
    
    # Process and learn
    result = system.process(x, learning_mode=LearningMode.BOTH, update_weights=True)
    
    # Consolidation happens automatically every N steps
    # (configured by config['consolidation']['interval_steps'])
    
    if epoch % 10 == 0:
        diagnostics = system.get_diagnostics()
        print(f"Epoch {epoch}: {diagnostics['learning_events']} events, "
              f"{diagnostics['consolidation_count']} consolidations")
```

### Example 4: Inference Only (No Learning)

```python
# Load pre-trained network
system = BioBrainMappingSystem(data_dir="data")
system.load_state(network_id="pretrained_network_id")

# Inference mode (no weight updates)
x = np.random.randn(4, 128).astype(np.float32)
result = system.process(x, learning_mode=LearningMode.BOTH, update_weights=False)

# Extract features from different levels
v1_features = result["module_activations"][ModuleType.V1]
it_features = result["module_activations"][ModuleType.IT]
pfc_features = result["module_activations"][ModuleType.PFC]
```

### Example 5: Visualization Hooks

```python
import matplotlib.pyplot as plt

# Process with diagnostics
result = system.process(x, learning_mode=LearningMode.BOTH, update_weights=True)

diagnostics = result["rsgn_diagnostics"]

# Visualize layer activations
for layer_idx, activation in enumerate(diagnostics["layer_activations"]):
    plt.figure(figsize=(12, 4))
    plt.imshow(activation, aspect='auto', cmap='viridis')
    plt.title(f"RSGN Layer {layer_idx} Activation")
    plt.colorbar()
    plt.xlabel("Neuron Index")
    plt.ylabel("Batch Sample")
    plt.tight_layout()
    plt.savefig(f"activation_layer_{layer_idx}.png")
    plt.close()

# Visualize module activations
module_activations = result["module_activations"]
fig, axes = plt.subplots(1, 5, figsize=(20, 4))
for idx, (mod_type, activation) in enumerate(module_activations.items()):
    axes[idx].imshow(activation, aspect='auto', cmap='plasma')
    axes[idx].set_title(f"{mod_type.value} Module")
    axes[idx].set_xlabel("Neuron Index")
    axes[idx].set_ylabel("Batch Sample")
plt.tight_layout()
plt.savefig("module_activations.png")
plt.close()
```

---

## Integration with Project-AI

### CognitionKernel Integration

The bio brain mapper is fully integrated with CognitionKernel:

```python
# In src/app/main.py
def initialize_kernel() -> CognitionKernel:
    # ... other subsystems ...
    
    # Initialize bio brain mapper
    bio_brain_mapper = BioBrainMappingSystem(data_dir="data")
    
    # Register with kernel
    bio_brain_mapper.register_with_kernel(kernel)
    
    # All operations now subject to Four Laws governance
```

### Security and Governance

The subsystem respects Project-AI governance:

- **Four Laws Compliance**: All operations subject to Asimov's Laws validation
- **Credential TTL**: 4 hours (configurable in `config/security_hardening.yaml`)
- **Allowed Operations**: read, write, analyze, consolidate
- **Resource Limits**: Configurable memory/CPU constraints

### Data Persistence

Follows Project-AI atomic write pattern:

```python
# Atomic save with file locking
with self._file_lock:
    temp_path = state_path.with_suffix(".tmp")
    with open(temp_path, "w") as f:
        json.dump(state, f, indent=2)
    temp_path.replace(state_path)  # Atomic rename
```

---

## Performance and Scaling

### Computational Complexity

| Operation | Complexity | Notes |
|-----------|------------|-------|
| RSGN Forward | O(n * m * s) | n=layers, m=max_neurons, s=sparsity |
| RSGN Hebbian | O(m² * s) | Per layer |
| Module Forward | O(k) | k=hierarchical_depth (5 modules) |
| Local Inhibition | O(m²) | Can be optimized with spatial indexing |

### Memory Usage

Typical configuration (production preset):
- **RSGN weights**: ~10 MB (128→256→512→256, sparsity=0.1)
- **Module weights**: ~5 MB (V1→V2→V4→IT→PFC)
- **Embeddings**: ~2 MB (64-dim hyperbolic)
- **Total**: ~20 MB per network instance

### Optimization Strategies

1. **Sparse Matrices**: Use scipy.sparse for large sparse masks
2. **Batch Processing**: Process multiple samples simultaneously
3. **GPU Acceleration**: Convert to PyTorch/JAX for GPU compute
4. **Pruning**: Aggressive pruning during consolidation (threshold=0.001)
5. **Quantization**: Use float16 for inference (reduces memory by 50%)

### Scaling Recommendations

| Use Case | Preset | Notes |
|----------|--------|-------|
| **Prototyping** | development | Fast iteration, smaller network |
| **Production** | production | Balanced performance/accuracy |
| **Research** | research | Maximum capacity, careful learning |
| **Edge Devices** | Custom (small) | layer_sizes=[64, 128, 64], sparsity=0.2 |
| **Cloud/GPU** | Custom (large) | layer_sizes=[512, 1024, 2048, 1024, 512] |

---

## Future Extensions

### Planned Enhancements

1. **Multi-Band Resonance**:
   - Theta (6 Hz), Alpha (10 Hz), Beta (20 Hz), Gamma (40 Hz)
   - Cross-frequency coupling
   - Hierarchical phase locking

2. **Adaptive Sparsity**:
   - Dynamic k-WTA based on input complexity
   - Energy-aware sparsity adjustment
   - Metabolic cost modeling

3. **Experience Replay**:
   - Memory buffer for continual learning
   - Prioritized experience sampling
   - Catastrophic forgetting prevention

4. **Attention Mechanisms**:
   - Top-down attentional modulation
   - Feature-based attention (V4/IT)
   - Spatial attention maps

5. **Visualization Dashboard**:
   - Real-time activation monitoring
   - Hyperbolic embedding plots (Plotly 3D)
   - Weight evolution timeseries
   - Resonance phase coherence

6. **GPU Acceleration**:
   - PyTorch backend (optional)
   - CUDA kernels for hyperbolic ops
   - Mixed-precision training

7. **Neuromorphic Hardware**:
   - Intel Loihi2 support
   - Event-driven spike encoding
   - Asynchronous processing

### Research Directions

- **Hierarchical Reinforcement Learning**: Use PFC for policy learning
- **Multi-Modal Integration**: Extend to audio, text, sensory fusion
- **Meta-Learning**: Fast adaptation via slow-weight modulation
- **Explainability**: Visualize which hyperbolic regions activate for specific inputs
- **Neuro-symbolic Integration**: Connect PFC outputs to symbolic reasoning (TARL)

---

## References

### Hyperbolic Geometry
- Nickel, M., & Kiela, D. (2017). "Poincaré Embeddings for Learning Hierarchical Representations." NeurIPS.
- Sala, F., et al. (2018). "Representation Tradeoffs for Hyperbolic Embeddings." ICML.

### Sparse Coding
- Olshausen, B. A., & Field, D. J. (1996). "Emergence of simple-cell receptive field properties by learning a sparse code for natural images." Nature.
- Rozell, C. J., et al. (2008). "Sparse coding via thresholding and local competition in neural circuits." Neural Computation.

### Hebbian Learning
- Hebb, D. O. (1949). "The Organization of Behavior." Wiley.
- Gerstner, W., & Kistler, W. M. (2002). "Spiking Neuron Models." Cambridge University Press.

### Cortical Hierarchy
- Felleman, D. J., & Van Essen, D. C. (1991). "Distributed hierarchical processing in the primate cerebral cortex." Cerebral Cortex.
- DiCarlo, J. J., et al. (2012). "How does the brain solve visual object recognition?" Neuron.

### Oscillations
- Fries, P. (2015). "Rhythms for Cognition: Communication through Coherence." Neuron.
- Buzsáki, G., & Draguhn, A. (2004). "Neuronal oscillations in cortical networks." Science.

---

## Contact and Support

For questions, issues, or contributions:
- **Repository**: https://github.com/IAmSoThirsty/Project-AI
- **Issues**: https://github.com/IAmSoThirsty/Project-AI/issues
- **Module**: `src/app/core/bio_brain_mapper.py`
- **Tests**: `tests/test_bio_brain_mapper.py`
- **Config**: `config/bio_brain_mapping.yaml`

---

**Document Version**: 1.0  
**Last Updated**: 2026-01-29  
**Author**: Project-AI Development Team
