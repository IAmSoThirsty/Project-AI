#!/usr/bin/env python3
"""
AI Safety Level (ASL) Assessment Runner

Runs comprehensive ASL evaluation against Project-AI's security test results
and generates detailed reports with safety measure recommendations.

Usage:
    python scripts/run_asl_assessment.py
    python scripts/run_asl_assessment.py --metrics-file data/robustness_metrics/novel_robustness_analysis_*.json
    python scripts/run_asl_assessment.py --output reports/asl_assessment.md

GOVERNANCE: GOVERNED
Classification: Security assessment
Risk: Medium (analyzes safety levels)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import governance
from app.core.runtime.router import route_request

from app.core.safety_levels import cli_main

if __name__ == "__main__":
    sys.exit(cli_main())
