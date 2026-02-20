"""
Unified exception hierarchy for Project-AI.

This module provides a comprehensive, cathedral-level exception framework
for all subsystems, enabling standardized error handling, categorization,
and observability across the entire system.
"""

import traceback
from datetime import datetime
from enum import Enum
from typing import Any


class ErrorSeverity(Enum):
    """Standardized error severity levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    FATAL = "FATAL"


class ErrorCategory(Enum):
    """Error categories for systematic classification."""

    CONFIGURATION = "CONFIGURATION"
    VALIDATION = "VALIDATION"
    AUTHENTICATION = "AUTHENTICATION"
    AUTHORIZATION = "AUTHORIZATION"
    NETWORK = "NETWORK"
    DATABASE = "DATABASE"
    FILESYSTEM = "FILESYSTEM"
    EXTERNAL_SERVICE = "EXTERNAL_SERVICE"
    BUSINESS_LOGIC = "BUSINESS_LOGIC"
    SYSTEM = "SYSTEM"
    SECURITY = "SECURITY"
    RESOURCE = "RESOURCE"
    TIMEOUT = "TIMEOUT"
    DEPENDENCY = "DEPENDENCY"
    UNKNOWN = "UNKNOWN"


class ProjectAIError(Exception):
    """
    Base exception for all Project-AI errors.

    Provides comprehensive error context including:
    - Error code for programmatic handling
    - Severity level for prioritization
    - Category for classification
    - Detailed context for debugging
    - Timestamp for temporal analysis
    - Traceback for root cause analysis
    """

    def __init__(
        self,
        message: str,
        error_code: str,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        context: dict[str, Any] | None = None,
        original_exception: Exception | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.context = context or {}
        self.original_exception = original_exception
        self.timestamp = datetime.now(datetime.UTC) if hasattr(datetime, "UTC") else datetime.utcnow()
        self.traceback = traceback.format_exc() if original_exception else None

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to structured dictionary for logging/serialization."""
        return {
            "message": self.message,
            "error_code": self.error_code,
            "severity": self.severity.value,
            "category": self.category.value,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "traceback": self.traceback,
            "original_exception": (str(self.original_exception) if self.original_exception else None),
        }

    def __str__(self) -> str:
        """Human-readable error representation."""
        return (
            f"[{self.error_code}] {self.severity.value}: {self.message} "
            f"(category={self.category.value}, timestamp={self.timestamp.isoformat()})"
        )


# Configuration Errors
class ConfigurationError(ProjectAIError):
    """Errors related to system configuration."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.pop("error_code", "CONFIG_ERROR"),
            severity=kwargs.pop("severity", ErrorSeverity.ERROR),
            category=ErrorCategory.CONFIGURATION,
            **kwargs,
        )


class ConfigValidationError(ConfigurationError):
    """Configuration validation failed."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="CONFIG_VALIDATION_FAILED", **kwargs)


class ConfigMissingError(ConfigurationError):
    """Required configuration is missing."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="CONFIG_MISSING", **kwargs)


# Validation Errors
class ValidationError(ProjectAIError):
    """Errors related to data validation."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.pop("error_code", "VALIDATION_ERROR"),
            severity=kwargs.pop("severity", ErrorSeverity.WARNING),
            category=ErrorCategory.VALIDATION,
            **kwargs,
        )


class InputValidationError(ValidationError):
    """Input data validation failed."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="INPUT_VALIDATION_FAILED", **kwargs)


class SchemaValidationError(ValidationError):
    """Schema validation failed."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="SCHEMA_VALIDATION_FAILED", **kwargs)


# Security Errors
class SecurityError(ProjectAIError):
    """Errors related to security violations."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.pop("error_code", "SECURITY_ERROR"),
            severity=kwargs.pop("severity", ErrorSeverity.CRITICAL),
            category=ErrorCategory.SECURITY,
            **kwargs,
        )


class AuthenticationError(SecurityError):
    """Authentication failed."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="AUTH_FAILED", **kwargs)


class AuthorizationError(SecurityError):
    """Authorization check failed."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="AUTHZ_FAILED", **kwargs)


class InjectionDetectedError(SecurityError):
    """Potential injection attack detected."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="INJECTION_DETECTED",
            severity=ErrorSeverity.CRITICAL,
            **kwargs,
        )


# Network Errors
class NetworkError(ProjectAIError):
    """Errors related to network operations."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.pop("error_code", "NETWORK_ERROR"),
            severity=kwargs.pop("severity", ErrorSeverity.ERROR),
            category=ErrorCategory.NETWORK,
            **kwargs,
        )


class ConnectionError(NetworkError):
    """Network connection failed."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="CONNECTION_FAILED", **kwargs)


class TimeoutError(NetworkError):
    """Operation timed out."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="TIMEOUT", category=ErrorCategory.TIMEOUT, **kwargs)


# Resource Errors
class ResourceError(ProjectAIError):
    """Errors related to resource management."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.pop("error_code", "RESOURCE_ERROR"),
            severity=kwargs.pop("severity", ErrorSeverity.ERROR),
            category=ErrorCategory.RESOURCE,
            **kwargs,
        )


class ResourceExhaustedError(ResourceError):
    """System resources exhausted."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="RESOURCE_EXHAUSTED",
            severity=ErrorSeverity.CRITICAL,
            **kwargs,
        )


class ResourceNotFoundError(ResourceError):
    """Required resource not found."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="RESOURCE_NOT_FOUND", **kwargs)


# Subsystem Errors
class SubsystemError(ProjectAIError):
    """Errors related to subsystem operations."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.pop("error_code", "SUBSYSTEM_ERROR"),
            severity=kwargs.pop("severity", ErrorSeverity.ERROR),
            category=ErrorCategory.SYSTEM,
            **kwargs,
        )


class SubsystemInitializationError(SubsystemError):
    """Subsystem initialization failed."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="SUBSYSTEM_INIT_FAILED",
            severity=ErrorSeverity.CRITICAL,
            **kwargs,
        )


class SubsystemHealthCheckError(SubsystemError):
    """Subsystem health check failed."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="SUBSYSTEM_HEALTH_CHECK_FAILED", **kwargs)


class CircuitBreakerOpenError(SubsystemError):
    """Circuit breaker is open, service unavailable."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="CIRCUIT_BREAKER_OPEN",
            severity=ErrorSeverity.WARNING,
            **kwargs,
        )


# Dependency Errors
class DependencyError(ProjectAIError):
    """Errors related to dependencies."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.pop("error_code", "DEPENDENCY_ERROR"),
            severity=kwargs.pop("severity", ErrorSeverity.ERROR),
            category=ErrorCategory.DEPENDENCY,
            **kwargs,
        )


class DependencyNotFoundError(DependencyError):
    """Required dependency not found."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="DEPENDENCY_NOT_FOUND",
            severity=ErrorSeverity.CRITICAL,
            **kwargs,
        )


class DependencyCycleError(DependencyError):
    """Circular dependency detected."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="DEPENDENCY_CYCLE",
            severity=ErrorSeverity.CRITICAL,
            **kwargs,
        )


# Database Errors
class DatabaseError(ProjectAIError):
    """Errors related to database operations."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.pop("error_code", "DATABASE_ERROR"),
            severity=kwargs.pop("severity", ErrorSeverity.ERROR),
            category=ErrorCategory.DATABASE,
            **kwargs,
        )


class DatabaseConnectionError(DatabaseError):
    """Database connection failed."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code="DB_CONNECTION_FAILED",
            severity=ErrorSeverity.CRITICAL,
            **kwargs,
        )


# External Service Errors
class ExternalServiceError(ProjectAIError):
    """Errors related to external service calls."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.pop("error_code", "EXTERNAL_SERVICE_ERROR"),
            severity=kwargs.pop("severity", ErrorSeverity.ERROR),
            category=ErrorCategory.EXTERNAL_SERVICE,
            **kwargs,
        )


class ExternalServiceUnavailableError(ExternalServiceError):
    """External service is unavailable."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="EXTERNAL_SERVICE_UNAVAILABLE", **kwargs)


# Business Logic Errors
class BusinessLogicError(ProjectAIError):
    """Errors related to business logic violations."""

    def __init__(self, message: str, **kwargs):
        super().__init__(
            message,
            error_code=kwargs.pop("error_code", "BUSINESS_LOGIC_ERROR"),
            severity=kwargs.pop("severity", ErrorSeverity.WARNING),
            category=ErrorCategory.BUSINESS_LOGIC,
            **kwargs,
        )


class InvalidStateError(BusinessLogicError):
    """Operation invalid for current state."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="INVALID_STATE", **kwargs)


class OperationNotAllowedError(BusinessLogicError):
    """Operation not allowed by business rules."""

    def __init__(self, message: str, **kwargs):
        super().__init__(message, error_code="OPERATION_NOT_ALLOWED", **kwargs)
