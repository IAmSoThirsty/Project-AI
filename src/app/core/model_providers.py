"""
Model Provider Adapters for AI Services.

This module provides abstraction for different AI model providers including
OpenAI, Perplexity, and future providers. It enables seamless switching
between providers while maintaining consistent interfaces.
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class ModelProvider(ABC):
    """Abstract base class for AI model providers."""

    @abstractmethod
    def __init__(self, api_key: str | None = None):
        """Initialize the provider with API key."""

    @abstractmethod
    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """
        Create a chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model identifier
            temperature: Sampling temperature (0.0-1.0)
            **kwargs: Additional provider-specific parameters

        Returns:
            Generated text response

        Raises:
            Exception: If API call fails
        """

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available (API key set, etc.)."""


class OpenAIProvider(ModelProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str | None = None):
        """Initialize OpenAI provider."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if self.api_key:
            try:
                import openai

                # Use client instantiation pattern (recommended by OpenAI)
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                logger.error("openai package not installed")
                self._client = None
        else:
            self._client = None

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Create a chat completion using OpenAI API."""
        if not self._client:
            raise RuntimeError("OpenAI not available. Check API key and installation.")

        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenAI API error: %s", e)
            raise

    def is_available(self) -> bool:
        """Check if OpenAI is available."""
        return self._client is not None and self.api_key is not None


class PerplexityProvider(ModelProvider):
    """Perplexity API provider."""

    def __init__(self, api_key: str | None = None):
        """Initialize Perplexity provider."""
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        # Perplexity uses OpenAI-compatible API
        if self.api_key:
            try:
                import openai

                self._client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url="https://api.perplexity.ai",
                )
            except ImportError:
                logger.error("openai package not installed")
                self._client = None
        else:
            self._client = None

    def chat_completion(
        self,
        messages: list[dict[str, str]],
        model: str = "llama-3.1-sonar-small-128k-online",
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> str:
        """Create a chat completion using Perplexity API."""
        if not self._client:
            raise RuntimeError(
                "Perplexity not available. Check API key and installation."
            )

        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("Perplexity API error: %s", e)
            raise

    def is_available(self) -> bool:
        """Check if Perplexity is available."""
        return self._client is not None and self.api_key is not None


def get_provider(
    provider_name: str = "openai", api_key: str | None = None
) -> ModelProvider:
    """
    Factory function to get a model provider.

    Args:
        provider_name: Name of provider ('openai', 'perplexity')
        api_key: Optional API key (will use env var if not provided)

    Returns:
        ModelProvider instance

    Raises:
        ValueError: If provider name is unknown
    """
    providers = {
        "openai": OpenAIProvider,
        "perplexity": PerplexityProvider,
    }

    provider_name_lower = provider_name.lower()
    if provider_name_lower not in providers:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            f"Available providers: {list(providers.keys())}"
        )

    provider_class = providers[provider_name_lower]
    provider = provider_class(api_key=api_key)

    if not provider.is_available():
        logger.warning("Provider %s is not available", provider_name)

    return provider
