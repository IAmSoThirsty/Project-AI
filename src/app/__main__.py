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

from app.cli import app

if __name__ == "__main__":
    app()
