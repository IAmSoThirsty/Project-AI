import unittest
from unittest.mock import patch, MagicMock
from src.app.infrastructure.networking.wifi_controller import WiFiController
from src.app.infrastructure.vpn.backends import WireGuardBackend, OpenVPNBackend, IKEv2Backend

class TestSubprocessShellFix(unittest.TestCase):
    @patch("subprocess.run")
    def test_wifi_controller_no_shell(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")

        # Override platform to reach Windows methods
        with patch("platform.system", return_value="Windows"):
            controller = WiFiController()
            # _discover_adapters -> _discover_adapters_windows
            controller._discover_adapters_windows()
            for call in mock_run.call_args_list:
                _, kwargs = call
                self.assertNotIn("shell", kwargs, "shell=True should not be used")
                self.assertNotEqual(kwargs.get("shell"), True, "shell=True should not be used")

            mock_run.reset_mock()
            # _get_adapter_capabilities_windows
            controller._get_adapter_capabilities_windows("Ethernet", "00:11:22:33:44:55")
            for call in mock_run.call_args_list:
                _, kwargs = call
                self.assertNotIn("shell", kwargs, "shell=True should not be used")
                self.assertNotEqual(kwargs.get("shell"), True, "shell=True should not be used")

            mock_run.reset_mock()
            # _scan_networks_windows
            controller._scan_networks_windows(None)
            for call in mock_run.call_args_list:
                _, kwargs = call
                self.assertNotIn("shell", kwargs, "shell=True should not be used")
                self.assertNotEqual(kwargs.get("shell"), True, "shell=True should not be used")

    @patch("subprocess.run")
    def test_wireguard_backend_no_shell(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        config = {"interface": "wg0", "config_path": "C:\\wg0.conf"}

        with patch("platform.system", return_value="Windows"):
            backend = WireGuardBackend(config)
            backend.platform = "Windows"

            backend.check_availability()
            for call in mock_run.call_args_list:
                _, kwargs = call
                self.assertNotIn("shell", kwargs, "shell=True should not be used")
                self.assertNotEqual(kwargs.get("shell"), True, "shell=True should not be used")

            mock_run.reset_mock()
            backend._connect_windows()
            for call in mock_run.call_args_list:
                _, kwargs = call
                self.assertNotIn("shell", kwargs, "shell=True should not be used")
                self.assertNotEqual(kwargs.get("shell"), True, "shell=True should not be used")

            mock_run.reset_mock()
            backend.disconnect()
            for call in mock_run.call_args_list:
                _, kwargs = call
                self.assertNotIn("shell", kwargs, "shell=True should not be used")
                self.assertNotEqual(kwargs.get("shell"), True, "shell=True should not be used")

    @patch("subprocess.run")
    def test_openvpn_backend_no_shell(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        config = {}

        with patch("platform.system", return_value="Windows"):
            backend = OpenVPNBackend(config)
            backend.platform = "Windows"

            backend.check_availability()
            for call in mock_run.call_args_list:
                _, kwargs = call
                self.assertNotIn("shell", kwargs, "shell=True should not be used")
                self.assertNotEqual(kwargs.get("shell"), True, "shell=True should not be used")

    @patch("subprocess.run")
    def test_ikev2_backend_no_shell(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        config = {"connection_name": "TestVPN"}

        with patch("platform.system", return_value="Windows"):
            backend = IKEv2Backend(config)
            backend.platform = "Windows"

            backend._connect_windows_native()
            for call in mock_run.call_args_list:
                _, kwargs = call
                self.assertNotIn("shell", kwargs, "shell=True should not be used")
                self.assertNotEqual(kwargs.get("shell"), True, "shell=True should not be used")

            mock_run.reset_mock()
            backend.connected = True
            backend.disconnect()
            for call in mock_run.call_args_list:
                _, kwargs = call
                self.assertNotIn("shell", kwargs, "shell=True should not be used")
                self.assertNotEqual(kwargs.get("shell"), True, "shell=True should not be used")

if __name__ == "__main__":
    unittest.main()
