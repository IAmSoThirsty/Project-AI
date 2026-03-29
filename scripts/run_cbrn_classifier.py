# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / run_cbrn_classifier.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / run_cbrn_classifier.py

#
# COMPLIANCE: Sovereign Substrate / run_cbrn_classifier.py


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

from app.core.cbrn_classifier import cli_main

if __name__ == "__main__":
    sys.exit(cli_main())
