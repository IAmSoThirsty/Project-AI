#!/usr/bin/env python3
"""
IncrediBuild Quick Start Script
Initializes and tests IncrediBuild distributed compilation
"""

import sys
import logging
from pathlib import Path

# Setup path
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("QuickStart")


def main():
    logger.info("=" * 80)
    logger.info("  IncrediBuild Quick Start")
    logger.info("=" * 80)
    logger.info("")
    
    # Step 1: Check configuration
    logger.info("Step 1: Checking configuration...")
    config_path = PROJECT_ROOT / "incredibuild" / "config" / "incredibuild.yaml"
    
    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        logger.info("Please copy incredibuild.example.yaml to incredibuild.yaml and configure it")
        return False
    
    logger.info(f"✅ Configuration found: {config_path}")
    logger.info("")
    
    # Step 2: Import coordinator
    logger.info("Step 2: Importing IncrediBuild coordinator...")
    try:
        from incredibuild_coordinator import IncrediBuildCoordinator
        logger.info("✅ Coordinator imported successfully")
    except ImportError as e:
        logger.error(f"Failed to import coordinator: {e}")
        return False
    logger.info("")
    
    # Step 3: Initialize
    logger.info("Step 3: Initializing IncrediBuild...")
    coordinator = IncrediBuildCoordinator()
    
    if not coordinator.initialize():
        logger.error("Failed to initialize IncrediBuild")
        logger.info("This is a demo - initialization 'failure' is expected without cloud credentials")
        logger.info("IncrediBuild will work in simulation mode")
    else:
        logger.info("✅ IncrediBuild initialized successfully")
    logger.info("")
    
    # Step 4: Run a test build
    logger.info("Step 4: Running test build...")
    logger.info("This will simulate a distributed build with mock nodes")
    logger.info("")
    
    try:
        success = coordinator.build(target="all", clean=False)
        
        if success:
            logger.info("")
            logger.info("=" * 80)
            logger.info("  ✅ QUICK START SUCCESSFUL!")
            logger.info("=" * 80)
            logger.info("")
            logger.info("Next steps:")
            logger.info("  1. Configure cloud credentials in incredibuild/config/incredibuild.yaml")
            logger.info("  2. Run: python incredibuild_coordinator.py init")
            logger.info("  3. Run: python incredibuild_coordinator.py build --target all")
            logger.info("  4. Monitor: python incredibuild/monitoring/dashboard.py")
            logger.info("")
            logger.info("Documentation: incredibuild/README.md")
            logger.info("Benchmarks: incredibuild/benchmarks/")
            logger.info("")
            return True
        else:
            logger.error("Test build failed")
            return False
            
    except Exception as e:
        logger.error(f"Error during test build: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        coordinator.cleanup()


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
