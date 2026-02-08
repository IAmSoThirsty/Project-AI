"""
God Tier Intent Compiler - Comprehensive Example

Demonstrates complete compilation pipeline from YAML intent to verified,
optimized, and executed IR with formal proof certificates.
"""

import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_basic_compilation():
    """Example: Basic YAML compilation"""
    from compiler import IntentCompiler

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

    logger.info("=== Basic Compilation Example ===")

    compiler = IntentCompiler(governance_enabled=True)
    graph = compiler.compile(yaml_content, source_file="example.yaml")

    logger.info(f"Compiled {len(graph.nodes)} IR nodes")
    logger.info(f"Entry node: {graph.entry_node}")
    logger.info(f"Metadata: {graph.metadata}")

    # Show compilation report
    report = compiler.get_compilation_report()
    logger.info(f"Compilation report: {json.dumps(report, indent=2)}")

    return graph


def example_optimization():
    """Example: IR optimization"""
    from compiler import IntentCompiler
    from optimizer import IROptimizer

    yaml_content = """
intent: compute-example
version: 1.0
steps:
  - action: validate
    policies: [safety]
  - action: compile
    source: src/
  - action: compile
    source: src/
  - action: test
    suite: pytest
"""

    logger.info("\n=== Optimization Example ===")

    # Compile
    compiler = IntentCompiler()
    graph = compiler.compile(yaml_content)

    logger.info(f"Before optimization: {len(graph.nodes)} nodes")

    # Optimize
    optimizer = IROptimizer(optimization_level=2)
    optimized_graph = optimizer.optimize(graph)

    logger.info(f"After optimization: {len(optimized_graph.nodes)} nodes")

    # Show statistics
    stats = optimizer.get_statistics()
    logger.info(f"Optimization stats: {json.dumps(stats, indent=2)}")

    # Show cost estimation
    original_cost = optimizer.estimate_cost(graph)
    optimized_cost = optimizer.estimate_cost(optimized_graph)
    logger.info(f"Cost reduction: {original_cost:.2f} -> {optimized_cost:.2f} ({100*(1-optimized_cost/original_cost):.1f}%)")

    return optimized_graph


def example_verification():
    """Example: Formal verification"""
    from compiler import IntentCompiler
    from verifier import IRVerifier

    yaml_content = """
intent: safe-deployment
version: 1.0
steps:
  - action: validate
    policies: [non_maleficence, transparency, accountability]
  - action: compile
    source: src/
    output: build/
  - action: test
    suite: pytest
  - action: package
    format: wheel
  - action: deploy
    target: production
"""

    logger.info("\n=== Verification Example ===")

    # Compile
    compiler = IntentCompiler(governance_enabled=True)
    graph = compiler.compile(yaml_content)

    # Verify
    verifier = IRVerifier(strict_mode=True)
    verification = verifier.verify(graph)

    logger.info(f"Verification result: {'PASSED' if verification['all_verified'] else 'FAILED'}")
    logger.info(f"Properties verified: {len([r for r in verification['results'] if r['verified']])}/{len(verification['results'])}")

    # Show results
    for result in verification['results']:
        status = "✓" if result['verified'] else "✗"
        logger.info(f"  {status} {result['property']}: confidence={result['confidence']:.2f}")
        if result['warnings']:
            for warning in result['warnings']:
                logger.info(f"    - {warning}")

    # Generate proof certificate
    certificate = verifier.generate_proof_certificate(graph)
    logger.info(f"Proof certificate hash: {certificate['certificate_hash']}")

    # Verify certificate
    is_valid = verifier.verify_certificate(certificate, graph)
    logger.info(f"Certificate validation: {'VALID' if is_valid else 'INVALID'}")

    return verification, certificate


def example_execution():
    """Example: Deterministic execution"""
    from compiler import IntentCompiler
    from ir_executor import IRExecutor

    yaml_content = """
intent: execute-workflow
version: 1.0
steps:
  - action: validate
    policies: [safety]
  - action: log
    message: "Starting workflow"
    level: info
  - action: compile
    source: src/
    output: build/
  - action: test
    suite: pytest
  - action: log
    message: "Workflow complete"
    level: info
  - action: checkpoint
"""

    logger.info("\n=== Execution Example ===")

    # Compile
    compiler = IntentCompiler()
    graph = compiler.compile(yaml_content)

    # Execute
    executor = IRExecutor(
        max_execution_time_ms=60000,
        enable_tracing=True,
        enable_checkpointing=True
    )

    results = executor.execute(graph)

    logger.info(f"Execution status: {results['status']}")
    logger.info(f"Nodes executed: {results['nodes_executed']}")
    logger.info(f"Execution time: {results['execution_time_ms']:.2f}ms")
    logger.info(f"Resource usage: {json.dumps(results['resource_usage'], indent=2)}")

    # Show trace
    if results.get('trace'):
        logger.info(f"Execution trace ({len(results['trace'])} entries):")
        for i, trace_entry in enumerate(results['trace'][:5]):  # Show first 5
            logger.info(f"  [{i}] {trace_entry['opcode']} (node {trace_entry['node_id']}): {trace_entry['duration_ms']:.2f}ms")
        if len(results['trace']) > 5:
            logger.info(f"  ... and {len(results['trace']) - 5} more")

    return results


def example_complete_pipeline():
    """Example: Complete compilation pipeline"""
    from compiler import IntentCompiler
    from ir_executor import IRExecutor
    from optimizer import IROptimizer
    from verifier import IRVerifier

    yaml_content = """
intent: production-deployment
version: 1.0
steps:
  - action: validate
    policies: [non_maleficence, transparency, accountability, security]
  - action: compile
    source: src/
    output: build/
  - action: test
    suite: pytest
  - action: package
    format: wheel
  - action: checkpoint
  - action: deploy
    target: production
  - action: log
    message: "Deployment successful"
    level: info
"""

    logger.info("\n=== Complete Pipeline Example ===")

    # Step 1: Compile
    logger.info("Step 1: Compiling YAML to IR...")
    compiler = IntentCompiler(governance_enabled=True)
    graph = compiler.compile(yaml_content, source_file="production.yaml")
    logger.info(f"  ✓ Compiled {len(graph.nodes)} IR nodes")

    # Step 2: Optimize
    logger.info("Step 2: Optimizing IR...")
    optimizer = IROptimizer(optimization_level=2)
    optimized_graph = optimizer.optimize(graph)
    stats = optimizer.get_statistics()
    logger.info(f"  ✓ Optimized to {len(optimized_graph.nodes)} nodes ({stats['reduction_percent']:.1f}% reduction)")

    # Step 3: Verify
    logger.info("Step 3: Verifying correctness...")
    verifier = IRVerifier(strict_mode=True)
    verification = verifier.verify(optimized_graph)
    logger.info(f"  ✓ Verification: {len([r for r in verification['results'] if r['verified']])}/{len(verification['results'])} properties verified")

    if not verification['all_verified']:
        logger.warning("  ⚠ Some properties could not be verified:")
        for result in verification['results']:
            if not result['verified']:
                logger.warning(f"    - {result['property']}: {result['warnings']}")

    # Step 4: Generate proof certificate
    logger.info("Step 4: Generating proof certificate...")
    certificate = verifier.generate_proof_certificate(optimized_graph)
    logger.info(f"  ✓ Certificate generated: {certificate['certificate_hash'][:16]}...")

    # Step 5: Execute
    logger.info("Step 5: Executing IR...")
    executor = IRExecutor(enable_tracing=True)
    results = executor.execute(optimized_graph)
    logger.info(f"  ✓ Execution {results['status']}: {results['nodes_executed']} nodes in {results['execution_time_ms']:.2f}ms")

    # Summary
    logger.info("\n=== Pipeline Summary ===")
    logger.info(f"Intent: {graph.metadata['intent']}")
    logger.info(f"Original nodes: {stats['nodes_before']}")
    logger.info(f"Optimized nodes: {stats['nodes_after']}")
    logger.info(f"Verification: {'✓ PASSED' if verification['all_verified'] else '⚠ PARTIAL'}")
    logger.info(f"Execution: {results['status'].upper()}")
    logger.info(f"Total time: {results['execution_time_ms']:.2f}ms")
    logger.info("Resource usage:")
    logger.info(f"  CPU: {results['resource_usage']['cpu_time_ms']:.2f}ms")
    logger.info(f"  Memory: {results['resource_usage']['memory_bytes'] / (1024*1024):.2f}MB")
    logger.info(f"  I/O ops: {results['resource_usage']['io_operations']}")

    return {
        "graph": optimized_graph,
        "verification": verification,
        "certificate": certificate,
        "execution": results
    }


def example_serialization():
    """Example: IR serialization and deserialization"""
    from compiler import IntentCompiler
    from ir_schema import IRGraph

    yaml_content = """
intent: test-serialization
version: 1.0
steps:
  - action: compile
    source: src/
  - action: test
    suite: pytest
"""

    logger.info("\n=== Serialization Example ===")

    # Compile
    compiler = IntentCompiler()
    graph = compiler.compile(yaml_content)

    logger.info(f"Original graph: {len(graph.nodes)} nodes")

    # Serialize
    graph_dict = graph.to_dict()
    graph_json = json.dumps(graph_dict, indent=2)
    logger.info(f"Serialized to JSON ({len(graph_json)} bytes)")

    # Deserialize
    restored_dict = json.loads(graph_json)
    restored_graph = IRGraph.from_dict(restored_dict)
    logger.info(f"Deserialized graph: {len(restored_graph.nodes)} nodes")

    # Verify integrity
    assert len(graph.nodes) == len(restored_graph.nodes), "Node count mismatch"
    assert graph.entry_node == restored_graph.entry_node, "Entry node mismatch"
    logger.info("✓ Serialization integrity verified")

    return restored_graph


def main():
    """Run all examples"""
    logger.info("=" * 60)
    logger.info("God Tier Intent Compiler - Comprehensive Examples")
    logger.info("=" * 60)

    try:
        # Run examples
        example_basic_compilation()
        example_optimization()
        example_verification()
        example_execution()
        example_serialization()

        # Run complete pipeline
        pipeline_result = example_complete_pipeline()

        logger.info("\n" + "=" * 60)
        logger.info("All examples completed successfully!")
        logger.info("=" * 60)

        return pipeline_result

    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
