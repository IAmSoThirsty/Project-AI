from __future__ import annotations

import argparse
from datetime import datetime, timedelta
from pathlib import Path


def prune(dir_path: Path, days: int, dry_run: bool = True):
    cutoff = datetime.now() - timedelta(days=days)
    removed = []
    for p in dir_path.glob("fourlaws-*.jsonl"):
        try:
            mtime = datetime.fromtimestamp(p.stat().st_mtime)
            if mtime < cutoff:
                removed.append(p)
                if not dry_run:
                    p.unlink()
        except Exception:
            continue
    return removed


def main():
    parser = argparse.ArgumentParser(description="Prune old test-artifacts files")
    parser.add_argument("--dir", default="test-artifacts", help="Artifacts directory")
    parser.add_argument("--days", type=int, default=30, help="Prune files older than DAYS")
    parser.add_argument("--delete", action="store_true", help="Actually delete files (default: dry-run)")
    args = parser.parse_args()

    d = Path(args.dir)
    if not d.exists():
        print(f"Artifacts dir not found: {d}")
        return 1

    removed = prune(d, args.days, dry_run=not args.delete)
    print(f"Found {len(removed)} files older than {args.days} days")
    for f in removed:
        print(f" - {f}")
    if args.delete:
        print("Deleted listed files")
    else:
        print("Dry-run: no files deleted. Rerun with --delete to remove them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
