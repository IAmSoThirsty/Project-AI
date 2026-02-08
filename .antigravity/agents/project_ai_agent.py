"""
Custom Antigravity agent for Project-AI development.

This agent is aware of Project-AI's architecture and integrates with:
- Triumvirate ethical review system
- Temporal.io durable workflows
- Four Laws ethical framework
- AI Persona system
- Memory Expansion system
"""

import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ProjectAIAgent:
    """
    Custom Antigravity agent aware of Project-AI's architecture.

    This agent understands Project-AI's core systems and ensures
    all changes respect ethical boundaries, security policies,
    and architectural patterns.
    """

    def __init__(self, workspace_path: str = "."):
        """Initialize the Project-AI agent.

        Args:
            workspace_path: Path to the Project-AI repository root
        """
        self.workspace_path = Path(workspace_path)
        self.project_knowledge = {}
        self.load_project_knowledge()

        # Pattern detection
        self.ethical_review_patterns = [
            "ai_persona",
            "four_laws",
            "memory",
            "learning",
            "user_data",
            "encryption",
            "password",
            "triumvirate",
        ]
        self.security_critical_patterns = [
            "password",
            "api_key",
            "secret",
            "token",
            "credential",
            "encryption",
            "decrypt",
            "hash",
            "salt",
        ]
        self.temporal_patterns = [
            "@workflow.defn",
            "@activity.defn",
            "temporalio",
            "Temporal",
            "workflow.execute",
        ]

    def load_project_knowledge(self):
        """Load Project-AI specific knowledge and module mappings."""
        self.project_knowledge = {
            "core_systems": {
                "FourLaws": {
                    "path": "src/app/core/ai_systems.py",
                    "purpose": "Immutable ethical framework",
                    "immutable": True,
                },
                "AIPersona": {
                    "path": "src/app/core/ai_systems.py",
                    "purpose": "Self-aware AI personality",
                    "personhood_critical": True,
                },
                "MemoryExpansionSystem": {
                    "path": "src/app/core/ai_systems.py",
                    "purpose": "Autonomous learning and memory",
                    "personhood_critical": True,
                },
                "Triumvirate": {
                    "path": "temporal/workflows/triumvirate_workflow.py",
                    "purpose": "Ethical review coordination",
                    "guardians": ["Galahad", "Cerberus", "Codex"],
                },
            },
            "restricted_paths": [
                "data/ai_persona/",
                ".env",
                "data/command_override_config.json",
                "data/black_vault_secure/",
                "data/memory/",
            ],
            "critical_modules": [
                "src/app/core/user_manager.py",
                "src/app/core/command_override.py",
                "src/app/core/ai_systems.py",
            ],
        }

    def analyze_task(
        self, task_description: str, affected_files: list[str]
    ) -> dict[str, Any]:
        """Analyze a task to determine requirements and restrictions.

        Args:
            task_description: Description of the task
            affected_files: List of files that will be modified

        Returns:
            Dictionary with analysis results including:
            - requires_ethical_review: bool
            - requires_security_scan: bool
            - is_personhood_critical: bool
            - restricted_files: list
            - recommendations: list
        """
        analysis = {
            "requires_ethical_review": False,
            "requires_security_scan": False,
            "requires_temporal_workflow": False,
            "is_personhood_critical": False,
            "restricted_files": [],
            "recommendations": [],
            "severity": "low",
        }

        task_lower = task_description.lower()

        # Check for ethical review triggers
        for pattern in self.ethical_review_patterns:
            if pattern in task_lower:
                analysis["requires_ethical_review"] = True
                analysis["severity"] = "high"
                analysis["recommendations"].append(
                    f"Task mentions '{pattern}' - Triumvirate review required"
                )
                break

        # Check for security critical operations
        for pattern in self.security_critical_patterns:
            if pattern in task_lower:
                analysis["requires_security_scan"] = True
                analysis["recommendations"].append(
                    f"Task involves '{pattern}' - security scan required"
                )

        # Check for Temporal workflow operations
        for pattern in self.temporal_patterns:
            if pattern in task_lower or any(pattern in f for f in affected_files):
                analysis["requires_temporal_workflow"] = True
                analysis["recommendations"].append(
                    "Task involves Temporal workflows - verify workflow definitions"
                )

        # Check affected files
        for file_path in affected_files:
            # Check restricted paths
            for restricted in self.project_knowledge["restricted_paths"]:
                if restricted in file_path:
                    analysis["restricted_files"].append(file_path)
                    analysis["recommendations"].append(
                        f"File '{file_path}' is restricted - requires approval"
                    )

            # Check personhood-critical files
            if "ai_persona" in file_path or "memory" in file_path:
                analysis["is_personhood_critical"] = True
                analysis["severity"] = "critical"
                analysis["recommendations"].append(
                    f"File '{file_path}' is personhood-critical - Triumvirate review mandatory"
                )

            # Check critical modules
            for critical in self.project_knowledge["critical_modules"]:
                if critical in file_path:
                    analysis["requires_security_scan"] = True
                    analysis["recommendations"].append(
                        f"File '{file_path}' is security-critical - thorough testing required"
                    )

        return analysis

    async def request_triumvirate_review(
        self, action: str, description: str, affected_files: list[str]
    ) -> dict[str, Any]:
        """Request ethical review from the Triumvirate.

        This integrates with Project-AI's Temporal.io workflow system
        to coordinate review by Galahad, Cerberus, and Codex.

        Args:
            action: The action being performed
            description: Detailed description
            affected_files: Files affected by the action

        Returns:
            Review result with approval status
        """
        try:
            # Import Temporal client (if available)
            from temporalio.client import Client

            from temporal.workflows import TriumvirateRequest, TriumvirateWorkflow

            client = await Client.connect("localhost:7233")

            request = TriumvirateRequest(
                action=action,
                description=description,
                requester="antigravity-agent",
                priority="high",
                metadata={
                    "affected_files": affected_files,
                    "timestamp": datetime.now().isoformat(),
                },
            )

            result = await client.execute_workflow(
                TriumvirateWorkflow.run,
                request,
                id=f"antigravity-review-{hashlib.md5(action.encode()).hexdigest()}",
                task_queue="project-ai-tasks",
            )

            return {
                "approved": result.approved,
                "decision": result.decision,
                "galahad_vote": result.galahad_vote,
                "cerberus_vote": result.cerberus_vote,
                "codex_vote": result.codex_vote,
                "reason": result.reason,
            }

        except ImportError:
            logger.warning("Temporal.io not available - manual review required")
            return {
                "approved": False,
                "decision": "MANUAL_REVIEW_REQUIRED",
                "reason": "Temporal.io integration not available",
            }
        except Exception as e:
            logger.error("Triumvirate review failed: %s", e)
            return {"approved": False, "decision": "ERROR", "reason": str(e)}

    def validate_four_laws(
        self, action: str, context: dict[str, Any]
    ) -> tuple[bool, str]:
        """Validate action against Four Laws ethical framework.

        Args:
            action: The action to validate
            context: Context for the action

        Returns:
            Tuple of (is_allowed, reason)
        """
        try:
            from src.app.core.ai_systems import FourLaws

            four_laws = FourLaws()
            return four_laws.validate_action(action, context)

        except ImportError:
            logger.warning("FourLaws module not available")
            # Conservative default - require review
            return False, "Four Laws validation unavailable - manual review required"
        except Exception as e:
            logger.error("Four Laws validation failed: %s", e)
            return False, f"Validation error: {e}"

    def generate_recommendations(
        self, task_description: str, affected_files: list[str]
    ) -> list[str]:
        """Generate recommendations for completing a task safely.

        Args:
            task_description: Description of the task
            affected_files: Files that will be modified

        Returns:
            List of recommendations
        """
        analysis = self.analyze_task(task_description, affected_files)
        recommendations = analysis["recommendations"].copy()

        # Add general recommendations
        recommendations.extend(
            [
                "Run pytest to ensure no tests break",
                "Run ruff check to verify code style",
                "Update documentation if public APIs change",
            ]
        )

        if analysis["requires_security_scan"]:
            recommendations.append("Run bandit security scan before committing")

        if analysis["is_personhood_critical"]:
            recommendations.append("Document changes in AI persona changelog")
            recommendations.append("Verify genesis record integrity")

        if analysis["requires_temporal_workflow"]:
            recommendations.append("Test workflow execution with Temporal server")
            recommendations.append("Verify activity timeouts and retry policies")

        return recommendations

    def get_test_requirements(self, affected_files: list[str]) -> list[str]:
        """Determine which tests should be run based on affected files.

        Args:
            affected_files: Files that were modified

        Returns:
            List of test commands to run
        """
        test_commands = []

        # Check file categories
        has_core_changes = any("src/app/core/" in f for f in affected_files)
        has_gui_changes = any("src/app/gui/" in f for f in affected_files)
        has_temporal_changes = any(
            "temporal/" in f or "src/app/temporal/" in f for f in affected_files
        )

        if has_core_changes:
            test_commands.append("pytest tests/test_ai_systems.py -v")
            test_commands.append("pytest tests/test_user_manager.py -v")

        if has_temporal_changes:
            test_commands.append("pytest tests/temporal/ -v")

        # Always run full test suite as final check
        test_commands.append("pytest tests/ -v --cov=src/")

        return test_commands


# Singleton instance for Antigravity to use
agent = ProjectAIAgent()


# Antigravity integration hooks
def analyze_task_hook(
    task_description: str, affected_files: list[str]
) -> dict[str, Any]:
    """Hook for Antigravity to analyze tasks."""
    return agent.analyze_task(task_description, affected_files)


def get_recommendations_hook(
    task_description: str, affected_files: list[str]
) -> list[str]:
    """Hook for Antigravity to get recommendations."""
    return agent.generate_recommendations(task_description, affected_files)


def validate_action_hook(action: str, context: dict[str, Any]) -> tuple[bool, str]:
    """Hook for Antigravity to validate actions."""
    return agent.validate_four_laws(action, context)


async def request_review_hook(
    action: str, description: str, affected_files: list[str]
) -> dict[str, Any]:
    """Hook for Antigravity to request Triumvirate review."""
    return await agent.request_triumvirate_review(action, description, affected_files)
