#!/usr/bin/env python3
"""
Surgical Logging Performance Fix - God Tier Edition

Uses regex-based approach to surgically fix logging calls while preserving
all formatting, comments, and code structure. Maximum precision!

This fixes the MEDIUM priority performance issue:
"Use lazy % formatting in logging functions" (1700+ instances)
"""

import argparse
import re
import sys
from pathlib import Path


def convert_fstring_logging(content: str) -> tuple[str, int]:
    """
    Convert f-string logging to lazy % formatting.
    Preserves all formatting, indentation, and structure.

    Returns:
        Tuple of (modified_content, num_changes)
    """
    changes = 0

    # Pattern to match logger.method(f"...") or logging.method(f"...")
    # Handles: logger.info("..."), logger.error("..."), etc.
    pattern = r'(logger\.|logging\.)(debug|info|warning|error|critical|log)\s*\(\s*f"([^"]*?)"\s*\)'

    def replacer(match):
        nonlocal changes
        prefix = match.group(1)  # logger. or logging.
        method = match.group(2)  # debug, info, error, etc.
        fstring_content = match.group(3)  # Content of f-string

        # Convert f-string to % format
        # Replace {var} with %s and collect variables
        vars_list = []

        def var_replacer(var_match):
            var_expr = var_match.group(1)
            vars_list.append(var_expr)
            return "%s"

        # Match {expression} patterns in f-string
        format_str = re.sub(r"\{([^}:]+?)(?::[^}]*)?\}", var_replacer, fstring_content)

        # Escape any % characters that were in the original string
        format_str = format_str.replace("%", "%%")
        # Restore our %s placeholders
        for _i in range(len(vars_list)):
            format_str = format_str.replace("%%s", "%s", 1)

        # Build the new logging call
        if vars_list:
            vars_str = ", ".join(vars_list)
            result = f'{prefix}{method}("{format_str}", {vars_str})'
        else:
            result = f'{prefix}{method}("{format_str}")'

        changes += 1
        return result

    # Apply the transformation
    new_content = re.sub(pattern, replacer, content)

    # Handle multi-line f-strings with triple quotes (less common but should handle)
    pattern_multiline = r'(logger\.|logging\.)(debug|info|warning|error|critical|log)\s*\(\s*f"""([^"]*?)"""\s*\)'

    def replacer_multiline(match):
        nonlocal changes
        prefix = match.group(1)
        method = match.group(2)
        fstring_content = match.group(3)

        vars_list = []

        def var_replacer(var_match):
            var_expr = var_match.group(1)
            vars_list.append(var_expr)
            return "%s"

        format_str = re.sub(r"\{([^}:]+?)(?::[^}]*)?\}", var_replacer, fstring_content)
        format_str = format_str.replace("%", "%%")
        for _i in range(len(vars_list)):
            format_str = format_str.replace("%%s", "%s", 1)

        if vars_list:
            vars_str = ", ".join(vars_list)
            result = f'{prefix}{method}("""{format_str}""", {vars_str})'
        else:
            result = f'{prefix}{method}("""{format_str}""")'

        changes += 1
        return result

    new_content = re.sub(pattern_multiline, replacer_multiline, new_content)

    # Handle self.logger patterns
    pattern_self = r'(self\.logger\.)(debug|info|warning|error|critical|log)\s*\(\s*f"([^"]*?)"\s*\)'

    def replacer_self(match):
        nonlocal changes
        prefix = match.group(1)
        method = match.group(2)
        fstring_content = match.group(3)

        vars_list = []

        def var_replacer(var_match):
            var_expr = var_match.group(1)
            vars_list.append(var_expr)
            return "%s"

        format_str = re.sub(r"\{([^}:]+?)(?::[^}]*)?\}", var_replacer, fstring_content)
        format_str = format_str.replace("%", "%%")
        for _i in range(len(vars_list)):
            format_str = format_str.replace("%%s", "%s", 1)

        if vars_list:
            vars_str = ", ".join(vars_list)
            result = f'{prefix}{method}("{format_str}", {vars_str})'
        else:
            result = f'{prefix}{method}("{format_str}")'

        changes += 1
        return result

    new_content = re.sub(pattern_self, replacer_self, new_content)

    return new_content, changes


def process_file(filepath: Path, dry_run: bool = False) -> int:
    """Process a single file."""
    try:
        content = filepath.read_text(encoding="utf-8")
        new_content, changes = convert_fstring_logging(content)

        if changes == 0:
            return 0

        if dry_run:
            print(f"Would fix {changes} logging calls in {filepath}")
            return changes

        # Write back
        filepath.write_text(new_content, encoding="utf-8")
        print(f"✅ Fixed {changes} logging calls in {filepath}")
        return changes

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}", file=sys.stderr)
        return 0


def find_python_files(root_path: Path, excludes: set) -> list[Path]:
    """Find all Python files, excluding specified directories."""
    files = []
    for filepath in root_path.rglob("*.py"):
        if not any(excluded in filepath.parts for excluded in excludes):
            files.append(filepath)
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Surgically fix logging performance issues (f-string to lazy %)"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show changes without modifying"
    )
    parser.add_argument(
        "--path", type=Path, default=Path("."), help="Root path to scan"
    )

    args = parser.parse_args()

    excludes = {
        ".venv",
        "venv",
        ".git",
        "__pycache__",
        ".pytest_cache",
        "node_modules",
        ".mypy_cache",
        ".tox",
        "build",
        "dist",
        ".eggs",
    }

    print(f"🔍 Scanning for Python files in {args.path.absolute()}...")
    files = find_python_files(args.path, excludes)
    print(f"📁 Found {len(files)} Python files")

    if args.dry_run:
        print("🔬 DRY RUN MODE\n")

    total_changes = 0
    files_changed = 0

    for filepath in files:
        changes = process_file(filepath, dry_run=args.dry_run)
        if changes > 0:
            total_changes += changes
            files_changed += 1

    print(f"\n{'='*60}")
    print("📊 GOD TIER SUMMARY")
    print(f"{'='*60}")
    print(f"Files scanned: {len(files)}")
    print(f"Files modified: {files_changed}")
    print(f"Total logging calls fixed: {total_changes}")
    print(f"{'='*60}")

    if args.dry_run:
        print("\n🚀 Run without --dry-run to execute changes")
    else:
        print("\n🔥 GOD TIER EXECUTION COMPLETE!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
