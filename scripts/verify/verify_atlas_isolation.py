"""
Phase C3B — Atlas Import Isolation Verifier

Provides an isolated sys.path context manager that temporarily adds the repo
root so 'from atlas.*' imports resolve correctly, then restores sys.path on exit.

Rules:
- sys.path is NEVER mutated globally.
- The context manager restores the original sys.path on exit (even on exception).
- engines/ is NEVER added to sys.path (would shadow atlas/ with engines/atlas/).
- This module does NOT import Atlas itself; it only provides the safe mechanism.
"""

from __future__ import annotations

import importlib
import importlib.util
import sys
from contextlib import contextmanager
from pathlib import Path

# Repo root is the parent of this script's directory's parent
_REPO_ROOT = str(Path(__file__).parent.parent.parent.resolve())


@contextmanager
def atlas_isolated_import():
    """Context manager for safe Atlas import with isolated sys.path.

    Temporarily prepends the repo root to sys.path so 'from atlas.*' imports
    resolve to the authoritative atlas/ package, then restores sys.path on exit.

    Usage:
        with atlas_isolated_import():
            import atlas
            kernel = atlas.get_constitutional_kernel()

    Invariants:
    - sys.path is restored exactly to its pre-entry state after the block.
    - The repo root is prepended (not appended) so it takes precedence.
    - engines/ is not added; atlas/ (top-level) is the correct resolution target.
    - Modules imported inside the block remain in sys.modules after exit.
      To fully isolate, caller must remove them from sys.modules manually.
    """
    original_path = sys.path[:]
    if _REPO_ROOT not in sys.path:
        sys.path.insert(0, _REPO_ROOT)
    try:
        yield
    finally:
        sys.path[:] = original_path


def probe_atlas_locatable() -> dict:
    """Return a dict describing Atlas discoverability without importing it.

    Safe to call at any time — uses find_spec only, never exec's modules.
    """
    result = {
        "repo_root": _REPO_ROOT,
        "atlas_top_level_spec": None,
        "engines_atlas_spec": None,
        "atlas_locatable": False,
        "engines_atlas_locatable": False,
        "collision_risk": "none",
    }

    try:
        spec = importlib.util.find_spec("atlas")
        if spec is not None:
            result["atlas_top_level_spec"] = spec.origin
            result["atlas_locatable"] = True
    except (ModuleNotFoundError, ValueError):
        pass

    try:
        spec2 = importlib.util.find_spec("engines.atlas")
        if spec2 is not None:
            result["engines_atlas_spec"] = spec2.origin
            result["engines_atlas_locatable"] = True
    except (ModuleNotFoundError, ValueError):
        pass

    if result["atlas_locatable"] and result["engines_atlas_locatable"]:
        result["collision_risk"] = "structural_mirror_only"
    elif result["atlas_locatable"]:
        result["collision_risk"] = "none"

    return result


def assert_no_engines_dir_on_syspath() -> None:
    """Assert engines/ is not in sys.path, raise AssertionError if it is."""
    engines_dir = str(Path(_REPO_ROOT) / "engines")
    for entry in sys.path:
        if Path(entry).resolve() == Path(engines_dir).resolve():
            raise AssertionError(
                f"engines/ is on sys.path: {entry!r} — this shadows atlas/ with "
                f"engines/atlas/ and must not be added globally."
            )


if __name__ == "__main__":
    import json

    print("=== Atlas Isolation Probe ===\n")

    assert_no_engines_dir_on_syspath()
    print("PASS: engines/ is not on sys.path globally\n")

    probe = probe_atlas_locatable()
    print("Probe results:")
    print(json.dumps(probe, indent=2))

    print("\nTesting sys.path isolation context manager...")
    path_before = sys.path[:]
    with atlas_isolated_import():
        path_inside = sys.path[:]
        print(f"  sys.path[0] inside context: {sys.path[0]}")
        assert sys.path[0] == _REPO_ROOT or _REPO_ROOT in sys.path
    path_after = sys.path[:]
    assert path_before == path_after, "sys.path was not restored!"
    print("PASS: sys.path restored after context exit\n")

    print("All isolation checks passed.")
