"""Offline command line interface for the repository intelligence index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from knowledge.repository import RepositoryIndex, build_repository_index


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build or inspect the local Project-AI repository index"
    )
    parser.add_argument("command", choices=("build", "status"))
    parser.add_argument("--root", type=Path, required=True, help="repository root to read")
    parser.add_argument("--output", type=Path, required=True, help="index artifact directory")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.expanduser().resolve()
    output = args.output.expanduser().resolve()
    if args.command == "build":
        status = build_repository_index(root, output)
    else:
        status = RepositoryIndex.status_for(output, root=root)
    print(json.dumps(status.as_dict(), sort_keys=True, indent=2))
    return 0 if status.state in {"ready", "empty"} and not status.stale else 2


if __name__ == "__main__":
    raise SystemExit(main())
