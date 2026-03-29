# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / test_firewall_backends.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / test_firewall_backends.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Tests for Firewall Backend Implementations
Tests firewall rule enforcement and platform-specific integrations
"""

import unittest
from unittest.mock import patch, MagicMock
from thirstys_waterfall.firewalls.backends import (
    NftablesBackend,
    WindowsFirewallBackend,
    PFBackend,
    FirewallBackendFactory,
)


class TestNftablesBackend(unittest.TestCase):
    """Test nftables (Linux) backend implementation"""

    def setUp(self):
        self.config = {"table": "test_table", "chain": "test_chain"}
        self.backend = NftablesBackend(self.config)

    def test_initialization(self):
        """Test nftables backend initialization"""
        self.assertEqual(self.backend.table_name, "test_table")
        self.assertEqual(self.backend.chain_name, "test_chain")
        self.assertFalse(self.backend.active)
        self.assertEqual(len(self.backend.rules), 0)

    @patch("subprocess.run")
    def test_check_availability_linux(self, mock_run):
        """Test nftables availability on Linux"""
        self.backend.platform = "Linux"
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.check_availability()

        self.assertTrue(result)

    def test_check_availability_non_linux(self):
        """Test nftables not available on non-Linux"""
        self.backend.platform = "Windows"

        result = self.backend.check_availability()

        self.assertFalse(result)

    @patch("subprocess.run")
    def test_initialize_success(self, mock_run):
        """Test successful nftables initialization"""
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.initialize()

        self.assertTrue(result)
        # Should create table and chain
        self.assertEqual(mock_run.call_count, 2)

    @patch("subprocess.run")
    def test_add_rule_basic(self, mock_run):
        """Test adding basic nftables rule"""
        mock_run.return_value = MagicMock(returncode=0)

        rule = {
            "id": "rule_001",
            "action": "accept",
            "protocol": "tcp",
            "dst_port": 443,
        }

        result = self.backend.add_rule(rule)

        self.assertTrue(result)
        self.assertEqual(len(self.backend.rules), 1)
        self.assertEqual(self.backend.rules[0]["id"], "rule_001")

    @patch("subprocess.run")
    def test_add_rule_with_source_ip(self, mock_run):
        """Test adding nftables rule with source IP filter"""
        mock_run.return_value = MagicMock(returncode=0)

        rule = {
            "id": "rule_002",
            "action": "drop",
            "protocol": "tcp",
            "src_ip": "192.168.1.0/24",
            "dst_port": 22,
        }

        result = self.backend.add_rule(rule)

        self.assertTrue(result)
        self.assertEqual(len(self.backend.rules), 1)

    def test_remove_rule(self):
        """Test removing nftables rule"""
        self.backend.rules = [
            {"id": "rule_001", "rule": {"action": "accept"}},
            {"id": "rule_002", "rule": {"action": "drop"}},
        ]

        result = self.backend.remove_rule("rule_001")

        self.assertTrue(result)
        self.assertEqual(len(self.backend.rules), 1)
        self.assertEqual(self.backend.rules[0]["id"], "rule_002")

    @patch("subprocess.run")
    def test_enable_firewall(self, mock_run):
        """Test enabling nftables firewall"""
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.enable()

        self.assertTrue(result)
        self.assertTrue(self.backend.active)

    @patch("subprocess.run")
    def test_disable_firewall(self, mock_run):
        """Test disabling nftables firewall"""
        self.backend.active = True
        self.backend.rules = [{"id": "rule_001", "rule": {}}]
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.disable()

        self.assertTrue(result)
        self.assertFalse(self.backend.active)
        self.assertEqual(len(self.backend.rules), 0)

    def test_get_statistics(self):
        """Test getting nftables statistics"""
        self.backend.active = True
        self.backend.rules = [{"id": "rule_001", "rule": {}}]

        stats = self.backend.get_statistics()

        self.assertTrue(stats["active"])
        self.assertEqual(stats["rules_count"], 1)
        self.assertIn("platform", stats)


class TestWindowsFirewallBackend(unittest.TestCase):
    """Test Windows Firewall backend implementation"""

    def setUp(self):
        self.config = {"rule_prefix": "TestPrefix"}
        self.backend = WindowsFirewallBackend(self.config)

    def test_initialization(self):
        """Test Windows Firewall backend initialization"""
        self.assertEqual(self.backend.rule_prefix, "TestPrefix")
        self.assertFalse(self.backend.active)

    @patch("subprocess.run")
    def test_check_availability_windows(self, mock_run):
        """Test Windows Firewall availability on Windows"""
        self.backend.platform = "Windows"
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.check_availability()

        self.assertTrue(result)

    def test_check_availability_non_windows(self):
        """Test Windows Firewall not available on non-Windows"""
        self.backend.platform = "Linux"

        result = self.backend.check_availability()

        self.assertFalse(result)

    @patch("subprocess.run")
    def test_initialize_success(self, mock_run):
        """Test successful Windows Firewall initialization"""
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.initialize()

        self.assertTrue(result)

    @patch("subprocess.run")
    def test_add_rule_inbound(self, mock_run):
        """Test adding inbound Windows Firewall rule"""
        mock_run.return_value = MagicMock(returncode=0)

        rule = {
            "id": "rule_001",
            "action": "allow",
            "protocol": "tcp",
            "direction": "in",
            "port": 443,
        }

        result = self.backend.add_rule(rule)

        self.assertTrue(result)
        self.assertEqual(len(self.backend.rules), 1)

    @patch("subprocess.run")
    def test_add_rule_outbound(self, mock_run):
        """Test adding outbound Windows Firewall rule"""
        mock_run.return_value = MagicMock(returncode=0)

        rule = {
            "id": "rule_002",
            "action": "block",
            "protocol": "udp",
            "direction": "out",
            "port": 53,
        }

        result = self.backend.add_rule(rule)

        self.assertTrue(result)
        self.assertEqual(len(self.backend.rules), 1)

    @patch("subprocess.run")
    def test_add_rule_with_program(self, mock_run):
        """Test adding rule with program filter"""
        mock_run.return_value = MagicMock(returncode=0)

        rule = {
            "id": "rule_003",
            "action": "allow",
            "protocol": "tcp",
            "direction": "in",
            "program": "C:\\Program Files\\MyApp\\app.exe",
        }

        result = self.backend.add_rule(rule)

        self.assertTrue(result)

    @patch("subprocess.run")
    def test_remove_rule(self, mock_run):
        """Test removing Windows Firewall rule"""
        self.backend.rules = [
            {"id": "rule_001", "name": "TestPrefix_rule_001", "rule": {}}
        ]
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.remove_rule("rule_001")

        self.assertTrue(result)
        self.assertEqual(len(self.backend.rules), 0)

    @patch("subprocess.run")
    def test_enable_firewall(self, mock_run):
        """Test enabling Windows Firewall"""
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.enable()

        self.assertTrue(result)
        self.assertTrue(self.backend.active)
        # Should enable all three profiles
        self.assertEqual(mock_run.call_count, 3)


class TestPFBackend(unittest.TestCase):
    """Test PF (macOS) backend implementation"""

    def setUp(self):
        self.config = {"anchor": "test_anchor", "rules_file": "/tmp/test_pf.rules"}
        self.backend = PFBackend(self.config)

    def test_initialization(self):
        """Test PF backend initialization"""
        self.assertEqual(self.backend.anchor_name, "test_anchor")
        self.assertEqual(self.backend.rules_file, "/tmp/test_pf.rules")
        self.assertFalse(self.backend.active)

    @patch("subprocess.run")
    def test_check_availability_macos(self, mock_run):
        """Test PF availability on macOS"""
        self.backend.platform = "Darwin"
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.check_availability()

        self.assertTrue(result)

    def test_check_availability_non_macos(self):
        """Test PF not available on non-macOS"""
        self.backend.platform = "Linux"

        result = self.backend.check_availability()

        self.assertFalse(result)

    def test_convert_to_pf_rule(self):
        """Test converting rule dict to PF syntax"""
        rule = {
            "action": "accept",
            "direction": "in",
            "protocol": "tcp",
            "dst_port": 443,
        }

        pf_rule = self.backend._convert_to_pf_rule(rule)

        self.assertIn("pass", pf_rule)
        self.assertIn("in", pf_rule)
        self.assertIn("tcp", pf_rule)
        self.assertIn("443", pf_rule)

    def test_convert_to_pf_rule_block(self):
        """Test converting block rule to PF syntax"""
        rule = {
            "action": "block",
            "direction": "out",
            "protocol": "udp",
            "src_ip": "10.0.0.0/8",
        }

        pf_rule = self.backend._convert_to_pf_rule(rule)

        self.assertIn("block", pf_rule)
        self.assertIn("out", pf_rule)
        self.assertIn("udp", pf_rule)
        self.assertIn("10.0.0.0/8", pf_rule)

    @patch("os.fdopen")
    @patch("os.open")
    @patch("subprocess.run")
    def test_add_rule(self, mock_run, mock_os_open, mock_fdopen):
        """Test adding PF rule"""
        mock_run.return_value = MagicMock(returncode=0)
        mock_file = MagicMock()
        mock_fdopen.return_value.__enter__ = MagicMock(return_value=mock_file)
        mock_fdopen.return_value.__exit__ = MagicMock(return_value=False)

        rule = {"id": "rule_001", "action": "accept", "protocol": "tcp", "dst_port": 80}

        result = self.backend.add_rule(rule)

        self.assertTrue(result)
        self.assertEqual(len(self.backend.rules), 1)
        # Verify secure file creation with os.open was attempted
        mock_os_open.assert_called_once()

    @patch("os.fdopen")
    @patch("os.open")
    @patch("subprocess.run")
    def test_remove_rule(self, mock_run, mock_os_open, mock_fdopen):
        """Test removing PF rule"""
        mock_file = MagicMock()
        mock_fdopen.return_value.__enter__ = MagicMock(return_value=mock_file)
        mock_fdopen.return_value.__exit__ = MagicMock(return_value=False)

        self.backend.rules = [
            {"id": "rule_001", "rule": {"action": "accept"}},
            {"id": "rule_002", "rule": {"action": "drop"}},
        ]
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.remove_rule("rule_001")

        self.assertTrue(result)
        self.assertEqual(len(self.backend.rules), 1)
        self.assertEqual(self.backend.rules[0]["id"], "rule_002")

    @patch("subprocess.run")
    def test_enable_firewall(self, mock_run):
        """Test enabling PF firewall"""
        mock_run.return_value = MagicMock(returncode=0)

        result = self.backend.enable()

        self.assertTrue(result)
        self.assertTrue(self.backend.active)


class TestFirewallBackendFactory(unittest.TestCase):
    """Test firewall backend factory"""

    @patch("platform.system")
    @patch.object(NftablesBackend, "check_availability")
    def test_create_linux_backend(self, mock_check, mock_platform):
        """Test creating Linux firewall backend"""
        mock_platform.return_value = "Linux"
        mock_check.return_value = True

        backend = FirewallBackendFactory.create_backend()

        self.assertIsInstance(backend, NftablesBackend)

    @patch("platform.system")
    @patch.object(WindowsFirewallBackend, "check_availability")
    def test_create_windows_backend(self, mock_check, mock_platform):
        """Test creating Windows firewall backend"""
        mock_platform.return_value = "Windows"
        mock_check.return_value = True

        backend = FirewallBackendFactory.create_backend()

        self.assertIsInstance(backend, WindowsFirewallBackend)

    @patch("platform.system")
    @patch.object(PFBackend, "check_availability")
    def test_create_macos_backend(self, mock_check, mock_platform):
        """Test creating macOS firewall backend"""
        mock_platform.return_value = "Darwin"
        mock_check.return_value = True

        backend = FirewallBackendFactory.create_backend()

        self.assertIsInstance(backend, PFBackend)

    @patch("platform.system")
    def test_create_unsupported_platform(self, mock_platform):
        """Test creating backend on unsupported platform"""
        mock_platform.return_value = "UnknownOS"

        backend = FirewallBackendFactory.create_backend()

        self.assertIsNone(backend)


class TestFirewallRuleEnforcement(unittest.TestCase):
    """Integration tests for firewall rule enforcement"""

    @patch("subprocess.run")
    def test_nftables_rule_enforcement(self, mock_run):
        """Test complete nftables rule enforcement flow"""
        backend = NftablesBackend({"table": "test", "chain": "input"})
        backend.platform = "Linux"
        mock_run.return_value = MagicMock(returncode=0)

        # Enable firewall
        self.assertTrue(backend.enable())

        # Add multiple rules
        rules = [
            {
                "id": "allow_https",
                "action": "accept",
                "protocol": "tcp",
                "dst_port": 443,
            },
            {"id": "allow_http", "action": "accept", "protocol": "tcp", "dst_port": 80},
            {"id": "block_ssh", "action": "drop", "protocol": "tcp", "dst_port": 22},
        ]

        for rule in rules:
            self.assertTrue(backend.add_rule(rule))

        self.assertEqual(len(backend.rules), 3)

        # Remove one rule
        self.assertTrue(backend.remove_rule("allow_http"))
        self.assertEqual(len(backend.rules), 2)

        # Get statistics
        stats = backend.get_statistics()
        self.assertEqual(stats["rules_count"], 2)

        # Disable firewall
        self.assertTrue(backend.disable())
        self.assertEqual(len(backend.rules), 0)

    @patch("subprocess.run")
    def test_windows_firewall_rule_enforcement(self, mock_run):
        """Test complete Windows Firewall rule enforcement flow"""
        backend = WindowsFirewallBackend({"rule_prefix": "Test"})
        backend.platform = "Windows"
        mock_run.return_value = MagicMock(returncode=0)

        # Enable firewall
        self.assertTrue(backend.enable())

        # Add rules
        rules = [
            {
                "id": "web_in",
                "action": "allow",
                "protocol": "tcp",
                "direction": "in",
                "port": 443,
            },
            {
                "id": "dns_out",
                "action": "allow",
                "protocol": "udp",
                "direction": "out",
                "port": 53,
            },
        ]

        for rule in rules:
            self.assertTrue(backend.add_rule(rule))

        self.assertEqual(len(backend.rules), 2)

    @patch("os.fdopen")
    @patch("os.open")
    @patch("subprocess.run")
    def test_pf_rule_enforcement(self, mock_run, mock_os_open, mock_fdopen):
        """Test complete PF rule enforcement flow"""
        backend = PFBackend({"anchor": "test", "rules_file": "/tmp/test.rules"})
        backend.platform = "Darwin"
        mock_run.return_value = MagicMock(returncode=0)
        mock_file = MagicMock()
        mock_fdopen.return_value.__enter__ = MagicMock(return_value=mock_file)
        mock_fdopen.return_value.__exit__ = MagicMock(return_value=False)

        # Enable firewall
        self.assertTrue(backend.enable())

        # Add rule
        rule = {
            "id": "web_traffic",
            "action": "accept",
            "protocol": "tcp",
            "dst_port": 443,
        }

        self.assertTrue(backend.add_rule(rule))
        self.assertEqual(len(backend.rules), 1)

    @patch("subprocess.run")
    def test_rule_priority_enforcement(self, mock_run):
        """Test that rules are enforced in order"""
        backend = NftablesBackend({"table": "test", "chain": "input"})
        backend.platform = "Linux"
        mock_run.return_value = MagicMock(returncode=0)

        backend.enable()

        # Add rules in specific order
        rules = [
            {"id": "rule_1", "action": "accept", "protocol": "tcp"},
            {"id": "rule_2", "action": "drop", "protocol": "udp"},
            {"id": "rule_3", "action": "accept", "protocol": "icmp"},
        ]

        for rule in rules:
            backend.add_rule(rule)

        # Verify order is maintained
        self.assertEqual(backend.rules[0]["id"], "rule_1")
        self.assertEqual(backend.rules[1]["id"], "rule_2")
        self.assertEqual(backend.rules[2]["id"], "rule_3")


if __name__ == "__main__":
    unittest.main()
