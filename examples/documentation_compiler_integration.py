"""Integration example: Using DocumentationCompilerAgent in Project-AI.

This example demonstrates how to use the DocumentationCompilerAgent
to generate documentation for Project-AI systems.
"""

from pathlib import Path

from app.agents.documentation_compiler import DocumentationCompilerAgent
from app.core.cognition_kernel import CognitionKernel


def example_basic_usage():
    """Basic usage: compile documentation for a single system."""
    print("=" * 60)
    print("Example 1: Basic System Documentation")
    print("=" * 60)

    # Initialize kernel and agent
    kernel = CognitionKernel()
    doc_agent = DocumentationCompilerAgent(kernel=kernel)

    # Compile documentation for InvariantEngine
    doc_path = doc_agent.compile_system_documentation(
        system_name="InvariantEngine",
        evidence_paths=[
            "src/app/core/invariant_engine.py",
            "tests/test_invariant_engine.py",
            "config/invariants.yaml",
        ],
        include_tests=True,
        include_code_samples=True,
    )

    print(f"✅ Documentation generated: {doc_path}")
    print()


def example_evidence_extraction():
    """Extract and analyze evidence from a source file."""
    print("=" * 60)
    print("Example 2: Evidence Extraction")
    print("=" * 60)

    doc_agent = DocumentationCompilerAgent(kernel=None)

    # Extract evidence from code
    code_evidence = doc_agent.extract_evidence(
        "src/app/agents/oversight.py",
        evidence_type="code",
    )

    print("Code Evidence:")
    print(f"  Classes found: {', '.join(code_evidence['classes'][:3])}")
    print(f"  Functions found: {len(code_evidence['functions'])}")
    print(f"  Has governance: {code_evidence['has_governance']}")
    print(f"  Has validation: {code_evidence['has_validation']}")
    print()

    # Extract evidence from tests
    test_evidence = doc_agent.extract_evidence(
        "tests/test_oversight.py",
        evidence_type="test",
    )

    print("Test Evidence:")
    print(f"  Test count: {test_evidence['test_count']}")
    print(f"  Test functions: {', '.join(test_evidence['test_functions'][:3])}")
    print(f"  Has unit tests: {test_evidence['has_unit_tests']}")
    print()


def example_documentation_verification():
    """Verify existing documentation against current codebase."""
    print("=" * 60)
    print("Example 3: Documentation Verification")
    print("=" * 60)

    doc_agent = DocumentationCompilerAgent(kernel=None)

    # Verify documentation
    result = doc_agent.verify_documentation(
        doc_path="docs/NIRL_IMPLEMENTATION.md",
        evidence_paths=[
            "src/app/core/nirl/heart.py",
            "src/app/core/nirl/mini_brain.py",
            "src/app/core/nirl/antibody.py",
            "src/app/core/nirl/forge.py",
        ],
    )

    print(f"Verification Status: {result['status']}")
    print(f"Evidence files analyzed: {result['evidence_files']}")

    if result["discrepancies"]:
        print("\nDiscrepancies found:")
        for discrepancy in result["discrepancies"]:
            print(f"  ⚠️  {discrepancy}")
    else:
        print("\n✅ No discrepancies found")

    if result["warnings"]:
        print("\nWarnings:")
        for warning in result["warnings"]:
            print(f"  ℹ️  {warning}")
    print()


def example_batch_documentation():
    """Generate documentation for multiple systems."""
    print("=" * 60)
    print("Example 4: Batch Documentation Generation")
    print("=" * 60)

    kernel = CognitionKernel()
    doc_agent = DocumentationCompilerAgent(
        kernel=kernel,
        output_dir="docs/generated",
    )

    # Define systems to document
    systems = [
        {
            "name": "OversightAgent",
            "paths": [
                "src/app/agents/oversight.py",
                "tests/test_oversight.py",
            ],
        },
        {
            "name": "ValidatorAgent",
            "paths": [
                "src/app/agents/validator.py",
                "tests/test_validator.py",
            ],
        },
        {
            "name": "ExplainabilityAgent",
            "paths": [
                "src/app/agents/explainability.py",
                "tests/test_explainability.py",
            ],
        },
    ]

    # Generate documentation for each system
    generated_docs = []
    for system in systems:
        try:
            doc_path = doc_agent.compile_system_documentation(
                system_name=system["name"],
                evidence_paths=system["paths"],
                include_tests=True,
            )
            generated_docs.append(doc_path)
            print(f"✅ {system['name']}: {doc_path}")
        except Exception as e:
            print(f"❌ {system['name']}: Failed - {e}")

    print(f"\n📚 Total documentation generated: {len(generated_docs)} files")
    print()


def example_custom_section_compilation():
    """Compile individual sections with custom evidence."""
    print("=" * 60)
    print("Example 5: Custom Section Compilation")
    print("=" * 60)

    doc_agent = DocumentationCompilerAgent(kernel=None)

    # Custom evidence dict
    custom_evidence = {
        "code": {
            "classes": ["ExecutionGate", "InvariantEngine"],
            "has_governance": True,
            "functions": ["validate", "execute", "check_invariants"],
        },
        "tests": {
            "test_count": 15,
            "has_unit_tests": True,
            "has_integration_tests": True,
        },
    }

    # Compile architecture section
    arch_section = doc_agent.compile_section(
        section_title="Architecture",
        evidence=custom_evidence,
        section_type="architecture",
    )

    print("Architecture Section:")
    print(f"  Title: {arch_section.title}")
    print(f"  Verification Status: {arch_section.verification_status}")
    print(f"  Content Preview: {arch_section.content[:100]}...")
    print()


def example_with_error_handling():
    """Demonstrate error handling and edge cases."""
    print("=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)

    doc_agent = DocumentationCompilerAgent(kernel=None)

    # Try to extract evidence from nonexistent file
    evidence = doc_agent.extract_evidence("/nonexistent/file.py")

    if "error" in evidence:
        print(f"❌ Error handled gracefully: {evidence['error']}")
    else:
        print("✅ Evidence extracted successfully")
    print()


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("DocumentationCompilerAgent Integration Examples")
    print("=" * 60)
    print()

    # Run examples (comment out examples that require actual files)
    # example_basic_usage()
    # example_evidence_extraction()
    # example_documentation_verification()
    # example_batch_documentation()
    example_custom_section_compilation()
    example_with_error_handling()

    print("=" * 60)
    print("Examples Complete")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
