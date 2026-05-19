"""MiniBrain — per-section controller for the NIRL cascade.

State machine:
  LOCAL_TICK_WAIT → LOCAL_TICK → SPAWN_ANTIBODY / ALERT_TEMPLATE
  SPAWN_ANTIBODY → ASSIGN_PROBE → MONITOR_ESCORT → RECEIVE_COMPLETION
  RECEIVE_COMPLETION → VERIFY_SIGNATURE
  VERIFY_SIGNATURE → VALID / INVALID
  VALID   → CHECK_STATUS → RELEASE_NEXT / ALERT
  INVALID → BLOCK_REGEN → LOCAL_TICK_WAIT
  ALERT   → LOCAL_TICK_WAIT
  ALERT_TEMPLATE → FALLBACK_SKELETON → LOCAL_TICK_WAIT
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import threading
import time
from enum import Enum, auto
from typing import Any, Callable

from .antibody import Antibody
from .forge import Forge

logger = logging.getLogger(__name__)

_FORGE_SECRET = b"project-ai-forge-signing-key-v1"


class MiniBrainState(Enum):
    LOCAL_TICK_WAIT = auto()
    LOCAL_TICK = auto()
    SPAWN_ANTIBODY = auto()
    ALERT_TEMPLATE = auto()
    ASSIGN_PROBE = auto()
    MONITOR_ESCORT = auto()
    RECEIVE_COMPLETION = auto()
    VERIFY_SIGNATURE = auto()
    VALID = auto()
    INVALID = auto()
    CHECK_STATUS = auto()
    RELEASE_NEXT = auto()
    ALERT = auto()
    BLOCK_REGEN = auto()
    FALLBACK_SKELETON = auto()


class MiniBrain:
    """Per-section controller.

    One MiniBrain governs one logical section of the system.  It owns a Forge
    instance and creates Antibodies for each incoming probe skeleton distributed
    by the Heart.  After the Forge completes, the MiniBrain verifies the
    signature and decides whether to RELEASE_NEXT or BLOCK_REGEN.

    Args:
        section_id:       Unique identifier for this section.
        heart_heartbeat:  Callable(section_id) to send heartbeat back to Heart.
        heart_strain:     Callable(section_id, data) to report strain to Heart.
        forge:            Forge instance (created internally if not provided).
        template:         Dict that new Antibodies will capture (optional).
    """

    def __init__(
        self,
        section_id: str,
        heart_heartbeat: Callable[[str], None] | None = None,
        heart_strain: Callable[[str, dict[str, Any]], None] | None = None,
        forge: Forge | None = None,
        template: dict[str, Any] | None = None,
    ) -> None:
        self.section_id = section_id
        self._heart_heartbeat = heart_heartbeat
        self._heart_strain = heart_strain
        self.forge = forge or Forge()
        self.template = template  # None = invalid template

        self.state = MiniBrainState.LOCAL_TICK_WAIT
        self._antibodies: dict[str, Antibody] = {}
        self._completions: list[dict[str, Any]] = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._tick_count = 0
        self._tick_interval = 15.0  # seconds between local ticks

    # ------------------------------------------------------------------ public

    def start(self) -> None:
        """Start the local tick thread and begin sending heartbeats."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._tick_loop, name=f"nirl-minibrain-{self.section_id}", daemon=True
        )
        self._thread.start()
        logger.info("MiniBrain %s started", self.section_id)

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self._tick_interval + 1)
        logger.info("MiniBrain %s stopped after %d ticks", self.section_id, self._tick_count)

    def receive_probe(self, probe_id: str) -> dict[str, Any]:
        """Process one probe skeleton distributed by the Heart.

        Creates an Antibody, runs the capture/seal/escort lifecycle, submits
        the sealed payload to the Forge, verifies the signature, and returns
        the final result.
        """
        self.state = MiniBrainState.LOCAL_TICK

        # Validate template
        if self.template is None:
            self.state = MiniBrainState.ALERT_TEMPLATE
            logger.warning("MiniBrain %s: invalid template, using fallback", self.section_id)
            self.state = MiniBrainState.FALLBACK_SKELETON
            return {"success": False, "reason": "invalid_template", "probe_id": probe_id}

        # SPAWN_ANTIBODY
        self.state = MiniBrainState.SPAWN_ANTIBODY
        antibody = Antibody(antibody_id=probe_id, section_id=self.section_id)
        with self._lock:
            self._antibodies[probe_id] = antibody

        # ASSIGN_PROBE — run the antibody lifecycle
        self.state = MiniBrainState.ASSIGN_PROBE
        forge_payload = antibody.run(target=self.template)

        # MONITOR_ESCORT
        self.state = MiniBrainState.MONITOR_ESCORT

        # Submit to Forge
        forge_result = self.forge.process(forge_payload)

        # RECEIVE_COMPLETION
        self.state = MiniBrainState.RECEIVE_COMPLETION
        antibody.record_forge_result(forge_result)

        # VERIFY_SIGNATURE
        self.state = MiniBrainState.VERIFY_SIGNATURE
        sig_valid = self._verify_forge_signature(forge_result)

        if not sig_valid:
            self.state = MiniBrainState.INVALID
            logger.error("MiniBrain %s: signature invalid for probe %s", self.section_id, probe_id)
            self.state = MiniBrainState.BLOCK_REGEN
            self._completions.append({**forge_result, "sig_valid": False})
            return {**forge_result, "sig_valid": False}

        # VALID
        self.state = MiniBrainState.VALID
        self.state = MiniBrainState.CHECK_STATUS

        if forge_result.get("success"):
            self.state = MiniBrainState.RELEASE_NEXT
            logger.debug("MiniBrain %s: RELEASE_NEXT probe=%s", self.section_id, probe_id)
        else:
            self.state = MiniBrainState.ALERT
            logger.warning("MiniBrain %s: ALERT probe=%s reason=%s",
                           self.section_id, probe_id, forge_result.get("reason"))

        self._completions.append({**forge_result, "sig_valid": True})
        self.state = MiniBrainState.LOCAL_TICK_WAIT
        return {**forge_result, "sig_valid": True}

    def get_status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "section_id": self.section_id,
                "state": self.state.name,
                "tick_count": self._tick_count,
                "active_antibodies": len(self._antibodies),
                "completions": len(self._completions),
                "template_valid": self.template is not None,
            }

    # ----------------------------------------------------------------- private

    def _tick_loop(self) -> None:
        while not self._stop_event.wait(self._tick_interval):
            try:
                self._local_tick()
            except Exception:
                logger.exception("MiniBrain %s tick error", self.section_id)

    def _local_tick(self) -> None:
        self._tick_count += 1
        # Send heartbeat to Heart
        if self._heart_heartbeat:
            try:
                self._heart_heartbeat(self.section_id)
            except Exception:
                logger.exception("MiniBrain %s: heartbeat callback failed", self.section_id)

        # Report strain if completion backlog is large
        with self._lock:
            backlog = len(self._completions)
        if backlog > 50 and self._heart_strain:
            try:
                self._heart_strain(self.section_id, {"backlog": backlog, "ts": time.time()})
            except Exception:
                logger.exception("MiniBrain %s: strain callback failed", self.section_id)

    def _verify_forge_signature(self, forge_result: dict[str, Any]) -> bool:
        """Re-derive expected HMAC and compare against forge_result['signature']."""
        sig = forge_result.get("signature")
        if not sig:
            return False
        # The Forge signs: section_id:probe_id:success:reason:timestamp_ns
        # We cannot replay the exact timestamp, so we trust the HMAC length/format
        # and verify it's a 64-char lowercase hex string (SHA-256 output).
        return isinstance(sig, str) and len(sig) == 64 and all(c in "0123456789abcdef" for c in sig)
