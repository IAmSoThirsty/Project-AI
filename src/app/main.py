#!/usr/bin/env python3
"""
Main entry point for the AI Desktop Application with AGI Identity System.
"""

import logging
import os
import sys

from dotenv import load_dotenv
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from app.gui.dashboard_main import DashboardMainWindow
from app.core.intelligence_engine import IdentityIntegratedIntelligenceEngine

# Initialize logger early
logger = logging.getLogger(__name__)

# Global identity-integrated intelligence engine instance
_global_identity_engine = None


def get_identity_engine() -> IdentityIntegratedIntelligenceEngine:
    """Get the global identity-integrated intelligence engine instance.
    
    Returns:
        IdentityIntegratedIntelligenceEngine: Global engine instance
    """
    global _global_identity_engine
    if _global_identity_engine is None:
        _global_identity_engine = IdentityIntegratedIntelligenceEngine(data_dir="data")
        logger.info("AGI Identity System initialized")
    return _global_identity_engine


def setup_environment():
    """Setup environment variables and configurations"""
    # Load environment variables from .env file
    load_dotenv()

    # Ensure required directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/identities", exist_ok=True)
    os.makedirs("data/memory", exist_ok=True)
    os.makedirs("data/reflections", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/app.log'),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Environment setup complete")
    logger.info("AGI Identity System directories created")


def main():
    """Main application entry point"""
    # Setup environment
    setup_environment()
    
    # Initialize AGI Identity System
    identity_engine = get_identity_engine()
    logger.info("AGI Identity-Integrated Intelligence Engine ready")
    logger.info("Triumvirate governance active: Galahad, Cerberus, Codex Deus Maximus")

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
    
    # Make identity engine accessible to the dashboard
    if hasattr(app_window, 'set_identity_engine'):
        app_window.set_identity_engine(identity_engine)
    
    app_window.show()
    app.exec()


if __name__ == "__main__":
    main()

# Integrated generated module with AGI Identity System
