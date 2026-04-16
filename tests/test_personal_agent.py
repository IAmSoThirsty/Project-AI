from __future__ import annotations

import json
from pathlib import Path

from app.personal_agent import CaregiverScribe, PersonalAgent


def write_config(tmp_path: Path) -> Path:
    instructions = tmp_path / "instructions.md"
    instructions.write_text("You are a test personal agent.", encoding="utf-8")
    config = {
        "backend": "openai_compatible",
        "base_url": "http://localhost:1234/v1",
        "model": "local-model",
        "instructions_file": str(instructions),
        "profile_file": str(tmp_path / "profile.json"),
        "notes_file": str(tmp_path / "notes.md"),
        "event_log_file": str(tmp_path / "events.jsonl"),
        "training_export_file": str(tmp_path / "training" / "chat_export.jsonl"),
        "obsidian_vault_path": str(tmp_path / "vault"),
        "scribe_folder": "_Scribe/Project-AI",
        "repo_root": str(tmp_path / "repo"),
    }
    config_path = tmp_path / "config.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    return config_path


def test_personal_agent_learns_and_forgets_memory(tmp_path: Path) -> None:
    agent = PersonalAgent.from_config(write_config(tmp_path))

    fact_id = agent.add_memory("fact", "The user prefers direct answers.")
    pref_id = agent.add_memory("preference", "Use Python examples first.")

    memory = agent.format_memory()
    assert fact_id == "fact-001"
    assert pref_id == "pref-001"
    assert "The user prefers direct answers." in memory
    assert "Use Python examples first." in memory

    assert agent.forget_memory(fact_id) is True
    memory = agent.format_memory()
    assert "The user prefers direct answers." not in memory
    assert "Use Python examples first." in memory


def test_personal_agent_exports_training_data(tmp_path: Path) -> None:
    agent = PersonalAgent.from_config(write_config(tmp_path))
    agent.log_chat_turn("Hello", "Hi there")

    exported = agent.export_training_data()
    export_path = agent.config.training_export_file
    rows = export_path.read_text(encoding="utf-8").splitlines()

    assert exported == 1
    assert len(rows) == 1
    example = json.loads(rows[0])
    assert example["messages"][1] == {"role": "user", "content": "Hello"}
    assert example["messages"][2] == {"role": "assistant", "content": "Hi there"}


def test_personal_agent_prompt_includes_memory_and_project_context(
    tmp_path: Path,
) -> None:
    agent = PersonalAgent.from_config(write_config(tmp_path))
    agent.add_memory("goal", "Build a private local agent.")

    prompt = agent.build_system_prompt()

    assert "Project-AI integration context" in prompt
    assert "Build a private local agent." in prompt


def test_caregiver_scribe_absorbs_vault_and_learns_repo(tmp_path: Path) -> None:
    vault = tmp_path / "vault"
    repo = tmp_path / "repo"
    (vault / ".obsidian").mkdir(parents=True)
    repo.mkdir()
    (vault / "Home.md").write_text(
        "# Home\n\nSee [[Project]] #start\n",
        encoding="utf-8",
    )
    (repo / "README.md").write_text("# Repo\n\nHello\n", encoding="utf-8")
    (repo / "app.py").write_text(
        "class Example:\n    pass\n\ndef run():\n    return True\n",
        encoding="utf-8",
    )

    config_path = write_config(tmp_path)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["obsidian_vault_path"] = str(vault)
    config["repo_root"] = str(repo)
    config_path.write_text(json.dumps(config), encoding="utf-8")

    scribe = CaregiverScribe.from_config(config_path)
    vault_result = scribe.absorb_vault()
    repo_result = scribe.learn_repo()

    assert vault_result["records"] == 1
    assert repo_result["records"] == 2
    assert (vault / "_Scribe" / "Project-AI" / "Vault Navigation Map.md").exists()
    assert (vault / "_Scribe" / "Project-AI" / "Project-AI File Index.md").exists()
