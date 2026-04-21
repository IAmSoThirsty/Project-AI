#!/usr/bin/env python3
"""
Index File Naming Convention Validator

Validates Obsidian vault index files against naming conventions defined in
NAMING_CONVENTIONS.md. Can validate individual files or entire directory trees.

Usage:
    python validate_index_names.py                           # Validate all indexes
    python validate_index_names.py path/to/file.md           # Validate specific file
    python validate_index_names.py --fix                     # Auto-fix naming issues
    python validate_index_names.py --check-only              # Check without fixing

Exit Codes:
    0 - All files pass validation
    1 - Validation failures found
    2 - Script error (invalid arguments, file not found, etc.)
"""

import re
import sys
import os
import argparse
from pathlib import Path
from typing import Tuple, List, Dict
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of validating a single file."""
    filepath: str
    is_valid: bool
    errors: List[str]
    suggestions: List[str]


def validate_index_filename(filename: str) -> Tuple[bool, List[str]]:
    """
    Validate index filename against naming conventions.
    
    Args:
        filename: Name of the file (not full path)
    
    Returns:
        Tuple of (is_valid, list_of_error_messages)
    """
    errors = []
    
    # Special case: Allow certain standard files
    allowed_special = [
        'README.md',
        'NAVIGATION_PLAN.md',
        'NAMING_CONVENTIONS.md',
        'AGENT-002-COMPLETION-REPORT.md',
        'INDEX_TEMPLATE.md',
    ]
    
    if filename in allowed_special:
        return (True, [])
    
    # Special case: Hidden config files
    if filename.startswith('.') and filename.endswith('.json'):
        return (True, [])
    
    # Rule 1: Must end with -index.md (for index files)
    if not filename.endswith('-index.md'):
        errors.append("Must end with '-index.md' (or be a special documentation file)")
    
    # Rule 2: Must be lowercase
    if filename != filename.lower():
        errors.append("Must be lowercase only")
    
    # Rule 3: Only a-z, 0-9, hyphen, and .md
    if not re.match(r'^[a-z0-9-]+-index\.md$', filename):
        errors.append("Only lowercase letters (a-z), numbers (0-9), and hyphens allowed")
    
    # Rule 4: Must not have consecutive hyphens
    if '--' in filename:
        errors.append("No consecutive hyphens allowed")
    
    # Rule 5: Must not start or end with hyphen (before -index.md)
    name_part = filename.replace('-index.md', '')
    if name_part and (name_part.startswith('-') or name_part.endswith('-')):
        errors.append("Cannot start or end with hyphen")
    
    # Rule 6: Maximum length (50 chars before .md)
    if len(filename) > 53:  # 50 + .md = 53
        errors.append(f"Maximum 50 characters (excluding .md), current: {len(filename) - 3}")
    
    # Rule 7: Minimum length (3 chars before -index.md)
    if len(name_part) < 3:
        errors.append("Minimum 3 characters required")
    
    return (len(errors) == 0, errors)


def suggest_fixes(filename: str) -> List[str]:
    """
    Suggest possible fixes for an invalid filename.
    
    Args:
        filename: Invalid filename
    
    Returns:
        List of suggested corrected filenames
    """
    suggestions = []
    
    # Convert to lowercase
    fixed = filename.lower()
    
    # Replace underscores with hyphens
    fixed = fixed.replace('_', '-')
    
    # Replace spaces with hyphens
    fixed = fixed.replace(' ', '-')
    
    # Remove consecutive hyphens
    while '--' in fixed:
        fixed = fixed.replace('--', '-')
    
    # Ensure ends with -index.md
    if not fixed.endswith('-index.md'):
        if fixed.endswith('.md'):
            fixed = fixed.replace('.md', '-index.md')
        else:
            fixed = fixed + '-index.md'
    
    # Remove leading/trailing hyphens from name part
    name_part = fixed.replace('-index.md', '')
    name_part = name_part.strip('-')
    fixed = name_part + '-index.md'
    
    # Remove invalid characters
    fixed = re.sub(r'[^a-z0-9-]', '', fixed.replace('-index.md', '')) + '-index.md'
    
    # Truncate if too long
    if len(fixed) > 53:
        name_part = fixed.replace('-index.md', '')
        name_part = name_part[:50]
        fixed = name_part + '-index.md'
    
    if fixed != filename:
        suggestions.append(fixed)
    
    # Additional domain-specific suggestions
    if 'domain' not in fixed and 'type' not in fixed and 'priority' not in fixed and 'status' not in fixed:
        # Try to infer index type
        base = fixed.replace('-index.md', '')
        suggestions.append(f"{base}-domain-index.md")
        suggestions.append(f"{base}-type-index.md")
    
    return list(set(suggestions))  # Remove duplicates


def validate_file(filepath: Path) -> ValidationResult:
    """
    Validate a single index file.
    
    Args:
        filepath: Path to the file to validate
    
    Returns:
        ValidationResult object
    """
    filename = filepath.name
    is_valid, errors = validate_index_filename(filename)
    suggestions = suggest_fixes(filename) if not is_valid else []
    
    return ValidationResult(
        filepath=str(filepath),
        is_valid=is_valid,
        errors=errors,
        suggestions=suggestions
    )


def validate_directory(dirpath: Path, recursive: bool = True) -> List[ValidationResult]:
    """
    Validate all .md files in a directory.
    
    Args:
        dirpath: Path to directory
        recursive: Whether to search subdirectories
    
    Returns:
        List of ValidationResult objects
    """
    results = []
    
    if recursive:
        md_files = dirpath.rglob('*.md')
    else:
        md_files = dirpath.glob('*.md')
    
    for filepath in md_files:
        result = validate_file(filepath)
        results.append(result)
    
    return results


def print_results(results: List[ValidationResult], verbose: bool = True) -> int:
    """
    Print validation results to console.
    
    Args:
        results: List of validation results
        verbose: Whether to print details for passing files
    
    Returns:
        Number of failed files
    """
    failures = 0
    passes = 0
    
    for result in results:
        if result.is_valid:
            passes += 1
            if verbose:
                print(f"✅ {result.filepath} - PASS")
        else:
            failures += 1
            print(f"❌ {result.filepath} - FAIL")
            for error in result.errors:
                print(f"   - {error}")
            if result.suggestions:
                print(f"   Suggested fixes:")
                for suggestion in result.suggestions:
                    print(f"   → {suggestion}")
            print()
    
    print(f"\nSummary: {passes} passed, {failures} failed out of {len(results)} files")
    
    return failures


def fix_filename(old_path: Path, new_name: str, dry_run: bool = False) -> bool:
    """
    Rename a file to fix naming convention violations.
    
    Args:
        old_path: Current file path
        new_name: New filename
        dry_run: If True, don't actually rename, just show what would happen
    
    Returns:
        True if renamed successfully (or would be in dry_run), False otherwise
    """
    new_path = old_path.parent / new_name
    
    if new_path.exists():
        print(f"   ⚠️  Cannot rename: {new_name} already exists")
        return False
    
    if dry_run:
        print(f"   Would rename: {old_path.name} → {new_name}")
        return True
    
    try:
        old_path.rename(new_path)
        print(f"   ✅ Renamed: {old_path.name} → {new_name}")
        return True
    except Exception as e:
        print(f"   ❌ Failed to rename: {e}")
        return False


def interactive_fix(results: List[ValidationResult]) -> int:
    """
    Interactively fix naming violations.
    
    Args:
        results: List of validation results
    
    Returns:
        Number of files fixed
    """
    fixed = 0
    
    failures = [r for r in results if not r.is_valid]
    
    if not failures:
        print("No files need fixing.")
        return 0
    
    print(f"\nFound {len(failures)} files with naming violations.\n")
    
    for result in failures:
        print(f"File: {result.filepath}")
        print(f"Issues:")
        for error in result.errors:
            print(f"  - {error}")
        
        if not result.suggestions:
            print("  No automatic fix available. Please rename manually.")
            print()
            continue
        
        print("\nSuggested fixes:")
        for i, suggestion in enumerate(result.suggestions, 1):
            print(f"  {i}. {suggestion}")
        print(f"  {len(result.suggestions) + 1}. Skip")
        print(f"  {len(result.suggestions) + 2}. Quit")
        
        choice = input("\nChoose option: ").strip()
        
        try:
            choice_num = int(choice)
            if choice_num == len(result.suggestions) + 2:
                print("Quitting...")
                break
            elif choice_num == len(result.suggestions) + 1:
                print("Skipping...")
                print()
                continue
            elif 1 <= choice_num <= len(result.suggestions):
                new_name = result.suggestions[choice_num - 1]
                if fix_filename(Path(result.filepath), new_name, dry_run=False):
                    fixed += 1
            else:
                print("Invalid choice, skipping...")
        except ValueError:
            print("Invalid input, skipping...")
        
        print()
    
    return fixed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Obsidian vault index file naming conventions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Validate all indexes in current dir
  %(prog)s path/to/index.md                   # Validate specific file
  %(prog)s --fix                              # Interactively fix violations
  %(prog)s --check-only                       # Check without printing passes
  %(prog)s path/to/_indexes/ --recursive      # Validate directory recursively
        """
    )
    
    parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Path to file or directory to validate (default: current directory)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Interactively fix naming violations'
    )
    parser.add_argument(
        '--check-only',
        action='store_true',
        help='Only show failures, not passes'
    )
    parser.add_argument(
        '--recursive',
        action='store_true',
        default=True,
        help='Recursively validate subdirectories (default: True)'
    )
    parser.add_argument(
        '--no-recursive',
        dest='recursive',
        action='store_false',
        help='Do not recursively validate subdirectories'
    )
    
    args = parser.parse_args()
    
    # Resolve path
    path = Path(args.path).resolve()
    
    if not path.exists():
        print(f"Error: Path does not exist: {path}", file=sys.stderr)
        return 2
    
    # Validate
    if path.is_file():
        results = [validate_file(path)]
    elif path.is_dir():
        results = validate_directory(path, recursive=args.recursive)
    else:
        print(f"Error: Path is neither file nor directory: {path}", file=sys.stderr)
        return 2
    
    if not results:
        print("No .md files found to validate.")
        return 0
    
    # Interactive fix mode
    if args.fix:
        fixed = interactive_fix(results)
        print(f"\nFixed {fixed} files.")
        # Re-validate to show final state
        if path.is_file():
            results = [validate_file(path)]
        else:
            results = validate_directory(path, recursive=args.recursive)
    
    # Print results
    verbose = not args.check_only
    failures = print_results(results, verbose=verbose)
    
    # Exit code
    if failures > 0:
        return 1
    else:
        return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
