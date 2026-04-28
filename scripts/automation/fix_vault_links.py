#!/usr/bin/env python3
"""
Fix wiki links after moving AGENT/REPORT files to docs/reports/
"""
import os
import re
from pathlib import Path

# Get all moved files in docs/reports/
reports_dir = Path(r"T:\Project-AI-main\docs\reports")
moved_files = {f.stem for f in reports_dir.glob("*.md")}

print(f"Found {len(moved_files)} moved files in docs/reports/")

# Vault paths to scan
vault_paths = [
    Path(r"T:\Project-AI-main\docs"),
    Path(r"T:\Project-AI-main\indexes"),
    Path(r"T:\Project-AI-main\relationships")
]

# Track changes
files_modified = 0
links_fixed = 0

for vault_path in vault_paths:
    for md_file in vault_path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
            original_content = content
            
            # Fix wiki links: [[AGENT_XXX]] or [[AGENT-XXX]] or [[XXX_REPORT]]
            def fix_link(match):
                global links_fixed
                link_text = match.group(1)
                # Remove any path prefix
                filename = link_text.split('/')[-1]
                
                # Check if this file was moved
                if filename in moved_files:
                    # Calculate relative path from current file to docs/reports/
                    # For simplicity, use absolute path from docs root
                    relative_path = f"docs/reports/{filename}"
                    links_fixed += 1
                    return f"[[{relative_path}]]"
                return match.group(0)  # No change
            
            # Pattern: [[anything]]
            content = re.sub(r'\[\[([^\]]+)\]\]', fix_link, content)
            
            if content != original_content:
                md_file.write_text(content, encoding='utf-8')
                files_modified += 1
                if files_modified <= 10:
                    print(f"✓ Fixed links in: {md_file.relative_to(Path(r'T:\Project-AI-main'))}")
        
        except Exception as e:
            print(f"✗ Error processing {md_file}: {e}")

print(f"\n✓ COMPLETE:")
print(f"  - Modified {files_modified} files")
print(f"  - Fixed {links_fixed} wiki links")
