"""
Sovereign War Room — Explicit Activation Contract
==================================================
Phase C3D-R3. 2026-05-19.

Defines the ONLY permitted path to activate SovereignWarRoom.
Importing this module does NOT activate SWR.
Calling activate_swr() does NOT activate SWR unless ALL gates pass.

Activation requires ALL of the following simultaneously:
  1. ENGINE_REGISTRY_ACTIVATION_ENABLED = True (engine_registry module-level flag)
  2. Registry entry sovereign_war_room.enabled = True
  3. Environment variable SWR_ACTIVATION_KEY is set to a non-empty string
  4. CryptoEngine() preflight succeeds (cffi/_cffi_backend available)

Activation is ALLOWED to:
  - Import the swr package
  - Construct SovereignWarRoom(bundle_dir=<explicit_path>)
  - Call load_scenarios()
  - Call execute_scenario()
  - Call verify_result_integrity()
  - Return the SovereignWarRoom instance to the caller

Activation is FORBIDDEN to:
  - Start a web server, API server, or network listener (Flask, FastAPI, uvicorn)
  - Open sockets, background threads, or subprocesses
  - Write to production databases, audit trails, or persistent state
  - Execute automatically on any import, find_spec, or registry lookup
  - Skip or weaken any preflight check
  - Swallow exceptions silently
  - Proceed if any gate is closed

Fail-closed invariant: any missing gate → SWRActivationError, no partial activation.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Environment variable key that must be set by an operator before activation.
# Value content is not checked — presence (non-empty) is sufficient as a
# deliberate operator action. Use a meaningful value like "c3d-r3-controlled".
SWR_ACTIVATION_ENV_KEY: str = "SWR_ACTIVATION_KEY"


class SWRActivationError(RuntimeError):
    """Raised when SWR activation is denied or a preflight check fails.

    Callers must catch this. All activation failure paths raise this class —
    the activation contract never silently succeeds or swallows failures.

    Callers may also catch RuntimeError to handle both this and
    CryptoUnavailableError from swr.crypto without explicit coupling.
    """


# ---------------------------------------------------------------------------
# Individual gate checks — each raises SWRActivationError on failure
# ---------------------------------------------------------------------------

def _check_registry_gate() -> None:
    """Gate 1: ENGINE_REGISTRY_ACTIVATION_ENABLED must be True."""
    from src.app.core import engine_registry
    if not engine_registry.ENGINE_REGISTRY_ACTIVATION_ENABLED:
        raise SWRActivationError(
            "Gate 1 CLOSED: ENGINE_REGISTRY_ACTIVATION_ENABLED is False. "
            "Set to True in src/app/core/engine_registry.py to open this gate."
        )


def _check_entry_enabled() -> None:
    """Gate 2: Registry entry sovereign_war_room.enabled must be True."""
    from src.app.core import engine_registry
    entry = engine_registry.get_engine("sovereign_war_room")
    if entry is None:
        raise SWRActivationError(
            "Gate 2 CLOSED: sovereign_war_room not found in engine registry."
        )
    if not entry.enabled:
        raise SWRActivationError(
            "Gate 2 CLOSED: Registry entry sovereign_war_room.enabled is False. "
            "Set enabled=True in engine_registry.ENGINES['sovereign_war_room'] "
            "to open this gate."
        )


def _check_activation_key() -> None:
    """Gate 3: SWR_ACTIVATION_KEY environment variable must be set and non-empty."""
    key = os.environ.get(SWR_ACTIVATION_ENV_KEY, "")
    if not key:
        raise SWRActivationError(
            f"Gate 3 CLOSED: Environment variable {SWR_ACTIVATION_ENV_KEY!r} is not set "
            "or is empty. Set it to a non-empty value to confirm deliberate operator "
            "intent before activation."
        )


def _check_crypto_preflight() -> None:
    """Gate 4: CryptoEngine() must construct without error.

    Verifies cffi 1.17.1 (_cffi_backend) is available and cryptography
    can initialize its Rust extension without pyo3 panic.
    """
    try:
        from engines.sovereign_war_room.swr.crypto import (
            CryptoEngine,
            CryptoUnavailableError,
        )
    except (SystemExit, KeyboardInterrupt):
        raise
    except BaseException as exc:
        raise SWRActivationError(
            f"Gate 4 CLOSED: swr.crypto import failed during preflight — "
            f"{type(exc).__name__}: {exc}"
        ) from None

    try:
        CryptoEngine()
    except CryptoUnavailableError as exc:
        raise SWRActivationError(
            f"Gate 4 CLOSED: CryptoEngine preflight failed — {exc}. "
            "Install cffi<2 (cffi 1.17.1) to restore _cffi_backend."
        ) from None
    except (SystemExit, KeyboardInterrupt):
        raise
    except BaseException as exc:
        raise SWRActivationError(
            f"Gate 4 CLOSED: CryptoEngine preflight raised uncontrolled "
            f"{type(exc).__name__}: {exc}"
        ) from None


# ---------------------------------------------------------------------------
# Preflight runner — all gates in sequence
# ---------------------------------------------------------------------------

def run_preflight() -> dict[str, bool]:
    """Run all activation gates in order.

    Returns a dict of gate results (all True) if every gate passes.
    Raises SWRActivationError on the first gate that fails — never continues
    past a failed gate, never returns a partial result.
    """
    _check_registry_gate()
    _check_entry_enabled()
    _check_activation_key()
    _check_crypto_preflight()
    return {
        "registry_gate": True,
        "entry_enabled": True,
        "activation_key_set": True,
        "crypto_preflight": True,
    }


# ---------------------------------------------------------------------------
# Activation entrypoint — the only permitted path to a SovereignWarRoom instance
# ---------------------------------------------------------------------------

def activate_swr(bundle_dir: Path | None = None) -> Any:
    """Activate SovereignWarRoom after all gates pass.

    This is the ONLY permitted path to a SovereignWarRoom instance.
    It fails closed on any missing gate, failed preflight, or unexpected error.

    Args:
        bundle_dir: Required — directory for BundleManager. Prevents ./bundles/
                    from being created in the repo root. Pass a temp or dedicated
                    path (e.g., tempfile.mkdtemp() or a configured data dir).

    Returns:
        SovereignWarRoom instance ready for controlled use.

    Raises:
        SWRActivationError: If any gate is closed or preflight fails.
                            Always fails closed — never silently activates.
    """
    # All gates must pass — fails closed at the first failure
    run_preflight()

    # Import only after all gates pass
    try:
        from engines.sovereign_war_room.swr import SovereignWarRoom
        from engines.sovereign_war_room.swr.crypto import CryptoUnavailableError
    except (SystemExit, KeyboardInterrupt):
        raise
    except BaseException as exc:
        raise SWRActivationError(
            f"SWR import failed during activation — {type(exc).__name__}: {exc}"
        ) from None

    # Construct only after import succeeds
    try:
        swr = SovereignWarRoom(bundle_dir=bundle_dir)
    except CryptoUnavailableError as exc:
        raise SWRActivationError(
            f"SovereignWarRoom() construction failed — {exc}"
        ) from None
    except (SystemExit, KeyboardInterrupt):
        raise
    except BaseException as exc:
        raise SWRActivationError(
            f"SovereignWarRoom() raised uncontrolled {type(exc).__name__}: {exc}"
        ) from None

    return swr
