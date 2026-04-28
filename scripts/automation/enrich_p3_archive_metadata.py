#!/usr/bin/env python3
"""
AGENT-015: P3 Archive Bulk Metadata Enrichment Script

Enhances existing archive file metadata with P3-specific fields:
- Adds p3-archive tag
- Adds last_verified: 2026-04-20
- Adds created date from git history
- Adds superseded_by (if applicable)
- Adds related_systems, stakeholders, review_cycle
- Maps type: historical_record -> type: archived
"""

import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import yaml

# Constants
ARCHIVE_DIR = Path("docs/internal/archive")
LAST_VERIFIED = "2026-04-20"
P3_TAG = "p3-archive"

# Superseded mapping (based on file name patterns)
SUPERSEDED_MAPPING = {
    "PROGRAM_SUMMARY.md": "docs/DEVELOPER_QUICK_REFERENCE.md",
    "REPO_STRUCTURE.md": "docs/ARCHITECTURE_DESIGN_PATTERNS_EVALUATION.md",
    "SECURITY_SUMMARY.md": "SECURITY.md",
    "GITHUB_UPDATE_GUIDE.md": "CONTRIBUTING.md",
}


def get_git_creation_date(filepath: Path) -> Optional[str]:
    """Get the earliest git commit date for a file."""
    try:
        result = subprocess.run(
            ["git", "log", "--format=%ai", "--reverse", "--", str(filepath)],
            capture_output=True,
            text=True,
            check=True,
            cwd=filepath.parent.parent.parent  # Project root
        )
        if result.stdout.strip():
            # Parse first line (earliest commit)
            date_str = result.stdout.strip().split('\n')[0]
            # Extract just YYYY-MM-DD
            return date_str.split()[0]
    except subprocess.CalledProcessError:
        pass
    return None


def parse_frontmatter(content: str) -> Tuple[Optional[Dict], str]:
    """Parse YAML frontmatter from markdown content."""
    match = re.match(r'^---\s*\n(.*?\n)---\s*\n(.*)$', content, re.DOTALL)
    if match:
        try:
            metadata = yaml.safe_load(match.group(1))
            body = match.group(2)
            return metadata, body
        except yaml.YAMLError as e:
            print(f"  ⚠️  YAML parsing error: {e}")
            return None, content
    return None, content


def determine_archive_type(metadata: Dict, filename: str) -> str:
    """Determine P3 archive type from existing metadata."""
    existing_type = metadata.get('type', '')
    archive_reason = metadata.get('archive_reason', '')
    
    # Map existing types to P3 taxonomy
    if archive_reason == 'superseded' or filename in SUPERSEDED_MAPPING:
        return 'superseded'
    elif archive_reason == 'deprecated':
        return 'legacy'
    elif archive_reason == 'completed':
        return 'archived'
    elif 'historical' in existing_type.lower():
        return 'historical'
    else:
        return 'archived'  # Default


def enrich_metadata(metadata: Dict, filepath: Path) -> Dict:
    """Enrich existing metadata with P3-specific fields."""
    filename = filepath.name
    
    # 1. Update type to P3 taxonomy
    metadata['type'] = determine_archive_type(metadata, filename)
    
    # 2. Add/update tags with p3-archive
    existing_tags = metadata.get('tags', [])
    if isinstance(existing_tags, str):
        existing_tags = [existing_tags]
    if P3_TAG not in existing_tags:
        existing_tags.insert(0, P3_TAG)
    metadata['tags'] = existing_tags
    
    # 3. Add created date from git
    if 'created' not in metadata:
        created_date = get_git_creation_date(filepath)
        if created_date:
            metadata['created'] = created_date
    
    # 4. Add last_verified
    metadata['last_verified'] = LAST_VERIFIED
    
    # 5. Add superseded_by if applicable
    if filename in SUPERSEDED_MAPPING and 'superseded_by' not in metadata:
        metadata['superseded_by'] = SUPERSEDED_MAPPING[filename]
        if metadata['type'] != 'superseded':
            metadata['type'] = 'superseded'
    
    # 6. Add related_systems (extract from tags/content if not present)
    if 'related_systems' not in metadata:
        # Infer from tags
        systems = []
        tags = metadata.get('tags', [])
        if 'security' in tags:
            systems.append('security-systems')
        if 'testing' in tags:
            systems.append('test-framework')
        if 'ci-cd' in tags:
            systems.append('ci-cd-pipeline')
        if 'architecture' in tags:
            systems.append('architecture')
        
        metadata['related_systems'] = systems if systems else ['historical-reference']
    
    # 7. Add stakeholders
    if 'stakeholders' not in metadata:
        metadata['stakeholders'] = metadata.get('audience', ['historical-reference'])
    
    # 8. Add review_cycle
    if 'review_cycle' not in metadata:
        metadata['review_cycle'] = 'annually'
    
    # 9. Ensure archive_reason exists
    if 'archive_reason' not in metadata:
        metadata['archive_reason'] = 'completed'
    
    return metadata


def format_frontmatter(metadata: Dict) -> str:
    """Format metadata dict as YAML frontmatter with proper field ordering."""
    # Define field order for P3 schema
    field_order = [
        'title', 'id', 'type', 'tags', 'created', 'last_verified', 
        'status', 'archived_date', 'archive_reason', 'superseded_by',
        'related_systems', 'stakeholders', 'audience', 'review_cycle',
        'historical_value', 'restore_candidate', 'path_confirmed'
    ]
    
    ordered_metadata = {}
    
    # Add fields in order (if they exist)
    for field in field_order:
        if field in metadata:
            ordered_metadata[field] = metadata[field]
    
    # Add any remaining fields not in order
    for key, value in metadata.items():
        if key not in ordered_metadata:
            ordered_metadata[key] = value
    
    # Format as YAML
    yaml_str = yaml.dump(ordered_metadata, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return f"---\n{yaml_str}---\n"


def process_file(filepath: Path, dry_run: bool = False) -> Dict:
    """Process a single archive file."""
    result = {
        'file': filepath.name,
        'status': 'unknown',
        'changes': [],
        'errors': []
    }
    
    try:
        # Read file
        content = filepath.read_text(encoding='utf-8')
        
        # Parse frontmatter
        metadata, body = parse_frontmatter(content)
        
        if metadata is None:
            result['status'] = 'no_frontmatter'
            result['errors'].append("No valid frontmatter found")
            return result
        
        # Store original for comparison
        original_metadata = metadata.copy()
        
        # Enrich metadata
        enriched_metadata = enrich_metadata(metadata, filepath)
        
        # Track changes
        for key in enriched_metadata:
            if key not in original_metadata:
                result['changes'].append(f"Added: {key}")
            elif enriched_metadata[key] != original_metadata.get(key):
                result['changes'].append(f"Updated: {key}")
        
        # Write back if not dry run
        if not dry_run and result['changes']:
            new_frontmatter = format_frontmatter(enriched_metadata)
            new_content = new_frontmatter + body
            filepath.write_text(new_content, encoding='utf-8')
            result['status'] = 'enriched'
        elif result['changes']:
            result['status'] = 'would_enrich'
        else:
            result['status'] = 'no_changes'
        
    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(str(e))
    
    return result


def main():
    """Main execution function."""
    print("=" * 80)
    print("AGENT-015: P3 Archive Bulk Metadata Enrichment")
    print("=" * 80)
    print()
    
    # Find all markdown files
    md_files = sorted(ARCHIVE_DIR.glob("*.md"))
    total_files = len(md_files)
    
    print(f"📁 Found {total_files} markdown files in {ARCHIVE_DIR}")
    print()
    
    # Process files
    results = []
    for i, filepath in enumerate(md_files, 1):
        print(f"[{i}/{total_files}] Processing: {filepath.name}...", end=" ")
        result = process_file(filepath, dry_run=False)
        results.append(result)
        
        if result['status'] == 'enriched':
            print(f"✅ ({len(result['changes'])} changes)")
        elif result['status'] == 'no_changes':
            print("⏭️  (already compliant)")
        elif result['status'] == 'error':
            print(f"❌ {result['errors'][0]}")
        else:
            print(f"⚠️  {result['status']}")
    
    # Summary
    print()
    print("=" * 80)
    print("ENRICHMENT SUMMARY")
    print("=" * 80)
    
    enriched = [r for r in results if r['status'] == 'enriched']
    no_changes = [r for r in results if r['status'] == 'no_changes']
    errors = [r for r in results if r['status'] == 'error']
    
    print(f"✅ Enriched: {len(enriched)}")
    print(f"⏭️  No changes needed: {len(no_changes)}")
    print(f"❌ Errors: {len(errors)}")
    print(f"📊 Total processed: {total_files}")
    print()
    
    if enriched:
        print("Most common changes:")
        all_changes = {}
        for r in enriched:
            for change in r['changes']:
                all_changes[change] = all_changes.get(change, 0) + 1
        
        for change, count in sorted(all_changes.items(), key=lambda x: -x[1])[:10]:
            print(f"  • {change}: {count} files")
    
    print()
    print("=" * 80)
    print("✅ BULK ENRICHMENT COMPLETE")
    print("=" * 80)
    
    return len(errors) == 0


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
