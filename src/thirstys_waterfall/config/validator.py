"""Configuration validation and schema enforcement"""

from typing import Any, Dict, List
import re


class ConfigValidator:
    """Validates configuration against schema and security requirements"""

    REQUIRED_SECTIONS = ["global", "firewalls", "vpn", "browser", "privacy", "storage"]

    VALID_PRIVACY_MODES = ["maximum", "high", "medium", "low"]
    VALID_LOG_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    VALID_VPN_PROTOCOLS = ["wireguard", "openvpn", "ikev2", "ipsec"]

    @staticmethod
    def validate(config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate configuration structure and values.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required sections
        for section in ConfigValidator.REQUIRED_SECTIONS:
            if section not in config:
                errors.append(f"Missing required section: {section}")

        # Validate global settings
        if "global" in config:
            errors.extend(ConfigValidator._validate_global(config["global"]))

        # Validate firewall settings
        if "firewalls" in config:
            errors.extend(ConfigValidator._validate_firewalls(config["firewalls"]))

        # Validate VPN settings
        if "vpn" in config:
            errors.extend(ConfigValidator._validate_vpn(config["vpn"]))

        # Validate browser settings
        if "browser" in config:
            errors.extend(ConfigValidator._validate_browser(config["browser"]))

        # Validate privacy settings
        if "privacy" in config:
            errors.extend(ConfigValidator._validate_privacy(config["privacy"]))

        return len(errors) == 0, errors

    @staticmethod
    def _validate_global(config: Dict[str, Any]) -> List[str]:
        """Validate global configuration"""
        errors = []

        if "privacy_mode" in config:
            if config["privacy_mode"] not in ConfigValidator.VALID_PRIVACY_MODES:
                errors.append(f"Invalid privacy_mode: {config['privacy_mode']}")

        if "log_level" in config:
            if config["log_level"] not in ConfigValidator.VALID_LOG_LEVELS:
                errors.append(f"Invalid log_level: {config['log_level']}")

        return errors

    @staticmethod
    def _validate_firewalls(config: Dict[str, Any]) -> List[str]:
        """Validate firewall configurations"""
        errors = []

        required_types = [
            "packet_filtering",
            "circuit_level",
            "stateful_inspection",
            "proxy",
            "next_generation",
            "software",
            "hardware",
            "cloud",
        ]

        for fw_type in required_types:
            if fw_type not in config:
                errors.append(f"Missing firewall type: {fw_type}")

        return errors

    @staticmethod
    def _validate_vpn(config: Dict[str, Any]) -> List[str]:
        """Validate VPN configuration"""
        errors = []

        if "hop_count" in config:
            if not isinstance(config["hop_count"], int) or config["hop_count"] < 1:
                errors.append("hop_count must be positive integer")

        if "protocol_fallback" in config:
            for protocol in config["protocol_fallback"]:
                if protocol not in ConfigValidator.VALID_VPN_PROTOCOLS:
                    errors.append(f"Invalid VPN protocol: {protocol}")

        return errors

    @staticmethod
    def _validate_browser(config: Dict[str, Any]) -> List[str]:
        """Validate browser configuration"""
        errors = []

        # Browser should have no persistent storage in maximum privacy mode
        if config.get("incognito_mode") and (
            config.get("no_history") is False
            or config.get("no_cache") is False
            or config.get("no_cookies") is False
        ):
            errors.append(
                "Incognito mode requires no_history, no_cache, and no_cookies"
            )

        return errors

    @staticmethod
    def _validate_privacy(config: Dict[str, Any]) -> List[str]:
        """Validate privacy configuration"""
        errors = []

        # Privacy-first: certain features must be enabled
        required_features = ["anti_fingerprint", "anti_tracker", "dns_over_https"]

        for feature in required_features:
            if feature in config and not config[feature]:
                errors.append(f"Privacy-first mode requires {feature} to be enabled")

        return errors

    @staticmethod
    def validate_ip_address(ip: str) -> bool:
        """Validate IPv4 or IPv6 address"""
        ipv4_pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
        ipv6_pattern = r"^([0-9a-fA-F]{0,4}:){7}[0-9a-fA-F]{0,4}$"

        return bool(re.match(ipv4_pattern, ip) or re.match(ipv6_pattern, ip))

    @staticmethod
    def validate_port(port: int) -> bool:
        """Validate port number"""
        return 1 <= port <= 65535
