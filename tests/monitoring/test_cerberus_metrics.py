from __future__ import annotations

import json
from pathlib import Path

from app.monitoring.cerberus_dashboard import get_metrics, record_incident


def test_metrics_record_and_read(tmp_path: Path, monkeypatch):
    incidents_file = tmp_path / "cerberus_incidents.json"
    incidents_file.write_text(json.dumps({"incidents": [], "attack_counts": {}}))
    monkeypatch.setattr("app.monitoring.cerberus_dashboard.INCIDENTS_FILE", incidents_file)

    # simple test: record incident and read metrics
    record_incident({"type": "test_incident", "gate": "g-1", "source": "s-1"})
    metrics = get_metrics()
    assert "incidents" in metrics
    assert len(metrics["incidents"]) == 1
    assert metrics["attack_counts"].get("s-1") >= 1
