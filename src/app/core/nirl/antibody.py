"""Antibody — single-lifecycle escort unit for the NIRL cascade.

State machine:
  SPAWNED → CAPTURE → SEALED → ESCORT → FORGE_ENTRY → DESTROYED / DEAD_LETTER
  DESTROYED  → [*]
  DEAD_LETTER → [*]
"""

from __future__ import annotations

import hashlib
import logging
import time
from enum import Enum, auto
from typing import Any

logger = logging.getLogger(__name__)


class AntibodyState(Enum):
    SPAWNED = auto()
    CAPTURE = auto()
    SEALED = auto()
    ESCORT = auto()
    FORGE_ENTRY = auto()
    DESTROYED = auto()
    DEAD_LETTER = auto()


class Antibody:
    """Single-lifecycle escort unit.

    An Antibody is spawned by a MiniBrain to capture one target payload, seal
    it cryptographically, and escort it to the Forge for purification and
    destruction.  Once the Forge returns a result the Antibody reaches a
    terminal state (DESTROYED or DEAD_LETTER) and must not be reused.

    Args:
        antibody_id: Unique identifier (typically probe_id from Heart).
        section_id:  The MiniBrain section that spawned this Antibody.
    """

    def __init__(self, antibody_id: str, section_id: str) -> None:
        self.antibody_id = antibody_id
        self.section_id = section_id
        self.state = AntibodyState.SPAWNED
        self._payload: dict[str, Any] | None = None
        self._sealed_at: float | None = None
        self._forge_result: dict[str, Any] | None = None

    # ------------------------------------------------------------------ public

    @property
    def is_terminal(self) -> bool:
        return self.state in (AntibodyState.DESTROYED, AntibodyState.DEAD_LETTER)

    def run(self, target: Any) -> dict[str, Any]:
        """Execute the full Antibody lifecycle for one target.

        Args:
            target: The payload data to capture, seal, and route to the Forge.

        Returns:
            Forge result dict, or an error dict on failure.
        """
        if self.is_terminal:
            raise RuntimeError(
                f"Antibody {self.antibody_id} is already in terminal state {self.state.name}"
            )

        try:
            # CAPTURE
            self._capture(target)
            # SEALED
            self._seal()
            # ESCORT
            self.state = AntibodyState.ESCORT
            logger.debug(
                "Antibody %s: escorting sealed payload to Forge", self.antibody_id
            )
        except Exception as exc:
            self.state = AntibodyState.DEAD_LETTER
            logger.error("Antibody %s failed pre-forge: %s", self.antibody_id, exc)
            return {"success": False, "error": str(exc), "antibody_id": self.antibody_id}

        # Caller (MiniBrain) drives FORGE_ENTRY by passing the payload to Forge
        return self._build_forge_payload()

    def record_forge_result(self, result: dict[str, Any]) -> None:
        """Record the outcome returned by the Forge and set terminal state."""
        self.state = AntibodyState.FORGE_ENTRY
        self._forge_result = result
        if result.get("success"):
            self.state = AntibodyState.DESTROYED
            logger.debug("Antibody %s: DESTROYED (forge success)", self.antibody_id)
        else:
            self.state = AntibodyState.DEAD_LETTER
            logger.warning(
                "Antibody %s: DEAD_LETTER (forge failure: %s)",
                self.antibody_id,
                result.get("reason"),
            )

    def get_status(self) -> dict[str, Any]:
        return {
            "antibody_id": self.antibody_id,
            "section_id": self.section_id,
            "state": self.state.name,
            "sealed_at": self._sealed_at,
            "forge_result": self._forge_result,
        }

    # ----------------------------------------------------------------- private

    def _capture(self, target: Any) -> None:
        """Capture the target into a structured payload."""
        self.state = AntibodyState.CAPTURE
        self._payload = {
            "data": target,
            "captured_at": time.time(),
            "section_id": self.section_id,
            "probe_id": self.antibody_id,
        }
        logger.debug("Antibody %s: captured target", self.antibody_id)

    def _seal(self) -> None:
        """Lock the payload with a SHA-256 checksum."""
        if self._payload is None:
            raise ValueError("No payload to seal")
        data_str = str(self._payload["data"])
        self._payload["checksum"] = hashlib.sha256(data_str.encode()).hexdigest()
        self._sealed_at = time.time()
        self.state = AntibodyState.SEALED
        logger.debug("Antibody %s: payload sealed", self.antibody_id)

    def _build_forge_payload(self) -> dict[str, Any]:
        """Return the sealed payload ready for submission to Forge."""
        if self._payload is None:
            raise ValueError("No sealed payload available")
        return dict(self._payload)
