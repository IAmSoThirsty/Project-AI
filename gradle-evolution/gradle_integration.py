"""
Gradle Integration Bridge
==========================

Provides Python-to-Gradle integration for the Evolution substrate.
Called from Gradle tasks to enforce constitutional, cognitive, and security policies.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gradle_evolution.api.documentation_generator import DocumentationGenerator
from gradle_evolution.api.verifiability_api import VerifiabilityAPI
from gradle_evolution.audit.accountability import AccountabilityManager
from gradle_evolution.audit.audit_integration import BuildAuditIntegration
from gradle_evolution.capsules.capsule_engine import BuildCapsuleEngine
from gradle_evolution.cognition.build_cognition import BuildCognitionEngine
from gradle_evolution.cognition.state_integration import BuildStateManager
from gradle_evolution.constitutional.enforcer import BuildPolicyEnforcer
from gradle_evolution.constitutional.engine import ConstitutionalEngine
from gradle_evolution.security.policy_scheduler import PolicyScheduler
from gradle_evolution.security.security_engine import SecurityEngine

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class GradleEvolutionBridge:
    """
    Bridge between Gradle build system and Python evolution substrate.
    Provides command-line interface for Gradle tasks to call.
    """

    def __init__(self, project_dir: str = "."):
        """
        Initialize the evolution bridge.

        Args:
            project_dir: Project root directory
        """
        self.project_dir = Path(project_dir).resolve()
        self.initialize_components()

    def initialize_components(self) -> None:
        """Initialize all evolution components."""
        logger.info("Initializing Gradle Evolution components...")

        try:
            # Constitutional layer
            self.constitutional_engine = ConstitutionalEngine(
                str(self.project_dir / "policies" / "constitution.yaml")
            )
            self.policy_enforcer = BuildPolicyEnforcer(self.constitutional_engine)

            # Cognition layer
            self.build_cognition = BuildCognitionEngine(
                cognition_dir=str(self.project_dir / "cognition")
            )
            self.state_manager = BuildStateManager(
                state_dir=str(self.project_dir / "data" / "build_state")
            )

            # Capsule layer
            self.capsule_engine = BuildCapsuleEngine(
                capsule_dir=str(self.project_dir / "build" / "capsules")
            )

            # Security layer
            self.security_engine = SecurityEngine(
                config_path=str(self.project_dir / "config" / "security_hardening.yaml")
            )
            self.policy_scheduler = PolicyScheduler(self.security_engine)

            # Audit layer
            self.audit_integration = BuildAuditIntegration(
                audit_log=str(self.project_dir / "cognition" / "governance_audit.log")
            )
            self.accountability_manager = AccountabilityManager(
                data_dir=str(self.project_dir / "data" / "accountability")
            )

            # API layer
            self.verifiability_api = VerifiabilityAPI(
                capsule_engine=self.capsule_engine,
                audit_integration=self.audit_integration,
            )
            self.doc_generator = DocumentationGenerator(
                output_dir=str(self.project_dir / "build" / "docs" / "generated")
            )

            logger.info("✓ All evolution components initialized")

        except Exception as e:
            logger.error("Failed to initialize components: %s", e)
            raise

    def validate_build_phase(
        self, phase: str, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Validate a build phase through all governance layers.

        Args:
            phase: Build phase name (e.g., "compile", "test", "package")
            context: Additional context for validation

        Returns:
            Validation result with status and details
        """
        if context is None:
            context = {}

        logger.info("Validating build phase: %s", phase)

        result = {
            "phase": phase,
            "allowed": True,
            "violations": [],
            "warnings": [],
            "details": {},
        }

        try:
            # Constitutional validation
            is_allowed, reason = self.constitutional_engine.validate_build_action(
                phase, context
            )
            if not is_allowed:
                result["allowed"] = False
                result["violations"].append(
                    {"layer": "constitutional", "reason": reason}
                )

            # Policy enforcement
            policy_result = self.policy_enforcer.enforce_build_policy(phase, context)
            if not policy_result["allowed"]:
                result["allowed"] = False
                result["violations"].extend(policy_result.get("violations", []))
            result["warnings"].extend(policy_result.get("warnings", []))

            # Security validation
            security_result = self.security_engine.validate_action(phase, context)
            if not security_result["allowed"]:
                result["allowed"] = False
                result["violations"].append(
                    {
                        "layer": "security",
                        "reason": security_result.get(
                            "reason", "Unknown security violation"
                        ),
                    }
                )

            # Audit logging
            self.audit_integration.log_build_event(phase, context, result)

            # Update build cognition
            self.build_cognition.record_build_event(phase, context, result)

            logger.info(
                "Validation result: %s", "ALLOWED" if result["allowed"] else "BLOCKED"
            )

        except Exception as e:
            logger.error("Error during validation: %s", e)
            result["allowed"] = False
            result["violations"].append(
                {"layer": "system", "reason": f"Validation error: {str(e)}"}
            )

        return result

    def create_build_capsule(
        self, phase: str, artifacts: list, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """
        Create a deterministic build capsule.

        Args:
            phase: Build phase
            artifacts: List of artifact paths
            metadata: Additional metadata

        Returns:
            Capsule creation result with hash and signature
        """
        logger.info("Creating build capsule for phase: %s", phase)

        if metadata is None:
            metadata = {}

        try:
            capsule = self.capsule_engine.create_capsule(
                phase=phase, artifacts=artifacts, metadata=metadata
            )

            # Log capsule creation
            self.audit_integration.log_build_event(
                "capsule_created",
                {"phase": phase, "capsule_id": capsule["capsule_id"]},
                {"success": True},
            )

            logger.info("✓ Capsule created: %s", capsule["capsule_id"])
            return capsule

        except Exception as e:
            logger.error("Failed to create capsule: %s", e)
            return {"success": False, "error": str(e)}

    def generate_documentation(self) -> dict[str, Any]:
        """
        Generate documentation from current execution state.

        Returns:
            Documentation generation result
        """
        logger.info("Generating evolution documentation...")

        try:
            # Gather state from all components
            state = {
                "constitutional": {
                    "violations": self.constitutional_engine.get_violations(),
                },
                "cognition": self.build_cognition.get_build_history(limit=10),
                "capsules": self.capsule_engine.list_capsules(),
                "audit": self.audit_integration.get_recent_events(limit=50),
                "accountability": self.accountability_manager.list_overrides(),
            }

            # Generate documentation
            docs = self.doc_generator.generate_from_state(state)

            logger.info(
                "✓ Documentation generated: %s files", len(docs.get("files", []))
            )
            return docs

        except Exception as e:
            logger.error("Failed to generate documentation: %s", e)
            return {"success": False, "error": str(e)}


def main():
    """Command-line interface for Gradle integration."""
    if len(sys.argv) < 2:
        print("Usage: python gradle_integration.py <command> [args...]")
        print("Commands:")
        print("  validate-phase <phase> [context_json]")
        print("  create-capsule <phase> <artifacts_json> [metadata_json]")
        print("  generate-docs")
        print("  status")
        sys.exit(1)

    command = sys.argv[1]
    bridge = GradleEvolutionBridge()

    try:
        if command == "validate-phase":
            phase = sys.argv[2]
            context = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
            result = bridge.validate_build_phase(phase, context)
            print(json.dumps(result, indent=2))
            sys.exit(0 if result["allowed"] else 1)

        elif command == "create-capsule":
            phase = sys.argv[2]
            artifacts = json.loads(sys.argv[3])
            metadata = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
            result = bridge.create_build_capsule(phase, artifacts, metadata)
            print(json.dumps(result, indent=2))
            sys.exit(0 if result.get("success", False) else 1)

        elif command == "generate-docs":
            result = bridge.generate_documentation()
            print(json.dumps(result, indent=2))
            sys.exit(0 if result.get("success", True) else 1)

        elif command == "status":
            status = {
                "initialized": True,
                "components": {
                    "constitutional": "✓",
                    "cognition": "✓",
                    "capsules": "✓",
                    "security": "✓",
                    "audit": "✓",
                    "api": "✓",
                },
            }
            print(json.dumps(status, indent=2))
            sys.exit(0)

        else:
            print(f"Unknown command: {command}")
            sys.exit(1)

    except Exception as e:
        logger.error("Command failed: %s", e)
        print(json.dumps({"error": str(e)}, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
