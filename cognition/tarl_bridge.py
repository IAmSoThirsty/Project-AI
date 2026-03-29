# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / tarl_bridge.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / Project-AI                                 #



"""
TARL Bridge: Sovereign Linguistic Logic Interface
Orchestrates communication between the Python substrate and the TARL interpreter.
"""

import subprocess
from pathlib import Path
from typing import Any

from cognition.audit import audit
from tarl.validate import validate

# Path to the Thirsty-Lang CLI interpreter
THIRSTY_CLI = Path(__file__).parent.parent / "src" / "thirsty_lang" / "src" / "cli.js"


def submit_tarl(tarl: Any) -> dict[str, Any]:
    """Validate and submit a TARL payload for sovereign execution."""
    validate(tarl)
    audit("TARL_SUBMIT", f"Hash: {tarl.hash()} / Authority: {tarl.authority}")
    return {"accepted": True, "hash": tarl.hash()}


def execute_sovereign_module(module_path: str, function_name: str, *args: Any) -> str:
    """Execute a Thirsty-Lang module function via the node.js interpreter."""
    cmd = ["node", str(THIRSTY_CLI), module_path, function_name] + [
        str(a) for a in args
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        audit(
            "SOVEREIGN_EXECUTION",
            f"Module: {module_path} / Function: {function_name} / STATUS: SUCCESS",
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        audit(
            "SOVEREIGN_EXECUTION_FAILURE",
            f"Module: {module_path} / Function: {function_name} / ERROR: {e.stderr}",
        )
        raise RuntimeError(f"Sovereign execution failed: {e.stderr}") from e
