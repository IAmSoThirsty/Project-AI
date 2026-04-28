#!/usr/bin/env python3
"""Remove YAML frontmatter from markdown files."""

import re
from pathlib import Path


def remove_frontmatter(filepath: Path) -> bool:
    """Remove YAML frontmatter from a file if present."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file starts with frontmatter
        if content.startswith('---'):
            # Remove frontmatter using regex
            # Pattern: Match from start --- to second --- (plus newlines)
            pattern = r'^---\n.*?\n---\n\n'
            cleaned = re.sub(pattern, '', content, count=1, flags=re.DOTALL)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(cleaned)
            
            print(f"✅ Cleaned: {filepath}")
            return True
        else:
            print(f"⏭️  No frontmatter: {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error cleaning {filepath}: {e}")
        return False


def main():
    """Clean all markdown files in target directories."""
    root = Path('.')
    target_dirs = ['engines', 'kernel', 'tarl', 'tarl_os']
    
    all_files = []
    for dir_name in target_dirs:
        dir_path = root / dir_name
        if dir_path.exists():
            all_files.extend(dir_path.rglob('*.md'))
    
    print(f"Found {len(all_files)} markdown files\n")
    
    cleaned = 0
    for filepath in sorted(all_files):
        if remove_frontmatter(filepath):
            cleaned += 1
    
    print(f"\n✅ Cleaned {cleaned}/{len(all_files)} files")


if __name__ == '__main__':
    main()
