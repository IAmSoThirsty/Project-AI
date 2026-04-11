#!/usr/bin/env python3
"""Phase 1 Classifier: Classify all README files by quality and accuracy."""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple


def get_all_readmes() -> List[str]:
    """Get all tracked README files using git."""
    result = subprocess.run(
        ['git', 'ls-files'],
        capture_output=True,
        text=True,
        check=True
    )
    all_files = result.stdout.strip().split('\n')
    readmes = [f for f in all_files if 'README' in f.upper()]
    return readmes


def classify_readme_type(path: str) -> str:
    """Classify README by TYPE: critical, useful, redundant, junk."""
    path_lower = path.lower()
    
    # Root README is critical
    if path == 'README.md':
        return 'critical'
    
    # Major module READMEs are critical
    critical_dirs = [
        'src/', 'docs/', 'api/', 'engines/', 'API_SPECIFICATIONS/',
        'governance/', 'kernel/', 'security/'
    ]
    for crit_dir in critical_dirs:
        if path.startswith(crit_dir) and path.count('/') <= 2:
            return 'critical'
    
    # Vendor/node_modules are junk
    junk_dirs = ['node_modules/', '.venv/', 'venv/', '__pycache__/', 'dist/', 'build/']
    for junk_dir in junk_dirs:
        if junk_dir in path:
            return 'junk'
    
    # Duplicate .agent vs .agents
    if path.startswith('.agent/') or path.startswith('.agents/'):
        return 'redundant'
    
    # Archive/backup directories
    if 'archive/' in path_lower or 'backup/' in path_lower or 'old/' in path_lower:
        return 'redundant'
    
    # Everything else is useful
    return 'useful'


def analyze_readme_content(path: str) -> Tuple[str, int, List[str]]:
    """Analyze README content and return STATE, line count, and issues."""
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')
            line_count = len([l for l in lines if l.strip()])  # Non-empty lines
    except Exception as e:
        return 'unknown', 0, [f'Cannot read: {str(e)}']
    
    issues = []
    
    # Check for stubs
    if line_count < 10:
        return 'unknown', line_count, ['Minimal stub (<10 lines)']
    
    content_lower = content.lower()
    
    # Check for TODO/FIXME markers
    if 'todo' in content_lower or 'fixme' in content_lower:
        issues.append('Contains TODO/FIXME markers')
    
    # Check for naming inconsistency
    if 'project-ai' in content_lower or 'project_ai' in content_lower:
        # Check if both variants exist
        if 'project-ai' in content_lower and 'project_ai' in content_lower:
            issues.append('Naming inconsistency: Project-AI vs project_ai')
    
    # Check for broken references (common missing files)
    broken_refs = [
        'PROJECT_STATUS.md', 'PRODUCTION_DEPLOYMENT.md',
        'DEPLOYMENT_GUIDE.md', 'ARCHITECTURE_OVERVIEW.md'
    ]
    for ref in broken_refs:
        if ref in content and not os.path.exists(ref):
            issues.append(f'Broken reference: {ref}')
    
    # Classify STATE based on sections
    has_purpose = any(s in content_lower for s in ['overview', 'description', 'about', 'introduction'])
    has_install = any(s in content_lower for s in ['install', 'setup', 'getting started', 'quick start'])
    has_usage = any(s in content_lower for s in ['usage', 'how to', 'example', 'tutorial'])
    has_api = 'api' in content_lower and ('endpoint' in content_lower or 'function' in content_lower)
    
    section_count = sum([has_purpose, has_install, has_usage, has_api])
    
    # Determine STATE
    if section_count >= 3 and line_count >= 50:
        state = 'complete'
    elif has_purpose and (has_install or has_usage):
        state = 'complete'
    elif has_purpose:
        state = 'partial'
    elif len(issues) > 0:
        state = 'broken'
    else:
        state = 'partial'
    
    return state, line_count, issues


def classify_quality_tier(line_count: int, state: str, readme_type: str) -> str:
    """Classify README by quality tier."""
    if readme_type == 'junk':
        return 'tier_4_stubs'
    
    if state == 'complete' and line_count >= 300:
        return 'tier_1_exemplary'
    elif state == 'complete' and line_count >= 50:
        return 'tier_2_good'
    elif state in ['complete', 'partial'] and line_count >= 10:
        return 'tier_3_adequate'
    else:
        return 'tier_4_stubs'


def main():
    """Main classification workflow."""
    print("=== Phase 1: README Classification ===\n")
    
    # Get all README files
    print("Scanning for README files...")
    readmes = get_all_readmes()
    print(f"Found {len(readmes)} tracked README files\n")
    
    # Classify each README
    classifications = []
    type_counts = {'critical': 0, 'useful': 0, 'redundant': 0, 'junk': 0}
    tier_counts = {
        'tier_1_exemplary': 0,
        'tier_2_good': 0,
        'tier_3_adequate': 0,
        'tier_4_stubs': 0
    }
    all_issues = []
    naming_inconsistency_count = 0
    outdated_refs_count = 0
    todo_count = 0
    duplicate_dirs = set()
    
    for readme in readmes:
        readme_type = classify_readme_type(readme)
        state, line_count, issues = analyze_readme_content(readme)
        tier = classify_quality_tier(line_count, state, readme_type)
        
        type_counts[readme_type] += 1
        tier_counts[tier] += 1
        
        # Track specific issues
        for issue in issues:
            if 'Naming inconsistency' in issue:
                naming_inconsistency_count += 1
            if 'Broken reference' in issue:
                outdated_refs_count += 1
            if 'TODO/FIXME' in issue:
                todo_count += 1
        
        if issues:
            all_issues.extend([(readme, issue) for issue in issues])
        
        # Track duplicate directories
        if readme_type == 'redundant' and ('.agent' in readme):
            duplicate_dirs.add(readme.split('/')[0])
        
        classifications.append({
            'path': readme,
            'type': readme_type,
            'state': state,
            'quality_tier': tier,
            'line_count': line_count,
            'issues': issues
        })
        
        # Progress indicator
        if len(classifications) % 50 == 0:
            print(f"Processed {len(classifications)} READMEs...")
    
    print(f"\nClassification complete: {len(classifications)} READMEs analyzed\n")
    
    # Identify critical missing READMEs based on Phase 0 report
    critical_missing = [
        'src/app/README.md',
        'src/security/README.md',
        'src/psia/README.md',
        'src/interpreter/README.md',
        'engines/hydra_50/README.md',
        'docs/api/README.md',
        'src/cognition/README.md',
        'src/features/README.md',
        'src/integrations/README.md',
        'src/plugins/README.md',
        'emergent-microservices/trust-graph/README.md',
        'emergent-microservices/compliance/README.md',
        'emergent-microservices/data-vault/README.md'
    ]
    
    # Create output
    output = {
        'total_readmes': len(readmes),
        'by_type': type_counts,
        'by_quality_tier': tier_counts,
        'issues': {
            'naming_inconsistency': naming_inconsistency_count,
            'outdated_references': outdated_refs_count,
            'todo_markers': todo_count,
            'duplicate_dirs': sorted(list(duplicate_dirs))
        },
        'critical_missing': critical_missing,
        'classifications': classifications,
        'all_issues': all_issues[:50]  # Top 50 issues
    }
    
    # Write to output file
    output_path = 'audit/classification_readmes.json'
    os.makedirs('audit', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2)
    
    print(f"✅ Classification saved to: {output_path}\n")
    
    # Print summary
    print("=== CLASSIFICATION SUMMARY ===\n")
    print(f"Total READMEs: {len(readmes)}")
    print(f"\nBy Type:")
    for t, count in type_counts.items():
        pct = (count / len(readmes)) * 100
        print(f"  {t:12s}: {count:3d} ({pct:5.1f}%)")
    
    print(f"\nBy Quality Tier:")
    for tier, count in tier_counts.items():
        pct = (count / len(readmes)) * 100
        print(f"  {tier:20s}: {count:3d} ({pct:5.1f}%)")
    
    print(f"\nIssues Found:")
    print(f"  Naming inconsistency: {naming_inconsistency_count}")
    print(f"  Outdated references:  {outdated_refs_count}")
    print(f"  TODO markers:         {todo_count}")
    print(f"  Duplicate dirs:       {len(duplicate_dirs)}")
    
    print(f"\nCritical Missing: {len(critical_missing)} READMEs")
    
    print("\n=== TOP RECOMMENDATIONS ===\n")
    print("1. Create 13 missing critical READMEs for src/ modules")
    print("2. Resolve .agent vs .agents duplicate directory confusion")
    print(f"3. Fix {outdated_refs_count} broken documentation references")
    print(f"4. Address {todo_count} TODO/FIXME markers in READMEs")
    print(f"5. Standardize naming: Project-AI vs project_ai ({naming_inconsistency_count} files)")
    print(f"6. Upgrade {tier_counts['tier_4_stubs']} stub READMEs to adequate quality")
    print(f"7. Review and delete/archive {type_counts['redundant']} redundant READMEs")
    print(f"8. Clean up {type_counts['junk']} vendor/junk READMEs")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
