"""Tests for the Tarl OS historical-spec subpackage.

Per the user's instruction, the 27 legacy
``.thirsty`` files (outdated syntax) and the 5
``.md`` docs (Obsidian artifacts) were removed.
The 3 Python files that referenced the deleted
``.thirsty`` files (bridge.py, multi_turn_tests.py,
test_legacy_tarl_os_bridge.py) were also removed.

The remaining content (4 files) is preserved as
historical reference: plain-text summary, legacy
ARCHITECTURE.py (no .thirsty refs), and the
actual stress-test result JSON.

These tests verify the cleanup is intact:

  - Zero ``.thirsty`` files (outdated syntax)
  - Zero ``.md`` files (Obsidian artifacts)
  - Zero bridge.py / multi_turn_tests.py /
    test_legacy_tarl_os_bridge.py (legacy code
    that tested for deleted files)
  - The plain-text ``SUMMARY.txt`` is present
  - ``tests/ARCHITECTURE.py`` is present (it
    doesn't reference the deleted .thirsty files)
  - The stress-test result JSON parses
  - The subpackage imports cleanly
"""

from __future__ import annotations

import json

from tarl.tarl_os import (
    list_legacy_docs,
    list_legacy_thirsty_files,
    os_spec_root,
)

# --- Tests --------------------------------------------------------------


def test_os_spec_root_exists() -> None:
    """The Tarl OS subpackage root exists."""
    root = os_spec_root()
    assert root.exists()
    assert root.is_dir()


def test_no_thirsty_files_in_subpackage() -> None:
    """There are ZERO ``.thirsty`` files in the
    Tarl OS subpackage.

    The 27 legacy ``.thirsty`` files were removed
    because they used outdated syntax (``shield X {``
    as a class declaration). Per the user's
    instruction ("DO NOT IMPLEMENT LEGACY OR
    OUTDATED REPLACING THE NEW THIRSTY-LANG UTF"),
    outdated syntax is not ported.
    """
    thirsty_files = list(os_spec_root().rglob("*.thirsty"))
    assert thirsty_files == [], (
        f"Found {len(thirsty_files)} .thirsty files; expected 0 (outdated syntax was removed)"
    )


def test_no_markdown_files_in_subpackage() -> None:
    """There are ZERO ``.md`` files in the Tarl OS
    subpackage.

    The 5 ``.md`` docs from the original recovery
    were removed because they all started with
    Obsidian YAML frontmatter. Per the user's
    instruction to drop Obsidian-specific content.
    """
    md_files = list(os_spec_root().rglob("*.md"))
    assert md_files == [], (
        f"Found {len(md_files)} .md files; expected 0 (Obsidian-vault artifacts were dropped)"
    )


def test_no_legacy_bridge_code() -> None:
    """The legacy ``bridge.py`` and
    ``test_legacy_tarl_os_bridge.py`` were removed
    because they referenced the deleted ``.thirsty``
    files. The same applies to
    ``tests/multi_turn_tests.py``."""
    assert not (os_spec_root() / "bridge.py").exists()
    assert not (os_spec_root() / "tests" / "test_legacy_tarl_os_bridge.py").exists()
    assert not (os_spec_root() / "tests" / "multi_turn_tests.py").exists()


def test_list_legacy_thirsty_files_returns_empty() -> None:
    """``list_legacy_thirsty_files()`` returns an
    empty list."""
    assert list_legacy_thirsty_files() == []


def test_summary_txt_is_present() -> None:
    """The plain-text ``SUMMARY.txt`` is present
    and has content. (No Obsidian frontmatter.)"""
    summary = os_spec_root() / "SUMMARY.txt"
    assert summary.exists()
    content = summary.read_text(encoding="utf-8")
    assert len(content) > 0
    assert not content.startswith("---")


def test_list_legacy_docs_returns_only_summary_txt() -> None:
    """``list_legacy_docs()`` returns only the
    ``SUMMARY.txt`` file."""
    docs = list_legacy_docs()
    for path in docs:
        assert path.suffix == ".txt"
    assert len(docs) == 1
    assert docs[0].name == "SUMMARY.txt"


def test_architecture_py_is_present() -> None:
    """``tests/ARCHITECTURE.py`` is present (it
    does not reference the deleted ``.thirsty``
    files)."""
    arch = os_spec_root() / "tests" / "ARCHITECTURE.py"
    assert arch.exists()
    content = arch.read_text(encoding="utf-8")
    assert len(content) > 0


def test_stress_test_result_json_is_present() -> None:
    """The stress-test result JSON is present and
    parses as valid JSON."""
    results_dir = os_spec_root() / "tests" / "results"
    assert results_dir.exists()
    json_files = list(results_dir.glob("*.json"))
    assert len(json_files) >= 1
    data = json.loads(json_files[0].read_text(encoding="utf-8"))
    assert isinstance(data, dict)


def test_no_obsidian_metadata_anywhere() -> None:
    """No file in the subpackage starts with Obsidian
    YAML frontmatter (``---\\ntype: ...``)."""
    for path in os_spec_root().rglob("*"):
        if path.is_file() and path.suffix in (
            ".md",
            ".txt",
            ".thirsty",
        ):
            content = path.read_text(encoding="utf-8")
            assert not content.startswith("---"), (
                f"{path.name} looks like Obsidian frontmatter; should be dropped per user directive"
            )
