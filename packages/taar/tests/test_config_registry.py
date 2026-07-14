"""Config, registry, and capability contract tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from taar.config import DEFAULT_AUTOMATION_ROOT, load_taar_config
from taar.errors import RegistryError
from taar.models import EvidenceBundle
from taar_test_helpers import edit_yaml

from taar.registry import Registry, get_capabilities_for_agent, load_registry

# --- config ---------------------------------------------------------------


def test_config_loads_safe_defaults_when_taar_toml_missing(tmp_path: Path) -> None:
    config = load_taar_config(tmp_path)
    assert config.facility_mode == "GREEN"
    assert config.automation_root == (tmp_path / DEFAULT_AUTOMATION_ROOT).resolve()


def test_config_loads_taar_toml_when_present(temp_repo: Path) -> None:
    (temp_repo / "taar.toml").write_text('[facility]\nmode = "YELLOW"\n', encoding="utf-8")
    config = load_taar_config(temp_repo)
    assert config.facility_mode == "YELLOW"


def test_config_creates_automation_directories(tmp_path: Path) -> None:
    config = load_taar_config(tmp_path)
    for sub in (
        "evidence",
        "reports",
        "digests",
        "patches",
        "quarantine",
        "audit",
        "locks",
        "cache",
    ):
        assert (config.automation_root / sub).is_dir()


def test_config_does_not_create_registry_files_implicitly(tmp_path: Path) -> None:
    load_taar_config(tmp_path)
    assert not (tmp_path / "registry").exists()


def test_config_resolves_repo_root(temp_repo: Path) -> None:
    nested = temp_repo / "a" / "b"
    nested.mkdir(parents=True)
    config = load_taar_config(nested)
    assert config.repo_root == temp_repo


# --- registry -------------------------------------------------------------


def test_valid_registry_loads(loaded_registry: Registry) -> None:
    assert loaded_registry.validation_errors == []
    assert "heartbeat-reader" in loaded_registry.agents_by_id
    assert "workflow-reader" in loaded_registry.agents_by_id
    assert len(loaded_registry.agents_by_id) == 44


def test_missing_registry_file_fails_closed(temp_repo: Path) -> None:
    (temp_repo / "registry" / "tasks.yaml").unlink()
    with pytest.raises(RegistryError):
        load_registry(temp_repo)


def test_malformed_yaml_rejected(temp_repo: Path) -> None:
    (temp_repo / "registry" / "agents.yaml").write_text("agents: [unclosed", encoding="utf-8")
    with pytest.raises(RegistryError):
        load_registry(temp_repo)


def test_duplicate_agent_id_rejected(temp_repo: Path) -> None:
    def mutate(data: dict[str, Any]) -> None:
        data["agents"].append(dict(data["agents"][0]))

    edit_yaml(temp_repo / "registry" / "agents.yaml", mutate)
    registry = load_registry(temp_repo)
    assert any("Duplicate agent id" in e for e in registry.validation_errors)


def test_duplicate_task_id_rejected(temp_repo: Path) -> None:
    def mutate(data: dict[str, Any]) -> None:
        data["tasks"].append(dict(data["tasks"][0]))

    edit_yaml(temp_repo / "registry" / "tasks.yaml", mutate)
    registry = load_registry(temp_repo)
    assert any("Duplicate task id" in e for e in registry.validation_errors)


def test_unknown_task_reference_rejected(temp_repo: Path) -> None:
    def mutate(data: dict[str, Any]) -> None:
        data["agents"][0]["task_id"] = "no-such-task"

    edit_yaml(temp_repo / "registry" / "agents.yaml", mutate)
    registry = load_registry(temp_repo)
    assert any("unknown task" in e for e in registry.validation_errors)


def test_unknown_capability_reference_rejected(temp_repo: Path) -> None:
    def mutate(data: dict[str, Any]) -> None:
        data["agents"][0]["capability_ids"].append("no-such-capability")

    edit_yaml(temp_repo / "registry" / "agents.yaml", mutate)
    registry = load_registry(temp_repo)
    assert any("unknown capability" in e for e in registry.validation_errors)


def test_unknown_schedule_reference_rejected(temp_repo: Path) -> None:
    def mutate(data: dict[str, Any]) -> None:
        data["agents"][0]["schedule_id"] = "no-such-schedule"

    edit_yaml(temp_repo / "registry" / "agents.yaml", mutate)
    registry = load_registry(temp_repo)
    assert any("unknown schedule" in e for e in registry.validation_errors)


def test_unknown_classification_rejected(temp_repo: Path) -> None:
    def mutate(data: dict[str, Any]) -> None:
        data["classifications"]["MYSTERY"] = {"rank": 99}

    edit_yaml(temp_repo / "registry" / "classifications.yaml", mutate)
    registry = load_registry(temp_repo)
    assert any("Unknown classification level" in e for e in registry.validation_errors)


def test_writer_without_consumes_evidence_rejected(temp_repo: Path) -> None:
    def mutate(data: dict[str, Any]) -> None:
        for task in data["tasks"]:
            if task["id"] == "heartbeat-report":
                task["consumes_evidence_from"] = []

    edit_yaml(temp_repo / "registry" / "tasks.yaml", mutate)
    registry = load_registry(temp_repo)
    assert any("no consumes_evidence_from" in e for e in registry.validation_errors)


def test_task_command_not_allowed_by_agent_rejected(temp_repo: Path) -> None:
    def mutate(data: dict[str, Any]) -> None:
        for task in data["tasks"]:
            if task["id"] == "heartbeat-check":
                task["commands"].append("rm -rf /")

    edit_yaml(temp_repo / "registry" / "tasks.yaml", mutate)
    registry = load_registry(temp_repo)
    assert any("not allowed by agent" in e for e in registry.validation_errors)


def test_task_output_path_not_allowed_by_agent_rejected(temp_repo: Path) -> None:
    def mutate(data: dict[str, Any]) -> None:
        for task in data["tasks"]:
            if task["id"] == "heartbeat-report":
                task["output_paths"] = ["src/evil.py"]

    edit_yaml(temp_repo / "registry" / "tasks.yaml", mutate)
    registry = load_registry(temp_repo)
    assert any("not allowed by agent" in e for e in registry.validation_errors)


def test_first_swarm_destructive_capability_rejected(temp_repo: Path) -> None:
    def mutate(data: dict[str, Any]) -> None:
        data["capabilities"].append(
            {
                "id": "evil-push",
                "description": "push",
                "capability_type": "push",
                "allowed_agents": ["heartbeat-reader"],
                "allowed_commands": ["git push"],
                "allowed_paths": ["**"],
                "classification_ceiling": "OPEN",
                "requires_human_approval": False,
            }
        )

    edit_yaml(temp_repo / "registry" / "capabilities.yaml", mutate)
    registry = load_registry(temp_repo)
    assert any("Forbidden first-swarm capability type" in e for e in registry.validation_errors)


def test_destructive_agent_flag_rejected(temp_repo: Path) -> None:
    def mutate(data: dict[str, Any]) -> None:
        data["agents"][0]["destructive_access"] = True

    edit_yaml(temp_repo / "registry" / "agents.yaml", mutate)
    registry = load_registry(temp_repo)
    assert any("destructive_access" in e for e in registry.validation_errors)


def test_black_evidence_grant_restricted_to_report_types(temp_repo: Path) -> None:
    def mutate(data: dict[str, Any]) -> None:
        for task in data["tasks"]:
            if task["id"] == "heartbeat-check":
                task["black_evidence_allowed"] = True

    edit_yaml(temp_repo / "registry" / "tasks.yaml", mutate)
    registry = load_registry(temp_repo)
    assert any("black_evidence_allowed" in e for e in registry.validation_errors)


# --- capabilities ----------------------------------------------------------


def test_agent_receives_declared_capabilities(loaded_registry: Registry) -> None:
    caps = {c.id for c in get_capabilities_for_agent(loaded_registry, "heartbeat-reader")}
    assert "execute-heartbeat-check" in caps
    assert "write-evidence" in caps


def test_secret_access_only_allowed_for_secret_reader(loaded_registry: Registry) -> None:
    for agent in loaded_registry.agents_by_id.values():
        if agent.secret_access:
            assert agent.id == "secret-reader"


def test_git_allowed_only_for_git_status_reader(loaded_registry: Registry) -> None:
    for agent in loaded_registry.agents_by_id.values():
        if agent.git_allowed:
            assert agent.id == "git-status-reader"


def test_models_serialize_deterministically(sample_evidence_bundle: EvidenceBundle) -> None:
    assert sample_evidence_bundle.canonical_json() == sample_evidence_bundle.canonical_json()
    assert '"evidence_hash"' in sample_evidence_bundle.canonical_json()
