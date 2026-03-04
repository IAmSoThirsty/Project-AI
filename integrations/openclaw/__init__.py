#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Legion - OpenClaw Integration Package
God-Tier Project-AI Agent: "For we are many, and we are one"
"""

from .agent_adapter import LegionAgent
from .config import LEGION_CONFIG, get_config
from .security_wrapper import SecurityResult, SecurityWrapper, ThreatLevel

__version__ = "1.0.0-phase1"
__all__ = [
    "LegionAgent",
    "LEGION_CONFIG",
    "get_config",
    "SecurityWrapper",
    "SecurityResult",
    "ThreatLevel",
]
