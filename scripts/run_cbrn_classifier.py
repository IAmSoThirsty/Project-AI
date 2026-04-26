#!/usr/bin/env python3
"""
CBRN & High-Risk Capability Classification Runner

GOVERNANCE: GOVERNED
Classification: Safety-Critical Operations
Risk: High (identifies dangerous content)

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

from app.core.runtime.router import route_request
from app.core.cbrn_classifier import cli_main


def main_governed():
    """Main function with governance routing."""
    operation = sys.argv[1] if len(sys.argv) > 1 else "stats"
    
    result = route_request("cli", {
        "action": "security.cbrn_classification",
        "params": {
            "operation": operation,
            "args": sys.argv[1:]
        },
        "metadata": {
            "script": __file__,
            "user": "security_operator",
            "risk_level": "high",
            "safety_critical": True
        }
    })
    
    if not result.get("approved", False):
        print(f"❌ CBRN operation blocked: {result.get('reason', 'Unknown')}")
        return 1
    
    # Proceed with CLI execution
    return cli_main()


if __name__ == "__main__":
    sys.exit(main_governed())
