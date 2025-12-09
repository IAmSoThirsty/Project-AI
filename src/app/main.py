#!/usr/bin/env python3
"""
Main entry point for the AI Desktop Application.
"""

import logging
import os
import sys

from dotenv import load_dotenv
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from app.gui.dashboard_main import DashboardMainWindow

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


def main():
    """Main application entry point"""
    # Setup environment
    setup_environment()

    # Create and run application
    app = QApplication(sys.argv)
    # Use a modern, legible default font and slightly larger base size
    try:
        default_font = QFont("Segoe UI", 10)
        app.setFont(default_font)
    except Exception:
        fallback_font = QFont("Arial", 10)
        app.setFont(fallback_font)

    # Show the consolidated dashboard
    app_window = DashboardMainWindow()
    app_window.show()
    app.exec()


if __name__ == "__main__":
    main()

# Integrated generated module
