# AGENT-018: Component Relationship Map

**Date:** 2026-04-20  
**Total Unique Systems:** 24  
**Engine Types:** 7

---

## System Architecture Overview

### AI-TAKEOVER

**Related Systems (3):**

- constraint-system
- simulation-engine
- threat-analysis

### AICPD

**Related Systems (3):**

- defense-simulation
- scenario-engine
- simulation-registry

### DJANGO-STATE

**Related Systems (3):**

- simulation-engine
- state-evolution
- trust-modeling

### EMP-DEFENSE

**Related Systems (3):**

- emp-modeling
- grid-analysis
- simulation-engine

### TARL-OS

**Related Systems (5):**

- ai-orchestration
- api-broker
- kernel
- observability
- security

### TARL-RUNTIME

**Related Systems (5):**

- bytecode
- compiler
- garbage-collector
- jit
- runtime-vm

### THIRSTY-SUPER-KERNEL

**Related Systems (4):**

- deception-system
- holographic-layers
- threat-detection
- visualization

---

## Cross-Engine Dependencies

| Component | Used By Engines | Integration Points |
|-----------|-----------------|-------------------|
| simulation-engine | ai-takeover, django-state, emp-defense | 3 engines |

---

## All Related Systems

- **ai-orchestration** - Used by: tarl-os
- **api-broker** - Used by: tarl-os
- **bytecode** - Used by: tarl-runtime
- **compiler** - Used by: tarl-runtime
- **constraint-system** - Used by: ai-takeover
- **deception-system** - Used by: thirsty-super-kernel
- **defense-simulation** - Used by: aicpd
- **emp-modeling** - Used by: emp-defense
- **garbage-collector** - Used by: tarl-runtime
- **grid-analysis** - Used by: emp-defense
- **holographic-layers** - Used by: thirsty-super-kernel
- **jit** - Used by: tarl-runtime
- **kernel** - Used by: tarl-os
- **observability** - Used by: tarl-os
- **runtime-vm** - Used by: tarl-runtime
- **scenario-engine** - Used by: aicpd
- **security** - Used by: tarl-os
- **simulation-engine** - Used by: ai-takeover, django-state, emp-defense
- **simulation-registry** - Used by: aicpd
- **state-evolution** - Used by: django-state
- **threat-analysis** - Used by: ai-takeover
- **threat-detection** - Used by: thirsty-super-kernel
- **trust-modeling** - Used by: django-state
- **visualization** - Used by: thirsty-super-kernel
