"""
Input Validation and Security Hardening for Project-AI.

Provides comprehensive input validation, sanitization, and protection against:
- SQL injection
- XSS (Cross-Site Scripting)
- Command injection
- Path traversal
- NoSQL injection
- LDAP injection
- Header injection
- And other common attack vectors
"""

import html
import logging
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from re import Pattern
from typing import Any
from urllib.parse import unquote

from .exceptions import InjectionDetectedError, InputValidationError

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    """Threat severity levels."""

    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented


@dataclass
class ValidationRule:
    """Input validation rule."""

    name: str
    pattern: Pattern | None = None
    validator: Callable[[str], bool] | None = None
    sanitizer: Callable[[str], str] | None = None
    threat_level: ThreatLevel = ThreatLevel.MEDIUM
    error_message: str = "Validation failed"


@dataclass
class ValidationResult:
    """Result of input validation."""

    is_valid: bool
    original_value: Any
    sanitized_value: Any | None = None
    threats_detected: list[str] = field(default_factory=list)
    threat_level: ThreatLevel = ThreatLevel.NONE
    error_message: str | None = None

    def raise_if_invalid(self) -> None:
        """Raise exception if validation failed."""
        if not self.is_valid:
            if self.threat_level >= ThreatLevel.HIGH:
                raise InjectionDetectedError(
                    self.error_message or "Security threat detected",
                    context={
                        "threats": self.threats_detected,
                        "threat_level": self.threat_level.name,
                        "original_value": str(self.original_value)[:100],
                    },
                )
            else:
                raise InputValidationError(
                    self.error_message or "Input validation failed",
                    context={"threats": self.threats_detected},
                )


class SecurityValidator:
    """
    Comprehensive security validation and sanitization system.

    Protects against common injection attacks and malicious input.
    """

    # SQL Injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bunion\b.*\bselect\b)",
        r"(\bselect\b.*\bfrom\b)",
        r"(\binsert\b.*\binto\b)",
        r"(\bupdate\b.*\bset\b)",
        r"(\bdelete\b.*\bfrom\b)",
        r"(\bdrop\b.*\btable\b)",
        r"(\bexec\b.*\()",
        r"(;.*(-{2}|/\*))",  # Comments
        r"('.*or.*'.*'.*=.*')",  # Classic SQLi
        r"(\bor\b.*\b1\s*=\s*1\b)",
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"onerror\s*=",
        r"onload\s*=",
        r"onclick\s*=",
        r"<iframe[^>]*>",
        r"<embed[^>]*>",
        r"<object[^>]*>",
        r"eval\s*\(",
        r"expression\s*\(",
    ]

    # Command injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|]\s*\w+",  # Command chaining
        r"`[^`]+`",  # Backticks
        r"\$\([^)]+\)",  # Command substitution
        r"\$\{[^}]+\}",  # Variable substitution
        r">\s*/dev/",  # File redirection
        r"<\s*/dev/",
    ]

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",  # Parent directory
        r"\.\./\.\./",  # Multiple parent directories
        r"%2e%2e/",  # URL encoded
        r"\.\.\\",  # Windows paths
    ]

    # NoSQL injection patterns
    NOSQL_INJECTION_PATTERNS = [
        r"\$where",
        r"\$ne",
        r"\$gt",
        r"\$regex",
        r"{\s*\$",
    ]

    # LDAP injection patterns
    LDAP_INJECTION_PATTERNS = [
        r"\(\|",
        r"\(&",
        r"\(!\s*",
        r"\*\)",
    ]

    def __init__(self):
        """Initialize security validator."""
        self._sql_patterns = [re.compile(p, re.IGNORECASE) for p in self.SQL_INJECTION_PATTERNS]
        self._xss_patterns = [re.compile(p, re.IGNORECASE) for p in self.XSS_PATTERNS]
        self._cmd_patterns = [re.compile(p, re.IGNORECASE) for p in self.COMMAND_INJECTION_PATTERNS]
        self._path_patterns = [re.compile(p, re.IGNORECASE) for p in self.PATH_TRAVERSAL_PATTERNS]
        self._nosql_patterns = [re.compile(p, re.IGNORECASE) for p in self.NOSQL_INJECTION_PATTERNS]
        self._ldap_patterns = [re.compile(p, re.IGNORECASE) for p in self.LDAP_INJECTION_PATTERNS]

        logger.info("SecurityValidator initialized with comprehensive threat detection")

    def validate_input(
        self,
        value: Any,
        input_type: str = "generic",
        allow_html: bool = False,
        strict: bool = True,
    ) -> ValidationResult:
        """
        Validate and sanitize input.

        Args:
            value: Input value to validate
            input_type: Type of input (generic, sql, html, path, command)
            allow_html: Whether to allow HTML (with sanitization)
            strict: Whether to use strict validation (reject on any threat)

        Returns:
            ValidationResult
        """
        if value is None:
            return ValidationResult(is_valid=True, original_value=None, sanitized_value=None)

        # Convert to string for validation
        str_value = str(value)
        result = ValidationResult(is_valid=True, original_value=value, sanitized_value=value)

        # Check for SQL injection
        sql_threats = self._check_sql_injection(str_value)
        if sql_threats:
            result.threats_detected.extend(sql_threats)
            result.threat_level = max(result.threat_level, ThreatLevel.CRITICAL)

        # Check for XSS
        if not allow_html:
            xss_threats = self._check_xss(str_value)
            if xss_threats:
                result.threats_detected.extend(xss_threats)
                result.threat_level = max(result.threat_level, ThreatLevel.HIGH)

        # Check for command injection
        cmd_threats = self._check_command_injection(str_value)
        if cmd_threats:
            result.threats_detected.extend(cmd_threats)
            result.threat_level = max(result.threat_level, ThreatLevel.CRITICAL)

        # Check for path traversal
        if input_type in ("path", "generic"):
            path_threats = self._check_path_traversal(str_value)
            if path_threats:
                result.threats_detected.extend(path_threats)
                result.threat_level = max(result.threat_level, ThreatLevel.HIGH)

        # Check for NoSQL injection
        nosql_threats = self._check_nosql_injection(str_value)
        if nosql_threats:
            result.threats_detected.extend(nosql_threats)
            result.threat_level = max(result.threat_level, ThreatLevel.HIGH)

        # Check for LDAP injection
        ldap_threats = self._check_ldap_injection(str_value)
        if ldap_threats:
            result.threats_detected.extend(ldap_threats)
            result.threat_level = max(result.threat_level, ThreatLevel.MEDIUM)

        # Determine if valid
        if strict and result.threats_detected:
            result.is_valid = False
            result.error_message = f"Security threats detected: {', '.join(result.threats_detected)}"
        else:
            # Sanitize the input
            result.sanitized_value = self._sanitize_input(str_value, input_type, allow_html)

        # Log threats
        if result.threats_detected:
            logger.warning(
                f"Security threats detected in input: {result.threats_detected} "
                f"(level={result.threat_level.name}, strict={strict})"
            )

        return result

    def _check_sql_injection(self, value: str) -> list[str]:
        """Check for SQL injection patterns."""
        threats = []
        for pattern in self._sql_patterns:
            if pattern.search(value):
                threats.append(f"SQL injection pattern detected: {pattern.pattern[:50]}")
        return threats

    def _check_xss(self, value: str) -> list[str]:
        """Check for XSS patterns."""
        threats = []
        for pattern in self._xss_patterns:
            if pattern.search(value):
                threats.append(f"XSS pattern detected: {pattern.pattern[:50]}")
        return threats

    def _check_command_injection(self, value: str) -> list[str]:
        """Check for command injection patterns."""
        threats = []
        for pattern in self._cmd_patterns:
            if pattern.search(value):
                threats.append(f"Command injection pattern detected: {pattern.pattern[:50]}")
        return threats

    def _check_path_traversal(self, value: str) -> list[str]:
        """Check for path traversal patterns."""
        threats = []
        for pattern in self._path_patterns:
            if pattern.search(value):
                threats.append(f"Path traversal pattern detected: {pattern.pattern[:50]}")
        return threats

    def _check_nosql_injection(self, value: str) -> list[str]:
        """Check for NoSQL injection patterns."""
        threats = []
        for pattern in self._nosql_patterns:
            if pattern.search(value):
                threats.append(f"NoSQL injection pattern detected: {pattern.pattern[:50]}")
        return threats

    def _check_ldap_injection(self, value: str) -> list[str]:
        """Check for LDAP injection patterns."""
        threats = []
        for pattern in self._ldap_patterns:
            if pattern.search(value):
                threats.append(f"LDAP injection pattern detected: {pattern.pattern[:50]}")
        return threats

    def _sanitize_input(self, value: str, input_type: str, allow_html: bool) -> str:
        """Sanitize input based on type."""
        if input_type == "html" or allow_html:
            return self.sanitize_html(value)
        elif input_type == "path":
            return self.sanitize_path(value)
        elif input_type == "sql":
            return self.sanitize_sql(value)
        else:
            return self.sanitize_generic(value)

    @staticmethod
    def sanitize_html(value: str) -> str:
        """Sanitize HTML to prevent XSS."""
        # Escape HTML entities
        sanitized = html.escape(value)

        # Remove dangerous attributes
        dangerous_attrs = [
            "onclick",
            "onload",
            "onerror",
            "onmouseover",
            "onfocus",
            "onblur",
            "onchange",
            "onsubmit",
        ]
        for attr in dangerous_attrs:
            sanitized = re.sub(f"{attr}\\s*=\\s*[\"'][^\"']*[\"']", "", sanitized, flags=re.IGNORECASE)

        return sanitized

    @staticmethod
    def sanitize_path(value: str) -> str:
        """Sanitize file path to prevent traversal."""
        # Remove parent directory references
        sanitized = value.replace("../", "").replace("..\\", "")

        # Remove URL encoding
        sanitized = unquote(sanitized)

        # Normalize path
        try:
            path = Path(sanitized).resolve()
            return str(path)
        except Exception:
            # If path resolution fails, return sanitized version
            return sanitized

    @staticmethod
    def sanitize_sql(value: str) -> str:
        """Sanitize SQL input (basic - use parameterized queries in production)."""
        # Escape single quotes
        sanitized = value.replace("'", "''")

        # Remove SQL comments
        sanitized = re.sub(r"--.*$", "", sanitized, flags=re.MULTILINE)
        sanitized = re.sub(r"/\*.*?\*/", "", sanitized, flags=re.DOTALL)

        return sanitized

    @staticmethod
    def sanitize_generic(value: str) -> str:
        """Generic sanitization."""
        # Remove null bytes
        sanitized = value.replace("\x00", "")

        # Remove control characters except newline, tab, carriage return
        sanitized = "".join(char for char in sanitized if ord(char) >= 32 or char in "\n\t\r")

        return sanitized

    def validate_email(self, email: str) -> ValidationResult:
        """Validate email address."""
        result = ValidationResult(is_valid=True, original_value=email)

        # Basic email regex
        email_pattern = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

        if not email_pattern.match(email):
            result.is_valid = False
            result.error_message = "Invalid email format"

        # Check for injection attempts
        validation = self.validate_input(email, strict=True)
        if not validation.is_valid:
            result.is_valid = False
            result.threats_detected = validation.threats_detected
            result.threat_level = validation.threat_level
            result.error_message = "Email contains security threats"

        if result.is_valid:
            result.sanitized_value = email.lower().strip()

        return result

    def validate_url(self, url: str, allowed_schemes: list[str] | None = None) -> ValidationResult:
        """Validate URL."""
        result = ValidationResult(is_valid=True, original_value=url)

        if allowed_schemes is None:
            allowed_schemes = ["http", "https"]

        # Basic URL validation
        url_pattern = re.compile(
            r"^(https?://)?"  # Protocol (optional)
            r"([a-zA-Z0-9.-]+)"  # Domain
            r"(:\d+)?"  # Port (optional)
            r"(/[^\s]*)?$"  # Path (optional)
        )

        if not url_pattern.match(url):
            result.is_valid = False
            result.error_message = "Invalid URL format"
            return result

        # Check scheme
        if url.startswith(("http://", "https://")):
            scheme = url.split("://")[0]
            if scheme not in allowed_schemes:
                result.is_valid = False
                result.error_message = f"URL scheme not allowed: {scheme}"
                return result

        # Check for injection attempts
        validation = self.validate_input(url, strict=True)
        if not validation.is_valid:
            result.is_valid = False
            result.threats_detected = validation.threats_detected
            result.threat_level = validation.threat_level
            result.error_message = "URL contains security threats"

        if result.is_valid:
            result.sanitized_value = url.strip()

        return result

    def validate_json(self, json_str: str, max_depth: int = 10) -> ValidationResult:
        """Validate JSON string."""
        import json

        result = ValidationResult(is_valid=True, original_value=json_str)

        try:
            # Parse JSON
            data = json.loads(json_str)

            # Check depth
            def check_depth(obj, depth=0):
                if depth > max_depth:
                    return False
                if isinstance(obj, dict):
                    return all(check_depth(v, depth + 1) for v in obj.values())
                elif isinstance(obj, list):
                    return all(check_depth(item, depth + 1) for item in obj)
                return True

            if not check_depth(data):
                result.is_valid = False
                result.error_message = f"JSON depth exceeds maximum of {max_depth}"
                return result

            result.sanitized_value = data

        except json.JSONDecodeError as e:
            result.is_valid = False
            result.error_message = f"Invalid JSON: {e}"

        return result


class RateLimiter:
    """
    Token bucket rate limiter for request throttling.
    """

    def __init__(self, rate: float, capacity: float):
        """
        Initialize rate limiter.

        Args:
            rate: Tokens per second
            capacity: Maximum tokens (burst capacity)
        """
        self.rate = rate
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = time.time()
        self._lock = threading.Lock()

    def allow_request(self, cost: float = 1.0) -> bool:
        """
        Check if request is allowed.

        Args:
            cost: Token cost of the request

        Returns:
            True if request is allowed, False otherwise
        """
        import time

        with self._lock:
            now = time.time()
            elapsed = now - self.last_update

            # Add tokens based on elapsed time
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now

            # Check if we have enough tokens
            if self.tokens >= cost:
                self.tokens -= cost
                return True

            return False


# Global singleton instance
_security_validator: SecurityValidator | None = None


def get_security_validator() -> SecurityValidator:
    """Get or create the global security validator instance."""
    global _security_validator

    if _security_validator is None:
        _security_validator = SecurityValidator()

    return _security_validator


def validate_input(value: Any, input_type: str = "generic", strict: bool = True) -> ValidationResult:
    """
    Convenience function to validate input.

    Args:
        value: Input value
        input_type: Type of input
        strict: Whether to use strict validation

    Returns:
        ValidationResult
    """
    validator = get_security_validator()
    return validator.validate_input(value, input_type=input_type, strict=strict)
