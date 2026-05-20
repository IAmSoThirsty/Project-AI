"""
PersonalAgent — local-first agent with memory, chat export, and vault/repo learning.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# ── Text signal extraction ────────────────────────────────────────────────────

_FM_PATTERN = re.compile(r"^\s*---\n(.*?)\n---\n?", re.DOTALL)
_YAML_TAGS_LIST = re.compile(r"^tags\s*:\s*\n((?:\s+-\s*.+\n?)*)", re.MULTILINE)
_YAML_TAG_INLINE = re.compile(r"^tag\s*:\s*\[(.*?)\]", re.MULTILINE)
_INLINE_TAG = re.compile(r"(?<!\S)#([A-Za-z][A-Za-z0-9_/\-]*)")


def extract_text_signals(path: Path, content: str) -> dict:
    tags: set[str] = set()
    body = content
    fm_match = _FM_PATTERN.match(content)
    if fm_match:
        fm_text = fm_match.group(1)
        body = content[fm_match.end():]
        for m in _YAML_TAGS_LIST.finditer(fm_text):
            for item in re.findall(r"-\s*(.+)", m.group(1)):
                item = item.strip().strip('"').strip("'")
                tags.add(item.lstrip("#"))
        for m in _YAML_TAG_INLINE.finditer(fm_text):
            for item in m.group(1).split(","):
                item = item.strip().strip('"').strip("'")
                if item:
                    tags.add(item.lstrip("#"))
    for m in _INLINE_TAG.finditer(body):
        tags.add(m.group(1))
    return {"tags": sorted(tags)}


# ── Config ────────────────────────────────────────────────────────────────────

@dataclass
class AgentConfig:
    backend: str
    base_url: str
    model: str
    instructions_file: Path
    profile_file: Path
    notes_file: Path
    event_log_file: Path
    training_export_file: Path
    obsidian_vault_path: Path
    scribe_folder: str
    repo_root: Path

    @classmethod
    def from_dict(cls, data: dict) -> AgentConfig:
        return cls(
            backend=data["backend"],
            base_url=data["base_url"],
            model=data["model"],
            instructions_file=Path(data["instructions_file"]),
            profile_file=Path(data["profile_file"]),
            notes_file=Path(data["notes_file"]),
            event_log_file=Path(data["event_log_file"]),
            training_export_file=Path(data["training_export_file"]),
            obsidian_vault_path=Path(data["obsidian_vault_path"]),
            scribe_folder=data["scribe_folder"],
            repo_root=Path(data["repo_root"]),
        )


# ── PersonalAgent ─────────────────────────────────────────────────────────────

class PersonalAgent:
    def __init__(self, config: AgentConfig, instructions: str) -> None:
        self.config = config
        self._instructions = instructions
        self._memories: dict[str, dict] = {}
        self._type_counters: dict[str, int] = {}
        self._chat_history: list[tuple[str, str]] = []

    @classmethod
    def from_config(cls, config_path: Path) -> PersonalAgent:
        data = json.loads(Path(config_path).read_text(encoding="utf-8"))
        cfg = AgentConfig.from_dict(data)
        instructions = ""
        if cfg.instructions_file.exists():
            instructions = cfg.instructions_file.read_text(encoding="utf-8")
        return cls(cfg, instructions)

    def add_memory(self, type: str, content: str) -> str:
        prefix = type[:4]
        self._type_counters[prefix] = self._type_counters.get(prefix, 0) + 1
        mem_id = f"{prefix}-{self._type_counters[prefix]:03d}"
        self._memories[mem_id] = {"type": type, "content": content}
        return mem_id

    def format_memory(self) -> str:
        return "\n".join(f"[{v['type']}] {v['content']}" for v in self._memories.values())

    def forget_memory(self, mem_id: str) -> bool:
        if mem_id in self._memories:
            del self._memories[mem_id]
            return True
        return False

    def log_chat_turn(self, user: str, assistant: str) -> None:
        self._chat_history.append((user, assistant))

    def export_training_data(self) -> int:
        export_path = self.config.training_export_file
        export_path.parent.mkdir(parents=True, exist_ok=True)
        system_prompt = self.build_system_prompt()
        rows = [
            {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg},
                    {"role": "assistant", "content": asst_msg},
                ]
            }
            for user_msg, asst_msg in self._chat_history
        ]
        export_path.write_text(
            "\n".join(json.dumps(r) for r in rows),
            encoding="utf-8",
        )
        return len(rows)

    def build_system_prompt(self) -> str:
        parts = ["Project-AI integration context", self._instructions]
        memory_str = self.format_memory()
        if memory_str:
            parts.append(memory_str)
        return "\n\n".join(parts)


# ── Link analysis ─────────────────────────────────────────────────────────────

_WIKILINK = re.compile(r"\[\[([^\]]+)\]\]")
_MDLINK = re.compile(r"\[(?:[^\]]*)\]\(([^)]+)\)")


def _normalize_stem(name: str) -> str:
    last = name.rsplit("/", 1)[-1]
    return last.lower().replace("-", "_")


def _build_md_index(root: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}
    for p in root.rglob("*.md"):
        index[_normalize_stem(p.stem)] = p
    return index


def _analyze_links(file_path: Path, content: str, md_index: dict[str, Path]) -> dict[str, Any]:
    wikilinks = _WIKILINK.findall(content)
    mdlinks = _MDLINK.findall(content)

    unresolved_wiki = [t for t in wikilinks if _normalize_stem(t) not in md_index]
    unresolved_md = [h for h in mdlinks if not (file_path.parent / h).resolve().exists()]

    signals: dict[str, Any] = {
        "link_health": {
            "wikilinks_total": len(wikilinks),
            "wikilinks_unresolved": len(unresolved_wiki),
            "markdown_links_total": len(mdlinks),
            "markdown_links_unresolved": len(unresolved_md),
        }
    }
    if unresolved_wiki:
        signals["unresolved_wikilinks"] = unresolved_wiki
    if unresolved_md:
        signals["unresolved_markdown_links"] = unresolved_md
    return signals


# ── CaregiverScribe ───────────────────────────────────────────────────────────

_REPO_EXTENSIONS = {".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml"}


class CaregiverScribe:
    def __init__(self, config: AgentConfig) -> None:
        self.config = config

    @classmethod
    def from_config(cls, config_path: Path) -> CaregiverScribe:
        data = json.loads(Path(config_path).read_text(encoding="utf-8"))
        return cls(AgentConfig.from_dict(data))

    def absorb_vault(self) -> dict:
        vault = self.config.obsidian_vault_path
        scribe_dir = vault / "_Scribe" / "Project-AI"
        scribe_dir.mkdir(parents=True, exist_ok=True)

        paths: list[Path] = []
        for p in vault.rglob("*.md"):
            parts = p.relative_to(vault).parts
            if parts[0] in (".obsidian", "_Scribe"):
                continue
            paths.append(p)

        (scribe_dir / "Vault Navigation Map.md").write_text(
            "# Vault Navigation Map\n\n" + "\n".join(f"- [[{p.stem}]]" for p in paths),
            encoding="utf-8",
        )
        (scribe_dir / "Project-AI File Index.md").write_text(
            "# Project-AI File Index\n\n"
            + "\n".join(str(p.relative_to(vault)).replace("\\", "/") for p in paths),
            encoding="utf-8",
        )
        return {"records": len(paths)}

    def learn_repo(self) -> dict:
        repo = self.config.repo_root
        count = sum(1 for p in repo.rglob("*") if p.is_file() and p.suffix in _REPO_EXTENSIONS)
        return {"records": count}

    def scan_tree(self, root: Path, context: str) -> list[dict]:
        md_index = _build_md_index(root)
        results = []
        for p in sorted(root.rglob("*.md")):
            content = p.read_text(encoding="utf-8")
            signals = {
                **extract_text_signals(p, content),
                **_analyze_links(p, content, md_index),
            }
            results.append({
                "relative_path": str(p.relative_to(root)).replace("\\", "/"),
                "signals": signals,
            })
        return results
