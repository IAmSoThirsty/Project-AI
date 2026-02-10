from __future__ import annotations

import json
from pathlib import Path

from app.monitoring.cerberus_dashboard import (
    INCIDENTS_FILE,
    get_metrics,
    record_incident,
)


def test_metrics_record_and_read(tmp_path: Path, monkeypatch):
    incidents_file = tmp_path / "cerberus_incidents.json"
    incidents_file.write_text(json.dumps({"incidents": [], "attack_counts": {}}))
    monkeypatch.setattr(
        "app.monitoring.cerberus_dashboard.INCIDENTS_FILE", incidents_file
    )

    # simple test: record incident and read metrics
    record_incident({"type": "test_incident", "gate": "g-1", "source": "s-1"})
    metrics = get_metrics()
    assert "incidents" in metrics
    assert len(metrics["incidents"]) == 1
    assert metrics["attack_counts"].get("s-1") >= 1


def test_global_file_not_affected(tmp_path: Path, monkeypatch):
    """Verify that test operations don't affect the global INCIDENTS_FILE."""
    # Read the original global file state
    original_data = json.loads(INCIDENTS_FILE.read_text(encoding="utf-8"))
    original_incident_count = len(original_data.get("incidents", []))

    # Create isolated test file
    incidents_file = tmp_path / "cerberus_incidents.json"
    incidents_file.write_text(json.dumps({"incidents": [], "attack_counts": {}}))
    monkeypatch.setattr(
        "app.monitoring.cerberus_dashboard.INCIDENTS_FILE", incidents_file
    )

    # Perform test operations
    record_incident({"type": "test_isolation", "gate": "g-test", "source": "s-test"})

    # Verify global file was not modified
    current_data = json.loads(INCIDENTS_FILE.read_text(encoding="utf-8"))
    current_incident_count = len(current_data.get("incidents", []))

    assert (
        current_incident_count == original_incident_count
    ), "Global INCIDENTS_FILE should not be modified by test"

    # Verify test data went to temp file
    temp_data = json.loads(incidents_file.read_text(encoding="utf-8"))
    assert len(temp_data["incidents"]) == 1
    assert temp_data["incidents"][0]["type"] == "test_isolation"
