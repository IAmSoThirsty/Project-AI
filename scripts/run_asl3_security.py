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

<<<<<<< HEAD
from app.core.security_enforcer import ASL3Security, cli_main
=======
from app.core.security_enforcer import cli_main
>>>>>>> 7680383fa2faae70c9879322f0f88b29211a4015

if __name__ == "__main__":
    sys.exit(cli_main())
