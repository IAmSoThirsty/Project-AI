"""
Configuration Validation System for Project-AI.

This module provides comprehensive configuration validation with JSON Schema support,
ensuring all configurations are valid before system initialization.
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft7Validator
    from jsonschema import ValidationError as JSONSchemaValidationError

    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False
    JSONSchemaValidationError = Exception

from .exceptions import ConfigValidationError

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of configuration validation."""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    validated_config: dict[str, Any] | None = None

    def raise_if_invalid(self) -> None:
        """Raise ConfigValidationError if validation failed."""
        if not self.is_valid:
            raise ConfigValidationError(
                f"Configuration validation failed: {', '.join(self.errors)}",
                context={"errors": self.errors, "warnings": self.warnings},
            )


class ConfigValidator:
    """
    Comprehensive configuration validator with schema support.

    Validates configurations against JSON schemas, performs type checking,
    and ensures all required fields are present with valid values.
    """

    def __init__(self, schema_dir: Path | None = None):
        """
        Initialize validator.

        Args:
            schema_dir: Directory containing JSON schema files
        """
        self.schema_dir = (
            schema_dir
            or Path(__file__).parent.parent.parent.parent / "config" / "schemas"
        )
        self._schema_cache: dict[str, dict[str, Any]] = {}

        if not HAS_JSONSCHEMA:
            logger.warning(
                "jsonschema package not installed. Schema validation will use basic checks only. "
                "Install with: pip install jsonschema"
            )

    def validate_subsystem_config(
        self,
        subsystem_id: str,
        config: dict[str, Any],
        schema_name: str | None = None,
    ) -> ValidationResult:
        """
        Validate subsystem configuration.

        Args:
            subsystem_id: Subsystem identifier
            config: Configuration to validate
            schema_name: Optional schema name (defaults to subsystem_id)

        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)

        # Load schema
        schema_name = schema_name or subsystem_id
        schema = self._load_schema(schema_name)

        if schema is None:
            # No schema found, use basic validation
            result.warnings.append(
                f"No schema found for {schema_name}, using basic validation"
            )
            self._basic_validation(config, result)
        else:
            # Use JSON schema validation
            self._schema_validation(config, schema, result)

        # Subsystem-specific validation
        self._validate_subsystem_fields(subsystem_id, config, result)

        if result.is_valid:
            result.validated_config = config

        return result

    def validate_bootstrap_config(self, config: dict[str, Any]) -> ValidationResult:
        """
        Validate bootstrap configuration.

        Args:
            config: Bootstrap configuration

        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)

        # Required top-level fields
        required_fields = ["subsystems"]
        for field in required_fields:
            if field not in config:
                result.is_valid = False
                result.errors.append(f"Missing required field: {field}")

        if "subsystems" in config:
            if not isinstance(config["subsystems"], dict):
                result.is_valid = False
                result.errors.append("'subsystems' must be a dictionary")
            else:
                # Validate each subsystem definition
                for subsystem_id, subsystem_def in config["subsystems"].items():
                    self._validate_subsystem_definition(
                        subsystem_id, subsystem_def, result
                    )

        # Validate optional fields
        if "discovery_paths" in config:
            if not isinstance(config["discovery_paths"], list):
                result.warnings.append("'discovery_paths' should be a list")

        if "failure_mode" in config:
            valid_modes = ["continue", "stop", "rollback"]
            if config["failure_mode"] not in valid_modes:
                result.is_valid = False
                result.errors.append(
                    f"Invalid failure_mode: {config['failure_mode']}. "
                    f"Must be one of: {valid_modes}"
                )

        if result.is_valid:
            result.validated_config = config

        return result

    def _validate_subsystem_definition(
        self, subsystem_id: str, definition: dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate a single subsystem definition."""
        # Required fields for subsystem definition
        required_fields = ["name", "module_path", "class_name"]
        for field in required_fields:
            if field not in definition:
                result.is_valid = False
                result.errors.append(
                    f"Subsystem '{subsystem_id}': Missing required field '{field}'"
                )

        # Validate priority if present
        if "priority" in definition:
            valid_priorities = ["CRITICAL", "HIGH", "NORMAL", "LOW", "BACKGROUND"]
            if definition["priority"] not in valid_priorities:
                result.is_valid = False
                result.errors.append(
                    f"Subsystem '{subsystem_id}': Invalid priority '{definition['priority']}'. "
                    f"Must be one of: {valid_priorities}"
                )

        # Validate dependencies if present
        if "dependencies" in definition:
            if not isinstance(definition["dependencies"], list):
                result.is_valid = False
                result.errors.append(
                    f"Subsystem '{subsystem_id}': 'dependencies' must be a list"
                )

        # Validate config if present
        if "config" in definition:
            if not isinstance(definition["config"], dict):
                result.is_valid = False
                result.errors.append(
                    f"Subsystem '{subsystem_id}': 'config' must be a dictionary"
                )

    def _validate_subsystem_fields(
        self, subsystem_id: str, config: dict[str, Any], result: ValidationResult
    ) -> None:
        """Subsystem-specific field validation."""
        # Add subsystem-specific validation rules here
        # For example, specific fields for certain subsystems

        if subsystem_id.endswith("_engine"):
            # Engine subsystems might require specific fields
            if "timeout" in config and not isinstance(config["timeout"], (int, float)):
                result.is_valid = False
                result.errors.append(
                    f"Subsystem '{subsystem_id}': 'timeout' must be a number"
                )

        if "model" in config:
            # Validate model configurations
            if not isinstance(config["model"], (str, dict)):
                result.is_valid = False
                result.errors.append(
                    f"Subsystem '{subsystem_id}': 'model' must be a string or dict"
                )

    def _load_schema(self, schema_name: str) -> dict[str, Any] | None:
        """Load JSON schema from file."""
        # Check cache first
        if schema_name in self._schema_cache:
            return self._schema_cache[schema_name]

        # Try to load from file
        schema_path = self.schema_dir / f"{schema_name}.schema.json"

        if not schema_path.exists():
            logger.debug(f"Schema file not found: {schema_path}")
            return None

        try:
            with open(schema_path) as f:
                schema = json.load(f)

            self._schema_cache[schema_name] = schema
            logger.debug(f"Loaded schema: {schema_name}")
            return schema

        except Exception as e:
            logger.error(f"Failed to load schema {schema_name}: {e}")
            return None

    def _schema_validation(
        self, config: dict[str, Any], schema: dict[str, Any], result: ValidationResult
    ) -> None:
        """Validate config against JSON schema."""
        if not HAS_JSONSCHEMA:
            result.warnings.append("jsonschema not available, using basic validation")
            self._basic_validation(config, result)
            return

        try:
            validator = Draft7Validator(schema)
            errors = list(validator.iter_errors(config))

            if errors:
                result.is_valid = False
                for error in errors:
                    path = ".".join(str(p) for p in error.path)
                    error_msg = f"{path}: {error.message}" if path else error.message
                    result.errors.append(error_msg)

        except Exception as e:
            logger.error(f"Schema validation error: {e}")
            result.is_valid = False
            result.errors.append(f"Schema validation failed: {e}")

    def _basic_validation(
        self, config: dict[str, Any], result: ValidationResult
    ) -> None:
        """Basic validation without JSON schema."""
        if not isinstance(config, dict):
            result.is_valid = False
            result.errors.append("Configuration must be a dictionary")
            return

        # Basic type checking for common fields
        type_checks = {
            "name": str,
            "version": str,
            "enabled": bool,
            "priority": str,
            "timeout": (int, float),
        }

        for field, expected_type in type_checks.items():
            if field in config:
                if not isinstance(config[field], expected_type):
                    result.is_valid = False
                    type_name = (
                        expected_type.__name__
                        if isinstance(expected_type, type)
                        else str(expected_type)
                    )
                    result.errors.append(f"Field '{field}' must be of type {type_name}")

    def validate_god_tier_config(self, config: dict[str, Any]) -> ValidationResult:
        """
        Validate God Tier configuration.

        Args:
            config: God Tier configuration

        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)

        # Expected top-level sections
        expected_sections = [
            "voice_model",
            "visual_model",
            "camera",
            "conversation",
            "fusion",
            "policy",
            "logging",
            "storage",
        ]

        # Check for required sections (at least some should be present)
        present_sections = [s for s in expected_sections if s in config]
        if not present_sections:
            result.warnings.append(
                f"None of the expected sections found: {expected_sections}"
            )

        # Validate voice_model section
        if "voice_model" in config:
            voice_config = config["voice_model"]
            if "model_name" not in voice_config:
                result.warnings.append("voice_model: missing 'model_name'")

        # Validate visual_model section
        if "visual_model" in config:
            visual_config = config["visual_model"]
            if "model_name" not in visual_config:
                result.warnings.append("visual_model: missing 'model_name'")

        # Validate camera section
        if "camera" in config:
            camera_config = config["camera"]
            if "auto_discover" in camera_config:
                if not isinstance(camera_config["auto_discover"], bool):
                    result.is_valid = False
                    result.errors.append("camera.auto_discover must be a boolean")

        # Validate storage section
        if "storage" in config:
            storage_config = config["storage"]
            if "base_directory" in storage_config:
                if not isinstance(storage_config["base_directory"], str):
                    result.is_valid = False
                    result.errors.append("storage.base_directory must be a string")

        if result.is_valid:
            result.validated_config = config

        return result

    def validate_defense_engine_config(
        self, config: dict[str, Any]
    ) -> ValidationResult:
        """
        Validate Defense Engine configuration (TOML).

        Args:
            config: Defense engine configuration

        Returns:
            ValidationResult with validation status and errors
        """
        result = ValidationResult(is_valid=True)

        # Defense engine should have subsystems
        if "subsystems" not in config:
            result.is_valid = False
            result.errors.append("Missing 'subsystems' section")
            return result

        subsystems = config["subsystems"]
        if not isinstance(subsystems, dict):
            result.is_valid = False
            result.errors.append("'subsystems' must be a dictionary")
            return result

        # Validate each subsystem
        for subsystem_id, subsystem_config in subsystems.items():
            required_fields = ["name", "version", "priority"]
            for field in required_fields:
                if field not in subsystem_config:
                    result.warnings.append(
                        f"Subsystem '{subsystem_id}': missing recommended field '{field}'"
                    )

            # Validate priority if present
            if "priority" in subsystem_config:
                valid_priorities = ["CRITICAL", "HIGH", "NORMAL", "LOW", "BACKGROUND"]
                if subsystem_config["priority"] not in valid_priorities:
                    result.is_valid = False
                    result.errors.append(
                        f"Subsystem '{subsystem_id}': invalid priority. "
                        f"Must be one of: {valid_priorities}"
                    )

        if result.is_valid:
            result.validated_config = config

        return result

    def create_example_schema(
        self, schema_name: str, output_path: Path | None = None
    ) -> dict[str, Any]:
        """
        Create an example JSON schema for a configuration.

        Args:
            schema_name: Name of the schema
            output_path: Optional path to save the schema

        Returns:
            Example schema dictionary
        """
        # Create a basic schema template
        schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": f"{schema_name} Configuration",
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the configuration"},
                "version": {
                    "type": "string",
                    "description": "Version of the configuration",
                },
                "enabled": {
                    "type": "boolean",
                    "description": "Whether this configuration is enabled",
                    "default": True,
                },
                "priority": {
                    "type": "string",
                    "enum": ["CRITICAL", "HIGH", "NORMAL", "LOW", "BACKGROUND"],
                    "description": "Priority level",
                },
                "timeout": {
                    "type": "number",
                    "minimum": 0,
                    "description": "Timeout in seconds",
                },
                "config": {
                    "type": "object",
                    "description": "Additional configuration parameters",
                },
            },
            "required": ["name"],
        }

        if output_path:
            # Ensure directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write schema to file
            with open(output_path, "w") as f:
                json.dump(schema, f, indent=2)

            logger.info(f"Example schema written to: {output_path}")

        return schema


def validate_config(
    config: dict[str, Any], config_type: str = "subsystem", **kwargs
) -> ValidationResult:
    """
    Convenience function to validate configuration.

    Args:
        config: Configuration to validate
        config_type: Type of configuration (subsystem, bootstrap, god_tier, defense_engine)
        **kwargs: Additional arguments passed to validator

    Returns:
        ValidationResult
    """
    validator = ConfigValidator()

    if config_type == "subsystem":
        return validator.validate_subsystem_config(
            subsystem_id=kwargs.get("subsystem_id", "unknown"), config=config
        )
    elif config_type == "bootstrap":
        return validator.validate_bootstrap_config(config)
    elif config_type == "god_tier":
        return validator.validate_god_tier_config(config)
    elif config_type == "defense_engine":
        return validator.validate_defense_engine_config(config)
    else:
        raise ValueError(f"Unknown config type: {config_type}")
