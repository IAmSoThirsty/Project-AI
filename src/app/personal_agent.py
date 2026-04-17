"""Personal agent mode for Project-AI.

This module keeps the personal assistant layer intentionally small and explicit:
Project-AI hosts it, but personal memory and local-model settings stay in their
own namespace under ``data/personal_agent``.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import posixpath
import re
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG_PATH = REPO_ROOT / "config" / "personal_agent.json"
PROFILE_SECTIONS = ("facts", "preferences", "goals", "skills")
CATEGORY_ALIASES = {
    "fact": "facts",
    "facts": "facts",
    "preference": "preferences",
    "preferences": "preferences",
    "pref": "preferences",
    "goal": "goals",
    "goals": "goals",
    "skill": "skills",
    "skills": "skills",
}
DEFAULT_SCAN_EXCLUDE_DIRS = (
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    ".venv",
    ".venv_airllm",
    ".venv_prod",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
    "node_modules",
    "venv",
)
TEXT_EXTENSIONS = {
    ".adoc",
    ".bat",
    ".cfg",
    ".cmd",
    ".conf",
    ".css",
    ".csv",
    ".dockerfile",
    ".go",
    ".gradle",
    ".html",
    ".ini",
    ".java",
    ".js",
    ".json",
    ".jsonl",
    ".kt",
    ".kts",
    ".md",
    ".ps1",
    ".py",
    ".rst",
    ".rs",
    ".sh",
    ".sql",
    ".svg",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}
DOC_EXTENSIONS = {".adoc", ".md", ".pdf", ".rst", ".txt"}
CODE_EXTENSIONS = {
    ".bat",
    ".cmd",
    ".go",
    ".java",
    ".js",
    ".kt",
    ".kts",
    ".ps1",
    ".py",
    ".rs",
    ".sh",
    ".ts",
    ".tsx",
}
DATA_EXTENSIONS = {".csv", ".json", ".jsonl", ".toml", ".xml", ".yaml", ".yml"}


class BackendUnavailable(RuntimeError):
    """Raised when the configured local model backend cannot be reached."""


@dataclass(frozen=True)
class PersonalAgentConfig:
    """Runtime configuration for the personal agent."""

    backend: str = "openai_compatible"
    base_url: str = "http://localhost:1234/v1"
    model: str = "local-model"
    temperature: float = 0.7
    max_tokens: int = 700
    instructions_file: Path = REPO_ROOT / "config" / "personal_agent_instructions.md"
    profile_file: Path = REPO_ROOT / "data" / "personal_agent" / "profile.json"
    notes_file: Path = REPO_ROOT / "data" / "personal_agent" / "notes.md"
    event_log_file: Path = REPO_ROOT / "data" / "personal_agent" / "events.jsonl"
    training_export_file: Path = (
        REPO_ROOT / "data" / "personal_agent" / "training" / "chat_export.jsonl"
    )
    obsidian_vault_path: Path = REPO_ROOT / "wiki"
    scribe_folder: str = "_Scribe/Project-AI"
    repo_root: Path = REPO_ROOT
    scan_exclude_dirs: tuple[str, ...] = DEFAULT_SCAN_EXCLUDE_DIRS
    max_text_preview_chars: int = 12000
    hash_limit_mb: int = 25

    @classmethod
    def from_file(cls, config_path: str | Path | None = None) -> "PersonalAgentConfig":
        path = resolve_repo_path(config_path or DEFAULT_CONFIG_PATH)
        data = load_json(path) if path.exists() else {}

        def path_value(key: str, default: Path) -> Path:
            return resolve_repo_path(data.get(key, default))

        return cls(
            backend=str(data.get("backend", cls.backend)),
            base_url=str(data.get("base_url", cls.base_url)),
            model=str(data.get("model", cls.model)),
            temperature=float(data.get("temperature", cls.temperature)),
            max_tokens=int(data.get("max_tokens", cls.max_tokens)),
            instructions_file=path_value("instructions_file", cls.instructions_file),
            profile_file=path_value("profile_file", cls.profile_file),
            notes_file=path_value("notes_file", cls.notes_file),
            event_log_file=path_value("event_log_file", cls.event_log_file),
            training_export_file=path_value(
                "training_export_file", cls.training_export_file
            ),
            obsidian_vault_path=path_value(
                "obsidian_vault_path", cls.obsidian_vault_path
            ),
            scribe_folder=str(data.get("scribe_folder", cls.scribe_folder)),
            repo_root=path_value("repo_root", cls.repo_root),
            scan_exclude_dirs=tuple(
                data.get("scan_exclude_dirs", cls.scan_exclude_dirs)
            ),
            max_text_preview_chars=int(
                data.get("max_text_preview_chars", cls.max_text_preview_chars)
            ),
            hash_limit_mb=int(data.get("hash_limit_mb", cls.hash_limit_mb)),
        )


def resolve_repo_path(path: str | Path) -> Path:
    resolved = Path(path)
    if resolved.is_absolute():
        return resolved
    return REPO_ROOT / resolved


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def read_text(path: Path, fallback: str = "") -> str:
    if not path.exists():
        return fallback
    return path.read_text(encoding="utf-8").strip()


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def memory_id(section: str, index: int) -> str:
    return f"{section[:4]}-{index + 1:03d}"


def request_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read().decode("utf-8"))


def normalize_path(path: Path) -> str:
    return path.as_posix()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def looks_binary(path: Path) -> bool:
    try:
        sample = path.read_bytes()[:4096]
    except OSError:
        return False
    return b"\0" in sample


def decode_text_preview(path: Path, max_chars: int) -> str:
    raw = path.read_bytes()[: max_chars * 4]
    for encoding in ("utf-8", "utf-8-sig", "cp1252"):
        try:
            return raw.decode(encoding)[:max_chars]
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")[:max_chars]


def file_category(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in DOC_EXTENSIONS:
        return "doc"
    if suffix in CODE_EXTENSIONS:
        return "code"
    if suffix in DATA_EXTENSIONS:
        return "data"
    if suffix in TEXT_EXTENSIONS:
        return "text"
    return "binary" if looks_binary(path) else "other"


def normalize_tag(tag: str) -> str | None:
    normalized = tag.strip().strip("'\"").lstrip("#").strip()
    return normalized or None


def parse_frontmatter_tag_value(raw_value: str) -> list[str]:
    value = raw_value.strip()
    if not value:
        return []
    if value.startswith("[") and value.endswith("]"):
        value = value[1:-1]
    parts = [part for part in re.split(r",|\s+", value) if part.strip()]
    return [tag for part in parts if (tag := normalize_tag(part))]


def extract_frontmatter_tags(text: str) -> list[str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return []

    closing_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            closing_index = index
            break
    if closing_index is None:
        return []

    frontmatter = lines[1:closing_index]
    tags: list[str] = []
    index = 0
    while index < len(frontmatter):
        line = frontmatter[index]
        match = re.match(r"^\s*tags?\s*:\s*(.*)$", line, re.IGNORECASE)
        if not match:
            index += 1
            continue

        inline_value = match.group(1).strip()
        if inline_value:
            tags.extend(parse_frontmatter_tag_value(inline_value))
            index += 1
            continue

        index += 1
        while index < len(frontmatter):
            item_line = frontmatter[index]
            if item_line and not item_line.startswith((" ", "\t")):
                break
            item = item_line.strip()
            if item.startswith("- "):
                tags.extend(parse_frontmatter_tag_value(item[2:]))
            index += 1

    return tags


def wiki_link_target(raw_link: str) -> str:
    target = raw_link.split("|", 1)[0].split("#", 1)[0].strip()
    return target.replace("\\", "/")


def link_slug(value: str) -> str:
    value = value.replace("\\", "/").strip().strip("/")
    value = re.sub(r"\.md$", "", value, flags=re.IGNORECASE)
    parts = []
    for part in value.split("/"):
        slug = re.sub(r"[^a-z0-9]+", "-", part.lower()).strip("-")
        if slug:
            parts.append(slug)
    return "/".join(parts)


def normalize_link_path(value: str) -> str:
    normalized = posixpath.normpath(value.replace("\\", "/"))
    return "" if normalized == "." else normalized.lstrip("./")


def markdown_link_target(raw_link: str) -> str:
    target = raw_link.strip()
    target = target.split("#", 1)[0].split("?", 1)[0].strip()
    return target.replace("\\", "/")


def is_external_link(target: str) -> bool:
    return bool(re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE))


def extract_text_signals(path: Path, text: str) -> dict[str, Any]:
    suffix = path.suffix.lower()
    signals: dict[str, Any] = {}

    if suffix == ".md":
        headings = []
        for match in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE):
            headings.append(
                {"level": len(match.group(1)), "text": match.group(2).strip()}
            )
        links = sorted(set(re.findall(r"\[\[([^\]]+)\]\]", text)))[:100]
        markdown_links = sorted(set(re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)))[:100]
        inline_tags = re.findall(r"(?<!\w)#([A-Za-z0-9_/-]+)", text)
        tags = sorted(set(extract_frontmatter_tags(text) + inline_tags))[:100]
        signals.update(
            {
                "headings": headings[:100],
                "wikilinks": links,
                "markdown_links": markdown_links,
                "tags": tags,
            }
        )

    if suffix == ".py":
        symbols = []
        pattern = r"^(class|def|async\s+def)\s+([A-Za-z_][A-Za-z0-9_]*)"
        for match in re.finditer(pattern, text, re.MULTILINE):
            symbols.append({"kind": match.group(1), "name": match.group(2)})
        signals["symbols"] = symbols[:100]

    if suffix in {".js", ".ts", ".tsx"}:
        symbols = []
        pattern = r"^(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)"
        symbols.extend(
            {"kind": "function", "name": name}
            for name in re.findall(pattern, text, re.MULTILINE)
        )
        class_pattern = r"^(?:export\s+)?class\s+([A-Za-z_$][\w$]*)"
        symbols.extend(
            {"kind": "class", "name": name}
            for name in re.findall(class_pattern, text, re.MULTILINE)
        )
        signals["symbols"] = symbols[:100]

    return signals


class CaregiverScribe:
    """Bounded active agent role: learn, index, and write navigation to Obsidian."""

    def __init__(self, config: PersonalAgentConfig | None = None):
        self.config = config or PersonalAgentConfig.from_file()

    @classmethod
    def from_config(cls, config_path: str | Path | None = None) -> "CaregiverScribe":
        return cls(PersonalAgentConfig.from_file(config_path))

    @property
    def vault_path(self) -> Path:
        return self.config.obsidian_vault_path

    @property
    def scribe_root(self) -> Path:
        return self.vault_path / Path(self.config.scribe_folder)

    def validate_vault(self) -> None:
        if not self.vault_path.exists():
            raise FileNotFoundError(f"Obsidian vault not found: {self.vault_path}")
        if not (self.vault_path / ".obsidian").exists():
            raise FileNotFoundError(
                f"Path is not an Obsidian vault; missing .obsidian: {self.vault_path}"
            )

    def ensure_scribe_space(self) -> None:
        self.validate_vault()
        self.scribe_root.mkdir(parents=True, exist_ok=True)

    def status(self) -> dict[str, Any]:
        vault_exists = self.vault_path.exists()
        is_vault = (self.vault_path / ".obsidian").exists()
        return {
            "repo_root": str(self.config.repo_root),
            "vault_path": str(self.vault_path),
            "vault_exists": vault_exists,
            "is_obsidian_vault": is_vault,
            "scribe_root": str(self.scribe_root),
            "scribe_root_exists": self.scribe_root.exists(),
            "config_path": str(DEFAULT_CONFIG_PATH),
        }

    def absorb_vault(self) -> dict[str, Any]:
        self.ensure_scribe_space()
        records = list(self.scan_tree(self.vault_path, context="vault"))
        manifest_path = self.scribe_root / "vault_manifest.jsonl"
        map_path = self.scribe_root / "Vault Navigation Map.md"
        home_path = self.write_scribe_home()

        self.write_jsonl(manifest_path, records)
        map_path.write_text(self.render_vault_map(records), encoding="utf-8")

        return {
            "records": len(records),
            "manifest": str(manifest_path),
            "map": str(map_path),
            "home": str(home_path),
        }

    def learn_repo(self) -> dict[str, Any]:
        self.ensure_scribe_space()
        records = list(self.scan_tree(self.config.repo_root, context="repo"))
        manifest_path = self.scribe_root / "repo_file_manifest.jsonl"
        index_path = self.scribe_root / "Project-AI File Index.md"
        home_path = self.write_scribe_home()

        self.write_jsonl(manifest_path, records)
        index_path.write_text(self.render_repo_index(records), encoding="utf-8")

        return {
            "records": len(records),
            "manifest": str(manifest_path),
            "index": str(index_path),
            "home": str(home_path),
        }

    def scan_tree(self, root: Path, context: str) -> list[dict[str, Any]]:
        root = root.resolve()
        records = []
        for current_root, dir_names, file_names in os.walk(root):
            current_path = Path(current_root)
            dir_names[:] = [
                name
                for name in dir_names
                if not self.should_skip_directory(current_path / name, root, context)
            ]
            for file_name in file_names:
                file_path = current_path / file_name
                if self.should_skip_file(file_path, root, context):
                    continue
                records.append(self.inspect_file(file_path, root, context))
        records.sort(key=lambda item: item["relative_path"].lower())
        self.annotate_link_health(records)
        return records

    def annotate_link_health(self, records: list[dict[str, Any]]) -> None:
        markdown_targets = self.markdown_target_index(records)
        file_targets = {item["relative_path"] for item in records}
        for record in records:
            signals = record.get("signals")
            if not signals:
                continue
            unresolved_wikilinks = []
            for raw_link in signals.get("wikilinks", []):
                target = wiki_link_target(raw_link)
                if not target or target.startswith("#"):
                    continue
                if (
                    self.resolve_wiki_target(
                        target, record["relative_path"], markdown_targets
                    )
                    is None
                ):
                    unresolved_wikilinks.append(raw_link)

            unresolved_markdown_links = []
            for raw_link in signals.get("markdown_links", []):
                target = markdown_link_target(raw_link)
                if not target or target.startswith("#") or is_external_link(target):
                    continue
                if (
                    self.resolve_markdown_target(
                        target, record["relative_path"], file_targets
                    )
                    is None
                ):
                    unresolved_markdown_links.append(raw_link)

            signals["link_health"] = {
                "wikilinks_total": len(signals.get("wikilinks", [])),
                "wikilinks_unresolved": len(unresolved_wikilinks),
                "markdown_links_total": len(signals.get("markdown_links", [])),
                "markdown_links_unresolved": len(unresolved_markdown_links),
            }
            if unresolved_wikilinks:
                signals["unresolved_wikilinks"] = unresolved_wikilinks[:100]
            if unresolved_markdown_links:
                signals["unresolved_markdown_links"] = unresolved_markdown_links[:100]

    def markdown_target_index(self, records: list[dict[str, Any]]) -> dict[str, str]:
        targets: dict[str, str] = {}
        for item in records:
            if item.get("extension") != ".md":
                continue
            relative_path = item["relative_path"]
            without_extension = re.sub(r"\.md$", "", relative_path, flags=re.IGNORECASE)
            parts = without_extension.split("/")
            for offset in range(len(parts)):
                targets.setdefault(link_slug("/".join(parts[offset:])), relative_path)
            targets.setdefault(link_slug(Path(relative_path).stem), relative_path)
        return targets

    def resolve_wiki_target(
        self, target: str, source_relative_path: str, targets: dict[str, str]
    ) -> str | None:
        candidates = []
        if target.startswith((".", "/")) or "/" in target:
            source_dir = posixpath.dirname(source_relative_path)
            candidates.append(normalize_link_path(posixpath.join(source_dir, target)))
            candidates.append(normalize_link_path(target))
        candidates.append(target)

        for candidate in candidates:
            resolved = targets.get(link_slug(candidate))
            if resolved is not None:
                return resolved
        return None

    def resolve_markdown_target(
        self, target: str, source_relative_path: str, targets: set[str]
    ) -> str | None:
        source_dir = posixpath.dirname(source_relative_path)
        if target.startswith("/"):
            base = normalize_link_path(target)
        else:
            base = normalize_link_path(posixpath.join(source_dir, target))

        candidates = [base]
        if not Path(base).suffix:
            candidates.extend([f"{base}.md", f"{base}/README.md", f"{base}/index.md"])
        if base.endswith("/"):
            candidates.extend([f"{base}README.md", f"{base}index.md"])

        for candidate in candidates:
            if candidate in targets:
                return candidate
        return None

    def should_skip_directory(self, path: Path, root: Path, context: str) -> bool:
        if path.name in set(self.config.scan_exclude_dirs):
            return True
        if path.name == ".obsidian":
            return True
        try:
            path.relative_to(self.scribe_root)
            return True
        except ValueError:
            pass
        if context == "repo":
            try:
                path.resolve().relative_to(
                    (self.vault_path / self.config.scribe_folder).resolve()
                )
                return True
            except ValueError:
                pass
        return False

    def should_skip_file(self, path: Path, root: Path, context: str) -> bool:
        try:
            path.resolve().relative_to(self.scribe_root.resolve())
            return True
        except ValueError:
            return False

    def inspect_file(self, path: Path, root: Path, context: str) -> dict[str, Any]:
        stat = path.stat()
        relative_path = path.relative_to(root)
        category = file_category(path)
        hash_limit = self.config.hash_limit_mb * 1024 * 1024
        record: dict[str, Any] = {
            "context": context,
            "relative_path": normalize_path(relative_path),
            "absolute_path": str(path.resolve()),
            "name": path.name,
            "extension": path.suffix.lower(),
            "category": category,
            "size_bytes": stat.st_size,
            "modified_at": dt.datetime.fromtimestamp(stat.st_mtime, tz=dt.timezone.utc)
            .replace(microsecond=0)
            .isoformat(),
            "sha256": sha256_file(path) if stat.st_size <= hash_limit else None,
            "sha256_status": "ok" if stat.st_size <= hash_limit else "skipped_large",
        }

        if path.suffix.lower() in TEXT_EXTENSIONS and not looks_binary(path):
            try:
                preview = decode_text_preview(path, self.config.max_text_preview_chars)
                record["signals"] = extract_text_signals(path, preview)
                record["text_preview_chars"] = len(preview)
            except OSError as error:
                record["read_error"] = str(error)
        return record

    def write_scribe_home(self) -> Path:
        self.ensure_scribe_space()
        home_path = self.scribe_root / "00 Scribe Home.md"
        generated_at = utc_now()
        content = f"""---
agent: caregiver-scribe
generated_at: {generated_at}
---

# Caregiver Scribe Home

This is the active scribe space for Project-AI's personal agent.

The scribe's first duty is to learn the terrain:

- Absorb the Obsidian vault structure first.
- Learn every Project-AI file as navigable metadata.
- Keep learned navigation data in this vault.
- Avoid becoming a general autonomous tool agent until the scribe layer is solid.

## Navigation

- [[Vault Navigation Map]]
- [[Project-AI File Index]]

## Machine Paths

- Repo root: `{self.config.repo_root}`
- Vault: `{self.vault_path}`
- Scribe folder: `{self.scribe_root}`

"""
        home_path.write_text(content, encoding="utf-8")
        return home_path

    def render_vault_map(self, records: list[dict[str, Any]]) -> str:
        generated_at = utc_now()
        markdown_records = [item for item in records if item["extension"] == ".md"]
        folders = self.folder_counts(records)
        tags = self.collect_signal_counts(records, "tags")
        links = self.collect_signal_counts(records, "wikilinks")
        link_health = self.link_health_totals(records)

        lines = [
            "---",
            "agent: caregiver-scribe",
            f"generated_at: {generated_at}",
            "source: obsidian-vault",
            "---",
            "",
            "# Vault Navigation Map",
            "",
            f"Vault path: `{self.vault_path}`",
            f"Files indexed: {len(records)}",
            f"Markdown notes: {len(markdown_records)}",
            "",
            "## Top Folders",
            "",
            *self.render_count_list(folders),
            "",
            "## Frequent Tags",
            "",
            *self.render_count_list(tags),
            "",
            "## Frequent Wiki Links",
            "",
            *self.render_count_list(links),
            "",
            "## Link Health",
            "",
            f"- Wiki links unresolved: {link_health['wikilinks_unresolved']}",
            f"- Markdown links unresolved: {link_health['markdown_links_unresolved']}",
            "",
            "## Notes",
            "",
        ]
        for item in markdown_records[:500]:
            lines.append(f"- `{item['relative_path']}`")
        if len(markdown_records) > 500:
            lines.append(
                f"- ... {len(markdown_records) - 500} more notes in vault_manifest.jsonl"
            )
        lines.append("")
        lines.append("Full file-level data is in `vault_manifest.jsonl`.")
        lines.append("")
        return "\n".join(lines)

    def render_repo_index(self, records: list[dict[str, Any]]) -> str:
        generated_at = utc_now()
        categories = self.value_counts(records, "category")
        extensions = self.value_counts(records, "extension")
        folders = self.folder_counts(records)
        link_health = self.link_health_totals(records)

        lines = [
            "---",
            "agent: caregiver-scribe",
            f"generated_at: {generated_at}",
            "source: project-ai-repo",
            "---",
            "",
            "# Project-AI File Index",
            "",
            f"Repo root: `{self.config.repo_root}`",
            f"Files indexed: {len(records)}",
            "",
            "This index is the scribe's map. Every indexed file has a record in",
            "`repo_file_manifest.jsonl`, including docs and non-doc files.",
            "",
            "## Categories",
            "",
            *self.render_count_list(categories),
            "",
            "## Extensions",
            "",
            *self.render_count_list(extensions, limit=80),
            "",
            "## Top Folders",
            "",
            *self.render_count_list(folders, limit=80),
            "",
            "## Link Health",
            "",
            f"- Wiki links unresolved: {link_health['wikilinks_unresolved']}",
            f"- Markdown links unresolved: {link_health['markdown_links_unresolved']}",
            "",
            "## High-Signal Files",
            "",
        ]
        for item in self.high_signal_records(records)[:300]:
            details = []
            signals = item.get("signals", {})
            if signals.get("headings"):
                details.append(f"{len(signals['headings'])} headings")
            if signals.get("symbols"):
                details.append(f"{len(signals['symbols'])} symbols")
            link_health = signals.get("link_health", {})
            unresolved_links = link_health.get(
                "wikilinks_unresolved", 0
            ) + link_health.get("markdown_links_unresolved", 0)
            if unresolved_links:
                details.append(f"{unresolved_links} unresolved links")
            label = ", ".join(details) if details else item["category"]
            lines.append(f"- `{item['relative_path']}` ({label})")
        lines.append("")
        lines.append("Full file-level data is in `repo_file_manifest.jsonl`.")
        lines.append("")
        return "\n".join(lines)

    def high_signal_records(
        self, records: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        def score(item: dict[str, Any]) -> int:
            signals = item.get("signals", {})
            return (
                len(signals.get("headings", [])) * 3
                + len(signals.get("symbols", [])) * 2
                + (10 if item["name"].lower() in {"readme.md", "pyproject.toml"} else 0)
            )

        return sorted(records, key=score, reverse=True)

    def write_jsonl(self, path: Path, records: list[dict[str, Any]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as handle:
            for record in records:
                handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    def value_counts(self, records: list[dict[str, Any]], key: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in records:
            value = str(item.get(key) or "(none)")
            counts[value] = counts.get(value, 0) + 1
        return dict(sorted(counts.items(), key=lambda pair: pair[1], reverse=True))

    def folder_counts(self, records: list[dict[str, Any]]) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in records:
            first = item["relative_path"].split("/", 1)[0]
            counts[first] = counts.get(first, 0) + 1
        return dict(sorted(counts.items(), key=lambda pair: pair[1], reverse=True))

    def collect_signal_counts(
        self, records: list[dict[str, Any]], signal_name: str
    ) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in records:
            for value in item.get("signals", {}).get(signal_name, []):
                text = str(value)
                counts[text] = counts.get(text, 0) + 1
        return dict(sorted(counts.items(), key=lambda pair: pair[1], reverse=True))

    def link_health_totals(self, records: list[dict[str, Any]]) -> dict[str, int]:
        totals = {
            "wikilinks_total": 0,
            "wikilinks_unresolved": 0,
            "markdown_links_total": 0,
            "markdown_links_unresolved": 0,
        }
        for item in records:
            health = item.get("signals", {}).get("link_health", {})
            for key in totals:
                totals[key] += int(health.get(key, 0))
        return totals

    def render_count_list(self, counts: dict[str, int], limit: int = 40) -> list[str]:
        if not counts:
            return ["- None found"]
        lines = []
        for name, count in list(counts.items())[:limit]:
            lines.append(f"- `{name}`: {count}")
        if len(counts) > limit:
            lines.append(f"- ... {len(counts) - limit} more")
        return lines


class PersonalAgent:
    """Memory-capable personal agent hosted inside Project-AI."""

    def __init__(self, config: PersonalAgentConfig | None = None):
        self.config = config or PersonalAgentConfig.from_file()
        self.ensure_storage()

    @classmethod
    def from_config(cls, config_path: str | Path | None = None) -> "PersonalAgent":
        return cls(PersonalAgentConfig.from_file(config_path))

    def ensure_storage(self) -> None:
        self.config.profile_file.parent.mkdir(parents=True, exist_ok=True)
        self.config.notes_file.parent.mkdir(parents=True, exist_ok=True)
        self.config.event_log_file.parent.mkdir(parents=True, exist_ok=True)
        self.config.training_export_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.config.profile_file.exists():
            save_json(
                self.config.profile_file,
                {section: [] for section in PROFILE_SECTIONS},
            )
        if not self.config.notes_file.exists():
            self.config.notes_file.write_text(
                "# Personal Agent Notes\n\n",
                encoding="utf-8",
            )
        scribe = CaregiverScribe(self.config)
        if scribe.vault_path.exists() and (scribe.vault_path / ".obsidian").exists():
            scribe.write_scribe_home()

    def load_profile(self) -> dict[str, list[dict[str, str]]]:
        loaded = load_json(self.config.profile_file)
        return {section: list(loaded.get(section, [])) for section in PROFILE_SECTIONS}

    def save_profile(self, profile: dict[str, list[dict[str, str]]]) -> None:
        save_json(self.config.profile_file, profile)

    def add_memory(self, category: str, text: str) -> str:
        section = CATEGORY_ALIASES.get(category)
        if section is None:
            accepted = ", ".join(sorted(CATEGORY_ALIASES))
            raise ValueError(f"Unknown memory category '{category}'. Use: {accepted}")

        clean_text = text.strip()
        if not clean_text:
            raise ValueError("Memory text cannot be empty.")

        profile = self.load_profile()
        profile[section].append({"text": clean_text, "created_at": utc_now()})
        self.save_profile(profile)
        item_id = memory_id(section, len(profile[section]) - 1)
        self.append_event(
            {
                "type": "memory_added",
                "created_at": utc_now(),
                "category": section,
                "memory_id": item_id,
                "text": clean_text,
            }
        )
        return item_id

    def append_note(self, note: str) -> None:
        clean_note = note.strip()
        if not clean_note:
            raise ValueError("Note cannot be empty.")
        existing = read_text(self.config.notes_file)
        prefix = "" if existing.endswith("\n") or not existing else "\n"
        with self.config.notes_file.open("a", encoding="utf-8") as handle:
            handle.write(f"{prefix}- {clean_note}\n")

    def forget_memory(self, target_id: str) -> bool:
        profile = self.load_profile()
        for section in PROFILE_SECTIONS:
            kept = []
            removed = False
            for index, item in enumerate(profile[section]):
                if memory_id(section, index) == target_id:
                    removed = True
                    continue
                kept.append(item)
            if removed:
                profile[section] = kept
                self.save_profile(profile)
                self.append_event(
                    {
                        "type": "memory_removed",
                        "created_at": utc_now(),
                        "memory_id": target_id,
                    }
                )
                return True
        return False

    def format_memory(self) -> str:
        profile = self.load_profile()
        chunks = []
        for section in PROFILE_SECTIONS:
            items = profile.get(section, [])
            if not items:
                continue
            lines = [f"{section.title()}:"]
            for index, item in enumerate(items):
                lines.append(f"- {memory_id(section, index)}: {item['text']}")
            chunks.append("\n".join(lines))

        notes = read_text(self.config.notes_file)
        if notes:
            chunks.append(f"Freeform notes:\n{notes}")

        return "\n\n".join(chunks) if chunks else "No personal memories yet."

    def build_system_prompt(self) -> str:
        instructions = read_text(
            self.config.instructions_file,
            "You are a useful personal agent hosted inside Project-AI.",
        )
        return (
            f"{instructions}\n\n"
            "Project-AI integration context:\n"
            "- You are running as Project-AI's personal-agent mode.\n"
            "- Personal memory lives under data/personal_agent.\n"
            "- The active first role is Caregiver Scribe.\n"
            f"- Obsidian vault path: {self.config.obsidian_vault_path}\n"
            f"- Scribe navigation path: {self.config.obsidian_vault_path / self.config.scribe_folder}\n"
            "- Use Project-AI context when the user asks for Project-AI work.\n"
            "- Keep personal facts separate from repository facts.\n\n"
            f"Saved personal memory:\n{self.format_memory()}"
        )

    def append_event(self, event: dict[str, Any]) -> None:
        self.config.event_log_file.parent.mkdir(parents=True, exist_ok=True)
        with self.config.event_log_file.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    def log_chat_turn(self, user_text: str, assistant_text: str) -> None:
        self.append_event(
            {
                "type": "chat_turn",
                "created_at": utc_now(),
                "user": user_text,
                "assistant": assistant_text,
            }
        )

    def ask(
        self,
        user_text: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        messages = [
            {"role": "system", "content": self.build_system_prompt()},
            *(history or []),
            {"role": "user", "content": user_text},
        ]

        try:
            if self.config.backend == "ollama":
                reply = self._ask_ollama(messages)
            else:
                reply = self._ask_openai_compatible(messages)
        except (KeyError, TimeoutError, OSError, urllib.error.URLError) as error:
            raise BackendUnavailable(str(error)) from error

        self.log_chat_turn(user_text, reply)
        return reply

    def _ask_openai_compatible(self, messages: list[dict[str, str]]) -> str:
        base_url = self.config.base_url.rstrip("/")
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
        }
        response = request_json(f"{base_url}/chat/completions", payload)
        return response["choices"][0]["message"]["content"].strip()

    def _ask_ollama(self, messages: list[dict[str, str]]) -> str:
        base_url = self.config.base_url.rstrip("/")
        payload = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": self.config.temperature,
                "num_predict": self.config.max_tokens,
            },
        }
        response = request_json(f"{base_url}/api/chat", payload)
        return response["message"]["content"].strip()

    def backend_status(self) -> dict[str, Any]:
        if self.config.backend == "ollama":
            status_url = f"{self.config.base_url.rstrip('/')}/api/tags"
        else:
            status_url = f"{self.config.base_url.rstrip('/')}/models"

        try:
            request = urllib.request.Request(status_url, method="GET")
            with urllib.request.urlopen(request, timeout=5) as response:
                body = response.read().decode("utf-8")
            return {
                "available": True,
                "backend": self.config.backend,
                "base_url": self.config.base_url,
                "model": self.config.model,
                "status_url": status_url,
                "response_preview": body[:500],
            }
        except (TimeoutError, OSError, urllib.error.URLError) as error:
            return {
                "available": False,
                "backend": self.config.backend,
                "base_url": self.config.base_url,
                "model": self.config.model,
                "status_url": status_url,
                "error": str(error),
            }

    def export_training_data(self) -> int:
        instructions = read_text(
            self.config.instructions_file,
            "You are a useful personal agent hosted inside Project-AI.",
        )
        exported = 0
        self.config.training_export_file.parent.mkdir(parents=True, exist_ok=True)

        with self.config.training_export_file.open("w", encoding="utf-8") as handle:
            for event in self.iter_events():
                if event.get("type") != "chat_turn":
                    continue
                example = {
                    "messages": [
                        {"role": "system", "content": instructions},
                        {"role": "user", "content": event["user"]},
                        {"role": "assistant", "content": event["assistant"]},
                    ]
                }
                handle.write(json.dumps(example, ensure_ascii=False) + "\n")
                exported += 1
        return exported

    def iter_events(self) -> list[dict[str, Any]]:
        if not self.config.event_log_file.exists():
            return []
        rows = []
        for line in self.config.event_log_file.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rows.append(json.loads(line))
        return rows


def run_chat(config_path: str | Path | None = None) -> int:
    agent = PersonalAgent.from_config(config_path)
    history: list[dict[str, str]] = []

    print("Project-AI Personal Agent")
    print("Type /exit to quit, /learn fact text to save memory, /reset to clear chat.")
    print()

    while True:
        try:
            user_text = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        if not user_text:
            continue
        if user_text == "/exit":
            return 0
        if user_text == "/reset":
            history.clear()
            print("agent> Chat history cleared.")
            continue
        if user_text == "/memory":
            print(agent.format_memory())
            continue
        if user_text == "/training-export":
            exported = agent.export_training_data()
            print(f"agent> Exported {exported} examples.")
            continue
        if user_text.startswith("/forget "):
            target_id = user_text.removeprefix("/forget ").strip()
            if agent.forget_memory(target_id):
                print(f"agent> Forgot {target_id}.")
            else:
                print(f"agent> I could not find memory id {target_id}.")
            continue
        if user_text.startswith("/remember "):
            item_id = agent.add_memory(
                "fact", user_text.removeprefix("/remember ").strip()
            )
            print(f"agent> Learned fact {item_id}.")
            continue
        if user_text.startswith("/prefer "):
            item_id = agent.add_memory(
                "preference", user_text.removeprefix("/prefer ").strip()
            )
            print(f"agent> Learned preference {item_id}.")
            continue
        if user_text.startswith("/goal "):
            item_id = agent.add_memory("goal", user_text.removeprefix("/goal ").strip())
            print(f"agent> Learned goal {item_id}.")
            continue
        if user_text.startswith("/learn "):
            parts = user_text.removeprefix("/learn ").strip().split(maxsplit=1)
            section = CATEGORY_ALIASES.get(parts[0]) if parts else None
            if len(parts) == 2 and section:
                item_id = agent.add_memory(section, parts[1])
                label = parts[0].removesuffix("s")
                print(f"agent> Learned {label} {item_id}.")
            else:
                print(
                    "agent> Use /learn fact text, /learn preference text, "
                    "/learn goal text, or /learn skill text."
                )
            continue

        try:
            reply = agent.ask(user_text, history=history)
        except BackendUnavailable as error:
            print_backend_help(agent, error)
            return 1

        history.extend(
            [
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": reply},
            ]
        )
        print(f"agent> {reply}\n")


def print_backend_help(agent: PersonalAgent, error: Exception) -> None:
    config = agent.config
    print()
    print("Could not reach the local model server.")
    print(f"Backend: {config.backend}")
    print(f"Base URL: {config.base_url}")
    print(f"Model: {config.model}")
    print(f"Error: {error}")
    print()
    print("Start LM Studio's local server or Ollama, then run this again.")


def print_scribe_result(title: str, result: dict[str, Any]) -> None:
    print(title)
    for key, value in result.items():
        print(f"{key}: {value}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Project-AI personal-agent mode.")
    parser.add_argument(
        "--config",
        default=str(DEFAULT_CONFIG_PATH),
        help="Path to personal-agent config JSON.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("chat", help="Start interactive personal-agent chat.")

    learn_parser = subparsers.add_parser(
        "learn", help="Store a structured personal memory."
    )
    learn_parser.add_argument("category", choices=sorted(CATEGORY_ALIASES))
    learn_parser.add_argument("text")

    subparsers.add_parser("memory", help="Print saved personal memory.")

    forget_parser = subparsers.add_parser("forget", help="Forget one memory id.")
    forget_parser.add_argument("memory_id")

    scribe_parser = subparsers.add_parser("scribe", help="Run caregiver-scribe tasks.")
    scribe_subparsers = scribe_parser.add_subparsers(dest="scribe_command")
    scribe_subparsers.add_parser("status", help="Show scribe/vault configuration.")
    scribe_subparsers.add_parser("init", help="Create the scribe home note.")
    scribe_subparsers.add_parser("absorb-vault", help="Index the Obsidian vault first.")
    scribe_subparsers.add_parser(
        "learn-repo", help="Index Project-AI files into the vault."
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    command = args.command or "chat"

    if command == "chat":
        return run_chat(args.config)

    agent = PersonalAgent.from_config(args.config)
    if command == "learn":
        item_id = agent.add_memory(args.category, args.text)
        print(f"Learned {args.category}: {item_id}")
        return 0
    if command == "memory":
        print(agent.format_memory())
        return 0
    if command == "forget":
        if agent.forget_memory(args.memory_id):
            print(f"Forgot {args.memory_id}.")
            return 0
        print(f"Memory id not found: {args.memory_id}")
        return 1
    if command == "scribe":
        scribe = CaregiverScribe(agent.config)
        scribe_command = args.scribe_command or "status"
        if scribe_command == "status":
            print_scribe_result("Caregiver Scribe Status", scribe.status())
            return 0
        if scribe_command == "init":
            home = scribe.write_scribe_home()
            print(f"Scribe home written: {home}")
            return 0
        if scribe_command == "absorb-vault":
            print_scribe_result("Vault absorbed", scribe.absorb_vault())
            return 0
        if scribe_command == "learn-repo":
            print_scribe_result("Project-AI files indexed", scribe.learn_repo())
            return 0

    print(f"Unknown command: {command}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
