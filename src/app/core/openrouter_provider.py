"""
OpenRouter API Provider for Project-AI.

This module provides direct OpenRouter API integration for the Galahad model,
enabling real LLM calls instead of static responses.
"""

import logging
import os
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class OpenRouterProvider:
    """
    OpenRouter API provider using OpenAI-compatible SDK.
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenRouter provider.
        
        Args:
            api_key: OpenRouter API key. If None, reads from OPENROUTER_API_KEY env var.
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self._client = None
        
        if self.api_key:
            try:
                import openai
                self._client = openai.OpenAI(
                    api_key=self.api_key,
                    base_url="https://openrouter.ai/api/v1",
                )
                logger.info("OpenRouter provider initialized")
            except ImportError:
                logger.error("openai package not installed. Run: pip install openai")
                self._client = None
            except Exception as e:
                logger.error("Failed to initialize OpenRouter client: %s", e)
                self._client = None
        else:
            logger.warning("OPENROUTER_API_KEY not set")

    def is_available(self) -> bool:
        """Check if OpenRouter is available."""
        return self._client is not None and self.api_key is not None

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "openai/gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> str:
        """
        Create a chat completion using OpenRouter API.
        
        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Model identifier (e.g., 'openai/gpt-3.5-turbo', 'anthropic/claude-3-opus')
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Generated text response
            
        Raises:
            RuntimeError: If API call fails or provider not available
        """
        if not self._client:
            raise RuntimeError(
                "OpenRouter not available. Check OPENROUTER_API_KEY and openai installation."
            )

        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                extra_headers={
                    "HTTP-Referer": "https://project-ai.local",
                    "X-Title": "Project-AI Galahad",
                },
                **kwargs,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("OpenRouter API error: %s", e)
            raise RuntimeError(f"OpenRouter API call failed: {e}")

    def test_connection(self) -> Dict[str, Any]:
        """
        Test OpenRouter connectivity by listing available models.
        
        Returns:
            Dict with 'success', 'models_count', and 'error' keys
        """
        if not self._client:
            return {
                "success": False,
                "error": "OpenRouter client not initialized. Check API key.",
                "models_count": 0,
            }
        
        try:
            import requests
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://project-ai.local",
                "X-Title": "Project-AI Galahad",
            }
            
            resp = requests.get(
                "https://openrouter.ai/api/v1/models",
                headers=headers,
                timeout=30,
            )
            
            if resp.status_code == 200:
                models = resp.json().get("data", [])
                return {
                    "success": True,
                    "models_count": len(models),
                    "error": None,
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {resp.status_code}: {resp.text}",
                    "models_count": 0,
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "models_count": 0,
            }


# Global provider instance
_openrouter_provider: Optional[OpenRouterProvider] = None


def get_openrouter_provider(api_key: Optional[str] = None) -> OpenRouterProvider:
    """
    Get or create OpenRouter provider singleton.
    
    Args:
        api_key: Optional API key override
        
    Returns:
        OpenRouterProvider instance
    """
    global _openrouter_provider
    
    if _openrouter_provider is None or api_key:
        _openrouter_provider = OpenRouterProvider(api_key=api_key)
    
    return _openrouter_provider
