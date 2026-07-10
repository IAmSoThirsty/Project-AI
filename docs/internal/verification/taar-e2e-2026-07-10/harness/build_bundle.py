"""Build the reproducible verification bundle for the 2026-07-10 TAAR E2E run.

Harvests the live scratch facility into
docs/internal/verification/taar-e2e-2026-07-10/ with machine-readable
manifests, per-artifact hashes, an audit chain head, denial records,
redaction assertions, cleanliness receipts, and invocation metadata.
"""

from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from importlib.metadata import version as dist_version
from pathlib import Path

import yaml

BEGINNINGS = Path(r"T:\00-Active\Project-AI-Beginnings")
FACILITY = Path(r"T:\Temp\claude\scratch\taar-e2e")
AUTOMATION = FACILITY / ".project-ai" / "automation"
BUNDLE = BEGINNINGS / "docs" / "internal" / "verification" / "taar-e2e-2026-07-10"
HARNESS_SRC = Path(r"T:\Temp\claude\scratch\taar_e2e.py")
SOURCE_REPO = Path(r"T:\01-Projects\TAAR-Agent-Taskforce\TAAR-Agent-Taskforce")
SOURCE_SHA = "7b51966317f64c7b1fe277e0db0935c5e460704c"
GENESIS = "0" * 64


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_hash(payload: dict, drop: str) -> str:
    data = dict(payload)
    data.pop(drop, None)
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return sha256_text(canonical)


def git(args: list[str], cwd: Path) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout.strip()


if BUNDLE.exists():
    shutil.rmtree(BUNDLE)
BUNDLE.mkdir(parents=True)

# ---------------------------------------------------------------- registry snapshot
(BUNDLE / "registry").mkdir()
registry_snapshot: dict[str, str] = {}
for src in sorted((FACILITY / "registry").glob("*.yaml")):
    shutil.copy2(src, BUNDLE / "registry" / src.name)
    registry_snapshot[src.name] = sha256_file(src)
registry_combined = sha256_text(
    "\n".join(f"{name}:{digest}" for name, digest in sorted(registry_snapshot.items()))
)

# ---------------------------------------------------------------- facility manifest
facility_manifest: dict[str, dict[str, object]] = {}
for path in sorted(FACILITY.rglob("*")):
    if not path.is_file() or ".git" in path.parts:
        continue
    rel = path.relative_to(FACILITY).as_posix()
    facility_manifest[rel] = {"size": path.stat().st_size, "sha256": sha256_file(path)}

# ---------------------------------------------------------------- evidence bundles
(BUNDLE / "evidence").mkdir()
evidence_entries: list[dict[str, object]] = []
for src in sorted((AUTOMATION / "evidence").rglob("evidence.yaml")):
    data = yaml.safe_load(src.read_text(encoding="utf-8"))
    recomputed = canonical_hash(data, drop="evidence_hash")
    dest = BUNDLE / "evidence" / src.parent.parent.name / src.parent.name
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest / "evidence.yaml")
    evidence_entries.append(
        {
            "agent_id": data["agent_id"],
            "run_id": data["run_id"],
            "classification": data["classification"],
            "evidence_hash": data["evidence_hash"],
            "recomputed_hash_matches": recomputed == data["evidence_hash"],
            "file_sha256": sha256_file(src),
        }
    )

# ---------------------------------------------------------------- writer outputs
(BUNDLE / "outputs").mkdir()
output_entries: list[dict[str, object]] = []
for src in sorted((AUTOMATION / "evidence").rglob("output.yaml")):
    data = yaml.safe_load(src.read_text(encoding="utf-8"))
    dest = BUNDLE / "outputs" / src.parent.parent.name / src.parent.name
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest / "output.yaml")
    output_entries.append(
        {
            "writer_agent_id": data["writer_agent_id"],
            "run_id": data["run_id"],
            "source_reader_agent_id": data["source_reader_agent_id"],
            "source_evidence_hash": data["source_evidence_hash"],
            "classification": data["classification"],
            "output_paths": data["output_paths"],
            "file_sha256": sha256_file(src),
        }
    )
known_evidence_hashes = {e["evidence_hash"] for e in evidence_entries}
for entry in output_entries:
    entry["source_evidence_hash_resolves"] = entry["source_evidence_hash"] in known_evidence_hashes

# ---------------------------------------------------------------- reports + digests
report_entries: list[dict[str, object]] = []
for sub in ("reports", "digests"):
    for src in sorted((AUTOMATION / sub).rglob("*.md")):
        rel = src.relative_to(AUTOMATION)
        dest = BUNDLE / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        report_entries.append(
            {"path": rel.as_posix(), "size": src.stat().st_size, "sha256": sha256_file(src)}
        )

# ---------------------------------------------------------------- audit spine
(BUNDLE / "audit").mkdir()
audit_files: list[dict[str, object]] = []
records: list[dict[str, object]] = []
for src in sorted((AUTOMATION / "audit").glob("*.audit.jsonl")):
    shutil.copy2(src, BUNDLE / "audit" / src.name)
    lines = [line for line in src.read_text(encoding="utf-8").splitlines() if line.strip()]
    audit_files.append({"file": src.name, "records": len(lines), "sha256": sha256_file(src)})
    records.extend(json.loads(line) for line in lines)

all_seals_valid = all(canonical_hash(rec, drop="hash") == rec["hash"] for rec in records)
chain = GENESIS
for rec in records:
    chain = sha256_text(chain + str(rec["hash"]))
denials = [
    {
        "timestamp": rec["timestamp"],
        "agent_id": rec["agent_id"],
        "run_id": rec["run_id"],
        "reasons": rec["message"],
        "record_seal": rec["hash"],
    }
    for rec in records
    if rec["event_type"] == "admission_denied"
]
run_table: dict[str, dict[str, object]] = {}
for rec in records:
    run_table[str(rec["run_id"])] = {
        "agent_id": rec["agent_id"],
        "final_status": rec["status"],
        "classification": rec["classification"],
        "at": rec["timestamp"],
    }

# ---------------------------------------------------------------- redaction assertions
fake_token = "ghp_" + "Qq1Ww2Ee3Rr4Tt5Yy6Uu7Ii8"
token_hash = sha256_text(fake_token)
plaintext_hits: list[str] = []
for rel, meta in facility_manifest.items():
    path = FACILITY / rel
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        continue
    if fake_token in text:
        plaintext_hits.append(rel)
secret_report = (AUTOMATION / "reports" / "security" / "secrets-latest.md").read_text(
    encoding="utf-8"
)
redaction = {
    "planted_token_sha256": token_hash,
    "planted_input_file": "config_backup.py (facility input; deliberately NOT in this bundle)",
    "plaintext_locations_in_facility": plaintext_hits,
    "plaintext_in_taar_outputs": [p for p in plaintext_hits if p.startswith(".project-ai/")],
    "redacted_fragment_in_secret_report": "ghp_...7Ii8" in secret_report,
}

# ---------------------------------------------------------------- invocation + receipts
beginnings_head = git(["rev-parse", "HEAD"], BEGINNINGS)
beginnings_status = git(["status", "--porcelain"], BEGINNINGS)
source_status = git(["status", "--porcelain"], SOURCE_REPO)
source_head = git(["rev-parse", "HEAD"], SOURCE_REPO)

invocation = {
    "run_date_utc": "2026-07-10",
    "harness": "harness/taar_e2e.py",
    "harness_sha256": sha256_file(HARNESS_SRC),
    "passes": [
        {
            "step": 1,
            "command": "uv run python taar_e2e.py",
            "description": "seed facility, plant inputs, drive 21 readers then 22 writers",
        },
        {
            "step": 2,
            "command": "uv run python -m taar.cli run phantom-reader --repo <facility>; "
            "uv run python -m taar.cli run phantom-report-writer --repo <facility>",
            "description": "quarantine-class phantom pass",
        },
        {
            "step": 3,
            "command": "uv run python -m taar.cli workflows classify|scan|harden --repo <facility>",
            "description": "Workflow Guardian CLI (read-only; classify=SECRET, scan exit 1 on "
            "critical findings by design)",
        },
    ],
    "environment": {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "taar_module_version": "0.1.0",
        "project_ai_taar_dist": dist_version("project-ai-taar"),
        "pyyaml": dist_version("pyyaml"),
        "typer": dist_version("typer"),
        "rich": dist_version("rich"),
    },
    "code_under_test": {
        "beginnings_repo": str(BEGINNINGS),
        "beginnings_head": beginnings_head,
        "taar_package": "packages/taar (commit e53bf2e7 feat(taar))",
        "upstream_source": str(SOURCE_REPO),
        "upstream_source_sha": SOURCE_SHA,
    },
    "planted_inputs": {
        "workflows": [
            ".github/workflows/ci.yaml (copied from Beginnings)",
            ".github/workflows/publish.yaml (copied from Beginnings)",
            ".github/workflows/dangerous.yml (packages/taar/examples/github-actions-dangerous)",
            ".github/workflows/hardened.yml (packages/taar/examples/github-actions-hardened)",
        ],
        "secret": "fake ghp_ token in config_backup.py (sha256 in redaction section)",
        "stale_path": "NOTES.md referencing T:/Project-AI-Beginnings (pre-migration path)",
    },
}

status_lines = [line for line in beginnings_status.splitlines() if line.strip()]
non_bundle_deltas = [
    line for line in status_lines if "docs/internal/verification/" not in line
]
cleanliness = {
    "checked_utc": datetime.now(UTC).isoformat(),
    "beginnings_head": beginnings_head,
    "beginnings_git_status_porcelain": beginnings_status,
    "beginnings_deltas_other_than_this_bundle": non_bundle_deltas,
    "beginnings_clean_apart_from_this_bundle": non_bundle_deltas == [],
    "upstream_source_head": source_head,
    "upstream_source_head_matches_port": source_head == SOURCE_SHA,
    "upstream_source_git_status_porcelain": source_status,
    "upstream_source_clean": source_status == "",
    "facility_path": str(FACILITY),
    "note": "All TAAR runtime state stayed under the facility. The Beginnings tree was clean "
    "after the E2E run (verified before bundle creation); at receipt time its only delta is "
    "this bundle directory itself. The read-only upstream source was untouched.",
}

# ---------------------------------------------------------------- harness copies
(BUNDLE / "harness").mkdir()
shutil.copy2(HARNESS_SRC, BUNDLE / "harness" / "taar_e2e.py")

bundle_doc = {
    "schema": "taar-e2e-verification-bundle/1",
    "created_utc": datetime.now(UTC).isoformat(),
    "registry_snapshot": {"files": registry_snapshot, "combined_sha256": registry_combined},
    "facility_manifest": facility_manifest,
    "evidence": evidence_entries,
    "outputs": output_entries,
    "reports": report_entries,
    "audit": {
        "files": audit_files,
        "total_records": len(records),
        "per_record_seals_valid": all_seals_valid,
        "chain_head": chain,
        "chain_algorithm": "h0 = 64*'0'; h_i = sha256(hex(h_{i-1}) + record_i.hash) over records "
        "in file order. NOTE: TAAR seals each record individually (sha256 of canonical JSON "
        "minus 'hash'); this chain head is computed BY THIS BUNDLE over the ordered seals, it "
        "is not an upstream TAAR feature.",
        "denials": denials,
    },
    "runs": run_table,
    "redaction": redaction,
    "invocation": invocation,
    "cleanliness_receipt": cleanliness,
}
(BUNDLE / "bundle.json").write_text(
    json.dumps(bundle_doc, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)

print(f"bundle dir: {BUNDLE}")
print(f"evidence: {len(evidence_entries)} (all recomputed hashes match: "
      f"{all(e['recomputed_hash_matches'] for e in evidence_entries)})")
print(f"outputs: {len(output_entries)} (all source hashes resolve: "
      f"{all(o['source_evidence_hash_resolves'] for o in output_entries)})")
print(f"reports+digests: {len(report_entries)}")
print(f"audit records: {len(records)}, seals valid: {all_seals_valid}")
print(f"chain head: {chain}")
print(f"denials: {len(denials)}")
print(f"redaction: outputs clean = {redaction['plaintext_in_taar_outputs'] == []}, "
      f"plaintext only in: {plaintext_hits}")
print(
    "cleanliness: beginnings clean apart from bundle = "
    f"{cleanliness['beginnings_clean_apart_from_this_bundle']}, "
    f"source clean = {cleanliness['upstream_source_clean']}"
)
