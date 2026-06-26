"""
tarl.parser — TARL text format parser.

Parses TARL text-format specs into typed TARL records. The legacy
`parser.py` used a line-oriented INI-like format with:
- UPPERCASE: section header (e.g. CONSTRAINTS:)
- key: value pairs (lowercase key, any case value)
- Inside CONSTRAINTS section, "- constraint" entries

This is a minimum port: it captures the format invariants and adds
explicit error reporting.

Architectural invariants (AGENTS.md v3):
- Downward-only deps: tarl.parser imports only tarl.core + stdlib.
- Fail-closed: invalid input raises TarlParseError with line context.
- Deterministic: same input → same TARL (canonical()).
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tarl.core import TARL, TARL_VERSION, make_tarl


class TarlParseError(ValueError):
    """Raised when a TARL text spec cannot be parsed."""


ALLOWED_KEYS: frozenset[str] = frozenset({"intent", "scope", "authority", "version"})


def parse(text: str) -> TARL:
    """Parse a TARL text spec into a TARL record.

    Format:
        INTENT: <text>
        SCOPE: <text>
        AUTHORITY: <id>
        VERSION: <version>  (optional, defaults to TARL_VERSION)
        CONSTRAINTS:
            - <constraint1>
            - <constraint2>

    Raises TarlParseError on invalid input.
    """
    if not isinstance(text, str):
        raise TarlParseError(f"text must be str, got {type(text).__name__}")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    data: dict[str, Any] = {"constraints": []}
    in_constraints_section = False
    line_no = 0

    for raw_line in lines:
        line_no += 1
        # Section header: UPPERCASE: with NO value (e.g. "CONSTRAINTS:")
        is_section_header = raw_line.endswith(":") and len(raw_line) > 1 and raw_line[:-1].isupper()
        if is_section_header:
            section_name = raw_line[:-1]
            if section_name == "CONSTRAINTS":
                in_constraints_section = True
                continue
            # Distinguish "INTENT:" (empty value, real key) from "RANDOM:"
            # (unsupported section). Known keys give empty-value error;
            # unknown UPPERCASE words give unsupported-section error.
            if section_name.lower() in ALLOWED_KEYS:
                raise TarlParseError(
                    f"line {line_no}: empty value for key {section_name.lower()!r}"
                )
            raise TarlParseError(f"line {line_no}: unsupported section {section_name!r}")

        # Inside CONSTRAINTS section: "- constraint" entries
        if in_constraints_section and raw_line.startswith("-"):
            constraint = raw_line[1:].strip()
            if not constraint:
                raise TarlParseError(f"line {line_no}: empty constraint")
            data["constraints"].append(constraint)
            continue

        # Outside section: key: value pair
        if ":" not in raw_line:
            raise TarlParseError(f"line {line_no}: missing colon in {raw_line!r}")
        key, value = raw_line.split(":", 1)
        key = key.strip().lower()
        value = value.strip()
        if key not in ALLOWED_KEYS:
            raise TarlParseError(f"line {line_no}: unknown key {key!r}")
        if not value:
            raise TarlParseError(f"line {line_no}: empty value for key {key!r}")
        data[key] = value

    # Validate required keys
    for required in ("intent", "scope", "authority"):
        if required not in data:
            raise TarlParseError(f"missing required key {required!r}")

    version = data.get("version", TARL_VERSION)
    return make_tarl(
        intent=data["intent"],
        scope=data["scope"],
        authority=data["authority"],
        constraints=data["constraints"],
        version=version,
    )


def parse_mapping(mapping: Mapping[str, object]) -> TARL:
    """Parse a TARL from a dict-like input.

    Same validation as parse() but takes a Mapping instead of text.
    """
    intent = mapping.get("intent")
    scope = mapping.get("scope")
    authority = mapping.get("authority")
    constraints = mapping.get("constraints", ())
    version = mapping.get("version", TARL_VERSION)
    if not isinstance(intent, str) or not intent.strip():
        raise TarlParseError("intent must be a non-empty string")
    if not isinstance(scope, str) or not scope.strip():
        raise TarlParseError("scope must be a non-empty string")
    if not isinstance(authority, str) or not authority.strip():
        raise TarlParseError("authority must be a non-empty string")
    if isinstance(constraints, list):
        constraints_list: list[str] = []
        for c in constraints:
            if not isinstance(c, str):
                raise TarlParseError(f"constraints entries must be str, got {type(c).__name__}")
            constraints_list.append(c)
        constraints_tuple: tuple[str, ...] = tuple(constraints_list)
    elif isinstance(constraints, tuple):
        constraints_tuple = constraints
    else:
        raise TarlParseError(
            f"constraints must be tuple or list of str, got {type(constraints).__name__}"
        )
    if not isinstance(version, str) or not version.strip():
        raise TarlParseError("version must be a non-empty string")
    return make_tarl(
        intent=intent,
        scope=scope,
        authority=authority,
        constraints=constraints_tuple,
        version=version,
    )


def format_tarl(record: TARL) -> str:
    """Format a TARL record as text (inverse of parse)."""
    lines = [
        f"INTENT: {record.intent}",
        f"SCOPE: {record.scope}",
        f"AUTHORITY: {record.authority}",
    ]
    if record.version != TARL_VERSION:
        lines.append(f"VERSION: {record.version}")
    if record.constraints:
        lines.append("CONSTRAINTS:")
        for c in record.constraints:
            lines.append(f"  - {c}")
    return "\n".join(lines) + "\n"


__all__ = [
    "ALLOWED_KEYS",
    "TarlParseError",
    "format_tarl",
    "parse",
    "parse_mapping",
]
