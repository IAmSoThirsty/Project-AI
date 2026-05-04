"""Input validation agent for data verification.

Validates user inputs, system states, and data integrity before
processing tasks or making decisions.

All validations route through CognitionKernel for governance tracking.
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.cognition_kernel import CognitionKernel, ExecutionType
from app.core.kernel_integration import KernelRoutedAgent

logger = logging.getLogger(__name__)

# Schema registry — field → {type, required, min_len, max_len, allowed}
_SCHEMAS: dict[str, dict[str, dict]] = {
    "governance_request": {
        "domain": {"type": str, "required": True, "max_len": 128},
        "action": {"type": str, "required": True, "max_len": 256},
        "user_id": {"type": str, "required": False, "max_len": 128},
        "payload": {"type": (dict, str), "required": False},
    },
    "execution_context": {
        "domain": {"type": str, "required": True},
        "action": {"type": str, "required": True},
        "context": {"type": dict, "required": True},
    },
    "audit_event": {
        "event_type": {"type": str, "required": True, "max_len": 128},
        "actor": {"type": str, "required": True, "max_len": 128},
        "data": {"type": dict, "required": False},
    },
    "trust_payload": {
        "user_id": {"type": str, "required": True},
        "trust_score": {"type": (int, float), "required": True, "min_val": 0.0, "max_val": 1.0},
    },
}


class ValidatorAgent(KernelRoutedAgent):
    """Validates inputs at the system boundary.

    Accepts named schema references or inline schema dicts. All validation
    operations route through CognitionKernel.
    """

    def __init__(self, kernel: CognitionKernel | None = None) -> None:
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="low",
        )
        self.enabled: bool = True
        self.validators: dict = dict(_SCHEMAS)

    # ------------------------------------------------------------------ public

    def validate(
        self,
        payload: dict[str, Any],
        schema: str | dict[str, dict],
    ) -> tuple[bool, list[str]]:
        """Validate *payload* against *schema*.

        Args:
            payload: The data to validate.
            schema: Either a registered schema name (str) or an inline schema dict.

        Returns:
            (valid, errors) — *valid* is True iff errors is empty.
        """
        return self._execute_through_kernel(
            self._do_validate,
            action_name="ValidatorAgent.validate",
            action_args=(payload, schema),
        )

    def register_schema(self, name: str, schema: dict[str, dict]) -> None:
        """Register a new named schema for reuse."""
        self.validators[name] = schema
        logger.info("ValidatorAgent: registered schema '%s'", name)

    def list_schemas(self) -> list[str]:
        """Return all registered schema names."""
        return list(self.validators.keys())

    # --------------------------------------------------------------- private

    def _do_validate(
        self,
        payload: dict[str, Any],
        schema: str | dict[str, dict],
    ) -> tuple[bool, list[str]]:
        if isinstance(schema, str):
            resolved = self.validators.get(schema)
            if resolved is None:
                return False, [f"Unknown schema: '{schema}'"]
        else:
            resolved = schema

        errors: list[str] = []

        if not isinstance(payload, dict):
            return False, ["Payload must be a dict"]

        for field, rules in resolved.items():
            value = payload.get(field)
            required = rules.get("required", False)

            if value is None:
                if required:
                    errors.append(f"Missing required field: '{field}'")
                continue

            # Type check
            expected_type = rules.get("type")
            if expected_type and not isinstance(value, expected_type):
                type_name = (
                    " | ".join(t.__name__ for t in expected_type)
                    if isinstance(expected_type, tuple)
                    else expected_type.__name__
                )
                errors.append(
                    f"Field '{field}' must be {type_name}, got {type(value).__name__}"
                )
                continue

            # String length constraints
            if isinstance(value, str):
                max_len = rules.get("max_len")
                min_len = rules.get("min_len", 0)
                if max_len is not None and len(value) > max_len:
                    errors.append(f"Field '{field}' exceeds max length {max_len}")
                if len(value) < min_len:
                    errors.append(f"Field '{field}' below min length {min_len}")

            # Numeric range constraints
            if isinstance(value, (int, float)):
                min_val = rules.get("min_val")
                max_val = rules.get("max_val")
                if min_val is not None and value < min_val:
                    errors.append(f"Field '{field}' below minimum {min_val}")
                if max_val is not None and value > max_val:
                    errors.append(f"Field '{field}' above maximum {max_val}")

            # Allowlist constraint
            allowed = rules.get("allowed")
            if allowed is not None and value not in allowed:
                errors.append(f"Field '{field}' value {value!r} not in allowed set")

        valid = len(errors) == 0
        if not valid:
            logger.info("ValidatorAgent: %d validation error(s): %s", len(errors), errors)
        return valid, errors
