"""
Gradle Integration Bridge
==========================

Provides Python-to-Gradle integration for the Evolution substrate.
Called from Gradle tasks to enforce constitutional, cognitive, and security policies.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gradle_evolution.api.documentation_generator import DocumentationGenerator
from gradle_evolution.api.verifiability_api import VerifiabilityAPI
from gradle_evolution.audit.accountability import AccountabilitySystem
from gradle_evolution.audit.audit_integration import BuildAuditIntegration
from gradle_evolution.capsules.capsule_engine import CapsuleEngine
from gradle_evolution.capsules.replay_engine import ReplayEngine
from gradle_evolution.cognition.build_cognition import BuildCognitionEngine
from gradle_evolution.cognition.state_integration import BuildStateIntegration
from gradle_evolution.constitutional.engine import ConstitutionalEngine
from gradle_evolution.security.policy_scheduler import PolicyScheduler
from gradle_evolution.security.security_engine import SecurityEngine
from project_ai.engine.state.state_manager import StateManager

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class _RewireDeliberationAdapter:
    """Minimal adapter implementing the interface expected by BuildCognitionEngine."""

    def deliberate(self, decision_type: str, inputs: dict[str, Any]) -> dict[str, Any]:
        tasks = inputs.get("tasks", [])
        return {
            "optimized_order": tasks,
            "reasoning": {
                "decision_type": decision_type,
                "strategy": "identity_preserving_noop",
            },
        }


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

            # Cognition layer
            self.deliberation_engine = _RewireDeliberationAdapter()
            self.build_cognition = BuildCognitionEngine(
                deliberation_engine=self.deliberation_engine,
                config={},
            )
            self.state_integration = BuildStateIntegration(
                state_manager=StateManager(config={}),
                state_dir=self.project_dir / "data" / "build_state",
            )

            # Capsule layer
            self.capsule_engine = CapsuleEngine(
                capsule_dir=self.project_dir / "build" / "capsules"
            )

            # Security layer
            self.security_engine = SecurityEngine(
                config_path=self.project_dir / "config" / "security_hardening.yaml"
            )
            self.policy_scheduler = PolicyScheduler()

            # Audit layer
            self.audit_integration = BuildAuditIntegration(
                audit_log_path=self.project_dir / "cognition" / "governance_audit.log"
            )
            self.accountability_manager = AccountabilitySystem(
                records_dir=self.project_dir / "data" / "accountability"
            )

            # API layer
            self.replay_engine = ReplayEngine(capsule_engine=self.capsule_engine)
            self.verifiability_api = VerifiabilityAPI(
                capsule_engine=self.capsule_engine,
                replay_engine=self.replay_engine,
                audit_integration=self.audit_integration,
            )
            self.doc_generator = DocumentationGenerator(
                capsule_engine=self.capsule_engine,
                state_integration=self.state_integration,
                audit_integration=self.audit_integration,
                output_dir=self.project_dir / "build" / "docs" / "generated",
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

            # Security validation
            security_allowed, security_reason = self.security_engine.validate_path_access(
                agent=context.get("agent", "build_agent"),
                path=context.get("path", "build/reports/evolution"),
                operation=context.get("operation", "write"),
            )
            if not security_allowed:
                result["allowed"] = False
                result["violations"].append(
                    {
                        "layer": "security",
                        "reason": security_reason or "Unknown security violation",
                    }
                )

            # Audit logging
            self.audit_integration.audit_policy_decision(
                decision_type="constitutional",
                action=phase,
                allowed=is_allowed,
                reason=reason,
                metadata=context,
            )

            self.audit_integration.audit_security_event(
                event_type="build_phase_check",
                agent=context.get("agent", "build_agent"),
                path=context.get("path", "build/reports/evolution"),
                operation=context.get("operation", "write"),
                allowed=security_allowed,
                reason=security_reason,
            )

            # Update build cognition
            execution_data = {
                "duration_seconds": context.get("duration_seconds", 0.0),
                "timestamp": datetime.utcnow().isoformat(),
                "result": result,
            }
            self.build_cognition.learn_from_build(
                tasks=[phase],
                execution_data=execution_data,
                success=result["allowed"],
            )

            self.state_integration.record_build_episode(
                build_id=f"{phase}-{int(datetime.utcnow().timestamp())}",
                tasks=[phase],
                result={"success": result["allowed"], **execution_data},
                metadata=context,
            )

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
            artifact_paths = [Path(p) for p in artifacts]
            capsule = self.capsule_engine.create_capsule(
                tasks=[phase],
                input_files=artifact_paths,
                output_files=artifact_paths,
                metadata=metadata,
            )

            # Log capsule creation
            self.audit_integration.audit_capsule_creation(
                capsule_id=capsule.capsule_id,
                tasks=capsule.tasks,
                input_count=len(capsule.inputs),
                output_count=len(capsule.outputs),
                merkle_root=capsule.merkle_root,
            )

            logger.info("✓ Capsule created: %s", capsule.capsule_id)
            return {
                "success": True,
                "capsule_id": capsule.capsule_id,
                "merkle_root": capsule.merkle_root,
                "task_count": len(capsule.tasks),
            }

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
            docs = self.doc_generator.generate_complete_documentation()

            file_paths = [str(path) for path in docs]
            logger.info("✓ Documentation generated: %s files", len(file_paths))
            return {"success": True, "files": file_paths}

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
