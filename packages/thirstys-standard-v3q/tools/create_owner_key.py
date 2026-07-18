#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from thirstys_standard_runtime.authority import generate_keypair, write_private_key  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create an owner Ed25519 keypair. Keep the private file secret."
    )
    parser.add_argument("--private-out", required=True)
    parser.add_argument("--public-out", required=True)
    parser.add_argument("--key-id", default="owner-primary")
    args = parser.parse_args()
    private_doc, public_doc = generate_keypair(
        args.key_id,
        "Jeremy / Thirsty",
        ["authority", "approval", "ratification", "execution_record"],
    )
    write_private_key(args.private_out, private_doc)
    Path(args.public_out).write_text(json.dumps(public_doc, indent=2) + "\n", encoding="utf-8")
    print(f"Created private key: {args.private_out}")
    print(f"Created public key: {args.public_out}")
    print("Do not commit, upload, email, or place the private key inside this package.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
