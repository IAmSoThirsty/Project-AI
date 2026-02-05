"""
MicroVM Isolation Module
Provides hardware-level process isolation using Firecracker/QEMU-based MicroVMs
for browser tabs, extensions, and sessions with hard process separation.
"""

import logging
import os
import socket
import subprocess
import threading
import time
import json
import secrets
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass, field
import tempfile


class VMBackend(Enum):
    """Supported MicroVM backend types"""
    FIRECRACKER = "firecracker"
    QEMU = "qemu"
    CLOUD_HYPERVISOR = "cloud-hypervisor"


class VMState(Enum):
    """MicroVM lifecycle states"""
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"
    DESTROYED = "destroyed"


class IsolationType(Enum):
    """Type of workload being isolated"""
    BROWSER_TAB = "browser_tab"
    EXTENSION = "extension"
    SESSION = "session"
    PLUGIN = "plugin"


@dataclass
class VMResourceLimits:
    """Resource limits for a MicroVM"""
    vcpu_count: int = 1
    memory_mb: int = 512
    disk_size_mb: int = 1024
    network_bandwidth_mbps: int = 100
    max_file_handles: int = 1024
    max_processes: int = 128


@dataclass
class VMNetworkConfig:
    """Network configuration for a MicroVM"""
    tap_device: Optional[str] = None
    ip_address: Optional[str] = None
    mac_address: Optional[str] = None
    gateway: Optional[str] = None
    dns_servers: List[str] = field(default_factory=list)
    isolated_network: bool = True


@dataclass
class VMHealthMetrics:
    """Health monitoring metrics for a MicroVM"""
    cpu_usage_percent: float = 0.0
    memory_usage_mb: int = 0
    disk_io_bytes: int = 0
    network_rx_bytes: int = 0
    network_tx_bytes: int = 0
    uptime_seconds: float = 0.0
    last_health_check: float = 0.0
    health_status: str = "unknown"


class CommunicationChannel:
    """
    Secure communication channel between host and MicroVM.
    Uses Unix domain sockets or virtio-vsock for IPC.
    """

    def __init__(self, vm_id: str, socket_path: Optional[str] = None):
        self.logger = logging.getLogger(__name__)
        self.vm_id = vm_id
        self.socket_path = socket_path or f"/tmp/thirstys_vm_{vm_id}.sock"
        self._socket: Optional[socket.socket] = None
        self._connected = False
        self._lock = threading.Lock()

    def connect(self, timeout: float = 5.0) -> bool:
        """Establish connection to MicroVM"""
        with self._lock:
            try:
                if os.path.exists(self.socket_path):
                    self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                    self._socket.settimeout(timeout)
                    self._socket.connect(self.socket_path)
                    self._connected = True
                    self.logger.info(f"Connected to VM {self.vm_id} via {self.socket_path}")
                    return True
            except Exception as e:
                self.logger.error(f"Failed to connect to VM {self.vm_id}: {e}")

            return False

    def send_message(self, message: Dict[str, Any]) -> bool:
        """Send message to MicroVM"""
        with self._lock:
            if not self._connected or not self._socket:
                return False

            try:
                data = json.dumps(message).encode('utf-8')
                length = len(data).to_bytes(4, byteorder='big')
                self._socket.sendall(length + data)
                return True
            except Exception as e:
                self.logger.error(f"Failed to send message to VM {self.vm_id}: {e}")
                return False

    def receive_message(self, timeout: float = 1.0) -> Optional[Dict[str, Any]]:
        """Receive message from MicroVM"""
        with self._lock:
            if not self._connected or not self._socket:
                return None

            try:
                self._socket.settimeout(timeout)

                # Read message length
                length_bytes = self._socket.recv(4)
                if not length_bytes:
                    return None

                message_length = int.from_bytes(length_bytes, byteorder='big')

                # Read message data
                data = b""
                while len(data) < message_length:
                    chunk = self._socket.recv(min(4096, message_length - len(data)))
                    if not chunk:
                        break
                    data += chunk

                return json.loads(data.decode('utf-8'))

            except socket.timeout:
                return None
            except Exception as e:
                self.logger.error(f"Failed to receive message from VM {self.vm_id}: {e}")
                return None

    def close(self):
        """Close communication channel"""
        with self._lock:
            if self._socket:
                try:
                    self._socket.close()
                except Exception:
                    pass
                self._socket = None
            self._connected = False

            if os.path.exists(self.socket_path):
                try:
                    os.unlink(self.socket_path)
                except Exception:
                    pass


class MicroVMInstance:
    """
    Represents an isolated MicroVM instance for browser tab/extension/session.
    Provides hard process separation and micro-segmentation.
    """

    def __init__(
        self,
        vm_id: str,
        backend: VMBackend,
        isolation_type: IsolationType,
        resource_limits: VMResourceLimits,
        network_config: Optional[VMNetworkConfig] = None,
        kernel_path: Optional[str] = None,
        rootfs_path: Optional[str] = None
    ):
        self.logger = logging.getLogger(__name__)

        # VM identification
        self.vm_id = vm_id
        self.backend = backend
        self.isolation_type = isolation_type

        # Configuration
        self.resource_limits = resource_limits
        self.network_config = network_config or VMNetworkConfig()
        self.kernel_path = kernel_path or self._get_default_kernel_path()
        self.rootfs_path = rootfs_path or self._get_default_rootfs_path()

        # Runtime state
        self._state = VMState.CREATED
        self._process: Optional[subprocess.Popen] = None
        self._pid: Optional[int] = None
        self._start_time: Optional[float] = None

        # Communication
        self._channel = CommunicationChannel(vm_id)

        # Monitoring
        self._health_metrics = VMHealthMetrics()
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitoring_active = False

        # Thread safety
        self._lock = threading.Lock()

        # Firecracker/QEMU specific
        self._config_file: Optional[str] = None
        self._socket_path = f"/tmp/thirstys_vm_{vm_id}.socket"

    def _get_default_kernel_path(self) -> str:
        """Get default kernel path for MicroVM"""
        # In production: Point to actual microvm kernel
        return "/var/lib/thirstys/kernels/vmlinux-microvm"

    def _get_default_rootfs_path(self) -> str:
        """Get default rootfs path for MicroVM"""
        # In production: Point to actual minimal rootfs image
        return "/var/lib/thirstys/images/rootfs.ext4"

    def start(self) -> bool:
        """Start the MicroVM instance"""
        with self._lock:
            if self._state == VMState.RUNNING:
                self.logger.warning(f"VM {self.vm_id} already running")
                return True

            if self._state not in [VMState.CREATED, VMState.STOPPED]:
                self.logger.error(f"Cannot start VM {self.vm_id} in state {self._state.value}")
                return False

            self.logger.info(f"Starting MicroVM {self.vm_id} with backend {self.backend.value}")
            self._state = VMState.STARTING

            try:
                # Create configuration
                if not self._create_vm_config():
                    self._state = VMState.ERROR
                    return False

                # Setup networking
                if not self._setup_networking():
                    self.logger.warning(f"Network setup failed for VM {self.vm_id}")

                # Launch VM process
                if not self._launch_vm_process():
                    self._state = VMState.ERROR
                    return False

                # Wait for VM to become ready
                if not self._wait_for_ready(timeout=30.0):
                    self.logger.error(f"VM {self.vm_id} did not become ready")
                    self.stop()
                    self._state = VMState.ERROR
                    return False

                self._state = VMState.RUNNING
                self._start_time = time.time()

                # Start health monitoring
                self._start_monitoring()

                self.logger.info(f"MicroVM {self.vm_id} started successfully (PID: {self._pid})")
                return True

            except Exception as e:
                self.logger.error(f"Failed to start VM {self.vm_id}: {e}")
                self._state = VMState.ERROR
                return False

    def _create_vm_config(self) -> bool:
        """Create VM configuration file"""
        try:
            if self.backend == VMBackend.FIRECRACKER:
                config = self._create_firecracker_config()
            elif self.backend == VMBackend.QEMU:
                config = self._create_qemu_config()
            else:
                self.logger.error(f"Unsupported backend: {self.backend.value}")
                return False

            # Write config to temporary file
            fd, self._config_file = tempfile.mkstemp(
                prefix=f"thirstys_vm_{self.vm_id}_",
                suffix=".json"
            )

            with os.fdopen(fd, 'w') as f:
                json.dump(config, f, indent=2)

            self.logger.debug(f"Created config file: {self._config_file}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create VM config: {e}")
            return False

    def _create_firecracker_config(self) -> Dict[str, Any]:
        """Create Firecracker configuration"""
        return {
            "boot-source": {
                "kernel_image_path": self.kernel_path,
                "boot_args": "console=ttyS0 reboot=k panic=1 pci=off"
            },
            "drives": [
                {
                    "drive_id": "rootfs",
                    "path_on_host": self.rootfs_path,
                    "is_root_device": True,
                    "is_read_only": False
                }
            ],
            "machine-config": {
                "vcpu_count": self.resource_limits.vcpu_count,
                "mem_size_mib": self.resource_limits.memory_mb,
                "ht_enabled": False
            },
            "network-interfaces": [
                {
                    "iface_id": "eth0",
                    "guest_mac": self.network_config.mac_address or self._generate_mac_address(),
                    "host_dev_name": self.network_config.tap_device or f"tap_{self.vm_id[:8]}"
                }
            ] if not self.network_config.isolated_network else []
        }

    def _create_qemu_config(self) -> Dict[str, Any]:
        """Create QEMU configuration"""
        return {
            "machine": "microvm",
            "cpu": f"host,cores={self.resource_limits.vcpu_count}",
            "memory": f"{self.resource_limits.memory_mb}M",
            "kernel": self.kernel_path,
            "drive": f"file={self.rootfs_path},format=raw,if=virtio",
            "append": "console=ttyS0 reboot=k panic=1",
            "serial": "stdio",
            "nodefaults": True,
            "no-user-config": True,
            "nographic": True
        }

    def _generate_mac_address(self) -> str:
        """Generate random MAC address"""
        mac = [0x52, 0x54, 0x00]  # QEMU OUI
        mac.extend([secrets.randbelow(256) for _ in range(3)])
        return ':'.join(f'{b:02x}' for b in mac)

    def _setup_networking(self) -> bool:
        """Setup networking for MicroVM"""
        try:
            if self.network_config.isolated_network:
                # No external network access
                self.logger.info(f"VM {self.vm_id} configured with isolated network")
                return True

            # Create TAP device
            tap_name = self.network_config.tap_device or f"tap_{self.vm_id[:8]}"

            # In production: Use proper network namespace and bridge setup
            # Commands would be:
            # ip tuntap add dev {tap_name} mode tap
            # ip link set {tap_name} up
            # ip link set {tap_name} master br0

            self.network_config.tap_device = tap_name
            self.logger.info(f"Network setup completed for VM {self.vm_id}")
            return True

        except Exception as e:
            self.logger.error(f"Network setup failed: {e}")
            return False

    def _launch_vm_process(self) -> bool:
        """Launch the VM process"""
        try:
            if self.backend == VMBackend.FIRECRACKER:
                cmd = self._build_firecracker_command()
            elif self.backend == VMBackend.QEMU:
                cmd = self._build_qemu_command()
            else:
                return False

            self.logger.debug(f"Launching VM with command: {' '.join(cmd)}")

            # Launch process
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )

            self._pid = self._process.pid
            self.logger.info(f"VM process launched with PID {self._pid}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to launch VM process: {e}")
            return False

    def _build_firecracker_command(self) -> List[str]:
        """Build Firecracker command line"""
        return [
            "firecracker",
            "--api-sock", self._socket_path,
            "--config-file", self._config_file,
        ]

    def _build_qemu_command(self) -> List[str]:
        """Build QEMU command line"""
        cmd = ["qemu-system-x86_64"]

        config = self._create_qemu_config()

        cmd.extend(["-machine", config["machine"]])
        cmd.extend(["-cpu", config["cpu"]])
        cmd.extend(["-m", config["memory"]])
        cmd.extend(["-kernel", config["kernel"]])
        cmd.extend(["-drive", config["drive"]])
        cmd.extend(["-append", config["append"]])
        cmd.extend(["-serial", config["serial"]])

        if config.get("nodefaults"):
            cmd.append("-nodefaults")
        if config.get("no-user-config"):
            cmd.append("-no-user-config")
        if config.get("nographic"):
            cmd.append("-nographic")

        # Add monitoring socket
        cmd.extend(["-qmp", f"unix:{self._socket_path},server,nowait"])

        return cmd

    def _wait_for_ready(self, timeout: float = 30.0) -> bool:
        """Wait for VM to become ready"""
        start_time = time.time()

        while time.time() - start_time < timeout:
            # Check if process is still running
            if self._process and self._process.poll() is not None:
                self.logger.error("VM process exited prematurely")
                return False

            # Try to connect via communication channel
            if self._channel.connect(timeout=1.0):
                # Send ping message
                if self._channel.send_message({"type": "ping"}):
                    response = self._channel.receive_message(timeout=1.0)
                    if response and response.get("type") == "pong":
                        return True

            time.sleep(0.5)

        return False

    def stop(self) -> bool:
        """Stop the MicroVM instance"""
        with self._lock:
            if self._state not in [VMState.RUNNING, VMState.PAUSED, VMState.ERROR]:
                self.logger.warning(f"VM {self.vm_id} not running")
                return True

            self.logger.info(f"Stopping MicroVM {self.vm_id}")
            self._state = VMState.STOPPING

            try:
                # Stop monitoring
                self._stop_monitoring()

                # Close communication channel
                self._channel.close()

                # Gracefully shutdown VM
                if self._process:
                    try:
                        # Send shutdown signal
                        self._process.terminate()

                        # Wait for graceful shutdown
                        try:
                            self._process.wait(timeout=10.0)
                        except subprocess.TimeoutExpired:
                            # Force kill if not responding
                            self.logger.warning(f"VM {self.vm_id} not responding, forcing shutdown")
                            self._process.kill()
                            self._process.wait()

                    except Exception as e:
                        self.logger.error(f"Error stopping VM process: {e}")

                # Cleanup networking
                self._cleanup_networking()

                # Cleanup config file
                if self._config_file and os.path.exists(self._config_file):
                    os.unlink(self._config_file)

                self._state = VMState.STOPPED
                self._process = None
                self._pid = None

                self.logger.info(f"MicroVM {self.vm_id} stopped successfully")
                return True

            except Exception as e:
                self.logger.error(f"Failed to stop VM {self.vm_id}: {e}")
                self._state = VMState.ERROR
                return False

    def pause(self) -> bool:
        """Pause the MicroVM instance"""
        with self._lock:
            if self._state != VMState.RUNNING:
                return False

            self.logger.info(f"Pausing MicroVM {self.vm_id}")

            # In production: Send pause command via QMP/Firecracker API
            self._state = VMState.PAUSED
            return True

    def resume(self) -> bool:
        """Resume the MicroVM instance"""
        with self._lock:
            if self._state != VMState.PAUSED:
                return False

            self.logger.info(f"Resuming MicroVM {self.vm_id}")

            # In production: Send resume command via QMP/Firecracker API
            self._state = VMState.RUNNING
            return True

    def _cleanup_networking(self):
        """Cleanup networking resources"""
        try:
            if self.network_config.tap_device:
                # In production: Remove TAP device
                # ip link delete {self.network_config.tap_device}
                self.logger.debug(f"Cleaned up network for VM {self.vm_id}")
        except Exception as e:
            self.logger.error(f"Network cleanup failed: {e}")

    def _start_monitoring(self):
        """Start health monitoring thread"""
        if self._monitoring_active:
            return

        self._monitoring_active = True
        self._monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self._monitor_thread.start()

    def _stop_monitoring(self):
        """Stop health monitoring thread"""
        self._monitoring_active = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)

    def _monitoring_loop(self):
        """Health monitoring loop"""
        while self._monitoring_active:
            try:
                self._update_health_metrics()
                self._check_health()
                time.sleep(5.0)
            except Exception as e:
                self.logger.error(f"Monitoring error for VM {self.vm_id}: {e}")

    def _update_health_metrics(self):
        """Update health metrics"""
        try:
            if not self._process or not self._pid:
                return

            # In production: Read from /proc/{pid}/* or use psutil
            # For now, simulate basic metrics

            self._health_metrics.uptime_seconds = (
                time.time() - self._start_time if self._start_time else 0.0
            )
            self._health_metrics.last_health_check = time.time()

            # Check if process is alive
            if self._process.poll() is not None:
                self._health_metrics.health_status = "dead"
                self._state = VMState.ERROR
            else:
                self._health_metrics.health_status = "healthy"

        except Exception as e:
            self.logger.error(f"Failed to update health metrics: {e}")

    def _check_health(self):
        """Perform health check"""
        if self._health_metrics.health_status == "dead":
            self.logger.error(f"VM {self.vm_id} health check failed - process dead")
            with self._lock:
                self._state = VMState.ERROR

    def get_state(self) -> VMState:
        """Get current VM state"""
        return self._state

    def get_health_metrics(self) -> VMHealthMetrics:
        """Get health metrics"""
        return self._health_metrics

    def send_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Send command to MicroVM"""
        message = {
            "type": "command",
            "command": command,
            "params": params or {}
        }

        if self._channel.send_message(message):
            return self._channel.receive_message(timeout=5.0)

        return None

    def get_info(self) -> Dict[str, Any]:
        """Get VM information"""
        return {
            "vm_id": self.vm_id,
            "backend": self.backend.value,
            "isolation_type": self.isolation_type.value,
            "state": self._state.value,
            "pid": self._pid,
            "resource_limits": {
                "vcpu_count": self.resource_limits.vcpu_count,
                "memory_mb": self.resource_limits.memory_mb,
                "disk_size_mb": self.resource_limits.disk_size_mb
            },
            "network_config": {
                "isolated": self.network_config.isolated_network,
                "tap_device": self.network_config.tap_device,
                "ip_address": self.network_config.ip_address
            },
            "health_metrics": {
                "status": self._health_metrics.health_status,
                "uptime_seconds": self._health_metrics.uptime_seconds,
                "cpu_usage": self._health_metrics.cpu_usage_percent,
                "memory_usage_mb": self._health_metrics.memory_usage_mb
            }
        }


class MicroVMIsolationManager:
    """
    Manager for MicroVM-based isolation.
    Handles lifecycle of multiple MicroVM instances for browser tabs, extensions, and sessions.
    Provides resource management and monitoring across all VMs.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

        # VM instances
        self._vms: Dict[str, MicroVMInstance] = {}

        # Resource tracking
        self._total_vcpus_allocated = 0
        self._total_memory_allocated = 0
        self._max_vcpus = self.config.get("max_vcpus", 16)
        self._max_memory_mb = self.config.get("max_memory_mb", 8192)

        # Default settings
        self._default_backend = VMBackend[
            self.config.get("default_backend", "FIRECRACKER").upper()
        ]
        self._default_resources = VMResourceLimits(
            vcpu_count=self.config.get("default_vcpu_count", 1),
            memory_mb=self.config.get("default_memory_mb", 512),
            disk_size_mb=self.config.get("default_disk_size_mb", 1024)
        )

        # Thread safety
        self._lock = threading.Lock()

        # Background tasks
        self._cleanup_thread: Optional[threading.Thread] = None
        self._cleanup_active = False

    def start(self):
        """Start the isolation manager"""
        self.logger.info("Starting MicroVM Isolation Manager")

        # Start cleanup thread
        self._cleanup_active = True
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_loop,
            daemon=True
        )
        self._cleanup_thread.start()

        self.logger.info(
            f"MicroVM Isolation Manager started "
            f"(backend: {self._default_backend.value}, "
            f"max_vcpus: {self._max_vcpus}, "
            f"max_memory: {self._max_memory_mb}MB)"
        )

    def stop(self):
        """Stop the isolation manager and all VMs"""
        self.logger.info("Stopping MicroVM Isolation Manager")

        # Stop cleanup thread
        self._cleanup_active = False
        if self._cleanup_thread:
            self._cleanup_thread.join(timeout=5.0)

        # Stop all VMs
        self.destroy_all_vms()

        self.logger.info("MicroVM Isolation Manager stopped")

    def create_vm(
        self,
        isolation_type: IsolationType,
        resource_limits: Optional[VMResourceLimits] = None,
        backend: Optional[VMBackend] = None,
        network_config: Optional[VMNetworkConfig] = None,
        vm_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a new MicroVM instance.

        Args:
            isolation_type: Type of workload to isolate
            resource_limits: Resource constraints
            backend: VM backend (defaults to configured backend)
            network_config: Network configuration
            vm_id: Optional VM identifier

        Returns:
            VM ID if successful, None otherwise
        """
        with self._lock:
            # Generate VM ID
            if not vm_id:
                vm_id = self._generate_vm_id(isolation_type)

            if vm_id in self._vms:
                self.logger.error(f"VM {vm_id} already exists")
                return None

            # Use defaults if not specified
            backend = backend or self._default_backend
            resource_limits = resource_limits or self._default_resources

            # Check resource availability
            if not self._check_resource_availability(resource_limits):
                self.logger.error(f"Insufficient resources for VM {vm_id}")
                return None

            try:
                # Create VM instance
                vm = MicroVMInstance(
                    vm_id=vm_id,
                    backend=backend,
                    isolation_type=isolation_type,
                    resource_limits=resource_limits,
                    network_config=network_config
                )

                self._vms[vm_id] = vm

                # Update resource tracking
                self._total_vcpus_allocated += resource_limits.vcpu_count
                self._total_memory_allocated += resource_limits.memory_mb

                self.logger.info(
                    f"Created MicroVM {vm_id} "
                    f"(type: {isolation_type.value}, "
                    f"vcpus: {resource_limits.vcpu_count}, "
                    f"memory: {resource_limits.memory_mb}MB)"
                )

                return vm_id

            except Exception as e:
                self.logger.error(f"Failed to create VM: {e}")
                return None

    def _generate_vm_id(self, isolation_type: IsolationType) -> str:
        """Generate unique VM identifier"""
        timestamp = int(time.time() * 1000)
        random_suffix = secrets.token_hex(4)
        return f"{isolation_type.value}_{timestamp}_{random_suffix}"

    def _check_resource_availability(self, limits: VMResourceLimits) -> bool:
        """Check if resources are available for new VM"""
        if self._total_vcpus_allocated + limits.vcpu_count > self._max_vcpus:
            return False

        if self._total_memory_allocated + limits.memory_mb > self._max_memory_mb:
            return False

        return True

    def start_vm(self, vm_id: str) -> bool:
        """Start a MicroVM instance"""
        vm = self._vms.get(vm_id)
        if not vm:
            self.logger.error(f"VM {vm_id} not found")
            return False

        return vm.start()

    def stop_vm(self, vm_id: str) -> bool:
        """Stop a MicroVM instance"""
        vm = self._vms.get(vm_id)
        if not vm:
            self.logger.error(f"VM {vm_id} not found")
            return False

        return vm.stop()

    def pause_vm(self, vm_id: str) -> bool:
        """Pause a MicroVM instance"""
        vm = self._vms.get(vm_id)
        if not vm:
            return False

        return vm.pause()

    def resume_vm(self, vm_id: str) -> bool:
        """Resume a MicroVM instance"""
        vm = self._vms.get(vm_id)
        if not vm:
            return False

        return vm.resume()

    def destroy_vm(self, vm_id: str) -> bool:
        """Destroy a MicroVM instance"""
        with self._lock:
            vm = self._vms.get(vm_id)
            if not vm:
                self.logger.error(f"VM {vm_id} not found")
                return False

            # Stop VM if running
            if vm.get_state() in [VMState.RUNNING, VMState.PAUSED]:
                vm.stop()

            # Update resource tracking
            self._total_vcpus_allocated -= vm.resource_limits.vcpu_count
            self._total_memory_allocated -= vm.resource_limits.memory_mb

            # Remove from tracking
            del self._vms[vm_id]

            self.logger.info(f"Destroyed MicroVM {vm_id}")
            return True

    def destroy_all_vms(self):
        """Destroy all MicroVM instances"""
        with self._lock:
            vm_ids = list(self._vms.keys())

        for vm_id in vm_ids:
            self.destroy_vm(vm_id)

    def get_vm(self, vm_id: str) -> Optional[MicroVMInstance]:
        """Get MicroVM instance by ID"""
        return self._vms.get(vm_id)

    def list_vms(
        self,
        isolation_type: Optional[IsolationType] = None,
        state: Optional[VMState] = None
    ) -> List[str]:
        """
        List VM IDs matching criteria.

        Args:
            isolation_type: Filter by isolation type
            state: Filter by state

        Returns:
            List of matching VM IDs
        """
        vms = []

        for vm_id, vm in self._vms.items():
            if isolation_type and vm.isolation_type != isolation_type:
                continue

            if state and vm.get_state() != state:
                continue

            vms.append(vm_id)

        return vms

    def get_vm_info(self, vm_id: str) -> Optional[Dict[str, Any]]:
        """Get VM information"""
        vm = self._vms.get(vm_id)
        if not vm:
            return None

        return vm.get_info()

    def get_all_vms_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information for all VMs"""
        return {
            vm_id: vm.get_info()
            for vm_id, vm in self._vms.items()
        }

    def send_command_to_vm(
        self,
        vm_id: str,
        command: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Send command to specific VM"""
        vm = self._vms.get(vm_id)
        if not vm:
            return None

        return vm.send_command(command, params)

    def get_resource_usage(self) -> Dict[str, Any]:
        """Get aggregate resource usage"""
        return {
            "total_vms": len(self._vms),
            "vcpus_allocated": self._total_vcpus_allocated,
            "vcpus_available": self._max_vcpus - self._total_vcpus_allocated,
            "memory_allocated_mb": self._total_memory_allocated,
            "memory_available_mb": self._max_memory_mb - self._total_memory_allocated,
            "vms_by_type": self._count_vms_by_type(),
            "vms_by_state": self._count_vms_by_state()
        }

    def _count_vms_by_type(self) -> Dict[str, int]:
        """Count VMs by isolation type"""
        counts = {}
        for vm in self._vms.values():
            iso_type = vm.isolation_type.value
            counts[iso_type] = counts.get(iso_type, 0) + 1
        return counts

    def _count_vms_by_state(self) -> Dict[str, int]:
        """Count VMs by state"""
        counts = {}
        for vm in self._vms.values():
            state = vm.get_state().value
            counts[state] = counts.get(state, 0) + 1
        return counts

    def _cleanup_loop(self):
        """Background cleanup of dead VMs"""
        while self._cleanup_active:
            try:
                self._cleanup_dead_vms()
                time.sleep(30.0)
            except Exception as e:
                self.logger.error(f"Cleanup error: {e}")

    def _cleanup_dead_vms(self):
        """Remove VMs in error state"""
        with self._lock:
            dead_vms = [
                vm_id for vm_id, vm in self._vms.items()
                if vm.get_state() == VMState.ERROR
            ]

        for vm_id in dead_vms:
            self.logger.warning(f"Cleaning up dead VM {vm_id}")
            self.destroy_vm(vm_id)

    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        healthy_count = 0
        unhealthy_count = 0

        for vm in self._vms.values():
            metrics = vm.get_health_metrics()
            if metrics.health_status == "healthy":
                healthy_count += 1
            else:
                unhealthy_count += 1

        return {
            "total_vms": len(self._vms),
            "healthy_vms": healthy_count,
            "unhealthy_vms": unhealthy_count,
            "resource_usage": self.get_resource_usage()
        }
