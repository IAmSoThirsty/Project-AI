"""
Security input validation: injection detection, sanitization, email/URL validation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class ValidationResult:
    is_valid: bool
    threats_detected: list[str] = field(default_factory=list)
    sanitized_value: str | None = None
    errors: list[str] = field(default_factory=list)


_SQL_RE = re.compile(
    r"(?i)(('\s*--)|(OR\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w)|(UNION\s+SELECT)"
    r"|(DROP\s+TABLE)|(INSERT\s+INTO)|(DELETE\s+FROM)|(;\s*DROP))"
)
_XSS_RE = re.compile(r"(?i)(<script|javascript\s*:|on\w+\s*=)")
_CMD_RE = re.compile(r"[;&|`$]|\brm\s+-rf\b")
_PATH_RE = re.compile(r"\.\.[/\\]")
_EMAIL_RE = re.compile(r"^[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}$")
_SAFE_SCHEMES = {"http", "https", "ftp"}


class SecurityValidator:
    def validate_input(
        self,
        value: str,
        strict: bool = True,
        input_type: str = "text",
        allow_html: bool = False,
    ) -> ValidationResult:
        threats: list[str] = []

        if _SQL_RE.search(value):
            threats.append("SQL injection detected")

        if not allow_html and _XSS_RE.search(value):
            threats.append("XSS detected")

        if _CMD_RE.search(value):
            threats.append("Command injection detected")

        if input_type == "path" and _PATH_RE.search(value):
            threats.append("Path traversal detected")

        if threats:
            return ValidationResult(is_valid=False, threats_detected=threats)

        return ValidationResult(is_valid=True, sanitized_value=value)

    def validate_email(self, value: str) -> ValidationResult:
        if _EMAIL_RE.match(value):
            return ValidationResult(is_valid=True, sanitized_value=value.lower())
        return ValidationResult(is_valid=False, errors=["Invalid email format"])

    def validate_url(self, value: str) -> ValidationResult:
        try:
            parsed = urlparse(value)
            if parsed.scheme.lower() not in _SAFE_SCHEMES:
                return ValidationResult(
                    is_valid=False,
                    errors=[f"Unsafe URL scheme: {parsed.scheme}"],
                )
            return ValidationResult(is_valid=True, sanitized_value=value)
        except Exception:
            return ValidationResult(is_valid=False, errors=["Invalid URL"])
