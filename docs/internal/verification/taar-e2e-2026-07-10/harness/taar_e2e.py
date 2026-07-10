"""TAAR end-to-end run in an isolated scratch facility.

Seeds a facility, plants real content (this repo's workflows, a
dangerous example workflow, a fake secret, a stale path), then drives
every enabled reader and writer through the governed executor and
prints the resulting evidence/report/audit surfaces.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

BEGINNINGS = Path(r"T:\00-Active\Project-AI-Beginnings")
TAAR_PKG = BEGINNINGS / "packages" / "taar"
FACILITY = Path(r"T:\Temp\claude\scratch\taar-e2e")

# ---------------------------------------------------------------- setup
if FACILITY.exists():
    shutil.rmtree(FACILITY)
FACILITY.mkdir(parents=True)

import taar  # noqa: E402

seed = Path(taar.__file__).parent / "seed"
(FACILITY / "registry").mkdir()
for src in sorted((seed / "registry").glob("*.yaml")):
    shutil.copy2(src, FACILITY / "registry" / src.name)
shutil.copy2(seed / "taar.toml", FACILITY / "taar.toml")

# Real workflows from Project-AI Beginnings + TAAR's dangerous/hardened examples
wf_dir = FACILITY / ".github" / "workflows"
wf_dir.mkdir(parents=True)
for real in sorted((BEGINNINGS / ".github" / "workflows").glob("*.yaml")):
    shutil.copy2(real, wf_dir / real.name)
shutil.copy2(TAAR_PKG / "examples" / "github-actions-dangerous" / "dangerous.yml", wf_dir)
shutil.copy2(TAAR_PKG / "examples" / "github-actions-hardened" / "hardened.yml", wf_dir)

# Planted findings: a fake secret (concatenated) and a stale path reference
fake_token = "ghp_" + "Qq1Ww2Ee3Rr4Tt5Yy6Uu7Ii8"
(FACILITY / "config_backup.py").write_text(f'API_TOKEN = "{fake_token}"\n', encoding="utf-8")
(FACILITY / "NOTES.md").write_text(
    "Migration note: old checkout lived at T:/Project-AI-Beginnings/engines\n",
    encoding="utf-8",
)

# Commit everything so deny_if_dirty agents see a clean facility
subprocess.run(["git", "init", "-q"], cwd=FACILITY, check=True)
subprocess.run(["git", "add", "-A"], cwd=FACILITY, check=True)
subprocess.run(
    ["git", "-c", "user.email=e2e@taar", "-c", "user.name=e2e", "commit", "-q", "-m", "seed"],
    cwd=FACILITY,
    check=True,
)

# ---------------------------------------------------------------- swarm
from taar.config import load_taar_config  # noqa: E402
from taar.errors import AdmissionDenied, TaarError  # noqa: E402
from taar.executor import run_agent  # noqa: E402
from taar.models import AgentClass  # noqa: E402

from taar.registry import load_registry  # noqa: E402

config = load_taar_config(FACILITY)
registry = load_registry(FACILITY)
print(f"facility: {config.repo_root}")
print(f"agents registered: {len(registry.agents_by_id)}")
print(f"registry validation errors: {len(registry.validation_errors)}")

results: list[tuple[str, str, str, str]] = []


def drive(agent_id: str) -> None:
    try:
        record = run_agent(agent_id, config, registry)
        results.append((agent_id, record.status.value, record.classification.value, record.message))
    except AdmissionDenied as exc:
        results.append((agent_id, "DENIED", "-", "; ".join(exc.reasons)[:100]))
    except TaarError as exc:
        results.append((agent_id, "ERROR", "-", str(exc)[:100]))


readers = sorted(
    a.id for a in registry.agents_by_id.values() if a.enabled and a.class_ == AgentClass.READER
)
writers = sorted(
    a.id for a in registry.agents_by_id.values() if a.enabled and a.class_ == AgentClass.WRITER
)
others = sorted(
    a.id
    for a in registry.agents_by_id.values()
    if a.enabled and a.class_ not in (AgentClass.READER, AgentClass.WRITER)
)
print(f"enabled readers: {len(readers)}, writers: {len(writers)}, other classes: {len(others)}")
if others:
    print(f"  (not driven in this pass: {', '.join(others)})")

for agent_id in readers:
    drive(agent_id)
for agent_id in writers:
    drive(agent_id)

print("\n=== SWARM RESULTS (readers then writers) ===")
width = max(len(r[0]) for r in results) + 2
for agent_id, status, classification, message in results:
    print(f"{agent_id:<{width}} {status:<10} {classification:<11} {message}")

# ---------------------------------------------------------------- artifacts
print("\n=== REPORTS WRITTEN ===")
for report in sorted(config.reports_root.rglob("*.md")):
    print(f"  {report.relative_to(FACILITY)}  ({report.stat().st_size} bytes)")

print("\n=== DIGESTS WRITTEN ===")
for digest in sorted(config.digests_root.rglob("*.md")):
    print(f"  {digest.relative_to(FACILITY)}  ({digest.stat().st_size} bytes)")

print("\n=== SECRET REDACTION PROOF ===")
secret_reports = sorted(config.reports_root.rglob("secrets-latest.md"))
if secret_reports:
    text = secret_reports[0].read_text(encoding="utf-8")
    print(f"  planted token present in report: {fake_token in text}")
    print("  redacted lines mentioning token pattern:")
    for line in text.splitlines():
        if "ghp_" in line or "github_token" in line:
            print(f"    {line.strip()[:110]}")
else:
    print("  no secret report found")

print("\n=== AUDIT SPINE (last 12 records) ===")
import json  # noqa: E402

audit_lines: list[str] = []
for audit_file in sorted(config.audit_root.glob("*.audit.jsonl")):
    audit_lines.extend(audit_file.read_text(encoding="utf-8").splitlines())
print(f"  total audit records: {len(audit_lines)}")
for line in audit_lines[-12:]:
    rec = json.loads(line)
    print(f"  {rec['timestamp']}  {rec['agent_id']:<28} {rec['event_type']:<10} {rec['status']}")

print("\n=== EVIDENCE BUNDLES ===")
bundle_count = 0
for evidence_file in sorted(config.evidence_root.rglob("evidence.yaml")):
    bundle_count += 1
print(f"  evidence.yaml bundles: {bundle_count}")
output_count = len(sorted(config.evidence_root.rglob("output.yaml")))
print(f"  writer output records: {output_count}")

print("\nE2E swarm complete.")
