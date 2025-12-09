"""Dependency & Security Auditor agent

Runs pip-audit and basic dependency checks on newly generated files.
"""
from __future__ import annotations

import logging
import subprocess
from typing import Any

logger = logging.getLogger(__name__)


class DependencyAuditor:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir

    def analyze_new_module(self, module_path: str) -> dict[str, Any]:
        # For now, scan imports and report them; run pip-audit for environment vulnerabilities
        try:
            with open(module_path, encoding="utf-8") as f:
                txt = f.read()
            imports = [line for line in txt.splitlines() if line.strip().startswith("import ") or line.strip().startswith("from ")]
            # Run pip-audit (best-effort)
            try:
                res = subprocess.run(["pip-audit", "--format", "json"], capture_output=True, text=True)
                audit_json = res.stdout
            except Exception:
                audit_json = None
            return {"success": True, "imports": imports, "pip_audit": audit_json}
        except Exception as e:
            logger.exception("Dependency audit failed for %s: %s", module_path, e)
            return {"success": False, "error": str(e)}
