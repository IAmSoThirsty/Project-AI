"""
Build Cognition & State Management
==================================

Integrates Project-AI's cognition and state management for intelligent builds.
"""

from .build_cognition import BuildCognitionEngine
from .state_integration import BuildStateIntegration

# Backward-compatible alias
BuildStateManager = BuildStateIntegration

__all__ = [
    "BuildCognitionEngine",
    "BuildStateManager",
    "BuildStateIntegration",
]
