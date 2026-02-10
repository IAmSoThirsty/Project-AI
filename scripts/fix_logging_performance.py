#!/usr/bin/env python3
"""
Automated Logging Refactoring Tool

Converts f-string logging to lazy % formatting for performance.
Handles 1700+ instances across the codebase systematically.

Usage:
    python scripts/fix_logging_performance.py [--dry-run] [--path PATH]
"""

import argparse
import ast
import sys
from pathlib import Path


class LoggingRefactorer(ast.NodeTransformer):
    """AST-based transformer to convert f-string logging to lazy % format."""

    def __init__(self):
        self.changes = []
        self.current_file = None

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """Visit function calls and transform logging calls with f-strings."""
        self.generic_visit(node)

        # Check if this is a logging call
        if not self._is_logging_call(node):
            return node

        # Check if the first argument is an f-string
        if not node.args or not isinstance(node.args[0], ast.JoinedStr):
            return node

        # Convert f-string to format string with args
        format_str, format_args = self._convert_fstring_to_format(node.args[0])

        if format_str is None:
            return node  # Couldn't convert, leave unchanged

        # Create new arguments: format string + format args
        new_args = [ast.Constant(value=format_str)] + format_args + node.args[1:]

        # Create new call node
        new_node = ast.Call(func=node.func, args=new_args, keywords=node.keywords)

        # Copy location info
        ast.copy_location(new_node, node)

        self.changes.append(
            {"file": self.current_file, "line": node.lineno, "col": node.col_offset}
        )

        return new_node

    def _is_logging_call(self, node: ast.Call) -> bool:
        """Check if this is a logging method call."""
        if isinstance(node.func, ast.Attribute):
            # logger.info(), logger.error(), etc.
            if node.func.attr in (
                "debug",
                "info",
                "warning",
                "error",
                "critical",
                "log",
            ):
                return True
        elif isinstance(node.func, ast.Name):
            # logging.info(), logging.error(), etc.
            if node.func.id in ("debug", "info", "warning", "error", "critical", "log"):
                return True
        return False

    def _convert_fstring_to_format(
        self, fstring: ast.JoinedStr
    ) -> tuple[str, list[ast.expr]]:
        """Convert f-string to % format string and argument list."""
        format_parts = []
        format_args = []

        for value in fstring.values:
            if isinstance(value, ast.Constant):
                # Plain string part
                # Escape % characters
                format_parts.append(str(value.value).replace("%", "%%"))
            elif isinstance(value, ast.FormattedValue):
                # Expression part - use %s for simplicity
                format_parts.append("%s")

                # Handle format specs if present
                if value.format_spec:
                    # Complex format spec - bail out
                    return None, []

                format_args.append(value.value)
            else:
                # Unknown node type
                return None, []

        format_str = "".join(format_parts)
        return format_str, format_args


def refactor_file(filepath: Path, dry_run: bool = False) -> int:
    """
    Refactor logging calls in a single file.

    Returns:
        Number of changes made
    """
    try:
        content = filepath.read_text(encoding="utf-8")

        # Parse the file
        try:
            tree = ast.parse(content, filename=str(filepath))
        except SyntaxError as e:
            print(f"⚠️  Syntax error in {filepath}: {e}", file=sys.stderr)
            return 0

        # Transform the AST
        refactorer = LoggingRefactorer()
        refactorer.current_file = str(filepath)
        new_tree = refactorer.visit(tree)

        if not refactorer.changes:
            return 0

        if dry_run:
            print(f"Would fix {len(refactorer.changes)} logging calls in {filepath}")
            return len(refactorer.changes)

        # Generate new source code
        try:
            new_content = ast.unparse(new_tree)
        except Exception as e:
            print(f"⚠️  Failed to generate code for {filepath}: {e}", file=sys.stderr)
            return 0

        # Write back
        filepath.write_text(new_content, encoding="utf-8")
        print(f"✅ Fixed {len(refactorer.changes)} logging calls in {filepath}")

        return len(refactorer.changes)

    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}", file=sys.stderr)
        return 0


def find_python_files(root_path: Path) -> list[Path]:
    """Find all Python files in the given path."""
    return list(root_path.rglob("*.py"))


def main():
    parser = argparse.ArgumentParser(
        description="Automatically refactor logging calls from f-strings to lazy % formatting"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without modifying files",
    )
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("."),
        help="Root path to search for Python files (default: current directory)",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Directories to exclude (can be specified multiple times)",
    )

    args = parser.parse_args()

    # Default exclusions
    default_excludes = {
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
    default_excludes.update(args.exclude)

    print(f"🔍 Scanning for Python files in {args.path.absolute()}...")

    # Find all Python files
    all_files = find_python_files(args.path)

    # Filter out excluded directories
    files = [
        f
        for f in all_files
        if not any(excluded in f.parts for excluded in default_excludes)
    ]

    print(f"📁 Found {len(files)} Python files to process")

    if args.dry_run:
        print("🔬 DRY RUN MODE - No files will be modified\n")

    # Process files
    total_changes = 0
    files_changed = 0

    for filepath in files:
        changes = refactor_file(filepath, dry_run=args.dry_run)
        if changes > 0:
            total_changes += changes
            files_changed += 1

    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    print(f"Files processed: {len(files)}")
    print(f"Files changed: {files_changed}")
    print(f"Total logging calls fixed: {total_changes}")

    if args.dry_run:
        print("\nRun without --dry-run to apply changes")

    return 0 if total_changes == 0 else 0


if __name__ == "__main__":
    sys.exit(main())
