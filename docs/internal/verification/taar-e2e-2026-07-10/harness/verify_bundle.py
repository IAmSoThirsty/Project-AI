"""Standalone verifier for the TAAR E2E verification bundle.

Requires only Python 3.12+ and PyYAML. Run from anywhere:

    python verify_bundle.py [bundle_root]

Checks, in order:
  1. SEAL.json — every bundle file hashes to its sealed value; seal head matches.
  2. Evidence — each evidence.yaml's embedded evidence_hash equals the SHA-256 of
     its canonical JSON (sorted keys, compact separators, evidence_hash removed).
  3. Outputs — every writer output's source_evidence_hash resolves to a bundled
     evidence hash.
  4. Audit — each record's per-record seal recomputes; the bundle chain head
     (h0 = 64*'0'; h_i = sha256(h_{i-1} + seal_i)) matches bundle.json.
  5. Redaction — no full-length ghp_ token anywhere in the bundle; in particular
     nothing hashing to the planted token's SHA-256; the redacted fragment IS
     present in the secret report (positive control).

Exit code 0 = all sections PASS; 1 = any failure.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

GENESIS = "0" * 64
TOKEN_PATTERN = re.compile(r"\bghp_[A-Za-z0-9]{20,}\b")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_hash(payload: dict, drop: str) -> str:
    data = {k: v for k, v in payload.items() if k != drop}
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return sha256_bytes(canonical.encode("utf-8"))


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    bundle = json.loads((root / "bundle.json").read_text(encoding="utf-8"))
    seal = json.loads((root / "SEAL.json").read_text(encoding="utf-8"))
    failures: list[str] = []

    # 1. Seal manifest
    actual_files = {
        p.relative_to(root).as_posix(): sha256_bytes(p.read_bytes())
        for p in sorted(root.rglob("*"))
        if p.is_file() and p.name != "SEAL.json"
    }
    if actual_files != seal["files"]:
        missing = set(seal["files"]) - set(actual_files)
        extra = set(actual_files) - set(seal["files"])
        changed = {
            k for k in set(seal["files"]) & set(actual_files) if seal["files"][k] != actual_files[k]
        }
        failures.append(f"SEAL mismatch: missing={missing} extra={extra} changed={changed}")
    head = sha256_bytes(
        "\n".join(f"{path}:{digest}" for path, digest in sorted(actual_files.items())).encode()
    )
    if head != seal["head_sha256"]:
        failures.append(f"SEAL head mismatch: {head} != {seal['head_sha256']}")
    print(f"[{'FAIL' if failures else 'PASS'}] seal: {len(actual_files)} files, head {head[:16]}…")

    # 2. Evidence hashes
    bad_evidence = []
    for path in sorted((root / "evidence").rglob("evidence.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        if canonical_hash(data, drop="evidence_hash") != data["evidence_hash"]:
            bad_evidence.append(path.relative_to(root).as_posix())
    if bad_evidence:
        failures.append(f"evidence hash mismatches: {bad_evidence}")
    n_evidence = len(list((root / "evidence").rglob("evidence.yaml")))
    print(f"[{'FAIL' if bad_evidence else 'PASS'}] evidence: {n_evidence} bundles recomputed")

    # 3. Output -> evidence linkage
    known = {e["evidence_hash"] for e in bundle["evidence"]}
    unresolved = [
        o["writer_agent_id"] for o in bundle["outputs"] if o["source_evidence_hash"] not in known
    ]
    if unresolved:
        failures.append(f"outputs with unresolved source evidence: {unresolved}")
    print(
        f"[{'FAIL' if unresolved else 'PASS'}] outputs: {len(bundle['outputs'])} "
        "source hashes resolve"
    )

    # 4. Audit seals + chain head
    records: list[dict] = []
    for audit_file in sorted((root / "audit").glob("*.audit.jsonl")):
        for line in audit_file.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
    bad_seals = [r["run_id"] for r in records if canonical_hash(r, drop="hash") != r["hash"]]
    chain = GENESIS
    for record in records:
        chain = sha256_bytes((chain + str(record["hash"])).encode())
    if bad_seals:
        failures.append(f"audit records with invalid seals: {bad_seals}")
    if chain != bundle["audit"]["chain_head"]:
        failures.append(f"audit chain head mismatch: {chain} != {bundle['audit']['chain_head']}")
    audit_ok = not bad_seals and chain == bundle["audit"]["chain_head"]
    print(
        f"[{'PASS' if audit_ok else 'FAIL'}] audit: {len(records)} records sealed, "
        f"chain head {chain[:16]}…, {len(bundle['audit']['denials'])} denials on record"
    )

    # 5. Redaction
    planted = bundle["redaction"]["planted_token_sha256"]
    leaked: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix in (".py",):
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in TOKEN_PATTERN.findall(text):
            leaked.append(f"{path.relative_to(root).as_posix()}: {match[:8]}… ")
            if sha256_bytes(match.encode()) == planted:
                failures.append(f"PLANTED TOKEN LEAKED in {path.relative_to(root).as_posix()}")
    if leaked:
        failures.append(f"full-length ghp_ tokens present in bundle: {leaked}")
    secret_report = root / "reports" / "security" / "secrets-latest.md"
    fragment_ok = "ghp_...7Ii8" in secret_report.read_text(encoding="utf-8")
    if not fragment_ok:
        failures.append("redacted fragment missing from secret report (positive control)")
    redaction_ok = not leaked and fragment_ok
    print(
        f"[{'PASS' if redaction_ok else 'FAIL'}] redaction: no plaintext tokens, "
        f"redacted fragment present={fragment_ok}"
    )

    if failures:
        print("\nVERIFICATION FAILED:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("\nVERIFICATION PASSED: bundle is internally consistent and sealed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
