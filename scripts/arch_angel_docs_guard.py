#!/usr/bin/env python3
"""CLI for the Arch Angel governance document guardian."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _bootstrap_imports(project_root: Path) -> None:
    src_path = project_root / "src"
    for path in (project_root, src_path):
        path_text = str(path)
        if path_text not in sys.path:
            sys.path.insert(0, path_text)


def _print_report(report) -> None:
    print(f"Arch Angel status: {report.status}")
    print(f"Publications: {report.total_publications}")
    print(f"Diagnostics: {len(report.diagnostics)}")
    changed = [repair for repair in report.repairs if repair.changed]
    print(f"Changed repairs: {len(changed)}")
    for diagnostic in report.diagnostics[:20]:
        where = f" [{diagnostic.path}]" if diagnostic.path else ""
        doi = f" ({diagnostic.doi})" if diagnostic.doi else ""
        print(f"- {diagnostic.severity}: {diagnostic.code}{where}: {diagnostic.message}{doi}")
    if len(report.diagnostics) > 20:
        print(f"...and {len(report.diagnostics) - 20} more diagnostics")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="arch_angel_docs_guard",
        description="Passive DOI/path guardian for Project-AI governance docs.",
    )
    parser.add_argument(
        "--root",
        dest="global_root",
        default=".",
        help="Project root. Defaults to the current working directory.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_root_option(command_parser: argparse.ArgumentParser) -> None:
        command_parser.add_argument(
            "--root",
            default=None,
            help="Project root. May be provided before or after the subcommand.",
        )

    check_parser = subparsers.add_parser("check", help="Validate protected governance docs.")
    add_root_option(check_parser)

    repair_parser = subparsers.add_parser("repair", help="Repair safe governance doc drift.")
    add_root_option(repair_parser)
    repair_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Plan repairs without writing protected documents.",
    )

    watch_parser = subparsers.add_parser("watch", help="Continuously watch protected docs.")
    add_root_option(watch_parser)
    watch_parser.add_argument(
        "--repair",
        action="store_true",
        help="Run safe repair on protected document changes.",
    )
    watch_parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Debounce interval in seconds.",
    )

    report_parser = subparsers.add_parser("report", help="Print the latest persisted report JSON.")
    add_root_option(report_parser)

    args = parser.parse_args(argv)
    root = Path(args.root or args.global_root).resolve()
    _bootstrap_imports(root)

    from app.agents.arch_angel import ArchAngel

    angel = ArchAngel(root)
    if args.command == "check":
        report = angel.check()
        _print_report(report)
        return 1 if report.has_issues else 0
    if args.command == "repair":
        report = angel.repair(dry_run=args.dry_run)
        _print_report(report)
        return 1 if report.has_critical else 0
    if args.command == "watch":
        print("Arch Angel watching protected governance docs. Press Ctrl+C to stop.")
        angel.watch(repair=args.repair, interval=args.interval)
        return 0
    if args.command == "report":
        latest = angel.latest_report()
        if latest is None:
            print("No Arch Angel report has been written yet.")
            return 1
        print(json.dumps(latest, indent=2))
        return 0
    parser.error(f"Unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
