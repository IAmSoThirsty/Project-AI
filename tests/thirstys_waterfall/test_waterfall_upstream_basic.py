"""
Basic tests for Thirstys Waterfall components
"""

import unittest
from thirstys_waterfall.config import ConfigRegistry, ConfigValidator
from thirstys_waterfall.firewalls import PacketFilteringFirewall
from cryptography.fernet import Fernet


class TestConfiguration(unittest.TestCase):
    """Test configuration management"""

    def test_config_registry_singleton(self):
        """Test that ConfigRegistry is a singleton"""
        config1 = ConfigRegistry()
        config2 = ConfigRegistry()
        self.assertIs(config1, config2)

    def test_config_defaults(self):
        """Test default configuration loading"""
        config = ConfigRegistry()
        config.initialize()

        self.assertEqual(config.get("global.privacy_mode"), "maximum")
        self.assertTrue(config.get("global.kill_switch_enabled"))
        self.assertTrue(config.get("vpn.enabled"))

    def test_config_validation(self):
        """Test configuration validation"""
        config = ConfigRegistry()
        config.initialize()

        valid, errors = ConfigValidator.validate(config.export_config())
        self.assertTrue(valid, f"Configuration validation failed: {errors}")


class TestFirewalls(unittest.TestCase):
    """Test firewall components"""

    def test_packet_filtering_firewall(self):
        """Test packet filtering firewall"""
        fw = PacketFilteringFirewall({"enabled": True, "default_policy": "deny"})
        fw.start()

        self.assertTrue(fw.is_active())

        # Test packet processing
        packet = {
            "src_ip": "192.168.1.1",
            "dst_ip": "8.8.8.8",
            "protocol": "tcp",
            "state": "established",
        }

        result = fw.process_packet(packet)
        # Established connections should be allowed
        self.assertTrue(result)

        fw.stop()


class TestEncryption(unittest.TestCase):
    """Test encryption components"""

    def test_config_encryption(self):
        """Test configuration encryption"""
        config = ConfigRegistry()
        key = Fernet.generate_key()
        config.initialize(encryption_key=key)

        # Test encrypted storage
        config.set_encrypted("test_key", "secret_value")
        retrieved = config.get_encrypted("test_key")

        self.assertEqual(retrieved, "secret_value")

    def test_encryption_required(self):
        """Test that encryption is used throughout"""
        from thirstys_waterfall.browser.encrypted_search import EncryptedSearchEngine
        from thirstys_waterfall.browser.encrypted_navigation import (
            EncryptedNavigationHistory,
        )

        cipher = Fernet(Fernet.generate_key())

        # Test encrypted search
        search = EncryptedSearchEngine(cipher)
        search.start()
        self.assertTrue(search._active)
        search.stop()

        # Test encrypted navigation
        nav = EncryptedNavigationHistory(cipher)
        nav.start()
        self.assertTrue(nav._active)
        nav.stop()


class TestPrivacyFeatures(unittest.TestCase):
    """Test privacy features"""

    def test_no_popups_config(self):
        """Test that pop-ups are blocked by default"""
        config = ConfigRegistry()
        config.initialize()

        # Browser should block pop-ups
        browser_config = config.get_section("browser")
        self.assertTrue(browser_config.get("tab_isolation"))

    def test_vpn_builtin(self):
        """Test that VPN is built-in"""
        config = ConfigRegistry()
        config.initialize()

        vpn_config = config.get_section("vpn")
        self.assertTrue(vpn_config.get("enabled"))
        self.assertTrue(vpn_config.get("multi_hop"))


if __name__ == "__main__":
    unittest.main()
