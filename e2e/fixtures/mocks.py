"""
Mock Services for E2E Tests

Provides mock implementations of external services for testing without
actual API calls.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class MockOpenAIClient:
    """Mock OpenAI API client for testing."""

    def __init__(self):
        """Initialize mock OpenAI client."""
        self.calls: list[dict[str, Any]] = []

    def chat_completions_create(
        self,
        model: str,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Mock chat completions endpoint.

        Args:
            model: Model name
            messages: Chat messages
            **kwargs: Additional arguments

        Returns:
            Mock completion response
        """
        self.calls.append(
            {
                "method": "chat.completions.create",
                "model": model,
                "messages": messages,
                "kwargs": kwargs,
            }
        )

        return {
            "id": "chatcmpl-mock-123",
            "object": "chat.completion",
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a mock response from the AI assistant.",
                    },
                    "finish_reason": "stop",
                }
            ],
        }

    def images_generate(
        self,
        prompt: str,
        n: int = 1,
        size: str = "1024x1024",
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Mock image generation endpoint.

        Args:
            prompt: Image prompt
            n: Number of images
            size: Image size
            **kwargs: Additional arguments

        Returns:
            Mock image generation response
        """
        self.calls.append(
            {
                "method": "images.generate",
                "prompt": prompt,
                "n": n,
                "size": size,
                "kwargs": kwargs,
            }
        )

        return {
            "created": 1234567890,
            "data": [
                {
                    "url": f"https://mock-image-url.example.com/image_{i}.png"
                }
                for i in range(n)
            ],
        }

    def get_call_count(self) -> int:
        """Get total number of API calls made."""
        return len(self.calls)

    def get_calls_by_method(self, method: str) -> list[dict[str, Any]]:
        """Get calls filtered by method name."""
        return [call for call in self.calls if call["method"] == method]

    def reset(self) -> None:
        """Reset call history."""
        self.calls = []


class MockHuggingFaceClient:
    """Mock HuggingFace API client for testing."""

    def __init__(self):
        """Initialize mock HuggingFace client."""
        self.calls: list[dict[str, Any]] = []

    def text_to_image(
        self,
        prompt: str,
        model: str = "stabilityai/stable-diffusion-2-1",
        **kwargs: Any,
    ) -> bytes:
        """Mock text-to-image generation.

        Args:
            prompt: Image prompt
            model: Model name
            **kwargs: Additional arguments

        Returns:
            Mock image bytes
        """
        self.calls.append(
            {
                "method": "text_to_image",
                "prompt": prompt,
                "model": model,
                "kwargs": kwargs,
            }
        )

        # Return mock image bytes (1x1 PNG)
        return b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"

    def get_call_count(self) -> int:
        """Get total number of API calls made."""
        return len(self.calls)

    def reset(self) -> None:
        """Reset call history."""
        self.calls = []


class MockEmailService:
    """Mock email service for testing."""

    def __init__(self):
        """Initialize mock email service."""
        self.sent_emails: list[dict[str, Any]] = []

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        from_addr: str | None = None,
        **kwargs: Any,
    ) -> bool:
        """Mock send email.

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            from_addr: Sender email
            **kwargs: Additional arguments

        Returns:
            True (always succeeds in mock)
        """
        self.sent_emails.append(
            {
                "to": to,
                "subject": subject,
                "body": body,
                "from": from_addr,
                "kwargs": kwargs,
            }
        )
        logger.info(f"Mock email sent to {to}: {subject}")
        return True

    def get_sent_email_count(self) -> int:
        """Get number of emails sent."""
        return len(self.sent_emails)

    def get_emails_to(self, recipient: str) -> list[dict[str, Any]]:
        """Get emails sent to a specific recipient."""
        return [
            email for email in self.sent_emails if email["to"] == recipient
        ]

    def reset(self) -> None:
        """Reset sent emails."""
        self.sent_emails = []


class MockGeolocationService:
    """Mock geolocation service for testing."""

    def __init__(self):
        """Initialize mock geolocation service."""
        self.calls: list[str] = []

    def get_location_by_ip(self, ip_address: str) -> dict[str, Any]:
        """Mock IP geolocation lookup.

        Args:
            ip_address: IP address to look up

        Returns:
            Mock location data
        """
        self.calls.append(ip_address)

        return {
            "ip": ip_address,
            "city": "Test City",
            "region": "Test Region",
            "country": "Test Country",
            "latitude": 40.7128,
            "longitude": -74.0060,
        }

    def get_call_count(self) -> int:
        """Get number of lookups performed."""
        return len(self.calls)

    def reset(self) -> None:
        """Reset call history."""
        self.calls = []


# Global mock instances
mock_openai = MockOpenAIClient()
mock_huggingface = MockHuggingFaceClient()
mock_email = MockEmailService()
mock_geolocation = MockGeolocationService()


def reset_all_mocks() -> None:
    """Reset all mock services."""
    mock_openai.reset()
    mock_huggingface.reset()
    mock_email.reset()
    mock_geolocation.reset()
    logger.info("All mock services reset")
