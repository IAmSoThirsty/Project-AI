"""
Start Thirsty Super Kernel as a Live Service

Runs the kernel continuously, monitoring for commands and threats.
"""

import logging
import sys
import time
from pathlib import Path

# Add kernel to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from kernel.thirsty_super_kernel import SystemConfig, ThirstySuperKernel

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_kernel_service():
    """Run kernel as continuous service"""

    print("\n" + "=" * 70)
    print("THIRSTY SUPER KERNEL - STARTING AS LIVE SERVICE")
    print("=" * 70 + "\n")

    # Initialize kernel
    kernel = ThirstySuperKernel(
        config=SystemConfig(
            enable_ai_detection=True, enable_deception=True, enable_visualization=True
        )
    )

    logger.info("✅ Kernel initialized successfully")
    logger.info("🔥 Kernel is now LIVE and monitoring")
    logger.info("")
    logger.info("Status:")
    logger.info("  - Version: %s", kernel.VERSION)
    logger.info("  - AI Detection: %s", 'ACTIVE' if kernel.config.enable_ai_detection else 'DISABLED')
    logger.info("  - Deception: %s", 'ACTIVE' if kernel.config.enable_deception else 'DISABLED')
    logger.info("  - Visualization: %s", 'ACTIVE' if kernel.config.enable_visualization else 'DISABLED')

    if hasattr(kernel, "learning_engine") and kernel.learning_engine:
        logger.info("  - Learning Engine: ACTIVE")

    if hasattr(kernel, "split_screen") and kernel.split_screen:
        logger.info("  - Advanced Visualizations: ACTIVE")

    logger.info("")
    logger.info("=" * 70)
    logger.info("KERNEL RUNNING - Press Ctrl+C to stop")
    logger.info("=" * 70 + "\n")

    # Run demo command sequence to show it's working
    logger.info("Running test command sequence to demonstrate live operation...")
    logger.info("")

    test_commands = [
        ("Normal user", 1001, "whoami"),
        ("Normal user", 1001, "ls -la"),
        ("Attacker", 666, "sudo cat /etc/shadow"),
        ("Attacker", 666, "grep root /etc/shadow"),
    ]

    for label, user_id, cmd in test_commands:
        logger.info("[%s %s] Executing: %s", label, user_id, cmd)
        result = kernel.execute_command(user_id, cmd)
        logger.info("  → Layer %s: %s", result.get('current_layer', result.get('layer', '?')), result['status'])
        logger.info("")
        time.sleep(1)

    logger.info("=" * 70)
    logger.info("Test sequence complete. Kernel remains ACTIVE.")
    logger.info("=" * 70 + "\n")

    # Keep running
    try:
        logger.info("Kernel is now in monitoring mode...")
        logger.info("(In production, this would monitor incoming commands)")
        logger.info("(For now, kernel is ready and waiting)")
        logger.info("")

        # Show status every 30 seconds
        counter = 0
        while True:
            time.sleep(30)
            counter += 1
            status = kernel.get_system_status()
            logger.info("[Heartbeat %s] Kernel ACTIVE - Commands: %s, Threats: %s", counter, status['total_commands'], status['threats_detected'])

    except KeyboardInterrupt:
        logger.info("\n\n🛑 Kernel shutdown requested")
        logger.info("Cleaning up...")
        logger.info("✅ Kernel stopped gracefully")
        print("\n")


if __name__ == "__main__":
    run_kernel_service()
