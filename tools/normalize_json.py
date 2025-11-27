"""Pretty-print JSON files in the repository for consistent formatting.

This will rewrite JSON files with 2-space indentation. Skips node_modules and venv directories.
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SKIP_DIRS = {'.git', '__pycache__', 'venv', '.venv', 'node_modules', '.pytest_cache'}

count = 0
for dirpath, dirs, files in os.walk(ROOT):
    parts = set(dirpath.split(os.sep))
    if parts & SKIP_DIRS:
        continue
    for fname in files:
        if not fname.lower().endswith('.json'):
            continue
        full = os.path.join(dirpath, fname)
        try:
            with open(full, 'r', encoding='utf-8') as f:
                data = json.load(f)
            with open(full, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write('\n')
            count += 1
        except Exception:
            # skip non-JSON or files that are not suitable
            continue

print(f'Formatted {count} JSON files')
