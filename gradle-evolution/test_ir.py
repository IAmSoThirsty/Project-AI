#!/usr/bin/env python
"""
Simple test script for God Tier Intent Compiler
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ir.compiler import IntentCompiler
from ir.ir_executor import IRExecutor
from ir.optimizer import IROptimizer
from ir.verifier import IRVerifier


def test_basic_compilation():
    """Test basic YAML compilation"""
    print("=== Testing Basic Compilation ===")

    yaml_content = """
intent: build-python-module
version: 1.0
steps:
  - action: validate
    policies: [non_maleficence, transparency]
  - action: compile
    source: src/
    output: build/
  - action: test
    suite: pytest
  - action: package
    format: wheel
"""

    compiler = IntentCompiler(governance_enabled=True)
    graph = compiler.compile(yaml_content, source_file="test.yaml")

    print(f"✓ Compiled {len(graph.nodes)} IR nodes")
    print(f"✓ Entry node: {graph.entry_node}")
    print(f"✓ Metadata: {graph.metadata}")

    return graph


def test_optimization(graph):
    """Test IR optimization"""
    print("\n=== Testing Optimization ===")

    optimizer = IROptimizer(optimization_level=2)
    optimized_graph = optimizer.optimize(graph)

    stats = optimizer.get_statistics()
    print(f"✓ Optimized: {stats['nodes_before']} -> {stats['nodes_after']} nodes")
    print(f"✓ Dead code removed: {stats['dead_code_removed']}")
    print(f"✓ Constants folded: {stats['constants_folded']}")

    return optimized_graph


def test_verification(graph):
    """Test formal verification"""
    print("\n=== Testing Verification ===")

    verifier = IRVerifier(strict_mode=True)
    verification = verifier.verify(graph)

    verified_count = len([r for r in verification['results'] if r['verified']])
    total_count = len(verification['results'])

    print(f"✓ Verification: {verified_count}/{total_count} properties verified")

    for result in verification['results']:
        status = "✓" if result['verified'] else "✗"
        print(f"  {status} {result['property']}: confidence={result['confidence']:.2f}")

    return verification


def test_execution(graph):
    """Test deterministic execution"""
    print("\n=== Testing Execution ===")

    executor = IRExecutor(enable_tracing=True)
    results = executor.execute(graph)

    print(f"✓ Status: {results['status']}")
    print(f"✓ Nodes executed: {results['nodes_executed']}")
    print(f"✓ Execution time: {results['execution_time_ms']:.2f}ms")
    print(f"✓ CPU time: {results['resource_usage']['cpu_time_ms']:.2f}ms")
    print(f"✓ Memory: {results['resource_usage']['memory_bytes'] / (1024*1024):.2f}MB")

    return results


def main():
    """Run all tests"""
    print("=" * 60)
    print("God Tier Intent Compiler - Test Suite")
    print("=" * 60)

    try:
        # Test compilation
        graph = test_basic_compilation()

        # Test optimization
        optimized_graph = test_optimization(graph)

        # Test verification
        verification = test_verification(optimized_graph)

        # Test execution
        results = test_execution(optimized_graph)

        print("\n" + "=" * 60)
        print("✓ All tests passed successfully!")
        print("=" * 60)

        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
