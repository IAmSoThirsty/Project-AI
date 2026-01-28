#!/usr/bin/env python3
"""
Script to populate the Project-AI knowledge base with cybersecurity educational content.

Usage:
    python scripts/populate_cybersecurity_knowledge.py
"""

import logging
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from app.core.ai_systems import MemoryExpansionSystem
from app.core.cybersecurity_knowledge import CybersecurityKnowledge

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


def main():
    """Main function to populate cybersecurity knowledge."""
    try:
        # Initialize the systems
        logger.info("Initializing systems...")
        data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        os.makedirs(data_dir, exist_ok=True)

        # Create cybersecurity knowledge instance
        cyber_knowledge = CybersecurityKnowledge(data_dir=data_dir)
        logger.info("Cybersecurity knowledge module initialized")

        # Create memory system instance
        memory_system = MemoryExpansionSystem(data_dir=data_dir)
        logger.info("Memory system initialized")

        # Export to JSON for reference
        export_path = cyber_knowledge.export_to_json()
        logger.info(f"Exported cybersecurity knowledge to: {export_path}")

        # Integrate with memory system
        logger.info("Integrating cybersecurity knowledge with memory system...")
        cyber_knowledge.integrate_with_memory_system(memory_system)

        # Display summary
        print("\n" + "=" * 80)
        print(cyber_knowledge.get_summary())
        print("=" * 80)
        print("\nCybersecurity knowledge successfully integrated!")
        print("Total sections added: 6")
        print(f"Export location: {export_path}")

        # Verify integration
        logger.info("Verifying integration...")
        stored_malware = memory_system.get_knowledge(
            "cybersecurity_education", "malware"
        )
        if stored_malware:
            logger.info("✓ Malware section verified")
            print("\n✓ Knowledge base integration verified successfully")
        else:
            logger.warning("⚠ Could not verify malware section")

        return 0

    except Exception as e:
        logger.error(f"Error populating cybersecurity knowledge: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
