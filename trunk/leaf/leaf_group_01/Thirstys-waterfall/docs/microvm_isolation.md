<!-- # ============================================================================ # -->
<!-- # STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59 # -->
<!-- # COMPLIANCE: Sovereign Substrate / microvm_isolation.md # -->
<!-- # ============================================================================ # -->
<!-- # ============================================================================ #


<!-- # COMPLIANCE: Sovereign Substrate / microvm_isolation.md # -->
<!-- # ============================================================================ #

<!-- # Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master -->
<div align="right">
  <img src="https://img.shields.io/badge/DATE-2026-03-18-blueviolet?style=for-the-badge" alt="Date" />
  <img src="https://img.shields.io/badge/PRODUCTIVITY-ACTIVE-success?style=for-the-badge" alt="Productivity" />
</div>

# MicroVM Isolation Module

Production-grade MicroVM isolation for browser tabs, extensions, and sessions using Firecracker and QEMU.

## Overview

The MicroVM Isolation Module provides hardware-level process isolation for security-critical browser components. Each browser tab, extension, or session can run in its own isolated MicroVM with dedicated resources and network segmentation.

## Features

### Core Capabilities

- **Hard Process Separation**: Complete isolation at the VM level
- **Micro-Segmentation**: Network-isolated VMs with optional connectivity
- **Resource Management**: Per-VM CPU, memory, disk, and network limits
- **Multiple Backends**: Support for Firecracker, QEMU, and Cloud Hypervisor
- **Lifecycle Management**: Create, start, stop, pause, resume, destroy operations
- **Health Monitoring**: Continuous health checks and metrics tracking
- **Secure Communication**: Unix domain sockets for host-VM IPC
- **Thread-Safe**: All operations protected with proper locking

### Isolation Types

- **Browser Tab**: Isolate individual browser tabs
- **Extension**: Isolate browser extensions
- **Session**: Isolate browsing sessions
- **Plugin**: Isolate plugins and third-party components

### VM Backends

- **Firecracker**: AWS's lightweight virtualization technology
- **QEMU**: Full-featured virtualization with microvm machine type
- **Cloud Hypervisor**: Rust-based VMM optimized for cloud workloads

## Usage

### Basic Example

```python
from thirstys_waterfall.security.microvm_isolation import (
    MicroVMIsolationManager,
    IsolationType,
    VMResourceLimits,
    VMNetworkConfig,
    VMBackend
)

# Initialize manager

config = {
    "max_vcpus": 16,
    "max_memory_mb": 8192,
    "default_backend": "QEMU"
}
manager = MicroVMIsolationManager(config)
manager.start()

# Create isolated VM for browser tab

vm_id = manager.create_vm(
    isolation_type=IsolationType.BROWSER_TAB,
    resource_limits=VMResourceLimits(
        vcpu_count=2,
        memory_mb=1024,
        disk_size_mb=2048
    ),
    network_config=VMNetworkConfig(
        isolated_network=True
    )
)

# Start the VM

vm = manager.get_vm(vm_id)
vm.start()

# Send command to VM

response = vm.send_command("execute", {"action": "render_page"})

# Get VM status

info = vm.get_info()
print(f"VM State: {info['state']}")
print(f"Resources: {info['resource_limits']}")

# Cleanup

vm.stop()
manager.destroy_vm(vm_id)
manager.stop()
```

### Advanced Example

```python

# Create VM with custom configuration

vm_id = manager.create_vm(
    isolation_type=IsolationType.EXTENSION,
    resource_limits=VMResourceLimits(
        vcpu_count=1,
        memory_mb=512,
        disk_size_mb=1024,
        network_bandwidth_mbps=100,
        max_file_handles=1024,
        max_processes=128
    ),
    backend=VMBackend.FIRECRACKER,
    network_config=VMNetworkConfig(
        tap_device="tap0",
        ip_address="192.168.100.10",
        gateway="192.168.100.1",
        dns_servers=["8.8.8.8", "8.8.4.4"],
        isolated_network=False
    ),
    kernel_path="/path/to/custom/kernel",
    rootfs_path="/path/to/custom/rootfs.ext4"
)
```

### Resource Management

```python

# Check resource usage

usage = manager.get_resource_usage()
print(f"Total VMs: {usage['total_vms']}")
print(f"vCPUs allocated: {usage['vcpus_allocated']}/{usage['vcpus_available']}")
print(f"Memory allocated: {usage['memory_allocated_mb']} MB")
print(f"VMs by type: {usage['vms_by_type']}")
print(f"VMs by state: {usage['vms_by_state']}")
```

### Health Monitoring

```python

# Get health status

health = manager.get_health_status()
print(f"Healthy VMs: {health['healthy_vms']}")
print(f"Unhealthy VMs: {health['unhealthy_vms']}")

# Get VM-specific health metrics

vm = manager.get_vm(vm_id)
metrics = vm.get_health_metrics()
print(f"CPU Usage: {metrics.cpu_usage_percent}%")
print(f"Memory Usage: {metrics.memory_usage_mb} MB")
print(f"Uptime: {metrics.uptime_seconds}s")
print(f"Status: {metrics.health_status}")
```

### Communication Channel

```python
from thirstys_waterfall.security.microvm_isolation import CommunicationChannel

# Create communication channel

channel = CommunicationChannel(vm_id)
channel.connect()

# Send message

channel.send_message({
    "type": "command",
    "action": "process_request",
    "data": {"url": "https://example.com"}
})

# Receive response

response = channel.receive_message(timeout=5.0)
print(f"Response: {response}")

channel.close()
```

## Configuration

### Manager Configuration

```python
config = {

    # Resource limits

    "max_vcpus": 16,              # Maximum vCPUs across all VMs
    "max_memory_mb": 8192,        # Maximum memory across all VMs (MB)

    # Defaults for new VMs

    "default_vcpu_count": 1,      # Default vCPUs per VM
    "default_memory_mb": 512,     # Default memory per VM (MB)
    "default_disk_size_mb": 1024, # Default disk size per VM (MB)
    "default_backend": "QEMU"     # Default VM backend
}
```

### Resource Limits

```python
limits = VMResourceLimits(
    vcpu_count=2,                  # Number of vCPUs
    memory_mb=1024,                # Memory in MB
    disk_size_mb=2048,            # Disk size in MB
    network_bandwidth_mbps=100,    # Network bandwidth limit
    max_file_handles=1024,         # Max open file handles
    max_processes=128              # Max processes in VM
)
```

### Network Configuration

```python
network = VMNetworkConfig(
    tap_device="tap0",                     # TAP device name
    ip_address="192.168.100.10",          # VM IP address
    mac_address="52:54:00:12:34:56",      # VM MAC address
    gateway="192.168.100.1",              # Gateway IP
    dns_servers=["8.8.8.8", "8.8.4.4"],  # DNS servers
    isolated_network=False                 # Enable network isolation
)
```

## Architecture

### Components

1. **MicroVMIsolationManager**: Central manager for all MicroVM instances
   - Resource tracking and allocation
   - VM lifecycle management
   - Background cleanup of dead VMs
   - Thread-safe operations

2. **MicroVMInstance**: Individual MicroVM instance
   - VM process management
   - State machine (Created → Starting → Running → Stopping → Stopped)
   - Health monitoring
   - Communication channel

3. **CommunicationChannel**: Secure IPC between host and VM
   - Unix domain socket-based
   - JSON message protocol
   - Bidirectional communication

### VM Lifecycle

```
CREATED → STARTING → RUNNING ⟷ PAUSED
                        ↓
                    STOPPING
                        ↓
                     STOPPED → DESTROYED
                        ↓
                      ERROR
```

### Security Features

- **Process Isolation**: Each VM runs as a separate process with its own memory space
- **Network Segmentation**: VMs can be completely isolated from network or given controlled access
- **Resource Limits**: Hard limits on CPU, memory, disk, and network prevent resource exhaustion
- **Secure Communication**: All host-VM communication through encrypted channels
- **Health Monitoring**: Continuous monitoring detects and handles VM failures

## Requirements

### System Requirements

- Linux kernel 4.14+ (for KVM support)
- x86_64 architecture
- KVM virtualization enabled
- Python 3.8+

### Optional Requirements

- Firecracker binary (for Firecracker backend)
- QEMU 4.2+ (for QEMU backend)
- Cloud Hypervisor (for Cloud Hypervisor backend)

### Python Dependencies

- Standard library only (no external dependencies)

## Performance

### Resource Overhead

- **Memory**: ~50-100MB base per VM + workload memory
- **CPU**: Minimal overhead (<5%) when VM is idle
- **Startup Time**:
  - Firecracker: ~125ms
  - QEMU microvm: ~150ms
  - Cloud Hypervisor: ~100ms

### Scaling

- Tested with 100+ concurrent VMs per host
- Resource limits enforced to prevent overcommitment
- Automatic cleanup of dead VMs reduces memory leaks

## Testing

Run the test suite:
```bash
python3 -m unittest tests.test_microvm_isolation -v
```

Run the demo:
```bash
python3 examples/microvm_isolation_demo.py
```

## Troubleshooting

### VM fails to start

- Check if KVM is enabled: `lsmod | grep kvm`
- Verify backend binary exists: `which firecracker` or `which qemu-system-x86_64`
- Check kernel and rootfs paths are correct
- Review logs for specific error messages

### Communication channel connection fails

- Ensure socket path is accessible
- Check VM has started successfully
- Verify firewall rules allow local socket communication

### Resource exhaustion

- Check resource usage: `manager.get_resource_usage()`
- Increase manager limits in configuration
- Clean up unused VMs: `manager.destroy_all_vms()`

## License

See repository LICENSE file.

## Contributing

Contributions welcome! Please ensure:

- All tests pass
- Code follows existing style
- Add tests for new features
- Update documentation
