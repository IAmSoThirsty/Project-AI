from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ALLOWED_KEYS = {
    "suite",
    "scenario_id",
    "action",
    "context",
    "expected_allowed",
    "allowed",
    "reason",
    "passed",
    "ts_utc",
}


def main(argv: list[str]) -> int:
    if len(argv) < 4:
        print(
            "Usage: python tools/merge_fourlaws_artifacts.py <out_jsonl> <out_sha256> <in1.jsonl> [in2.jsonl ...]",
            file=sys.stderr,
        )
        return 2

    out_jsonl = Path(argv[1])
    out_sha256 = Path(argv[2])
    in_files = [Path(p) for p in argv[3:]]

    out_jsonl.parent.mkdir(parents=True, exist_ok=True)

    merged_count = 0
    bad_lines = 0
    ts_merge = datetime.now(UTC).isoformat()

    with out_jsonl.open("w", encoding="utf-8") as out:
        for f in in_files:
            with f.open("r", encoding="utf-8") as src:
                for line in src:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except Exception:
                        bad_lines += 1
                        continue

                    sanitized = {k: obj.get(k) for k in ALLOWED_KEYS if k in obj}
                    sanitized["merge_ts_utc"] = ts_merge
                    out.write(json.dumps(sanitized, ensure_ascii=False) + "\n")
                    merged_count += 1

    # Write sha256
    h = hashlib.sha256()
    with out_jsonl.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    digest = h.hexdigest()
    out_sha256.write_text(f"{digest}  {out_jsonl.name}\n", encoding="utf-8")

    print(f"merged={merged_count} bad_lines={bad_lines} -> {out_jsonl}")
    print(f"sha256={digest} -> {out_sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
