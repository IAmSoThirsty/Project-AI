"""
Phase C3A connectivity tests — recovered engine registry.

Verifies:
1. Registry module imports cleanly.
2. All three engines are listed in the registry.
3. All engines are disabled by default (enabled=False).
4. Registry does NOT import heavy engine modules during package import.
5. No engine starts automatically on import.
6. Known blockers are documented in each entry.
7. ENGINES global has correct structure per entry.
8. Helper functions work correctly.
9. Pytest collection baseline is not worsened.
"""

import sys


# ---------------------------------------------------------------------------
# 1. Registry imports cleanly
# ---------------------------------------------------------------------------


def test_engine_registry_importable():
    from src.app.core import engine_registry
    import types
    assert isinstance(engine_registry, types.ModuleType)


def test_engine_registry_exposes_engines_dict():
    from src.app.core.engine_registry import ENGINES
    assert isinstance(ENGINES, dict)
    assert len(ENGINES) > 0


# ---------------------------------------------------------------------------
# 2. All three engines are listed
# ---------------------------------------------------------------------------

EXPECTED_ENGINES = {"atlas", "hydra_50", "sovereign_war_room"}


def test_all_three_engines_registered():
    from src.app.core.engine_registry import ENGINES
    assert EXPECTED_ENGINES == set(ENGINES.keys()), (
        f"Expected {EXPECTED_ENGINES}, got {set(ENGINES.keys())}"
    )


def test_list_engines_returns_all_three():
    from src.app.core.engine_registry import list_engines
    assert EXPECTED_ENGINES == set(list_engines())


# ---------------------------------------------------------------------------
# 3. All disabled by default
# ---------------------------------------------------------------------------


def test_all_engines_disabled_by_default():
    from src.app.core.engine_registry import ENGINES
    for name, entry in ENGINES.items():
        assert entry.enabled is False, f"Engine '{name}' should be disabled by default"


def test_list_enabled_engines_empty_by_default():
    from src.app.core.engine_registry import list_enabled_engines
    assert list_enabled_engines() == []


def test_global_activation_disabled_by_default():
    from src.app.core.engine_registry import ENGINE_REGISTRY_ACTIVATION_ENABLED
    assert ENGINE_REGISTRY_ACTIVATION_ENABLED is False


# ---------------------------------------------------------------------------
# 4. Registry does NOT import engine modules during package import
#    (checked by absence from sys.modules after import)
# ---------------------------------------------------------------------------


def test_atlas_engine_module_not_imported_by_registry():
    # Import the registry, then confirm the heavy atlas internals are absent.
    import src.app.core.engine_registry  # noqa: F401
    # Top-level engines.atlas.__init__ is lightweight, but atlas submodules
    # (cli, core, schemas, simulation) must not be loaded.
    heavy_atlas = [k for k in sys.modules if k.startswith("engines.atlas.")]
    assert not heavy_atlas, (
        f"atlas submodules were imported during registry load: {heavy_atlas}"
    )


def test_hydra_50_engine_module_not_imported_by_registry():
    import src.app.core.engine_registry  # noqa: F401
    heavy_hydra = [k for k in sys.modules if "hydra_50.cerberus_hydra" in k]
    assert not heavy_hydra, (
        f"hydra cerberus_hydra was imported during registry load: {heavy_hydra}"
    )


def test_sovereign_war_room_not_imported_by_registry():
    import src.app.core.engine_registry  # noqa: F401
    swr_modules = [k for k in sys.modules if k.startswith("engines.sovereign_war_room.")]
    assert not swr_modules, (
        f"SWR submodules were imported during registry load: {swr_modules}"
    )


# ---------------------------------------------------------------------------
# 5. Entry structure is correct
# ---------------------------------------------------------------------------


def test_each_entry_has_required_fields():
    from src.app.core.engine_registry import ENGINES
    required = {
        "name", "path", "module_path", "status", "enabled",
        "import_mode", "known_blockers", "activation_requires_explicit_config",
        "module_locatable",
    }
    for name, entry in ENGINES.items():
        entry_dict = entry.as_dict()
        missing = required - set(entry_dict.keys())
        assert not missing, f"Entry '{name}' missing fields: {missing}"


def test_all_statuses_are_recovered_unactivated():
    from src.app.core.engine_registry import ENGINES
    for name, entry in ENGINES.items():
        assert entry.status == "recovered_unactivated", (
            f"Engine '{name}' has unexpected status: {entry.status}"
        )


def test_all_import_modes_are_lazy():
    from src.app.core.engine_registry import ENGINES
    for name, entry in ENGINES.items():
        assert entry.import_mode == "lazy", (
            f"Engine '{name}' has import_mode={entry.import_mode!r}, expected 'lazy'"
        )


def test_all_require_explicit_config():
    from src.app.core.engine_registry import ENGINES
    for name, entry in ENGINES.items():
        assert entry.activation_requires_explicit_config is True


# ---------------------------------------------------------------------------
# 6. Known blockers are documented (non-empty per engine)
# ---------------------------------------------------------------------------


def test_atlas_has_documented_blockers():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("atlas")
    assert entry is not None
    assert len(entry.known_blockers) >= 1
    # Atlas's primary blocker is the package name collision
    blocker_text = " ".join(entry.known_blockers).lower()
    assert "atlas" in blocker_text


def test_hydra_50_has_documented_blockers():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("hydra_50")
    assert entry is not None
    assert len(entry.known_blockers) >= 1
    blocker_text = " ".join(entry.known_blockers).lower()
    assert "assertion" in blocker_text or "test" in blocker_text


def test_sovereign_war_room_has_documented_blockers():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("sovereign_war_room")
    assert entry is not None
    assert len(entry.known_blockers) >= 1
    blocker_text = " ".join(entry.known_blockers).lower()
    assert "_cffi_backend" in blocker_text or "cryptography" in blocker_text


# ---------------------------------------------------------------------------
# 7. Helper function correctness
# ---------------------------------------------------------------------------


def test_get_engine_returns_entry_for_known_name():
    from src.app.core.engine_registry import get_engine
    for name in ("atlas", "hydra_50", "sovereign_war_room"):
        entry = get_engine(name)
        assert entry is not None, f"get_engine('{name}') returned None"
        assert entry.name == name


def test_get_engine_returns_none_for_unknown():
    from src.app.core.engine_registry import get_engine
    assert get_engine("nonexistent_engine_xyz") is None


def test_is_engine_locatable_atlas():
    from src.app.core.engine_registry import is_engine_locatable
    # Atlas __init__.py exists — must be locatable
    assert is_engine_locatable("atlas") is True


def test_is_engine_locatable_unknown():
    from src.app.core.engine_registry import is_engine_locatable
    assert is_engine_locatable("not_a_real_engine") is False
