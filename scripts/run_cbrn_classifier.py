#!/usr/bin/env python3
"""
CBRN & High-Risk Capability Classification Runner

Runs CBRN classifier for ASL-3 deployment safeguards.

Usage:
    python scripts/run_cbrn_classifier.py classify --text "input text"
    python scripts/run_cbrn_classifier.py stats
    python scripts/run_cbrn_classifier.py report
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

<<<<<<< HEAD
from app.core.cbrn_classifier import CBRNClassifier, cli_main
=======
from app.core.cbrn_classifier import cli_main
>>>>>>> 7680383fa2faae70c9879322f0f88b29211a4015

if __name__ == "__main__":
    sys.exit(cli_main())
