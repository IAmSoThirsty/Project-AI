"""Configuration file management for Project-AI CLI.

This module provides configuration loading from TOML files, supporting:
- User-specific config: ~/.projectai.toml
- Project-specific config: .projectai.toml (in current directory)
- Environment variable overrides

Configuration priority (highest to lowest):
1. Environment variables
2. Project-specific config (.projectai.toml)
3. User config (~/.projectai.toml)
4. Default values
"""

import os
from pathlib import Path
from typing import Any

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python < 3.11


class Config:
    """Configuration manager for Project-AI."""

    # Default configuration values
    DEFAULTS = {
        "general": {
            "log_level": "INFO",
            "data_dir": "data",
            "verbose": False,
        },
        "ai": {
            "model": "gpt-3.5-turbo",
            "temperature": 0.7,
            "max_tokens": 256,
        },
        "security": {
            "enable_four_laws": True,
            "enable_black_vault": True,
            "enable_audit_log": True,
        },
        "api": {
            "timeout": 30,
            "retry_attempts": 3,
        },
    }

    def __init__(self, config_path: Path | None = None):
        """Initialize configuration.

        Args:
            config_path: Optional path to config file. If not provided,
                        will search in standard locations.
        """
        self.config: dict[str, Any] = {}
        self._load_config(config_path)

    def _load_config(self, config_path: Path | None = None) -> None:
        """Load configuration from file(s).

        Args:
            config_path: Optional path to config file.
        """
        # Start with defaults
        self.config = self.DEFAULTS.copy()

        # Load user config from home directory
        user_config_path = Path.home() / ".projectai.toml"
        if user_config_path.exists():
            self._merge_config(self._read_toml(user_config_path))

        # Load project-specific config from current directory
        project_config_path = Path.cwd() / ".projectai.toml"
        if project_config_path.exists():
            self._merge_config(self._read_toml(project_config_path))

        # Load from specified path if provided
        if config_path and config_path.exists():
            self._merge_config(self._read_toml(config_path))

        # Apply environment variable overrides
        self._apply_env_overrides()

    def _read_toml(self, path: Path) -> dict[str, Any]:
        """Read and parse a TOML file.

        Args:
            path: Path to TOML file.

        Returns:
            Parsed configuration dictionary.
        """
        try:
            with open(path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            print(f"Warning: Failed to read config from {path}: {e}")
            return {}

    def _merge_config(self, new_config: dict[str, Any]) -> None:
        """Merge new configuration into existing config.

        Args:
            new_config: Configuration dictionary to merge.
        """
        for section, values in new_config.items():
            if section not in self.config:
                self.config[section] = {}
            if isinstance(values, dict):
                self.config[section].update(values)
            else:
                self.config[section] = values

    def _apply_env_overrides(self) -> None:
        """Apply environment variable overrides.

        Environment variables should be in the format:
        PROJECTAI_SECTION_KEY=value
        Example: PROJECTAI_GENERAL_LOG_LEVEL=DEBUG
        """
        prefix = "PROJECTAI_"
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Remove prefix and split into section and key
                parts = key[len(prefix) :].lower().split("_", 1)
                if len(parts) == 2:
                    section, config_key = parts
                    if section in self.config:
                        # Try to preserve type
                        if config_key in self.config[section]:
                            original_value = self.config[section][config_key]
                            if isinstance(original_value, bool):
                                value = value.lower() in ("true", "1", "yes")
                            elif isinstance(original_value, int):
                                value = int(value)
                            elif isinstance(original_value, float):
                                value = float(value)
                        self.config[section][config_key] = value

    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get a configuration value.

        Args:
            section: Configuration section name.
            key: Configuration key name.
            default: Default value if key not found.

        Returns:
            Configuration value or default.
        """
        return self.config.get(section, {}).get(key, default)

    def get_section(self, section: str) -> dict[str, Any]:
        """Get entire configuration section.

        Args:
            section: Configuration section name.

        Returns:
            Configuration section dictionary.
        """
        return self.config.get(section, {})


# Global config instance
_config: Config | None = None


def get_config(reload: bool = False) -> Config:
    """Get global configuration instance.

    Args:
        reload: If True, reload configuration from files.

    Returns:
        Global Config instance.
    """
    global _config
    if _config is None or reload:
        _config = Config()
    return _config
