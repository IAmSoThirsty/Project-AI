"""
Reasoning Matrix — Formalized Decision Tracking for Project AI.

Provides a cross-cutting module that tracks, scores, and formalizes
reasoning decisions across all subsystems (Triumvirate, Galahad,
Waterfall, safety agents, governance, etc.).

Usage:
    from cognition.reasoning_matrix import ReasoningMatrix, ReasoningFactor

    matrix = ReasoningMatrix()
    entry_id = matrix.begin_reasoning("triumvirate_pipeline")
    matrix.add_factor(entry_id, "cerberus_validation", True, weight=1.0,
                      source="cerberus", rationale="Input passed policy enforcement")
    matrix.score_factor(entry_id, "cerberus_validation", 1.0)
    matrix.render_verdict(entry_id, decision="allow", confidence=0.95)
"""

from src.cognition.reasoning_matrix.core import (
    MatrixEntry,
    ReasoningFactor,
    ReasoningMatrix,
    ReasoningVerdict,
)

__all__ = [
    "ReasoningFactor",
    "ReasoningVerdict",
    "MatrixEntry",
    "ReasoningMatrix",
]
