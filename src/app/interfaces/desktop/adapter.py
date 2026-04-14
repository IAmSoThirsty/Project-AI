"""
Desktop interface adapter: Routes PyQt6 GUI operations through governance pipeline.

This adapter wraps existing desktop functionality to ensure governance compliance.

Old behavior: GUI → Direct core imports
New behavior: GUI → Desktop Adapter → Router → Governance → Systems
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.runtime.router import route_request

logger = logging.getLogger(__name__)


class DesktopAdapter:
    """
    Adapter that routes desktop GUI operations through governance pipeline.
    
    Usage in GUI code:
        adapter = DesktopAdapter()
        result = adapter.execute("ai.chat", {"prompt": "Hello"})
    """

    def __init__(self, username: str | None = None):
        """
        Initialize desktop adapter.
        
        Args:
            username: Logged-in user (for authorization context)
        """
        self.username = username
        logger.info(f"Desktop adapter initialized for user: {username or 'anonymous'}")

    def execute(self, action: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Execute action through governance pipeline.
        
        Args:
            action: Action identifier (e.g., "ai.chat", "persona.update")
            payload: Action parameters
            
        Returns:
            Response dict with status, result, metadata
        """
        # Add user context
        payload["action"] = action
        payload["user"] = {"username": self.username} if self.username else {}

        # Route through governance pipeline
        response = route_request(source="desktop", payload=payload)
        
        logger.info(
            f"Desktop action {action}: {response['status']}"
        )
        
        return response

    def ai_chat(self, prompt: str, model: str | None = None, provider: str | None = None) -> str:
        """
        Convenience method for AI chat operations.
        
        Args:
            prompt: User prompt
            model: Optional model override
            provider: Optional provider override
            
        Returns:
            AI response text
            
        Raises:
            RuntimeError: If request fails
        """
        response = self.execute(
            "ai.chat",
            {
                "task_type": "chat",
                "prompt": prompt,
                "model": model,
                "provider": provider,
            },
        )

        if response["status"] == "success":
            return response["result"]
        else:
            raise RuntimeError(f"AI chat failed: {response.get('error', 'Unknown error')}")

    def ai_image(self, prompt: str, model: str | None = None, provider: str | None = None) -> Any:
        """
        Convenience method for AI image generation.
        
        Args:
            prompt: Image description
            model: Optional model override
            provider: Optional provider override
            
        Returns:
            Image URL or binary data
            
        Raises:
            RuntimeError: If request fails
        """
        response = self.execute(
            "ai.image",
            {
                "task_type": "image",
                "prompt": prompt,
                "model": model,
                "provider": provider,
            },
        )

        if response["status"] == "success":
            return response["result"]
        else:
            raise RuntimeError(f"Image generation failed: {response.get('error', 'Unknown error')}")

    def persona_update(self, trait: str, value: float) -> bool:
        """
        Update AI persona trait.
        
        Args:
            trait: Trait name (curiosity, empathy, etc.)
            value: New trait value (0.0 - 1.0)
            
        Returns:
            True if successful
            
        Raises:
            RuntimeError: If update fails
        """
        response = self.execute(
            "persona.update",
            {
                "trait": trait,
                "value": value,
            },
        )

        if response["status"] == "success":
            return True
        else:
            raise RuntimeError(f"Persona update failed: {response.get('error', 'Unknown error')}")

    def login(self, username: str, password: str) -> dict[str, Any]:
        """
        Authenticate user.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            Login result with token
            
        Raises:
            RuntimeError: If authentication fails
        """
        response = self.execute(
            "user.login",
            {
                "username": username,
                "password": password,
            },
        )

        if response["status"] == "success":
            self.username = username
            return response["result"]
        else:
            raise RuntimeError(f"Login failed: {response.get('error', 'Unknown error')}")
