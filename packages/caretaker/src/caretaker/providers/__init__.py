"""caretaker.providers — Inference providers (the model is untrusted)."""

from caretaker.providers.base import (
    InferenceProvider,
    InferenceResult,
    LogitVector,
    Message,
    TokenCandidate,
)
from caretaker.providers.mock import MockProvider
from caretaker.providers.ollama import OllamaProvider

__all__ = [
    "InferenceProvider",
    "InferenceResult",
    "LogitVector",
    "Message",
    "MockProvider",
    "OllamaProvider",
    "TokenCandidate",
]
