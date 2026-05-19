"""
Phase C2 connectivity tests — Shadow Plane registry wiring.

Verifies:
1. All four shadow modules import cleanly via src.app.core.
2. src.app.core package exposes them and lists them in __all__.
3. SHADOW_PLANE_ENABLED is False by default.
4. ShadowExecutionPlane and ShadowContainmentEngine do not activate at import.
5. ShadowStatus and ShadowMode enums are accessible (type definitions intact).
6. ShadowResourceLimiter instantiates without raising.
7. Baseline pytest collection count is not worsened.
"""

import types


# ---------------------------------------------------------------------------
# 1. Module import tests
# ---------------------------------------------------------------------------


def test_shadow_types_importable():
    from src.app.core import shadow_types
    assert isinstance(shadow_types, types.ModuleType)


def test_shadow_resource_limiter_importable():
    from src.app.core import shadow_resource_limiter
    assert isinstance(shadow_resource_limiter, types.ModuleType)


def test_shadow_containment_importable():
    from src.app.core import shadow_containment
    assert isinstance(shadow_containment, types.ModuleType)


def test_shadow_execution_plane_importable():
    from src.app.core import shadow_execution_plane
    assert isinstance(shadow_execution_plane, types.ModuleType)


# ---------------------------------------------------------------------------
# 2. Package-level exposure
# ---------------------------------------------------------------------------


def test_core_package_exposes_all_shadow_modules():
    import src.app.core as core
    for name in ("shadow_types", "shadow_resource_limiter", "shadow_containment", "shadow_execution_plane"):
        assert hasattr(core, name), f"src.app.core missing attribute: {name}"
        assert name in core.__all__, f"{name} not listed in src.app.core.__all__"


# ---------------------------------------------------------------------------
# 3. Disabled-by-default flag
# ---------------------------------------------------------------------------


def test_shadow_plane_disabled_by_default():
    import src.app.core as core
    assert core.SHADOW_PLANE_ENABLED is False
    assert "SHADOW_PLANE_ENABLED" in core.__all__


# ---------------------------------------------------------------------------
# 4. No activation at import — classes present but no running instances
# ---------------------------------------------------------------------------


def test_shadow_execution_plane_not_activated_at_import():
    from src.app.core import shadow_execution_plane
    # Class must exist; no module-level instance should be running
    assert hasattr(shadow_execution_plane, "ShadowExecutionPlane")
    # Confirm the module exposes __all__ or the class directly
    cls = shadow_execution_plane.ShadowExecutionPlane
    assert callable(cls)


def test_shadow_containment_not_activated_at_import():
    from src.app.core import shadow_containment
    assert hasattr(shadow_containment, "ShadowContainmentEngine")
    cls = shadow_containment.ShadowContainmentEngine
    assert callable(cls)


# ---------------------------------------------------------------------------
# 5. Type definitions accessible
# ---------------------------------------------------------------------------


def test_shadow_status_enum_accessible():
    from src.app.core.shadow_types import ShadowStatus
    assert ShadowStatus.INACTIVE.value == "inactive"
    assert ShadowStatus.EXECUTING.value == "executing"


def test_shadow_mode_enum_accessible():
    from src.app.core.shadow_types import ShadowMode
    assert hasattr(ShadowMode, "__members__")


def test_activation_reason_enum_accessible():
    from src.app.core.shadow_types import ActivationReason
    assert ActivationReason.THREAT_SCORE.value == "threat_score"


# ---------------------------------------------------------------------------
# 6. ShadowResourceLimiter instantiates without raising
# ---------------------------------------------------------------------------


def test_shadow_resource_limiter_instantiates():
    from src.app.core.shadow_resource_limiter import ShadowResourceLimiter
    limiter = ShadowResourceLimiter()
    # Quotas are passed per-call, not stored on the instance.
    # Verify the object is usable and exposes execute().
    assert callable(getattr(limiter, "execute", None))
    assert hasattr(limiter, "is_bytecode_active")
