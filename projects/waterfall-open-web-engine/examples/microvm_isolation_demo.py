# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / microvm_isolation_demo.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / microvm_isolation_demo.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
#!/usr/bin/env python3
"""
MicroVM Isolation Module Demo
Demonstrates the key features of the MicroVM isolation system
"""

import logging
from thirstys_waterfall.security.microvm_isolation import (
    MicroVMIsolationManager,
    IsolationType,
    VMResourceLimits,
    VMNetworkConfig,
    VMBackend,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    print("=" * 60)
    print("MicroVM Isolation Module Demo")
    print("=" * 60)
    print()

    # Initialize manager
    print("1. Initializing MicroVM Isolation Manager...")
    config = {
        "max_vcpus": 16,
        "max_memory_mb": 8192,
        "default_vcpu_count": 1,
        "default_memory_mb": 512,
        "default_backend": "QEMU",
    }
    manager = MicroVMIsolationManager(config)
    manager.start()
    print(
        f"   ✓ Manager initialized (max vCPUs: {config['max_vcpus']}, max memory: {config['max_memory_mb']}MB)"
    )
    print()

    # Create VMs for different isolation types
    print("2. Creating MicroVM instances...")

    # Browser tab VM
    tab_vm_id = manager.create_vm(
        isolation_type=IsolationType.BROWSER_TAB,
        resource_limits=VMResourceLimits(vcpu_count=1, memory_mb=512),
        network_config=VMNetworkConfig(isolated_network=True),
    )
    print(f"   ✓ Browser Tab VM created: {tab_vm_id}")

    # Extension VM
    ext_vm_id = manager.create_vm(
        isolation_type=IsolationType.EXTENSION,
        resource_limits=VMResourceLimits(vcpu_count=1, memory_mb=256),
        network_config=VMNetworkConfig(isolated_network=True),
    )
    print(f"   ✓ Extension VM created: {ext_vm_id}")

    # Session VM with more resources
    session_vm_id = manager.create_vm(
        isolation_type=IsolationType.SESSION,
        resource_limits=VMResourceLimits(vcpu_count=2, memory_mb=1024),
        backend=VMBackend.FIRECRACKER,
    )
    print(f"   ✓ Session VM created: {session_vm_id}")
    print()

    # Show resource usage
    print("3. Resource Usage:")
    usage = manager.get_resource_usage()
    print(f"   Total VMs: {usage['total_vms']}")
    print(f"   vCPUs allocated: {usage['vcpus_allocated']}/{config['max_vcpus']}")
    print(
        f"   Memory allocated: {usage['memory_allocated_mb']}/{config['max_memory_mb']} MB"
    )
    print(f"   VMs by type: {usage['vms_by_type']}")
    print()

    # Get VM info
    print("4. VM Information:")
    for vm_id in [tab_vm_id, ext_vm_id, session_vm_id]:
        info = manager.get_vm_info(vm_id)
        print(f"\n   VM: {info['vm_id']}")
        print(f"   - Type: {info['isolation_type']}")
        print(f"   - Backend: {info['backend']}")
        print(f"   - State: {info['state']}")
        print(
            f"   - Resources: {info['resource_limits']['vcpu_count']} vCPU, {info['resource_limits']['memory_mb']} MB"
        )
        print(
            f"   - Network: {'Isolated' if info['network_config']['isolated'] else 'Connected'}"
        )
    print()

    # Health status
    print("5. Health Status:")
    health = manager.get_health_status()
    print(f"   Total VMs: {health['total_vms']}")
    print(f"   Healthy VMs: {health['healthy_vms']}")
    print(f"   Unhealthy VMs: {health['unhealthy_vms']}")
    print()

    # List VMs by type
    print("6. VMs by Isolation Type:")
    print(
        f"   Browser Tabs: {len(manager.list_vms(isolation_type=IsolationType.BROWSER_TAB))}"
    )
    print(
        f"   Extensions: {len(manager.list_vms(isolation_type=IsolationType.EXTENSION))}"
    )
    print(f"   Sessions: {len(manager.list_vms(isolation_type=IsolationType.SESSION))}")
    print()

    # Cleanup
    print("7. Cleaning up...")
    manager.destroy_vm(tab_vm_id)
    print(f"   ✓ Destroyed {tab_vm_id}")

    manager.destroy_vm(ext_vm_id)
    print(f"   ✓ Destroyed {ext_vm_id}")

    manager.destroy_vm(session_vm_id)
    print(f"   ✓ Destroyed {session_vm_id}")

    manager.stop()
    print("   ✓ Manager stopped")
    print()

    print("=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    print()
    print("Key Features Demonstrated:")
    print("  ✓ Multiple isolation types (browser tab, extension, session)")
    print("  ✓ Resource management (CPU, memory limits)")
    print("  ✓ Multiple VM backends (QEMU, Firecracker)")
    print("  ✓ Network isolation")
    print("  ✓ Health monitoring")
    print("  ✓ Resource tracking")
    print("  ✓ Complete lifecycle management")


if __name__ == "__main__":
    main()
