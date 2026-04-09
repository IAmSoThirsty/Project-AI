#                                           [2026-03-03 13:45]
#                                          Productivity: Active
"""
Cognition Module - Triumvirate AI Architecture

This module implements a three-engine AI system with production-ready features:
- Codex: ML model inference with GPU/CPU fallback
- Galahad: Reasoning engine with arbitration and curiosity
- Cerberus: Policy enforcement and output validation

The Triumvirate orchestrator coordinates these engines for robust AI decision-making.
"""

# Lazy imports to avoid circular dependencies and missing optional deps
# Use: from cognition.triumvirate import Triumvirate

__all__ = ["Triumvirate", "TriumvirateConfig"]


def __getattr__(name: str):
    """Lazy import for better dependency management."""
    if name in __all__:
        from src.cognition.triumvirate import Triumvirate, TriumvirateConfig
        return {"Triumvirate": Triumvirate, "TriumvirateConfig": TriumvirateConfig}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
