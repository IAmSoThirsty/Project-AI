"""Normalize Markdown files: trim trailing whitespace and ensure final newline.

Usage: python tools/normalize_md.py
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SKIP_DIRS = {'.git', '__pycache__', 'venv', '.venv', 'node_modules', '.pytest_cache'}

count = 0
for dirpath, dirs, files in os.walk(ROOT):
    # skip unwanted dirs
    parts = set(dirpath.split(os.sep))
    if parts & SKIP_DIRS:
        continue
    for fname in files:
        if not fname.lower().endswith('.md'):
            continue
        full = os.path.join(dirpath, fname)
        try:
            with open(full, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # trim trailing whitespace
            new_lines = [l.rstrip() + '\n' for l in lines]
            # ensure file ends with single newline
            if new_lines and not new_lines[-1].endswith('\n'):
                new_lines[-1] = new_lines[-1] + '\n'
            # remove potential extra blank lines at end, keep single newline
            while len(new_lines) >= 2 and new_lines[-1].strip() == '' and new_lines[-2].strip() == '':
                new_lines.pop()
            # write back if changed
            if new_lines != lines:
                with open(full, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                count += 1
        except Exception as e:
            print('Failed to normalize', full, e)

print(f'Normalized {count} Markdown files')
