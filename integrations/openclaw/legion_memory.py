#!/usr/bin/env python3
"""
Legion Memory System
Structured per-user memory (facts, preferences, goals, skills), freeform notes,
persistent conversation event log, and training data export.

Adapted from the Personal-Agent project's memory architecture — ported and
extended for Legion's multi-user, governed context.

Storage: data/legion/users/{user_id}/ relative to repo root.
"""

import datetime as dt
import json
from pathlib import Path
from typing import Any

PROFILE_SECTIONS = ("facts", "preferences", "goals", "skills")

CATEGORY_ALIASES: dict[str, str] = {
    "fact": "facts", "facts": "facts",
    "preference": "preferences", "preferences": "preferences", "pref": "preferences",
    "goal": "goals", "goals": "goals",
    "skill": "skills", "skills": "skills",
}

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_USERS_ROOT = _REPO_ROOT / "data" / "legion" / "users"


# ── Internal helpers ─────────────────────────────────────────────────────────

def _user_dir(user_id: str) -> Path:
    path = _USERS_ROOT / user_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def _utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


def _memory_id(section: str, index: int) -> str:
    return f"{section[:4]}-{index + 1:03d}"


# ── Profile (structured memory) ───────────────────────────────────────────────

def load_profile(user_id: str) -> dict[str, list[dict[str, str]]]:
    path = _user_dir(user_id) / "profile.json"
    if not path.exists():
        return {s: [] for s in PROFILE_SECTIONS}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {s: list(data.get(s, [])) for s in PROFILE_SECTIONS}


def _save_profile(user_id: str, profile: dict) -> None:
    path = _user_dir(user_id) / "profile.json"
    path.write_text(json.dumps(profile, indent=2) + "\n", encoding="utf-8")


def add_memory(user_id: str, section: str, text: str) -> str:
    """Add an item to a profile section. Returns the assigned memory ID."""
    profile = load_profile(user_id)
    profile[section].append({"text": text.strip(), "created_at": _utc_now()})
    _save_profile(user_id, profile)
    return _memory_id(section, len(profile[section]) - 1)


def forget_memory(user_id: str, target_id: str) -> bool:
    """Remove a memory item by ID. Returns True if found and removed."""
    profile = load_profile(user_id)
    for section in PROFILE_SECTIONS:
        kept, removed = [], False
        for i, item in enumerate(profile[section]):
            if _memory_id(section, i) == target_id:
                removed = True
            else:
                kept.append(item)
        if removed:
            profile[section] = kept
            _save_profile(user_id, profile)
            return True
    return False


def format_profile(user_id: str) -> str:
    """Return a human-readable summary of the user's structured memory."""
    profile = load_profile(user_id)
    chunks = []
    for section in PROFILE_SECTIONS:
        items = profile.get(section, [])
        if not items:
            continue
        lines = [f"{section.title()}:"]
        for i, item in enumerate(items):
            lines.append(f"  - {_memory_id(section, i)}: {item['text']}")
        chunks.append("\n".join(lines))
    return "\n\n".join(chunks) if chunks else "No memories stored yet."


# ── Freeform notes ────────────────────────────────────────────────────────────

def load_notes(user_id: str) -> str:
    path = _user_dir(user_id) / "notes.md"
    return path.read_text(encoding="utf-8").strip() if path.exists() else ""


def append_note(user_id: str, note: str) -> None:
    path = _user_dir(user_id) / "notes.md"
    existing = path.read_text(encoding="utf-8").strip() if path.exists() else ""
    prefix = "\n" if existing else ""
    with path.open("a", encoding="utf-8") as f:
        f.write(f"{prefix}- {note.strip()}\n")


# ── Event log (persistent conversation history) ───────────────────────────────

def log_event(user_id: str, user_msg: str, assistant_msg: str) -> None:
    """Append a chat turn to the user's JSONL event log."""
    path = _user_dir(user_id) / "events.jsonl"
    event: dict[str, Any] = {
        "type": "chat_turn",
        "created_at": _utc_now(),
        "user": user_msg,
        "assistant": assistant_msg,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def load_recent_history(user_id: str, n: int = 10) -> list[dict]:
    """Return the last n chat turns as OpenAI-format message dicts."""
    path = _user_dir(user_id) / "events.jsonl"
    if not path.exists():
        return []
    events = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
            if e.get("type") == "chat_turn":
                events.append(e)
        except json.JSONDecodeError:
            continue
    messages = []
    for e in events[-n:]:
        messages.append({"role": "user", "content": e["user"]})
        messages.append({"role": "assistant", "content": e["assistant"]})
    return messages


# ── System prompt builder ─────────────────────────────────────────────────────

def build_legion_system_prompt(user_id: str) -> str:
    """Build a personalized Legion system prompt enriched with user memory."""
    from .llm_provider import LEGION_SYSTEM_PROMPT

    prompt = LEGION_SYSTEM_PROMPT
    profile_text = format_profile(user_id)
    if profile_text != "No memories stored yet.":
        prompt += f"\n\nUser profile:\n{profile_text}"
    notes_text = load_notes(user_id)
    if notes_text:
        prompt += f"\n\nNotes:\n{notes_text}"
    return prompt


# ── Training export ───────────────────────────────────────────────────────────

def export_training_data(user_id: str) -> tuple[int, Path]:
    """Export conversation history as fine-tuning ready JSONL. Returns (count, path)."""
    from .llm_provider import LEGION_SYSTEM_PROMPT

    src = _user_dir(user_id) / "events.jsonl"
    dst = _user_dir(user_id) / "training_export.jsonl"
    if not src.exists():
        return 0, dst

    count = 0
    with dst.open("w", encoding="utf-8") as out:
        for line in src.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                e = json.loads(line)
                if e.get("type") != "chat_turn":
                    continue
                example = {
                    "messages": [
                        {"role": "system", "content": LEGION_SYSTEM_PROMPT},
                        {"role": "user", "content": e["user"]},
                        {"role": "assistant", "content": e["assistant"]},
                    ]
                }
                out.write(json.dumps(example) + "\n")
                count += 1
            except (json.JSONDecodeError, KeyError):
                continue
    return count, dst
