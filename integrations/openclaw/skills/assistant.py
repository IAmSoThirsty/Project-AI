"""
Legion Assistant Skills
Tasks, Notes, Scheduling, Timers — file-backed, per-user.
"""
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any

_DATA = Path(__file__).resolve().parent.parent.parent.parent / "data" / "legion"


def _dir(user_id: str, category: str) -> Path:
    p = _DATA / category / user_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def _utc_now() -> str:
    return dt.datetime.now(dt.UTC).replace(microsecond=0).isoformat()


# ── Tasks ─────────────────────────────────────────────────────────────────────

def _tasks_path(user_id: str) -> Path:
    return _dir(user_id, "tasks") / "tasks.json"


def _load_tasks(user_id: str) -> list[dict]:
    p = _tasks_path(user_id)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def _save_tasks(user_id: str, tasks: list[dict]) -> None:
    _tasks_path(user_id).write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")


async def handle_tasks(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message", "")
    user_id = params.get("user_id", "default")
    msg_l = msg.lower()
    tasks = _load_tasks(user_id)

    # LIST
    if any(w in msg_l for w in ["list", "show", "what", "view", "all my task", "pending", "my task"]):
        if not tasks:
            return {"success": True, "result": "No tasks yet. Say 'add task: [description]' to create one."}
        pending = [t for t in tasks if t["status"] == "pending"]
        done = [t for t in tasks if t["status"] == "done"]
        lines = []
        if pending:
            lines.append("**Pending:**")
            for t in pending:
                lines.append(f"  [{t['id']}] {t['text']}")
        if done:
            lines.append(f"\n**Completed:** {len(done)} task(s)")
        return {"success": True, "result": "\n".join(lines)}

    # COMPLETE
    m = re.search(r'\bt(\d+)\b', msg_l)
    if m and any(w in msg_l for w in ["done", "complete", "finish", "check off", "mark"]):
        tid = f"t{m.group(1).zfill(3)}"
        for t in tasks:
            if t["id"] == tid:
                t["status"] = "done"
                t["completed_at"] = _utc_now()
                _save_tasks(user_id, tasks)
                return {"success": True, "result": f"Task {tid} marked complete: {t['text']}"}
        return {"success": False, "result": f"Task {tid} not found."}

    # DELETE
    if m and any(w in msg_l for w in ["delete", "remove"]):
        tid = f"t{m.group(1).zfill(3)}"
        original = len(tasks)
        tasks = [t for t in tasks if t["id"] != tid]
        if len(tasks) < original:
            _save_tasks(user_id, tasks)
            return {"success": True, "result": f"Task {tid} deleted."}
        return {"success": False, "result": f"Task {tid} not found."}

    # ADD
    if any(w in msg_l for w in ["add", "create", "new task", "remind me to", "todo"]):
        text = msg
        for marker in ["add task:", "new task:", "task:", "remind me to", "todo:", "add:"]:
            if marker in msg_l:
                idx = msg_l.index(marker) + len(marker)
                text = msg[idx:].strip()
                break
        task_id = f"t{len(tasks) + 1:03d}"
        tasks.append({"id": task_id, "text": text, "status": "pending", "created_at": _utc_now()})
        _save_tasks(user_id, tasks)
        return {"success": True, "result": f"Task created [{task_id}]: {text}"}

    # Default: show list
    if not tasks:
        return {"success": True, "result": "No tasks. Say 'add task: [description]' to create one."}
    lines = [f"  [{t['id']}] {'✓' if t['status'] == 'done' else '○'} {t['text']}" for t in tasks[-20:]]
    return {"success": True, "result": "Your tasks:\n" + "\n".join(lines)}


# ── Notes ─────────────────────────────────────────────────────────────────────

async def handle_notes(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message", "")
    user_id = params.get("user_id", "default")
    msg_l = msg.lower()
    notes_dir = _dir(user_id, "notes")

    # LIST
    if any(w in msg_l for w in ["list notes", "show notes", "all notes", "my notes", "view notes"]):
        files = sorted(notes_dir.glob("*.md"))
        if not files:
            return {"success": True, "result": "No notes yet. Say 'create note: [title]' to write one."}
        return {"success": True, "result": "**Your notes:**\n" + "\n".join(f"  - {f.stem}" for f in files)}

    # READ
    if any(w in msg_l for w in ["read note", "open note", "show note", "get note"]):
        for f in notes_dir.glob("*.md"):
            if f.stem.lower() in msg_l:
                return {"success": True, "result": f"**{f.stem}**\n\n{f.read_text(encoding='utf-8')}"}
        return {"success": False, "result": "Specify a note name to read (e.g. 'read note meeting_notes')."}

    # DELETE
    if any(w in msg_l for w in ["delete note", "remove note"]):
        for f in notes_dir.glob("*.md"):
            if f.stem.lower() in msg_l:
                f.unlink()
                return {"success": True, "result": f"Note '{f.stem}' deleted."}
        return {"success": False, "result": "Note not found."}

    # CREATE
    if any(w in msg_l for w in ["create note", "new note", "save note", "write note", "note:"]):
        lines = msg.splitlines()
        title, content_lines = "untitled", lines[:]
        for i, line in enumerate(lines):
            if any(t in line.lower() for t in ["note:", "create note", "new note", "save note"]):
                rest = line.split(":", 1)[-1].strip() if ":" in line else ""
                if rest:
                    title = rest
                content_lines = lines[i + 1:]
                break
        content = "\n".join(content_lines).strip()
        safe = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "_")[:50] or "note"
        path = notes_dir / f"{safe}.md"
        path.write_text(f"# {title}\n\n{content}\n", encoding="utf-8")
        return {"success": True, "result": f"Note '{title}' saved."}

    return {"success": False, "result": "Try: 'list notes', 'create note: [title]', or 'read note [name]'."}


# ── Scheduling ────────────────────────────────────────────────────────────────

def _schedule_path(user_id: str) -> Path:
    return _dir(user_id, "schedule") / "events.json"


def _load_events(user_id: str) -> list[dict]:
    p = _schedule_path(user_id)
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def _save_events(user_id: str, events: list[dict]) -> None:
    _schedule_path(user_id).write_text(json.dumps(events, indent=2) + "\n", encoding="utf-8")


async def handle_scheduling(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message", "")
    user_id = params.get("user_id", "default")
    msg_l = msg.lower()
    events = _load_events(user_id)

    # LIST
    if any(w in msg_l for w in ["list", "show", "what", "view", "calendar", "upcoming", "my schedule"]):
        if not events:
            return {"success": True, "result": "No events scheduled. Say 'schedule: [event] on [date/time]'."}
        lines = ["**Scheduled Events:**"]
        for e in events:
            lines.append(f"  [{e['id']}] {e['title']} — {e.get('when', 'No date set')}")
        return {"success": True, "result": "\n".join(lines)}

    # DELETE
    m = re.search(r'\be(\d+)\b', msg_l)
    if m and any(w in msg_l for w in ["cancel", "delete", "remove"]):
        eid = f"e{m.group(1).zfill(3)}"
        events = [e for e in events if e["id"] != eid]
        _save_events(user_id, events)
        return {"success": True, "result": f"Event {eid} cancelled."}

    # ADD
    if any(w in msg_l for w in ["schedule", "book", "add event", "new event", "appointment", "meeting"]):
        text = msg
        for marker in ["schedule:", "book:", "event:", "appointment:", "meeting:"]:
            if marker in msg_l:
                idx = msg_l.index(marker) + len(marker)
                text = msg[idx:].strip()
                break
        event_id = f"e{len(events) + 1:03d}"
        when = "Time not specified"
        for pat in [r"on (\w+ \d+)", r"at (\d+:\d+\s*(?:am|pm)?)", r"(\w+day)", r"(\d{4}-\d{2}-\d{2})"]:
            dm = re.search(pat, text, re.IGNORECASE)
            if dm:
                when = dm.group(1)
                break
        events.append({"id": event_id, "title": text, "when": when, "created_at": _utc_now()})
        _save_events(user_id, events)
        return {"success": True, "result": f"Event scheduled [{event_id}]: {text} ({when})"}

    return {"success": False, "result": "Try: 'show my schedule', 'schedule: [event] on [date]', or 'cancel e001'."}


# ── Timers ────────────────────────────────────────────────────────────────────

_active_timers: dict[str, dict] = {}


async def handle_timers(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message", "")
    msg_l = msg.lower()

    minutes: float | None = None
    for pat, mult in [(r"(\d+)\s*(?:hour?s?|h\b)", 60), (r"(\d+)\s*(?:min(?:ute)?s?|m\b)", 1), (r"(\d+)\s*(?:sec(?:ond)?s?|s\b)", 1 / 60)]:
        dm = re.search(pat, msg_l)
        if dm:
            minutes = float(dm.group(1)) * mult
            break

    if minutes is not None:
        end = dt.datetime.now(dt.UTC) + dt.timedelta(minutes=minutes)
        tid = f"tmr{len(_active_timers) + 1}"
        _active_timers[tid] = {"end": end.isoformat(), "minutes": minutes}
        label = f"{int(minutes)}m" if minutes >= 1 else f"{int(minutes * 60)}s"
        return {"success": True, "result": f"Timer [{tid}] set for {label}. Ends at {end.strftime('%H:%M:%S UTC')}."}

    if any(w in msg_l for w in ["list", "show", "active", "running", "timers"]):
        if not _active_timers:
            return {"success": True, "result": "No active timers."}
        now = dt.datetime.now(dt.UTC)
        lines = ["**Active Timers:**"]
        expired = []
        for tid, t in _active_timers.items():
            end = dt.datetime.fromisoformat(t["end"])
            remaining = (end - now).total_seconds()
            if remaining <= 0:
                lines.append(f"  [{tid}] Expired")
                expired.append(tid)
            else:
                lines.append(f"  [{tid}] {int(remaining // 60)}m {int(remaining % 60)}s remaining")
        for tid in expired:
            del _active_timers[tid]
        return {"success": True, "result": "\n".join(lines)}

    return {"success": False, "result": "Say 'set timer for 10 minutes', 'set timer 2 hours', or 'show timers'."}
