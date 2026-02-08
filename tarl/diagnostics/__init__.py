"""
T.A.R.L. (Thirstys Active Resistance Language) Diagnostics Subsystem

Production-grade error reporting, warning system, and code quality diagnostics.
Provides comprehensive feedback for compilation and runtime errors with rich
context, source location tracking, and actionable suggestions.

Features:
    - Structured error reporting with severity levels
    - Source location tracking with line/column precision
    - Multi-error aggregation and batching
    - Warning categories with configurable levels
    - Rich error context with code snippets
    - Suggestion engine for common mistakes
    - Integration with linter and formatter
    - Telemetry and error analytics

Architecture Contract:
    - MUST depend only on config subsystem
    - MUST provide structured error objects
    - MUST support batch error reporting
    - MUST maintain error history for diagnostics
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class Severity(Enum):
    """Diagnostic severity levels"""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


class DiagnosticCategory(Enum):
    """Diagnostic categories for classification"""

    SYNTAX = "syntax"
    SEMANTIC = "semantic"
    TYPE = "type"
    RUNTIME = "runtime"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"


@dataclass
class SourceLocation:
    """Source code location information"""

    file: str
    line: int
    column: int
    length: int = 1

    def __str__(self) -> str:
        return f"{self.file}:{self.line}:{self.column}"


@dataclass
class Diagnostic:
    """
    Structured diagnostic message

    Represents a single error, warning, or informational message with
    full context including source location, severity, and suggested fixes.
    """

    severity: Severity
    category: DiagnosticCategory
    code: str
    message: str
    location: SourceLocation | None = None
    context: str | None = None
    suggestions: list[str] = field(default_factory=list)
    related_info: list[str] = field(default_factory=list)

    def format(self) -> str:
        """
        Format diagnostic for human-readable output

        Returns:
            Formatted diagnostic string
        """
        parts = []

        # Header: severity, location, code
        header = f"{self.severity.value.upper()}"
        if self.location:
            header += f" [{self.location}]"
        header += f" [{self.code}]"
        parts.append(header)

        # Message
        parts.append(f"  {self.message}")

        # Context (source code snippet)
        if self.context:
            parts.append("")
            parts.append("  Context:")
            for line in self.context.split("\n"):
                parts.append(f"    {line}")

        # Suggestions
        if self.suggestions:
            parts.append("")
            parts.append("  Suggestions:")
            for suggestion in self.suggestions:
                parts.append(f"    - {suggestion}")

        # Related information
        if self.related_info:
            parts.append("")
            parts.append("  Related:")
            for info in self.related_info:
                parts.append(f"    - {info}")

        return "\n".join(parts)


class DiagnosticsEngine:
    """
    Central diagnostics engine for T.A.R.L. system

    Manages error reporting, warning aggregation, and diagnostic analysis
    across all subsystems. Provides structured error objects with rich
    context for developer experience.

    Example:
        >>> diagnostics = DiagnosticsEngine(config)
        >>> diagnostics.report_error(
        ...     code="E001",
        ...     message="Undefined variable 'x'",
        ...     location=SourceLocation("test.tarl", 5, 10)
        ... )
    """

    def __init__(self, config):
        """
        Initialize diagnostics engine

        Args:
            config: ConfigRegistry instance
        """
        self.config = config
        self.diagnostics: list[Diagnostic] = []
        self.error_count = 0
        self.warning_count = 0
        self._initialized = False

        logger.info("DiagnosticsEngine created")

    def initialize(self) -> None:
        """Initialize diagnostics engine"""
        if self._initialized:
            return

        # Load configuration
        self.log_level = self.config.get("diagnostics.log_level", "INFO")
        self.enable_warnings = self.config.get("diagnostics.enable_warnings", True)
        self.context_lines = self.config.get("diagnostics.error_context_lines", 3)

        self._initialized = True
        logger.info("Diagnostics engine initialized")

    def report_error(
        self,
        code: str,
        message: str,
        category: DiagnosticCategory = DiagnosticCategory.RUNTIME,
        location: SourceLocation | None = None,
        context: str | None = None,
        suggestions: list[str] | None = None,
    ) -> None:
        """
        Report an error diagnostic

        Args:
            code: Error code (e.g., "E001")
            message: Human-readable error message
            category: Diagnostic category
            location: Source location of error
            context: Source code context
            suggestions: List of suggested fixes
        """
        diagnostic = Diagnostic(
            severity=Severity.ERROR,
            category=category,
            code=code,
            message=message,
            location=location,
            context=context,
            suggestions=suggestions or [],
        )

        self.diagnostics.append(diagnostic)
        self.error_count += 1

        logger.error(
            f"[{code}] {message}",
            extra={"location": str(location) if location else None},
        )

    def report_warning(
        self,
        code: str,
        message: str,
        category: DiagnosticCategory = DiagnosticCategory.STYLE,
        location: SourceLocation | None = None,
        context: str | None = None,
        suggestions: list[str] | None = None,
    ) -> None:
        """
        Report a warning diagnostic

        Args:
            code: Warning code (e.g., "W001")
            message: Human-readable warning message
            category: Diagnostic category
            location: Source location
            context: Source code context
            suggestions: List of suggested fixes
        """
        if not self.enable_warnings:
            return

        diagnostic = Diagnostic(
            severity=Severity.WARNING,
            category=category,
            code=code,
            message=message,
            location=location,
            context=context,
            suggestions=suggestions or [],
        )

        self.diagnostics.append(diagnostic)
        self.warning_count += 1

        logger.warning(
            f"[{code}] {message}",
            extra={"location": str(location) if location else None},
        )

    def report_info(
        self,
        code: str,
        message: str,
        category: DiagnosticCategory = DiagnosticCategory.STYLE,
        location: SourceLocation | None = None,
    ) -> None:
        """
        Report an informational diagnostic

        Args:
            code: Info code
            message: Informational message
            category: Diagnostic category
            location: Source location
        """
        diagnostic = Diagnostic(
            severity=Severity.INFO,
            category=category,
            code=code,
            message=message,
            location=location,
        )

        self.diagnostics.append(diagnostic)
        logger.info("[%s] %s", code, message)

    def get_diagnostics(
        self,
        severity: Severity | None = None,
        category: DiagnosticCategory | None = None,
    ) -> list[Diagnostic]:
        """
        Get filtered diagnostics

        Args:
            severity: Filter by severity level
            category: Filter by category

        Returns:
            List of matching diagnostics
        """
        result = self.diagnostics

        if severity:
            result = [d for d in result if d.severity == severity]

        if category:
            result = [d for d in result if d.category == category]

        return result

    def has_errors(self) -> bool:
        """Check if any errors have been reported"""
        return self.error_count > 0

    def has_warnings(self) -> bool:
        """Check if any warnings have been reported"""
        return self.warning_count > 0

    def clear(self) -> None:
        """Clear all diagnostics"""
        self.diagnostics.clear()
        self.error_count = 0
        self.warning_count = 0
        logger.info("Diagnostics cleared")

    def format_all(self) -> str:
        """
        Format all diagnostics for output

        Returns:
            Formatted diagnostic report
        """
        if not self.diagnostics:
            return "No diagnostics"

        parts = []
        parts.append("=" * 80)
        parts.append("T.A.R.L. DIAGNOSTICS REPORT")
        parts.append("=" * 80)
        parts.append(f"Errors: {self.error_count}, Warnings: {self.warning_count}")
        parts.append("")

        for diagnostic in self.diagnostics:
            parts.append(diagnostic.format())
            parts.append("")

        parts.append("=" * 80)

        return "\n".join(parts)

    def get_status(self) -> dict[str, Any]:
        """
        Get diagnostics status

        Returns:
            Status dictionary
        """
        return {
            "initialized": self._initialized,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "total_diagnostics": len(self.diagnostics),
            "enable_warnings": self.enable_warnings,
        }

    def shutdown(self) -> None:
        """Shutdown diagnostics engine"""
        self.clear()
        self._initialized = False
        logger.info("Diagnostics engine shutdown")


# Public API
__all__ = [
    "DiagnosticsEngine",
    "Diagnostic",
    "Severity",
    "DiagnosticCategory",
    "SourceLocation",
]
