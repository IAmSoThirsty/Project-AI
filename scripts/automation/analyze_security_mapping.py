"""
Security Controls to Components Mapping Script
AGENT-086 Mission: Create ~350 bidirectional wiki links
"""
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple

# Project root
PROJECT_ROOT = Path(r"T:\Project-AI-main")

# Security control documents
SECURITY_DOCS = [
    "docs/security_compliance/SECURITY_FRAMEWORK.md",
    "docs/security_compliance/ASL3_IMPLEMENTATION.md",
    "docs/security_compliance/THREAT_MODEL.md",
    "docs/security_compliance/CERBERUS_SECURITY_STRUCTURE.md",
    "docs/security_compliance/AI_SECURITY_FRAMEWORK.md",
    "docs/security_compliance/SECRET_MANAGEMENT.md",
    "docs/security_compliance/ENHANCED_DEFENSES.md",
    "docs/security_compliance/SECURITY_GOVERNANCE.md",
    "relationships/security/01_security_system_overview.md",
    "relationships/security/03_defense_layers.md",
    "relationships/security/05_cross_system_integrations.md",
]

# Component directories to scan
COMPONENT_DIRS = [
    "src/app/core",
    "src/app/security",
    "src/app/agents",
    "src/app/gui",
    "src/app/vault",
    "src/app/infrastructure",
]

def extract_security_controls(doc_path: Path) -> List[Dict]:
    """Extract security controls from documentation."""
    controls = []
    if not doc_path.exists():
        return controls
    
    content = doc_path.read_text(encoding="utf-8")
    
    # Extract control patterns
    # Pattern 1: Heading-based controls
    control_headings = re.findall(r'^#{2,4}\s+(.+(?:Control|System|Protection|Defense|Enforcement|Guard|Monitor|Detector).*?)$', 
                                   content, re.MULTILINE | re.IGNORECASE)
    
    # Pattern 2: Code block references
    code_refs = re.findall(r'`([a-zA-Z_]+\.(py|md))`', content)
    
    # Pattern 3: Explicit component mentions
    component_mentions = re.findall(r'\*\*Location:\*\*\s+`([^`]+)`', content)
    
    return {
        'headings': control_headings,
        'code_refs': code_refs,
        'locations': component_mentions,
        'file': str(doc_path.relative_to(PROJECT_ROOT))
    }

def scan_components(component_dir: Path) -> List[Dict]:
    """Scan component directory for security-related files."""
    components = []
    if not component_dir.exists():
        return components
    
    for py_file in component_dir.glob("**/*.py"):
        if "__pycache__" in str(py_file):
            continue
        
        rel_path = py_file.relative_to(PROJECT_ROOT)
        content = py_file.read_text(encoding="utf-8", errors="ignore")
        
        # Security indicators
        has_security = any([
            'security' in py_file.name.lower(),
            'auth' in py_file.name.lower(),
            'encrypt' in py_file.name.lower(),
            'validate' in py_file.name.lower(),
            re.search(r'class\s+\w*(Security|Auth|Guard|Protect|Enforce|Monitor|Defend)', content),
        ])
        
        components.append({
            'file': str(rel_path),
            'name': py_file.stem,
            'has_security': has_security,
            'lines': len(content.splitlines())
        })
    
    return components

# Main analysis
results = {
    'controls': {},
    'components': [],
    'mappings': []
}

print("Scanning security control documentation...")
for doc_path in SECURITY_DOCS:
    full_path = PROJECT_ROOT / doc_path
    if full_path.exists():
        controls = extract_security_controls(full_path)
        results['controls'][doc_path] = controls
        print(f"  ✓ {doc_path}: {len(controls.get('headings', []))} controls found")

print("\nScanning component directories...")
for comp_dir in COMPONENT_DIRS:
    full_path = PROJECT_ROOT / comp_dir
    if full_path.exists():
        components = scan_components(full_path)
        results['components'].extend(components)
        print(f"  ✓ {comp_dir}: {len(components)} components found")

# Save results
output_path = PROJECT_ROOT / "security_mapping_analysis.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)

print(f"\n✓ Analysis complete: {output_path}")
print(f"  - Control documents: {len(results['controls'])}")
print(f"  - Components found: {len(results['components'])}")
print(f"  - Security components: {sum(1 for c in results['components'] if c['has_security'])}")
