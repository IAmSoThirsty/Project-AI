#!/usr/bin/env python3
"""Final validation of all enriched engine documentation."""

import yaml
from pathlib import Path
from typing import Dict, List, Tuple


def validate_yaml_frontmatter(filepath: Path) -> Tuple[bool, str]:
    """Validate YAML frontmatter in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if not content.startswith('---'):
            return False, "No frontmatter found"
        
        # Extract frontmatter
        parts = content.split('---', 2)
        if len(parts) < 3:
            return False, "Invalid frontmatter structure"
        
        frontmatter = parts[1]
        
        # Parse YAML
        try:
            metadata = yaml.safe_load(frontmatter)
        except yaml.YAMLError as e:
            return False, f"YAML parsing error: {e}"
        
        # Validate required fields
        required_fields = [
            'type', 'tags', 'created', 'last_verified', 'status',
            'related_systems', 'stakeholders', 'engine_type',
            'implementation_status', 'language', 'review_cycle'
        ]
        
        missing = [f for f in required_fields if f not in metadata]
        if missing:
            return False, f"Missing required fields: {', '.join(missing)}"
        
        # Validate field types
        if not isinstance(metadata['tags'], list):
            return False, "tags must be a list"
        
        if not isinstance(metadata['related_systems'], list):
            return False, "related_systems must be a list"
        
        if not isinstance(metadata['stakeholders'], list):
            return False, "stakeholders must be a list"
        
        # Validate enum values
        valid_types = ['engine-architecture', 'kernel-doc', 'runtime-spec', 'implementation-guide']
        if metadata['type'] not in valid_types:
            return False, f"Invalid type: {metadata['type']}"
        
        valid_statuses = ['complete', 'in-progress', 'planned']
        if metadata['implementation_status'] not in valid_statuses:
            return False, f"Invalid implementation_status: {metadata['implementation_status']}"
        
        return True, "Valid"
        
    except Exception as e:
        return False, f"Validation error: {e}"


def main():
    """Validate all enriched files."""
    root = Path('.')
    target_dirs = ['engines', 'kernel', 'tarl', 'tarl_os']
    
    all_files = []
    for dir_name in target_dirs:
        dir_path = root / dir_name
        if dir_path.exists():
            all_files.extend(dir_path.rglob('*.md'))
    
    print("=" * 70)
    print("AGENT-018: Final Metadata Validation")
    print("=" * 70)
    print(f"\nValidating {len(all_files)} files...\n")
    
    valid = 0
    invalid = 0
    errors = []
    
    for filepath in sorted(all_files):
        is_valid, message = validate_yaml_frontmatter(filepath)
        
        if is_valid:
            valid += 1
            print(f"[OK] {filepath.relative_to(root)}")
        else:
            invalid += 1
            errors.append((filepath, message))
            print(f"[ERROR] {filepath.relative_to(root)}: {message}")
    
    print("\n" + "=" * 70)
    print(f"Validation Complete: {valid}/{len(all_files)} valid")
    print("=" * 70)
    
    if errors:
        print("\nErrors:")
        for filepath, message in errors:
            print(f"  - {filepath}: {message}")
        return 1
    else:
        print("\n[SUCCESS] All files pass validation!")
        return 0


if __name__ == '__main__':
    exit(main())
