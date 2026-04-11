"""
Helper script to run STATE_REGISTER enhanced tests with proper PYTHONPATH.
"""

import os
import sys
import subprocess
from pathlib import Path

# Get project root
project_root = Path(__file__).parent
src_dir = project_root / "src"
governance_dir = project_root / "governance"

# Set PYTHONPATH
pythonpath_parts = [str(src_dir), str(governance_dir)]
if "PYTHONPATH" in os.environ:
    pythonpath_parts.append(os.environ["PYTHONPATH"])

env = os.environ.copy()
env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)

# Run pytest
cmd = [
    sys.executable,
    "-m",
    "pytest",
    "tests/test_state_register_enhanced.py",
    "-v",
    "--tb=short",
] + sys.argv[1:]  # Pass through any additional arguments

print(f"Running tests with PYTHONPATH={env['PYTHONPATH']}")
result = subprocess.run(cmd, env=env)
sys.exit(result.returncode)
