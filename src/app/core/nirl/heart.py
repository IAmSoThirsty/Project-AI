"""Heart — global tick engine for the NIRL cascade.

State machine:
  TICK_WAIT → GLOBAL_TICK → SPAWN_SKELETON / CHECK_HEARTBEATS → DISTRIBUTE → TICK_WAIT
                                     ↓ (heartbeat missing)
                          SECTION_DEAD → LOST_PARENT_INJECT → RESET_SECTION → TICK_WAIT
                                     ↓ (heartbeat valid)
                          SECTION_OK → CHECK_STRAIN → INJECT → DISTRIBUTE
                                                    ↓ (no strain)
                                              TICK_WAIT
"""

from __future__ import annotations

import hashlib
import logging
import threading
import time
from enum import Enum, auto
from typing import Any, Callable

logger = logging.getLogger(__name__)


class HeartState(Enum):
    TICK_WAIT = auto()
    GLOBAL_TICK = auto()
    SPAWN_SKELETON = auto()
    CHECK_HEARTBEATS = auto()
    DISTRIBUTE = auto()
    SECTION_OK = auto()
    SECTION_DEAD = auto()
    CHECK_STRAIN = auto()
    INJECT = auto()
    LOST_PARENT_INJECT = auto()
    RESET_SECTION = auto()


class Heart:
    """Global tick engine.

    Drives the NIRL cascade: spawns probe skeletons on each tick, monitors
    heartbeats from all registered MiniBrain sections, and injects strain
    signals when a section signals overload.

    Args:
        tick_interval: Seconds between global ticks (default 30 s).
        min_probes:    Probe skeletons created per tick (default 1).
        on_spawn:      Called with (section_id, probe_id) on each skeleton spawn.
        on_strain:     Called with (section_id, strain_data) on strain injection.
    """

    def __init__(
        self,
        tick_interval: float = 30.0,
        min_probes: int = 1,
        on_spawn: Callable[[str, str], None] | None = None,
        on_strain: Callable[[str, dict[str, Any]], None] | None = None,
    ) -> None:
        self.tick_interval = tick_interval
        self.min_probes = min_probes
        self._on_spawn = on_spawn
        self._on_strain = on_strain

        self.state = HeartState.TICK_WAIT
        self._sections: dict[str, dict[str, Any]] = {}  # section_id → {last_beat, strain}
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._tick_count = 0

    # ------------------------------------------------------------------ public

    def register_section(self, section_id: str) -> None:
        """Register a MiniBrain section so the Heart tracks its heartbeat."""
        with self._lock:
            if section_id not in self._sections:
                self._sections[section_id] = {"last_beat": time.monotonic(), "strain": None}
                logger.debug("Heart: registered section %s", section_id)

    def heartbeat(self, section_id: str) -> None:
        """Called by a MiniBrain to confirm it is alive."""
        with self._lock:
            if section_id in self._sections:
                self._sections[section_id]["last_beat"] = time.monotonic()

    def signal_strain(self, section_id: str, strain_data: dict[str, Any]) -> None:
        """Called by a MiniBrain when its load exceeds threshold."""
        with self._lock:
            if section_id in self._sections:
                self._sections[section_id]["strain"] = strain_data

    def start(self) -> None:
        """Start the background tick thread."""
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._tick_loop, name="nirl-heart", daemon=True
        )
        self._thread.start()
        logger.info("Heart started (tick_interval=%.1fs)", self.tick_interval)

    def stop(self) -> None:
        """Stop the tick thread."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self.tick_interval + 1)
        logger.info("Heart stopped after %d ticks", self._tick_count)

    def get_status(self) -> dict[str, Any]:
        with self._lock:
            return {
                "state": self.state.name,
                "tick_count": self._tick_count,
                "registered_sections": list(self._sections.keys()),
            }

    # ----------------------------------------------------------------- private

    def _tick_loop(self) -> None:
        while not self._stop_event.wait(self.tick_interval):
            try:
                self._run_tick()
            except Exception:
                logger.exception("Heart tick error")

    def _run_tick(self) -> None:
        self._tick_count += 1
        self.state = HeartState.GLOBAL_TICK
        logger.debug("Heart tick #%d", self._tick_count)

        with self._lock:
            sections = dict(self._sections)

        # Spawn probe skeletons
        self.state = HeartState.SPAWN_SKELETON
        spawned: list[tuple[str, str]] = []
        for section_id in sections:
            for _ in range(self.min_probes):
                probe_id = self._new_probe_id(section_id)
                spawned.append((section_id, probe_id))
                if self._on_spawn:
                    try:
                        self._on_spawn(section_id, probe_id)
                    except Exception:
                        logger.exception("on_spawn callback failed")

        # Check heartbeats in parallel (conceptually — single thread for safety)
        self.state = HeartState.CHECK_HEARTBEATS
        now = time.monotonic()
        dead_sections: list[str] = []
        live_sections: list[str] = []
        for sid, info in sections.items():
            age = now - info["last_beat"]
            if age > self.tick_interval * 2:
                dead_sections.append(sid)
            else:
                live_sections.append(sid)

        # Handle dead sections
        for sid in dead_sections:
            self.state = HeartState.SECTION_DEAD
            logger.warning("Heart: section %s is dead (no heartbeat)", sid)
            self.state = HeartState.LOST_PARENT_INJECT
            self._lost_parent_inject(sid)
            self.state = HeartState.RESET_SECTION
            self._reset_section(sid)

        # Handle live sections — check strain
        for sid in live_sections:
            self.state = HeartState.SECTION_OK
            self.state = HeartState.CHECK_STRAIN
            with self._lock:
                strain = sections[sid].get("strain")
                if strain:
                    self._sections[sid]["strain"] = None  # consume
            if strain:
                self.state = HeartState.INJECT
                logger.debug("Heart: injecting strain signal for section %s", sid)
                if self._on_strain:
                    try:
                        self._on_strain(sid, strain)
                    except Exception:
                        logger.exception("on_strain callback failed")

        # Distribute spawned skeletons
        self.state = HeartState.DISTRIBUTE
        logger.debug("Heart: distributed %d probe skeletons", len(spawned))
        self.state = HeartState.TICK_WAIT

    def _lost_parent_inject(self, section_id: str) -> None:
        """Inject a lost-parent signal for an unresponsive section."""
        logger.warning("Heart: lost_parent_inject for section %s", section_id)

    def _reset_section(self, section_id: str) -> None:
        """Reset a dead section's heartbeat timestamp so it gets a fresh start."""
        with self._lock:
            if section_id in self._sections:
                self._sections[section_id]["last_beat"] = time.monotonic()
        logger.info("Heart: section %s reset", section_id)

    @staticmethod
    def _new_probe_id(section_id: str) -> str:
        raw = f"{section_id}:{time.monotonic_ns()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]
