#!/usr/bin/env python3
"""
Bootstrap Script - Project-AI TARL Integration

This script initializes the core Project-AI system with TARL security policies,
governance, and the CodexDeus escalation system.

Usage:
    python bootstrap.py

Environment Variables:
    TARL_ENABLED: Enable TARL security layer (default: 1)
    CODEX_ESCALATION_ENABLED: Enable CodexDeus escalation (default: 1)
"""

import logging
import sys

from governance.core import GovernanceCore
from kernel.execution import ExecutionKernel
from src.cognition.codex.escalation import CodexDeus
from tarl import TarlRuntime
from tarl.policies.default import DEFAULT_POLICIES

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def bootstrap():
    """
    Bootstrap the Project-AI system with TARL and governance.

    Returns:
        ExecutionKernel: Configured execution kernel ready for use
    """
    logger.info("Starting Project-AI bootstrap sequence...")

    # Initialize TARL runtime with default policies
    logger.info("Initializing TARL runtime...")
    tarl_runtime = TarlRuntime(DEFAULT_POLICIES)
    logger.info(f"Loaded {len(DEFAULT_POLICIES)} TARL policies")

    # Initialize CodexDeus escalation system
    logger.info("Initializing CodexDeus escalation system...")
    codex = CodexDeus()

    # Initialize governance core
    logger.info("Initializing governance core...")
    governance = GovernanceCore()

    # Create execution kernel with all components
    logger.info("Creating execution kernel...")
    kernel = ExecutionKernel(governance, tarl_runtime, codex)

    logger.info("Bootstrap complete! System ready.")
    return kernel


def main():
    """Main entry point for bootstrap script."""
    try:
        kernel = bootstrap()

        # Example: Test the kernel with a safe context
        logger.info("Running bootstrap verification test...")
        test_context = {
            "agent": "bootstrap_test",
            "mutation": False,
            "mutation_allowed": False,
        }

        result = kernel.execute("test_action", test_context)
        logger.info(f"Bootstrap test result: {result}")
        logger.info("✓ Bootstrap verification successful!")

        return 0

    except Exception as e:
        logger.error(f"Bootstrap failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
