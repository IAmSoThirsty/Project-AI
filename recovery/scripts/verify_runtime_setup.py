#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Runtime Environment Verification Test Suite
Runs all verification checks and generates a comprehensive report
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


class VerificationSuite:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def test(self, name: str, command: List[str], expect_success: bool = True) -> bool:
        """Run a test command and track results"""
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"{'='*60}")
        print(f"Command: {' '.join(command)}")
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = (result.returncode == 0) if expect_success else (result.returncode != 0)
            
            if success:
                print(f"✓ PASS")
                self.passed.append(name)
                return True
            else:
                print(f"✗ FAIL")
                print(f"Exit code: {result.returncode}")
                if result.stdout:
                    print(f"STDOUT:\n{result.stdout}")
                if result.stderr:
                    print(f"STDERR:\n{result.stderr}")
                self.failed.append(name)
                return False
                
        except subprocess.TimeoutExpired:
            print(f"✗ FAIL (timeout)")
            self.failed.append(name)
            return False
        except Exception as e:
            print(f"✗ FAIL (exception: {e})")
            self.failed.append(name)
            return False
    
    def check_file(self, name: str, filepath: str) -> bool:
        """Verify a file exists"""
        print(f"\n{'='*60}")
        print(f"FILE CHECK: {name}")
        print(f"{'='*60}")
        print(f"Path: {filepath}")
        
        path = Path(filepath)
        if path.exists():
            size = path.stat().st_size
            print(f"✓ PASS (size: {size:,} bytes)")
            self.passed.append(name)
            return True
        else:
            print(f"✗ FAIL (not found)")
            self.failed.append(name)
            return False
    
    def report(self):
        """Print final report"""
        print(f"\n\n{'='*60}")
        print("VERIFICATION SUITE - FINAL REPORT")
        print(f"{'='*60}")
        
        total = len(self.passed) + len(self.failed) + len(self.warnings)
        
        print(f"\nTotal Tests: {total}")
        print(f"✓ Passed:    {len(self.passed)}")
        print(f"✗ Failed:    {len(self.failed)}")
        print(f"⚠ Warnings:  {len(self.warnings)}")
        
        if self.failed:
            print(f"\n{'='*60}")
            print("FAILED TESTS:")
            print(f"{'='*60}")
            for test in self.failed:
                print(f"  ✗ {test}")
        
        if self.warnings:
            print(f"\n{'='*60}")
            print("WARNINGS:")
            print(f"{'='*60}")
            for warning in self.warnings:
                print(f"  ⚠ {warning}")
        
        print(f"\n{'='*60}")
        if len(self.failed) == 0:
            print("✓ ALL TESTS PASSED")
            print(f"{'='*60}\n")
            return 0
        else:
            print("✗ SOME TESTS FAILED")
            print(f"{'='*60}\n")
            return 1


def main():
    suite = VerificationSuite()
    
    print("=" * 60)
    print("RUNTIME ENVIRONMENT VERIFICATION SUITE")
    print("=" * 60)
    print("\nThis suite verifies:")
    print("  1. Runtime health check script")
    print("  2. Documentation completeness")
    print("  3. Configuration files")
    print("  4. Production readiness")
    print("\n")
    
    # Test 1: Runtime health check (quick mode)
    suite.test(
        "Runtime Health Check (Quick)",
        ["python", "runtime_health_check.py", "--quick"]
    )
    
    # Test 2: Runtime health check (full)
    suite.test(
        "Runtime Health Check (Full)",
        ["python", "runtime_health_check.py"]
    )
    
    # Test 3: Runtime health check (JSON output)
    suite.test(
        "Runtime Health Check (JSON)",
        ["python", "runtime_health_check.py", "--json", "--quiet"]
    )
    
    # Test 4: Verify documentation files
    suite.check_file(
        "Runtime Requirements Documentation",
        "RUNTIME_REQUIREMENTS.md"
    )
    
    suite.check_file(
        "Runtime Dependencies Report",
        "RUNTIME_DEPENDENCIES_REPORT.md"
    )
    
    suite.check_file(
        "Runtime Optimization Guide",
        "RUNTIME_OPTIMIZATION_GUIDE.md"
    )
    
    suite.check_file(
        "Executive Summary",
        "EXECUTIVE_SUMMARY.md"
    )
    
    # Test 5: Verify configuration files
    suite.check_file(
        "Node Version Lock (.nvmrc)",
        ".nvmrc"
    )
    
    suite.check_file(
        "Production Environment Example",
        ".env.production.example"
    )
    
    suite.check_file(
        "Production Start Script",
        "start_production.sh"
    )
    
    suite.check_file(
        "Enhanced Entrypoint",
        "entrypoint.sh"
    )
    
    # Test 6: Verify Python can import core modules
    suite.test(
        "Python Core Imports",
        ["python", "-c", "import fastapi, uvicorn, pydantic, sqlalchemy"]
    )
    
    # Test 7: Verify Python syntax of health check script
    suite.test(
        "Health Check Script Syntax",
        ["python", "-m", "py_compile", "runtime_health_check.py"]
    )
    
    # Test 8: Check if pytest is available
    suite.test(
        "Pytest Installation",
        ["pytest", "--version"]
    )
    
    # Test 9: Check if ruff is available
    suite.test(
        "Ruff Linter Installation",
        ["ruff", "--version"]
    )
    
    # Test 10: Verify git status (no critical files uncommitted)
    # This is informational, not a blocker
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.stdout:
            suite.warnings.append("Uncommitted changes detected (see git status)")
    except:
        pass
    
    # Generate report
    return suite.report()


if __name__ == "__main__":
    sys.exit(main())
