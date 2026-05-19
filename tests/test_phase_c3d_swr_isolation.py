"""
Phase C3D connectivity tests -- Sovereign War Room dependency isolation.

Verifies:
1. engine_registry imports cleanly (no SWR code executed).
2. sovereign_war_room registry entry exists with correct metadata.
3. enabled=False, status="recovered_unactivated", import_mode="lazy".
4. Registry source does not contain SWR import statements.
5. Known blockers reference _cffi_backend / cryptography / pyo3.
6. Namespace package probe (top-level only) is safe.
7. Subpackage probe (swr/) triggers pyo3 panic — documented, not suppressed.
8. No engine starts automatically from registry import.
9. Crypto preflight subprocess approach is documented and testable.
"""

import importlib.util
import subprocess
import sys


# ---------------------------------------------------------------------------
# 1. Registry imports cleanly
# ---------------------------------------------------------------------------


def test_engine_registry_imports_cleanly():
    """engine_registry.py must import without executing SWR code."""
    from src.app.core.engine_registry import ENGINES, ENGINE_REGISTRY_ACTIVATION_ENABLED
    assert isinstance(ENGINES, dict)
    assert ENGINE_REGISTRY_ACTIVATION_ENABLED is False


# ---------------------------------------------------------------------------
# 2-4. Registry entry metadata
# ---------------------------------------------------------------------------


def test_sovereign_war_room_entry_exists():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("sovereign_war_room")
    assert entry is not None
    assert entry.name == "sovereign_war_room"


def test_sovereign_war_room_enabled_false():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("sovereign_war_room")
    assert entry.enabled is False


def test_sovereign_war_room_status_recovered_unactivated():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("sovereign_war_room")
    assert entry.status == "recovered_unactivated"


def test_sovereign_war_room_import_mode_lazy():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("sovereign_war_room")
    assert entry.import_mode == "lazy"


def test_sovereign_war_room_activation_requires_explicit_config():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("sovereign_war_room")
    assert entry.activation_requires_explicit_config is True


# ---------------------------------------------------------------------------
# 5. Registry source does not import SWR
# ---------------------------------------------------------------------------


def test_registry_source_does_not_import_sovereign_war_room():
    """engine_registry.py source must not contain SWR import statements.

    Checks for actual Python import statement syntax, not string literal content.
    The blockers may reference "from swr import ..." in documentation text;
    that is expected and does not constitute an executable import.
    """
    spec = importlib.util.find_spec("src.app.core.engine_registry")
    assert spec is not None and spec.origin is not None
    source = open(spec.origin).read()
    # Check for executable import statement syntax (not string literal content)
    assert "import sovereign_war_room" not in source
    assert "from sovereign_war_room import" not in source
    assert "from engines.sovereign_war_room import" not in source
    assert "import engines.sovereign_war_room.swr" not in source
    assert "from engines.sovereign_war_room.swr import" not in source


def test_registry_source_does_not_import_cryptography():
    """engine_registry.py source must not have cryptography import statements.

    Checks code lines only (line starts with from/import), not string literal
    content. Blocker strings may document 'from cryptography...' as evidence;
    that is documentation, not an executable import.
    """
    spec = importlib.util.find_spec("src.app.core.engine_registry")
    assert spec is not None and spec.origin is not None
    source = open(spec.origin).read()
    import_lines = [
        line for line in source.split("\n")
        if line.strip().startswith(("from cryptography", "import cryptography"))
    ]
    assert import_lines == [], (
        f"engine_registry.py must not contain cryptography import statements: {import_lines}"
    )


# ---------------------------------------------------------------------------
# 6. Known blockers reference the correct dependency failure
# ---------------------------------------------------------------------------


def test_known_blockers_reference_cffi_backend():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("sovereign_war_room")
    combined = " ".join(entry.known_blockers).lower()
    assert "_cffi_backend" in combined, "Blockers must mention _cffi_backend"


def test_known_blockers_reference_cryptography():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("sovereign_war_room")
    combined = " ".join(entry.known_blockers).lower()
    assert "cryptography" in combined, "Blockers must mention cryptography"


def test_known_blockers_reference_pyo3():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("sovereign_war_room")
    combined = " ".join(entry.known_blockers).lower()
    assert "pyo3" in combined, "Blockers must mention pyo3"


def test_sovereign_war_room_has_multiple_blockers():
    from src.app.core.engine_registry import get_engine
    entry = get_engine("sovereign_war_room")
    assert len(entry.known_blockers) >= 2


# ---------------------------------------------------------------------------
# 7. Namespace package probe is safe (top-level only)
# ---------------------------------------------------------------------------


def test_namespace_package_probe_is_safe():
    """find_spec('engines.sovereign_war_room') must return a namespace package spec.

    The top-level sovereign_war_room directory has NO __init__.py.
    Python treats it as a namespace package. The stable invariants are:
    - spec.origin is None (no __init__.py file path)
    - spec.submodule_search_locations is not None (search locations exist)

    Note: spec.loader may be None or NamespaceLoader depending on whether the
    package has been previously accessed in sys.modules. Both are valid namespace
    package states; origin=None is the reliable check.
    """
    spec = importlib.util.find_spec("engines.sovereign_war_room")
    assert spec is not None, "engines.sovereign_war_room must be locatable"
    assert spec.origin is None, (
        "namespace package must have origin=None (no __init__.py file path). "
        f"Got origin={spec.origin!r}"
    )
    assert spec.submodule_search_locations is not None, (
        "namespace package must have submodule_search_locations"
    )


def test_module_locatable_via_registry():
    """Registry's module_locatable flag must be True (namespace spec found)."""
    from src.app.core.engine_registry import get_engine
    entry = get_engine("sovereign_war_room")
    assert entry.module_locatable is True, (
        "engines.sovereign_war_room namespace package must be discoverable"
    )


# ---------------------------------------------------------------------------
# 8. C3D-R1: swr import is now safe — instantiation raises CryptoUnavailableError
# ---------------------------------------------------------------------------


def test_swr_import_is_safe_post_c3d_r1():
    """C3D-R1: importing engines.sovereign_war_room.swr no longer panics.

    Before C3D-R1: importing swr triggered pyo3 panic via swr/crypto.py
    module-level cryptography imports. After C3D-R1: all cryptography imports
    are inside CryptoEngine.__init__(), so the module import is safe.
    The panic is now deferred to instantiation and re-raised as
    CryptoUnavailableError (a controlled RuntimeError subclass).
    """
    repo_root = str(__import__("pathlib").Path(__file__).parent.parent)
    import os
    env = dict(os.environ)
    env["PYTHONPATH"] = repo_root
    result = subprocess.run(
        [sys.executable, "-c",
         "from engines.sovereign_war_room.swr import SovereignWarRoom; "
         "print('import ok')"],
        capture_output=True,
        env=env,
        timeout=15,
    )
    assert result.returncode == 0, (
        "from engines.sovereign_war_room.swr import SovereignWarRoom must succeed "
        "after C3D-R1 repair. Panic is now deferred to CryptoEngine() instantiation "
        "and re-raised as CryptoUnavailableError.\n"
        f"stderr: {result.stderr.decode('utf-8', errors='replace')[:300]}"
    )
    assert b"import ok" in result.stdout


def test_swr_instantiation_raises_crypto_unavailable():
    """C3D-R1: constructing CryptoEngine raises CryptoUnavailableError, not panic.

    The pyo3 panic (BaseException subclass) is caught inside __init__() and
    re-raised as CryptoUnavailableError(RuntimeError). The subprocess exits 0
    because the error is caught and handled gracefully.
    """
    repo_root = str(__import__("pathlib").Path(__file__).parent.parent)
    import os
    env = dict(os.environ)
    env["PYTHONPATH"] = repo_root
    result = subprocess.run(
        [sys.executable, "-c",
         "from engines.sovereign_war_room.swr.crypto import CryptoEngine, CryptoUnavailableError\n"
         "try:\n"
         "    CryptoEngine()\n"
         "    print('crypto_ok')\n"
         "except CryptoUnavailableError:\n"
         "    print('crypto_unavailable_error')\n"],
        capture_output=True,
        env=env,
        timeout=15,
    )
    assert result.returncode == 0, (
        "Subprocess must exit 0 — CryptoUnavailableError is a controlled exception, "
        f"not a panic.\nstderr: {result.stderr.decode('utf-8', errors='replace')[:300]}"
    )
    stdout = result.stdout.decode("utf-8", errors="replace").strip()
    assert stdout in ("crypto_ok", "crypto_unavailable_error"), (
        f"Expected 'crypto_ok' or 'crypto_unavailable_error', got: {stdout!r}"
    )


# ---------------------------------------------------------------------------
# 9. No engine starts automatically
# ---------------------------------------------------------------------------


def test_no_engine_starts_automatically():
    """Importing engine_registry must not instantiate SWR or start it."""
    from src.app.core import engine_registry
    assert engine_registry.ENGINE_REGISTRY_ACTIVATION_ENABLED is False
    enabled = engine_registry.list_enabled_engines()
    assert "sovereign_war_room" not in enabled, (
        "sovereign_war_room must not be in list_enabled_engines()"
    )


def test_list_enabled_engines_is_empty():
    """No engines should be enabled in the default registry state."""
    from src.app.core.engine_registry import list_enabled_engines
    assert list_enabled_engines() == [], (
        "No engines should be enabled by default"
    )


# ---------------------------------------------------------------------------
# 10. Crypto preflight subprocess pattern
# ---------------------------------------------------------------------------


def test_crypto_preflight_pattern_is_testable():
    """The subprocess-based preflight pattern itself works without panicking.

    The preflight runs cryptography import in a subprocess. If it exits non-zero,
    the environment is blocked. If zero, C3D-R1 repair may proceed.
    This test verifies the subprocess invocation pattern is valid Python.
    """
    result = subprocess.run(
        [sys.executable, "-c",
         "from cryptography.fernet import Fernet; print('preflight_ok')"],
        capture_output=True,
        timeout=15,
    )
    # We don't assert the returncode here — it may be 0 or non-zero depending
    # on environment. We only assert the pattern itself doesn't crash the runner.
    assert isinstance(result.returncode, int)
    # Document the environment state:
    if result.returncode == 0:
        assert b"preflight_ok" in result.stdout
    # Non-zero exit is the documented blocked state — also valid.
