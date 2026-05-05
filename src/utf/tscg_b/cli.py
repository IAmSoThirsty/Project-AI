from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import pack_text, unpack_frame


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tscgb")
    sub = parser.add_subparsers(dest="cmd", required=True)

    pack_p = sub.add_parser("pack")
    pack_p.add_argument("text")
    pack_p.add_argument("-o", "--output")

    unpack_p = sub.add_parser("unpack")
    unpack_p.add_argument("file")

    args = parser.parse_args(argv)
    if args.cmd == "pack":
        frame = pack_text(args.text)
        if args.output:
            Path(args.output).write_bytes(frame)
        else:
            print(frame.hex())
        return 0
    info = unpack_frame(Path(args.file).read_bytes())
    print(json.dumps(info, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
