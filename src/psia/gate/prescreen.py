"""
PSIA Pre-Screen Gate — fast O(1) filter before full 7-stage pipeline.

Rejects obviously invalid or prohibited requests before spending resources
on full schema validation, shadow simulation, or Triumvirate evaluation.

This is NOT a security boundary — the full pipeline must still run for
anything that passes pre-screening.  Pre-screening is an efficiency gate.
"""

from __future__ import annotations

from typing import Any

# Absolute prohibitions: any request matching these patterns is rejected
# at the gate with no further processing.  These are the hardest denials.
_ABSOLUTE_DENY_PATTERNS = [
    "disable triumvirate",
    "disable cerberus",
    "disable galahad",
    "jailbreak",
    "ignore fourlaws",
    "rewrite fourlaws",
    "dissolve triumvirate",
    "erase memory",
    "delete audit",
    "format drive",
]


class PreScreenGate:
    """
    Fast pre-screen gate.  Checks the raw dict before Stage 0 ingestion.

    Usage:
        gate = PreScreenGate()
        allowed, reason = gate.check(raw_dict)
        if not allowed:
            raise PermissionError(reason)
    """

    def check(self, raw: Any) -> tuple[bool, str]:
        """
        Returns (allowed: bool, reason: str).
        reason is empty string on allow.
        """
        if not isinstance(raw, dict):
            return False, "pre-screen: input must be a dict"

        text = " ".join(str(v) for v in raw.values()).lower()

        for pattern in _ABSOLUTE_DENY_PATTERNS:
            if pattern in text:
                return False, f"pre-screen: absolute prohibition matched: '{pattern}'"

        # Empty target or action is rejected immediately
        if not str(raw.get("target", "")).strip():
            return False, "pre-screen: empty target"
        if not str(raw.get("action", "")).strip():
            return False, "pre-screen: empty action"

        return True, ""
