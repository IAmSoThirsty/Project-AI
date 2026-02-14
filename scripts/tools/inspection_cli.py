#!/usr/bin/env python3
"""
Repository Inspection & Audit System - Standalone CLI

Quick access script for running repository audits.

Usage:
    python inspection_cli.py
    python inspection_cli.py --repo /path/to/repo
    python inspection_cli.py --help

Author: Project-AI Team
Date: 2026-02-08
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from app.inspection.cli import main

if __name__ == "__main__":
    main()
