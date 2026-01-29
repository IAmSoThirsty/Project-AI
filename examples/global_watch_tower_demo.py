"""Example: Global Watch Tower Integration.

This example demonstrates how to use the Global Watch Tower system
for system-wide file verification and monitoring.

Features demonstrated:
1. Initialization with custom configuration
2. File verification and quarantine
3. Statistics monitoring
4. Emergency lockdown
5. Incident tracking
"""

from pathlib import Path
from tempfile import NamedTemporaryFile

from app.core.global_watch_tower import (
    GlobalWatchTower,
    get_global_watch_tower,
    verify_file_globally,
)


def example_basic_initialization():
    """Example 1: Basic initialization and verification."""
    print("=" * 80)
    print("Example 1: Basic Initialization and Verification")
    print("=" * 80)

    # Initialize the global watch tower system
    # This should be done once at application startup
    tower = GlobalWatchTower.initialize(
        num_port_admins=1,
        towers_per_port=5,
        gates_per_tower=3,
        data_dir="data",
        timeout=8,
    )

    print(f"✅ Watch tower initialized")
    print(f"   - Port Admins: {len(tower.port_admins)}")
    print(f"   - Watch Towers: {len(tower.watch_towers)}")
    print(f"   - Gate Guardians: {len(tower.gate_guardians)}")

    # Verify a file
    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("# Test file\nprint('Hello from verified file')\n")
        test_file = Path(f.name)

    print(f"\n📁 Verifying file: {test_file.name}")
    result = tower.verify_file(test_file)

    print(f"   - Success: {result['success']}")
    print(f"   - Verdict: {result['verdict']}")
    print(f"   - Imports found: {len(result['deps']['imports'])}")

    # Cleanup
    test_file.unlink()
    GlobalWatchTower.reset()
    print("\n" + "=" * 80 + "\n")


def example_quarantine_workflow():
    """Example 2: Quarantine and deferred processing."""
    print("=" * 80)
    print("Example 2: Quarantine and Deferred Processing")
    print("=" * 80)

    tower = GlobalWatchTower.initialize()

    # Create a test file
    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("import sys\nimport os\nprint('Suspicious activity')\n")
        test_file = Path(f.name)

    print(f"📁 Placing file in quarantine: {test_file.name}")

    # Place in quarantine without processing
    box = tower.quarantine_file(test_file)
    print(f"   - Quarantine box created")
    print(f"   - Sealed: {box.sealed}")
    print(f"   - Verified: {box.verified}")

    # Check stats
    stats = tower.get_stats()
    print(f"\n📊 Current quarantine status:")
    print(f"   - Total quarantined: {stats['total_quarantined']}")
    print(f"   - Active in quarantine: {stats['active_quarantine']}")

    # Later: process the quarantined file
    print(f"\n🔍 Processing quarantined file...")
    result = tower.process_quarantined(str(test_file))
    print(f"   - Success: {result['success']}")
    print(f"   - Verdict: {result['verdict']}")

    # Check stats after processing
    stats = tower.get_stats()
    print(f"\n📊 After processing:")
    print(f"   - Total verifications: {stats['total_verifications']}")
    print(f"   - Active in quarantine: {stats['active_quarantine']}")

    # Cleanup
    test_file.unlink()
    GlobalWatchTower.reset()
    print("\n" + "=" * 80 + "\n")


def example_statistics_and_monitoring():
    """Example 3: Statistics and monitoring."""
    print("=" * 80)
    print("Example 3: Statistics and Monitoring")
    print("=" * 80)

    tower = GlobalWatchTower.initialize(
        num_port_admins=2,
        towers_per_port=3,
        gates_per_tower=2,
    )

    # Get initial stats
    stats = tower.get_stats()
    print("📊 Initial Statistics:")
    print(f"   - Port Admins: {stats['num_admins']}")
    print(f"   - Watch Towers: {stats['num_towers']}")
    print(f"   - Gate Guardians: {stats['num_gates']}")
    print(f"   - Total Verifications: {stats['total_verifications']}")
    print(f"   - Total Incidents: {stats['total_incidents']}")
    print(f"   - Total Lockdowns: {stats['total_lockdowns']}")

    # Verify multiple files
    print("\n🔍 Verifying multiple files...")
    for i in range(5):
        with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(f"# Test file {i}\nprint('Test {i}')\n")
            test_file = Path(f.name)

        tower.verify_file(test_file)
        test_file.unlink()
        print(f"   - File {i+1} verified")

    # Get updated stats
    stats = tower.get_stats()
    print("\n📊 Updated Statistics:")
    print(f"   - Total Verifications: {stats['total_verifications']}")
    print(f"   - Total Quarantined: {stats['total_quarantined']}")
    print(f"   - Cerberus Incidents: {stats['cerberus_incidents']}")

    GlobalWatchTower.reset()
    print("\n" + "=" * 80 + "\n")


def example_emergency_lockdown():
    """Example 4: Emergency lockdown procedure."""
    print("=" * 80)
    print("Example 4: Emergency Lockdown")
    print("=" * 80)

    tower = GlobalWatchTower.initialize()

    print("🚨 Initiating emergency lockdown...")
    tower.activate_emergency_lockdown("Critical security threat detected")

    # Check that all gates have force fields active
    active_force_fields = sum(
        1 for gate in tower.gate_guardians if gate.force_field_active
    )

    print(f"   - Gates with active force fields: {active_force_fields}/{len(tower.gate_guardians)}")

    stats = tower.get_stats()
    print(f"   - Total lockdowns: {stats['total_lockdowns']}")

    GlobalWatchTower.reset()
    print("\n" + "=" * 80 + "\n")


def example_convenience_functions():
    """Example 5: Using convenience functions."""
    print("=" * 80)
    print("Example 5: Convenience Functions")
    print("=" * 80)

    # Initialize first
    GlobalWatchTower.initialize()

    # Create a test file
    with NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write("# Simple test\nprint('Hello')\n")
        test_file = Path(f.name)

    print("🔍 Using verify_file_globally() convenience function")
    result = verify_file_globally(test_file)
    print(f"   - Verdict: {result['verdict']}")

    print("\n🔍 Using get_global_watch_tower() convenience function")
    tower = get_global_watch_tower()
    stats = tower.get_stats()
    print(f"   - Total verifications: {stats['total_verifications']}")

    # Cleanup
    test_file.unlink()
    GlobalWatchTower.reset()
    print("\n" + "=" * 80 + "\n")


def example_accessing_specific_components():
    """Example 6: Accessing specific towers and gates."""
    print("=" * 80)
    print("Example 6: Accessing Specific Components")
    print("=" * 80)

    tower = GlobalWatchTower.initialize(
        num_port_admins=1,
        towers_per_port=3,
        gates_per_tower=2,
    )

    # Access a specific watch tower
    print("🏰 Accessing specific watch tower:")
    watch_tower = tower.get_tower_by_id("wt-0-1")
    if watch_tower:
        print(f"   - Tower ID: {watch_tower.tower_id}")
        print(f"   - Reports received: {len(watch_tower.reports)}")
    else:
        print("   - Tower not found")

    # Access a specific gate guardian
    print("\n🚪 Accessing specific gate guardian:")
    gate = tower.get_gate_by_id("gate-0-1-0")
    if gate:
        print(f"   - Gate ID: {gate.gate_id}")
        print(f"   - Force field active: {gate.force_field_active}")
        print(f"   - Quarantined items: {len(gate.quarantine)}")
    else:
        print("   - Gate not found")

    GlobalWatchTower.reset()
    print("\n" + "=" * 80 + "\n")


def main():
    """Run all examples."""
    print("\n" + "🏰 Global Watch Tower System - Examples 🏰".center(80))
    print()

    try:
        example_basic_initialization()
        example_quarantine_workflow()
        example_statistics_and_monitoring()
        example_emergency_lockdown()
        example_convenience_functions()
        example_accessing_specific_components()

        print("✅ All examples completed successfully!")
        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
