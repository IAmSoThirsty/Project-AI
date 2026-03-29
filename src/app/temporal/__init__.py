# ============================================================================ #
#                                           [2026-03-18 09:59]
#                                          Productivity: Active
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-18 | TIME: 09:59             #
# COMPLIANCE: Sovereign Substrate / __init__.py
# ============================================================================ #
#
# COMPLIANCE: Sovereign Substrate / __init__.py

"""
Temporal.io integration module for Project-AI.

This module provides workflow orchestration, durable execution, and distributed
task coordination using Temporal.io platform.
"""

from .activities import (
    data_activities,
    image_activities,
    learning_activities,
    memory_activities,
)
from .client import TemporalClientManager
from .workflows import (
    AILearningWorkflow,
    DataAnalysisWorkflow,
    ImageGenerationWorkflow,
    MemoryExpansionWorkflow,
)

__all__ = [
    "TemporalClientManager",
    "AILearningWorkflow",
    "DataAnalysisWorkflow",
    "ImageGenerationWorkflow",
    "MemoryExpansionWorkflow",
    "learning_activities",
    "memory_activities",
    "image_activities",
    "data_activities",
]
