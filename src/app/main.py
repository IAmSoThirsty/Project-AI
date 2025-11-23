#!/usr/bin/env python3
"""
Main entry point for the AI Desktop Application.
"""

import sys
import os
from dotenv import load_dotenv  # type: ignore
from PyQt6.QtWidgets import QApplication, QDialog  # type: ignore
from PyQt6.QtGui import QFont  # type: ignore
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
    
    # GLORIOUS STYLING - Use modern font and apply dark theme
    try:
        default_font = QFont("Segoe UI", 11)
        app.setFont(default_font)
    except Exception:
        fallback_font = QFont("Arial", 11)
        app.setFont(fallback_font)
    
    # Load the glorious dark theme stylesheet
    try:
        style_path = os.path.join(
            os.path.dirname(__file__),
            'gui',
            'styles_dark.qss'
        )
        if os.path.exists(style_path):
            with open(style_path, 'r', encoding='utf-8') as f:
                app.setStyleSheet(f.read())
    except Exception as e:
        print(f"Could not load stylesheet: {e}")
    
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
