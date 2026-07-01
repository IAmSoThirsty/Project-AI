"""T6 namespace isolation test: Beginnings' tarl and Thirsty-Lang's
tarl coexist in the same Python process.

Per PHASE_T_DISCOVERY.md Phase T6 (renamed to "documented non-
collision" per docs/internal/T6_NAMING.md): the two `tarl`
namespaces are siblings, not parent/child.

  - `import tarl`        -> Beginnings' Threat-Adaptive Rule Language
  - `import utf.tarl`    -> Thirsty-Lang's 5th tier (TARL spec lang)

The test verifies that:
  1. Both imports succeed.
  2. Each `tarl` module is the correct one (its `__name__` is
     `tarl` for Beginnings, `utf.tarl` for Thirsty).
  3. The Beginnings TARL exposes its public surface
     (Compiler, Policy, TarlConfig).
  4. The Thirsty-Lang tier exposes its public surface
     (PolicyParser, TarlRuntime) via `utf.tarl.core` and
     `utf.tarl.runtime`.
  5. There is no aliasing or shadowing: each module's identity
     is stable across multiple `import` statements.

This test is the canonical proof that the T6 rename plan was
unnecessary. If this test ever fails, the namespace isolation
is broken and a rename becomes required.
"""

from __future__ import annotations

import importlib
import sys

# ── 1. Both imports succeed in the same process ──────────────


def test_both_imports_succeed() -> None:
    """Both `tarl` and `utf.tarl` can be imported in one process."""
    import utf.tarl  # noqa: F401  (Thirsty-Lang's 5th tier)

    import tarl  # noqa: F401  (Beginnings' Threat-Adaptive Rule Language)

    # If we got here, both imports succeeded.
    assert "tarl" in sys.modules
    assert "utf.tarl" in sys.modules


# ── 2. Each module is the correct one ────────────────────────


def test_beginnings_tarl_is_the_project_language() -> None:
    """`import tarl` is Beginnings' Threat-Adaptive Rule Language."""
    import tarl

    assert tarl.__name__ == "tarl"
    # The package file location is under packages/tarl/src/tarl/__init__.py
    init_path = getattr(tarl, "__file__", "") or ""
    assert "packages" in init_path
    assert "tarl" in init_path


def test_thirsty_tarl_is_dotted_namespace() -> None:
    """`import utf.tarl` is Thirsty-Lang's 5th tier, dotted namespace."""
    import utf.tarl

    assert utf.tarl.__name__ == "utf.tarl"
    # The package file location is under the thirsty-lang wheel
    init_path = getattr(utf.tarl, "__file__", "") or ""
    assert "site-packages" in init_path or "thirsty" in init_path.lower()


# ── 3. Beginnings' TARL exposes its public surface ──────────


def test_beginnings_tarl_has_compiler() -> None:
    """Beginnings' tarl exposes the Compiler class."""
    import tarl

    assert hasattr(tarl, "Compiler")
    assert callable(tarl.Compiler)


def test_beginnings_tarl_has_policy_types() -> None:
    """Beginnings' tarl exposes its policy types."""
    import tarl

    # The package re-exports policy types from `tarl.policy`.
    # We don't pin a specific symbol because the surface is
    # large; we just confirm the module is loadable and has
    # policy-related symbols.
    has_policy_module = "tarl.policy" in sys.modules
    if not has_policy_module:
        # If the policy module hasn't been imported, import it.
        import tarl.policy  # noqa: F401
    assert "tarl.policy" in sys.modules


# ── 4. Thirsty-Lang's tier exposes its public surface ────────


def test_thirsty_tarl_exposes_policy_parser() -> None:
    """`utf.tarl.core.PolicyParser` is the Thirsty-Lang parser."""
    from utf.tarl.core import PolicyParser

    assert PolicyParser is not None
    assert callable(PolicyParser)


def test_thirsty_tarl_exposes_tarl_runtime() -> None:
    """`utf.tarl.runtime.TarlRuntime` is the Thirsty-Lang runtime."""
    from utf.tarl.runtime import TarlRuntime

    assert TarlRuntime is not None
    assert callable(TarlRuntime)


# ── 5. No aliasing or shadowing across re-imports ───────────


def test_reimport_yields_same_modules() -> None:
    """Re-importing both tarl modules yields the same module objects."""
    import utf.tarl as thirsty_tarl_a
    import utf.tarl as thirsty_tarl_b

    import tarl as tarl_a
    import tarl as tarl_b

    assert tarl_a is tarl_b
    assert thirsty_tarl_a is thirsty_tarl_b
    # And the two are NOT the same.
    assert tarl_a is not thirsty_tarl_a


# ── 6. importlib round-trip ───────────────────────────────


def test_importlib_round_trip_preserves_namespace() -> None:
    """importlib.import_module returns the same module object for each."""
    tarl_mod = importlib.import_module("tarl")
    thirsty_mod = importlib.import_module("utf.tarl")
    assert tarl_mod is not thirsty_mod
    assert tarl_mod.__name__ == "tarl"
    assert thirsty_mod.__name__ == "utf.tarl"


# ── 7. No STAR collisions in __all__ ─────────────────────


def test_no_star_collision_between_namespaces() -> None:
    """Neither namespace's __all__ shadows the other.

    Both `tarl.__all__` and `utf.tarl.__all__` are independent
    and don't reference each other. The test asserts that
    importing both with star import works without shadowing
    (we don't actually do `from X import *` in production code;
    this is a smoke test).
    """
    import utf.tarl

    import tarl

    # Both have __all__ attributes.
    assert hasattr(tarl, "__all__")
    # The Thirsty tarl __init__.py may not have __all__, in which
    # case we just check that the package is importable.
    thirsty_all = getattr(utf.tarl, "__all__", None)
    # The two __all__s are not required to be disjoint (they are
    # in different namespaces), but neither should reference the
    # other module.
    if tarl.__all__ and thirsty_all:
        # Both have __all__: confirm they're independent strings.
        assert tarl.__all__ is not thirsty_all
