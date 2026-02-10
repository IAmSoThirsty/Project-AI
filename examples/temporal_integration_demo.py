#!/usr/bin/env python3
"""
Example demonstrating the Temporal integration.

This script shows how to use the AI Controller to start and execute
workflows. It's designed to work even without a Temporal server running
(it will show connection errors, which is expected for demo purposes).

Usage:
    python examples/temporal_integration_demo.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app.service.ai_controller import AIController


async def demo_without_server():
    """
    Demonstrate the integration structure (will fail without Temporal server).

    This shows the proper way to use the controller even if server is not running.
    """
    print("=" * 70)
    print("Temporal Integration Demo")
    print("=" * 70)
    print()
    print("This demo shows how to use the Temporal integration.")
    print("Note: A Temporal server must be running for this to work.")
    print()
    print("To start the Temporal server:")
    print("  docker-compose up -d temporal temporal-postgresql")
    print()
    print("To start a worker:")
    print("  python -m integrations.temporal.worker")
    print()
    print("=" * 70)
    print()

    controller = AIController()

    print("1. Testing connection to Temporal server...")
    try:
        await controller.connect()
        print("   ✓ Connected to Temporal server")

        print()
        print("2. Starting an example workflow...")
        result = await controller.process_ai_request(
            data="Explain the concept of machine learning",
            user_id="demo_user",
            workflow_id="demo-workflow-test",
        )

        print("   ✓ Workflow completed")
        print(f"   - Success: {result.success}")

        if result.success:
            print(f"   - Result: {result.result}")
            print(f"   - Steps completed: {result.steps_completed}")
        else:
            print(f"   - Error: {result.error}")

    except ConnectionError as e:
        print(f"   ✗ Connection failed: {e}")
        print()
        print("   This is expected if Temporal server is not running.")
        print("   Start it with: docker-compose up -d temporal")

    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")

    finally:
        await controller.close()
        print()
        print("=" * 70)
        print("Demo complete")
        print("=" * 70)


async def demo_workflow_structure():
    """Show the workflow structure without connecting to server."""
    print()
    print("=" * 70)
    print("Workflow Structure Information")
    print("=" * 70)
    print()

    print("Available Workflows:")
    print("  - ExampleWorkflow: Multi-step AI processing")
    print()

    print("Available Activities:")
    print("  - validate_input: Validate request data")
    print("  - simulate_ai_call: Simulate AI API call")
    print("  - process_ai_task: Process results")
    print()

    print("Usage Example:")
    print("""
from app.service.ai_controller import AIController

async def main():
    controller = AIController()
    result = await controller.process_ai_request(
        data="Your input here",
        user_id="user123"
    )
    print(f"Success: {result.success}")
    await controller.close()
""")
    print()
    print("=" * 70)


async def main():
    """Main entry point."""
    await demo_without_server()
    await demo_workflow_structure()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        sys.exit(0)
