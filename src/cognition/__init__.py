"""
Cognition Module - Triumvirate AI Architecture

This module implements a three-engine AI system with production-ready features:
- Codex: ML model inference with GPU/CPU fallback
- Galahad: Reasoning engine with arbitration and curiosity
- Cerberus: Policy enforcement and output validation

The Triumvirate orchestrator coordinates these engines for robust AI decision-making.
"""

from src.cognition.triumvirate import Triumvirate, TriumvirateConfig

__all__ = ["Triumvirate", "TriumvirateConfig"]
