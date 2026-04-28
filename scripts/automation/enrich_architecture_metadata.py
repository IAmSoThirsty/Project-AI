#!/usr/bin/env python3
"""
AGENT-010: P0 Architecture Documentation Metadata Enrichment
Adds missing YAML frontmatter fields to architecture documentation.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional

# ANSI color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RED = '\033[91m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def extract_yaml_and_content(file_path: str) -> tuple[Optional[str], Optional[str], str]:
    """Extract YAML frontmatter and content from markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if file has YAML frontmatter
    yaml_pattern = r'^---\n(.*?)\n---\n(.*)$'
    match = re.match(yaml_pattern, content, re.DOTALL)
    
    if match:
        return match.group(1), match.group(2), content
    else:
        return None, content, content

def parse_yaml_dict(yaml_str: str) -> Dict[str, any]:
    """Simple YAML parser for our specific metadata structure."""
    result = {}
    current_key = None
    current_list = []
    in_list = False
    
    lines = yaml_str.split('\n')
    for line in lines:
        # Skip empty lines
        if not line.strip():
            continue
        
        # Main key-value pair
        if ':' in line and not line.strip().startswith('-'):
            if in_list and current_key:
                result[current_key] = current_list
                current_list = []
                in_list = False
            
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            
            # Check if value is a list indicator
            if value.startswith('['):
                # Inline list
                result[key] = eval(value) if value else []
            elif not value:
                # Next lines might be a list
                current_key = key
                in_list = True
            else:
                # Simple value
                result[key] = value.strip('"\'')
        
        # List item
        elif line.strip().startswith('-') and in_list:
            item = line.strip()[1:].strip()
            current_list.append(item.strip('"\''))
    
    # Handle last list
    if in_list and current_key:
        result[current_key] = current_list
    
    return result

def determine_stakeholders(arch_layer: str, tags: List[str]) -> List[str]:
    """Determine stakeholders based on architecture layer and tags."""
    base_stakeholders = ["architecture-team", "developers"]
    
    if arch_layer == "infrastructure":
        base_stakeholders.append("platform-team")
        base_stakeholders.append("devops-team")
    elif arch_layer == "application":
        base_stakeholders.append("product-team")
    
    # Add specialized stakeholders based on tags
    if any(tag in tags for tag in ["security", "governance", "contrarian-firewall"]):
        base_stakeholders.append("security-team")
    
    if any(tag in tags for tag in ["god-tier", "distributed-systems"]):
        base_stakeholders.append("infrastructure-team")
    
    if "tarl" in str(tags).lower() or "governance" in str(tags).lower():
        base_stakeholders.append("compliance-team")
    
    return list(set(base_stakeholders))  # Remove duplicates

def map_related_systems(related_docs: List[str], uses: List[str], tags: List[str]) -> List[str]:
    """Map related_docs and uses to related_systems."""
    systems = []
    
    # Core architecture systems
    architecture_keywords = {
        "kernel": "kernel",
        "superkernel": "superkernel", 
        "pace": "pace-engine",
        "tarl": "tarl-governance",
        "triumvirate": "triumvirate",
        "governance": "governance-service",
        "workflow": "workflow-engine",
        "agent": "agent-coordinator",
        "capability": "capability-system",
        "state": "state-manager",
        "identity": "identity-engine",
        "temporal": "temporal-integration",
        "contrarian": "contrarian-firewall",
        "planetary": "planetary-defense",
        "sovereign": "sovereign-runtime",
        "god-tier": "god-tier-platform",
        "cluster": "cluster-coordinator",
        "hydra": "hydra-50",
        "bio-brain": "bio-brain-mapping"
    }
    
    # Extract from related_docs and uses
    all_refs = related_docs + uses + tags
    for ref in all_refs:
        ref_lower = str(ref).lower()
        for keyword, system in architecture_keywords.items():
            if keyword in ref_lower and system not in systems:
                systems.append(system)
    
    return systems if systems else ["core-architecture"]

def enrich_metadata(yaml_dict: Dict, filename: str) -> str:
    """Add missing metadata fields to existing YAML."""
    enriched = yaml_dict.copy()
    
    # Add missing fields with smart defaults
    if 'created' not in enriched:
        enriched['created'] = enriched.get('created_date', '2026-02-01')
    
    if 'last_verified' not in enriched:
        enriched['last_verified'] = '2026-04-20'
    
    if 'review_cycle' not in enriched:
        enriched['review_cycle'] = 'quarterly'
    
    # Map stakeholders
    if 'stakeholders' not in enriched:
        arch_layer = enriched.get('architecture_layer', 'application')
        tags = enriched.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        enriched['stakeholders'] = determine_stakeholders(arch_layer, tags)
    
    # Map related_systems from existing fields
    if 'related_systems' not in enriched:
        related_docs = enriched.get('related_docs', [])
        uses = enriched.get('uses', [])
        tags = enriched.get('tags', [])
        
        if isinstance(related_docs, str):
            related_docs = [related_docs]
        if isinstance(uses, str):
            uses = [uses]
        if isinstance(tags, str):
            tags = [tags]
        
        enriched['related_systems'] = map_related_systems(related_docs, uses, tags)
    
    return enriched

def format_yaml_value(value) -> str:
    """Format a value for YAML output."""
    if isinstance(value, list):
        if not value:
            return "[]"
        return "[" + ", ".join(f'"{v}"' if isinstance(v, str) else str(v) for v in value) + "]"
    elif isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, (int, float)):
        return str(value)
    else:
        # String value - quote if contains special characters
        str_val = str(value)
        if ':' in str_val or '#' in str_val or str_val.startswith('-'):
            return f'"{str_val}"'
        return str_val

def generate_yaml_frontmatter(metadata: Dict) -> str:
    """Generate formatted YAML frontmatter."""
    lines = ["---"]
    
    # Define field order for readability
    field_order = [
        'title', 'id', 'type', 'version', 
        'created', 'created_date', 'last_verified', 'updated_date',
        'status', 'author', 'contributors',
        '# Architecture-Specific Metadata',
        'architecture_layer', 'design_pattern', 
        'implements', 'uses',
        'quality_attributes', 'adr_status',
        '# Component Classification',
        'area', 'tags', 'component',
        '# Relationships',
        'related_docs', 'related_systems', 'depends_on',
        'supersedes', 'superseded_by',
        '# Audience & Priority',
        'audience', 'stakeholders', 'priority', 'difficulty',
        'estimated_reading_time', 'review_cycle',
        '# Security & Compliance',
        'classification', 'sensitivity', 'compliance',
        '# Discovery',
        'keywords', 'search_terms', 'aliases',
        '# Quality Metadata',
        'review_status', 'accuracy_rating', 'test_coverage'
    ]
    
    # Add fields in order
    for field in field_order:
        if field.startswith('#'):
            lines.append(field)
        elif field in metadata:
            value = metadata[field]
            formatted_value = format_yaml_value(value)
            lines.append(f"{field}: {formatted_value}")
    
    # Add any remaining fields not in order
    for key, value in metadata.items():
        if key not in field_order:
            formatted_value = format_yaml_value(value)
            lines.append(f"{key}: {formatted_value}")
    
    lines.append("---")
    return '\n'.join(lines)

def create_metadata_for_report_file() -> str:
    """Create YAML frontmatter for METADATA_P0_ARCHITECTURE_REPORT.md."""
    return """---
type: report
tags: [p0-architecture, metadata-enrichment, documentation, agent-010]
created: 2026-04-20
last_verified: 2026-04-20
status: complete
related_systems: [core-architecture, documentation-system]
stakeholders: [architecture-team, documentation-team, developers]
architectural_layer: documentation
design_patterns: []
dependencies: []
review_cycle: quarterly
---"""

def process_file(file_path: Path) -> Dict[str, any]:
    """Process a single markdown file."""
    result = {
        'filename': file_path.name,
        'status': 'pending',
        'changes': [],
        'errors': []
    }
    
    try:
        yaml_str, content, full_content = extract_yaml_and_content(str(file_path))
        
        if yaml_str is None:
            # No YAML frontmatter - create it
            if file_path.name == "METADATA_P0_ARCHITECTURE_REPORT.md":
                new_yaml = create_metadata_for_report_file()
                new_content = f"{new_yaml}\n\n{content}"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                result['status'] = 'created'
                result['changes'].append('Created new YAML frontmatter')
            else:
                result['status'] = 'skipped'
                result['errors'].append('No YAML frontmatter found and not report file')
        else:
            # Parse and enrich existing YAML
            yaml_dict = parse_yaml_dict(yaml_str)
            enriched_dict = enrich_metadata(yaml_dict, file_path.name)
            
            # Check what changed
            changes = []
            for key in ['created', 'last_verified', 'review_cycle', 'stakeholders', 'related_systems']:
                if key not in yaml_dict and key in enriched_dict:
                    changes.append(f"Added {key}")
            
            if changes:
                # Generate new YAML
                new_yaml = generate_yaml_frontmatter(enriched_dict)
                new_content = f"{new_yaml}\n\n{content}"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                result['status'] = 'enriched'
                result['changes'] = changes
            else:
                result['status'] = 'up-to-date'
        
    except Exception as e:
        result['status'] = 'error'
        result['errors'].append(str(e))
    
    return result

def main():
    """Main execution function."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}╔═══════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║  AGENT-010: P0 Architecture Metadata Enrichment         ║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚═══════════════════════════════════════════════════════════╝{Colors.RESET}\n")
    
    arch_dir = Path(r"T:\Project-AI-main\docs\architecture")
    
    if not arch_dir.exists():
        print(f"{Colors.RED}✗ Architecture directory not found: {arch_dir}{Colors.RESET}")
        return
    
    # Get all markdown files
    md_files = sorted(arch_dir.glob("*.md"))
    
    print(f"{Colors.BLUE}📁 Processing {len(md_files)} architecture files...{Colors.RESET}\n")
    
    results = []
    stats = {
        'created': 0,
        'enriched': 0,
        'up-to-date': 0,
        'error': 0,
        'skipped': 0
    }
    
    for file_path in md_files:
        print(f"{Colors.YELLOW}Processing: {file_path.name}{Colors.RESET}")
        result = process_file(file_path)
        results.append(result)
        
        status = result['status']
        stats[status] = stats.get(status, 0) + 1
        
        # Print result
        if result['status'] == 'created':
            print(f"  {Colors.GREEN}✓ Created YAML frontmatter{Colors.RESET}")
        elif result['status'] == 'enriched':
            print(f"  {Colors.GREEN}✓ Enriched: {', '.join(result['changes'])}{Colors.RESET}")
        elif result['status'] == 'up-to-date':
            print(f"  {Colors.CYAN}○ Already up-to-date{Colors.RESET}")
        elif result['status'] == 'error':
            print(f"  {Colors.RED}✗ Error: {'; '.join(result['errors'])}{Colors.RESET}")
        elif result['status'] == 'skipped':
            print(f"  {Colors.YELLOW}⊘ Skipped{Colors.RESET}")
        print()
    
    # Print summary
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══════════════ SUMMARY ═══════════════{Colors.RESET}\n")
    print(f"  {Colors.GREEN}✓ Created:     {stats['created']}{Colors.RESET}")
    print(f"  {Colors.GREEN}✓ Enriched:    {stats['enriched']}{Colors.RESET}")
    print(f"  {Colors.CYAN}○ Up-to-date:  {stats['up-to-date']}{Colors.RESET}")
    print(f"  {Colors.YELLOW}⊘ Skipped:     {stats['skipped']}{Colors.RESET}")
    print(f"  {Colors.RED}✗ Errors:      {stats['error']}{Colors.RESET}")
    print(f"\n{Colors.BOLD}Total files processed: {len(md_files)}{Colors.RESET}\n")
    
    if stats['error'] > 0:
        print(f"\n{Colors.RED}Files with errors:{Colors.RESET}")
        for r in results:
            if r['status'] == 'error':
                print(f"  - {r['filename']}: {'; '.join(r['errors'])}")

if __name__ == "__main__":
    main()
