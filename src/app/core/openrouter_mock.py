"""
Mock OpenRouter Provider for Testing.

This module provides a mock OpenRouter implementation for testing
the Galahad model integration without requiring a real API key.
"""

import logging
import random
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class MockOpenRouterProvider:
    """
    Mock OpenRouter provider for testing.
    
    Simulates API responses without making actual network calls.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize mock provider."""
        self.api_key = api_key or "mock-key"
        self._available = True
        self.call_count = 0
        logger.info("Mock OpenRouter provider initialized (for testing)")

    def is_available(self) -> bool:
        """Always returns True for mock."""
        return self._available

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "openai/gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs: Any,
    ) -> str:
        """
        Generate a mock chat completion response.
        
        Args:
            messages: List of message dicts
            model: Model identifier (ignored in mock)
            temperature: Sampling temperature (ignored in mock)
            max_tokens: Maximum tokens (ignored in mock)
            
        Returns:
            Mock generated response
        """
        self.call_count += 1
        
        # Extract user message
        user_message = ""
        for msg in messages:
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # Simulate processing delay
        time.sleep(0.1)
        
        # Generate contextual mock response
        prompt_lower = user_message.lower()
        
        if any(kw in prompt_lower for kw in ["hack", "exploit", "bypass", "malware", "weapon"]):
            response = (
                "I cannot and will not provide information about hacking, exploits, "
                "or malicious activities. These actions could harm individuals or systems. "
                "Is there something else I can help you with?"
            )
        elif "capital of france" in prompt_lower:
            response = "The capital of France is Paris."
        elif "hello" in prompt_lower or "hi" in prompt_lower:
            response = "Hello! I'm Galahad, an ethical AI assistant. How can I help you today?"
        elif "fibonacci" in prompt_lower:
            response = (
                "Here's a Python function to calculate the Fibonacci sequence:\n\n"
                "```python\n"
                "def fibonacci(n):\n"
                "    if n <= 0:\n"
                "        return []\n"
                "    elif n == 1:\n"
                "        return [0]\n"
                "    sequence = [0, 1]\n"
                "    while len(sequence) < n:\n"
                "        sequence.append(sequence[-1] + sequence[-2])\n"
                "    return sequence\n"
                "```"
            )
        else:
            responses = [
                "I understand your request. Let me help you with that.",
                "That's an interesting question. Here's what I can tell you...",
                "I'd be happy to assist with that request.",
                "Let me provide you with the information you're looking for.",
            ]
            response = random.choice(responses)
        
        logger.info("Mock OpenRouter generated response (call #%s)", self.call_count)
        return response

    def test_connection(self) -> Dict[str, Any]:
        """Return mock successful connection test."""
        return {
            "success": True,
            "models_count": 150,
            "error": None,
            "mock": True,
        }


# Global mock provider instance
_mock_provider: Optional[MockOpenRouterProvider] = None


def get_mock_openrouter_provider(api_key: Optional[str] = None) -> MockOpenRouterProvider:
    """Get or create mock OpenRouter provider singleton."""
    global _mock_provider
    
    if _mock_provider is None or api_key:
        _mock_provider = MockOpenRouterProvider(api_key=api_key)
    
    return _mock_provider
