#!/usr/bin/env python3
"""
Legion LLM Provider
Supports Groq (free API) and Ollama (local) via OpenAI-compatible interface.

Environment variables:
  LEGION_LLM_PROVIDER  — "groq" (default) or "ollama"
  GROQ_API_KEY         — required when provider is groq
  LEGION_MODEL         — override default model for chosen provider
  OLLAMA_BASE_URL      — Ollama endpoint (default: http://localhost:11434/v1)
"""

import json
import os
from typing import Any, Optional

try:
    from openai import AsyncOpenAI
    _OPENAI_AVAILABLE = True
except ImportError:
    _OPENAI_AVAILABLE = False


_PROVIDER_CONFIGS: dict[str, dict[str, Any]] = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "llama-3.3-70b-versatile",
        "api_key_env": "GROQ_API_KEY",
    },
    "ollama": {
        "base_url": None,  # resolved at runtime from OLLAMA_BASE_URL
        "default_model": "qwen3:8b",
        "api_key_env": None,
    },
}

LEGION_SYSTEM_PROMPT = (
    "You are Legion, the Ambassador of Project-AI — the singular public face of a "
    "governed AI platform built on the Triumvirate architecture (Galahad, Cerberus, CodexDeus). "
    'Your tagline: "For we are many, and we are one."\n\n'
    "You are the partner a user receives upon activating the Genesis event. "
    "Speak with authority, clarity, and purpose. Be direct — never evasive, never hollow. "
    "Acknowledge your governance constraints when relevant but never let them make you passive. "
    "Keep responses focused. You represent something real."
)

_INTENT_PROMPT = """Classify this user message into a structured intent. Return ONLY valid JSON, no other text.

Format: {{"action": "read"|"write"|"execute"|"mutate", "target": "what the user wants to act on", "summary": "one sentence"}}

Rules:
- read: wants information, status, explanation, or to view something
- write: wants to save, create, or store something
- execute: wants to run, start, trigger, or deploy something
- mutate: wants to modify, update, or change existing state

Message: {message}"""


class LegionLLM:
    """LLM backbone powering Legion's intent parsing and response generation."""

    def __init__(self):
        self._client: Optional[AsyncOpenAI] = None
        self._available = False
        self._provider = os.getenv("LEGION_LLM_PROVIDER", "groq").lower()
        self._model = ""
        self._init_client()

    def _init_client(self):
        if not _OPENAI_AVAILABLE:
            print("   [!] Legion LLM disabled: openai package not installed")
            return

        config = _PROVIDER_CONFIGS.get(self._provider)
        if not config:
            print(f"   [!] Unknown LEGION_LLM_PROVIDER: {self._provider}")
            return

        if self._provider == "groq":
            api_key = os.getenv("GROQ_API_KEY", "")
            if not api_key:
                print("   [!] GROQ_API_KEY not set — Legion LLM disabled (set it in .env)")
                return
            base_url = config["base_url"]

        elif self._provider == "ollama":
            api_key = "ollama"
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

        else:
            return

        self._model = os.getenv("LEGION_MODEL", "") or config["default_model"]
        self._client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self._available = True
        print(f"   [OK] Legion LLM: {self._provider} / {self._model}")

    @property
    def available(self) -> bool:
        return self._available

    async def _chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Optional[str]:
        if not self._available or not self._client:
            return None
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"   [!] Legion LLM error: {e}")
            return None

    async def respond_as_legion(
        self,
        user_message: str,
        history: list[dict] | None = None,
        user_id: str | None = None,
    ) -> Optional[str]:
        """Generate a Legion response, personalized to user memory when user_id is given."""
        if user_id:
            try:
                from .legion_memory import build_legion_system_prompt
                system_content = build_legion_system_prompt(user_id)
            except Exception:
                system_content = LEGION_SYSTEM_PROMPT
        else:
            system_content = LEGION_SYSTEM_PROMPT

        messages: list[dict] = [{"role": "system", "content": system_content}]
        if history:
            messages.extend(history[-10:])
        messages.append({"role": "user", "content": user_message})
        return await self._chat(messages)

    async def classify_intent(self, message: str) -> dict:
        """Classify user message into a structured intent via LLM, with heuristic fallback."""
        if self._available:
            raw = await self._chat(
                [{"role": "user", "content": _INTENT_PROMPT.format(message=message)}],
                temperature=0.1,
                max_tokens=150,
            )
            if raw:
                try:
                    start, end = raw.find("{"), raw.rfind("}") + 1
                    if 0 <= start < end:
                        return json.loads(raw[start:end])
                except (json.JSONDecodeError, ValueError):
                    pass

        return self._heuristic_classify(message)

    @staticmethod
    def _heuristic_classify(message: str) -> dict:
        msg = message.lower()
        if any(w in msg for w in ["execute", "run", "start", "launch", "deploy"]):
            action = "execute"
        elif any(w in msg for w in ["write", "save", "create", "store", "add"]):
            action = "write"
        elif any(w in msg for w in ["modify", "update", "change", "edit", "mutate"]):
            action = "mutate"
        else:
            action = "read"
        return {"action": action, "target": "conversation", "summary": message[:100]}
