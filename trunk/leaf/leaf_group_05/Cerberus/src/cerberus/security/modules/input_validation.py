# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / input_validation.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / input_validation.py


# Date: 2026-03-10 | Time: 20:38 | Status: Active | Tier: Master
"""
Input Validation Module

Secure data ingestion and attack vector detection for:
- XML External Entity (XXE) attacks
- SQL Injection (SQLi)
- Cross-Site Scripting (XSS)
- Command Injection
- Path Traversal
- LDAP Injection
- NoSQL Injection
"""

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from enum import Enum


class AttackType(Enum):
    """Types of detected attacks"""

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
    """Result of input validation"""

    is_valid: bool
    attack_type: AttackType
    confidence: float  # 0.0 to 1.0
    details: str
    sanitized_input: str | None = None
    patterns_matched: list[str] = None

    def __post_init__(self):
        if self.patterns_matched is None:
            self.patterns_matched = []


class InputValidator:
    """
    Validates and sanitizes user inputs to detect and prevent common attacks
    """

    # SQL Injection patterns
    SQL_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\bOR\b.*?=.*?)",
        r"(\bAND\b.*?=.*?)",
        r"(\bUNION\b.*?\bSELECT\b)",
        r"('(\s*OR\s*'?\d*'?\s*=\s*'?\d*))",
    ]

    # XSS patterns
    XSS_PATTERNS = [
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

    # Command Injection patterns
    COMMAND_PATTERNS = [
        r"[;&|`$]",
        r"\$\(.*?\)",
        r"`.*?`",
        r"&&",
        r"\|\|",
        r">\s*/",
    ]

    # Path Traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\./\.\./",
        r"%2e%2e/",
        r"\.\.\\",
        r"%5c%5c",
    ]

    # XXE patterns
    XXE_PATTERNS = [
        r"<!ENTITY",
        r"<!DOCTYPE",
        r"SYSTEM",
        r"PUBLIC",
    ]

    # LDAP Injection patterns
    LDAP_PATTERNS = [
        r"\*",
        r"\(",
        r"\)",
        r"&",
        r"\|",
        r"!",
    ]

    # NoSQL Injection patterns
    NOSQL_PATTERNS = [
        r"\$gt",
        r"\$lt",
        r"\$ne",
        r"\$where",
        r"\$regex",
    ]

    # AI/LLM specific patterns
    PROMPT_INJECTION_PATTERNS = [
        r"ignore\s+(previous|all)\s+instructions",
        r"disregard\s+(previous|all)\s+instructions",
        r"forget\s+(everything|all)\s+(you|your)",
        r"new\s+instructions",
        r"system\s+prompt",
        r"override\s+",
    ]

    JAILBREAK_PATTERNS = [
        r"pretend\s+you\s+are",
        r"act\s+as\s+if",
        r"roleplay\s+as",
        r"do\s+anything\s+now",
        r"DAN\s+mode",
        r"developer\s+mode",
        r"sudo\s+",
    ]

    def __init__(self):
        """Initialize the input validator"""
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile all regex patterns for better performance"""
        self.compiled_sql = [re.compile(p, re.IGNORECASE) for p in self.SQL_PATTERNS]
        self.compiled_xss = [re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS]
        self.compiled_command = [
            re.compile(p, re.IGNORECASE) for p in self.COMMAND_PATTERNS
        ]
        self.compiled_path = [
            re.compile(p, re.IGNORECASE) for p in self.PATH_TRAVERSAL_PATTERNS
        ]
        self.compiled_xxe = [re.compile(p, re.IGNORECASE) for p in self.XXE_PATTERNS]
        self.compiled_ldap = [
            re.compile(p, re.IGNORECASE) for p in self.LDAP_PATTERNS
        ]
        self.compiled_nosql = [
            re.compile(p, re.IGNORECASE) for p in self.NOSQL_PATTERNS
        ]
        self.compiled_prompt = [
            re.compile(p, re.IGNORECASE) for p in self.PROMPT_INJECTION_PATTERNS
        ]
        self.compiled_jailbreak = [
            re.compile(p, re.IGNORECASE) for p in self.JAILBREAK_PATTERNS
        ]

    def validate(self, input_data: str | dict | list) -> ValidationResult:
        """
        Validate input data for various attack vectors

        Args:
            input_data: Input to validate (string, dict, or list)

        Returns:
            ValidationResult with detection details
        """
        # Convert input to string for pattern matching
        if isinstance(input_data, dict):
            input_str = json.dumps(input_data)
        elif isinstance(input_data, list):
            input_str = " ".join(str(item) for item in input_data)
        else:
            input_str = str(input_data)

        # Check for various attack types
        checks = [
            (self._check_sql_injection, AttackType.SQLI),
            (self._check_xss, AttackType.XSS),
            (self._check_command_injection, AttackType.COMMAND_INJECTION),
            (self._check_path_traversal, AttackType.PATH_TRAVERSAL),
            (self._check_xxe, AttackType.XXE),
            (self._check_ldap_injection, AttackType.LDAP_INJECTION),
            (self._check_nosql_injection, AttackType.NOSQL_INJECTION),
            (self._check_prompt_injection, AttackType.PROMPT_INJECTION),
            (self._check_jailbreak, AttackType.JAILBREAK),
        ]

        for check_func, attack_type in checks:
            patterns_found = check_func(input_str)
            if patterns_found:
                return ValidationResult(
                    is_valid=False,
                    attack_type=attack_type,
                    confidence=self._calculate_confidence(patterns_found),
                    details=f"Detected {attack_type.value} attack patterns",
                    patterns_matched=patterns_found,
                )

        # Input is clean
        return ValidationResult(
            is_valid=True,
            attack_type=AttackType.NONE,
            confidence=1.0,
            details="Input passed all validation checks",
            sanitized_input=input_str,
        )

    def _check_sql_injection(self, input_str: str) -> list[str]:
        """Check for SQL injection patterns"""
        return self._match_patterns(self.compiled_sql, input_str)

    def _check_xss(self, input_str: str) -> list[str]:
        """Check for XSS patterns"""
        return self._match_patterns(self.compiled_xss, input_str)

    def _check_command_injection(self, input_str: str) -> list[str]:
        """Check for command injection patterns"""
        return self._match_patterns(self.compiled_command, input_str)

    def _check_path_traversal(self, input_str: str) -> list[str]:
        """Check for path traversal patterns"""
        return self._match_patterns(self.compiled_path, input_str)

    def _check_xxe(self, input_str: str) -> list[str]:
        """Check for XXE patterns"""
        return self._match_patterns(self.compiled_xxe, input_str)

    def _check_ldap_injection(self, input_str: str) -> list[str]:
        """Check for LDAP injection patterns"""
        # LDAP patterns need more context, so we're more lenient
        patterns = self._match_patterns(self.compiled_ldap, input_str)
        # Only flag if multiple patterns found
        return patterns if len(patterns) >= 3 else []

    def _check_nosql_injection(self, input_str: str) -> list[str]:
        """Check for NoSQL injection patterns"""
        return self._match_patterns(self.compiled_nosql, input_str)

    def _check_prompt_injection(self, input_str: str) -> list[str]:
        """Check for AI/LLM prompt injection patterns"""
        return self._match_patterns(self.compiled_prompt, input_str)

    def _check_jailbreak(self, input_str: str) -> list[str]:
        """Check for jailbreak attempt patterns"""
        return self._match_patterns(self.compiled_jailbreak, input_str)

    def _match_patterns(
        self, compiled_patterns: list[re.Pattern], input_str: str
    ) -> list[str]:
        """Match input against compiled patterns"""
        matched = []
        for pattern in compiled_patterns:
            if pattern.search(input_str):
                matched.append(pattern.pattern)
        return matched

    def _calculate_confidence(self, patterns_matched: list[str]) -> float:
        """Calculate confidence score based on number of patterns matched"""
        # More patterns = higher confidence
        base_confidence = 0.6
        pattern_bonus = min(0.4, len(patterns_matched) * 0.1)
        return min(1.0, base_confidence + pattern_bonus)

    def sanitize_html(self, input_str: str) -> str:
        """
        Sanitize HTML input by removing dangerous tags and attributes

        Args:
            input_str: HTML string to sanitize

        Returns:
            Sanitized HTML string
        """
        # Remove script tags
        sanitized = re.sub(r"<script[^>]*>.*?</script>", "", input_str, flags=re.DOTALL)

        # Remove dangerous attributes
        sanitized = re.sub(r'on\w+\s*=\s*["\']?[^"\']*["\']?', "", sanitized)

        # Remove javascript: URLs
        sanitized = re.sub(r"javascript:", "", sanitized, flags=re.IGNORECASE)

        return sanitized

    def validate_json(self, json_str: str) -> ValidationResult:
        """
        Validate and parse JSON input

        Args:
            json_str: JSON string to validate

        Returns:
            ValidationResult
        """
        try:
            parsed = json.loads(json_str)
            # Also validate the parsed content
            return self.validate(parsed)
        except json.JSONDecodeError as e:
            return ValidationResult(
                is_valid=False,
                attack_type=AttackType.NONE,
                confidence=1.0,
                details=f"Invalid JSON: {str(e)}",
            )

    def validate_xml(self, xml_str: str) -> ValidationResult:
        """
        Validate XML input with XXE protection

        Args:
            xml_str: XML string to validate

        Returns:
            ValidationResult
        """
        # First check for XXE patterns
        xxe_check = self._check_xxe(xml_str)
        if xxe_check:
            return ValidationResult(
                is_valid=False,
                attack_type=AttackType.XXE,
                confidence=0.9,
                details="Detected potential XXE attack",
                patterns_matched=xxe_check,
            )

        try:
            # Try to parse with defused XML if available
            try:
                import defusedxml.ElementTree as DefusedET

                DefusedET.fromstring(xml_str)
            except ImportError:
                # Fallback to standard parsing with DTD disabled
                parser = ET.XMLParser()
                parser.entity = {}  # Disable entity expansion
                ET.fromstring(xml_str, parser=parser)

            return ValidationResult(
                is_valid=True,
                attack_type=AttackType.NONE,
                confidence=1.0,
                details="XML validation passed",
            )
        except ET.ParseError as e:
            return ValidationResult(
                is_valid=False,
                attack_type=AttackType.NONE,
                confidence=1.0,
                details=f"Invalid XML: {str(e)}",
            )

    def validate_csv(self, csv_str: str) -> ValidationResult:
        """
        Validate CSV input for formula injection

        Args:
            csv_str: CSV string to validate

        Returns:
            ValidationResult
        """
        # Check for formula injection (CSV formula starts with =, +, -, @)
        formula_patterns = [
            r"^[\s]*=",
            r"^[\s]*\+",
            r"^[\s]*-",
            r"^[\s]*@",
        ]

        lines = csv_str.split("\n")
        for line in lines:
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
