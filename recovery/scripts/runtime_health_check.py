#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runtime Health Check Script
Verifies all runtime dependencies and execution environment

Usage:
    python runtime_health_check.py              # Full check
    python runtime_health_check.py --quick      # Quick check only
    python runtime_health_check.py --json       # JSON output
"""

import sys
import os
import platform
import importlib.util
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
import json

# Fix Windows console encoding
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())


class RuntimeHealthChecker:
    def __init__(self, verbose: bool = True, json_output: bool = False):
        self.verbose = verbose
        self.json_output = json_output
        self.results = {
            "python": {},
            "node": {},
            "dependencies": {},
            "environment": {},
            "services": {},
            "overall": "UNKNOWN"
        }
        self.issues = []
        self.warnings = []

    def log(self, msg: str, level: str = "INFO"):
        """Log message if verbose mode enabled"""
        if not self.json_output and self.verbose:
            prefix = {
                "INFO": "✓",
                "WARN": "⚠",
                "ERROR": "✗",
                "CHECK": "→"
            }.get(level, "·")
            print(f"{prefix} {msg}")

    def check_python_version(self) -> Tuple[bool, str]:
        """Verify Python version >= 3.11"""
        self.log("Checking Python version...", "CHECK")
        version = sys.version_info
        current = f"{version.major}.{version.minor}.{version.micro}"
        
        self.results["python"]["version"] = current
        self.results["python"]["executable"] = sys.executable
        
        if version.major == 3 and version.minor >= 11:
            self.log(f"Python {current} (OK)", "INFO")
            return True, current
        elif version.major == 3 and version.minor >= 10:
            msg = f"Python {current} detected (3.11+ recommended, 3.10 acceptable)"
            self.log(msg, "WARN")
            self.warnings.append(msg)
            return True, current
        else:
            msg = f"Python {current} too old (requires 3.11+)"
            self.log(msg, "ERROR")
            self.issues.append(msg)
            return False, current

    def check_node_version(self) -> Tuple[bool, str]:
        """Verify Node.js version >= 18.0.0"""
        self.log("Checking Node.js version...", "CHECK")
        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip().replace('v', '')
                self.results["node"]["version"] = version
                
                major = int(version.split('.')[0])
                if major >= 18:
                    self.log(f"Node.js {version} (OK)", "INFO")
                    return True, version
                else:
                    msg = f"Node.js {version} too old (requires 18+)"
                    self.log(msg, "ERROR")
                    self.issues.append(msg)
                    return False, version
            else:
                raise Exception("node command failed")
        except Exception as e:
            msg = f"Node.js not found or not accessible: {e}"
            self.log(msg, "WARN")
            self.warnings.append(msg)
            self.results["node"]["version"] = "not found"
            return False, "N/A"

    def check_python_package(self, package_name: str, import_name: str = None) -> bool:
        """Check if a Python package is installed and importable"""
        if import_name is None:
            import_name = package_name.replace('-', '_')
        
        spec = importlib.util.find_spec(import_name)
        if spec is not None:
            try:
                module = importlib.import_module(import_name)
                version = getattr(module, '__version__', 'unknown')
                self.results["dependencies"][package_name] = {
                    "installed": True,
                    "version": version
                }
                return True
            except ImportError:
                self.results["dependencies"][package_name] = {
                    "installed": False,
                    "error": "import failed"
                }
                return False
        else:
            self.results["dependencies"][package_name] = {
                "installed": False,
                "error": "not found"
            }
            return False

    def check_core_dependencies(self) -> Tuple[int, int]:
        """Check all core runtime dependencies"""
        self.log("Checking core Python dependencies...", "CHECK")
        
        core_packages = [
            ("fastapi", "fastapi"),
            ("uvicorn", "uvicorn"),
            ("pydantic", "pydantic"),
            ("sqlalchemy", "sqlalchemy"),
            ("cryptography", "cryptography"),
            ("PyQt6", "PyQt6"),
            ("flask", "flask"),
            ("requests", "requests"),
            ("httpx", "httpx"),
            ("typer", "typer"),
            ("rich", "rich"),
            ("pytest", "pytest"),
            ("pyyaml", "yaml"),
        ]
        
        success = 0
        failed = 0
        
        for package_name, import_name in core_packages:
            if self.check_python_package(package_name, import_name):
                version = self.results["dependencies"][package_name]["version"]
                self.log(f"  {package_name} {version}", "INFO")
                success += 1
            else:
                self.log(f"  {package_name} NOT FOUND", "ERROR")
                self.issues.append(f"Missing package: {package_name}")
                failed += 1
        
        return success, failed

    def check_optional_dependencies(self) -> Tuple[int, int]:
        """Check optional runtime dependencies"""
        self.log("Checking optional dependencies...", "CHECK")
        
        optional_packages = [
            ("redis", "redis"),
            ("opencv-python-headless", "cv2"),
            ("whisper", "whisper"),
            ("pydub", "pydub"),
            ("torch", "torch"),
            ("transformers", "transformers"),
        ]
        
        success = 0
        missing = 0
        
        for package_name, import_name in optional_packages:
            if self.check_python_package(package_name, import_name):
                version = self.results["dependencies"][package_name]["version"]
                self.log(f"  {package_name} {version}", "INFO")
                success += 1
            else:
                self.log(f"  {package_name} not installed (optional)", "WARN")
                missing += 1
        
        return success, missing

    def check_environment_variables(self) -> Tuple[int, int]:
        """Check required environment variables"""
        self.log("Checking environment configuration...", "CHECK")
        
        required_vars = [
            "PYTHONPATH",
        ]
        
        optional_vars = [
            "OPENAI_API_KEY",
            "DEEPSEEK_API_KEY",
            "DATABASE_URL",
            "TEMPORAL_HOST",
            "REDIS_HOST",
        ]
        
        set_count = 0
        missing_count = 0
        
        for var in required_vars:
            value = os.environ.get(var)
            self.results["environment"][var] = {
                "set": value is not None,
                "value": value if value else "NOT SET"
            }
            if value:
                self.log(f"  {var}={value}", "INFO")
                set_count += 1
            else:
                self.log(f"  {var} NOT SET", "WARN")
                self.warnings.append(f"Environment variable not set: {var}")
                missing_count += 1
        
        for var in optional_vars:
            value = os.environ.get(var)
            self.results["environment"][var] = {
                "set": value is not None,
                "value": "***" if value else "NOT SET"
            }
            if value:
                self.log(f"  {var}=*** (set)", "INFO")
        
        return set_count, missing_count

    def check_paths(self) -> bool:
        """Verify critical paths exist"""
        self.log("Checking critical paths...", "CHECK")
        
        critical_paths = [
            Path("src"),
            Path("src/app"),
            Path("tests"),
            Path("requirements.txt"),
            Path("pyproject.toml"),
        ]
        
        all_exist = True
        for path in critical_paths:
            if path.exists():
                self.log(f"  {path} exists", "INFO")
            else:
                self.log(f"  {path} MISSING", "ERROR")
                self.issues.append(f"Missing path: {path}")
                all_exist = False
        
        return all_exist

    def check_service_connectivity(self) -> Dict[str, bool]:
        """Check connectivity to external services (optional)"""
        self.log("Checking service connectivity...", "CHECK")
        
        services = {}
        
        # Check Temporal (if configured)
        temporal_host = os.environ.get("TEMPORAL_HOST", "localhost:7233")
        if temporal_host:
            self.log(f"  Temporal configured at {temporal_host}", "INFO")
            services["temporal"] = "configured"
        
        # Check Redis (if configured)
        redis_host = os.environ.get("REDIS_HOST")
        if redis_host:
            try:
                import redis
                client = redis.Redis(host=redis_host, socket_connect_timeout=2)
                client.ping()
                self.log(f"  Redis at {redis_host} (OK)", "INFO")
                services["redis"] = "connected"
            except Exception as e:
                self.log(f"  Redis at {redis_host} (FAILED): {e}", "WARN")
                services["redis"] = "failed"
                self.warnings.append(f"Redis connection failed: {e}")
        
        self.results["services"] = services
        return services

    def run_quick_check(self) -> bool:
        """Run quick health check (Python version + imports only)"""
        py_ok, _ = self.check_python_version()
        self.check_node_version()
        
        if not py_ok:
            return False
        
        # Try to import critical modules
        try:
            import fastapi
            import uvicorn
            import pydantic
            self.log("Critical imports successful", "INFO")
            return True
        except ImportError as e:
            self.log(f"Critical import failed: {e}", "ERROR")
            self.issues.append(f"Import error: {e}")
            return False

    def run_full_check(self) -> bool:
        """Run comprehensive health check"""
        self.log("=" * 60)
        self.log("RUNTIME HEALTH CHECK - FULL SCAN")
        self.log("=" * 60)
        
        # System info
        self.log(f"Platform: {platform.platform()}", "INFO")
        self.log(f"Architecture: {platform.machine()}", "INFO")
        self.log("")
        
        # Version checks
        py_ok, _ = self.check_python_version()
        node_ok, _ = self.check_node_version()
        self.log("")
        
        # Dependencies
        core_ok, core_failed = self.check_core_dependencies()
        self.log(f"Core dependencies: {core_ok} OK, {core_failed} failed")
        self.log("")
        
        opt_ok, opt_missing = self.check_optional_dependencies()
        self.log(f"Optional dependencies: {opt_ok} installed, {opt_missing} missing")
        self.log("")
        
        # Environment
        env_ok, env_missing = self.check_environment_variables()
        self.log("")
        
        # Paths
        paths_ok = self.check_paths()
        self.log("")
        
        # Services
        services = self.check_service_connectivity()
        self.log("")
        
        # Summary
        overall_ok = (
            py_ok and
            core_failed == 0 and
            paths_ok
        )
        
        self.results["overall"] = "PASS" if overall_ok else "FAIL"
        
        self.log("=" * 60)
        if overall_ok:
            self.log("HEALTH CHECK: PASS ✓", "INFO")
        else:
            self.log("HEALTH CHECK: FAIL ✗", "ERROR")
        
        if self.warnings:
            self.log(f"Warnings: {len(self.warnings)}", "WARN")
            for warn in self.warnings:
                self.log(f"  - {warn}", "WARN")
        
        if self.issues:
            self.log(f"Issues: {len(self.issues)}", "ERROR")
            for issue in self.issues:
                self.log(f"  - {issue}", "ERROR")
        
        self.log("=" * 60)
        
        return overall_ok

    def output_json(self):
        """Output results as JSON"""
        self.results["warnings"] = self.warnings
        self.results["issues"] = self.issues
        print(json.dumps(self.results, indent=2))


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Runtime health checker")
    parser.add_argument("--quick", action="store_true", help="Quick check only")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    checker = RuntimeHealthChecker(
        verbose=not args.quiet,
        json_output=args.json
    )
    
    if args.quick:
        success = checker.run_quick_check()
    else:
        success = checker.run_full_check()
    
    if args.json:
        checker.output_json()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
