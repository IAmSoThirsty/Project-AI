# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / utf_bridge.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / utf_bridge.py

#
# COMPLIANCE: Sovereign Substrate / Core Component



# COMPLIANCE: Sovereign Substrate / Universal Translation Family (UTF) Bridge

"""
UTF Bridge: Sovereign Substrate Interoperability Layer.

This module provides the authoritative bridge between the Python runtime and the
Thirsty-Lang / Sovereign substrate (.thirsty files). It allows the Cognition
Kernel to delegate constitutional enforcement and audit integrity to the
natively sovereign language layer.

UTF: Universal Translation Family.
"""

import json
import logging
import os
from typing import Any

from src.thirsty_lang.src.thirsty_interpreter import ThirstyInterpreter

logger = logging.getLogger(__name__)


class UTFBridge:
    """
    Authoritative bridge for Sovereign Language delegation.
    """

    def __init__(self, substrate_root: str = "."):
        self.interpreter = ThirstyInterpreter()
        self.substrate_root = substrate_root
        self.active_shields: list[str] = []
        logger.info("UTF Bridge initialized - Sovereign Substrate Ready.")

    def execute_thirsty_file(self, relative_path: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute a Thirsty-Lang file within a given context.
        """
        full_path = os.path.join(self.substrate_root, relative_path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Sovereign substrate not found: {relative_path}")

        # Inject context as thirsty 'drink' variables
        if context:
            for key, value in context.items():
                # Convert Python types to Thirsty-Lang strings for the basic interpreter
                # Note: Real implementation would handle deep types or TSCG+B
                val_str = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
                self.interpreter.execute_line(f"drink {key} = {val_str}")

        with open(full_path, "r", encoding="utf-8") as f:
            code = f.read()

        logger.info(f"Executing Sovereign Logic: {relative_path}")
        self.interpreter.interpret(code)

        return self.interpreter.get_variables()

    def enforce_constitution(self, action_name: str, context_data: dict[str, Any]) -> dict[str, Any]:
        """
        Delegate constitutional enforcementTable to thirstys_constitution.thirsty.
        """
        thirsty_context = {
            "proposed_action_name": action_name,
            "proposed_context": context_data
        }

        # Note: In a full implementation, we would load the constitution shield once
        # For this bridge, we invoke the enforcement logic
        results = self.execute_thirsty_file("tarl_os/security/thirstys_constitution.thirsty", thirsty_context)

        # Extract verdict from thirsty variables
        # Assuming the .thirsty file sets an 'enforcement_result' drink
        return results.get("enforcement_result", {"allowed": True, "reason": "Sovereign Default"})

    def log_sovereign_event(self, event_type: str, data: dict[str, Any], severity: str = "INFO") -> dict[str, Any]:
        """
        Commit event to the immutable Sovereign Runtime audit trail.
        """
        thirsty_context = {
            "p_event_type": event_type,
            "p_data": data,
            "p_severity": severity
        }
        self.execute_thirsty_file("governance/sovereign_runtime.thirsty", thirsty_context)


# Singleton Instance
_bridge: UTFBridge | None = None


def get_utf_bridge() -> UTFBridge:
    global _bridge
    if _bridge is None:
        _bridge = UTFBridge()
    return _bridge
