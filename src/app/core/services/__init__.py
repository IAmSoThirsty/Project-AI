"""
Core services package for modular CognitionKernel architecture.

This package contains the service modules that were extracted from the monolithic
CognitionKernel to improve maintainability while preserving the monolith philosophy.

Services:
- GovernanceService: Handles governance evaluation and Triumvirate decisions
- ExecutionService: Manages action execution with TARL enforcement
- MemoryLoggingService: Handles multi-channel memory recording and storage

Each service maintains clear separation of concerns while working together through
the CognitionKernel orchestration layer.
"""

from .execution_service import ExecutionService
from .governance_service import GovernanceService
from .memory_logging_service import MemoryLoggingService

__all__ = [
    "GovernanceService",
    "ExecutionService",
    "MemoryLoggingService",
]
