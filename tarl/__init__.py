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
import importlib.util

from tarl.policy import TarlPolicy
from tarl.spec import TarlDecision, TarlVerdict

_runtime_file = _tarl_dir / "runtime.py"
_spec = importlib.util.spec_from_file_location("tarl.runtime_policy", _runtime_file)
_runtime_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_runtime_module)
TarlRuntime = _runtime_module.TarlRuntime

__all__ = ["TarlDecision", "TarlVerdict", "TarlPolicy", "TarlRuntime"]
