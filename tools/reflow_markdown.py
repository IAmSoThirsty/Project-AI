"""
Reflow Markdown paragraphs to a target column width while preserving
code fences, YAML frontmatter, tables, headings, blockquotes, and lists.

Usage:
    python tools/reflow_markdown.py --width 88

This script edits files in-place. It skips paths containing
`node_modules` or `.venv` and will report which files were changed.
"""
from __future__ import annotations

import argparse
import os
import textwrap
from pathlib import Path

SKIP_DIR_PARTS = {"node_modules", ".venv", "venv"}


def should_skip(path: Path) -> bool:
    s = str(path)
    for p in SKIP_DIR_PARTS:
        if f"{os.sep}{p}{os.sep}" in s or s.endswith(f"{os.sep}{p}"):
            return True
    return False


def is_table_line(line: str) -> bool:
    # heuristic: lines with pipe characters and at least one letter/digit
    return "|" in line and any(c.isalnum() for c in line)


def is_code_fence(line: str) -> bool:
    """Check if line is a code fence marker."""
    stripped = line.strip()
    return stripped.startswith("```") or stripped.startswith("~~~")


def should_preserve_line(line: str) -> bool:
    """Check if line should be preserved as-is (not reflowed)."""
    stripped = line.lstrip()
    if not line.strip():
        return True
    if stripped.startswith("#") or stripped.startswith(">"):
        return True
    if stripped.startswith("-") or stripped.startswith("*"):
        return True
    if stripped.startswith("+"):
        return True
    if stripped[0].isdigit() and stripped.split(" ", 1)[0].endswith("."):
        return True
    if stripped.startswith("<") or line.strip().startswith(":::"):
        return True
    return is_table_line(line)


def _process_lines(
    lines: list[str], width: int, flush_fn
) -> tuple[list[str], int]:
    """Process all lines and return (out_lines, changed count)."""
    out_lines: list[str] = []
    changed = 0
    in_code = False
    code_fence = ""
    paragraph: list[str] = []

    for line in lines:
        # detect code fence
        if not in_code and is_code_fence(line):
            flush_fn(paragraph)
            paragraph = []
            in_code = True
            code_fence = line.strip()[:3]
            out_lines.append(line)
            continue

        if in_code:
            out_lines.append(line)
            if line.strip().startswith(code_fence):
                in_code = False
            continue

        # YAML frontmatter
        if line.strip().startswith("---") and not paragraph:
            flush_fn(paragraph)
            paragraph = []
            out_lines.append(line)
            continue

        # preserve special lines
        if should_preserve_line(line):
            flush_fn(paragraph)
            paragraph = []
            out_lines.append(line)
            continue

        # accumulate paragraph lines
        paragraph.append(line)

    flush_fn(paragraph)
    return out_lines, changed


def reflow_markdown_text(text: str, width: int) -> tuple[str, int]:
    lines = text.splitlines()
    changed = 0

    def flush_paragraph(paragraph: list):
        nonlocal changed
        if not paragraph:
            return
        raw = "\n".join(paragraph).strip()
        # keep leading/trailing blank lines as single blank line
        if not raw:
            out_lines.append("")
            return
        # reflow using textwrap while preserving single leading indent
        indent = ""
        for pl in paragraph:
            stripped = pl.lstrip()
            if stripped:
                indent = pl[: len(pl) - len(stripped)]
                break

        wrapped = textwrap.fill(raw, width=width)
        wrapped_lines = [(indent + line).rstrip() for line in wrapped.splitlines()]
        if wrapped_lines != [line.rstrip() for line in paragraph]:
            changed += 1
        out_lines.extend(wrapped_lines)

    out_lines: list[str] = []
    out_lines, changed = _process_lines(lines, width, flush_paragraph)
    return "\n".join(out_lines) + ("\n" if text.endswith("\n") else ""), changed


def process_file(path: Path, width: int) -> int:
    text = path.read_text(encoding="utf8")
    new_text, changed = reflow_markdown_text(text, width)
    if changed:
        path.write_text(new_text, encoding="utf8")
    return changed


def find_md_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*.md"):
        if should_skip(p):
            continue
        files.append(p)
    return files


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--width", type=int, default=88, help="target wrap column")
    p.add_argument("--root", type=str, default=".", help="repo root")
    args = p.parse_args()
    root = Path(args.root).resolve()
    files = find_md_files(root)
    total_changed = 0
    for f in sorted(files):
        try:
            changed = process_file(f, args.width)
        except Exception as e:
            print(f"ERROR processing {f}: {e}")
            continue
        if changed:
            print(f"Reflowed {f} ({changed} paragraphs changed)")
            total_changed += 1
    print(f"Done. Files changed: {total_changed}/{len(files)}")


if __name__ == "__main__":
    main()
