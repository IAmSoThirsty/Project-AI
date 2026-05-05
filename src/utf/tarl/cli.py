from __future__ import annotations

import argparse
from pathlib import Path

from .core import evaluate, load_context, parse_policy


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="tarl")
    sub = parser.add_subparsers(dest="cmd", required=True)

    check_p = sub.add_parser("check")
    check_p.add_argument("file")

    eval_p = sub.add_parser("eval")
    eval_p.add_argument("file")
    eval_p.add_argument("--input", required=True)

    args = parser.parse_args(argv)
    text = Path(args.file).read_text(encoding="utf-8")
    policy = parse_policy(text)
    if args.cmd == "check":
        print(f"ok: {policy.name} ({len(policy.rules)} rules)")
        return 0
    context = load_context(args.input)
    print(evaluate(policy, context))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
