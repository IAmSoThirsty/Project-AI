"""
Core exception hierarchy for Project-AI.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum


class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ProjectAIError(Exception):
    error_code: str = "PROJECT_AI_ERROR"
    category: str = "GENERAL"
    severity: ErrorSeverity = ErrorSeverity.MEDIUM

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        context: dict | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if error_code is not None:
            self.error_code = error_code
        self.context: dict = context or {}
        self.timestamp: datetime = datetime.utcnow()

    def to_dict(self) -> dict:
        return {
            "message": self.message,
            "error_code": self.error_code,
            "category": self.category,
            "severity": self.severity.name,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
        }


class ConfigurationError(ProjectAIError):
    error_code = "CONFIG_ERROR"
    category = "CONFIGURATION"


class SecurityError(ProjectAIError):
    error_code = "SECURITY_ERROR"
    category = "SECURITY"
    severity = ErrorSeverity.CRITICAL


class CircuitBreakerOpenError(ProjectAIError):
    error_code = "CIRCUIT_BREAKER_OPEN"
    category = "INFRASTRUCTURE"


class DependencyNotFoundError(ProjectAIError):
    error_code = "DEPENDENCY_NOT_FOUND"
    category = "INFRASTRUCTURE"


class AuthorizationError(ProjectAIError):
    error_code = "AUTHORIZATION_ERROR"
    category = "SECURITY"
    severity = ErrorSeverity.HIGH


class ValidationError(ProjectAIError):
    error_code = "VALIDATION_ERROR"
    category = "VALIDATION"
