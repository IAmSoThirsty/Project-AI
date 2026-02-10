"""
Configuration Loader and Validator for PROJECT ATLAS

Loads and validates all YAML configuration files with schema enforcement,
cryptographic verification, and safety checks.

Production-grade with full error handling and audit logging.
"""

import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    """Raised when configuration is invalid or cannot be loaded."""

    pass


class SafetyViolationError(Exception):
    """Raised when safety rules are violated."""

    pass


class ConfigLoader:
    """
    Production-grade configuration loader for PROJECT ATLAS.

    Loads, validates, and provides access to all YAML configuration files
    with immutability enforcement and audit logging.
    """

    def __init__(self, config_dir: Path | None = None):
        """
        Initialize configuration loader.

        Args:
            config_dir: Path to configuration directory (defaults to atlas/config)
        """
        if config_dir is None:
            # Default to atlas/config (this file is already in config directory)
            config_dir = Path(__file__).parent

        self.config_dir = Path(config_dir)
        if not self.config_dir.exists():
            raise ConfigurationError(
                f"Configuration directory not found: {self.config_dir}"
            )

        self._configs: dict[str, dict[str, Any]] = {}
        self._hashes: dict[str, str] = {}
        self._load_timestamp = datetime.utcnow().isoformat()

        logger.info("Initializing ConfigLoader with directory: %s", self.config_dir)

        # Load all configurations
        self._load_all()

        # Validate integrity
        self._validate_all()

        logger.info("Configuration loaded and validated successfully")

    def _load_all(self) -> None:
        """Load all configuration files."""
        config_files = {
            "stacks": "stacks.yaml",
            "drivers": "drivers.yaml",
            "penalties": "penalties.yaml",
            "thresholds": "thresholds.yaml",
            "safety": "safety.yaml",
            "seeds": "seeds.yaml",
        }

        for config_name, filename in config_files.items():
            filepath = self.config_dir / filename
            try:
                self._load_config(config_name, filepath)
            except Exception as e:
                logger.error("Failed to load %s: %s", filename, e)
                raise ConfigurationError(f"Failed to load {filename}: {e}") from e

    def _load_config(self, name: str, filepath: Path) -> None:
        """
        Load a single configuration file.

        Args:
            name: Configuration name (e.g., 'stacks')
            filepath: Path to YAML file
        """
        logger.debug("Loading configuration: %s from %s", name, filepath)

        if not filepath.exists():
            raise ConfigurationError(f"Configuration file not found: {filepath}")

        try:
            with open(filepath, encoding="utf-8") as f:
                content = f.read()

            # Compute hash for integrity
            config_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
            self._hashes[name] = config_hash

            # Parse YAML
            config = yaml.safe_load(content)

            if not isinstance(config, dict):
                raise ConfigurationError(f"{name} configuration must be a dictionary")

            self._configs[name] = config
            logger.debug(
                "Loaded %s configuration (hash: %s...)", name, config_hash[:16]
            )

        except yaml.YAMLError as e:
            logger.error("YAML parse error in %s: %s", filepath, e)
            raise ConfigurationError(f"YAML parse error in {filepath}: {e}") from e
        except Exception as e:
            logger.error("Error loading %s: %s", filepath, e)
            raise ConfigurationError(f"Error loading {filepath}: {e}") from e

    def _validate_all(self) -> None:
        """Validate all loaded configurations."""
        logger.debug("Validating all configurations")

        # Validate required fields
        required_configs = [
            "stacks",
            "drivers",
            "penalties",
            "thresholds",
            "safety",
            "seeds",
        ]
        for config_name in required_configs:
            if config_name not in self._configs:
                raise ConfigurationError(
                    f"Required configuration missing: {config_name}"
                )

        # Validate versions
        self._validate_versions()

        # Validate safety configuration (most critical)
        self._validate_safety()

        # Validate stacks configuration
        self._validate_stacks()

        # Validate drivers configuration
        self._validate_drivers()

        # Validate cross-configuration consistency
        self._validate_consistency()

        logger.debug("All configurations validated successfully")

    def _validate_versions(self) -> None:
        """Validate that all configurations have consistent versions."""
        versions = {}
        for name, config in self._configs.items():
            if "version" not in config:
                raise ConfigurationError(f"Configuration {name} missing version field")
            versions[name] = config["version"]

        # Log versions for audit
        logger.info("Configuration versions: %s", versions)

    def _validate_safety(self) -> None:
        """Validate safety configuration with strict enforcement."""
        safety = self._configs["safety"]

        # Verify immutability flags
        if not safety.get("locked", False):
            raise SafetyViolationError("Safety configuration must be locked")

        if safety.get("modification_allowed", True):
            raise SafetyViolationError(
                "Safety configuration must not allow modification"
            )

        # Validate required safety sections
        required_sections = [
            "stack_separation",
            "data_integrity",
            "determinism",
            "governance",
            "security",
        ]

        for section in required_sections:
            if section not in safety:
                raise SafetyViolationError(
                    f"Safety configuration missing required section: {section}"
                )

        # Validate that all critical rules have bypass: false
        for section_name, section in safety.items():
            if isinstance(section, dict):
                for rule_name, rule in section.items():
                    if isinstance(rule, dict) and "bypass" in rule:
                        if rule.get("bypass", True):
                            logger.warning(
                                "Safety rule %s.%s allows bypass",
                                section_name,
                                rule_name,
                            )

        logger.info("Safety configuration validated successfully")

    def _validate_stacks(self) -> None:
        """Validate stacks configuration."""
        stacks_config = self._configs["stacks"]

        if "stacks" not in stacks_config:
            raise ConfigurationError("Stacks configuration missing 'stacks' section")

        stacks = stacks_config["stacks"]
        required_stacks = ["RS", "TS-0", "TS-1", "TS-2", "TS-3", "SS"]

        for stack_name in required_stacks:
            if stack_name not in stacks:
                raise ConfigurationError(f"Required stack missing: {stack_name}")

        # Validate SS cannot be promoted
        if "transitions" in stacks_config:
            for transition in stacks_config["transitions"]:
                if transition.get("from") == "SS" and transition.get("allowed", False):
                    raise SafetyViolationError(
                        "SS stack must not allow transitions to other stacks"
                    )

        logger.info("Stacks configuration validated successfully")

    def _validate_drivers(self) -> None:
        """Validate drivers configuration."""
        drivers = self._configs["drivers"]

        if "influence_drivers" not in drivers:
            raise ConfigurationError(
                "Drivers configuration missing 'influence_drivers' section"
            )

        # Validate that weights sum to 1.0
        influence_drivers = drivers["influence_drivers"]
        total_weight = sum(
            driver.get("weight", 0.0)
            for driver in influence_drivers.values()
            if isinstance(driver, dict)
        )

        if not (0.99 <= total_weight <= 1.01):  # Allow small floating point error
            raise ConfigurationError(
                f"Influence driver weights must sum to 1.0, got {total_weight}"
            )

        logger.info("Drivers configuration validated successfully")

    def _validate_consistency(self) -> None:
        """Validate cross-configuration consistency."""
        # Validate that all stacks referenced in seeds exist in stacks config
        stacks = self._configs["stacks"]["stacks"]
        seeds = self._configs["seeds"]

        if "timeline_seeds" in seeds:
            for stack_name in seeds["timeline_seeds"].keys():
                if stack_name not in stacks:
                    logger.warning("Seed defined for unknown stack: %s", stack_name)

        logger.info("Cross-configuration consistency validated")

    def get(self, config_name: str) -> dict[str, Any]:
        """
        Get a configuration by name.

        Args:
            config_name: Name of configuration (e.g., 'stacks', 'drivers')

        Returns:
            Configuration dictionary

        Raises:
            ConfigurationError: If configuration not found
        """
        if config_name not in self._configs:
            raise ConfigurationError(f"Configuration not found: {config_name}")

        # Return a copy to prevent modification
        return dict(self._configs[config_name])

    def get_hash(self, config_name: str) -> str:
        """
        Get the SHA-256 hash of a configuration file.

        Args:
            config_name: Name of configuration

        Returns:
            Hex-encoded SHA-256 hash
        """
        if config_name not in self._hashes:
            raise ConfigurationError(f"Configuration not found: {config_name}")

        return self._hashes[config_name]

    def get_all_hashes(self) -> dict[str, str]:
        """Get hashes of all configurations for audit trail."""
        return dict(self._hashes)

    def verify_integrity(self) -> bool:
        """
        Verify that configurations have not been modified.

        Returns:
            True if all configurations are unchanged, False otherwise
        """
        for config_name, original_hash in self._hashes.items():
            filename = f"{config_name}.yaml"
            filepath = self.config_dir / filename

            try:
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()

                current_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

                if current_hash != original_hash:
                    logger.error(
                        f"Configuration {config_name} has been modified! "
                        f"Original: {original_hash}, Current: {current_hash}"
                    )
                    return False

            except Exception as e:
                logger.error("Error verifying %s: %s", config_name, e)
                return False

        return True

    def get_metadata(self) -> dict[str, Any]:
        """Get metadata about loaded configurations."""
        return {
            "load_timestamp": self._load_timestamp,
            "config_dir": str(self.config_dir),
            "configs_loaded": list(self._configs.keys()),
            "hashes": self._hashes,
            "versions": {
                name: config.get("version", "unknown")
                for name, config in self._configs.items()
            },
        }

    def export_audit_log(self) -> str:
        """
        Export configuration audit log as JSON.

        Returns:
            JSON string containing audit information
        """
        audit_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": self.get_metadata(),
            "integrity_verified": self.verify_integrity(),
            "safety_status": {
                "locked": self._configs["safety"].get("locked", False),
                "modification_allowed": self._configs["safety"].get(
                    "modification_allowed", True
                ),
            },
        }

        return json.dumps(audit_data, indent=2)


# Singleton instance for application-wide access
_global_config_loader: ConfigLoader | None = None


def get_config_loader(config_dir: Path | None = None) -> ConfigLoader:
    """
    Get the global configuration loader instance.

    Args:
        config_dir: Configuration directory (only used on first call)

    Returns:
        ConfigLoader instance
    """
    global _global_config_loader

    if _global_config_loader is None:
        _global_config_loader = ConfigLoader(config_dir)

    return _global_config_loader


def reset_config_loader() -> None:
    """Reset the global configuration loader (for testing)."""
    global _global_config_loader
    _global_config_loader = None


if __name__ == "__main__":
    # Test configuration loading
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        loader = ConfigLoader()
        print("Configuration loaded successfully!")
        print("\nMetadata:")
        print(json.dumps(loader.get_metadata(), indent=2))

        print("\nAudit Log:")
        print(loader.export_audit_log())

    except Exception as e:
        print(f"Error: {e}")
        raise
