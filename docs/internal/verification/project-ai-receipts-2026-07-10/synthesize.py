"""Assemble summary.json + summary.csv from the measured JSON metrics and the
verified tool results. All numbers trace to raw/ outputs; nothing estimated."""

from __future__ import annotations

import csv
import json
from pathlib import Path

R = Path(__file__).resolve().parent
fs = json.loads((R / "fs_metrics.json").read_text(encoding="utf-8"))
act = json.loads((R / "git_activity.json").read_text(encoding="utf-8"))
inv = json.loads((R / "inventory.json").read_text(encoding="utf-8"))

summary = {
    "audit": {
        "date": "2026-07-10",
        "repo": "Project-AI-Beginnings",
        "head_sha": "656a26dbb245d5d2dbd2626389e9204737698882",
        "branch": "chore/warning-cleanup-utc-artifacts",
        "archive_sha256": "be4b128d37e96013e9e94c1c096e7c9f592457f354085bb18605baaa2a63a343",
        "archive_bytes": 37215466,
        "read_only": True,
    },
    "files": {
        "physical_all_incl_git": fs["physical_all_files"],
        "git_dir_files": fs["git_dir_files"],
        "nongit_files": fs["nongit_files"],
        "git_tracked_files": 2852,
        "excluded_files": fs["excluded_files"],
        "kept_after_standard_exclusions": fs["kept_files"],
        "kept_bytes": fs["kept_bytes"],
        "kept_bytes_note": "84% of kept bytes is untracked generated ML data under "
                           "data/knowledge/ (chunks.jsonl 260MB + vectors.npy 202MB, gitignored)",
    },
    "excluded_by_segment_files": fs["excluded_by_segment"],
    "concentration": {
        "kept_files_under_docs": 2000,
        "kept_files_total": fs["kept_files"],
        "docs_share_pct": round(2000 / fs["kept_files"] * 100, 1),
        "note": "Repository is documentation-dominated; source (Python) is a minority of files.",
    },
    "category_split_kept_files": fs["by_category_files"],
    "extension_buckets": fs["ext_buckets"],
    "lines": {
        "scc_total_files": 2628, "scc_code_lines": 1155111, "scc_total_lines": 1379960,
        "cloc_total_files": 2449, "cloc_code_lines": 1078633, "cloc_comment_lines": 24305,
        "self_counter_total_lines": fs["lines_total"],
        "by_language_scc_code": {
            "Markdown": 606667, "JSON(data)": 344938, "Python": 84753, "HTML": 31019,
            "YAML": 26221, "JavaScript": 8277, "C#": 2180, "TypeScript": 511,
            "PowerShell": 1102, "Shell": 686, "Rust": 180,
        },
        "note": "Line totals are dominated by Markdown docs (~607K) and JSON data (~345K); "
                "Python source code is ~75K-85K lines depending on tool.",
    },
    "tests": {
        "test_files": fs["test_files"],
        "py_test_functions": fs["py_test_functions"],
        "js_test_cases": fs["js_test_cases"],
        "pytest_passed": 2509, "pytest_failed": 0, "pytest_errors": 0,
        "pytest_xfailed": 1, "pytest_skipped": 0, "pytest_exit_code": 0,
        "pytest_runtime_sec": 72.68,
        "assert_in_test_files": fs["assert_in_tests"],
        "assert_all_python": fs["assert_all_py"],
    },
    "static_analysis": {
        "ruff_check": "PASS (repo, receipt dir excluded)",
        "ruff_format": "PASS (425 files already formatted)",
        "mypy_precommit_hook": "PASS (configured strict gate)",
        "black": "N/A - not a repo-configured tool; only-available copy ran under Python 3.11 "
                 "and could not parse 3.12 syntax (invalid run)",
        "bandit_optional_py312": {"issues": 2923, "high": 5, "medium": 30, "low": 2888,
                                  "loc": 77054, "note": "optional/unconfigured; low findings "
                                  "(assert/subprocess) dominate"},
        "pyright_optional_scoped": "1 error in sampled packages/kernel/src/kernel (unconfigured)",
        "eslint_web_configured": "230 problems (largely eslint v10 flat-config migration errors)",
        "semgrep": "available (1.169.0) but not executed - auto config requires telemetry; "
                   "declined for a private-repo audit (bandit used for offline SAST)",
    },
    "authorship": {
        "first_commit_sha": "4acf92a9fe69b5e30577fb6b926196e9575013bb",
        "first_commit_date": act["first_commit_date"],
        "first_commit_author": "Jeremy Karrick <IAmSoThirsty@users.noreply.github.com>",
        "head_commit_date": "2026-07-10",
        "elapsed_calendar_days": act["elapsed_days"],
        "commits_current_branch_head": act["head_commit_count"],
        "commits_all_refs": act["allrefs_commit_count"],
        "distinct_identities": act["distinct_authors_allrefs"],
        "current_branch_owner_share": "192/192 (100%) owner-attributed by git",
        "all_refs_by_category": act["commits_by_category"],
    },
    "inventory": {
        "python_packages": len(inv["packages_pyproject"]),
        "apps": inv["apps_dirs"],
        "crates": inv["crates_dirs"],
        "console_scripts": list(inv["console_scripts"].keys()),
        "github_workflows": [w.split("/")[-1] for w in inv["workflows"]],
        "helm_charts": len(inv["helm_charts"]),
        "helm_templates": inv["helm_templates"],
        "k8s_kinds": inv["k8s_kinds"],
        "compose_files": inv["compose_files"],
        "terraform_files": len(inv["terraform_files"]),
        "pdf_documents": inv["pdf_count"],
        "license_files": len(inv["license_files"]),
        "submodules": inv["has_submodules"],
        "spdx_headers": inv["spdx_headers"],
    },
    "prometheus": {
        "files_matched": fs["prometheus_files"],
        "note": "Almost all are documentation MENTIONS of 'prometheus' in Markdown. Real "
                "integration = 2 helm templates (PrometheusRule + ServiceMonitor CRs). "
                "No vendored Prometheus, no dashboards, no scrape config.",
    },
    "integrity": {
        "git_fsck": "no non-dangling errors (dangling objects only, which is normal)",
        "git_status": "clean working tree at audit start (receipt dir untracked)",
        "count_objects_packs": 5, "count_objects_pack_size": "199.59 MiB",
        "count_objects_garbage": 11,
        "garbage_note": "11 stray .git/objects/**/tmp_obj_* files (5.45 KiB) - leftover "
                        "temp objects, not corruption; not written by this audit",
        "branches_local": 5, "tags": 0, "submodules": 0, "worktrees": 1,
    },
}
(R / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def flatten(prefix, obj, rows):
    if isinstance(obj, dict):
        for k, v in obj.items():
            flatten(f"{prefix}.{k}" if prefix else k, v, rows)
    elif isinstance(obj, list):
        rows.append((prefix, "; ".join(str(x) for x in obj)))
    else:
        rows.append((prefix, obj))


rows: list = []
flatten("", summary, rows)
with (R / "summary.csv").open("w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["key", "value"])
    w.writerows(rows)

print(f"summary.json + summary.csv written ({len(rows)} flattened rows)")
print(f"headline: physical={summary['files']['physical_all_incl_git']} "
      f"tracked={summary['files']['git_tracked_files']} "
      f"kept={summary['files']['kept_after_standard_exclusions']} "
      f"commits(head)={summary['authorship']['commits_current_branch_head']} "
      f"commits(all)={summary['authorship']['commits_all_refs']}")
