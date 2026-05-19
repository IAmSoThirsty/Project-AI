"""
Phase C3B connectivity tests — Atlas import isolation.

Verifies:
1. Engine registry imports without triggering any Atlas module import.
2. Atlas entry exists in registry, disabled by default.
3. AtlasIsolatedContext restores sys.path after exit (no global PYTHONPATH leak).
4. engines/ directory is never on sys.path globally.
5. Atlas collision audit: find_spec probes work without importing Atlas.
6. Registry atlas known_blockers document all C3B findings.
7. verify_atlas_isolation.py probe function works without importing Atlas.
"""

import sys
import importlib.util
from pathlib import Path

# Repo root — used in collision path checks
_REPO_ROOT = str(Path(__file__).parent.parent.resolve())
_ENGINES_DIR = str(Path(_REPO_ROOT) / "engines")


# ---------------------------------------------------------------------------
# 1. Registry imports without Atlas side effects
# ---------------------------------------------------------------------------


def test_engine_registry_imports_without_atlas():
    """Importing engine_registry must not trigger any atlas.* module load."""
    import src.app.core.engine_registry  # noqa: F401
    atlas_mods = [k for k in sys.modules if k.startswith("atlas.") or k == "atlas"]
    assert not atlas_mods, (
        f"atlas modules were imported during registry load: {atlas_mods}"
    )


def test_engine_registry_imports_without_engines_atlas():
    """Importing engine_registry must not trigger any engines.atlas.* module load."""
    import src.app.core.engine_registry  # noqa: F401
    ea_mods = [k for k in sys.modules if k.startswith("engines.atlas")]
    assert not ea_mods, (
        f"engines.atlas modules were imported during registry load: {ea_mods}"
    )


# ---------------------------------------------------------------------------
# 2. Atlas entry exists and is disabled
# ---------------------------------------------------------------------------


def test_atlas_entry_exists_in_registry():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("atlas")
    assert entry is not None
    assert entry.name == "atlas"


def test_atlas_entry_disabled_by_default():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("atlas")
    assert entry.enabled is False


def test_atlas_entry_status_recovered_unactivated():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("atlas")
    assert entry.status == "recovered_unactivated"


def test_atlas_entry_import_mode_lazy():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("atlas")
    assert entry.import_mode == "lazy"


def test_atlas_entry_requires_explicit_config():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("atlas")
    assert entry.activation_requires_explicit_config is True


# ---------------------------------------------------------------------------
# 3. AtlasIsolatedContext restores sys.path
# ---------------------------------------------------------------------------


def test_atlas_isolated_context_restores_syspath():
    """sys.path must be identical before and after atlas_isolated_import()."""
    from scripts.verify.verify_atlas_isolation import atlas_isolated_import

    path_before = sys.path[:]
    with atlas_isolated_import():
        # Inside: repo root should be accessible
        pass
    path_after = sys.path[:]

    assert path_before == path_after, (
        "sys.path was not restored after atlas_isolated_import() exit"
    )


def test_atlas_isolated_context_restores_syspath_on_exception():
    """sys.path must be restored even if the block raises."""
    from scripts.verify.verify_atlas_isolation import atlas_isolated_import

    path_before = sys.path[:]
    try:
        with atlas_isolated_import():
            raise RuntimeError("simulated failure inside isolated context")
    except RuntimeError:
        pass
    path_after = sys.path[:]

    assert path_before == path_after, (
        "sys.path was not restored after exception inside atlas_isolated_import()"
    )


# ---------------------------------------------------------------------------
# 4. engines/ is not on sys.path globally
# ---------------------------------------------------------------------------


def test_engines_dir_not_on_global_syspath():
    """engines/ must never be added to sys.path globally."""
    from scripts.verify.verify_atlas_isolation import assert_no_engines_dir_on_syspath
    # This raises AssertionError if engines/ is on sys.path — should not raise
    assert_no_engines_dir_on_syspath()


def test_engines_subdir_not_on_syspath_raw():
    """Raw check: no sys.path entry resolves to T:/Project-AI-main/engines."""
    engines_resolved = Path(_ENGINES_DIR).resolve()
    for entry in sys.path:
        try:
            entry_resolved = Path(entry).resolve()
        except (ValueError, OSError):
            continue
        assert entry_resolved != engines_resolved, (
            f"engines/ is on sys.path: {entry!r}"
        )


# ---------------------------------------------------------------------------
# 5. find_spec probes work without importing Atlas
# ---------------------------------------------------------------------------


def test_probe_atlas_locatable_does_not_import_atlas():
    """probe_atlas_locatable() uses find_spec only — no import side effects."""
    from scripts.verify.verify_atlas_isolation import probe_atlas_locatable

    mods_before = set(sys.modules.keys())
    result = probe_atlas_locatable()
    mods_after = set(sys.modules.keys())

    new_atlas_mods = {
        k for k in (mods_after - mods_before)
        if k == "atlas" or k.startswith("atlas.")
    }
    assert not new_atlas_mods, (
        f"probe_atlas_locatable() imported atlas modules: {new_atlas_mods}"
    )
    # Result should have expected keys
    assert "atlas_locatable" in result
    assert "collision_risk" in result


# ---------------------------------------------------------------------------
# 6. Registry atlas blockers document C3B findings
# ---------------------------------------------------------------------------


def test_atlas_blockers_document_numpy_blocker():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("atlas")
    combined = " ".join(entry.known_blockers).lower()
    assert "numpy" in combined, "Atlas blockers should document numpy unavailability"


def test_atlas_blockers_document_jsonschema_blocker():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("atlas")
    combined = " ".join(entry.known_blockers).lower()
    assert "jsonschema" in combined, "Atlas blockers should document jsonschema breakage"


def test_atlas_blockers_document_engines_path_collision():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("atlas")
    combined = " ".join(entry.known_blockers).lower()
    assert "engines/" in combined or "sys.path" in combined, (
        "Atlas blockers should document engines/ path collision risk"
    )


def test_atlas_has_multiple_blockers():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("atlas")
    assert len(entry.known_blockers) >= 5, (
        f"Expected at least 5 C3B blockers documented, got {len(entry.known_blockers)}"
    )
