
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import analyze, parse_shadow, promote, replay_hash, visualize


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="shadowthirst")
    sub = parser.add_subparsers(dest="cmd", required=True)

    check_p = sub.add_parser("check")
    check_p.add_argument("file")

    replay_p = sub.add_parser("replay")
    replay_p.add_argument("file")

    promote_p = sub.add_parser("promote")
    promote_p.add_argument("file")
    promote_p.add_argument("--dry-run", action="store_true")
    promote_p.add_argument("--replay-id")

    vis_p = sub.add_parser("visualize")
    vis_p.add_argument("file")
    vis_p.add_argument("-o", "--output")

    args = parser.parse_args(argv)
    text = Path(args.file).read_text(encoding="utf-8")
    module = parse_shadow(text, args.file)
    if args.cmd == "check":
        print(json.dumps([r.__dict__ for r in analyze(module)], indent=2))
        return 0
    if args.cmd == "replay":
        print(replay_hash(module))
        return 0
    if args.cmd == "visualize":
        mermaid = visualize(module)
        if args.output:
            Path(args.output).write_text(mermaid, encoding="utf-8")
        else:
            print(mermaid)
        return 0
    print(json.dumps(promote(module, dry_run=args.dry_run, replay_id=args.replay_id), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
