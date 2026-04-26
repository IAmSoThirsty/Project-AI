"""
Fix datetime.UTC compatibility bug across all Python files.
Converts Python 3.11+ datetime.UTC to Python 3.10 compatible timezone.utc
"""

import re
from pathlib import Path

def fix_file(filepath):
    """Fix datetime.UTC imports and usage in a single file."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        original = content
        
        # Fix import statement
        content = re.sub(
            r'from datetime import ([^,\n]*,\s*)?UTC(,\s*[^\n]*)?',
            lambda m: f'from datetime import {m.group(1) or ""}timezone{m.group(2) or ""}',
            content
        )
        
        # Fix UTC usage: datetime.now(timezone.utc) -> datetime.now(timezone.utc)
        content = re.sub(r'\bdatetime\.now\(UTC\)', 'datetime.now(timezone.utc)', content)
        
        # Fix direct UTC references in other contexts
        content = re.sub(r'\.replace\(tzinfo=UTC\)', '.replace(tzinfo=timezone.utc)', content)
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Fix all Python files in repository (except archives and external)."""
    root = Path(__file__).parent
    
    fixed = 0
    skip_dirs = {'.git', '.venv', '.venv-linux', '.venv.bak', '.venv_prod', 
                 'node_modules', '.pytest_cache', 'htmlcov', '__pycache__', 
                 '.ruff_cache', 'archive', 'external'}
    
    for py_file in root.rglob("*.py"):
        # Skip if in excluded directory
        if any(skip_dir in py_file.parts for skip_dir in skip_dirs):
            continue
        if fix_file(py_file):
            print(f"Fixed: {py_file.relative_to(root)}")
            fixed += 1
    
    print(f"\n[OK] Fixed {fixed} files total")

if __name__ == "__main__":
    main()
