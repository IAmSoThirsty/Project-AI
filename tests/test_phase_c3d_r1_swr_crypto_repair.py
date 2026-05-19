"""
Phase C3D-R1 tests -- Sovereign War Room crypto import repair.

Verifies the structural fix applied to engines/sovereign_war_room/swr/crypto.py:
  - All 4 cryptography.* module-level imports moved inside CryptoEngine.__init__().
  - CryptoUnavailableError added as a controlled RuntimeError subclass.
  - pyo3_runtime.PanicException (BaseException) caught and re-raised cleanly.

Required proof:
1. find_spec('engines.sovereign_war_room.swr') remains safe.
2. Importing swr.crypto no longer panics.
3. CryptoUnavailableError is defined and is a RuntimeError subclass.
4. Constructing CryptoEngine fails safely if crypto backend is missing/broken.
5. crypto.py has no module-level cryptography import statements.
6. No SWR engine starts automatically.
7. engine_registry still imports with no SWR side effects.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = str(Path(__file__).parent.parent)
_SWR_ENV = {**os.environ, "PYTHONPATH": _REPO_ROOT}


# ---------------------------------------------------------------------------
# 1. find_spec safety
# ---------------------------------------------------------------------------


def test_find_spec_swr_namespace_safe():
    """find_spec('engines.sovereign_war_room') still returns namespace spec.

    spec.origin is None (no __init__.py). spec.loader may be None or
    NamespaceLoader depending on sys.modules cache state — both are valid.
    """
    spec = importlib.util.find_spec("engines.sovereign_war_room")
    assert spec is not None
    assert spec.origin is None, f"namespace package must have origin=None, got {spec.origin!r}"
    assert spec.submodule_search_locations is not None


def test_find_spec_swr_subpackage_safe():
    """find_spec('engines.sovereign_war_room.swr') does not execute __init__.py.

    In Python 3.12 this was already safe (deferred init for namespace-package
    subpackage discovery). C3D-R1 makes the actual IMPORT safe too.
    """
    result = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, '.'); import importlib.util; "
         "s = importlib.util.find_spec('engines.sovereign_war_room.swr'); "
         "print('ok' if s else 'none')"],
        capture_output=True, env=_SWR_ENV, timeout=15,
    )
    assert result.returncode == 0
    assert b"ok" in result.stdout


# ---------------------------------------------------------------------------
# 2. Module-level import of swr.crypto is now safe
# ---------------------------------------------------------------------------


def test_import_swr_crypto_module_does_not_panic():
    """Importing swr.crypto no longer triggers pyo3 panic."""
    result = subprocess.run(
        [sys.executable, "-c",
         "from engines.sovereign_war_room.swr.crypto import CryptoEngine, CryptoUnavailableError; "
         "print('import ok')"],
        capture_output=True, env=_SWR_ENV, timeout=15,
    )
    assert result.returncode == 0, (
        f"swr.crypto import must succeed after C3D-R1. "
        f"stderr: {result.stderr.decode('utf-8', errors='replace')[:400]}"
    )
    assert b"import ok" in result.stdout


def test_import_swr_package_does_not_panic():
    """Importing the full swr package no longer triggers pyo3 panic."""
    result = subprocess.run(
        [sys.executable, "-c",
         "from engines.sovereign_war_room.swr import SovereignWarRoom, CryptoEngine; "
         "print('import ok')"],
        capture_output=True, env=_SWR_ENV, timeout=15,
    )
    assert result.returncode == 0, (
        f"swr package import must succeed after C3D-R1. "
        f"stderr: {result.stderr.decode('utf-8', errors='replace')[:400]}"
    )
    assert b"import ok" in result.stdout


# ---------------------------------------------------------------------------
# 3. CryptoUnavailableError is correctly defined
# ---------------------------------------------------------------------------


def test_crypto_unavailable_error_is_importable():
    """CryptoUnavailableError must be importable from swr.crypto."""
    result = subprocess.run(
        [sys.executable, "-c",
         "from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError; "
         "print('ok')"],
        capture_output=True, env=_SWR_ENV, timeout=15,
    )
    assert result.returncode == 0
    assert b"ok" in result.stdout


def test_crypto_unavailable_error_is_runtime_error_subclass():
    """CryptoUnavailableError must be a RuntimeError subclass."""
    result = subprocess.run(
        [sys.executable, "-c",
         "from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError; "
         "assert issubclass(CryptoUnavailableError, RuntimeError), "
         "'CryptoUnavailableError must subclass RuntimeError'; "
         "print('ok')"],
        capture_output=True, env=_SWR_ENV, timeout=15,
    )
    assert result.returncode == 0, (
        result.stderr.decode("utf-8", errors="replace")[:300]
    )
    assert b"ok" in result.stdout


# ---------------------------------------------------------------------------
# 4. Constructing CryptoEngine fails safely (controlled error, not panic)
# ---------------------------------------------------------------------------


def test_cryptoengine_instantiation_raises_controlled_error():
    """CryptoEngine() raises CryptoUnavailableError if backend is broken.

    The pyo3 panic (BaseException subclass) is now caught inside __init__()
    and re-raised as CryptoUnavailableError. The subprocess exits 0 because
    the exception is handled — no more uncatchable pyo3 panic.
    """
    result = subprocess.run(
        [sys.executable, "-c",
         "from engines.sovereign_war_room.swr.crypto import CryptoEngine, CryptoUnavailableError\n"
         "try:\n"
         "    CryptoEngine()\n"
         "    print('crypto_available')\n"
         "except CryptoUnavailableError as e:\n"
         "    print(f'controlled_error:{type(e).__name__}')\n"
         "except Exception as e:\n"
         "    print(f'unexpected_exception:{type(e).__name__}')\n"],
        capture_output=True, env=_SWR_ENV, timeout=15,
    )
    assert result.returncode == 0, (
        "Subprocess must exit 0 — CryptoUnavailableError is a controlled "
        "RuntimeError, not a panic.\n"
        f"stderr: {result.stderr.decode('utf-8', errors='replace')[:300]}"
    )
    stdout = result.stdout.decode("utf-8", errors="replace").strip()
    assert "unexpected_exception" not in stdout, (
        f"Must not raise unexpected exception: {stdout!r}"
    )
    # Either crypto is available (clean env) or CryptoUnavailableError raised (blocked env)
    assert stdout.startswith("crypto_available") or stdout.startswith("controlled_error"), (
        f"Expected controlled outcome, got: {stdout!r}"
    )


def test_cryptoengine_instantiation_not_uncatchable_panic():
    """The pyo3 PanicException is now caught inside __init__ — not a process crash."""
    result = subprocess.run(
        [sys.executable, "-c",
         "from engines.sovereign_war_room.swr.crypto import CryptoEngine, CryptoUnavailableError\n"
         "try:\n"
         "    CryptoEngine()\n"
         "except CryptoUnavailableError:\n"
         "    pass\n"
         "except Exception:\n"
         "    pass\n"
         "print('process survived')"],
        capture_output=True, env=_SWR_ENV, timeout=15,
    )
    assert result.returncode == 0
    assert b"process survived" in result.stdout


# ---------------------------------------------------------------------------
# 5. crypto.py has no module-level cryptography import statements
# ---------------------------------------------------------------------------


def test_crypto_py_has_no_module_level_cryptography_imports():
    """crypto.py must not have cryptography.* imports at module scope.

    Only stdlib imports (hashlib, hmac, json, secrets, datetime, typing)
    are allowed at module scope. All cryptography.* imports must be inside
    CryptoEngine.__init__(). Module-level imports have no leading indentation;
    imports inside methods are indented with 8+ spaces.
    """
    spec = importlib.util.find_spec("engines.sovereign_war_room.swr.crypto")
    assert spec is not None and spec.origin is not None
    source = open(spec.origin).read()
    # Check for lines with NO leading whitespace that start with cryptography imports.
    # Indented imports (inside __init__) will have leading spaces and won't match.
    import_lines = [
        line for line in source.split("\n")
        if line.startswith(("from cryptography", "import cryptography"))
    ]
    assert import_lines == [], (
        f"crypto.py must have no module-level cryptography imports: {import_lines}"
    )


def test_crypto_py_has_stdlib_imports_only_at_module_level():
    """crypto.py module-level imports must be stdlib only."""
    spec = importlib.util.find_spec("engines.sovereign_war_room.swr.crypto")
    assert spec is not None and spec.origin is not None
    source = open(spec.origin).read()
    allowed_prefixes = (
        "import hashlib", "import hmac", "import json", "import secrets",
        "from datetime", "from typing", "from __future__",
    )
    module_level_imports = []
    in_class = False
    for line in source.split("\n"):
        stripped = line.strip()
        if stripped.startswith("class ") or stripped.startswith("def "):
            in_class = True
        if not in_class and stripped.startswith(("import ", "from ")):
            module_level_imports.append(stripped)

    for imp in module_level_imports:
        assert any(imp.startswith(p) for p in allowed_prefixes), (
            f"Unexpected module-level import: {imp!r}"
        )


# ---------------------------------------------------------------------------
# 6. No engine starts automatically
# ---------------------------------------------------------------------------


def test_no_engine_starts_automatically():
    """Registry import must not instantiate SWR."""
    from src.app.core.engine_registry import (
        ENGINE_REGISTRY_ACTIVATION_ENABLED,
        list_enabled_engines,
        get_engine,
    )
    assert ENGINE_REGISTRY_ACTIVATION_ENABLED is False
    assert "sovereign_war_room" not in list_enabled_engines()
    entry = get_engine("sovereign_war_room")
    assert entry.enabled is False
    assert entry.status == "recovered_unactivated"


# ---------------------------------------------------------------------------
# 7. engine_registry has no SWR side effects
# ---------------------------------------------------------------------------


def test_engine_registry_source_has_no_swr_import_statements():
    """engine_registry.py must not contain SWR executable import statements."""
    spec = importlib.util.find_spec("src.app.core.engine_registry")
    assert spec is not None and spec.origin is not None
    source = open(spec.origin).read()
    import_lines = [
        line for line in source.split("\n")
        if line.strip().startswith(("from cryptography", "import cryptography",
                                    "from engines.sovereign_war_room.swr",
                                    "import engines.sovereign_war_room.swr"))
    ]
    assert import_lines == [], (
        f"engine_registry.py must not have SWR/crypto import statements: {import_lines}"
    )


def test_engine_registry_imports_cleanly():
    """Importing engine_registry must not trigger any SWR or crypto code."""
    from src.app.core.engine_registry import ENGINES, ENGINE_REGISTRY_ACTIVATION_ENABLED
    assert isinstance(ENGINES, dict)
    assert "sovereign_war_room" in ENGINES
    assert ENGINE_REGISTRY_ACTIVATION_ENABLED is False


# ---------------------------------------------------------------------------
# 8. Collection baseline not worsened
# ---------------------------------------------------------------------------


def test_c3d_r1_isolation_tests_all_pass():
    """C3D isolation test suite must still pass after C3D-R1 repair."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "tests/test_phase_c3d_swr_isolation.py", "-q", "--tb=short"],
        capture_output=True,
        cwd=_REPO_ROOT,
        timeout=60,
    )
    output = result.stdout.decode("utf-8", errors="replace")
    assert result.returncode == 0, (
        f"C3D isolation tests must pass after C3D-R1.\n{output[-1000:]}"
    )
    assert "failed" not in output.lower() or "0 failed" in output.lower()
