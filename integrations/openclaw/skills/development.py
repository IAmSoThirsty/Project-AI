"""
Legion Development Skills
Code Execution, Git Operations, Code Analysis
"""
import ast
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


# ── Code Execution ────────────────────────────────────────────────────────────

async def handle_code_execution(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message", "")
    msg_l = msg.lower()

    # Extract code block (markdown fences first)
    code, lang = None, "python"
    m = re.search(r"```(python|py|javascript|js)?\n(.*?)```", msg, re.DOTALL | re.IGNORECASE)
    if m:
        raw_lang = (m.group(1) or "python").lower()
        lang = "javascript" if raw_lang in ("js", "javascript") else "python"
        code = m.group(2).strip()
    else:
        for marker in ["run:", "execute:", "python:", "code:", "js:", "javascript:"]:
            if marker in msg_l:
                idx = msg_l.index(marker) + len(marker)
                code = msg[idx:].strip()
                if marker.startswith(("js:", "javascript:")):
                    lang = "javascript"
                break

    if not code:
        return {
            "success": False,
            "result": "Provide code to run in a ```python block``` or after 'run: [code]'.",
        }

    suffix = ".py" if lang == "python" else ".js"
    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False, encoding="utf-8") as f:
            f.write(code)
            tmp = f.name

        cmd = ["python", tmp] if lang == "python" else ["node", tmp]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        output = (result.stdout + result.stderr).strip()[:2000]
        Path(tmp).unlink(missing_ok=True)

        return {
            "success": result.returncode == 0,
            "result": f"**{lang.title()} output:**\n```\n{output or '(no output)'}\n```",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "result": "Execution timed out (15s limit)."}
    except FileNotFoundError:
        return {"success": False, "result": f"{lang.title()} runtime not found. Is it installed?"}
    except Exception as e:
        return {"success": False, "result": f"Execution error: {e}"}


# ── Git Operations ────────────────────────────────────────────────────────────

_GIT_COMMAND_MAP = [
    (["status", "what changed", "changes", "modified"], ["git", "status", "--short"]),
    (["log", "history", "commits", "recent commit"], ["git", "log", "--oneline", "-20"]),
    (["diff", "difference", "what's different", "show diff"], ["git", "diff", "--stat"]),
    (["branch", "branches"], ["git", "branch", "-a"]),
    (["stash"], ["git", "stash", "list"]),
    (["pull", "update", "sync", "fetch"], ["git", "pull"]),
    (["remote"], ["git", "remote", "-v"]),
]


async def handle_git(params: dict[str, Any]) -> dict[str, Any]:
    msg_l = params.get("message", "").lower()

    cmd = ["git", "status", "--short"]  # default
    for keywords, git_cmd in _GIT_COMMAND_MAP:
        if any(k in msg_l for k in keywords):
            cmd = git_cmd
            break

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=30, cwd=str(_REPO_ROOT),
        )
        output = (result.stdout + result.stderr).strip()[:3000]
        return {
            "success": result.returncode == 0,
            "result": f"**`{' '.join(cmd)}`**\n```\n{output or '(clean — no output)'}\n```",
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "result": "Git command timed out."}
    except Exception as e:
        return {"success": False, "result": f"Git error: {e}"}


# ── Code Analysis ─────────────────────────────────────────────────────────────

async def handle_code_analysis(params: dict[str, Any]) -> dict[str, Any]:
    msg = params.get("message", "")

    # Inline code block
    m = re.search(r"```(?:python|py)?\n(.*?)```", msg, re.DOTALL)
    if m:
        return _analyze_python(m.group(1).strip(), "<inline>")

    # File path in message
    pm = re.search(r'["\']?([^\s"\']+\.py)["\']?', msg)
    if pm:
        p = Path(pm.group(1))
        if not p.is_absolute():
            p = _REPO_ROOT / p
        if p.exists():
            return _analyze_python(p.read_text(encoding="utf-8", errors="replace"), str(p.relative_to(_REPO_ROOT)))
        return {"success": False, "result": f"File not found: {pm.group(1)}"}

    return {"success": False, "result": "Provide a .py file path or a ```python code block``` to analyze."}


def _analyze_python(code: str, label: str) -> dict[str, Any]:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return {"success": False, "result": f"Syntax error in `{label}`: {e}"}

    lines = code.splitlines()
    loc = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
    functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
    classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    imports = [ast.unparse(n) for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
    branches = sum(
        1 for n in ast.walk(tree)
        if isinstance(n, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler, ast.With))
    )
    todos = [l.strip() for l in lines if re.search(r"\b(TODO|FIXME|HACK|XXX)\b", l, re.IGNORECASE)]

    report = [
        f"**Code Analysis: `{label}`**",
        f"Lines of code: {loc} ({len(lines)} total)",
        f"Functions ({len(functions)}): {', '.join(functions[:10]) or 'none'}",
        f"Classes ({len(classes)}): {', '.join(classes[:5]) or 'none'}",
        f"Imports: {len(imports)}",
        f"Branch complexity: {branches}",
    ]
    if todos:
        report.append(f"\n**TODOs/FIXMEs ({len(todos)}):**")
        report.extend(f"  - {t}" for t in todos[:5])
    if branches > 30:
        report.append("\n⚠️ High cyclomatic complexity — consider refactoring.")
    if len(lines) > 500:
        report.append("⚠️ Large file — consider splitting into modules.")
    if not functions and not classes and loc > 50:
        report.append("⚠️ No functions or classes — consider structuring the code.")

    return {"success": True, "result": "\n".join(report)}
