"""
Governance Pipeline: Shared enforcement layer for all execution paths.

Ensures every request (web/desktop/CLI/agent) flows through:
    1. Validation - Input sanitization, schema checks
    2. Simulation - Shadow execution, impact analysis
    3. Gate - Authorization, Four Laws compliance
    4. Execution - Actual operation
    5. Commit - State persistence
    6. Logging - Audit trail

This is the enforcement layer that makes multi-path governance work.
"""

from .pipeline import enforce_pipeline

__all__ = ["enforce_pipeline"]
