"""
Thirsty's Gradle—Total System Evolution
========================================

Integrates existing Project-AI components into a governed execution substrate:
- Constitutional engine (policies/constitution.yaml)
- Policy enforcement (project_ai/engine/policy/)
- Build cognition (cognition/ + project_ai/engine/cognition/)
- State management (project_ai/engine/state/)
- Governance core (governance/)
- Security infrastructure (config/security_hardening.yaml)
- Audit system (cognition/audit.py)
- Temporal workflows (temporal/)

This evolution layer wires together pre-existing components to create a
maximal, production-grade governed execution substrate for the Gradle build system.
"""

__version__ = "1.0.0"
__all__ = [
    "constitutional",
    "cognition",
    "capsules",
    "security",
    "audit",
    "api",
]
