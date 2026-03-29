# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / run_asl3_security.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / run_asl3_security.py

#
# COMPLIANCE: Sovereign Substrate / run_asl3_security.py


#!/usr/bin/env python3
"""
ASL-3 Security Operations Runner

Runs ASL-3 security operations including encryption, monitoring, and compliance reporting.

Usage:
    python scripts/run_asl3_security.py encrypt-critical
    python scripts/run_asl3_security.py status
    python scripts/run_asl3_security.py report
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.core.security_enforcer import cli_main

if __name__ == "__main__":
    sys.exit(cli_main())
