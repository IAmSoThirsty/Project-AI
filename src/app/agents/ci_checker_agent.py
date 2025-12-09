"""CI Checker Agent

This agent is deployed as a smaller agent under CouncilHub and runs periodic
random CI checks: pytest, lint (ruff), and static analysis (ruff/pyflakes).
It attempts to run with minimal external dependencies and writes a report to
`data/ci_reports/` with a correlation id and timestamp.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import datetime
from typing import Any

from app.core.ai_systems import new_correlation_id


class CICheckerAgent:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir
        self.reports_dir = os.path.join(data_dir, "ci_reports")
        os.makedirs(self.reports_dir, exist_ok=True)
        self.running = False

    def initialize(self) -> bool:
        # Register with council hub (defer import to avoid circular import at module import time)
        try:
            from app.core.council_hub import get_council_hub
        except Exception:
            # If council hub is not importable, skip registration (tests may import agent standalone)
            return True
        hub = get_council_hub()
        hub.register_agent("ci_checker", self)
        return True

    def run_one(self) -> dict[str, Any]:
        corr = new_correlation_id()
        ts = datetime.utcnow().isoformat()
        report = {"corr": corr, "timestamp": ts, "results": {}}
        # run pytest -q (only tests directory)
        try:
            res = subprocess.run(["pytest", "-q"], capture_output=True, text=True)
            report["results"]["pytest"] = {"rc": res.returncode, "output": res.stdout + res.stderr}
        except Exception as e:
            report["results"]["pytest"] = {"rc": -1, "error": str(e)}
        # run ruff (lint)
        try:
            res = subprocess.run(["ruff", "check", "src", "tests"], capture_output=True, text=True)
            report["results"]["ruff"] = {"rc": res.returncode, "output": res.stdout + res.stderr}
        except Exception as e:
            report["results"]["ruff"] = {"rc": -1, "error": str(e)}
        # write report
        out = os.path.join(self.reports_dir, f"ci_{corr}.json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        return report

    def receive_message(self, from_id: str, message: str) -> None:
        # Commands: 'run' triggers a single run
        if message.strip().lower() == "run":
            self.run_one()

    def start_daemon(self, interval: float = 3600.0) -> None:
        self.running = True
        while self.running:
            self.run_one()
            time.sleep(interval)

    def stop(self) -> None:
        self.running = False
