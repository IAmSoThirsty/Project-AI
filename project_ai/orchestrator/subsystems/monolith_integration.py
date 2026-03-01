"""
Thirstys-Monolith Governance & Policy Engine Integration
Provides schematic enforcement and policy validation
"""

import logging
import sys
from pathlib import Path
from typing import Any, Dict

# Add Monolith to path
monolith_path = (
    Path(__file__).parent.parent.parent.parent
    / "external"
    / "Thirstys-Monolith"
    / "src"
)
sys.path.insert(0, str(monolith_path))

try:
    from app.agents.codex_deus_maximus import create_codex

    MONOLITH_AVAILABLE = True
except ImportError as e:
    MONOLITH_AVAILABLE = False
    import_error = str(e)


class MonolithIntegration:
    """Integrates Thirstys-Monolith schematic guardian and policy enforcement"""

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.active = False

        if not MONOLITH_AVAILABLE:
            self.logger.warning(f"Monolith not available: {import_error}")
            self.guardian = None
            return

        try:
            self.guardian = create_codex()
            self.logger.info("Codex Deus Maximus guardian loaded")
        except Exception as e:
            self.logger.warning(f"Could not create Codex Deus Maximus: {e}")
            self.guardian = None

    def start(self) -> None:
        """Start Monolith governance engine"""
        self.logger.info("=" * 60)
        self.logger.info("STARTING THIRSTYS-MONOLITH GOVERNANCE ENGINE")
        self.logger.info("=" * 60)

        if not MONOLITH_AVAILABLE or not self.guardian:
            self.logger.warning(
                "Guardian not available - skipping schematic enforcement"
            )
            self.active = False
            return

        # Run schematic enforcement
        try:
            self.logger.info("Running schematic enforcement...")
            result = self.guardian.run_schematic_enforcement()

            if result.get("status") == "pass":
                self.logger.info("✓ Schematic validation PASSED")
                self.active = True
            else:
                issues = result.get("issues", [])
                self.logger.warning(f"Schematic issues detected: {len(issues)} issues")
                for issue in issues[:5]:  # Show first 5
                    self.logger.warning(f"  - {issue}")
                # Still activate even with warnings
                self.active = True

        except Exception as e:
            self.logger.error(f"Schematic enforcement failed: {e}")
            self.active = False
            raise

        self.logger.info("✓ Monolith Governance Engine OPERATIONAL")

    def stop(self) -> None:
        """Stop Monolith"""
        self.logger.info("Stopping Monolith Governance Engine...")
        self.active = False

    def get_status(self) -> Dict[str, Any]:
        """Get Monolith status"""
        return {
            "active": self.active,
            "available": MONOLITH_AVAILABLE,
            "guardian_available": self.guardian is not None,
        }
