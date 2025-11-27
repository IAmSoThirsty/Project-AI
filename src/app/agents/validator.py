"""Validator agent: performs pre-execution validation checks."""

from typing import Any, Dict, Tuple


class ValidatorAgent:
    """Lightweight validator for actions or items prior to execution.

    The purpose is to provide a single place for quick syntactic or
    policy checks before higher-cost operations are performed.
    """

    def __init__(self) -> None:
        pass

    def validate(self, item: Any, context: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Return (is_valid, reason).

        Currently performs trivial checks (non-empty strings, no disallowed keywords).
        """
        context = context or {}
        if item is None:
            return False, "Validator: Item is None"

        if isinstance(item, str):
            s = item.strip()
            if not s:
                return False, "Validator: Empty string"
            for kw in ("rm -rf", "shutdown", "format "):
                if kw in s.lower():
                    return False, f"Validator: Disallowed substring '{kw}'"

        return True, "Validator: OK"
