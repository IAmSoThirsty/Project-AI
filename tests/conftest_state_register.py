"""
PyTest configuration for STATE_REGISTER enhanced tests.
Ensures proper path setup for imports.
"""

import sys
import os
from pathlib import Path

# Get project root
project_root = Path(__file__).parent.parent
src_dir = project_root / "src"
governance_dir = project_root / "governance"

# Add to path
for directory in [str(src_dir), str(governance_dir)]:
    if directory not in sys.path:
        sys.path.insert(0, directory)
