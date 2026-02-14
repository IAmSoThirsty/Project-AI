"""Simple telemetry manager (opt-in) with atomic JSON event logging and rotation.

Telemetry is disabled by default. Enable by setting TELEMETRY_ENABLED=true in the environment
or `.env` file. Events are recorded to `logs/telemetry.json` using atomic writes to avoid
corruption from concurrent writers.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any

from app.core.ai_systems import _atomic_write_json

TELEMETRY_ENABLED = os.getenv("TELEMETRY_ENABLED", "false").lower() in (
    "1",
    "true",
    "yes",
)
TELEMETRY_FILE = os.getenv("TELEMETRY_FILE", os.path.join("logs", "telemetry.json"))
TELEMETRY_MAX_EVENTS = int(os.getenv("TELEMETRY_MAX_EVENTS", "1000"))


def _ensure_logs_dir() -> None:
    telemetry_dir = os.path.dirname(TELEMETRY_FILE)
    if telemetry_dir:
        os.makedirs(telemetry_dir, exist_ok=True)


class TelemetryManager:
    """Minimal telemetry manager. Stores events as a JSON array in TELEMETRY_FILE.

    Use `send_event` to append a structured event. This is intentionally simple and
    operates only when TELEMETRY_ENABLED is True.
    """

    @staticmethod
    def enabled() -> bool:
        return TELEMETRY_ENABLED

    @staticmethod
    def send_event(name: str, payload: dict[str, Any] | None = None) -> None:
        if not TelemetryManager.enabled():
            return
        _ensure_logs_dir()
        payload = payload or {}
        event = {
            "name": name,
            "timestamp": time.time(),
            "payload": payload,
        }
        # Load existing events (best-effort), append and rotate if necessary
        try:
            events = []
            if os.path.exists(TELEMETRY_FILE):
                with open(TELEMETRY_FILE, encoding="utf-8") as f:
                    try:
                        events = json.load(f)
                        if not isinstance(events, list):
                            events = []
                    except Exception:
                        events = []
            events.append(event)
            # simple rotation: keep last TELEMETRY_MAX_EVENTS events
            if len(events) > TELEMETRY_MAX_EVENTS:
                events = events[-TELEMETRY_MAX_EVENTS:]
            _atomic_write_json(TELEMETRY_FILE, events)
        except Exception:
            # Fail silently — telemetry must not affect app behavior
            pass


# Convenience function
send_event = TelemetryManager.send_event
