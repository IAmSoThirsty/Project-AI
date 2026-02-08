#!/usr/bin/env python3
"""
God Tier Phase 2: Fix Assert Statements in Production Code
Replace assert with proper error handling (raise ValueError, TypeError, etc.)
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple


def fix_assert_statements(content: str, filepath: Path) -> Tuple[str, int]:
    """
    Replace assert statements with proper error handling.
    
    Patterns:
    - assert condition, "message" -> if not condition: raise ValueError("message")
    - assert condition -> if not condition: raise AssertionError()
    """
    changes = 0
    lines = content.split('\n')
    new_lines = []
    
    for i, line in enumerate(lines):
        # Skip if it's in a test file (double-check)
        if 'test_' in str(filepath) or '/tests/' in str(filepath) or '/test/' in str(filepath):
            new_lines.append(line)
            continue
        
        # Check for assert statements
        assert_match = re.match(r'^(\s*)assert\s+(.+?)\s*(?:,\s*["\'](.+?)["\'])?\s*$', line)
        
        if assert_match:
            indent = assert_match.group(1)
            condition = assert_match.group(2)
            message = assert_match.group(3)
            
            # Determine appropriate exception type
            if message:
                # Use ValueError for validation errors
                if 'invalid' in message.lower() or 'must' in message.lower() or 'cannot' in message.lower():
                    exception_type = 'ValueError'
                elif 'type' in message.lower() or 'expected' in message.lower():
                    exception_type = 'TypeError'
                else:
                    exception_type = 'AssertionError'
                
                new_line = f'{indent}if not ({condition}):\n{indent}    raise {exception_type}("{message}")'
            else:
                # No message, use AssertionError
                new_line = f'{indent}if not ({condition}):\n{indent}    raise AssertionError("Assertion failed: {condition}")'
            
            new_lines.append(new_line)
            changes += 1
        else:
            new_lines.append(line)
    
    return '\n'.join(new_lines), changes


def process_file(filepath: Path, dry_run: bool = False) -> int:
    """Process a single file."""
    # Skip test files
    if 'test_' in filepath.name or '/tests/' in str(filepath) or '/test/' in str(filepath):
        return 0
    
    try:
        content = filepath.read_text(encoding='utf-8')
        
        # Quick check if file has assert statements
        if 'assert ' not in content:
            return 0
        
        new_content, changes = fix_assert_statements(content, filepath)
        
        if changes == 0:
            return 0
        
        if dry_run:
            print(f"Would fix {changes} assert statements in {filepath}")
            return changes
        
        filepath.write_text(new_content, encoding='utf-8')
        print(f"✅ Fixed {changes} assert statements in {filepath}")
        return changes
        
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}", file=sys.stderr)
        return 0


def find_python_files(root_path: Path, excludes: set) -> List[Path]:
    """Find all Python files."""
    files = []
    for filepath in root_path.rglob('*.py'):
        # Exclude test directories
        if any(excluded in filepath.parts for excluded in excludes):
            continue
        # Skip test files
        if 'test_' in filepath.name:
            continue
        files.append(filepath)
    return files


def main():
    parser = argparse.ArgumentParser(description='Fix assert statements in production code')
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--path', type=Path, default=Path('.'))
    
    args = parser.parse_args()
    
    excludes = {
        '.venv', 'venv', '.git', '__pycache__', '.pytest_cache',
        'node_modules', '.mypy_cache', '.tox', 'build', 'dist', '.eggs',
        'tests', 'test'  # Exclude test directories
    }
    
    print(f"🔍 Scanning for assert statements in production code...")
    files = find_python_files(args.path, excludes)
    print(f"📁 Found {len(files)} non-test Python files")
    
    total_changes = 0
    files_changed = 0
    
    for filepath in files:
        changes = process_file(filepath, dry_run=args.dry_run)
        if changes > 0:
            total_changes += changes
            files_changed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 ASSERT FIXES COMPLETE")
    print(f"{'='*60}")
    print(f"Files modified: {files_changed}")
    print(f"Assert statements fixed: {total_changes}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
