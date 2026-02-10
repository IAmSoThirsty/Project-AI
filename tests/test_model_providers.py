"""Tests for model provider adapters."""

import os
from unittest.mock import patch

import pytest


class TestOpenAIProvider:
    """Test OpenAI provider functionality."""

    def test_initialization_without_api_key(self):
        """Test OpenAI provider initialization without API key."""
        from app.core.model_providers import OpenAIProvider

        with patch.dict(os.environ, {}, clear=True):
            provider = OpenAIProvider(api_key=None)
            assert provider.api_key is None
            assert provider.is_available() is False

    def test_initialization_with_api_key(self):
        """Test OpenAI provider initialization with API key."""
        from app.core.model_providers import OpenAIProvider

        provider = OpenAIProvider(api_key="test-key")
        assert provider.api_key == "test-key"

    def test_chat_completion_without_initialization(self):
        """Test chat completion fails without proper initialization."""
        from app.core.model_providers import OpenAIProvider

        provider = OpenAIProvider(api_key=None)
        with pytest.raises(RuntimeError, match="OpenAI not available"):
            provider.chat_completion(
                messages=[{"role": "user", "content": "Test"}],
                model="gpt-3.5-turbo",
            )


class TestPerplexityProvider:
    """Test Perplexity provider functionality."""

    def test_initialization_without_api_key(self):
        """Test Perplexity provider initialization without API key."""
        from app.core.model_providers import PerplexityProvider

        with patch.dict(os.environ, {}, clear=True):
            provider = PerplexityProvider(api_key=None)
            assert provider.api_key is None
            assert provider.is_available() is False

    def test_initialization_with_api_key(self):
        """Test Perplexity provider initialization with API key."""
        from app.core.model_providers import PerplexityProvider

        provider = PerplexityProvider(api_key="test-key")
        assert provider.api_key == "test-key"

    def test_chat_completion_without_initialization(self):
        """Test chat completion fails without proper initialization."""
        from app.core.model_providers import PerplexityProvider

        provider = PerplexityProvider(api_key=None)
        with pytest.raises(RuntimeError, match="Perplexity not available"):
            provider.chat_completion(
                messages=[{"role": "user", "content": "Test"}],
                model="llama-3.1-sonar-small-128k-online",
            )


class TestProviderFactory:
    """Test provider factory function."""

    def test_get_openai_provider(self):
        """Test getting OpenAI provider."""
        from app.core.model_providers import OpenAIProvider, get_provider

        provider = get_provider("openai", api_key="test-key")
        assert isinstance(provider, OpenAIProvider)
        assert provider.api_key == "test-key"

    def test_get_perplexity_provider(self):
        """Test getting Perplexity provider."""
        from app.core.model_providers import PerplexityProvider, get_provider

        provider = get_provider("perplexity", api_key="test-key")
        assert isinstance(provider, PerplexityProvider)
        assert provider.api_key == "test-key"

    def test_get_unknown_provider(self):
        """Test getting unknown provider raises ValueError."""
        from app.core.model_providers import get_provider

        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("unknown-provider")

    def test_get_provider_case_insensitive(self):
        """Test provider name is case insensitive."""
        from app.core.model_providers import (
            OpenAIProvider,
            PerplexityProvider,
            get_provider,
        )

        provider = get_provider("OPENAI", api_key="test-key")
        assert isinstance(provider, OpenAIProvider)

        provider = get_provider("Perplexity", api_key="test-key")
        assert isinstance(provider, PerplexityProvider)


class TestProviderIntegration:
    """Integration tests for provider usage."""

    def test_openai_provider_env_var(self):
        """Test OpenAI provider reads from environment variable."""
        from app.core.model_providers import OpenAIProvider

        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-test-key"}):
            provider = OpenAIProvider()
            assert provider.api_key == "env-test-key"

    def test_perplexity_provider_env_var(self):
        """Test Perplexity provider reads from environment variable."""
        from app.core.model_providers import PerplexityProvider

        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "env-test-key"}):
            provider = PerplexityProvider()
            assert provider.api_key == "env-test-key"
