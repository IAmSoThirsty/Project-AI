from unittest.mock import MagicMock, patch

import pytest

from src.app.infrastructure.networking.wifi_controller import WiFiController
from src.app.infrastructure.vpn.backends import (
    IKEv2Backend,
    OpenVPNBackend,
    WireGuardBackend,
)


@pytest.fixture
def mock_subprocess_run():
    with patch("subprocess.run") as mock_run:
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "Mock output"
        mock_run.return_value = mock_result
        yield mock_run


def test_wireguard_backend_no_shell(mock_subprocess_run):
    backend = WireGuardBackend({"interface": "wg0", "config_path": "mock.conf"})
    backend.platform = "Windows"

    backend.check_availability()
    mock_subprocess_run.assert_called_with(
        ["where", "wireguard"], capture_output=True, timeout=5, shell=False
    )

    backend._connect_windows()
    mock_subprocess_run.assert_called_with(
        ["wireguard", "/installtunnelservice", "mock.conf"],
        capture_output=True,
        timeout=30,
        shell=False,
    )

    backend.connected = True
    backend.disconnect()
    mock_subprocess_run.assert_called_with(
        ["wireguard", "/uninstalltunnelservice", "wg0"],
        capture_output=True,
        timeout=30,
        shell=False,
    )


def test_openvpn_backend_no_shell(mock_subprocess_run):
    backend = OpenVPNBackend({"config_file": "mock.conf"})
    backend.platform = "Windows"

    backend.check_availability()
    mock_subprocess_run.assert_called_with(
        ["where", "openvpn"], capture_output=True, timeout=5, shell=False
    )


def test_ikev2_backend_no_shell(mock_subprocess_run):
    backend = IKEv2Backend({"connection_name": "MockVPN"})
    backend.platform = "Windows"

    backend._connect_windows_native()
    mock_subprocess_run.assert_called_with(
        ["rasdial", "MockVPN"], capture_output=True, timeout=30, shell=False
    )

    backend.connected = True
    backend.disconnect()
    mock_subprocess_run.assert_called_with(
        ["rasdial", "MockVPN", "/disconnect"],
        capture_output=True,
        timeout=30,
        shell=False,
    )


def test_wificontroller_no_shell(mock_subprocess_run):
    controller = WiFiController()
    controller.platform = "Windows"

    controller._discover_adapters_windows()
    mock_subprocess_run.assert_called_with(
        ["netsh", "wlan", "show", "interfaces"],
        capture_output=True,
        text=True,
        timeout=10,
        shell=False,
    )

    controller._get_adapter_capabilities_windows("mock_interface", "mock_mac")
    mock_subprocess_run.assert_called_with(
        ["netsh", "wlan", "show", "drivers"],
        capture_output=True,
        text=True,
        timeout=10,
        shell=False,
    )

    controller._scan_networks_windows(None)
    mock_subprocess_run.assert_called_with(
        ["netsh", "wlan", "show", "networks", "mode=bssid"],
        capture_output=True,
        text=True,
        timeout=10,
        shell=False,
    )
