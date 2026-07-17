#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thirstys_standard_runtime.ratification import verify_ratification_record  # noqa: E402
from thirstys_standard_runtime.strict_yaml import load  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify an owner ratification record.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--record", required=True)
    parser.add_argument("--registry", required=True)
    args = parser.parse_args()
    manifest = load(args.manifest)
    record = json.loads(Path(args.record).read_text(encoding="utf-8"))
    registry = json.loads(Path(args.registry).read_text(encoding="utf-8"))
    verify_ratification_record(args.manifest, manifest, record, registry)
    print("VERIFIED: owner ratification signature, identity, effective date, version, and manifest hash")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
