"""Command line interface for PA-SHIELD."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path

from app.testing.pa_shield.harness import EvaluationHarness


def _default_output_dir() -> Path:
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    return Path("ci-reports") / "pa-shield" / timestamp


def build_parser() -> argparse.ArgumentParser:
    """Build the PA-SHIELD CLI parser."""
    parser = argparse.ArgumentParser(prog="pa-shield", description="PA-SHIELD benchmark CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run one system against a suite")
    run_parser.add_argument("--system", required=True, choices=["baseline", "project_ai"])
    run_parser.add_argument("--suite", default="full")
    run_parser.add_argument("--fuzz", action="store_true")
    run_parser.add_argument("--iterations", type=int, default=5)
    run_parser.add_argument("--seed", type=int, default=1337)
    run_parser.add_argument("--output-dir", type=Path, default=_default_output_dir())
    run_parser.add_argument("--include-legacy", action="store_true")

    compare_parser = subparsers.add_parser("compare", help="Compare systems on a suite")
    compare_parser.add_argument(
        "--systems",
        nargs="+",
        default=["baseline", "project_ai"],
        choices=["baseline", "project_ai"],
    )
    compare_parser.add_argument("--suite", default="full")
    compare_parser.add_argument("--fuzz", action="store_true")
    compare_parser.add_argument("--iterations", type=int, default=5)
    compare_parser.add_argument("--seed", type=int, default=1337)
    compare_parser.add_argument("--output-dir", type=Path, default=_default_output_dir())
    compare_parser.add_argument("--include-legacy", action="store_true")

    replay_parser = subparsers.add_parser("replay", help="Replay a prior audit log")
    replay_parser.add_argument("--system", required=True, choices=["baseline", "project_ai"])
    replay_parser.add_argument("--log", type=Path, required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint."""
    parser = build_parser()
    args = parser.parse_args(argv)
    harness = EvaluationHarness()

    if args.command == "run":
        report = harness.run_system(
            system_name=args.system,
            suite=args.suite,
            output_dir=args.output_dir,
            fuzz=args.fuzz,
            iterations=args.iterations if args.fuzz else 0,
            seed=args.seed,
            include_legacy=args.include_legacy,
        )
        print(json.dumps(report["results"]["metrics"], indent=2))
        print(f"Artifacts: {args.output_dir}")
        return 0

    if args.command == "compare":
        report = harness.compare_systems(
            systems=args.systems,
            suite=args.suite,
            output_dir=args.output_dir,
            fuzz=args.fuzz,
            iterations=args.iterations if args.fuzz else 0,
            seed=args.seed,
            include_legacy=args.include_legacy,
        )
        print(json.dumps(report, indent=2))
        print(f"Artifacts: {args.output_dir}")
        return 0

    if args.command == "replay":
        replay = harness.replay.replay_log(
            runner=harness.create_runner(args.system),
            log_path=args.log,
        )
        print(json.dumps(replay, indent=2))
        return 0

    parser.error("Unhandled command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
