from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any

_lock = threading.Lock()

# Default monitor directory and file (lazy-init)
_MONITOR_DIR: Path | None = None
_INCIDENTS_FILE: Path | None = None


def set_monitor_path(path: str) -> None:
    """Set custom monitor path; useful for tests to isolate file writes."""
    global _MONITOR_DIR, _INCIDENTS_FILE
    _MONITOR_DIR = Path(path)
    _INCIDENTS_FILE = _MONITOR_DIR / "cerberus_incidents.json"


def ensure_monitor_files() -> None:
    """Ensure monitor dir and incidents file exist. Called lazily on first operation."""
    global _MONITOR_DIR, _INCIDENTS_FILE
    if _MONITOR_DIR is None:
        _MONITOR_DIR = Path("data/monitoring")
    if _INCIDENTS_FILE is None:
        _INCIDENTS_FILE = _MONITOR_DIR / "cerberus_incidents.json"
    try:
        _MONITOR_DIR.mkdir(parents=True, exist_ok=True)
        if not _INCIDENTS_FILE.exists():
            _INCIDENTS_FILE.write_text(json.dumps({"incidents": [], "attack_counts": {}}))
    except Exception:
        # best-effort; errors will be surfaced on read/write
        pass


def record_incident(incident: dict[str, Any]) -> None:
    ensure_monitor_files()
    with _lock:
        try:
            data = json.loads(_INCIDENTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {"incidents": [], "attack_counts": {}}
        incident["ts"] = time.time()
        data.setdefault("incidents", []).append(incident)
        # update attack_counts by source if present
        src = incident.get("source") or incident.get("gate") or "unknown"
        counts = data.setdefault("attack_counts", {})
        counts[src] = counts.get(src, 0) + 1
        try:
            _INCIDENTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))
        except Exception:
            # best-effort persistence
            pass


def get_metrics() -> dict[str, Any]:
    ensure_monitor_files()
    with _lock:
        try:
            return json.loads(_INCIDENTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"incidents": [], "attack_counts": {}}
