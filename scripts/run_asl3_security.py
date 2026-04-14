#!/usr/bin/env python3
"""
ASL-3 Security Operations Runner

GOVERNANCE: GOVERNED
Classification: Security Operations
Risk: High (manages encryption, security controls)

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

from app.core.runtime.router import route_request
from app.core.security_enforcer import cli_main


def main_governed():
    """Main function with governance routing."""
    operation = sys.argv[1] if len(sys.argv) > 1 else "status"
    
    result = route_request("cli", {
        "action": "security.asl3_operation",
        "params": {
            "operation": operation,
            "args": sys.argv[1:]
        },
        "metadata": {
            "script": __file__,
            "user": "security_operator",
            "risk_level": "high"
        }
    })
    
    if not result.get("approved", False):
        print(f"❌ Security operation blocked: {result.get('reason', 'Unknown')}")
        return 1
    
    # Proceed with CLI execution
    return cli_main()


if __name__ == "__main__":
    sys.exit(main_governed())
