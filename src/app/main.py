#!/usr/bin/env python3
"""
Main entry point for the AI Desktop Application.
"""

import os
import sys
import logging

from dotenv import load_dotenv
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from app.gui.leather_book_interface import LeatherBookInterface

# Initialize logger early
logger = logging.getLogger(__name__)


def setup_environment():
    """Setup environment variables and configurations"""
    # Load environment variables from .env file
    load_dotenv()

    # Ensure required directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Set up logging if needed
    # Configure any external APIs (OpenAI, etc.)


def initialize_cerberus_adapter():
    """Initialize CerberusGuard adapter if available."""
    try:
        from app.plugins.cerberus_adapter import CerberusAdapter

        adapter = CerberusAdapter()
        adapter.initialize()
        return adapter
    except Exception:
        logger.info("Cerberus adapter not available in this environment")
        return None


def main():
    """Main application entry point"""
    # Setup environment
    setup_environment()

    # Initialize optional Cerberus guard
    cerberus_adapter = initialize_cerberus_adapter()

    # Create and run application
    app = QApplication(sys.argv)
    # Use a modern, legible default font and slightly larger base size
    try:
        default_font = QFont("Segoe UI", 10)
        app.setFont(default_font)
    except Exception:
        fallback_font = QFont("Arial", 10)
        app.setFont(fallback_font)

    # Use new leather book interface
    app_window = LeatherBookInterface()
    # Attach adapter for potential runtime checks
    if cerberus_adapter is not None:
        app_window.cerberus = cerberus_adapter

    app_window.show()
    app.exec()



if __name__ == "__main__":
    main()
