"""Dependency & Security Auditor agent

Runs pip-audit and basic dependency checks on newly generated files.
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DependencyAuditor:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        # reports dir
        self.reports_dir = os.path.join(self.data_dir, "sandbox_reports")
        os.makedirs(self.reports_dir, exist_ok=True)

    def analyze_new_module(self, module_path: str) -> dict[str, Any]:
        # For now, scan imports and report them; run pip-audit for environment vulnerabilities
        try:
            with open(module_path, encoding="utf-8") as f:
                txt = f.read()
            imports = [
                line
                for line in txt.splitlines()
                if line.strip().startswith("import ") or line.strip().startswith("from ")
            ]

            # Run pip-audit (best-effort)
            try:
                res = subprocess.run([sys.executable, "-m", "pip_audit", "--format", "json"], capture_output=True, text=True)
                audit_json = res.stdout
            except Exception:
                audit_json = None

            # Run the sandbox worker as a subprocess to safely execute the module
            try:
                worker = Path(__file__).parent.parent / "agents" / "sandbox_worker.py"
                cmd = [sys.executable, str(worker), str(Path(module_path).resolve())]
                proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                # sandbox_worker prints JSON to stdout
                sandbox_output = None
                try:
                    sandbox_output = json.loads(proc.stdout) if proc.stdout else None
                except Exception:
                    sandbox_output = {"raw_stdout": proc.stdout, "raw_stderr": proc.stderr}
            except subprocess.TimeoutExpired:
                sandbox_output = {"error": "timeout"}
            except Exception as e:
                sandbox_output = {"error": str(e)}

            report = {
                "success": True,
                "module": str(module_path),
                "imports": imports,
                "pip_audit": audit_json,
                "sandbox": sandbox_output,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }

            # Persist report
            report_name = Path(self.reports_dir) / f"sandbox_report_{Path(module_path).stem}_{int(time.time())}.json"
            try:
                with open(report_name, "w", encoding="utf-8") as rf:
                    json.dump(report, rf, ensure_ascii=False, indent=2)
            except Exception:
                logger.exception("Failed to persist sandbox report")

            return report
        except Exception as e:
            logger.exception("Dependency audit failed for %s: %s", module_path, e)
            return {"success": False, "error": str(e)}
