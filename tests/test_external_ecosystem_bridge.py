"""Tests for external ecosystem governance bridge."""

from __future__ import annotations

from pathlib import Path

from app.core.governance.external_ecosystem_bridge import (
    ExternalEcosystemBridge,
    ExternalRepositorySpec,
)


def _make_file(path: Path, content: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


class TestExternalEcosystemBridge:
    def test_inventory_detects_known_capabilities(self, tmp_path: Path) -> None:
        the_fates = tmp_path / "the_fates"
        _make_file(the_fates / "agents" / "tools" / "the_fates.py", "# fates")
        _make_file(
            the_fates / "agents" / "tools" / "architect_of_flowing.py",
            "# architect",
        )

        execution_governed = tmp_path / "execution_governed"
        _make_file(
            execution_governed / "src" / "caretaker_foundation" / "main.py",
            "# main",
        )
        _make_file(
            execution_governed / "src" / "caretaker_foundation" / "models.py",
            "# models",
        )

        bridge = ExternalEcosystemBridge(
            repository_specs=[
                ExternalRepositorySpec(
                    key="the_fates",
                    path=str(the_fates),
                    category="governed_memory",
                ),
                ExternalRepositorySpec(
                    key="execution_governed",
                    path=str(execution_governed),
                    category="governance_runtime",
                ),
            ]
        )

        inventory = bridge.inventory()
        assert len(inventory) == 2
        assert all(item.exists for item in inventory)

        by_key = {item.key: item for item in inventory}
        assert "substrate_memory_layer" in by_key["the_fates"].capabilities
        assert (
            "deterministic_work_queue_orchestration"
            in by_key["the_fates"].capabilities
        )
        assert (
            "governed_runtime_api_surface"
            in by_key["execution_governed"].capabilities
        )
        assert (
            "mutation_governance_contract_models"
            in by_key["execution_governed"].capabilities
        )

    def test_governance_context_filters_missing_repositories(self, tmp_path: Path) -> None:
        present = tmp_path / "knowledge_services"
        _make_file(present / "navigator_pathfinder.py", "# module")

        bridge = ExternalEcosystemBridge(
            repository_specs=[
                ExternalRepositorySpec(
                    key="knowledge_services",
                    path=str(present),
                    category="knowledge_domain_services",
                ),
                ExternalRepositorySpec(
                    key="verifiable_reality",
                    path=str(tmp_path / "missing_repo"),
                    category="proof_infrastructure",
                ),
            ]
        )

        context = bridge.governance_context()
        assert context["configured_repositories"] == 2
        assert context["available_repositories"] == 1
        assert context["repository_keys"] == ["knowledge_services"]
        assert "knowledge_services" in context["capabilities"]
        assert any(
            cap.startswith("module_count_")
            for cap in context["capabilities"]["knowledge_services"]
        )
