"""
SWR Isolation Verifier — Phase C3D

Safe probes for Sovereign War Room without triggering _cffi_backend/pyo3 panic.

Usage:
    python scripts/verify/verify_swr_isolation.py

Returns exit 0 if isolation is confirmed, exit 1 if any check fails.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = str(Path(__file__).parent.parent.parent)


def probe_swr_namespace_locatable() -> bool:
    """Safe: probe engines.sovereign_war_room namespace package only.

    The top-level sovereign_war_room directory has no __init__.py.
    find_spec returns a namespace spec with loader=None — no code executed.
    """
    try:
        spec = importlib.util.find_spec("engines.sovereign_war_room")
        return (
            spec is not None
            and spec.loader is None
            and spec.origin is None
        )
    except Exception:
        return False


def probe_swr_subpackage_is_blocked() -> bool:
    """Confirm engines.sovereign_war_room.swr triggers panic in subprocess.

    Runs the unsafe probe in an isolated subprocess so the pyo3 panic cannot
    crash the calling process. Returns True if the subprocess exits non-zero
    (confirming the blocker is still active).
    """
    result = subprocess.run(
        [sys.executable, "-c",
         "import importlib.util; "
         "importlib.util.find_spec('engines.sovereign_war_room.swr')"],
        capture_output=True,
        cwd=_REPO_ROOT,
        timeout=15,
    )
    return result.returncode != 0


def run_crypto_preflight() -> bool:
    """Run cryptography import preflight in a subprocess.

    Returns True if cryptography imports cleanly (C3D-R1 may proceed).
    Returns False if the import panics or fails (environment still blocked).
    """
    result = subprocess.run(
        [sys.executable, "-c",
         "from cryptography.fernet import Fernet; print('preflight_ok')"],
        capture_output=True,
        timeout=15,
    )
    return (
        result.returncode == 0
        and b"preflight_ok" in result.stdout
    )


def verify_registry_isolation() -> bool:
    """Verify engine_registry imports cleanly without loading SWR."""
    if _REPO_ROOT not in sys.path:
        sys.path.insert(0, _REPO_ROOT)
    try:
        from src.app.core.engine_registry import get_engine, ENGINE_REGISTRY_ACTIVATION_ENABLED
        entry = get_engine("sovereign_war_room")
        return (
            entry is not None
            and entry.enabled is False
            and entry.status == "recovered_unactivated"
            and ENGINE_REGISTRY_ACTIVATION_ENABLED is False
        )
    except Exception:
        return False


def main() -> int:
    results: list[tuple[str, bool, str]] = []

    results.append((
        "Namespace package locatable (engines.sovereign_war_room)",
        probe_swr_namespace_locatable(),
        "find_spec returns namespace spec with loader=None",
    ))

    results.append((
        "Registry isolation confirmed",
        verify_registry_isolation(),
        "engine_registry imports cleanly, SWR entry disabled",
    ))

    crypto_ok = run_crypto_preflight()
    results.append((
        "Crypto preflight (subprocess)",
        True,  # reporting the state, not asserting pass/fail
        f"cryptography imports cleanly: {crypto_ok} "
        f"({'C3D-R1 may proceed' if crypto_ok else 'BLOCKED — cffi missing'})",
    ))

    if not crypto_ok:
        blocked_confirmed = probe_swr_subpackage_is_blocked()
        results.append((
            "Subpackage probe confirms pyo3 panic (subprocess)",
            blocked_confirmed,
            "find_spec('engines.sovereign_war_room.swr') exits non-zero",
        ))

    all_pass = True
    for label, passed, note in results:
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"  [{status}] {label}")
        print(f"         {note}")

    print()
    if all_pass:
        print("SWR isolation confirmed. Engine is safely registered but not active.")
        if crypto_ok:
            print("Crypto preflight passed — C3D-R1 repair may proceed when ready.")
        else:
            print("Crypto preflight BLOCKED — install cffi before C3D-R1 repair.")
        return 0
    else:
        print("ISOLATION CHECK FAILED — review output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
