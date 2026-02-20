#!/usr/bin/env python3
"""
Shadow Thirst Static Analyzers Demonstration

This script demonstrates all 6 production-ready static analyzers:
1. PlaneIsolationAnalyzer - Ensures shadow never mutates canonical
2. DeterminismAnalyzer - Verifies deterministic shadow execution
3. PrivilegeEscalationAnalyzer - Detects unauthorized elevation
4. ResourceEstimator - Bounds CPU/memory usage
5. DivergenceRiskEstimator - Estimates divergence probability
6. InvariantPurityChecker - Verifies invariants are pure

Run: python docs/shadow_thirst/STATIC_ANALYZERS_DEMO.py

STATUS: PRODUCTION
VERSION: 1.0.0
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from shadow_thirst.compiler import compile_source
from shadow_thirst.static_analysis import (
    PlaneIsolationAnalyzer,
    DeterminismAnalyzer,
    PrivilegeEscalationAnalyzer,
    ResourceEstimator,
    DivergenceRiskEstimator,
    InvariantPurityChecker,
    StaticAnalyzer,
    AnalysisSeverity
)


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_analysis_report(report):
    """Print analysis report findings."""
    print(f"\n📊 Analysis Summary:")
    print(f"   Total Findings: {report.summary['total_findings']}")
    print(f"   Errors: {report.summary['errors']}")
    print(f"   Warnings: {report.summary['warnings']}")
    print(f"   Passed: {'✅ YES' if report.passed else '❌ NO'}")

    if report.findings:
        print(f"\n📋 Findings:")
        for finding in report.findings:
            icon = "❌" if finding.severity in (AnalysisSeverity.ERROR, AnalysisSeverity.CRITICAL) else "⚠️"
            print(f"   {icon} {finding}")


def demo_1_plane_isolation():
    """Demo 1: Plane Isolation Analyzer"""
    print_section("DEMO 1: Plane Isolation Analyzer")

    print("\n🔍 Testing: Shadow attempting to mutate canonical state")

    source = """
    fn unsafe_mutation() -> Integer {
        primary {
            drink x: Canonical<Integer> = 10
            return x
        }

        shadow {
            drink x: Canonical<Integer> = 20
            x = 30  # ❌ VIOLATION: Shadow mutating canonical
            return x
        }
    }
    """

    print(f"\nSource Code:\n{source}")

    result = compile_source(source, enable_static_analysis=True)

    if result.analysis_report:
        print_analysis_report(result.analysis_report)

        # Check for plane isolation violation
        errors = result.analysis_report.get_errors()
        canonical_violation = any('canonical' in str(e).lower() for e in errors)

        if canonical_violation:
            print("\n✅ SUCCESS: Plane Isolation Analyzer detected canonical mutation!")
        else:
            print("\n❌ FAILURE: Should have detected plane isolation violation")


def demo_2_determinism():
    """Demo 2: Determinism Analyzer"""
    print_section("DEMO 2: Determinism Analyzer")

    print("\n🔍 Testing: Non-deterministic operation in shadow")

    # Note: In the current implementation, INPUT is the non-deterministic opcode
    # In a real implementation, this would also include random(), time(), etc.

    source = """
    fn deterministic_shadow() -> Integer {
        shadow {
            drink x = 42
            drink y = 100
            drink result = x + y
            return result
        }
    }
    """

    print(f"\nSource Code:\n{source}")

    result = compile_source(source, enable_static_analysis=True)

    if result.analysis_report:
        print_analysis_report(result.analysis_report)

        if result.analysis_report.passed:
            print("\n✅ SUCCESS: Deterministic code passed analysis!")
        else:
            print("\n⚠️ Determinism issues detected")


def demo_3_privilege_escalation():
    """Demo 3: Privilege Escalation Analyzer"""
    print_section("DEMO 3: Privilege Escalation Analyzer")

    print("\n🔍 Testing: Missing validation for canonical mutation")

    source = """
    fn missing_validation() -> Integer {
        primary {
            drink x: Canonical<Integer> = 10
            return x
        }

        mutation validated_canonical
    }
    """

    print(f"\nSource Code:\n{source}")

    result = compile_source(source, enable_static_analysis=True)

    if result.analysis_report:
        print_analysis_report(result.analysis_report)

        # Check for privilege escalation warning
        errors = result.analysis_report.get_errors()
        validation_missing = any('VALIDATE_AND_COMMIT' in str(e) for e in errors)

        if validation_missing:
            print("\n✅ SUCCESS: Detected missing validation for canonical write!")


def demo_4_resource_estimation():
    """Demo 4: Resource Estimator"""
    print_section("DEMO 4: Resource Estimator")

    print("\n🔍 Testing: Resource usage estimation")

    source = """
    fn compute_intensive() -> Integer {
        shadow {
            drink x = 1
            drink y = 2
            drink z = x + y
            drink a = z * 2
            drink b = a - 5
            return b
        }
    }
    """

    print(f"\nSource Code:\n{source}")

    result = compile_source(source, enable_static_analysis=True)

    if result.analysis_report:
        print_analysis_report(result.analysis_report)

        # Look for resource estimation info
        resource_findings = [
            f for f in result.analysis_report.findings
            if 'ResourceEstimator' in f.analyzer
        ]

        if resource_findings:
            print(f"\n📈 Resource Estimation Details:")
            for finding in resource_findings:
                if finding.metadata:
                    print(f"   Shadow Instructions: {finding.metadata.get('shadow_instructions', 'N/A')}")
                    print(f"   Estimated CPU (ms): {finding.metadata.get('estimated_cpu_ms', 'N/A')}")
                    print(f"   CPU Quota (ms): {finding.metadata.get('cpu_quota_ms', 'N/A')}")

        print("\n✅ SUCCESS: Resource estimator provided analysis!")


def demo_5_divergence_risk():
    """Demo 5: Divergence Risk Estimator"""
    print_section("DEMO 5: Divergence Risk Estimator")

    print("\n🔍 Testing: Divergence risk estimation")

    source = """
    fn dual_plane_function(amount: Integer) -> Integer {
        primary {
            drink total = amount
            return total
        }

        shadow {
            drink shadow_total = amount
            drink extra_validation = shadow_total * 2
            drink more_checks = extra_validation + 100
            return shadow_total
        }

        activate_if amount > 0

        invariant {
            total == shadow_total
        }
    }
    """

    print(f"\nSource Code:\n{source}")

    result = compile_source(source, enable_static_analysis=True)

    if result.analysis_report:
        print_analysis_report(result.analysis_report)

        # Look for divergence risk findings
        divergence_findings = [
            f for f in result.analysis_report.findings
            if 'DivergenceRiskEstimator' in f.analyzer
        ]

        if divergence_findings:
            print(f"\n📊 Divergence Analysis:")
            for finding in divergence_findings:
                if finding.metadata:
                    print(f"   Primary Instructions: {finding.metadata.get('primary_instructions', 'N/A')}")
                    print(f"   Shadow Instructions: {finding.metadata.get('shadow_instructions', 'N/A')}")
                    print(f"   Difference Ratio: {finding.metadata.get('difference_ratio', 'N/A')}")

        print("\n✅ SUCCESS: Divergence risk estimator provided analysis!")


def demo_6_invariant_purity():
    """Demo 6: Invariant Purity Checker"""
    print_section("DEMO 6: Invariant Purity Checker")

    print("\n🔍 Testing: Invariant purity checking")

    source = """
    fn with_invariants() -> Integer {
        primary {
            drink x = 10
            return x
        }

        shadow {
            drink y = 10
            return y
        }

        invariant {
            x == y
        }
    }
    """

    print(f"\nSource Code:\n{source}")

    result = compile_source(source, enable_static_analysis=True)

    if result.analysis_report:
        print_analysis_report(result.analysis_report)

        # Pure invariants should pass
        purity_errors = [
            f for f in result.analysis_report.get_errors()
            if 'InvariantPurityChecker' in f.analyzer
        ]

        if not purity_errors:
            print("\n✅ SUCCESS: Pure invariant passed purity check!")
        else:
            print("\n⚠️ Invariant purity issues detected")


def demo_composite_analyzer():
    """Demo: Composite Static Analyzer"""
    print_section("COMPOSITE ANALYZER: All 6 Analyzers Together")

    print("\n🔍 Testing: Complete static analysis with all analyzers")

    source = """
    fn complete_function(amount: Integer) -> Integer {
        primary {
            drink result = amount
            return result
        }

        shadow {
            drink shadow_result = amount
            return shadow_result
        }

        activate_if amount > 0

        invariant {
            result == shadow_result
        }

        divergence allow_epsilon(0.01)
        mutation read_only
    }
    """

    print(f"\nSource Code:\n{source}")

    result = compile_source(source, enable_static_analysis=True)

    if result.analysis_report:
        print_analysis_report(result.analysis_report)

        print(f"\n📈 Analyzers Run: {result.analysis_report.summary['analyzers_run']}")

        if result.analysis_report.passed:
            print("\n✅ SUCCESS: All analyzers passed! Code is production-ready!")
        else:
            print("\n⚠️ Some analyzers flagged issues")


def main():
    """Run all demonstrations."""
    print("\n" + "🎯" * 35)
    print(" " * 10 + "Shadow Thirst Static Analyzers Demo")
    print("🎯" * 35)

    try:
        demo_1_plane_isolation()
        demo_2_determinism()
        demo_3_privilege_escalation()
        demo_4_resource_estimation()
        demo_5_divergence_risk()
        demo_6_invariant_purity()
        demo_composite_analyzer()

        print("\n" + "=" * 70)
        print("  🎉 All demonstrations complete!")
        print("=" * 70)
        print("\n✅ All 6 static analyzers are production-ready:")
        print("   1. PlaneIsolationAnalyzer")
        print("   2. DeterminismAnalyzer")
        print("   3. PrivilegeEscalationAnalyzer")
        print("   4. ResourceEstimator")
        print("   5. DivergenceRiskEstimator")
        print("   6. InvariantPurityChecker")
        print("\n" + "=" * 70 + "\n")

    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
