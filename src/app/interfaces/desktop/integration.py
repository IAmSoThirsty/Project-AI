"""
Desktop entry point integration with governance pipeline.

This module provides backward compatibility while routing all operations
through the new governance pipeline.

Old pattern: Direct imports
New pattern: Desktop → Adapter → Router → Governance → Systems
"""

from __future__ import annotations

import logging

# Import the desktop adapter
from app.interfaces.desktop import DesktopAdapter

logger = logging.getLogger(__name__)

# Global adapter instance (created after user login)
_desktop_adapter: DesktopAdapter | None = None


def get_desktop_adapter() -> DesktopAdapter:
    """
    Get global desktop adapter instance.
    
    Returns:
        DesktopAdapter instance
        
    Raises:
        RuntimeError: If adapter not initialized (user not logged in)
    """
    if _desktop_adapter is None:
        # Create anonymous adapter for pre-login operations
        return DesktopAdapter()
    return _desktop_adapter


def initialize_desktop_adapter(username: str) -> DesktopAdapter:
    """
    Initialize desktop adapter after user login.
    
    Args:
        username: Logged-in username
        
    Returns:
        Initialized adapter
    """
    global _desktop_adapter
    _desktop_adapter = DesktopAdapter(username=username)
    logger.info(f"Desktop adapter initialized for user: {username}")
    return _desktop_adapter


# Backward compatibility functions for existing GUI code
def execute_ai_chat(prompt: str, model: str | None = None, provider: str | None = None) -> str:
    """Execute AI chat through governance pipeline."""
    adapter = get_desktop_adapter()
    return adapter.ai_chat(prompt, model, provider)


def execute_ai_image(prompt: str, model: str | None = None, provider: str | None = None):
    """Execute AI image generation through governance pipeline."""
    adapter = get_desktop_adapter()
    return adapter.ai_image(prompt, model, provider)


def execute_persona_update(trait: str, value: float) -> bool:
    """Update persona trait through governance pipeline."""
    adapter = get_desktop_adapter()
    return adapter.persona_update(trait, value)
