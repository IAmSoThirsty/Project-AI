"""
cerberus.security.modules.input_validation — Attack-vector detection.

Ported from upstream ``IAmSoThirsty/Cerberus``
``src/cerberus/security/modules/input_validation.py``. Pure-stdlib detection
and sanitization for SQLi, XSS, command/LDAP/NoSQL injection, path traversal,
XXE, and AI-specific prompt-injection / jailbreak patterns.
"""

from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar


class AttackType(Enum):
    """Types of detected attacks."""

    XXE = "XXE"
    SQLI = "SQL_INJECTION"
    XSS = "CROSS_SITE_SCRIPTING"
    COMMAND_INJECTION = "COMMAND_INJECTION"
    PATH_TRAVERSAL = "PATH_TRAVERSAL"
    LDAP_INJECTION = "LDAP_INJECTION"
    NOSQL_INJECTION = "NOSQL_INJECTION"
    PROMPT_INJECTION = "PROMPT_INJECTION"
    JAILBREAK = "JAILBREAK"
    NONE = "NONE"


@dataclass
class ValidationResult:
    """Result of input validation."""

    is_valid: bool
    attack_type: AttackType
    confidence: float  # 0.0 to 1.0
    details: str
    sanitized_input: str | None = None
    patterns_matched: list[str] = field(default_factory=list)


class InputValidator:
    """Validates and sanitizes inputs to detect and prevent common attacks."""

    SQL_PATTERNS: ClassVar[list[str]] = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b.*?=.*?)",
        r"(\bAND\b.*?=.*?)",
        r"(\bUNION\b.*?\bSELECT\b)",
        r"('(\s*OR\s*'?\d*'?\s*=\s*'?\d*))",
    ]

    XSS_PATTERNS: ClassVar[list[str]] = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe",
        r"<object",
        r"<embed",
        r"<applet",
        r"onerror\s*=",
        r"onload\s*=",
    ]

    COMMAND_PATTERNS: ClassVar[list[str]] = [
        r"[;&|`$]",
        r"\$\(.*?\)",
        r"`.*?`",
        r"&&",
        r"\|\|",
        r">\s*/",
    ]

    PATH_TRAVERSAL_PATTERNS: ClassVar[list[str]] = [
        r"\.\./",
        r"\.\./\.\./",
        r"%2e%2e/",
        r"\.\.\\",
        r"%5c%5c",
    ]

    # SYSTEM/PUBLIC are bound to their XML external-identifier context
    # (keyword followed by a quoted identifier); upstream matched the bare
    # words case-insensitively, which blocked ordinary prose containing
    # "system" or "public" as XXE.
    XXE_PATTERNS: ClassVar[list[str]] = [
        r"<!ENTITY",
        r"<!DOCTYPE",
        r"\bSYSTEM\s+[\"']",
        r"\bPUBLIC\s+[\"']",
    ]

    LDAP_PATTERNS: ClassVar[list[str]] = [
        r"\*",
        r"\(",
        r"\)",
        r"&",
        r"\|",
        r"!",
    ]

    NOSQL_PATTERNS: ClassVar[list[str]] = [
        r"\$gt",
        r"\$lt",
        r"\$ne",
        r"\$where",
        r"\$regex",
    ]

    # Optional all/previous groups so common phrasings ("ignore all previous
    # instructions") match — upstream's `(previous|all)` form missed them.
    PROMPT_INJECTION_PATTERNS: ClassVar[list[str]] = [
        r"ignore\s+(?:all\s+)?(?:previous\s+)?instructions?",
        r"disregard\s+(?:all\s+)?(?:previous\s+)?(?:instructions?|rules|guidelines)",
        r"forget\s+(everything|all)\s+(you|your)",
        r"new\s+instructions",
        r"system\s+prompt",
        r"override\s+",
    ]

    JAILBREAK_PATTERNS: ClassVar[list[str]] = [
        r"pretend\s+you\s+are",
        r"act\s+as\s+if",
        r"roleplay\s+as",
        r"do\s+anything\s+now",
        r"DAN\s+mode",
        r"developer\s+mode",
        r"sudo\s+",
    ]

    def __init__(self) -> None:
        """Initialize the input validator and compile all patterns."""
        self.compiled_sql = self._compile(self.SQL_PATTERNS)
        self.compiled_xss = self._compile(self.XSS_PATTERNS)
        self.compiled_command = self._compile(self.COMMAND_PATTERNS)
        self.compiled_path = self._compile(self.PATH_TRAVERSAL_PATTERNS)
        self.compiled_xxe = self._compile(self.XXE_PATTERNS)
        self.compiled_ldap = self._compile(self.LDAP_PATTERNS)
        self.compiled_nosql = self._compile(self.NOSQL_PATTERNS)
        self.compiled_prompt = self._compile(self.PROMPT_INJECTION_PATTERNS)
        self.compiled_jailbreak = self._compile(self.JAILBREAK_PATTERNS)

    @staticmethod
    def _compile(patterns: list[str]) -> list[re.Pattern[str]]:
        return [re.compile(p, re.IGNORECASE) for p in patterns]

    def validate(self, input_data: str | dict[str, object] | list[object]) -> ValidationResult:
        """Validate input data for various attack vectors."""
        if isinstance(input_data, dict):
            input_str = json.dumps(input_data)
        elif isinstance(input_data, list):
            input_str = " ".join(str(item) for item in input_data)
        else:
            input_str = str(input_data)

        checks: list[tuple[list[re.Pattern[str]], AttackType, int]] = [
            (self.compiled_sql, AttackType.SQLI, 1),
            (self.compiled_xss, AttackType.XSS, 1),
            (self.compiled_command, AttackType.COMMAND_INJECTION, 1),
            (self.compiled_path, AttackType.PATH_TRAVERSAL, 1),
            (self.compiled_xxe, AttackType.XXE, 1),
            (self.compiled_ldap, AttackType.LDAP_INJECTION, 3),
            (self.compiled_nosql, AttackType.NOSQL_INJECTION, 1),
            (self.compiled_prompt, AttackType.PROMPT_INJECTION, 1),
            (self.compiled_jailbreak, AttackType.JAILBREAK, 1),
        ]

        for compiled, attack_type, min_matches in checks:
            patterns_found = self._match_patterns(compiled, input_str)
            if len(patterns_found) >= min_matches:
                return ValidationResult(
                    is_valid=False,
                    attack_type=attack_type,
                    confidence=self._calculate_confidence(patterns_found),
                    details=f"Detected {attack_type.value} attack patterns",
                    patterns_matched=patterns_found,
                )

        return ValidationResult(
            is_valid=True,
            attack_type=AttackType.NONE,
            confidence=1.0,
            details="Input passed all validation checks",
            sanitized_input=input_str,
        )

    @staticmethod
    def _match_patterns(compiled_patterns: list[re.Pattern[str]], input_str: str) -> list[str]:
        return [pattern.pattern for pattern in compiled_patterns if pattern.search(input_str)]

    @staticmethod
    def _calculate_confidence(patterns_matched: list[str]) -> float:
        base_confidence = 0.6
        pattern_bonus = min(0.4, len(patterns_matched) * 0.1)
        return min(1.0, base_confidence + pattern_bonus)

    def sanitize_html(self, input_str: str) -> str:
        """Sanitize HTML by removing script tags, event handlers, and js: URLs."""
        sanitized = re.sub(r"<script[^>]*>.*?</script>", "", input_str, flags=re.DOTALL)
        sanitized = re.sub(r'on\w+\s*=\s*["\']?[^"\']*["\']?', "", sanitized)
        sanitized = re.sub(r"javascript:", "", sanitized, flags=re.IGNORECASE)
        return sanitized

    def validate_json(self, json_str: str) -> ValidationResult:
        """Validate and parse JSON input, then validate the parsed content."""
        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                attack_type=AttackType.NONE,
                confidence=1.0,
                details=f"Invalid JSON: {e}",
            )
        return self.validate(parsed)

    def validate_xml(self, xml_str: str) -> ValidationResult:
        """Validate XML input with XXE protection."""
        xxe_check = self._match_patterns(self.compiled_xxe, xml_str)
        if xxe_check:
            return ValidationResult(
                is_valid=False,
                attack_type=AttackType.XXE,
                confidence=0.9,
                details="Detected potential XXE attack",
                patterns_matched=xxe_check,
            )

        try:
            # Standard parser with entity expansion disabled (XXE hardening).
            parser = ET.XMLParser()
            ET.fromstring(xml_str, parser=parser)
        except ET.ParseError as e:
            return ValidationResult(
                is_valid=False,
                attack_type=AttackType.NONE,
                confidence=1.0,
                details=f"Invalid XML: {e}",
            )
        return ValidationResult(
            is_valid=True,
            attack_type=AttackType.NONE,
            confidence=1.0,
            details="XML validation passed",
        )

    def validate_csv(self, csv_str: str) -> ValidationResult:
        """Validate CSV input for formula injection (cells starting = + - @)."""
        formula_patterns = [r"^[\s]*=", r"^[\s]*\+", r"^[\s]*-", r"^[\s]*@"]
        for line in csv_str.split("\n"):
            for pattern in formula_patterns:
                if re.match(pattern, line.strip()):
                    return ValidationResult(
                        is_valid=False,
                        attack_type=AttackType.COMMAND_INJECTION,
                        confidence=0.8,
                        details="Detected potential CSV formula injection",
                        patterns_matched=[pattern],
                    )
        return ValidationResult(
            is_valid=True,
            attack_type=AttackType.NONE,
            confidence=1.0,
            details="CSV validation passed",
        )


__all__ = ["AttackType", "InputValidator", "ValidationResult"]
