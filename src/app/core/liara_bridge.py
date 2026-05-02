"""
Liara Bridge — connects the governance pipeline to the Liara temporal enforcement guard.

Liara (cognition/liara_guard.py) is a crisis-response activation system:
- authorize_liara(role, ttl) grants a temporary crisis role
- revoke_liara(reason)       revokes the active role
- check_liara_state()        auto-revokes if TTL has expired

This bridge:
1. Exposes a single pre-execution invariant (liara_ttl_check) that auto-revokes
   any expired Liara authorization before each action runs.
2. Provides get_liara_context() so the execution_router can inject Liara state
   into the context dict — making it visible to Triumvirate and OctoReflex.
3. Gracefully degrades to a no-op when the cognition package is not on sys.path
   (e.g., during unit tests that only add src/ to PYTHONPATH).
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Dynamic import — cognition/ lives at the repo root, not under src/.
# Add repo root if needed.
# ---------------------------------------------------------------------------

def _ensure_cognition_on_path() -> None:
    repo_root = str(Path(__file__).resolve().parents[4])  # src/app/core/.. → repo root
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


_liara_available = False
_check_liara_state = None
_authorize_liara = None
_revoke_liara = None
_LiaraState_ref = None

try:
    _ensure_cognition_on_path()
    from cognition.liara_guard import (  # type: ignore[import]
        LiaraState,
        STATE as _LIARA_STATE,
        authorize_liara as _authorize_liara,
        check_liara_state as _check_liara_state,
        revoke_liara as _revoke_liara,
    )
    _LiaraState_ref = _LIARA_STATE
    _liara_available = True
    logger.info("LiaraBridge: cognition.liara_guard loaded")
except (ImportError, Exception) as _e:
    logger.debug("LiaraBridge: cognition not available — stub mode (%s)", _e)


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def liara_ttl_check(context: Dict[str, Any]) -> bool:
    """
    Pre-execution invariant: auto-revoke Liara if TTL expired.

    Always returns True (never blocks) — it is a side-effect invariant.
    The actual blocking of unauthorized actions is handled by OctoReflex
    rules that read the injected context flags.
    """
    if _liara_available and _check_liara_state is not None:
        try:
            _check_liara_state()
        except Exception as exc:
            logger.error("liara_ttl_check: %s", exc)
    return True


def get_liara_context() -> Dict[str, Any]:
    """
    Return current Liara state for context injection.

    Keys injected:
      liara_active (bool)  — whether a crisis role is currently active
      liara_role   (str|None) — the active role name
    """
    if not _liara_available or _LiaraState_ref is None:
        return {"liara_active": False, "liara_role": None}

    try:
        from datetime import datetime
        state = _LiaraState_ref
        active = (
            state.active_role is not None
            and state.expires_at is not None
            and datetime.utcnow() < state.expires_at
        )
        return {
            "liara_active": active,
            "liara_role": state.active_role if active else None,
        }
    except Exception as exc:
        logger.error("get_liara_context: %s", exc)
        return {"liara_active": False, "liara_role": None}


def activate_liara(role: str, ttl_seconds: int = 900) -> bool:
    """Activate Liara for a crisis role (delegates to authorize_liara)."""
    if not _liara_available or _authorize_liara is None:
        return False
    try:
        return bool(_authorize_liara(role, ttl_seconds))
    except Exception as exc:
        logger.error("activate_liara: %s", exc)
        return False


def deactivate_liara(reason: str = "manual") -> bool:
    """Deactivate Liara (delegates to revoke_liara)."""
    if not _liara_available or _revoke_liara is None:
        return False
    try:
        return bool(_revoke_liara(reason))
    except Exception as exc:
        logger.error("deactivate_liara: %s", exc)
        return False


__all__ = [
    "liara_ttl_check",
    "get_liara_context",
    "activate_liara",
    "deactivate_liara",
]
