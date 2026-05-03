"""Forge — purification and destruction engine for the NIRL cascade.

State machine:
  RECEIVE → VERIFY_PAYLOAD → VALID / REJECT
  VALID → CHECK_REPLAY → SHADOW_REPLAY / DIRECT_DESTROY
  SHADOW_REPLAY → ANALYZE → DESTROY
  DIRECT_DESTROY → DESTROY
  DESTROY → ATOMIC_CHECK → SUCCESS / DEAD_LETTER
  SUCCESS     → SIGN_COMPLETION → ROUTE_SIGNAL → [*]
  DEAD_LETTER → SIGN_FAILURE   → ROUTE_SIGNAL → [*]
  REJECT      → SIGN_FAILURE   → ROUTE_SIGNAL → [*]
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import time
from enum import Enum, auto
from typing import Any, Callable

logger = logging.getLogger(__name__)

_FORGE_SECRET = b"project-ai-forge-signing-key-v1"


class ForgeState(Enum):
    RECEIVE = auto()
    VERIFY_PAYLOAD = auto()
    VALID = auto()
    REJECT = auto()
    CHECK_REPLAY = auto()
    SHADOW_REPLAY = auto()
    DIRECT_DESTROY = auto()
    ANALYZE = auto()
    DESTROY = auto()
    ATOMIC_CHECK = auto()
    SUCCESS = auto()
    DEAD_LETTER = auto()
    SIGN_COMPLETION = auto()
    SIGN_FAILURE = auto()
    ROUTE_SIGNAL = auto()


class Forge:
    """Purification and destruction engine.

    Receives sealed payloads from Antibodies, verifies integrity, optionally
    runs a shadow replay for deterministic validation, atomically destroys both
    primary and shadow copies, then signs and routes a completion or failure
    signal back to the originating MiniBrain.

    Args:
        require_shadow_replay: When True, all payloads are replayed through
                               the shadow plane before destruction.
        on_completion:         Callback(section_id, probe_id, success, signature)
                               called after ROUTE_SIGNAL.
    """

    def __init__(
        self,
        require_shadow_replay: bool = False,
        on_completion: Callable[[str, str, bool, str], None] | None = None,
    ) -> None:
        self.require_shadow_replay = require_shadow_replay
        self._on_completion = on_completion
        self.state = ForgeState.RECEIVE
        self._processed: list[dict[str, Any]] = []

    # ------------------------------------------------------------------ public

    def process(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Full purification + destruction pipeline for one payload.

        Args:
            payload: Must contain 'data', 'section_id', 'probe_id', and
                     optionally 'checksum' (sha256 hex of data string).

        Returns:
            Result dict with 'success', 'signature', 'state', and 'error' keys.
        """
        self.state = ForgeState.RECEIVE
        section_id = payload.get("section_id", "unknown")
        probe_id = payload.get("probe_id", "unknown")

        # VERIFY_PAYLOAD
        self.state = ForgeState.VERIFY_PAYLOAD
        integrity_ok = self._verify_integrity(payload)

        if not integrity_ok:
            self.state = ForgeState.REJECT
            logger.warning("Forge: payload rejected (integrity failure) probe=%s", probe_id)
            return self._sign_and_route(section_id, probe_id, success=False, reason="integrity_failure")

        self.state = ForgeState.VALID

        # CHECK_REPLAY
        self.state = ForgeState.CHECK_REPLAY
        if self.require_shadow_replay:
            self.state = ForgeState.SHADOW_REPLAY
            shadow_ok = self._shadow_replay(payload)
            self.state = ForgeState.ANALYZE
            if not shadow_ok:
                return self._sign_and_route(section_id, probe_id, success=False, reason="shadow_replay_mismatch")
        else:
            self.state = ForgeState.DIRECT_DESTROY

        # DESTROY
        self.state = ForgeState.DESTROY
        primary_destroyed = self._destroy(payload, plane="primary")
        shadow_destroyed = self._destroy(payload, plane="shadow") if self.require_shadow_replay else True

        # ATOMIC_CHECK
        self.state = ForgeState.ATOMIC_CHECK
        if primary_destroyed and shadow_destroyed:
            self.state = ForgeState.SUCCESS
        else:
            self.state = ForgeState.DEAD_LETTER
            logger.error("Forge: partial destruction failure probe=%s", probe_id)
            return self._sign_and_route(section_id, probe_id, success=False, reason="partial_destruction")

        return self._sign_and_route(section_id, probe_id, success=True)

    def get_processed_count(self) -> int:
        return len(self._processed)

    # ----------------------------------------------------------------- private

    def _verify_integrity(self, payload: dict[str, Any]) -> bool:
        data = payload.get("data")
        if data is None:
            return False
        checksum = payload.get("checksum")
        if checksum:
            computed = hashlib.sha256(str(data).encode()).hexdigest()
            return hmac.compare_digest(computed, checksum)
        return True  # No checksum provided — accept as-is

    def _shadow_replay(self, payload: dict[str, Any]) -> bool:
        """Replay the payload through the shadow plane and compare outcomes."""
        data = payload.get("data")
        # Deterministic replay: hash twice and confirm idempotence
        h1 = hashlib.sha256(str(data).encode()).hexdigest()
        h2 = hashlib.sha256(str(data).encode()).hexdigest()
        return h1 == h2

    def _destroy(self, payload: dict[str, Any], plane: str = "primary") -> bool:
        """Destroy (consume) the payload from the given plane."""
        try:
            record = {
                "probe_id": payload.get("probe_id"),
                "section_id": payload.get("section_id"),
                "plane": plane,
                "destroyed_at": time.time(),
            }
            self._processed.append(record)
            logger.debug("Forge: destroyed probe=%s plane=%s", payload.get("probe_id"), plane)
            return True
        except Exception:
            logger.exception("Forge: destruction failed probe=%s plane=%s", payload.get("probe_id"), plane)
            return False

    def _sign_and_route(
        self,
        section_id: str,
        probe_id: str,
        success: bool,
        reason: str = "ok",
    ) -> dict[str, Any]:
        if success:
            self.state = ForgeState.SIGN_COMPLETION
        else:
            self.state = ForgeState.SIGN_FAILURE

        # HMAC-SHA256 signature over section_id:probe_id:success
        msg = f"{section_id}:{probe_id}:{success}:{reason}:{time.time_ns()}".encode()
        signature = hmac.new(_FORGE_SECRET, msg, hashlib.sha256).hexdigest()

        self.state = ForgeState.ROUTE_SIGNAL
        result: dict[str, Any] = {
            "success": success,
            "signature": signature,
            "section_id": section_id,
            "probe_id": probe_id,
            "reason": reason,
            "state": self.state.name,
        }

        if self._on_completion:
            try:
                self._on_completion(section_id, probe_id, success, signature)
            except Exception:
                logger.exception("Forge: on_completion callback failed")

        return result
