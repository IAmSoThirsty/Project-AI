"""
Validation Runner Script
========================

Automated script to run all validation tests and generate reports.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tests.integration_enhanced.test_full_integration import EnhancedSystemIntegration
from tests.integration_enhanced.test_e2e_scenarios import SovereignE2EFramework
from tests.integration_enhanced.test_performance_benchmarks import PerformanceBenchmarkSuite
from tests.integration_enhanced.test_security_audit import SecurityAuditFramework


class ValidationRunner:
    """Main validation runner"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.start_time = None
        self.end_time = None
        
    async def run_all_validations(self) -> Dict[str, Any]:
        """Run all validation suites"""
        self.start_time = datetime.now()
        print("=" * 80)
        print("SOVEREIGN GOVERNANCE SUBSTRATE - FINAL VALIDATION")
        print("=" * 80)
        print(f"Started: {self.start_time.isoformat()}")
        print()
        
        # 1. Integration Tests
        print("Running Integration Tests...")
        integration_results = await self._run_integration_tests()
        self.results["integration"] = integration_results
        print(f"  ✓ Integration: {integration_results['status']}")
        print()
        
        # 2. E2E Scenarios
        print("Running E2E Scenarios...")
        e2e_results = await self._run_e2e_scenarios()
        self.results["e2e"] = e2e_results
        print(f"  ✓ E2E: {e2e_results['status']}")
        print()
        
        # 3. Performance Benchmarks
        print("Running Performance Benchmarks...")
        perf_results = await self._run_performance_benchmarks()
        self.results["performance"] = perf_results
        print(f"  ✓ Performance: {perf_results['status']}")
        print()
        
        # 4. Security Audit
        print("Running Security Audit...")
        security_results = await self._run_security_audit()
        self.results["security"] = security_results
        print(f"  ✓ Security: {security_results['status']}")
        print()
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        # Generate summary
        summary = self._generate_summary()
        self.results["summary"] = summary
        
        print("=" * 80)
        print("VALIDATION COMPLETE")
        print("=" * 80)
        print(f"Duration: {duration:.2f} seconds")
        print(f"Overall Status: {summary['overall_status']}")
        print()
        print("Results Summary:")
        print(f"  Integration:  {summary['integration_passed']}/{summary['integration_total']} passed")
        print(f"  E2E:          {summary['e2e_passed']}/{summary['e2e_total']} passed")
        print(f"  Performance:  {summary['performance_passed']}/{summary['performance_total']} passed")
        print(f"  Security:     {summary['security_passed']}/{summary['security_total']} passed")
        print()
        
        return self.results
    
    async def _run_integration_tests(self) -> Dict[str, Any]:
        """Run integration tests"""
        integration = EnhancedSystemIntegration()
        
        try:
            # Initialize all components
            init_success = await integration.initialize_all_components()
            
            # Test communication
            comm_results = await integration.validate_cross_component_communication()
            
            # Measure throughput
            throughput = await integration.measure_system_throughput()
            
            # Generate report
            report = integration.generate_integration_report()
            
            passed = init_success and comm_results["failed_communications"] == 0
            
            return {
                "status": "PASS" if passed else "FAIL",
                "components_initialized": len(integration.component_status),
                "components_healthy": sum(1 for s in integration.component_status.values() if s.healthy),
                "communication_success_rate": comm_results["successful_communications"] / max(comm_results["total_pairs"], 1),
                "throughput_ops_sec": throughput["ops_per_second"],
                "health_percentage": report["health_percentage"],
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    async def _run_e2e_scenarios(self) -> Dict[str, Any]:
        """Run E2E scenarios"""
        framework = SovereignE2EFramework()
        
        try:
            scenarios = [
                await framework.scenario_boot_to_operational(),
                await framework.scenario_normal_operation(),
                await framework.scenario_graceful_shutdown(),
            ]
            
            # Reset for fault recovery
            framework = SovereignE2EFramework()
            fault_recovery = await framework.scenario_fault_recovery()
            scenarios.append(fault_recovery)
            
            passed = sum(1 for s in scenarios if s.success)
            total = len(scenarios)
            
            return {
                "status": "PASS" if passed == total else "FAIL",
                "scenarios_passed": passed,
                "scenarios_total": total,
                "scenarios": [
                    {
                        "name": s.scenario_name,
                        "success": s.success,
                        "duration": s.duration_seconds,
                        "metrics": s.performance_metrics
                    }
                    for s in scenarios
                ]
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    async def _run_performance_benchmarks(self) -> Dict[str, Any]:
        """Run performance benchmarks"""
        suite = PerformanceBenchmarkSuite()
        
        try:
            # Run all benchmarks
            results = await suite.run_all_benchmarks()
            
            # Run stress test
            stress_result = await suite.benchmark_stress_test(duration_seconds=5)
            
            # Generate report
            report = suite.generate_benchmark_report()
            
            # Check if all benchmarks meet SLA
            sla_met = all(
                r.throughput_ops_sec > 100 and r.p95_latency_ms < 100
                for r in results
            )
            
            return {
                "status": "PASS" if sla_met and stress_result["stable"] else "FAIL",
                "benchmarks_completed": len(results),
                "avg_throughput": report["summary"]["avg_throughput"],
                "avg_latency_ms": report["summary"]["avg_latency_ms"],
                "stress_test_stable": stress_result["stable"],
                "stress_test_ops_sec": stress_result["ops_per_second"],
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    async def _run_security_audit(self) -> Dict[str, Any]:
        """Run security audit"""
        audit = SecurityAuditFramework()
        
        try:
            report = await audit.run_full_security_audit()
            
            # Pass if no critical or high severity findings
            passed = report["critical"] == 0 and report["high"] == 0
            
            return {
                "status": "PASS" if passed else "FAIL",
                "total_findings": report["total_findings"],
                "critical": report["critical"],
                "high": report["high"],
                "medium": report["medium"],
                "low": report["low"],
                "findings": report["findings"]
            }
        except Exception as e:
            return {
                "status": "ERROR",
                "error": str(e)
            }
    
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary"""
        integration = self.results.get("integration", {})
        e2e = self.results.get("e2e", {})
        performance = self.results.get("performance", {})
        security = self.results.get("security", {})
        
        all_passed = all(
            r.get("status") == "PASS"
            for r in [integration, e2e, performance, security]
        )
        
        return {
            "overall_status": "READY FOR PRODUCTION" if all_passed else "NOT READY",
            "integration_passed": 1 if integration.get("status") == "PASS" else 0,
            "integration_total": 1,
            "e2e_passed": e2e.get("scenarios_passed", 0),
            "e2e_total": e2e.get("scenarios_total", 0),
            "performance_passed": 1 if performance.get("status") == "PASS" else 0,
            "performance_total": 1,
            "security_passed": 1 if security.get("status") == "PASS" else 0,
            "security_total": 1,
            "timestamp": self.end_time.isoformat() if self.end_time else None,
            "duration_seconds": (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0,
        }
    
    def save_report(self, filepath: str):
        """Save validation report to file"""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"Report saved to: {filepath}")


async def main():
    """Main entry point"""
    runner = ValidationRunner()
    results = await runner.run_all_validations()
    
    # Save report
    report_dir = Path(__file__).parent.parent.parent / "validation_evidence"
    report_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"validation_report_{timestamp}.json"
    runner.save_report(str(report_path))
    
    # Exit with appropriate code
    if results["summary"]["overall_status"] == "READY FOR PRODUCTION":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
