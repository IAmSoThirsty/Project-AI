"""Simple script to trim trailing whitespace and ensure EOF newline for project files.
Targets: src/, tests/, setup.py, tools/.

Run from repository root. Prints modified files.
"""
from pathlib import Path

TARGETS = ["src", "tests", "setup.py", "tools"]


def fix_file(p: Path) -> bool:
    try:
        text = p.read_text(encoding="utf-8")
    except Exception:
        return False

    lines = text.splitlines()
    # remove trailing whitespace on each line
    new_lines = [ln.rstrip() for ln in lines]

    # ensure file ends with a single newline
    new_text = "\n".join(new_lines) + "\n"

    if new_text != text:
        p.write_text(new_text, encoding="utf-8")
        return True
    return False


def iter_files(root: Path):
    for t in TARGETS:
        p = root / t
        if p.is_dir():
            for f in p.rglob("*"):
                if f.is_file() and f.suffix in {".py", ".qss", ".md", ".txt", ".json"}:
                    yield f
        elif p.is_file():
            yield p


if __name__ == "__main__":
    repo = Path(__file__).resolve().parent.parent
    modified = []
    for f in iter_files(repo):
        if fix_file(f):
            modified.append(str(f.relative_to(repo)))

    if modified:
        print("Modified files:")
        for m in modified:
            print(" -", m)
    else:
        print("No files needed changes.")
