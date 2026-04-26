"""
Fix StrEnum compatibility - Python 3.11+ only
For Python 3.10, use str + Enum instead
"""

import re
from pathlib import Path


def fix_strenum_file(filepath):
    """Fix StrEnum usage to be Python 3.10 compatible."""
    try:
        content = filepath.read_text(encoding='utf-8', errors='ignore')
        original = content
        
        # Fix import: from enum import StrEnum -> from enum import Enum
        content = re.sub(
            r'from enum import ([^,\n]*,\s*)?StrEnum(,\s*[^\n]*)?',
            lambda m: f'from enum import {m.group(1) or ""}Enum{m.group(2) or ""}',
            content
        )
        
        # Fix class declaration: class X(StrEnum): -> class X(str, Enum):
        content = re.sub(
            r'class\s+(\w+)\(StrEnum\):',
            r'class \1(str, Enum):',
            content
        )
        
        if content != original:
            filepath.write_text(content, encoding='utf-8')
            return True
        return False
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False

def main():
    """Fix all StrEnum files."""
    files_to_fix = [
        "src/app/governance/acceptance_ledger.py",
        "src/app/governance/company_pricing.py",
        "src/app/governance/government_pricing.py",
        "src/app/governance/runtime_enforcer.py",
        "src/app/inspection/repository_inspector.py",
        "api/main.py",
    ]
    
    root = Path(__file__).parent
    fixed = 0
    
    for file_path in files_to_fix:
        full_path = root / file_path
        if full_path.exists() and fix_strenum_file(full_path):
            print(f"Fixed: {file_path}")
            fixed += 1
    
    print(f"\n[OK] Fixed {fixed} files")

if __name__ == "__main__":
    main()
    main()
