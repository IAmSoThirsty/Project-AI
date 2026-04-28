"""
AGENT-076: Cross-Links Addition Script
Adds comprehensive wiki links between Core AI, Governance, and Constitutional systems
"""

import re
from pathlib import Path

# Define cross-link templates
CORE_AI_RELATED = """
### Core AI Integration
- **[[relationships/core-ai/01-FourLaws-Relationship-Map|FourLaws]]**: Ethics validation framework
- **[[relationships/core-ai/02-AIPersona-Relationship-Map|AIPersona]]**: Personality and behavior system
- **[[relationships/core-ai/03-MemoryExpansionSystem-Relationship-Map|MemoryExpansion]]**: Knowledge storage
- **[[relationships/core-ai/04-LearningRequestManager-Relationship-Map|LearningRequest]]**: Learning governance
- **[[relationships/core-ai/05-PluginManager-Relationship-Map|PluginManager]]**: Plugin system
- **[[relationships/core-ai/06-CommandOverride-Relationship-Map|CommandOverride]]**: Emergency controls"""

GOVERNANCE_RELATED = """
### Governance Integration
- **[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW|Pipeline System]]**: Universal enforcement layer (6-phase)
- **[[relationships/governance/02_POLICY_ENFORCEMENT_POINTS|Policy Enforcement]]**: PEP locations and mechanisms
- **[[relationships/governance/03_AUTHORIZATION_FLOWS|Authorization Flows]]**: Request authorization workflows
- **[[relationships/governance/04_AUDIT_TRAIL_GENERATION|Audit Trail]]**: Cryptographic audit logging (SHA-256)
- **[[relationships/governance/05_SYSTEM_INTEGRATION_MATRIX|Integration Matrix]]**: Cross-system dependencies"""

CONSTITUTIONAL_RELATED = """
### Constitutional Integration
- **[[relationships/constitutional/01_constitutional_systems_overview|Constitutional AI]]**: Constitutional framework and principles
- **[[relationships/constitutional/02_enforcement_chains|Enforcement Chains]]**: Hierarchical ethics enforcement
- **[[relationships/constitutional/03_ethics_validation_flows|Ethics Validation]]**: Validation workflows and decision logic"""

RELATED_SYSTEMS_TEMPLATE = f"""
## Related Systems

{CORE_AI_RELATED}

{GOVERNANCE_RELATED}

{CONSTITUTIONAL_RELATED}
"""

def add_related_systems_section(file_path: Path):
    """Add Related Systems section before Document Metadata"""
    content = file_path.read_text(encoding='utf-8')
    
    # Skip if already has Related Systems section
    if '## Related Systems' in content:
        print(f"  ✓ {file_path.name} already has Related Systems section")
        return False
    
    # Find Document Metadata section
    if '## Document Metadata' in content:
        content = content.replace(
            '---\n\n## Document Metadata',
            f'---\n{RELATED_SYSTEMS_TEMPLATE}\n\n---\n\n## Document Metadata'
        )
        file_path.write_text(content, encoding='utf-8')
        print(f"  + Added Related Systems section to {file_path.name}")
        return True
    else:
        print(f"  ! No Document Metadata section found in {file_path.name}")
        return False

def add_inline_wiki_links(file_path: Path, patterns):
    """Add inline wiki links based on patterns"""
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    links_added = 0
    
    for pattern, replacement in patterns:
        if pattern in content and replacement not in content:
            content = content.replace(pattern, replacement)
            links_added += 1
    
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        print(f"  + Added {links_added} inline links to {file_path.name}")
        return links_added
    return 0

# Process files
def main():
    base = Path("T:/Project-AI-main/relationships")
    
    # Core AI files
    core_ai_files = list((base / "core-ai").glob("*.md"))
    governance_files = list((base / "governance").glob("*.md"))
    constitutional_files = list((base / "constitutional").glob("*.md"))
    
    all_files = core_ai_files + governance_files + constitutional_files
    all_files = [f for f in all_files if 'MISSION_COMPLETE' not in f.name and 'README' not in f.name]
    
    print(f"\n🎯 AGENT-076: Processing {len(all_files)} documentation files\n")
    
    sections_added = 0
    inline_links_added = 0
    
    for file_path in all_files:
        print(f"\n📄 {file_path.name}")
        if add_related_systems_section(file_path):
            sections_added += 1
        
        # Add inline links (examples - expand as needed)
        patterns = [
            ('FourLaws.validate_action()', '[[relationships/core-ai/01-FourLaws-Relationship-Map|FourLaws]].validate_action()'),
            ('Pipeline System', '[[relationships/governance/01_GOVERNANCE_SYSTEMS_OVERVIEW|Pipeline System]]'),
            ('audit trail', '[[relationships/governance/04_AUDIT_TRAIL_GENERATION|audit trail]]'),
            ('Constitutional AI', '[[relationships/constitutional/01_constitutional_systems_overview|Constitutional AI]]'),
        ]
        inline_links_added += add_inline_wiki_links(file_path, patterns)
    
    print(f"\n\n✅ COMPLETED:")
    print(f"   • Related Systems sections added: {sections_added}")
    print(f"   • Inline wiki links added: {inline_links_added}")
    print(f"   • Total files processed: {len(all_files)}")

if __name__ == "__main__":
    main()
