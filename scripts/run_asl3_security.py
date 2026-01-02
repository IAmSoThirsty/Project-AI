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

from app.core.security_enforcer import ASL3Security, cli_main

if __name__ == "__main__":
    sys.exit(cli_main())
