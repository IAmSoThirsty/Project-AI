#!/usr/bin/env python3
"""
Temporal/Liara Test Suite Runner

Runs comprehensive tests for Temporal and Liara agents with performance
benchmarking and detailed reporting.
"""

import sys
import subprocess
import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any


class TestRunner:
    """Manages test execution and reporting."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: Dict[str, Any] = {}
        self.test_dir = Path(__file__).parent
    
    def run_command(self, cmd: List[str]) -> Dict[str, Any]:
        """Run command and capture output."""
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"Running: {' '.join(cmd)}")
            print(f"{'='*80}\n")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.test_dir.parent.parent
            )
            
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False
            }
    
    def run_temporal_consistency_tests(self) -> bool:
        """Run temporal consistency tests."""
        print("\n[1/5] Running Temporal Consistency Tests...")
        
        cmd = [
            'pytest',
            'tests/temporal/test_temporal_consistency.py',
            '-v',
            '--tb=short'
        ]
        
        result = self.run_command(cmd)
        self.results['temporal_consistency'] = result
        
        if result['success']:
            print("✓ Temporal consistency tests passed")
        else:
            print("✗ Temporal consistency tests failed")
        
        return result['success']
    
    def run_failover_tests(self) -> bool:
        """Run failover scenario tests."""
        print("\n[2/5] Running Failover Scenario Tests...")
        
        cmd = [
            'pytest',
            'tests/temporal/test_failover_scenarios.py',
            '-v',
            '--tb=short'
        ]
        
        result = self.run_command(cmd)
        self.results['failover'] = result
        
        if result['success']:
            print("✓ Failover tests passed")
        else:
            print("✗ Failover tests failed")
        
        return result['success']
    
    def run_race_condition_tests(self) -> bool:
        """Run race condition tests."""
        print("\n[3/5] Running Race Condition Tests...")
        
        cmd = [
            'pytest',
            'tests/temporal/test_race_conditions.py',
            '-v',
            '--tb=short'
        ]
        
        result = self.run_command(cmd)
        self.results['race_conditions'] = result
        
        if result['success']:
            print("✓ Race condition tests passed")
        else:
            print("✗ Race condition tests failed")
        
        return result['success']
    
    def run_byzantine_tests(self) -> bool:
        """Run Byzantine fault tolerance tests."""
        print("\n[4/5] Running Byzantine Fault Tolerance Tests...")
        
        cmd = [
            'pytest',
            'tests/temporal/test_byzantine_faults.py',
            '-v',
            '--tb=short'
        ]
        
        result = self.run_command(cmd)
        self.results['byzantine'] = result
        
        if result['success']:
            print("✓ Byzantine fault tolerance tests passed")
        else:
            print("✗ Byzantine fault tolerance tests failed")
        
        return result['success']
    
    def run_performance_benchmarks(self) -> bool:
        """Run performance benchmarks."""
        print("\n[5/5] Running Performance Benchmarks...")
        
        cmd = [
            'pytest',
            'tests/temporal/test_performance_benchmarks.py',
            '-v',
            '--tb=short'
        ]
        
        result = self.run_command(cmd)
        self.results['performance'] = result
        
        if result['success']:
            print("✓ Performance benchmarks passed")
        else:
            print("✗ Performance benchmarks failed")
        
        return result['success']
    
    def run_all_tests(self) -> bool:
        """Run all test suites."""
        print("\n" + "="*80)
        print("TEMPORAL/LIARA COMPREHENSIVE TEST SUITE")
        print("="*80)
        
        tests = [
            self.run_temporal_consistency_tests,
            self.run_failover_tests,
            self.run_race_condition_tests,
            self.run_byzantine_tests,
            self.run_performance_benchmarks
        ]
        
        results = [test() for test in tests]
        
        return all(results)
    
    def run_with_coverage(self) -> bool:
        """Run all tests with coverage reporting."""
        print("\n[Coverage] Running tests with coverage analysis...")
        
        cmd = [
            'pytest',
            'tests/temporal/',
            '-v',
            '--cov=cognition',
            '--cov-report=html',
            '--cov-report=term',
            '--tb=short'
        ]
        
        result = self.run_command(cmd)
        self.results['coverage'] = result
        
        if result['success']:
            print("✓ Tests with coverage passed")
            print("\nCoverage report generated in htmlcov_temporal/")
        else:
            print("✗ Tests with coverage failed")
        
        return result['success']
    
    def generate_report(self, output_file: str = "test-report.json") -> None:
        """Generate JSON report of test results."""
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_suites': len(self.results),
                'passed': sum(1 for r in self.results.values() if r['success']),
                'failed': sum(1 for r in self.results.values() if not r['success'])
            },
            'results': self.results
        }
        
        output_path = self.test_dir / output_file
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\nTest report saved to: {output_path}")
    
    def print_summary(self) -> None:
        """Print test execution summary."""
        print("\n" + "="*80)
        print("TEST EXECUTION SUMMARY")
        print("="*80)
        
        total = len(self.results)
        passed = sum(1 for r in self.results.values() if r['success'])
        failed = total - passed
        
        print(f"\nTotal Test Suites: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed == 0:
            print("\n✓ ALL TESTS PASSED!")
        else:
            print("\n✗ SOME TESTS FAILED")
            print("\nFailed suites:")
            for name, result in self.results.items():
                if not result['success']:
                    print(f"  - {name}")
        
        print("\n" + "="*80)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Run Temporal/Liara test suite"
    )
    
    parser.add_argument(
        '--suite',
        choices=['all', 'consistency', 'failover', 'race', 'byzantine', 'performance'],
        default='all',
        help='Test suite to run'
    )
    
    parser.add_argument(
        '--coverage',
        action='store_true',
        help='Run with coverage reporting'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--report',
        type=str,
        help='Generate JSON report to file'
    )
    
    args = parser.parse_args()
    
    runner = TestRunner(verbose=args.verbose)
    
    # Run selected test suite
    if args.coverage:
        success = runner.run_with_coverage()
    elif args.suite == 'all':
        success = runner.run_all_tests()
    elif args.suite == 'consistency':
        success = runner.run_temporal_consistency_tests()
    elif args.suite == 'failover':
        success = runner.run_failover_tests()
    elif args.suite == 'race':
        success = runner.run_race_condition_tests()
    elif args.suite == 'byzantine':
        success = runner.run_byzantine_tests()
    elif args.suite == 'performance':
        success = runner.run_performance_benchmarks()
    
    # Generate report if requested
    if args.report:
        runner.generate_report(args.report)
    
    # Print summary
    runner.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
