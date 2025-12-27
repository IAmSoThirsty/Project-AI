from __future__ import annotations

import json
from pathlib import Path

from app.monitoring.cerberus_dashboard import record_incident, get_metrics


def test_metrics_record_and_read(tmp_path: Path):
    data_dir = tmp_path / "data_monitor"
    data_dir.mkdir()
    incidents = data_dir / "cerberus_incidents.json"
    incidents.write_text(json.dumps({"incidents": [], "attack_counts": {}}))

    # monkeypatch global path by writing to default file used by module
    # simple test: record incident and read metrics
    record_incident({"type": "test_incident", "gate": "g-1", "source": "s-1"})
    metrics = get_metrics()
    assert "incidents" in metrics
    assert metrics["attack_counts"].get("s-1") >= 1
