"""
Shadow Thirst Enhanced Compiler - Demo Script

Demonstrates all major features of the enhanced compiler:
1. Taint analysis
2. Alias analysis
3. Value flow analysis
4. Symbolic execution
5. Test generation

Run with: python demo_enhanced.py
"""

import sys
from pathlib import Path

# Add to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from shadow_enhanced import (
    ShadowThirstEnhancedCompiler,
    TaintAnalyzer,
    AliasAnalyzer,
    ValueFlowAnalyzer,
    SymbolicExecutionEngine,
    AutomatedTestGenerator,
    Z3_AVAILABLE
)


def print_header(title: str):
    """Print section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def demo_taint_analysis():
    """Demonstrate taint analysis."""
    print_header("DEMO 1: Taint Analysis")
    
    # Sample vulnerable code
    sample_code = """
    drink user_input = sip()  # Tainted source
    drink query = "SELECT * FROM users WHERE id = " + user_input
    pour(query)  # Dangerous! Unsanitized tainted data to sink
    """
    
    print("Sample Code:")
    print(sample_code)
    
    compiler = ShadowThirstEnhancedCompiler(
        enable_taint_analysis=True,
        enable_alias_analysis=False,
        enable_value_flow=False,
        enable_symbolic_execution=False,
        enable_test_generation=False,
        performance_mode=True
    )
    
    report = compiler.analyze(sample_code, "taint_demo.shadow")
    
    print("\nResults:")
    if report.taint_analysis:
        ta = report.taint_analysis
        print(f"  Vulnerabilities Found: {ta.get('vulnerabilities', 0)}")
        print(f"  Analysis Time: {ta.get('analysis_time_ms', 0):.2f}ms")
        
        for finding in ta.get('findings', []):
            print(f"\n  [{finding['severity']}] {finding['type']}")
            print(f"  Message: {finding['message']}")
    
    print(f"\n  Status: {'✓ PASSED' if report.passed else '✗ FAILED'}")


def demo_alias_analysis():
    """Demonstrate alias analysis."""
    print_header("DEMO 2: Alias Analysis")
    
    sample_code = """
    drink x = 10
    drink y = x  # y aliases x
    drink z = y  # z aliases y and x
    """
    
    print("Sample Code:")
    print(sample_code)
    
    compiler = ShadowThirstEnhancedCompiler(
        enable_taint_analysis=False,
        enable_alias_analysis=True,
        enable_value_flow=False,
        enable_symbolic_execution=False,
        enable_test_generation=False,
        performance_mode=True
    )
    
    report = compiler.analyze(sample_code, "alias_demo.shadow")
    
    print("\nResults:")
    if report.alias_analysis:
        aa = report.alias_analysis
        print(f"  Alias Sets: {len(aa.get('alias_sets', {}))}")
        print(f"  Analysis Time: {aa.get('analysis_time_ms', 0):.2f}ms")
        
        print("\n  Points-To Graph:")
        for var, targets in aa.get('points_to_graph', {}).items():
            if targets:
                print(f"    {var} → {targets}")


def demo_value_flow():
    """Demonstrate value flow analysis."""
    print_header("DEMO 3: Value Flow Analysis")
    
    sample_code = """
    drink x = 5
    drink y = 10
    drink z = x + y  # Should be constant 15
    """
    
    print("Sample Code:")
    print(sample_code)
    
    compiler = ShadowThirstEnhancedCompiler(
        enable_taint_analysis=False,
        enable_alias_analysis=False,
        enable_value_flow=True,
        enable_symbolic_execution=False,
        enable_test_generation=False,
        performance_mode=True
    )
    
    report = compiler.analyze(sample_code, "value_flow_demo.shadow")
    
    print("\nResults:")
    if report.value_flow_analysis:
        vfa = report.value_flow_analysis
        print(f"  Value Ranges Computed: {len(vfa.get('value_map', {}))}")
        print(f"  Def-Use Chains: {len(vfa.get('def_use_chains', {}))}")
        print(f"  Analysis Time: {vfa.get('analysis_time_ms', 0):.2f}ms")


def demo_symbolic_execution():
    """Demonstrate symbolic execution."""
    print_header("DEMO 4: Symbolic Execution")
    
    if not Z3_AVAILABLE:
        print("\n  ⚠ Z3 not available. Install with: pip install z3-solver")
        print("  Running in simplified mode...\n")
    
    sample_code = """
    drink x: Integer = sip()
    
    thirsty x > 10 {
        pour("Large")
    }
    hydrated {
        pour("Small")
    }
    """
    
    print("Sample Code:")
    print(sample_code)
    
    compiler = ShadowThirstEnhancedCompiler(
        enable_taint_analysis=False,
        enable_alias_analysis=False,
        enable_value_flow=False,
        enable_symbolic_execution=True,
        enable_test_generation=False,
        performance_mode=False
    )
    
    report = compiler.analyze(sample_code, "symbolic_demo.shadow")
    
    print("\nResults:")
    if report.symbolic_execution:
        se = report.symbolic_execution
        print(f"  Paths Explored: {se.get('paths_explored', 0)}")
        print(f"  Execution Time: {se.get('execution_time_ms', 0):.2f}ms")
        print(f"  Z3 Available: {Z3_AVAILABLE}")


def demo_test_generation():
    """Demonstrate automated test generation."""
    print_header("DEMO 5: Automated Test Generation")
    
    sample_code = """
    glass calculate(x: Integer, y: Integer) -> Integer {
        thirsty x > y {
            return x - y
        }
        hydrated {
            return y - x
        }
    }
    """
    
    print("Sample Code:")
    print(sample_code)
    
    compiler = ShadowThirstEnhancedCompiler(
        enable_taint_analysis=False,
        enable_alias_analysis=False,
        enable_value_flow=False,
        enable_symbolic_execution=True,
        enable_test_generation=True,
        target_coverage=90.0,
        performance_mode=False
    )
    
    report = compiler.analyze(sample_code, "test_gen_demo.shadow")
    
    print("\nResults:")
    if report.test_generation:
        tg = report.test_generation
        coverage = tg.get('coverage', {})
        
        print(f"  Tests Generated: {len(tg.get('test_cases', []))}")
        print(f"  Line Coverage: {coverage.get('line', 0):.1f}%")
        print(f"  Branch Coverage: {coverage.get('branch', 0):.1f}%")
        print(f"  Target Achieved: {tg.get('target_achieved', False)}")
        print(f"  Generation Time: {tg.get('generation_time_ms', 0):.2f}ms")


def demo_full_analysis():
    """Demonstrate full analysis pipeline."""
    print_header("DEMO 6: Full Analysis Pipeline")
    
    sample_code = """
    glass authenticate(username: String, password: String) -> Boolean {
        drink sanitized_user = sanitize(username)
        drink query = "SELECT * FROM users WHERE username = " + sanitized_user
        
        thirsty password == "" {
            return false
        }
        
        drink result = execute(query)
        return result != null
    }
    """
    
    print("Sample Code:")
    print(sample_code)
    
    print("\nRunning full analysis (all features enabled)...")
    
    compiler = ShadowThirstEnhancedCompiler(
        enable_taint_analysis=True,
        enable_alias_analysis=True,
        enable_value_flow=True,
        enable_symbolic_execution=True,
        enable_test_generation=True,
        target_coverage=95.0,
        performance_mode=False
    )
    
    report = compiler.analyze(sample_code, "full_demo.shadow")
    
    print("\n" + "-" * 80)
    print("COMPREHENSIVE RESULTS")
    print("-" * 80)
    
    print(f"\nOverall Status: {'✓ PASSED' if report.passed else '✗ FAILED'}")
    print(f"Lines Analyzed: {report.lines_analyzed}")
    print(f"Total Analysis Time: {report.total_analysis_time_ms:.2f}ms")
    print(f"Performance: {report.lines_per_second:.0f} LOC/sec")
    
    if report.taint_analysis:
        print(f"\nTaint Analysis:")
        print(f"  Vulnerabilities: {report.taint_analysis.get('vulnerabilities', 0)}")
        print(f"  Time: {report.taint_analysis.get('analysis_time_ms', 0):.2f}ms")
    
    if report.alias_analysis:
        print(f"\nAlias Analysis:")
        print(f"  Alias Sets: {len(report.alias_analysis.get('alias_sets', {}))}")
        print(f"  Time: {report.alias_analysis.get('analysis_time_ms', 0):.2f}ms")
    
    if report.value_flow_analysis:
        print(f"\nValue Flow Analysis:")
        print(f"  Value Ranges: {len(report.value_flow_analysis.get('value_map', {}))}")
        print(f"  Time: {report.value_flow_analysis.get('analysis_time_ms', 0):.2f}ms")
    
    if report.symbolic_execution:
        print(f"\nSymbolic Execution:")
        print(f"  Paths Explored: {report.symbolic_execution.get('paths_explored', 0)}")
        print(f"  Time: {report.symbolic_execution.get('execution_time_ms', 0):.2f}ms")
    
    if report.test_generation:
        coverage = report.test_generation.get('coverage', {})
        print(f"\nTest Generation:")
        print(f"  Tests: {len(report.test_generation.get('test_cases', []))}")
        print(f"  Line Coverage: {coverage.get('line', 0):.1f}%")
        print(f"  Branch Coverage: {coverage.get('branch', 0):.1f}%")
        print(f"  Time: {report.test_generation.get('generation_time_ms', 0):.2f}ms")


def demo_performance_mode():
    """Demonstrate performance mode."""
    print_header("DEMO 7: Performance Mode Comparison")
    
    sample_code = """
    glass fibonacci(n: Integer) -> Integer {
        thirsty n <= 1 {
            return n
        }
        
        drink a = fibonacci(n - 1)
        drink b = fibonacci(n - 2)
        return a + b
    }
    """
    
    print("Sample Code:")
    print(sample_code)
    
    # Normal mode
    print("\n[1] Normal Mode (thorough):")
    compiler_normal = ShadowThirstEnhancedCompiler(performance_mode=False)
    report_normal = compiler_normal.analyze(sample_code, "perf_normal.shadow")
    print(f"  Time: {report_normal.total_analysis_time_ms:.2f}ms")
    print(f"  Speed: {report_normal.lines_per_second:.0f} LOC/sec")
    
    # Performance mode
    print("\n[2] Performance Mode (fast):")
    compiler_fast = ShadowThirstEnhancedCompiler(
        enable_symbolic_execution=False,
        enable_test_generation=False,
        performance_mode=True
    )
    report_fast = compiler_fast.analyze(sample_code, "perf_fast.shadow")
    print(f"  Time: {report_fast.total_analysis_time_ms:.2f}ms")
    print(f"  Speed: {report_fast.lines_per_second:.0f} LOC/sec")
    
    # Calculate speedup
    if report_fast.total_analysis_time_ms > 0:
        speedup = report_normal.total_analysis_time_ms / report_fast.total_analysis_time_ms
        print(f"\n  Speedup: {speedup:.1f}x faster")


def main():
    """Run all demos."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 78 + "║")
    print("║" + "  Shadow Thirst Enhanced Compiler - Interactive Demo".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("║" + "  Version 2.0.0 | Performance: 10,000+ LOC/sec".center(78) + "║")
    print("║" + " " * 78 + "║")
    print("╚" + "=" * 78 + "╝")
    
    print("\nThis demo showcases all major features of the enhanced compiler.")
    print(f"Z3 Constraint Solver: {'✓ Available' if Z3_AVAILABLE else '✗ Not Available'}")
    
    try:
        # Run demos
        demo_taint_analysis()
        demo_alias_analysis()
        demo_value_flow()
        demo_symbolic_execution()
        demo_test_generation()
        demo_full_analysis()
        demo_performance_mode()
        
        # Summary
        print_header("DEMO COMPLETE")
        print("\n✓ All demos executed successfully!")
        print("\nNext Steps:")
        print("  1. Read SHADOW_ENHANCED_DOCUMENTATION.md for full details")
        print("  2. Try analyzing your own Shadow Thirst programs")
        print("  3. Integrate into your CI/CD pipeline")
        print("  4. Install Z3 for full symbolic execution: pip install z3-solver")
        print("\nUsage:")
        print("  python -m shadow_enhanced your_program.shadow")
        print("")
        
    except Exception as e:
        print(f"\n✗ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
