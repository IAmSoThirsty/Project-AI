from __future__ import annotations

import json
from pathlib import Path

from app.monitoring.cerberus_dashboard import record_incident, get_metrics, set_monitor_path


def test_metrics_record_and_read(tmp_path: Path):
    data_dir = tmp_path / "data_monitor"
    data_dir.mkdir()
    # point the cerberus module to this temp directory
    set_monitor_path(str(data_dir))
    incidents = data_dir / "cerberus_incidents.json"
    # ensure initial file exists
    incidents.write_text(json.dumps({"incidents": [], "attack_counts": {}}))

    # write and read via API
    record_incident({"type": "test_incident", "gate": "g-1", "source": "s-1"})
    metrics = get_metrics()
    assert "incidents" in metrics
    assert metrics["attack_counts"].get("s-1") >= 1
