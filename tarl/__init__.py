# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py

#
# COMPLIANCE: Sovereign Substrate / __init__.py


#                                                             DATE: 2026-03-03 09:33:22
#                                                             STATUS: Active
#                                                             OWNER: Jeremy Karrick / IAmSoThirsty
"""TARL - Trust and Authorization Runtime Layer"""

# Import from runtime module (the simple policy runtime, not the VM directory)
import sys
from pathlib import Path

# Add current directory to path to prioritize runtime.py over runtime/ directory
_tarl_dir = Path(__file__).parent
if str(_tarl_dir) not in sys.path:
    sys.path.insert(0, str(_tarl_dir))

# Import TarlRuntime from the runtime.py file (not runtime/ directory)
# We do this by importing the module explicitly
import importlib.util  # noqa: E402

from tarl.policy import TarlPolicy  # noqa: E402
from tarl.spec import TarlDecision, TarlVerdict  # noqa: E402

_runtime_file = _tarl_dir / "runtime.py"
_spec = importlib.util.spec_from_file_location("tarl.runtime_policy", _runtime_file)
_runtime_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_runtime_module)
TarlRuntime = _runtime_module.TarlRuntime

# Import TARL VM system (compiler, runtime VM, etc.)
from tarl.system import TARLSystem, get_system

__all__ = [
    # Policy/Governance runtime
    "TarlDecision",
    "TarlVerdict",
    "TarlPolicy",
    "TarlRuntime",
    # VM System
    "TARLSystem",
    "get_system",
]
