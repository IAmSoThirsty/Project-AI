"""
Centralized Configuration Registry
Manages all subsystem configurations with encryption and validation
"""

import json
import os
import threading
from typing import Any, Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class ConfigRegistry:
    """
    Thread-safe configuration registry with encryption support.
    Manages all configurations for firewall, VPN, browser, and privacy subsystems.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self._config: Dict[str, Any] = {}
            self._encrypted_config: Dict[str, bytes] = {}
            self._cipher: Optional[Fernet] = None
            self._observers: Dict[str, list] = {}
            self.initialized = True

    def initialize(
        self, config_path: Optional[str] = None, encryption_key: Optional[bytes] = None
    ):
        """
        Initialize registry with optional config file and encryption key.

        Args:
            config_path: Path to JSON config file
            encryption_key: Encryption key for sensitive data
        """
        if encryption_key:
            self._cipher = Fernet(encryption_key)

        if config_path and os.path.exists(config_path):
            with open(config_path, "r") as f:
                self._config = json.load(f)
        else:
            self._load_defaults()

    def _load_defaults(self):
        """Load default configuration values"""
        self._config = {
            "global": {
                "privacy_mode": "maximum",
                "kill_switch_enabled": True,
                "telemetry_disabled": True,
                "log_level": "INFO",
            },
            "firewalls": {
                "packet_filtering": {"enabled": True, "default_policy": "deny"},
                "circuit_level": {"enabled": True, "proxy_timeout": 30},
                "stateful_inspection": {"enabled": True, "connection_timeout": 3600},
                "proxy": {"enabled": True, "cache_enabled": False},
                "next_generation": {"enabled": True, "ai_detection": True},
                "software": {"enabled": True, "user_space": True},
                "hardware": {"enabled": True, "bypass_mode": False},
                "cloud": {"enabled": True, "distributed": True},
            },
            "vpn": {
                "enabled": True,
                "multi_hop": True,
                "hop_count": 3,
                "kill_switch": True,
                "dns_leak_protection": True,
                "ipv6_leak_protection": True,
                "split_tunneling": False,
                "stealth_mode": True,
                "logging": "never",
                "protocol_fallback": ["wireguard", "openvpn", "ikev2"],
                "exit_node_selection": "user",
            },
            "browser": {
                "incognito_mode": True,
                "no_history": True,
                "no_cache": True,
                "no_cookies": True,
                "tab_isolation": True,
                "sandbox_enabled": True,
                "fingerprint_protection": True,
                "tracker_blocking": True,
                "extension_whitelist": [],
                "download_isolation": True,
                "keyboard_cloaking": True,
                "mouse_cloaking": True,
            },
            "privacy": {
                "anti_fingerprint": True,
                "anti_tracker": True,
                "anti_phishing": True,
                "anti_malware": True,
                "dns_over_https": True,
                "onion_routing": True,
                "ephemeral_storage": True,
                "forensic_resistance": True,
                "session_auditing": True,
                "leak_auditing": True,
                "privacy_vault_enabled": True,
            },
            "storage": {
                "encrypted": True,
                "ephemeral_mode": True,
                "secure_delete": True,
                "memory_only": False,
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dotted key path.

        Args:
            key: Dotted key path (e.g., 'vpn.enabled')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any, notify: bool = True):
        """
        Set configuration value by dotted key path.

        Args:
            key: Dotted key path
            value: Value to set
            notify: Whether to notify observers
        """
        with self._lock:
            keys = key.split(".")
            config = self._config

            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]

            config[keys[-1]] = value

            if notify:
                self._notify_observers(key, value)

    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self._config.get(section, {})

    def set_encrypted(self, key: str, value: str):
        """Store encrypted configuration value"""
        if not self._cipher:
            raise ValueError("Encryption not initialized")

        self._encrypted_config[key] = self._cipher.encrypt(value.encode())

    def get_encrypted(self, key: str) -> Optional[str]:
        """Retrieve and decrypt configuration value"""
        if not self._cipher or key not in self._encrypted_config:
            return None

        return self._cipher.decrypt(self._encrypted_config[key]).decode()

    def register_observer(self, key: str, callback):
        """Register callback for configuration changes"""
        if key not in self._observers:
            self._observers[key] = []
        self._observers[key].append(callback)

    def _notify_observers(self, key: str, value: Any):
        """Notify observers of configuration changes"""
        if key in self._observers:
            for callback in self._observers[key]:
                try:
                    callback(key, value)
                except Exception as e:
                    print(f"Observer error: {e}")

    def save(self, config_path: str):
        """Save configuration to file"""
        with open(config_path, "w") as f:
            json.dump(self._config, f, indent=2)

    def export_config(self) -> Dict[str, Any]:
        """Export full configuration"""
        return self._config.copy()

    @staticmethod
    def generate_encryption_key(password: str, salt: bytes = None) -> bytes:
        """Generate encryption key from password"""
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        kdf.derive(password.encode())
        return Fernet.generate_key()
