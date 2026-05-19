from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = PROJECT_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from repo_scan_contract import SCAN_PHASES, collect_repo_scan, ordered_file_paths


def test_repo_scan_contract_enforces_phase_order() -> None:
    snapshot = collect_repo_scan(PROJECT_ROOT, branch_required_paths={"README.md"})

    assert snapshot.phases == SCAN_PHASES
    assert snapshot.tracked
    assert snapshot.branches
    assert "README.md" in snapshot.tracked
    assert snapshot.branch_tree_survey["refs_count"] >= 1


def test_ordered_file_paths_returns_tracked_before_untracked_and_ignored() -> None:
    snapshot = collect_repo_scan(PROJECT_ROOT)
    ordered = ordered_file_paths(
        ["README.md", "scripts/repo_scan_contract.py"], snapshot
    )

    assert ordered.index("README.md") < ordered.index("scripts/repo_scan_contract.py")


def test_repo_library_refresher_uses_shared_scan_contract() -> None:
    refresher = (
        PROJECT_ROOT / "wiki" / "09_Repo-Library" / "refresh_local_repo_library.py"
    )
    text = refresher.read_text(encoding="utf-8")

    assert "collect_repo_scan(ROOT)" in text
    assert "ordered_file_paths(local_files(), scan)" in text
    assert "database_scan_phase" in text
    assert "database_scan_order" in text
