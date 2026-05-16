"""
Legion System Skills
System Info, File Operations, Shell Command Execution — all governance-gated.
"""
import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent

_ALLOWED_READ_ROOTS = [_REPO_ROOT, Path("T:/Project-AI-vault"), Path.home() / "Documents"]
_ALLOWED_WRITE_ROOTS = [_REPO_ROOT / "data" / "legion"]

_SAFE_COMMANDS = {
    "git", "python", "python3", "pip", "node", "npm",
    "ls", "dir", "echo", "cat", "type", "pwd", "where",
    "powershell", "py",
}


def _is_safe_path(path: Path, roots: list[Path]) -> bool:
    try:
        resolved = path.resolve()
        for root in roots:
            try:
                resolved.relative_to(root.resolve())
                return True
            except ValueError:
                continue
    except Exception:
        pass
    return False


# ── System Info ───────────────────────────────────────────────────────────────

async def handle_system_info(params: dict[str, Any]) -> dict[str, Any]:
    try:
        lines = [
            "**System Status**",
            f"OS: {platform.system()} {platform.release()} ({platform.machine()})",
            f"Python: {sys.version.split()[0]}",
            f"CPU cores: {os.cpu_count()}",
        ]

        # CPU usage (Windows PowerShell)
        if platform.system() == "Windows":
            try:
                r = subprocess.run(
                    ["powershell", "-Command", "(Get-CimInstance Win32_Processor).LoadPercentage"],
                    capture_output=True, text=True, timeout=6,
                )
                lines.append(f"CPU load: {r.stdout.strip()}%")
            except Exception:
                pass
            try:
                r = subprocess.run(
                    ["powershell", "-Command",
                     "$m=(Get-CimInstance Win32_OperatingSystem);"
                     "[math]::Round($m.FreePhysicalMemory/1MB,1).ToString()"
                     "+' GB free of '+"
                     "[math]::Round($m.TotalVisibleMemorySize/1MB,1).ToString()+' GB'"],
                    capture_output=True, text=True, timeout=6,
                )
                lines.append(f"RAM: {r.stdout.strip()}")
            except Exception:
                pass
            try:
                r = subprocess.run(
                    ["powershell", "-Command",
                     "$d=Get-PSDrive T;"
                     "'T: Free: '+[math]::Round($d.Free/1GB,1)+' GB / '+[math]::Round(($d.Used+$d.Free)/1GB,1)+' GB'"],
                    capture_output=True, text=True, timeout=6,
                )
                lines.append(f"Disk: {r.stdout.strip()}")
            except Exception:
                pass
        else:
            try:
                r = subprocess.run(["free", "-h"], capture_output=True, text=True, timeout=5)
                lines.append(r.stdout.strip())
            except Exception:
                pass
            try:
                st = os.statvfs("/")
                free_gb = (st.f_bavail * st.f_frsize) / 1e9
                total_gb = (st.f_blocks * st.f_frsize) / 1e9
                lines.append(f"Disk /: {free_gb:.1f} GB free of {total_gb:.1f} GB")
            except Exception:
                pass

        return {"success": True, "result": "\n".join(lines)}
    except Exception as e:
        return {"success": False, "result": f"System info error: {e}"}


# ── File Operations ───────────────────────────────────────────────────────────

async def handle_file_operations(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message", "")
    msg_l = msg.lower()

    # READ
    if any(w in msg_l for w in ["read", "show file", "open file", "cat ", "view file", "contents of"]):
        m = re.search(r'["\']([^"\']+)["\']', msg) or re.search(
            r'(?:read|open|show|cat|view|contents of)\s+([^\s]+\.\w+)', msg, re.IGNORECASE
        )
        if not m:
            return {"success": False, "result": "Specify a file path (e.g. read \"README.md\")."}
        path = Path(m.group(1).strip())
        if not path.is_absolute():
            path = _REPO_ROOT / path
        if not _is_safe_path(path, _ALLOWED_READ_ROOTS):
            return {"success": False, "result": "Access denied: path outside allowed read roots."}
        if not path.exists():
            return {"success": False, "result": f"File not found: {path}"}
        try:
            content = path.read_text(encoding="utf-8", errors="replace")[:4000]
            return {"success": True, "result": f"**{path.name}**\n```\n{content}\n```"}
        except Exception as e:
            return {"success": False, "result": f"Read error: {e}"}

    # LIST
    if any(w in msg_l for w in ["list files", "list dir", "ls ", "dir ", "list folder", "show folder"]):
        m = re.search(r'(?:list|ls|dir|folder)\s+([^\s"\']+)', msg, re.IGNORECASE)
        path = Path(m.group(1)) if m else _REPO_ROOT
        if not path.is_absolute():
            path = _REPO_ROOT / path
        if not _is_safe_path(path, _ALLOWED_READ_ROOTS):
            return {"success": False, "result": "Access denied."}
        if not path.exists():
            return {"success": False, "result": f"Directory not found: {path}"}
        try:
            items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name))
            lines = [f"  {'📁' if i.is_dir() else '📄'} {i.name}" for i in items[:60]]
            return {"success": True, "result": f"**{path.name}/**\n" + "\n".join(lines)}
        except Exception as e:
            return {"success": False, "result": f"List error: {e}"}

    return {"success": False, "result": "Try: 'read \"path/to/file\"', 'list files in docs/', 'list dir'."}


# ── Shell ─────────────────────────────────────────────────────────────────────

async def handle_shell(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message", "")
    msg_l = msg.lower()

    command = msg
    for marker in ["run:", "execute:", "shell:", "cmd:", "run command", "run the command"]:
        if marker in msg_l:
            idx = msg_l.index(marker) + len(marker)
            command = msg[idx:].strip()
            break

    if not command:
        return {"success": False, "result": "Specify a command to run (e.g. 'run: git status')."}

    first_word = command.strip().split()[0].lower().lstrip("./")
    if first_word not in _SAFE_COMMANDS:
        return {
            "success": False,
            "result": (
                f"Command '{first_word}' is not in the allowlist.\n"
                f"Allowed: {', '.join(sorted(_SAFE_COMMANDS))}\n\n"
                "High-risk shell operations require explicit Triumvirate approval."
            ),
        }

    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30, cwd=str(_REPO_ROOT),
        )
        output = (result.stdout + result.stderr).strip()[:3000]
        return {
            "success": result.returncode == 0,
            "result": f"```\n{output or '(no output)'}\n```",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "result": "Command timed out (30s limit)."}
    except Exception as e:
        return {"success": False, "result": f"Execution error: {e}"}
