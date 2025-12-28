from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path
from typing import Any

_lock = threading.Lock()

MONITOR_DIR = Path("data/monitoring")
MONITOR_DIR.mkdir(parents=True, exist_ok=True)
INCIDENTS_FILE = MONITOR_DIR / "cerberus_incidents.json"

# ensure file exists
if not INCIDENTS_FILE.exists():
    INCIDENTS_FILE.write_text(json.dumps({"incidents": [], "attack_counts": {}}))


def record_incident(incident: dict[str, Any]) -> None:
    with _lock:
        try:
            data = json.loads(INCIDENTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            data = {"incidents": [], "attack_counts": {}}
        incident["ts"] = time.time()
        data.setdefault("incidents", []).append(incident)
        # update attack_counts by source if present
        src = incident.get("source") or incident.get("gate") or "unknown"
        counts = data.setdefault("attack_counts", {})
        counts[src] = counts.get(src, 0) + 1
        INCIDENTS_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def get_metrics() -> dict[str, Any]:
    with _lock:
        try:
            return json.loads(INCIDENTS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"incidents": [], "attack_counts": {}}
