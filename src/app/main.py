#!/usr/bin/env python3
"""
Main entry point for the AI Desktop Application.
"""

import sys
import os
from dotenv import load_dotenv
from PyQt6.QtWidgets import QApplication, QDialog
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from app.gui.login import LoginDialog
from app.gui.dashboard import DashboardWindow


def setup_environment():
    """Setup environment variables and configurations"""
    # Load environment variables from .env file
    load_dotenv()

    # Ensure required directories exist
    os.makedirs('data', exist_ok=True)
    os.makedirs('logs', exist_ok=True)

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
    # Show login dialog first
    login = LoginDialog()
    if login.exec() == QDialog.DialogCode.Accepted:
        username = login.username
        initial_tab = getattr(login, 'selected_tab', 0)
        window = DashboardWindow(username=username, initial_tab=initial_tab)
        window.show()
        sys.exit(app.exec())
    else:
        # User cancelled login
        sys.exit(0)


if __name__ == "__main__":
    main()
