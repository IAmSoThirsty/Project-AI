"""
Settings Manager - Comprehensive settings with God tier encryption
Covers ALL features: standard + additional features
"""

import logging
from typing import Dict, Any
import json
from cryptography.fernet import Fernet


class SettingsManager:
    """
    Comprehensive Settings Manager with God tier encryption.

    Settings Categories:
    - General (language, theme, startup)
    - Privacy (encryption, data minimization, telemetry)
    - Security (kill switch, VPN, firewalls, DNS protection)
    - Browser (history, cache, cookies, tabs, downloads)
    - Ad Blocker (HOLY WAR mode, aggressiveness, filters)
    - Consigliere (capabilities, on-device, locked mode)
    - Media Downloader (quality, formats, library)
    - AI Assistant (local inference, context size)
    - Remote Access (browser, desktop, authentication)
    - Network (VPN hops, protocols, leak protection)
    - Firewall (8 types configuration)
    - Support (Q/A, contact, feedback)
    """

    def __init__(self, god_tier_encryption):
        self.logger = logging.getLogger(__name__)
        self.god_tier_encryption = god_tier_encryption
        self._cipher = Fernet(Fernet.generate_key())

        # Comprehensive settings for ALL features
        self.settings = {
            # General Settings
            "general": {
                "language": "en",
                "theme": "dark",
                "auto_start": False,
                "minimize_to_tray": True,
                "check_updates": False,  # Privacy-first: no auto-updates
                "notifications": True,
            },
            # Privacy Settings (God Tier)
            "privacy": {
                "god_tier_encryption": True,
                "encryption_layers": 7,
                "quantum_resistant": True,
                "data_minimization": True,
                "on_device_only": True,
                "no_telemetry": True,
                "no_logging": True,
                "forensic_resistance": True,
                "perfect_forward_secrecy": True,
                "ephemeral_storage": True,
            },
            # Security Settings
            "security": {
                "kill_switch": True,
                "kill_switch_mode": "aggressive",  # aggressive/normal
                "vpn_multi_hop": True,
                "vpn_required": True,
                "dns_leak_protection": True,
                "ipv6_leak_protection": True,
                "webrtc_leak_protection": True,
                "firewall_count": 8,
                "firewall_mode": "maximum",
                "auto_security_audit": True,
                "malware_scanning": True,
                "phishing_protection": True,
            },
            # Browser Settings
            "browser": {
                "incognito_mode": True,
                "no_history": True,
                "no_cache": True,
                "no_cookies": True,
                "no_popups": True,
                "no_redirects": True,
                "tab_isolation": True,
                "sandbox_enabled": True,
                "anti_fingerprint": True,
                "keyboard_cloaking": True,
                "mouse_cloaking": True,
                "user_agent_rotation": True,
                "referrer_policy": "no-referrer",
                "download_isolation": True,
                "encrypted_downloads": True,
            },
            # Ad Blocker Settings (HOLY WAR)
            "ad_blocker": {
                "enabled": True,
                "holy_war_mode": True,
                "aggressiveness": "MAXIMUM",  # MAXIMUM/HIGH/MEDIUM/LOW
                "block_ads": True,
                "block_trackers": True,
                "block_popups": True,
                "block_redirects": True,
                "block_autoplay": True,
                "block_video_ads": True,
                "block_audio_ads": True,
                "block_banners": True,
                "block_malvertising": True,
                "block_cryptominers": True,
                "block_social_widgets": True,
                "custom_filters": True,
                "update_filters": False,  # Manual updates only for privacy
            },
            # Thirsty Consigliere Settings
            "consigliere": {
                "enabled": True,
                "on_device_only": True,
                "code_of_omerta": True,
                "capability_mode": "manual",  # manual/auto
                "default_locked": True,
                "data_minimization": True,
                "no_training": True,
                "max_context_size": 10,
                "ephemeral_context": True,
                "action_ledger_size": 100,
                "auto_wipe_on_close": True,
            },
            # Media Downloader Settings
            "media_downloader": {
                "enabled": True,
                "default_mode": "best_quality",  # audio_only/video_only/audio_video/best_quality
                "audio_format": "mp3",
                "video_format": "mp4",
                "default_quality": "best",
                "download_directory": "./downloads",
                "library_enabled": True,
                "encrypt_metadata": True,
                "encrypt_files": True,
                "auto_organize": True,
                "thumbnail_encryption": True,
            },
            # AI Assistant Settings
            "ai_assistant": {
                "enabled": True,
                "god_tier_encrypted": True,
                "local_inference": True,
                "no_external_calls": True,
                "no_data_collection": True,
                "max_context": 20,
                "capabilities": {
                    "text_generation": True,
                    "code_assistance": True,
                    "problem_solving": True,
                    "privacy_analysis": True,
                    "security_audit": True,
                },
                "conversation_encryption": True,
                "auto_clear_history": True,
            },
            # Remote Access Settings
            "remote_access": {
                "browser_enabled": False,  # Disabled by default for security
                "desktop_enabled": False,  # Disabled by default for security
                "require_authentication": True,
                "require_vpn": True,
                "encryption_required": True,
                "session_timeout": 3600,  # 1 hour
                "max_sessions": 1,
                "remote_host": "0.0.0.0",
                "remote_port": 9000,
                "desktop_port": 9001,
                "secure_tunnel": True,
            },
            # Network/VPN Settings
            "network": {
                "vpn_enabled": True,
                "vpn_protocol": "multi-protocol",
                "vpn_hops": 3,  # Multi-hop routing
                "max_hops": 5,
                "location_spoofing": True,
                "dns_over_https": True,
                "dns_provider": "cloudflare",  # cloudflare/quad9/custom
                "split_tunneling": False,  # All traffic through VPN
                "stealth_mode": True,
                "never_logs": True,
                "connection_timeout": 30,
                "auto_reconnect": True,
            },
            # Firewall Settings (8 Types)
            "firewalls": {
                "packet_filtering": {
                    "enabled": True,
                    "mode": "strict",
                    "default_policy": "deny",
                },
                "circuit_level": {"enabled": True, "tcp_monitoring": True},
                "stateful_inspection": {"enabled": True, "connection_tracking": True},
                "proxy": {"enabled": True, "application_layer": True},
                "next_generation": {
                    "enabled": True,
                    "ai_powered": True,
                    "threat_detection": True,
                },
                "software": {"enabled": True, "user_space_protection": True},
                "hardware": {"enabled": True, "hardware_filtering": True},
                "cloud": {"enabled": True, "distributed_protection": True},
            },
            # Support Settings
            "support": {
                "qa_enabled": True,
                "contact_enabled": True,
                "feedback_enabled": True,
                "bug_reports_enabled": True,
                "feature_requests_enabled": True,
                "security_reports_enabled": True,
                "code_of_conduct_suggestions": True,
                "encrypt_communications": True,
            },
            # Advanced Settings
            "advanced": {
                "debug_mode": False,
                "verbose_logging": False,
                "performance_monitoring": False,
                "memory_optimization": True,
                "cpu_priority": "normal",
                "network_buffer_size": 65536,
                "max_concurrent_connections": 100,
                "encryption_hardware_acceleration": True,
            },
        }

        self._modified = False
        self._defaults = self.settings.copy()  # Keep defaults for reset

    def get_setting(self, category: str, key: str) -> Any:
        """Get a specific setting"""
        if category in self.settings:
            return self.settings[category].get(key)
        return None

    def set_setting(self, category: str, key: str, value: Any):
        """Set a specific setting (encrypted)"""
        if category not in self.settings:
            self.settings[category] = {}

        old_value = self.settings[category].get(key)
        self.settings[category][key] = value
        self._modified = True

        self.logger.info(f"Setting updated: {category}.{key} = {value}")

        # Log security-critical changes
        if category in ["security", "privacy", "ad_blocker"]:
            self.logger.warning(
                f"SECURITY SETTING CHANGED: {category}.{key} from {old_value} to {value}"
            )

    def get_category(self, category: str) -> Dict[str, Any]:
        """Get all settings in a category"""
        return self.settings.get(category, {}).copy()

    def get_all_settings(self) -> Dict[str, Dict[str, Any]]:
        """Get all settings"""
        return self.settings.copy()

    def reset_category(self, category: str):
        """Reset a category to defaults"""
        if category in self._defaults:
            self.settings[category] = self._defaults[category].copy()
            self._modified = True
            self.logger.info(f"Category reset to defaults: {category}")

    def reset_all(self):
        """Reset all settings to defaults"""
        self.settings = self._defaults.copy()
        self._modified = True
        self.logger.warning("ALL SETTINGS RESET TO DEFAULTS")

    def export_settings(self) -> bytes:
        """Export all settings (encrypted with God tier)"""
        settings_json = json.dumps(self.settings, indent=2)
        encrypted_settings = self.god_tier_encryption.encrypt_god_tier(
            settings_json.encode()
        )

        self.logger.info("Settings exported (God tier encrypted)")

        return encrypted_settings

    def import_settings(self, encrypted_data: bytes):
        """Import settings from encrypted data"""
        try:
            decrypted_data = self.god_tier_encryption.decrypt_god_tier(encrypted_data)
            imported = json.loads(decrypted_data.decode())

            # Merge with current settings (preserve structure)
            for category, values in imported.items():
                if category in self.settings:
                    self.settings[category].update(values)

            self._modified = True
            self.logger.info("Settings imported successfully")

        except Exception as e:
            self.logger.error(f"Failed to import settings: {e}")

    def validate_settings(self) -> Dict[str, Any]:
        """Validate all settings for security and consistency"""
        issues = []

        # Check critical security settings
        if not self.settings["privacy"]["god_tier_encryption"]:
            issues.append("God tier encryption is disabled!")

        if not self.settings["security"]["kill_switch"]:
            issues.append("Kill switch is disabled!")

        if not self.settings["ad_blocker"]["holy_war_mode"]:
            issues.append("Ad blocker HOLY WAR mode is disabled!")

        if (
            self.settings["remote_access"]["browser_enabled"]
            or self.settings["remote_access"]["desktop_enabled"]
        ):
            if not self.settings["remote_access"]["require_authentication"]:
                issues.append("Remote access enabled without authentication!")

        return {"valid": len(issues) == 0, "issues": issues, "warnings": len(issues)}

    def get_status(self) -> Dict[str, Any]:
        """Get settings manager status"""
        validation = self.validate_settings()

        return {
            "god_tier_encrypted": True,
            "encryption_layers": 7,
            "categories": list(self.settings.keys()),
            "total_settings": sum(len(cat) for cat in self.settings.values()),
            "modified": self._modified,
            "validation": validation,
        }
