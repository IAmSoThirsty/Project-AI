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
import importlib
import platform

logger = logging.getLogger(__name__)


def _running_in_container() -> bool:
    # Best-effort detection for Docker/container environments
    try:
        if os.path.exists("/.dockerenv"):
            return True
        # check cgroup for docker/k8s indicators
        cgroup = Path("/proc/1/cgroup")
        if cgroup.exists():
            txt = cgroup.read_text(errors="ignore")
            if "docker" in txt or "kubepods" in txt:
                return True
    except Exception:
        pass
    return False


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

            # Try programmatic pip-audit if available
            audit_json = None
            try:
                pip_audit = importlib.import_module("pip_audit")
                # Try a variety of programmatic entrypoints (best-effort)
                try:
                    if hasattr(pip_audit, "audit"):
                        # some versions may expose an API; attempt to call and JSON-serialize result
                        try:
                            res = pip_audit.audit()
                            audit_json = json.dumps(res)
                        except Exception:
                            audit_json = None
                    elif hasattr(pip_audit, "main"):
                        # capture stdout of main
                        import io
                        old_stdout = sys.stdout
                        buf = io.StringIO()
                        sys.stdout = buf
                        try:
                            # call main with json format flag if supported
                            try:
                                pip_audit.main(["--format", "json"])
                            except TypeError:
                                # some entrypoints accept no args
                                pip_audit.main()
                            audit_json = buf.getvalue()
                        except SystemExit:
                            audit_json = buf.getvalue()
                        except Exception:
                            audit_json = None
                        finally:
                            sys.stdout = old_stdout
                except Exception:
                    audit_json = None
            except Exception:
                # fall back to subprocess if import fails
                try:
                    res = subprocess.run([sys.executable, "-m", "pip_audit", "--format", "json"], capture_output=True, text=True)
                    audit_json = res.stdout
                except Exception:
                    audit_json = None

            # Sandbox execution: run the sandbox worker as a subprocess to safely execute the module
            # Safety guard: sandbox limits are only effective on POSIX. Refuse to run on Windows unless in container.
            sandbox_output = None
            try:
                if platform.system() == "Windows" and not _running_in_container():
                    # Record an incident: sandbox cannot be trusted on Windows outside containers
                    try:
                        from app.monitoring.cerberus_dashboard import record_incident

                        record_incident({
                            "type": "sandbox_declined",
                            "reason": "unsafe_platform",
                            "platform": "Windows",
                            "message": "Sandbox limits unavailable on Windows; run inside container or enable ALLOW_UNSAFE_SANDBOX",
                        })
                    except Exception:
                        pass
                    sandbox_output = {
                        "error": "platform_unsafe",
                        "message": "Sandbox limits unavailable on Windows; run inside container or set environment to allow unsafe sandbox",
                    }
                else:
                    worker = Path(__file__).parent.parent / "agents" / "sandbox_worker.py"
                    cmd = [sys.executable, str(worker), str(Path(module_path).resolve())]
                    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    # sandbox_worker prints JSON to stdout
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
