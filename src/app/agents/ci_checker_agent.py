"""CI Checker Agent

This agent is deployed as a smaller agent under CouncilHub and runs periodic
random CI checks: pytest, lint (ruff), and static analysis (ruff/pyflakes).
It attempts to run with minimal external dependencies and writes a report to
`data/ci_reports/` with a correlation id and timestamp.

Security Note: This agent uses subprocess to run trusted development tools
(pytest, ruff) that are part of the project's dependencies. All commands
are hardcoded and do not accept external input.
"""

from __future__ import annotations

import json
import logging
import os
import shutil
import subprocess  # nosec B404 - subprocess usage for trusted dev tools only
import time
from datetime import datetime
from typing import Any

from app.core.ai_systems import new_correlation_id
from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)


class CICheckerAgent(KernelRoutedAgent):
    def __init__(
        self, data_dir: str = "data", kernel: CognitionKernel | None = None
    ) -> None:
        # Initialize kernel routing (COGNITION KERNEL INTEGRATION)
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",
        )
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
        """Run CI checks using trusted development tools.

        Security: Commands are hardcoded and use only trusted tools from
        project dependencies. No external input is used in commands.
        """
        # Route through kernel (COGNITION KERNEL ROUTING)
        return self._execute_through_kernel(
            self._do_run_one,
            operation_name="run_ci_checks",
            risk_level="medium",
            metadata={"check_type": "pytest_and_ruff"},
        )

    def _do_run_one(self) -> dict[str, Any]:
        """Internal implementation of CI check execution."""
        corr = new_correlation_id()
        ts = datetime.utcnow().isoformat()
        report = {"corr": corr, "timestamp": ts, "results": {}}

        # Resolve tool paths - validate they exist
        pytest_cmd = shutil.which("pytest")
        ruff_cmd = shutil.which("ruff")

        # run pytest -q (only tests directory)
        if pytest_cmd:
            try:
                # nosec B603 B607 - pytest is a trusted dev tool, path resolved with shutil.which
                res = subprocess.run(  # nosec B603
                    [pytest_cmd, "-q"],
                    capture_output=True,
                    text=True,
                    timeout=180,  # 3 minute timeout for CI checks
                )
                report["results"]["pytest"] = {
                    "rc": res.returncode,
                    "output": res.stdout + res.stderr,
                }
            except subprocess.TimeoutExpired:
                logger.warning("pytest command timed out after 180 seconds")
                report["results"]["pytest"] = {"rc": -1, "error": "timeout"}
            except Exception as e:
                logger.error("pytest execution failed: %s", e)
                report["results"]["pytest"] = {"rc": -1, "error": str(e)}
        else:
            logger.warning("pytest command not found in PATH")
            report["results"]["pytest"] = {"rc": -1, "error": "pytest not found"}

        # run ruff (lint)
        if ruff_cmd:
            try:
                # nosec B603 B607 - ruff is a trusted dev tool, path resolved with shutil.which
                res = subprocess.run(  # nosec B603
                    [ruff_cmd, "check", "src", "tests"],
                    capture_output=True,
                    text=True,
                    timeout=60,  # 1 minute timeout (ruff is fast)
                )
                report["results"]["ruff"] = {
                    "rc": res.returncode,
                    "output": res.stdout + res.stderr,
                }
            except subprocess.TimeoutExpired:
                logger.warning("ruff command timed out after 60 seconds")
                report["results"]["ruff"] = {"rc": -1, "error": "timeout"}
            except Exception as e:
                logger.error("ruff execution failed: %s", e)
                report["results"]["ruff"] = {"rc": -1, "error": str(e)}
        else:
            logger.warning("ruff command not found in PATH")
            report["results"]["ruff"] = {"rc": -1, "error": "ruff not found"}

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
