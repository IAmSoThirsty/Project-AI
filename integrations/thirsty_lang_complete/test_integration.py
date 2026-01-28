#!/usr/bin/env python3
"""
Integration Test Suite for Thirsty-lang + TARL

This script validates the complete integration of Thirsty-lang and TARL components.
It tests all major features and ensures the combined system works correctly.

Usage:
    python test_integration.py [--verbose] [--quick]
"""

import sys
import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class IntegrationTester:
    """Main integration test runner"""
    
    def __init__(self, verbose=False, quick=False):
        self.verbose = verbose
        self.quick = quick
        self.passed = 0
        self.failed = 0
        self.skipped = 0
        self.results = []
        
    def log(self, message, level='INFO'):
        """Log message with color coding"""
        if level == 'SUCCESS':
            print(f"{GREEN}✓ {message}{RESET}")
        elif level == 'ERROR':
            print(f"{RED}✗ {message}{RESET}")
        elif level == 'WARN':
            print(f"{YELLOW}⚠ {message}{RESET}")
        elif level == 'INFO' and self.verbose:
            print(f"{BLUE}ℹ {message}{RESET}")
    
    def run_test(self, name: str, test_func) -> bool:
        """Run a single test and record results"""
        try:
            self.log(f"Running: {name}", 'INFO')
            test_func()
            self.log(f"PASS: {name}", 'SUCCESS')
            self.passed += 1
            self.results.append(('PASS', name))
            return True
        except Exception as e:
            self.log(f"FAIL: {name} - {str(e)}", 'ERROR')
            self.failed += 1
            self.results.append(('FAIL', name, str(e)))
            return False
    
    def test_thirsty_lang_exists(self):
        """Test that Thirsty-lang source exists"""
        thirsty_path = Path('src/thirsty_lang')
        if not thirsty_path.exists():
            raise FileNotFoundError("src/thirsty_lang directory not found")
        
        required_files = [
            'src/index.js',
            'src/thirsty_interpreter.py',
            'src/security/threat-detector.js',
            'package.json',
            'requirements.txt'
        ]
        
        for file in required_files:
            if not (thirsty_path / file).exists():
                raise FileNotFoundError(f"Required file not found: {file}")
    
    def test_tarl_exists(self):
        """Test that TARL source exists"""
        tarl_path = Path('tarl')
        if not tarl_path.exists():
            raise FileNotFoundError("tarl directory not found")
        
        required_files = [
            '__init__.py',
            'spec.py',
            'policy.py',
            'runtime.py',
            'policies/default.py',
            'config/tarl.toml'
        ]
        
        for file in required_files:
            if not (tarl_path / file).exists():
                raise FileNotFoundError(f"Required file not found: {file}")
    
    def test_integration_package_exists(self):
        """Test that integration package exists"""
        integration_path = Path('integrations/thirsty_lang_complete')
        if not integration_path.exists():
            raise FileNotFoundError("Integration package not found")
        
        required_files = [
            'README.md',
            'INTEGRATION_COMPLETE.md',
            'MIGRATION_CHECKLIST.md',
            'FEATURES.md',
            'QUICK_REFERENCE.md',
            'MANIFEST.json',
            'bridge/tarl-bridge.js',
            'bridge/unified-security.py',
            'bridge/README.md',
            'copy_to_thirsty_lang.sh'
        ]
        
        for file in required_files:
            if not (integration_path / file).exists():
                raise FileNotFoundError(f"Required integration file not found: {file}")
    
    def test_tarl_import(self):
        """Test that TARL can be imported"""
        try:
            # Add tarl to path
            sys.path.insert(0, str(Path.cwd()))
            
            import tarl
            from tarl.spec import TarlDecision, TarlVerdict
            from tarl.policy import TarlPolicy
            from tarl.runtime import TarlRuntime
            
            # Test basic initialization
            runtime = TarlRuntime([])
            if not runtime:
                raise RuntimeError("Failed to create TARLRuntime")
                
        except ImportError as e:
            raise ImportError(f"Failed to import TARL: {e}")
    
    def test_tarl_policy_evaluation(self):
        """Test TARL policy evaluation"""
        sys.path.insert(0, str(Path.cwd()))
        
        from tarl.runtime import TarlRuntime
        from tarl.policies.default import DEFAULT_POLICIES
        from tarl.spec import TarlVerdict
        
        runtime = TarlRuntime(DEFAULT_POLICIES)
        
        # Test ALLOW case
        context_allow = {
            "agent": "test_user",
            "mutation": False,
            "mutation_allowed": False
        }
        decision = runtime.evaluate(context_allow)
        if decision.verdict != TarlVerdict.ALLOW:
            raise AssertionError(f"Expected ALLOW, got {decision.verdict}")
        
        # Test DENY case
        context_deny = {
            "agent": "test_user",
            "mutation": True,
            "mutation_allowed": False
        }
        decision = runtime.evaluate(context_deny)
        if decision.verdict != TarlVerdict.DENY:
            raise AssertionError(f"Expected DENY, got {decision.verdict}")
    
    def test_node_dependencies(self):
        """Test that Node.js dependencies exist"""
        package_json = Path('src/thirsty_lang/package.json')
        if not package_json.exists():
            raise FileNotFoundError("package.json not found")
        
        with open(package_json) as f:
            data = json.load(f)
            if 'dependencies' not in data and 'devDependencies' not in data:
                raise ValueError("No dependencies found in package.json")
    
    def test_python_dependencies(self):
        """Test that Python dependencies are listed"""
        requirements = Path('src/thirsty_lang/requirements.txt')
        if not requirements.exists():
            raise FileNotFoundError("requirements.txt not found")
        
        with open(requirements) as f:
            deps = f.read()
            if len(deps.strip()) == 0:
                raise ValueError("requirements.txt is empty")
    
    def test_documentation_complete(self):
        """Test that all documentation exists"""
        integration_path = Path('integrations/thirsty_lang_complete')
        
        docs = [
            'README.md',
            'INTEGRATION_COMPLETE.md',
            'MIGRATION_CHECKLIST.md',
            'FEATURES.md',
            'QUICK_REFERENCE.md',
            'bridge/README.md'
        ]
        
        for doc in docs:
            doc_path = integration_path / doc
            if not doc_path.exists():
                raise FileNotFoundError(f"Documentation missing: {doc}")
            
            # Check minimum size
            if doc_path.stat().st_size < 100:
                raise ValueError(f"Documentation too small: {doc}")
    
    def test_bridge_files_syntax(self):
        """Test that bridge files have valid syntax"""
        integration_path = Path('integrations/thirsty_lang_complete')
        
        # Test JavaScript syntax
        js_file = integration_path / 'bridge/tarl-bridge.js'
        if js_file.exists():
            # Basic syntax check - look for required elements
            content = js_file.read_text()
            if 'class TARLBridge' not in content:
                raise ValueError("tarl-bridge.js missing TARLBridge class")
            if 'async initialize' not in content:
                raise ValueError("tarl-bridge.js missing initialize method")
        
        # Test Python syntax
        py_file = integration_path / 'bridge/unified-security.py'
        if py_file.exists():
            try:
                import ast
                with open(py_file) as f:
                    ast.parse(f.read())
            except SyntaxError as e:
                raise SyntaxError(f"unified-security.py has syntax error: {e}")
    
    def test_shell_script_executable(self):
        """Test that shell script is executable"""
        script = Path('integrations/thirsty_lang_complete/copy_to_thirsty_lang.sh')
        if not script.exists():
            raise FileNotFoundError("copy_to_thirsty_lang.sh not found")
        
        # Check if shebang is present
        with open(script) as f:
            first_line = f.readline()
            if not first_line.startswith('#!'):
                raise ValueError("Shell script missing shebang")
    
    def test_manifest_valid_json(self):
        """Test that MANIFEST.json is valid"""
        manifest = Path('integrations/thirsty_lang_complete/MANIFEST.json')
        if not manifest.exists():
            raise FileNotFoundError("MANIFEST.json not found")
        
        try:
            with open(manifest) as f:
                data = json.load(f)
                
            required_keys = ['name', 'version', 'components', 'integration_status']
            for key in required_keys:
                if key not in data:
                    raise ValueError(f"MANIFEST.json missing key: {key}")
                    
        except json.JSONDecodeError as e:
            raise ValueError(f"MANIFEST.json is not valid JSON: {e}")
    
    def test_examples_exist(self):
        """Test that example files exist"""
        examples_path = Path('src/thirsty_lang/examples')
        if not examples_path.exists():
            raise FileNotFoundError("examples directory not found")
        
        required_examples = [
            'hello.thirsty',
            'variables.thirsty',
            'security/basic-protection.thirsty'
        ]
        
        for example in required_examples:
            if not (examples_path / example).exists():
                raise FileNotFoundError(f"Example missing: {example}")
    
    def run_all_tests(self):
        """Run all integration tests"""
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}Thirsty-lang + TARL Integration Test Suite{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")
        
        # Core component tests
        print(f"{YELLOW}Testing Core Components...{RESET}")
        self.run_test("Thirsty-lang source exists", self.test_thirsty_lang_exists)
        self.run_test("TARL source exists", self.test_tarl_exists)
        self.run_test("Integration package exists", self.test_integration_package_exists)
        
        # Python tests
        print(f"\n{YELLOW}Testing Python Components...{RESET}")
        self.run_test("TARL can be imported", self.test_tarl_import)
        self.run_test("TARL policy evaluation works", self.test_tarl_policy_evaluation)
        
        # Dependency tests
        print(f"\n{YELLOW}Testing Dependencies...{RESET}")
        self.run_test("Node.js dependencies exist", self.test_node_dependencies)
        self.run_test("Python dependencies exist", self.test_python_dependencies)
        
        # Documentation tests
        print(f"\n{YELLOW}Testing Documentation...{RESET}")
        self.run_test("All documentation complete", self.test_documentation_complete)
        
        # File integrity tests
        print(f"\n{YELLOW}Testing File Integrity...{RESET}")
        self.run_test("Bridge files have valid syntax", self.test_bridge_files_syntax)
        self.run_test("Shell script is valid", self.test_shell_script_executable)
        self.run_test("MANIFEST.json is valid", self.test_manifest_valid_json)
        self.run_test("Example files exist", self.test_examples_exist)
        
        # Print summary
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}Test Summary{RESET}")
        print(f"{BLUE}{'='*60}{RESET}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        if self.failed > 0:
            print(f"{RED}Failed: {self.failed}{RESET}")
        if self.skipped > 0:
            print(f"{YELLOW}Skipped: {self.skipped}{RESET}")
        print(f"Total: {self.passed + self.failed + self.skipped}")
        
        # Print failed tests
        if self.failed > 0:
            print(f"\n{RED}Failed Tests:{RESET}")
            for result in self.results:
                if result[0] == 'FAIL':
                    print(f"  {RED}✗{RESET} {result[1]}")
                    if len(result) > 2:
                        print(f"    {result[2]}")
        
        print()
        return self.failed == 0

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Integration test suite for Thirsty-lang + TARL')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--quick', action='store_true', help='Run quick tests only')
    args = parser.parse_args()
    
    tester = IntegrationTester(verbose=args.verbose, quick=args.quick)
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
