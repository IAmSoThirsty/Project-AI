"""atlas.config - Runtime-tunable YAML configuration for ATLAS Omega.

SUBORDINATION NOTICE:
This module is part of ATLAS Omega, a SECONDARY, OPTIONAL
tool subordinate to Project-AI.

Primary System: Project-AI (Jeremy Karrick, Architect and Founder)
Triumvirate governance: ACTIVE and UNCHANGED

The config module loads + validates + provides access to
all YAML configuration files for the atlas stack. Includes:

- stacks.yaml: stack definitions (RS, TS-0..3, SS) +
  transitions
- drivers.yaml: influence drivers + weights (must sum to 1.0)
- penalties.yaml: stack penalties
- thresholds.yaml: operational thresholds
- safety.yaml: safety rules (LOCKED, no modification)
- seeds.yaml: timeline seeds for divergence analysis
"""
