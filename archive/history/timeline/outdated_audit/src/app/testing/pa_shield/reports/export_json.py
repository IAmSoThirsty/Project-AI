"""JSON export for PA-SHIELD reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json_report(report: dict[str, Any], output_path: Path) -> Path:
    """Write a JSON report to disk."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=False), encoding="utf-8")
    return output_path
