#!/usr/bin/env python3
"""
Test client for the canonical scenario HTTP server.

This script tests the server endpoints without requiring the server to be running.
It simulates the execute_canonical_scenario function to validate the interface.
"""

import json
from pathlib import Path


def test_execute_canonical():
    """Test canonical scenario execution locally."""
    print("=" * 80)
    print("🧪 TESTING CANONICAL SERVER INTERFACE")
    print("=" * 80)
    print()

    # Import the execution function
    import sys

    sys.path.insert(0, str(Path(__file__).parent.parent))

    from canonical.server import execute_canonical_scenario

    print("📋 Executing canonical scenario...")
    print()

    result = execute_canonical_scenario()

    print("✅ Execution complete!")
    print()

    # Display results
    print("📊 Results:")
    print(f"   Status: {result['status']}")
    print(f"   Exit Code: {result['exit_code']}")
    print(f"   Duration: {result['duration_ms']:.2f}ms")

    if "trace_hash" in result:
        print(f"   Trace Hash: sha256:{result['trace_hash'][:16]}...")

    if "metrics" in result:
        metrics = result["metrics"]
        print()
        print("📈 Metrics:")

        if "success_criteria" in metrics:
            sc = metrics["success_criteria"]
            print(
                f"   Success Criteria: {'✅ ALL MET' if sc['all_met'] else '❌ FAILED'}"
            )

        if "invariants" in metrics:
            inv = metrics["invariants"]
            print(
                f"   Invariants: {inv['passed']}/{inv['total']} passed ({inv['pass_rate']*100:.1f}%)"
            )

    # Show sample artifacts (truncated)
    if "artifacts" in result:
        artifacts = result["artifacts"]
        if "trace" in artifacts:
            trace = artifacts["trace"]
            print()
            print("📦 Artifacts:")
            print(f"   Trace size: {len(json.dumps(trace))} bytes")
            print(f"   Scenario: {trace.get('scenario', {}).get('name', 'N/A')}")

        if "stdout" in artifacts and artifacts["stdout"]:
            print()
            print("📄 Sample stdout (last 500 chars):")
            print("   " + artifacts["stdout"][-500:].replace("\n", "\n   "))

    print()
    print("=" * 80)

    return result


def test_api_shape():
    """Test that the API returns expected shape."""
    print()
    print("🔍 Validating API response shape...")
    print()

    result = test_execute_canonical()

    # Required fields
    required_fields = [
        "status",
        "exit_code",
        "duration_ms",
        "trace_hash",
        "metrics",
        "artifacts",
    ]

    missing = []
    for field in required_fields:
        if field not in result:
            missing.append(field)
            print(f"   ❌ Missing field: {field}")
        else:
            print(f"   ✅ Has field: {field}")

    print()

    if missing:
        print(f"❌ API shape validation FAILED: missing {len(missing)} field(s)")
        return False
    else:
        print("✅ API shape validation PASSED")
        return True


def show_curl_examples():
    """Show curl examples for external access."""
    print()
    print("=" * 80)
    print("🌐 EXTERNAL ACCESS EXAMPLES")
    print("=" * 80)
    print()

    print("# Start the server:")
    print("python canonical/server.py")
    print("# or")
    print("uvicorn canonical.server:app --host 0.0.0.0 --port 8000")
    print()

    print("# Execute canonical scenario:")
    print("curl -X POST http://localhost:8000/run-canonical")
    print()

    print("# Health check:")
    print("curl http://localhost:8000/health")
    print()

    print("# Get metrics:")
    print("curl http://localhost:8000/metrics")
    print()

    print("# View API docs:")
    print("curl http://localhost:8000/")
    print("# or open http://localhost:8000/docs in browser")
    print()

    print("# External access (once deployed):")
    print("curl -X POST https://project-ai.example.com/run-canonical")
    print()

    print("=" * 80)
    print()


if __name__ == "__main__":
    # Run tests
    shape_valid = test_api_shape()

    # Show examples
    show_curl_examples()

    # Exit with appropriate code
    exit(0 if shape_valid else 1)
