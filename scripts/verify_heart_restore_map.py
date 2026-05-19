#!/usr/bin/env python3
"""Validate the Heart Restore control-plane map against the local checkout."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from repo_scan_contract import SCAN_PHASES, RepoScanSnapshot, collect_repo_scan

BUCKET_1_REQUIRED = (
    "governance/sovereign_runtime.py",
    "governance/iron_path.py",
    "governance/existential_proof.py",
    "governance/singularity_override.py",
    "governance/sovereign_verifier.py",
    "governance/core.py",
    "src/app/governance/audit_log.py",
    "src/app/governance/sovereign_audit_log.py",
    "src/app/governance/tsa_provider.py",
    "canonical/replay.py",
    "canonical/server.py",
    "src/app/core/ai_systems.py",
    "src/app/core/command_override.py",
    "src/app/core/config_loader.py",
    "src/app/core/distress_kernel.py",
    "src/app/core/error_aggregator.py",
    "src/app/core/cognition_kernel.py",
    "src/app/core/guardian_approval_system.py",
    "src/app/core/legion_protocol.py",
    "src/app/core/memory_engine.py",
    "src/app/core/operational_substructure.py",
    "src/app/core/perspective_engine.py",
    "src/app/core/realtime_monitoring.py",
    "src/app/core/red_hat_expert_defense.py",
    "src/app/core/red_team_stress_test.py",
    "src/app/core/relationship_model.py",
    "src/app/core/robotic_controller_manager.py",
    "src/app/core/robotic_hardware_layer.py",
    "src/app/core/robotic_mainframe_integration.py",
    "src/app/core/sensor_fusion.py",
    "src/app/core/shadow_containment.py",
    "src/app/core/shadow_execution_plane.py",
    "src/app/core/super_kernel.py",
    "src/app/core/tarl_operational_extensions.py",
    "src/app/core/tier_governance_policies.py",
    "src/app/core/tier_health_dashboard.py",
    "src/app/core/location_tracker.py",
    "src/app/pipeline/signal_flows.py",
    "cognition/triumvirate.py",
    "cognition/kernel_liara.py",
    "cognition/liara_guard.py",
    "src/app/agents/oversight.py",
    "src/app/agents/planner.py",
    "src/app/agents/validator.py",
    "src/app/agents/explainability.py",
    "src/app/agents/tarl_protector.py",
    "src/app/agents/thirsty_lang_validator.py",
    ".github/workflows/codex-deus-ultimate.yml",
    ".github/workflows/project-ai-monolith.yml",
    ".github/workflows/format-and-fix.yml",
    ".github/workflows/tk8s-civilization-pipeline.yml",
    ".github/workflows/codeql.yml",
    ".github/workflows/bandit.yml",
    ".github/workflows/security-secret-scan.yml",
    ".github/workflows/generate-sbom.yml",
    "config/distress_simplified.yaml",
    "config/defense_engine.toml",
    "config/god_tier_config.yaml",
    "config/security_hardening.yaml",
    "config/memory_optimization.yaml",
    "config/settings.py",
)

BUCKET_1_CONDITIONAL = (
    "src/app/core/master_harness.py",
    "src/app/core/nld_harness.py",
)

BUCKET_2_OPTIONAL = (
    "src/app/miniature_office",
    "src/app/agents/cerberus_codex_bridge.py",
    "src/app/agents/constitutional_guardrail_agent.py",
    "src/app/agents/red_team_agent.py",
    "src/app/agents/red_team_persona_agent.py",
    "desktop",
    "web",
    "android",
    "services",
    "integrations",
    "emergent-microservices",
    "project_ai",
    "Project-AI.code-workspace",
    "FIX_WORKSTATION.ps1",
    "IDE_Work_Spaces",
    "archive/aspirational_architecture",
)

VAULT_PARENT_REQUIRED = (
    "wiki",
    "wiki/.obsidian",
    "wiki/05_Operations",
)

OPERATIONS_DOCS_REQUIRED = (
    "docs/operations/HEART_RESTORE_MAP_2026-04-02.md",
    "docs/operations/README.md",
    "docs/operations/HEART_RESTORE_STATUS_2026-04-17.md",
)

REPO_LIBRARY_REQUIRED = (
    "wiki/09_Repo-Library/Local-Repo-Library.md",
    "wiki/09_Repo-Library/Local-Git-State.md",
    "wiki/09_Repo-Library/Local-Working-Tree.md",
    "wiki/09_Repo-Library/local_file_manifest.jsonl",
    "wiki/09_Repo-Library/local_folder_manifest.jsonl",
    "wiki/09_Repo-Library/ignored_file_manifest.jsonl",
)

SUPPORT_PATHS = (
    "FIX_WORKSTATION.ps1",
    "IDE_Work_Spaces/README.md",
    "IDE_Work_Spaces/project-ai-control-plane.code-workspace",
    "scripts/verify_heart_restore_map.py",
    "docs/operations/README.md",
    "docs/operations/HEART_RESTORE_STATUS_2026-04-17.md",
)

BASELINE_FILES = (
    "SYSTEM_MANIFEST.md",
    "FULL_REPOSITORY_MANIFEST.md",
    "DIRECTORY_INDEX.md",
    "REPO_TREE_DIAGRAM.md",
)


@dataclass(frozen=True)
class Check:
    status: str
    path: str
    scope: str
    message: str


def exists(root: Path, relative_path: str) -> bool:
    return (root / relative_path).exists()


def baseline_mentions(root: Path, relative_path: str) -> bool:
    needles = {relative_path, relative_path.replace("/", "\\")}
    for manifest in BASELINE_FILES:
        path = root / manifest
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if any(needle in text for needle in needles):
            return True
    return False


def read_library_head(root: Path) -> str | None:
    library = root / "wiki/09_Repo-Library/Local-Repo-Library.md"
    if not library.exists():
        return None
    text = library.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"^- HEAD:\s+`([^`]+)`", text, re.MULTILINE)
    return match.group(1) if match else None


def count_jsonl_lines(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        return sum(1 for _line in handle)


def library_records(root: Path, wanted_paths: set[str]) -> dict[str, dict[str, Any]]:
    manifest = root / "wiki/09_Repo-Library/local_file_manifest.jsonl"
    records: dict[str, dict[str, Any]] = {}
    if not manifest.exists():
        return records
    with manifest.open("r", encoding="utf-8", errors="ignore") as handle:
        for line in handle:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            relative_path = str(record.get("relative_path") or "")
            if relative_path in wanted_paths:
                records[relative_path] = record
    return records


def validate_paths(root: Path) -> list[Check]:
    checks: list[Check] = []
    for path in VAULT_PARENT_REQUIRED:
        if exists(root, path):
            checks.append(
                Check("pass", path, "vault-parent", "required vault path exists")
            )
        else:
            checks.append(
                Check("fail", path, "vault-parent", "required vault path is missing")
            )

    for path in OPERATIONS_DOCS_REQUIRED:
        if exists(root, path):
            checks.append(
                Check("pass", path, "operations-docs", "required operations doc exists")
            )
        else:
            checks.append(
                Check(
                    "fail",
                    path,
                    "operations-docs",
                    "required operations doc is missing",
                )
            )

    for path in BUCKET_1_REQUIRED:
        if exists(root, path):
            checks.append(
                Check("pass", path, "bucket-1", "required control-plane path exists")
            )
        else:
            checks.append(
                Check(
                    "fail", path, "bucket-1", "required control-plane path is missing"
                )
            )

    for path in BUCKET_1_CONDITIONAL:
        if exists(root, path):
            checks.append(
                Check("pass", path, "bucket-1-conditional", "conditional path exists")
            )
        elif baseline_mentions(root, path):
            checks.append(
                Check(
                    "fail",
                    path,
                    "bucket-1-conditional",
                    "conditional path is in baseline but missing from checkout",
                )
            )
        else:
            checks.append(
                Check(
                    "skip",
                    path,
                    "bucket-1-conditional",
                    "conditional path is not present in baseline manifests",
                )
            )

    for path in BUCKET_2_OPTIONAL:
        if exists(root, path):
            checks.append(
                Check("pass", path, "bucket-2", "optional live-root surface exists")
            )
        else:
            checks.append(
                Check(
                    "warn",
                    path,
                    "bucket-2",
                    "optional live-root surface is absent; restore only from a verified candidate",
                )
            )
    return checks


def validate_scan_order(snapshot: RepoScanSnapshot) -> list[Check]:
    return [
        Check(
            "pass" if snapshot.phases == SCAN_PHASES else "fail",
            "repo-scan-contract",
            "repo-scan-contract",
            "scan order is " + " -> ".join(snapshot.phases),
        )
    ]


def validate_tracked_phase(snapshot: RepoScanSnapshot) -> list[Check]:
    return [
        Check(
            "pass",
            "tracked",
            "git",
            f"{len(snapshot.tracked)} tracked paths scanned before branches",
        )
    ]


def validate_untracked_git_phase(snapshot: RepoScanSnapshot) -> list[Check]:
    checks: list[Check] = []
    checks.append(
        Check(
            "pass" if snapshot.git_dir_exists else "fail",
            snapshot.git_dir_raw,
            "git",
            (
                "git metadata path resolves"
                if snapshot.git_dir_exists
                else "git metadata path is missing"
            ),
        )
    )
    for required, present in snapshot.git_metadata.items():
        checks.append(
            Check(
                "pass" if present else "fail",
                f"{snapshot.git_dir_raw}/{required}",
                "git",
                (
                    "required git metadata exists"
                    if present
                    else "required git metadata is missing"
                ),
            )
        )

    modified = [line for line in snapshot.status_lines if not line.startswith("??")]

    checks.append(Check("pass", "HEAD", "git", f"current HEAD is {snapshot.head[:12]}"))
    checks.append(
        Check(
            "pass",
            "branch",
            "git",
            f"current branch is {snapshot.branch}",
        )
    )
    checks.append(
        Check(
            "warn" if modified else "pass",
            "working-tree",
            "git",
            f"{len(modified)} modified tracked paths",
        )
    )
    checks.append(
        Check(
            "warn" if snapshot.untracked else "pass",
            "untracked",
            "git",
            f"{len(snapshot.untracked)} untracked non-ignored paths",
        )
    )
    checks.append(
        Check("pass", "ignored", "git", f"{len(snapshot.ignored)} ignored paths")
    )
    return checks


def validate_repo_library(root: Path, snapshot: RepoScanSnapshot) -> list[Check]:
    checks: list[Check] = []
    for path in REPO_LIBRARY_REQUIRED:
        checks.append(
            Check(
                "pass" if exists(root, path) else "fail",
                path,
                "repo-library",
                (
                    "library artifact exists"
                    if exists(root, path)
                    else "library artifact is missing"
                ),
            )
        )

    current_head = snapshot.head
    library_head = read_library_head(root)
    if library_head and current_head:
        checks.append(
            Check(
                "pass" if library_head == current_head else "warn",
                "wiki/09_Repo-Library/Local-Repo-Library.md",
                "repo-library",
                (
                    "library HEAD matches current git HEAD"
                    if library_head == current_head
                    else f"library HEAD {library_head[:12]} is behind current HEAD {current_head[:12]}"
                ),
            )
        )
    else:
        checks.append(
            Check(
                "warn",
                "wiki/09_Repo-Library/Local-Repo-Library.md",
                "repo-library",
                "could not compare library HEAD to current git HEAD",
            )
        )

    wanted = set(BUCKET_1_REQUIRED) | set(BUCKET_1_CONDITIONAL) | set(SUPPORT_PATHS)
    records = library_records(root, wanted)
    for path in BUCKET_1_REQUIRED:
        status = "pass" if path in records else "warn"
        message = (
            "library records required control-plane path"
            if path in records
            else "library does not currently record this required path; refresh may be needed"
        )
        checks.append(Check(status, path, "repo-library", message))

    for path in SUPPORT_PATHS:
        status = "pass" if path in records else "warn"
        message = (
            "library records support path"
            if path in records
            else "support path is not yet in the library mirror; refresh may be needed"
        )
        checks.append(Check(status, path, "repo-library", message))

    ignored_manifest = root / "wiki/09_Repo-Library/ignored_file_manifest.jsonl"
    ignored_count = count_jsonl_lines(ignored_manifest)
    live_ignored = len(snapshot.ignored)
    if ignored_count and live_ignored:
        checks.append(
            Check(
                "pass" if ignored_count == live_ignored else "warn",
                "wiki/09_Repo-Library/ignored_file_manifest.jsonl",
                "repo-library",
                (
                    "ignored manifest count matches live git ignored count"
                    if ignored_count == live_ignored
                    else f"ignored manifest has {ignored_count}; live git reports {live_ignored}"
                ),
            )
        )
    return checks


def validate_branch_trees(snapshot: RepoScanSnapshot) -> list[Check]:
    checks: list[Check] = []
    survey = snapshot.branch_tree_survey
    refs = list(survey.get("refs") or [])
    if not refs:
        return [
            Check("warn", "branches", "git-branches", "no local or remote refs found")
        ]

    checks.append(
        Check(
            "pass",
            "branches",
            "git-branches",
            f"surveyed {len(refs)} refs after tracked scan",
        )
    )
    missing_by_ref = list(survey.get("missing_by_ref") or [])
    unreadable_refs = list(survey.get("unreadable_refs") or [])

    if unreadable_refs:
        checks.append(
            Check(
                "warn",
                "branches",
                "git-branches",
                f"{len(unreadable_refs)} refs could not be read",
            )
        )

    if missing_by_ref:
        worst = max(missing_by_ref, key=lambda item: len(item["missing"]))
        examples = ", ".join(item["ref"] for item in missing_by_ref[:5])
        checks.append(
            Check(
                "warn",
                "branches",
                "git-branches",
                (
                    f"{len(missing_by_ref)} refs are missing one or more Bucket 1 paths; "
                    f"worst is {worst['ref']} missing {len(worst['missing'])}; examples: {examples}"
                ),
            )
        )
    else:
        checks.append(
            Check("pass", "branches", "git-branches", "all refs include Bucket 1 paths")
        )
    return checks


def load_workspace(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except OSError as exc:
        return None, str(exc)
    except json.JSONDecodeError as exc:
        return None, f"invalid JSON: {exc}"


def validate_workspace(root: Path, strict_external: bool) -> list[Check]:
    checks: list[Check] = []
    root_workspace = root / "Project-AI.code-workspace"
    workspace, error = load_workspace(root_workspace)
    if error:
        return [
            Check("fail", "Project-AI.code-workspace", "workspace", error),
        ]

    folders = workspace.get("folders", []) if workspace else []
    local_root = any(
        item.get("path") == "." for item in folders if isinstance(item, dict)
    )
    checks.append(
        Check(
            "pass" if local_root else "fail",
            "Project-AI.code-workspace",
            "workspace",
            (
                "root workspace includes the checkout root"
                if local_root
                else "root workspace omits '.'"
            ),
        )
    )

    missing_external = []
    for item in folders:
        if not isinstance(item, dict) or "path" not in item:
            continue
        raw_path = item["path"]
        resolved = (root / raw_path).resolve()
        if raw_path == ".":
            continue
        if not resolved.exists():
            missing_external.append(raw_path)
    if missing_external:
        status = "fail" if strict_external else "warn"
        checks.append(
            Check(
                status,
                "Project-AI.code-workspace",
                "workspace",
                f"{len(missing_external)} external workspace folders do not resolve locally",
            )
        )
    else:
        checks.append(
            Check(
                "pass",
                "Project-AI.code-workspace",
                "workspace",
                "all workspace folders resolve",
            )
        )

    compact_path = root / "IDE_Work_Spaces/project-ai-control-plane.code-workspace"
    compact, compact_error = load_workspace(compact_path)
    if compact_error:
        checks.append(
            Check(
                "fail",
                "IDE_Work_Spaces/project-ai-control-plane.code-workspace",
                "workspace",
                compact_error,
            )
        )
        return checks

    for item in compact.get("folders", []) if compact else []:
        if not isinstance(item, dict) or "path" not in item:
            checks.append(
                Check(
                    "fail",
                    "IDE_Work_Spaces/project-ai-control-plane.code-workspace",
                    "workspace",
                    "workspace folder entry is malformed",
                )
            )
            continue
        raw_path = item["path"]
        resolved = (compact_path.parent / raw_path).resolve()
        status = "pass" if resolved.exists() else "fail"
        message = (
            "compact workspace folder resolves"
            if resolved.exists()
            else "compact workspace folder is missing"
        )
        checks.append(Check(status, raw_path, "workspace", message))

    return checks


def summarize(checks: list[Check]) -> dict[str, Any]:
    counts = {"pass": 0, "warn": 0, "skip": 0, "fail": 0}
    for check in checks:
        counts[check.status] += 1
    return {
        "status": "fail" if counts["fail"] else "ok",
        "counts": counts,
        "checks": [asdict(check) for check in checks],
    }


def print_human(summary: dict[str, Any]) -> None:
    print(f"Heart restore status: {summary['status']}")
    counts = summary["counts"]
    print(
        "Checks: "
        f"{counts['pass']} pass, {counts['warn']} warn, "
        f"{counts['skip']} skip, {counts['fail']} fail"
    )
    for check in summary["checks"]:
        if check["status"] == "pass":
            continue
        print(
            f"- {check['status'].upper()} [{check['scope']}] "
            f"{check['path']}: {check['message']}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Project-AI against the Heart Restore control-plane map."
    )
    parser.add_argument("--root", default=".", help="Project-AI checkout root")
    parser.add_argument(
        "--strict-workspace",
        action="store_true",
        help="Fail when external workspace folders do not resolve locally.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    snapshot = collect_repo_scan(root, branch_required_paths=set(BUCKET_1_REQUIRED))
    checks = validate_scan_order(snapshot)
    checks.extend(validate_tracked_phase(snapshot))
    checks.extend(validate_branch_trees(snapshot))
    checks.extend(validate_untracked_git_phase(snapshot))
    checks.extend(validate_paths(root))
    checks.extend(validate_repo_library(root, snapshot))
    checks.extend(validate_workspace(root, strict_external=args.strict_workspace))
    summary = summarize(checks)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_human(summary)
    return 1 if summary["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
