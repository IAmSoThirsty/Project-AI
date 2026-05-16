"""
VPN Backend Implementations
Concrete wrappers for WireGuard, OpenVPN, and IKEv2 protocols
with platform-specific OS integration.
"""

import subprocess
import platform
import time
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod


class VPNBackend(ABC):
    """Abstract base class for VPN backend implementations"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connected = False
        self.platform = platform.system()  # 'Linux', 'Windows', 'Darwin'

    @abstractmethod
    def connect(self) -> bool:
        """Establish VPN connection"""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect VPN connection"""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get connection status"""
        pass

    @abstractmethod
    def check_availability(self) -> bool:
        """Check if backend is available on this platform"""
        pass


class WireGuardBackend(VPNBackend):
    """
    WireGuard VPN Backend
    Integrates with WireGuard kernel module or userspace implementation
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.interface_name = config.get("interface", "wg0")
        self.config_path = config.get("config_path", "/etc/wireguard/wg0.conf")

    def check_availability(self) -> bool:
        """Check if WireGuard is available on system"""
        try:
            if self.platform == "Linux":
                # Check for wg command
                result = subprocess.run(["which", "wg"], capture_output=True, timeout=5)
                return result.returncode == 0

            elif self.platform == "Windows":
                # Check for wireguard.exe
                result = subprocess.run(
                    ["where", "wireguard"], capture_output=True, timeout=5, shell=True
                )
                return result.returncode == 0

            elif self.platform == "Darwin":
                # Check for wg command on macOS
                result = subprocess.run(["which", "wg"], capture_output=True, timeout=5)
                return result.returncode == 0

        except Exception as e:
            self.logger.debug(f"WireGuard availability check failed: {e}")
            return False

        return False

    def connect(self) -> bool:
        """Establish WireGuard VPN connection"""
        try:
            if not self.check_availability():
                self.logger.warning("WireGuard not available on system")
                return False

            if self.platform == "Linux":
                return self._connect_linux()
            elif self.platform == "Windows":
                return self._connect_windows()
            elif self.platform == "Darwin":
                return self._connect_macos()
            else:
                self.logger.error(f"Unsupported platform: {self.platform}")
                return False

        except Exception as e:
            self.logger.error(f"WireGuard connection failed: {e}")
            return False

    def _connect_linux(self) -> bool:
        """Connect WireGuard on Linux using wg-quick"""
        try:
            # Use wg-quick to bring up interface
            # Note: Requires root/sudo privileges
            cmd = ["sudo", "wg-quick", "up", self.interface_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self.connected = True
                self.logger.info(f"WireGuard connected on Linux: {self.interface_name}")
                return True
            else:
                self.logger.error(f"wg-quick failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("WireGuard connection timeout")
            return False
        except FileNotFoundError:
            self.logger.error("wg-quick command not found")
            return False

    def _connect_windows(self) -> bool:
        """Connect WireGuard on Windows"""
        try:
            # Use WireGuard Windows service
            # Assumes WireGuard for Windows is installed
            cmd = ["wireguard", "/installtunnelservice", self.config_path]
            result = subprocess.run(cmd, capture_output=True, timeout=30, shell=True)

            if result.returncode == 0:
                self.connected = True
                self.logger.info("WireGuard connected on Windows")
                return True
            else:
                self.logger.error("WireGuard Windows connection failed")
                return False

        except Exception as e:
            self.logger.error(f"Windows connection error: {e}")
            return False

    def _connect_macos(self) -> bool:
        """Connect WireGuard on macOS"""
        try:
            # Use wg-quick on macOS (via Homebrew or official app)
            cmd = ["sudo", "wg-quick", "up", self.interface_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                self.connected = True
                self.logger.info(f"WireGuard connected on macOS: {self.interface_name}")
                return True
            else:
                self.logger.error(f"macOS wg-quick failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"macOS connection error: {e}")
            return False

    def disconnect(self) -> bool:
        """Disconnect WireGuard VPN"""
        try:
            if not self.connected:
                return True

            if self.platform == "Linux" or self.platform == "Darwin":
                cmd = ["sudo", "wg-quick", "down", self.interface_name]
                result = subprocess.run(cmd, capture_output=True, timeout=30)

                if result.returncode == 0:
                    self.connected = False
                    self.logger.info("WireGuard disconnected")
                    return True

            elif self.platform == "Windows":
                cmd = ["wireguard", "/uninstalltunnelservice", self.interface_name]
                result = subprocess.run(
                    cmd, capture_output=True, timeout=30, shell=True
                )

                if result.returncode == 0:
                    self.connected = False
                    self.logger.info("WireGuard disconnected on Windows")
                    return True

            return False

        except Exception as e:
            self.logger.error(f"WireGuard disconnect failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get WireGuard connection status"""
        status = {
            "backend": "wireguard",
            "connected": self.connected,
            "interface": self.interface_name,
            "platform": self.platform,
        }

        if self.connected:
            try:
                # Get interface statistics
                result = subprocess.run(
                    ["wg", "show", self.interface_name],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )

                if result.returncode == 0:
                    status["details"] = result.stdout

            except Exception as e:
                self.logger.debug(f"Could not get WireGuard stats: {e}")

        return status


class OpenVPNBackend(VPNBackend):
    """
    OpenVPN Backend
    Integrates with OpenVPN client
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.config_file = config.get("config_file", "/etc/openvpn/client.conf")
        self.process = None

    def check_availability(self) -> bool:
        """Check if OpenVPN is available"""
        try:
            if self.platform == "Windows":
                cmd = ["where", "openvpn"]
                result = subprocess.run(cmd, capture_output=True, timeout=5, shell=True)
            else:
                cmd = ["which", "openvpn"]
                result = subprocess.run(cmd, capture_output=True, timeout=5)

            return result.returncode == 0

        except Exception as e:
            self.logger.debug(f"OpenVPN availability check failed: {e}")
            return False

    def connect(self) -> bool:
        """Establish OpenVPN connection"""
        try:
            if not self.check_availability():
                self.logger.warning("OpenVPN not available on system")
                return False

            if self.platform == "Windows":
                cmd = ["openvpn", "--config", self.config_file]
            else:
                cmd = ["sudo", "openvpn", "--config", self.config_file]

            # Start OpenVPN process in background
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )

            # Wait briefly to check if connection succeeds
            time.sleep(5)

            if self.process.poll() is None:
                # Process still running
                self.connected = True
                self.logger.info("OpenVPN connected")
                return True
            else:
                self.logger.error("OpenVPN process terminated unexpectedly")
                return False

        except Exception as e:
            self.logger.error(f"OpenVPN connection failed: {e}")
            return False

    def disconnect(self) -> bool:
        """Disconnect OpenVPN"""
        try:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                self.process.wait(timeout=10)
                self.connected = False
                self.logger.info("OpenVPN disconnected")
                return True

            return True

        except Exception as e:
            self.logger.error(f"OpenVPN disconnect failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get OpenVPN status"""
        return {
            "backend": "openvpn",
            "connected": self.connected,
            "config_file": self.config_file,
            "platform": self.platform,
            "process_running": self.process is not None and self.process.poll() is None,
        }


class IKEv2Backend(VPNBackend):
    """
    IKEv2/IPSec Backend
    Uses native OS VPN capabilities
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.connection_name = config.get("connection_name", "ThirstysVPN")

    def check_availability(self) -> bool:
        """IKEv2 is built into most modern OSes"""
        return self.platform in ["Linux", "Windows", "Darwin"]

    def connect(self) -> bool:
        """Establish IKEv2 connection"""
        try:
            if self.platform == "Linux":
                return self._connect_linux_strongswan()
            elif self.platform == "Windows":
                return self._connect_windows_native()
            elif self.platform == "Darwin":
                return self._connect_macos_native()

            return False

        except Exception as e:
            self.logger.error(f"IKEv2 connection failed: {e}")
            return False

    def _connect_linux_strongswan(self) -> bool:
        """Connect using strongSwan on Linux"""
        try:
            # Use strongSwan's swanctl or ipsec command
            cmd = ["sudo", "ipsec", "up", self.connection_name]
            result = subprocess.run(cmd, capture_output=True, timeout=30)

            if result.returncode == 0:
                self.connected = True
                self.logger.info("IKEv2 connected on Linux")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Linux IKEv2 connection error: {e}")
            return False

    def _connect_windows_native(self) -> bool:
        """Connect using Windows native VPN"""
        try:
            # Use rasdial command
            cmd = ["rasdial", self.connection_name]
            result = subprocess.run(cmd, capture_output=True, timeout=30, shell=True)

            if result.returncode == 0:
                self.connected = True
                self.logger.info("IKEv2 connected on Windows")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Windows IKEv2 connection error: {e}")
            return False

    def _connect_macos_native(self) -> bool:
        """Connect using macOS native VPN"""
        try:
            # Use scutil for IKEv2/IPSec VPN connections
            cmd = ["scutil", "--nc", "start", self.connection_name]
            result = subprocess.run(cmd, capture_output=True, timeout=30)

            if result.returncode == 0:
                self.connected = True
                self.logger.info("IKEv2 connected on macOS")
                return True

            return False

        except Exception as e:
            self.logger.error(f"macOS IKEv2 connection error: {e}")
            return False

    def disconnect(self) -> bool:
        """Disconnect IKEv2"""
        try:
            if not self.connected:
                return True

            if self.platform == "Linux":
                cmd = ["sudo", "ipsec", "down", self.connection_name]
            elif self.platform == "Windows":
                cmd = ["rasdial", self.connection_name, "/disconnect"]
            elif self.platform == "Darwin":
                # Use scutil for IKEv2/IPSec on macOS
                cmd = ["scutil", "--nc", "stop", self.connection_name]
            else:
                return False

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=30,
                shell=True if self.platform == "Windows" else False,
            )

            if result.returncode == 0:
                self.connected = False
                self.logger.info("IKEv2 disconnected")
                return True

            return False

        except Exception as e:
            self.logger.error(f"IKEv2 disconnect failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get IKEv2 status"""
        return {
            "backend": "ikev2",
            "connected": self.connected,
            "connection_name": self.connection_name,
            "platform": self.platform,
        }


class VPNBackendFactory:
    """Factory for creating VPN backend instances"""

    @staticmethod
    def create_backend(protocol: str, config: Dict[str, Any]) -> Optional[VPNBackend]:
        """
        Create VPN backend based on protocol

        Args:
            protocol: 'wireguard', 'openvpn', or 'ikev2'
            config: Backend-specific configuration

        Returns:
            VPNBackend instance or None if protocol unsupported
        """
        backends = {
            "wireguard": WireGuardBackend,
            "openvpn": OpenVPNBackend,
            "ikev2": IKEv2Backend,
        }

        backend_class = backends.get(protocol.lower())
        if backend_class:
            return backend_class(config)

        return None

    @staticmethod
    def get_available_backends() -> List[str]:
        """
        Get list of available VPN backends on this system

        Returns:
            List of available backend names
        """
        available = []
        test_config = {}

        for protocol in ["wireguard", "openvpn", "ikev2"]:
            backend = VPNBackendFactory.create_backend(protocol, test_config)
            if backend and backend.check_availability():
                available.append(protocol)

        return available
