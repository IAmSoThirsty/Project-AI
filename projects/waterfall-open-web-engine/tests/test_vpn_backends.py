# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_vpn_backends.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_vpn_backends.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Tests for VPN Backend Implementations
Tests VPN handshake and platform-specific integrations
"""

import unittest
import platform
from unittest.mock import patch, MagicMock
from thirstys_waterfall.vpn.backends import (
    WireGuardBackend,
    OpenVPNBackend,
    IKEv2Backend,
    VPNBackendFactory,
)


class TestWireGuardBackend(unittest.TestCase):
    """Test WireGuard backend implementation"""

    def setUp(self):
        self.config = {"interface": "wg0", "config_path": "/etc/wireguard/wg0.conf"}
        self.backend = WireGuardBackend(self.config)

    def test_initialization(self):
        """Test WireGuard backend initialization"""
        self.assertEqual(self.backend.interface_name, "wg0")
        self.assertEqual(self.backend.config_path, "/etc/wireguard/wg0.conf")
        self.assertFalse(self.backend.connected)
        self.assertEqual(self.backend.platform, platform.system())

    @patch("subprocess.run")
    def test_check_availability_linux(self, mock_run):
        """Test WireGuard availability check on Linux"""
        self.backend.platform = "Linux"
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.check_availability()

        self.assertTrue(result)
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_check_availability_not_installed(self, mock_run):
        """Test WireGuard availability when not installed"""
        self.backend.platform = "Linux"
        mock_run.return_value = MagicMock(returncode=1)

        result = self.backend.check_availability()

        self.assertFalse(result)

    @patch("subprocess.run")
    def test_connect_linux_success(self, mock_run):
        """Test successful WireGuard connection on Linux"""
        self.backend.platform = "Linux"
        mock_run.side_effect = [
            MagicMock(returncode=0),  # availability check
            MagicMock(returncode=0, stderr=""),  # wg-quick up
        ]

        result = self.backend.connect()

        self.assertTrue(result)
        self.assertTrue(self.backend.connected)
        self.assertEqual(mock_run.call_count, 2)

    @patch("subprocess.run")
    def test_connect_failure(self, mock_run):
        """Test failed WireGuard connection"""
        self.backend.platform = "Linux"
        mock_run.side_effect = [
            MagicMock(returncode=0),  # availability check
            MagicMock(returncode=1, stderr="Connection failed"),  # wg-quick up
        ]

        result = self.backend.connect()

        self.assertFalse(result)
        self.assertFalse(self.backend.connected)

    @patch("subprocess.run")
    def test_disconnect_linux(self, mock_run):
        """Test WireGuard disconnection on Linux"""
        self.backend.platform = "Linux"
        self.backend.connected = True
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.disconnect()

        self.assertTrue(result)
        self.assertFalse(self.backend.connected)

    def test_get_status(self):
        """Test getting WireGuard status"""
        self.backend.connected = True

        status = self.backend.get_status()

        self.assertEqual(status["backend"], "wireguard")
        self.assertTrue(status["connected"])
        self.assertEqual(status["interface"], "wg0")
        self.assertIn("platform", status)


class TestOpenVPNBackend(unittest.TestCase):
    """Test OpenVPN backend implementation"""

    def setUp(self):
        self.config = {"config_file": "/etc/openvpn/client.conf"}
        self.backend = OpenVPNBackend(self.config)

    def test_initialization(self):
        """Test OpenVPN backend initialization"""
        self.assertEqual(self.backend.config_file, "/etc/openvpn/client.conf")
        self.assertFalse(self.backend.connected)
        self.assertIsNone(self.backend.process)

    @patch("subprocess.run")
    def test_check_availability(self, mock_run):
        """Test OpenVPN availability check"""
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.check_availability()

        self.assertTrue(result)

    @patch("subprocess.Popen")
    @patch("time.sleep")
    def test_connect_success(self, mock_sleep, mock_popen):
        """Test successful OpenVPN connection"""
        mock_process = MagicMock()
        mock_process.poll.return_value = None  # Process still running
        mock_popen.return_value = mock_process

        with patch.object(self.backend, "check_availability", return_value=True):
            result = self.backend.connect()

        self.assertTrue(result)
        self.assertTrue(self.backend.connected)
        self.assertIsNotNone(self.backend.process)

    @patch("subprocess.Popen")
    @patch("time.sleep")
    def test_connect_process_dies(self, mock_sleep, mock_popen):
        """Test OpenVPN connection when process dies immediately"""
        mock_process = MagicMock()
        mock_process.poll.return_value = 1  # Process terminated
        mock_popen.return_value = mock_process

        with patch.object(self.backend, "check_availability", return_value=True):
            result = self.backend.connect()

        self.assertFalse(result)
        self.assertFalse(self.backend.connected)

    def test_disconnect(self):
        """Test OpenVPN disconnection"""
        mock_process = MagicMock()
        mock_process.poll.return_value = None
        self.backend.process = mock_process
        self.backend.connected = True

        result = self.backend.disconnect()

        self.assertTrue(result)
        self.assertFalse(self.backend.connected)
        mock_process.terminate.assert_called_once()

    def test_get_status(self):
        """Test getting OpenVPN status"""
        self.backend.connected = True

        status = self.backend.get_status()

        self.assertEqual(status["backend"], "openvpn")
        self.assertTrue(status["connected"])
        self.assertIn("config_file", status)


class TestIKEv2Backend(unittest.TestCase):
    """Test IKEv2 backend implementation"""

    def setUp(self):
        self.config = {"connection_name": "TestVPN"}
        self.backend = IKEv2Backend(self.config)

    def test_initialization(self):
        """Test IKEv2 backend initialization"""
        self.assertEqual(self.backend.connection_name, "TestVPN")
        self.assertFalse(self.backend.connected)

    def test_check_availability(self):
        """Test IKEv2 availability - should be available on major platforms"""
        result = self.backend.check_availability()

        # IKEv2 should be available on Linux, Windows, Darwin
        expected = self.backend.platform in ["Linux", "Windows", "Darwin"]
        self.assertEqual(result, expected)

    @patch("subprocess.run")
    def test_connect_linux(self, mock_run):
        """Test IKEv2 connection on Linux"""
        self.backend.platform = "Linux"
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.connect()

        self.assertTrue(result)
        self.assertTrue(self.backend.connected)

    @patch("subprocess.run")
    def test_connect_windows(self, mock_run):
        """Test IKEv2 connection on Windows"""
        self.backend.platform = "Windows"
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.connect()

        self.assertTrue(result)
        self.assertTrue(self.backend.connected)

    @patch("subprocess.run")
    def test_connect_macos(self, mock_run):
        """Test IKEv2 connection on macOS"""
        self.backend.platform = "Darwin"
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.connect()

        self.assertTrue(result)
        self.assertTrue(self.backend.connected)

    @patch("subprocess.run")
    def test_disconnect(self, mock_run):
        """Test IKEv2 disconnection"""
        self.backend.platform = "Linux"
        self.backend.connected = True
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.disconnect()

        self.assertTrue(result)
        self.assertFalse(self.backend.connected)

    def test_get_status(self):
        """Test getting IKEv2 status"""
        self.backend.connected = True

        status = self.backend.get_status()

        self.assertEqual(status["backend"], "ikev2")
        self.assertTrue(status["connected"])
        self.assertEqual(status["connection_name"], "TestVPN")


class TestVPNBackendFactory(unittest.TestCase):
    """Test VPN backend factory"""

    def test_create_wireguard_backend(self):
        """Test creating WireGuard backend"""
        config = {"interface": "wg0"}
        backend = VPNBackendFactory.create_backend("wireguard", config)

        self.assertIsInstance(backend, WireGuardBackend)
        self.assertEqual(backend.interface_name, "wg0")

    def test_create_openvpn_backend(self):
        """Test creating OpenVPN backend"""
        config = {"config_file": "/etc/openvpn/test.conf"}
        backend = VPNBackendFactory.create_backend("openvpn", config)

        self.assertIsInstance(backend, OpenVPNBackend)
        self.assertEqual(backend.config_file, "/etc/openvpn/test.conf")

    def test_create_ikev2_backend(self):
        """Test creating IKEv2 backend"""
        config = {"connection_name": "MyVPN"}
        backend = VPNBackendFactory.create_backend("ikev2", config)

        self.assertIsInstance(backend, IKEv2Backend)
        self.assertEqual(backend.connection_name, "MyVPN")

    def test_create_unknown_backend(self):
        """Test creating unknown backend returns None"""
        backend = VPNBackendFactory.create_backend("unknown", {})

        self.assertIsNone(backend)

    def test_case_insensitive_protocol(self):
        """Test that protocol names are case-insensitive"""
        backend1 = VPNBackendFactory.create_backend("WireGuard", {})
        backend2 = VPNBackendFactory.create_backend("WIREGUARD", {})

        self.assertIsInstance(backend1, WireGuardBackend)
        self.assertIsInstance(backend2, WireGuardBackend)

    @patch.object(WireGuardBackend, "check_availability")
    @patch.object(OpenVPNBackend, "check_availability")
    @patch.object(IKEv2Backend, "check_availability")
    def test_get_available_backends(self, mock_ikev2, mock_openvpn, mock_wg):
        """Test getting available backends"""
        mock_wg.return_value = True
        mock_openvpn.return_value = False
        mock_ikev2.return_value = True

        available = VPNBackendFactory.get_available_backends()

        self.assertIn("wireguard", available)
        self.assertNotIn("openvpn", available)
        self.assertIn("ikev2", available)


class TestVPNHandshake(unittest.TestCase):
    """Integration tests for VPN handshake procedures"""

    @patch("subprocess.run")
    def test_wireguard_handshake_sequence(self, mock_run):
        """Test complete WireGuard handshake sequence"""
        backend = WireGuardBackend({"interface": "wg0"})
        backend.platform = "Linux"

        # Mock successful handshake
        mock_run.side_effect = [
            MagicMock(returncode=0),  # availability
            MagicMock(returncode=0, stderr=""),  # connect
            MagicMock(
                returncode=0, stdout="interface: wg0\n  public key: ..."
            ),  # status
        ]

        # Connect
        self.assertTrue(backend.connect())

        # Verify connection
        self.assertTrue(backend.connected)

        # Get status
        status = backend.get_status()
        self.assertTrue(status["connected"])

    @patch("subprocess.Popen")
    @patch("time.sleep")
    def test_openvpn_handshake_sequence(self, mock_sleep, mock_popen):
        """Test complete OpenVPN handshake sequence"""
        backend = OpenVPNBackend({"config_file": "/etc/openvpn/client.conf"})

        mock_process = MagicMock()
        mock_process.poll.return_value = None
        mock_popen.return_value = mock_process

        with patch.object(backend, "check_availability", return_value=True):
            # Connect
            self.assertTrue(backend.connect())

            # Verify connection
            self.assertTrue(backend.connected)

            # Disconnect
            self.assertTrue(backend.disconnect())
            self.assertFalse(backend.connected)

    @patch("subprocess.run")
    def test_protocol_fallback(self, mock_run):
        """Test VPN protocol fallback mechanism"""
        # Simulate WireGuard not available, but OpenVPN available
        wg_backend = WireGuardBackend({})
        wg_backend.platform = "Linux"

        mock_run.return_value = MagicMock(returncode=1)  # WireGuard not available
        self.assertFalse(wg_backend.check_availability())

        # OpenVPN should be tried next
        openvpn_backend = OpenVPNBackend({})
        mock_run.return_value = MagicMock(returncode=0)  # OpenVPN available
        self.assertTrue(openvpn_backend.check_availability())

    @patch("subprocess.run")
    def test_connection_resilience(self, mock_run):
        """Test connection resilience and reconnection"""
        backend = WireGuardBackend({"interface": "wg0"})
        backend.platform = "Linux"

        # Initial connection
        mock_run.side_effect = [
            MagicMock(returncode=0),  # availability
            MagicMock(returncode=0),  # connect
        ]
        self.assertTrue(backend.connect())

        # Simulate disconnection
        mock_run.side_effect = [MagicMock(returncode=0)]  # disconnect
        self.assertTrue(backend.disconnect())

        # Reconnection
        mock_run.side_effect = [
            MagicMock(returncode=0),  # availability
            MagicMock(returncode=0),  # connect
        ]
        self.assertTrue(backend.connect())
        self.assertTrue(backend.connected)


if __name__ == "__main__":
    unittest.main()
