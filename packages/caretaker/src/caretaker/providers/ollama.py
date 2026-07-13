"""
caretaker.providers.ollama — Ollama inference provider.

Ported from ``thirsty_governance_framework_0722``
``governance_core/caretaker/providers/ollama.py``. Ollama does NOT expose
logits in its /api/chat endpoint, so this provider sets has_logits=False and
the Actualizer falls back to post-generation text-level scoring
(DIEPT/CAKI/redundancy) rather than logit re-weighting. A future provider
that exposes logits fills logit_history and the Actualizer automatically
switches to the re-weighting path.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

import httpx

from caretaker.providers.base import InferenceProvider, InferenceResult, Message

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "qwen2.5-coder:14b"


class OllamaProvider(InferenceProvider):
    """Ollama provider — no logit access, uses post-generation scoring."""

    def __init__(self, host: str = "http://localhost:11434", model: str = DEFAULT_MODEL) -> None:
        self._host = host
        self._model = model
        self._client = httpx.Client(timeout=300.0)

    @property
    def name(self) -> str:
        return "ollama"

    @property
    def exposes_logits(self) -> bool:
        return False

    def generate(
        self,
        system_prompt: str,
        user_message: str,
        context: Sequence[Message] | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> InferenceResult:
        messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]
        if context:
            messages.extend(dict(m) for m in context)
        messages.append({"role": "user", "content": user_message})

        try:
            response = self._client.post(
                f"{self._host}/api/chat",
                json={
                    "model": self._model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens,
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("message", {}).get("content", "")
            tokens = int(data.get("eval_count", 0))
            return InferenceResult(
                text=text,
                token_count=tokens,
                logit_history=[],  # No logits from Ollama
                has_logits=False,
            )
        except httpx.HTTPError as e:
            logger.error("Ollama request failed: %s", e)
            return InferenceResult(
                text=f"[PROVIDER ERROR] {e}",
                token_count=0,
                logit_history=[],
                has_logits=False,
            )

    def health_check(self) -> bool:
        try:
            r = self._client.get(f"{self._host}/api/tags", timeout=5.0)
        except httpx.HTTPError:
            return False
        return r.status_code == 200


__all__ = ["DEFAULT_MODEL", "OllamaProvider"]
