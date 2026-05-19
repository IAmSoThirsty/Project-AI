#!/usr/bin/env python3
"""
Daily Test Runner - Executes daily regression tests
Excludes 4000 weekly stress tests, runs 3954 daily tests
"""

import subprocess
import sys
from datetime import datetime

def run_daily_tests():
    """Run daily test suite."""
    print("=" * 70)
    print(f"Daily Test Run - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    print("Running 3954 daily tests (excluding weekly stress tests)...")
    print()
    
    cmd = [
        sys.executable, "-m", "pytest",
        "-c", "pytest-daily.ini",
        "--tb=short",
        "--maxfail=20",
        "-v"
    ]
    
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_daily_tests())
