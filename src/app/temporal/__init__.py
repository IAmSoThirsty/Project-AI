"""
Temporal.io integration module for Project-AI.

This module provides workflow orchestration, durable execution, and distributed
task coordination using Temporal.io platform.
"""

from .activities import (data_activities, image_activities, learning_activities,
                         memory_activities)
from .client import TemporalClientManager
from .workflows import (AILearningWorkflow, DataAnalysisWorkflow,
                        ImageGenerationWorkflow, MemoryExpansionWorkflow)

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
