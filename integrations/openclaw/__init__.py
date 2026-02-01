"""
Legion - OpenClaw Integration Package
God-Tier Project-AI Agent: "For we are many, and we are one"
"""

from .agent_adapter import LegionAgent
from .config import LEGION_CONFIG, get_config
from .security_wrapper import SecurityWrapper, SecurityResult, ThreatLevel

__version__ = "1.0.0-phase1"
__all__ = [
    "LegionAgent",
    "LEGION_CONFIG",
   "get_config",
    "SecurityWrapper",
    "SecurityResult",
    "ThreatLevel",
]
