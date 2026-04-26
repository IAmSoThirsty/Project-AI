"""External ecosystem bridge for governed companion-repository integration.

This module discovers and normalizes capabilities from companion repositories
so they can be surfaced through the governance pipeline in a deterministic,
read-only fashion.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ExternalRepositorySpec:
    """Descriptor for a companion repository path."""

    key: str
    path: str
    category: str


@dataclass
class ExternalRepositoryInventory:
    """Normalized inventory for a discovered companion repository."""

    key: str
    path: str
    exists: bool
    category: str
    files: list[str] = field(default_factory=list)
    capabilities: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ExternalEcosystemBridge:
    """Discovers and summarizes companion repositories for governance use."""

    def __init__(self, repository_specs: list[ExternalRepositorySpec] | None = None):
        self.repository_specs = repository_specs or self._default_specs()

    def inventory(self) -> list[ExternalRepositoryInventory]:
        """Collect inventory for all configured companion repositories."""
        inventories: list[ExternalRepositoryInventory] = []
        for spec in self.repository_specs:
            inventories.append(self._inventory_one(spec))
        return inventories

    def governance_context(self) -> dict[str, Any]:
        """Build governance-facing capability summary for downstream policy usage."""
        inventories = self.inventory()
        available = [inv for inv in inventories if inv.exists]
        return {
            "available_repositories": len(available),
            "configured_repositories": len(inventories),
            "repository_keys": [inv.key for inv in available],
            "capabilities": {
                inv.key: inv.capabilities for inv in available
            },
        }

    def _inventory_one(self, spec: ExternalRepositorySpec) -> ExternalRepositoryInventory:
        path_obj = Path(spec.path)
        inv = ExternalRepositoryInventory(
            key=spec.key,
            path=spec.path,
            exists=path_obj.exists(),
            category=spec.category,
        )

        if not inv.exists:
            return inv

        try:
            inv.files = self._top_level_files(path_obj)
            inv.capabilities = self._infer_capabilities(spec.key, path_obj)
            inv.metadata = self._collect_metadata(path_obj)
        except Exception as e:
            logger.error("Failed inventory for %s at %s: %s", spec.key, spec.path, e)
            inv.metadata["error"] = str(e)

        return inv

    @staticmethod
    def _top_level_files(path_obj: Path) -> list[str]:
        entries = sorted(p.name for p in path_obj.iterdir())
        return entries[:50]

    @staticmethod
    def _collect_metadata(path_obj: Path) -> dict[str, Any]:
        metadata: dict[str, Any] = {
            "has_pyproject": (path_obj / "pyproject.toml").exists(),
            "has_requirements": (path_obj / "requirements.txt").exists(),
            "has_readme": any((path_obj / name).exists() for name in ("README.md", "readme.md")),
        }

        pyproject = path_obj / "pyproject.toml"
        if pyproject.exists():
            metadata["pyproject_size"] = pyproject.stat().st_size

        return metadata

    def _infer_capabilities(self, key: str, path_obj: Path) -> list[str]:
        if key == "the_fates":
            return self._capabilities_the_fates(path_obj)
        if key == "execution_governed":
            return self._capabilities_execution_governed(path_obj)
        if key == "i_believe_in_you":
            return self._capabilities_i_believe(path_obj)
        if key == "knowledge_services":
            return self._capabilities_knowledge_services(path_obj)
        if key == "verifiable_reality":
            return self._capabilities_verifiable_reality(path_obj)
        return []

    @staticmethod
    def _capabilities_the_fates(path_obj: Path) -> list[str]:
        capabilities: list[str] = []
        fates_tool = path_obj / "agents" / "tools" / "the_fates.py"
        architect_tool = path_obj / "agents" / "tools" / "architect_of_flowing.py"
        if fates_tool.exists():
            capabilities.append("substrate_memory_layer")
        if architect_tool.exists():
            capabilities.append("deterministic_work_queue_orchestration")
        return capabilities

    @staticmethod
    def _capabilities_execution_governed(path_obj: Path) -> list[str]:
        capabilities: list[str] = []
        main_py = path_obj / "src" / "caretaker_foundation" / "main.py"
        models_py = path_obj / "src" / "caretaker_foundation" / "models.py"
        if main_py.exists():
            capabilities.append("governed_runtime_api_surface")
        if models_py.exists():
            capabilities.append("mutation_governance_contract_models")
        return capabilities

    @staticmethod
    def _capabilities_i_believe(path_obj: Path) -> list[str]:
        capabilities: list[str] = []
        app_main = path_obj / "app" / "main.py"
        features = path_obj / "app" / "features"
        if app_main.exists():
            capabilities.append("unified_social_reconnection_service")
        if features.exists():
            capabilities.append("modular_feature_router_stack")
        return capabilities

    @staticmethod
    def _capabilities_knowledge_services(path_obj: Path) -> list[str]:
        capabilities: list[str] = []
        py_files = list(path_obj.glob("*.py"))
        if py_files:
            capabilities.append("specialized_domain_service_scripts")
            capabilities.append(f"module_count_{len(py_files)}")
        return capabilities

    @staticmethod
    def _capabilities_verifiable_reality(path_obj: Path) -> list[str]:
        capabilities: list[str] = []
        main_py = path_obj / "app" / "main.py"
        docs_dir = path_obj / "docs"
        if main_py.exists():
            capabilities.append("content_authenticity_api")
        if docs_dir.exists():
            capabilities.append("operational_security_runbooks")
        return capabilities

    @staticmethod
    def _default_specs() -> list[ExternalRepositorySpec]:
        return [
            ExternalRepositorySpec(
                key="the_fates",
                path=os.getenv(
                    "PROJECT_AI_THE_FATES_PATH",
                    r"C:\Users\Quencher\Desktop\Github\Personal Repo's\the_fates",
                ),
                category="governed_memory",
            ),
            ExternalRepositorySpec(
                key="i_believe_in_you",
                path=os.getenv(
                    "PROJECT_AI_I_BELIEVE_PATH",
                    r"C:\Users\Quencher\Desktop\Github\Personal Repo's\I Believe in you - Love Thirsty\I Believe In You",
                ),
                category="social_infrastructure",
            ),
            ExternalRepositorySpec(
                key="execution_governed",
                path=os.getenv(
                    "PROJECT_AI_EXECUTION_GOVERNED_PATH",
                    r"C:\Users\Quencher\Desktop\Github\Personal Repo's\Execution-Governed",
                ),
                category="governance_runtime",
            ),
            ExternalRepositorySpec(
                key="knowledge_services",
                path=os.getenv(
                    "PROJECT_AI_KNOWLEDGE_SERVICES_PATH",
                    r"C:\Users\Quencher\Desktop\Github\Personal Repo's\knowledge_services",
                ),
                category="knowledge_domain_services",
            ),
            ExternalRepositorySpec(
                key="verifiable_reality",
                path=os.getenv(
                    "PROJECT_AI_VERIFIABLE_REALITY_PATH",
                    r"C:\Users\Quencher\Desktop\Github\Personal Repo's\Verifiable Reality Infrastructure (Post-AI Proof Layer)\Verifiable Reality Infrastructure (Post-AI Proof Layer)",
                ),
                category="proof_infrastructure",
            ),
        ]


_external_ecosystem_bridge: ExternalEcosystemBridge | None = None


def get_external_ecosystem_bridge() -> ExternalEcosystemBridge:
    """Return singleton external ecosystem bridge instance."""
    global _external_ecosystem_bridge
    if _external_ecosystem_bridge is None:
        _external_ecosystem_bridge = ExternalEcosystemBridge()
    return _external_ecosystem_bridge


def export_external_ecosystem_inventory_json() -> str:
    """Export inventory to stable JSON for audit/event attachment."""
    bridge = get_external_ecosystem_bridge()
    payload = [item.to_dict() for item in bridge.inventory()]
    return json.dumps(payload, sort_keys=True, indent=2)
