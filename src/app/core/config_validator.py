"""
Configuration validation for subsystems and bootstrap configs.
"""

from __future__ import annotations

from dataclasses import dataclass, field

_VALID_PRIORITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}


@dataclass
class ValidationResult:
    is_valid: bool
    validated_config: dict | None = None
    errors: list[str] = field(default_factory=list)


class ConfigValidator:
    def validate_subsystem_config(self, name: str, config: dict) -> ValidationResult:
        errors: list[str] = []
        priority = config.get("priority", "MEDIUM")
        if priority not in _VALID_PRIORITIES:
            errors.append(f"Invalid priority '{priority}' for subsystem '{name}'")
        if errors:
            return ValidationResult(is_valid=False, errors=errors)
        return ValidationResult(is_valid=True, validated_config=dict(config))

    def validate_bootstrap_config(self, config: dict) -> ValidationResult:
        errors: list[str] = []
        for subsystem_name, subsystem_config in config.get("subsystems", {}).items():
            priority = subsystem_config.get("priority", "MEDIUM")
            if priority not in _VALID_PRIORITIES:
                errors.append(
                    f"Invalid priority '{priority}' for subsystem '{subsystem_name}'"
                )
            if "module_path" not in subsystem_config:
                errors.append(f"Missing module_path for '{subsystem_name}'")
            if "class_name" not in subsystem_config:
                errors.append(f"Missing class_name for '{subsystem_name}'")
        if errors:
            return ValidationResult(is_valid=False, errors=errors)
        return ValidationResult(is_valid=True, validated_config=config)
