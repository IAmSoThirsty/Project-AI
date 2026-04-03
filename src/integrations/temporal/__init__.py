#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Temporal.io integration for Project-AI.

This module provides the Temporal workflow orchestration layer for durable,
fault-tolerant execution of AI operations.
"""

from .client import TemporalClient

__all__ = ["TemporalClient"]
