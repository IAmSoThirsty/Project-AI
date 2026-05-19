"""
Core subsystem for Project-AI.

This package provides the runtime kernel, governance enforcement,
and shadow execution infrastructure.

Shadow Plane modules (shadow_types, shadow_resource_limiter,
shadow_containment, shadow_execution_plane) are importable but
runtime activation is disabled by default.

Set SHADOW_PLANE_ENABLED = True in application config to allow
ShadowExecutionPlane and ShadowContainmentEngine instantiation.
No shadow execution starts on import.
"""

from . import shadow_types
from . import shadow_resource_limiter
from . import shadow_containment
from . import shadow_execution_plane

# Runtime activation flag — disabled by default.
# Callers must explicitly set this True before instantiating
# ShadowExecutionPlane or ShadowContainmentEngine.
SHADOW_PLANE_ENABLED: bool = False

__all__ = [
    "shadow_types",
    "shadow_resource_limiter",
    "shadow_containment",
    "shadow_execution_plane",
    "SHADOW_PLANE_ENABLED",
]
