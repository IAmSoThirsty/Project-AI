#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thirstys_standard_runtime.ratification import create_ratification_record, prepare_ratified_manifest  # noqa: E402
from thirstys_standard_runtime.strict_yaml import load  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Ratify an exact manifest release with the owner's Ed25519 key.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--owner-private-key", required=True)
    parser.add_argument("--effective-date", required=True)
    parser.add_argument("--output-manifest", required=True)
    parser.add_argument("--output-record", required=True)
    args = parser.parse_args()

    source = load(args.manifest)
    private_key = json.loads(Path(args.owner_private_key).read_text(encoding="utf-8"))
    ratified = prepare_ratified_manifest(source, args.effective_date)

    output_manifest = Path(args.output_manifest).resolve()
    output_record = Path(args.output_record).resolve()
    output_manifest.parent.mkdir(parents=True, exist_ok=True)
    output_record.parent.mkdir(parents=True, exist_ok=True)

    manifest_temp: Path | None = None
    record_temp: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_manifest.parent,
            prefix=f".{output_manifest.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            yaml.safe_dump(ratified, handle, sort_keys=False, allow_unicode=True)
            handle.flush()
            os.fsync(handle.fileno())
            manifest_temp = Path(handle.name)

        record = create_ratification_record(manifest_temp, ratified, private_key, args.effective_date)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=output_record.parent,
            prefix=f".{output_record.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(record, handle, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            record_temp = Path(handle.name)

        os.replace(manifest_temp, output_manifest)
        manifest_temp = None
        os.replace(record_temp, output_record)
        record_temp = None
    finally:
        for temporary in (manifest_temp, record_temp):
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    print(f"Ratified manifest: {output_manifest}")
    print(f"Ratification record: {output_record}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
