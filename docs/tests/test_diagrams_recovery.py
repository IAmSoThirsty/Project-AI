"""Tests for the diagrams/ recovery.

Per the user's directive, 42 files of visual
documentation (architecture Mermaid graphs,
flow diagrams, sequence diagrams, Excalidraw
sources + SVG renders, 1 stdlib-only converter
script) were ported from the vault's
``Project-AI/diagrams/`` to
``docs/diagrams/``.

This test verifies:

  - 42 files were copied
  - All 29 ``.md`` files are non-Obsidian
    (no YAML frontmatter)
  - All 6 ``.excalidraw`` files are valid
    Excalidraw JSON
  - All 6 ``.svg`` files start with ``<svg``
  - The 1 ``.py`` file is stdlib-only
"""

from __future__ import annotations

import json
from pathlib import Path

DIAGRAMS_DIR = Path(__file__).resolve().parents[2] / "docs" / "diagrams"


def test_diagrams_dir_exists() -> None:
    """The diagrams/ directory exists."""
    assert DIAGRAMS_DIR.exists()
    assert DIAGRAMS_DIR.is_dir()


def test_diagrams_dir_has_42_files() -> None:
    """The recovery contains exactly 42 files
    (29 .md + 6 .excalidraw + 6 .svg + 1 .py
    = 42) — plus 1 ``README.md`` written by this
    recovery = 43 total."""
    all_files = [p for p in DIAGRAMS_DIR.rglob("*") if p.is_file()]
    assert len(all_files) == 43


def test_diagrams_dir_has_readme() -> None:
    """The diagrams/ directory has a README.md."""
    readme = DIAGRAMS_DIR / "README.md"
    assert readme.exists()
    assert readme.stat().st_size > 0


def test_no_obsidian_yaml_frontmatter() -> None:
    """No ``.md`` file in the recovery has
    Obsidian YAML frontmatter
    (``created:``/``last_verified:``/
    ``review_cycle:``/``tags:``)."""
    for path in DIAGRAMS_DIR.rglob("*.md"):
        if path.name == "README.md":
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if not (content.startswith("---\n") or content.startswith("---\r\n")):
            continue
        lines = content.split("\n")
        for i in range(1, min(50, len(lines))):
            if lines[i].strip() == "---":
                head = "\n".join(lines[:i])
                for key in ("created:", "last_verified:", "review_cycle:", "tags:"):
                    assert key not in head, (
                        f"{path.name} has Obsidian key '{key}'; "
                        "should be dropped per user directive"
                    )
                break


def test_excalidraw_files_are_valid_json() -> None:
    """All 6 ``.excalidraw`` files are valid JSON
    with the expected Excalidraw structure
    (``elements`` array, ``type: "excalidraw"``)."""
    excalidraw_files = list(DIAGRAMS_DIR.rglob("*.excalidraw"))
    assert len(excalidraw_files) == 6
    for path in excalidraw_files:
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data.get("type") == "excalidraw", (
            f"{path.name} is not a valid Excalidraw file (missing type='excalidraw')"
        )
        assert "elements" in data, f"{path.name} is missing 'elements' array"


def test_svg_files_start_with_svg_tag() -> None:
    """All 6 ``.svg`` files start with ``<svg``
    (or whitespace + ``<?xml`` declaration then
    ``<svg``)."""
    svg_files = list(DIAGRAMS_DIR.rglob("*.svg"))
    assert len(svg_files) == 6
    for path in svg_files:
        content = path.read_text(encoding="utf-8", errors="ignore").lstrip()
        assert content.startswith("<svg") or content.startswith("<?xml"), (
            f"{path.name} is not a valid SVG file"
        )


def test_python_file_is_stdlib_only() -> None:
    """The 1 ``.py`` file (``convert_to_svg.py``)
    uses only Python stdlib (no external deps
    per Thirstys V3 #9)."""
    py_files = list(DIAGRAMS_DIR.rglob("*.py"))
    assert len(py_files) == 1
    convert = py_files[0]
    content = convert.read_text(encoding="utf-8")
    # Find all imports
    import_lines = [
        line.strip()
        for line in content.split("\n")
        if line.strip().startswith(("import ", "from "))
    ]
    # Stdlib modules that are commonly used
    stdlib = {
        "json",
        "os",
        "sys",
        "pathlib",
        "typing",
        "re",
        "math",
        "datetime",
        "collections",
        "itertools",
        "functools",
        "argparse",
        "io",
        "logging",
        "subprocess",
        "shutil",
        "tempfile",
        "urllib",
        "http",
        "html",
        "xml",
        "csv",
        "configparser",
        "ast",
        "copy",
        "enum",
        "dataclasses",
        "traceback",
        "inspect",
        "textwrap",
        "unicodedata",
    }
    for line in import_lines:
        # Extract the module name
        parts = line.split()
        if parts[0] == "import":
            mod = parts[1].split(".")[0].split(" as ")[0]
        elif parts[0] == "from":
            mod = parts[1].split(".")[0]
        else:
            continue
        assert mod in stdlib, f"{convert.name} imports non-stdlib module: {mod}"


def test_architecture_dir_has_10_topics() -> None:
    """The architecture/ subdir has 10 topic
    files + 1 README."""
    arch_dir = DIAGRAMS_DIR / "architecture"
    assert arch_dir.exists()
    md_files = [p for p in arch_dir.glob("*.md") if p.name != "README.md"]
    assert len(md_files) == 10


def test_flows_dir_has_8_topics() -> None:
    """The flows/ subdir has 8 topic files +
    1 INTEGRATION_GUIDE + 1 README."""
    flows_dir = DIAGRAMS_DIR / "flows"
    assert flows_dir.exists()
    md_files = [
        p for p in flows_dir.glob("*.md") if p.name not in ("README.md", "INTEGRATION_GUIDE.md")
    ]
    assert len(md_files) == 8


def test_sequences_dir_has_6_topics() -> None:
    """The sequences/ subdir has 6 sequence
    files + 1 README."""
    seq_dir = DIAGRAMS_DIR / "sequences"
    assert seq_dir.exists()
    md_files = [p for p in seq_dir.glob("*.md") if p.name != "README.md"]
    assert len(md_files) == 6
