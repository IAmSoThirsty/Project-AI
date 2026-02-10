#!/usr/bin/env python3
"""
God Tier Phase 2: Complete Logging Fix
Catches ALL remaining f-string logging patterns including error handlers, multi-line, etc.
"""

import argparse
import re
import sys
from pathlib import Path


def convert_all_fstring_logging(content: str) -> tuple[str, int]:
    """
    Convert ALL f-string logging patterns to lazy % formatting.
    Handles error logging, multi-line, custom loggers, etc.
    """
    changes = 0

    # Pattern 1: Standard single-line logger.method(f"...")
    pattern1 = r'((?:logger|logging|self\.logger)\.(debug|info|warning|error|critical|log))\s*\(\s*f"([^"]*?)"\s*\)'

    def replacer1(match):
        nonlocal changes
        method_call = match.group(1)
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
            result = f'{method_call}("{format_str}", {vars_str})'
        else:
            result = f'{method_call}("{format_str}")'

        changes += 1
        return result

    new_content = re.sub(pattern1, replacer1, content)

    # Pattern 2: Error logging with exc_info (multi-line)
    # logger.error("...", exc_info=True)
    pattern2 = r'((?:logger|logging|self\.logger)\.(debug|info|warning|error|critical|log))\s*\(\s*f"([^"]*?)"\s*,\s*(exc_info\s*=\s*True)\s*\)'

    def replacer2(match):
        nonlocal changes
        method_call = match.group(1)
        fstring_content = match.group(3)
        exc_info = match.group(4)

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
            result = f'{method_call}("{format_str}", {vars_str}, {exc_info})'
        else:
            result = f'{method_call}("{format_str}", {exc_info})'

        changes += 1
        return result

    new_content = re.sub(pattern2, replacer2, new_content)

    # Pattern 3: Custom logger methods (log_operation, etc.)
    pattern3 = r'(self\.logger\.\w+)\s*\(\s*f"([^"]*?)"\s*\)'

    def replacer3(match):
        nonlocal changes
        method_call = match.group(1)
        fstring_content = match.group(2)

        # Only process if it has variables
        if "{" not in fstring_content:
            return match.group(0)

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
            result = f'{method_call}("{format_str}", {vars_str})'
        else:
            result = f'{method_call}("{format_str}")'

        changes += 1
        return result

    new_content = re.sub(pattern3, replacer3, new_content)

    return new_content, changes


def process_file(filepath: Path, dry_run: bool = False) -> int:
    """Process a single file."""
    try:
        content = filepath.read_text(encoding="utf-8")
        new_content, changes = convert_all_fstring_logging(content)

        if changes == 0:
            return 0

        if dry_run:
            print(f"Would fix {changes} logging calls in {filepath}")
            return changes

        filepath.write_text(new_content, encoding="utf-8")
        print(f"✅ Fixed {changes} logging calls in {filepath}")
        return changes

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}", file=sys.stderr)
        return 0


def find_python_files(root_path: Path, excludes: set) -> list[Path]:
    """Find all Python files."""
    files = []
    for filepath in root_path.rglob("*.py"):
        if not any(excluded in filepath.parts for excluded in excludes):
            files.append(filepath)
    return files


def main():
    parser = argparse.ArgumentParser(description="Complete logging fix - Phase 2")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--path", type=Path, default=Path("."))

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

    print("🔍 Phase 2: Scanning for remaining f-string logging...")
    files = find_python_files(args.path, excludes)

    total_changes = 0
    files_changed = 0

    for filepath in files:
        changes = process_file(filepath, dry_run=args.dry_run)
        if changes > 0:
            total_changes += changes
            files_changed += 1

    print(f"\n{'='*60}")
    print("📊 PHASE 2 COMPLETE")
    print(f"{'='*60}")
    print(f"Files modified: {files_changed}")
    print(f"Logging calls fixed: {total_changes}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
