"""
Tarl OS — HISTORICAL SPEC DATA (recovered).

This subpackage preserves a minimal subset of the
Tarl OS specification that was originally
recovered from
``T:\\00-Active\\Project-AI-vault\\Project-AI\\tarl_os\\``.

**IMPORTANT: This is NOT executable Tarl OS code.**

The 27 ``.thirsty`` source files from the original
Tarl OS specification have been **removed** from
this subpackage. They used outdated Thirsty-Lang
syntax (``shield X { ... }`` as a class
declaration) that is NOT valid in the current
canonical Thirsty-Lang grammar (where ``shield``
is a block keyword inside ``governed`` modules,
not a class keyword). Per the user's instruction
("DO NOT IMPLEMENT LEGACY OR OUTDATED REPLACING
THE NEW THIRSTY-LANG UTF"), outdated syntax is
not ported.

The 5 ``.md`` docs from the original recovery
have also been **removed** because they started
with Obsidian YAML frontmatter
(``created:``, ``last_verified:``, ``status:``,
``review_cycle:``) — i.e., they were Obsidian-vault
artifacts. Per the user's instruction, Obsidian
content is dropped, not ported.

The 3 legacy Python files that referenced the
deleted ``.thirsty`` files (``bridge.py``,
``tests/multi_turn_tests.py``,
``tests/test_legacy_tarl_os_bridge.py``) have
also been removed. They were paired with the
outdated ``.thirsty`` files and tested for
behavior that no longer applies.

What is preserved here (4 files):

  - ``SUMMARY.txt`` — plain-text implementation
    summary (no Obsidian frontmatter)
  - ``tests/ARCHITECTURE.py`` — legacy code that
    does not reference the deleted ``.thirsty``
    files (preserved as historical reference)
  - ``tests/results/stress_test_results_1769808374.json``
    — actual stress-test result data from the
    legacy Tarl OS run (preserved as data)
  - ``__init__.py`` — this file

If a future Tarl OS is implemented, it MUST use
the canonical Thirsty-Lang syntax (see
``C:\\Users\\Quencher\\Desktop\\Github\\Personal Repo\\
's\\thirsty_lang_exploration_0754\\src\\utf\\thirsty_lang\\
lexer.py`` and ``parser.py``). The legacy Tarl OS
``.thirsty`` files in the vault are NOT a valid
specification of the future Tarl OS.
"""

from __future__ import annotations

from pathlib import Path

_THIRSTY_OS_ROOT = Path(__file__).resolve().parent


def os_spec_root() -> Path:
    """Return the root directory of the Tarl OS
    historical spec subpackage."""
    return _THIRSTY_OS_ROOT


def list_legacy_thirsty_files() -> list[Path]:
    """Return an empty list. The legacy ``.thirsty``
    files were removed; this function is kept for
    backward compatibility with code that may have
    imported it."""
    return []


def list_legacy_docs() -> list[Path]:
    """List the legacy plain-text documentation
    files in this subpackage (the ``SUMMARY.txt``
    file). The 4 ``.md`` docs were removed because
    they were Obsidian-vault artifacts."""
    return sorted(_THIRSTY_OS_ROOT.glob("*.txt"))


__all__ = [
    "list_legacy_docs",
    "list_legacy_thirsty_files",
    "os_spec_root",
]
