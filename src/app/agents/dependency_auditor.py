"""Dependency & Security Auditor agent

Runs pip-audit and basic dependency checks on newly generated files.

Security Note: This agent uses subprocess to run pip-audit, a trusted
security auditing tool. Commands are hardcoded and do not accept external input.
"""
from __future__ import annotations

import logging
import shutil
import subprocess  # nosec B404 - subprocess usage for trusted security tool only
from typing import Any

logger = logging.getLogger(__name__)


class DependencyAuditor:
    def __init__(self, data_dir: str = "data") -> None:
        self.data_dir = data_dir

    def analyze_new_module(self, module_path: str) -> dict[str, Any]:
        """Analyze a module for security issues.

        Security: Runs pip-audit with hardcoded arguments. The module_path
        is only used for reading file content, not passed to subprocess.
        """
        # For now, scan imports and report them; run pip-audit for environment vulnerabilities
        try:
            with open(module_path, encoding="utf-8") as f:
                txt = f.read()
            imports = [line for line in txt.splitlines() if line.strip().startswith("import ") or line.strip().startswith("from ")]

            # Run pip-audit (best-effort) - validate tool exists
            pip_audit_cmd = shutil.which("pip-audit")
            if pip_audit_cmd:
                try:
                    # nosec B603 - pip-audit is a trusted security tool, path resolved with shutil.which
                    res = subprocess.run(
                        [pip_audit_cmd, "--format", "json"],
                        capture_output=True,
                        text=True,
                        timeout=60,  # 1 minute timeout
                    )
                    audit_json = res.stdout
                except subprocess.TimeoutExpired:
                    logger.warning("pip-audit command timed out after 60 seconds")
                    audit_json = None
                except Exception as e:
                    logger.debug("pip-audit execution failed: %s", e)
                    audit_json = None
            else:
                logger.debug("pip-audit not found in PATH, skipping audit")
                audit_json = None
            return {"success": True, "imports": imports, "pip_audit": audit_json}
        except Exception as e:
            logger.exception("Dependency audit failed for %s: %s", module_path, e)
            return {"success": False, "error": str(e)}
