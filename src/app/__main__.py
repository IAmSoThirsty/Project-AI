"""
Main entry point for running the app as a Python module.

Usage:
    python -m src.app              # Show help
    python -m src.app health       # Generate health report
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from the cli.py file, not the cli directory
import importlib.util

cli_path = Path(__file__).parent / "cli.py"
spec = importlib.util.spec_from_file_location("app_cli", cli_path)
app_cli = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_cli)

if __name__ == "__main__":
    app_cli.app()
