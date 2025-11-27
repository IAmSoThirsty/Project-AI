"""Update Markdown files to add a standardized footer with last-updated timestamp.

This script is idempotent: it checks for a hidden marker <!-- last-updated-marker -->
and only appends the footer if the marker isn't present.

Run from the repository root (where this script lives):
    python tools/update_md_footers.py --date 2025-11-24

It will walk the repository and update all `*.md` files.
"""
import argparse
import os
from datetime import datetime

FOOTER_MARKER = '<!-- last-updated-marker -->'
DEFAULT_FOOTER = "\n\n---\n\n**Repository note:** Last updated: {date} (automated)\n\n" + FOOTER_MARKER + "\n"


def update_file(path: str, date: str) -> bool:
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if FOOTER_MARKER in content:
            return False
        footer = DEFAULT_FOOTER.format(date=date)
        with open(path, 'a', encoding='utf-8') as f:
            f.write(footer)
        return True
    except Exception as e:
        print(f"Failed to update {path}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date', default=datetime.now().strftime('%Y-%m-%d'))
    parser.add_argument('--root', default=os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    args = parser.parse_args()

    updated = []
    skipped = []
    for dirpath, dirs, files in os.walk(args.root):
        # skip virtual envs, .git, node_modules
        if any(x in dirpath for x in ['.git', 'venv', 'env', 'node_modules', '__pycache__']):
            continue
        for fname in files:
            if fname.lower().endswith('.md'):
                full = os.path.join(dirpath, fname)
                if update_file(full, args.date):
                    updated.append(full)
                else:
                    skipped.append(full)

    print(f"Updated {len(updated)} files")
    for p in updated[:20]:
        print(' +', p)
    if skipped:
        print(f"Skipped {len(skipped)} files (already had footer)")

if __name__ == '__main__':
    main()
