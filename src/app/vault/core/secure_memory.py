"""
Secure memory utilities: wipe-on-free buffers and log sanitization.
"""

from __future__ import annotations

import re


class SecureMemory:
    """Provides secure buffer allocation and zero-wipe operations."""

    def disable_core_dumps(self) -> None:
        """Disable OS core dumps so plaintext key material never hits disk."""
        try:
            import resource  # Unix only
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        except (ImportError, AttributeError, ValueError):
            pass  # Windows or restricted environment — skip silently

    def secure_wipe(self, data: bytearray) -> None:
        """Zero every byte of *data* in-place."""
        for i in range(len(data)):
            data[i] = 0

    def secure_bytes(self, size: int) -> bytearray:
        """Allocate a zeroed bytearray of *size* bytes."""
        return bytearray(size)


# Patterns whose values must be redacted from log output
_SENSITIVE_PATTERN = re.compile(
    r"(?i)\b(key|passphrase|password|secret|token|private_key|auth(?:_key)?)"
    r"=(\S+)"
)


class LogSanitizer:
    """Removes sensitive key-value pairs from log strings."""

    def sanitize(self, message: str) -> str:
        return _SENSITIVE_PATTERN.sub(r"\1=***REDACTED***", message)
