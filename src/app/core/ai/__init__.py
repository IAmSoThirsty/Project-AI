"""
AI Orchestration Layer: Single coordination point for all AI provider calls.

This is NOT a single AI path - it's a shared coordination layer that:
- Routes ALL AI calls through one control point (no scattered OpenAI/HF imports)
- Provides fallback across providers (OpenAI → HuggingFace → Perplexity)
- Enables cost tracking, governance alignment, rate limiting
- Maintains provider abstraction for flexibility

Architecture:
    Systems → AI Orchestrator → Providers (OpenAI/HF/Perplexity/Local)
"""

from .orchestrator import run_ai, AIRequest, AIResponse

__all__ = ["run_ai", "AIRequest", "AIResponse"]
