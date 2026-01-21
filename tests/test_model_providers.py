"""Tests for model provider adapters."""

import os
from unittest.mock import MagicMock, Mock, patch

import pytest

# Mock openai before importing model_providers
with patch.dict("sys.modules", {"openai": MagicMock()}):
    from app.core.model_providers import (
        OpenAIProvider,
        PerplexityProvider,
        get_provider,
    )


class TestOpenAIProvider:
    """Test OpenAI provider functionality."""

    @patch("app.core.model_providers.openai", new_callable=MagicMock)
    def test_initialization_with_api_key(self, mock_openai):
        """Test OpenAI provider initialization with API key."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.api_key == "test-key"

    @patch("app.core.model_providers.openai", new_callable=MagicMock)
    def test_initialization_with_env_var(self, mock_openai):
        """Test OpenAI provider initialization with environment variable."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "env-key"}):
            provider = OpenAIProvider()
            assert provider.api_key == "env-key"

    @patch("app.core.model_providers.openai", new_callable=MagicMock)
    def test_is_available_with_api_key(self, mock_openai):
        """Test is_available returns True when API key is set."""
        provider = OpenAIProvider(api_key="test-key")
        assert provider.is_available() is True

    def test_is_available_without_api_key(self):
        """Test is_available returns False when API key is not set."""
        with patch.dict(os.environ, {}, clear=True):
            provider = OpenAIProvider(api_key=None)
            assert provider.is_available() is False

    @patch("app.core.model_providers.openai", new_callable=MagicMock)
    def test_chat_completion_success(self, mock_openai):
        """Test successful chat completion."""
        # Mock the response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"

        mock_openai.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="test-key")
        result = provider.chat_completion(
            messages=[{"role": "user", "content": "Test"}],
            model="gpt-3.5-turbo",
        )

        assert result == "Test response"
        mock_openai.chat.completions.create.assert_called_once()

    def test_chat_completion_without_initialization(self):
        """Test chat completion fails without proper initialization."""
        provider = OpenAIProvider(api_key=None)
        with pytest.raises(RuntimeError, match="OpenAI not available"):
            provider.chat_completion(
                messages=[{"role": "user", "content": "Test"}],
                model="gpt-3.5-turbo",
            )


class TestPerplexityProvider:
    """Test Perplexity provider functionality."""

    @patch("app.core.model_providers.openai", new_callable=MagicMock)
    def test_initialization_with_api_key(self, mock_openai):
        """Test Perplexity provider initialization with API key."""
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client

        provider = PerplexityProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider._client == mock_client
        mock_openai.OpenAI.assert_called_once_with(
            api_key="test-key",
            base_url="https://api.perplexity.ai",
        )

    @patch("app.core.model_providers.openai", new_callable=MagicMock)
    def test_initialization_with_env_var(self, mock_openai):
        """Test Perplexity provider initialization with environment variable."""
        with patch.dict(os.environ, {"PERPLEXITY_API_KEY": "env-key"}):
            mock_client = MagicMock()
            mock_openai.OpenAI.return_value = mock_client

            provider = PerplexityProvider()
            assert provider.api_key == "env-key"

    @patch("app.core.model_providers.openai", new_callable=MagicMock)
    def test_is_available_with_api_key(self, mock_openai):
        """Test is_available returns True when API key is set."""
        mock_client = MagicMock()
        mock_openai.OpenAI.return_value = mock_client

        provider = PerplexityProvider(api_key="test-key")
        assert provider.is_available() is True

    def test_is_available_without_api_key(self):
        """Test is_available returns False when API key is not set."""
        with patch.dict(os.environ, {}, clear=True):
            provider = PerplexityProvider(api_key=None)
            assert provider.is_available() is False

    @patch("app.core.model_providers.openai", new_callable=MagicMock)
    def test_chat_completion_success(self, mock_openai):
        """Test successful chat completion with Perplexity."""
        # Mock the client and response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Perplexity response"

        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.OpenAI.return_value = mock_client

        provider = PerplexityProvider(api_key="test-key")
        result = provider.chat_completion(
            messages=[{"role": "user", "content": "Test"}],
            model="llama-3.1-sonar-small-128k-online",
        )

        assert result == "Perplexity response"
        mock_client.chat.completions.create.assert_called_once()

    def test_chat_completion_without_initialization(self):
        """Test chat completion fails without proper initialization."""
        provider = PerplexityProvider(api_key=None)
        with pytest.raises(RuntimeError, match="Perplexity not available"):
            provider.chat_completion(
                messages=[{"role": "user", "content": "Test"}],
                model="llama-3.1-sonar-small-128k-online",
            )


class TestProviderFactory:
    """Test provider factory function."""

    @patch("app.core.model_providers.openai", new_callable=MagicMock)
    def test_get_openai_provider(self, mock_openai):
        """Test getting OpenAI provider."""
        provider = get_provider("openai", api_key="test-key")
        assert isinstance(provider, OpenAIProvider)
        assert provider.api_key == "test-key"

    @patch("app.core.model_providers.openai", new_callable=MagicMock)
    def test_get_perplexity_provider(self, mock_openai):
        """Test getting Perplexity provider."""
        mock_openai.OpenAI.return_value = MagicMock()
        provider = get_provider("perplexity", api_key="test-key")
        assert isinstance(provider, PerplexityProvider)
        assert provider.api_key == "test-key"

    def test_get_unknown_provider(self):
        """Test getting unknown provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("unknown-provider")

    @patch("app.core.model_providers.openai", new_callable=MagicMock)
    def test_get_provider_case_insensitive(self, mock_openai):
        """Test provider name is case insensitive."""
        provider = get_provider("OPENAI", api_key="test-key")
        assert isinstance(provider, OpenAIProvider)

        mock_openai.OpenAI.return_value = MagicMock()
        provider = get_provider("Perplexity", api_key="test-key")
        assert isinstance(provider, PerplexityProvider)
