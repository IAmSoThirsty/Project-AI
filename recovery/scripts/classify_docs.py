#!/usr/bin/env python3
"""
Phase 1: Classify all docs/ content by value and state
Cross-reference with code reality and identify broken links
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

# Load docs structure
with open('audit/docs_structure.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

docs_files = data['docs']
src_modules = set(data['src_modules'])
total_files = data['total_files']

# Initialize classification
classification = {
    'total_files': total_files,
    'by_type': {'critical': 0, 'useful': 0, 'redundant': 0, 'junk': 0},
    'by_state': {'complete': 0, 'partial': 0, 'broken': 0, 'unknown': 0},
    'by_category': defaultdict(int),
    'files': [],
    'broken_links_files': [],
    'orphaned_but_valid': [],
    'recommend_delete': [],
    'recommend_repair': []
}

# Critical keywords for TYPE classification
CRITICAL_KEYWORDS = [
    'architecture', 'security', 'api', 'governance', 'constitutional',
    'framework', 'protocol', 'specification', 'doctrine', 'compliance',
    'policy', 'sovereignty', 'threat', 'audit', 'trust'
]

USEFUL_KEYWORDS = [
    'guide', 'runbook', 'playbook', 'operations', 'developer',
    'implementation', 'integration', 'deployment', 'monitoring',
    'report', 'sre', 'testing', 'procedure'
]

JUNK_INDICATORS = [
    'scratch', 'temp', 'tmp', 'test', 'draft', 'wip', 'old',
    'backup', 'copy', '~', '.swp', '.bak'
]

def check_broken_links(filepath):
    """Check for broken markdown links and references"""
    if not filepath.endswith('.md'):
        return []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        broken = []
        
        # Check markdown links [text](path)
        md_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        for text, link in md_links:
            if link.startswith('http'):
                continue  # Skip external links
            if link.startswith('#'):
                continue  # Skip anchor links
            
            # Resolve relative path
            link_path = link.split('#')[0]  # Remove anchor
            if link_path:
                full_path = os.path.normpath(os.path.join(os.path.dirname(filepath), link_path))
                if not os.path.exists(full_path):
                    broken.append(f"Link to {link}")
        
        # Check image references
        img_refs = re.findall(r'!\[([^\]]*)\]\(([^)]+)\)', content)
        for alt, src in img_refs:
            if src.startswith('http'):
                continue
            full_path = os.path.normpath(os.path.join(os.path.dirname(filepath), src))
            if not os.path.exists(full_path):
                broken.append(f"Image {src}")
        
        return broken
    except Exception as e:
        return [f"Error checking: {e}"]

def classify_file(file_info):
    """Classify a single file by TYPE and STATE"""
    path = file_info['path']
    name = file_info['name'].lower()
    category = file_info['category']
    
    classification['by_category'][category] += 1
    
    # TYPE classification
    file_type = 'unknown'
    
    # Check for junk first
    if any(indicator in name for indicator in JUNK_INDICATORS):
        file_type = 'junk'
    # Check for critical
    elif any(keyword in name or keyword in category for keyword in CRITICAL_KEYWORDS):
        file_type = 'critical'
    # Check for useful
    elif any(keyword in name or keyword in category for keyword in USEFUL_KEYWORDS):
        file_type = 'useful'
    # Special category handling
    elif category in ['internal', 'archive', 'art']:
        file_type = 'useful' if category == 'internal' else 'redundant'
    elif category == 'reports':
        file_type = 'useful'
    else:
        # Default to useful for organized content
        file_type = 'useful' if category != 'root' else 'unknown'
    
    # STATE classification
    state = 'unknown'
    broken_links = []
    
    # Check if file exists and is readable
    if not os.path.exists(path):
        state = 'broken'
    elif file_info['size'] < 100:
        state = 'partial'  # Very small files likely stubs
    else:
        # Check for broken links
        broken_links = check_broken_links(path)
        if broken_links:
            state = 'broken'
        elif file_info['size'] > 1000:
            state = 'complete'  # Substantial content
        else:
            state = 'partial'
    
    # Cross-reference with src/ modules
    accuracy_note = None
    # Extract potential module references from filename
    module_refs = re.findall(r'([a-z_]+)', name)
    referenced_modules = [m for m in module_refs if m in src_modules]
    
    if referenced_modules:
        accuracy_note = f"References modules: {', '.join(referenced_modules)}"
    
    result = {
        'path': path,
        'name': file_info['name'],
        'category': category,
        'type': file_type,
        'state': state,
        'size': file_info['size'],
        'broken_links': broken_links,
        'accuracy_note': accuracy_note
    }
    
    # Update counters
    classification['by_type'][file_type] += 1
    classification['by_state'][state] += 1
    
    # Track broken files
    if broken_links:
        classification['broken_links_files'].append({
            'path': path,
            'broken_count': len(broken_links),
            'issues': broken_links[:5]  # First 5 issues
        })
    
    # Track recommendations
    if file_type == 'junk' or (file_type == 'redundant' and state == 'broken'):
        classification['recommend_delete'].append(path)
    elif state == 'broken' and file_type in ['critical', 'useful']:
        classification['recommend_repair'].append(path)
    
    return result

print(f"Classifying {total_files} documentation files...")

# Process all files
for i, file_info in enumerate(docs_files, 1):
    if i % 100 == 0:
        print(f"  Processed {i}/{total_files} files...")
    
    result = classify_file(file_info)
    classification['files'].append(result)

# Identify orphaned but valid files
# Files in well-organized directories that aren't broken
for file_result in classification['files']:
    if file_result['category'] not in ['root', 'archive'] and \
       file_result['state'] != 'broken' and \
       file_result['type'] in ['critical', 'useful']:
        classification['orphaned_but_valid'].append(file_result['path'])

# Summary statistics
print(f"\n=== CLASSIFICATION SUMMARY ===")
print(f"Total files: {total_files}")
print(f"\nBy TYPE:")
for type_name, count in sorted(classification['by_type'].items()):
    pct = (count / total_files) * 100
    print(f"  {type_name:12s}: {count:4d} ({pct:5.1f}%)")

print(f"\nBy STATE:")
for state_name, count in sorted(classification['by_state'].items()):
    pct = (count / total_files) * 100
    print(f"  {state_name:12s}: {count:4d} ({pct:5.1f}%)")

print(f"\nBroken links found in: {len(classification['broken_links_files'])} files")
print(f"Orphaned but valid: {len(classification['orphaned_but_valid'])} files")
print(f"Recommend delete: {len(classification['recommend_delete'])} files")
print(f"Recommend repair: {len(classification['recommend_repair'])} files")

# Save classification
with open('audit/classification_docs.json', 'w', encoding='utf-8') as f:
    json.dump(classification, f, indent=2)

print(f"\n✓ Classification saved to audit/classification_docs.json")
