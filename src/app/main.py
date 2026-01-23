#!/usr/bin/env python3
"""
Main entry point for the AI Desktop Application with AGI Identity System.

CRITICAL: This is the trust root - where CognitionKernel is instantiated
and all subsystems are wired together. No execution happens without kernel authority.
"""

import logging
import os
import sys

from dotenv import load_dotenv
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication

from app.core.cognition_kernel import CognitionKernel
from app.core.council_hub import CouncilHub
from app.core.governance import Triumvirate as GovernanceTriumvirate
from app.core.intelligence_engine import IdentityIntegratedIntelligenceEngine
from app.core.kernel_integration import set_global_kernel
from app.core.memory_engine import MemoryEngine
from app.core.reflection_cycle import ReflectionCycle
from app.gui.dashboard_main import DashboardMainWindow
from src.cognition.triumvirate import Triumvirate

# Initialize logger early
logger = logging.getLogger(__name__)

# Global instances (trust root)
_global_identity_engine = None
_global_cognition_kernel = None
_global_council_hub = None


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


def get_cognition_kernel() -> CognitionKernel:
    """Get the global CognitionKernel instance.

    This is the trust root for all executions. Only instantiated once in main().

    Returns:
        CognitionKernel: Global kernel instance
    """
    global _global_cognition_kernel
    if _global_cognition_kernel is None:
        logger.error("CognitionKernel not initialized. Call initialize_kernel() first.")
        raise RuntimeError("CognitionKernel not initialized")
    return _global_cognition_kernel


def initialize_kernel() -> CognitionKernel:
    """Initialize the CognitionKernel with all subsystems.

    CRITICAL: This is the trust root where all authority originates.
    Called once during application startup.

    Returns:
        CognitionKernel: Initialized kernel with all subsystems
    """
    global _global_cognition_kernel

    if _global_cognition_kernel is not None:
        logger.warning("CognitionKernel already initialized")
        return _global_cognition_kernel

    logger.info("Initializing CognitionKernel (trust root)")

    # Initialize subsystems (in dependency order)
    try:
        # 1. Identity System (immutable snapshots for governance)
        identity_system = get_identity_engine()

        # 2. Memory Engine (four-channel recording)
        try:
            memory_engine = MemoryEngine(data_dir="data")
        except Exception as e:
            logger.warning("MemoryEngine initialization failed: %s, using fallback", e)
            memory_engine = None

        # 3. Governance System (Four Laws enforcement)
        try:
            governance_system = GovernanceTriumvirate()
        except Exception as e:
            logger.warning(
                f"GovernanceTriumvirate initialization failed: {e}, using fallback"
            )
            governance_system = None

        # 4. Reflection Engine (post-hoc reasoning)
        try:
            reflection_engine = ReflectionCycle(data_dir="data")
        except Exception as e:
            logger.warning(
                f"ReflectionCycle initialization failed: {e}, using fallback"
            )
            reflection_engine = None

        # 5. Triumvirate (Galahad, Cerberus, Codex)
        try:
            triumvirate = Triumvirate()
            logger.info(
                "Triumvirate initialized: Galahad, Cerberus, Codex Deus Maximus"
            )
        except Exception as e:
            logger.warning("Triumvirate initialization failed: %s, using fallback", e)
            triumvirate = None

        # 6. Create CognitionKernel with all subsystems
        kernel = CognitionKernel(
            identity_system=identity_system,
            memory_engine=memory_engine,
            governance_system=governance_system,
            reflection_engine=reflection_engine,
            triumvirate=triumvirate,
            data_dir="data",
        )

        _global_cognition_kernel = kernel

        # Set as global kernel for agents
        set_global_kernel(kernel)

        logger.info("✅ CognitionKernel initialized successfully")
        logger.info("   - Identity: ✓")
        logger.info("   - Memory: %s", '✓' if memory_engine else '✗ (fallback)')
        logger.info("   - Governance: %s", '✓' if governance_system else '✗ (fallback)')
        logger.info("   - Reflection: %s", '✓' if reflection_engine else '✗ (fallback)')
        logger.info("   - Triumvirate: %s", '✓' if triumvirate else '✗ (fallback)')
        logger.info("🔒 Kernel syscall boundary active - all execution governed")

        return kernel

    except Exception as e:
        logger.error("Failed to initialize CognitionKernel: %s", e)
        raise


def initialize_council_hub(kernel: CognitionKernel) -> CouncilHub:
    """Initialize CouncilHub with kernel injection.

    All agents registered in CouncilHub will route through the kernel.

    Args:
        kernel: CognitionKernel instance to inject into agents

    Returns:
        CouncilHub: Initialized hub with kernel-routed agents
    """
    global _global_council_hub

    logger.info("Initializing CouncilHub with kernel injection")

    hub = CouncilHub(autolearn_interval=60.0, kernel=kernel)
    hub.register_project(name="Project-AI")

    _global_council_hub = hub

    logger.info("✅ CouncilHub initialized with kernel-routed agents")
    logger.info("   - Registered agents: %s", len(hub.list_agents()))

    return hub


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
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("logs/app.log"), logging.StreamHandler()],
    )

    logger.info("Environment setup complete")
    logger.info("AGI Identity System directories created")


def main():
    """Main application entry point.

    CRITICAL: This is the trust root where CognitionKernel is instantiated.
    All subsystems are wired through the kernel here.
    """
    # Setup environment
    setup_environment()

    logger.info("=" * 60)
    logger.info("🚀 Starting Project-AI with CognitionKernel governance")
    logger.info("=" * 60)

    # Initialize CognitionKernel (trust root)
    kernel = initialize_kernel()

    # Initialize CouncilHub with kernel injection
    council_hub = initialize_council_hub(kernel)

    # Start autonomous learning (optional)
    # council_hub.start_autonomous_learning()

    logger.info("=" * 60)
    logger.info("✅ All systems initialized and governed by CognitionKernel")
    logger.info("=" * 60)

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

    # Make subsystems accessible to the dashboard
    if hasattr(app_window, "set_identity_engine"):
        app_window.set_identity_engine(get_identity_engine())
    if hasattr(app_window, "set_cognition_kernel"):
        app_window.set_cognition_kernel(kernel)
    if hasattr(app_window, "set_council_hub"):
        app_window.set_council_hub(council_hub)

    app_window.show()

    logger.info("🎨 GUI launched - kernel governance active")

    app.exec()

    # Cleanup
    logger.info("Shutting down...")
    if council_hub:
        council_hub.stop_autonomous_learning()

    logger.info("Shutdown complete")


if __name__ == "__main__":
    main()

# Integrated generated module with AGI Identity System and CognitionKernel
