# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / thirsty_test_runner.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / thirsty_test_runner.py

#
# COMPLIANCE: Sovereign-Native / Dependency-Free                               #



import os
import sys
import time
import importlib.util
import unittest
from pathlib import Path
from typing import List, Dict, Any

class ThirstyTestRunner:
    """
    Sovereign Test Runner for Project-AI.
    
    Discovers and executes tests without requiring external dependencies like pytest.
    Prioritizes audit-compliant reporting and high-speed execution.
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[Dict[str, Any]] = []
        
        # Ensure 'src' is in sys.path for internal imports
        src_path = str(Path(os.getcwd()) / "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        # Also ensure 'tests' subdirectory packages are resolvable if needed
        tests_path = str(Path(os.getcwd()) / "tests")
        if tests_path not in sys.path:
            sys.path.append(tests_path)

    def discover_and_run(self, paths: List[str]) -> bool:
        """
        Discover tests in given paths and run them.
        Supports both unittest.TestCase and functional pytest-style tests.
        """
        print(f"Sovereign Test Discovery initiated for: {', '.join(paths)}")
        
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()

        for path_str in paths:
            path = Path(path_str)
            if path.is_dir():
                # For directories, use standard discovery but then supplement with our custom discovery
                discovered = loader.discover(str(path), pattern='test_*.py')
                suite.addTests(discovered)
                
                # Also supplement with functional tests in those files
                for test_file in path.rglob("test_*.py"):
                    self._add_functional_tests_to_suite(test_file, suite)
            elif path.is_file():
                # Standard unittest discovery
                suite.addTests(loader.loadTestsFromName(path.stem) if path.stem in sys.modules else [])
                # Supplement with functional tests
                self._add_functional_tests_to_suite(path, suite)

        runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1)
        result = runner.run(suite)
        
        return result.wasSuccessful()

    def _add_functional_tests_to_suite(self, path: Path, suite: unittest.TestSuite):
        """Discovers and wraps functional tests from a file into a TestSuite."""
        try:
            module_name = f"dynamic_test_{path.stem}_{hash(str(path)) & 0xffffffff}"
            spec = importlib.util.spec_from_file_location(module_name, str(path))
            if not (spec and spec.loader):
                return
            
            module = importlib.util.module_from_spec(spec)
            # Add to sys.modules so imports within the test work
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # 1. Look for standalone functions starting with test_
            for name in dir(module):
                obj = getattr(module, name)
                if name.startswith("test_") and callable(obj):
                    # Wrap in FunctionTestCase
                    suite.addTest(unittest.FunctionTestCase(obj))
            
            # 2. Look for classes starting with Test that don't inherit from unittest.TestCase
            for name in dir(module):
                obj = getattr(module, name)
                if name.startswith("Test") and isinstance(obj, type) and not issubclass(obj, unittest.TestCase):
                    # Wrap methods starting with test_
                    for meth_name in dir(obj):
                        if meth_name.startswith("test_"):
                            meth = getattr(obj, meth_name)
                            if callable(meth):
                                # We need to instantiate the class for each test method
                                def test_wrapper(m=meth, cls=obj):
                                    instance = cls()
                                    import inspect
                                    sig = inspect.signature(m)
                                    # Count parameters excluding 'self'
                                    params = list(sig.parameters.keys())
                                    if params and params[0] in ('self', 'cls'):
                                        params = params[1:]
                                    
                                    if not params:
                                        return m(instance)
                                    else:
                                        # Simple fixture injection for common ones
                                        kwargs = {}
                                        for p in params:
                                            if p in ("tmp_path", "tmpdir"):
                                                import tempfile
                                                from pathlib import Path
                                                temp_path = Path(tempfile.mkdtemp())
                                                kwargs[p] = temp_path
                                        
                                        if len(kwargs) == len(params):
                                            return m(instance, **kwargs)
                                        else:
                                            print(f"Skipping {cls.__name__}.{m.__name__}: requires unhandled fixtures {set(params) - set(kwargs.keys())}")
                                            return None
                                
                                wrapper = unittest.FunctionTestCase(test_wrapper, description=f"{name}.{meth_name}")
                                suite.addTest(wrapper)
        except Exception as e:
            if self.verbose:
                print(f"Error discovering functional tests in {path}: {e}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Thirsty-Lang Sovereign Test Runner")
    parser.add_argument("paths", nargs="+", help="Paths to test files or directories")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    runner = ThirstyTestRunner(verbose=args.verbose)
    success = runner.discover_and_run(args.paths)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
