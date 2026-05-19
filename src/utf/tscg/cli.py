from __future__ import annotations

import argparse
import json

from .core import canonical, checksum, parse, validate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tscg")
    sub = parser.add_subparsers(dest="cmd", required=True)

    enc = sub.add_parser("encode")
    enc.add_argument("text")

    dec = sub.add_parser("decode")
    dec.add_argument("text")

    args = parser.parse_args(argv)
    expr = parse(args.text)
    validate(expr)
    if args.cmd == "encode":
        print(json.dumps({"canonical": canonical(expr), "checksum": checksum(expr)}, indent=2))
        return 0
    print(canonical(expr))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
