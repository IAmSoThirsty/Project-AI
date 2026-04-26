#!/usr/bin/env python3
"""
Developer Documentation Metadata Addition Script
AGENT-026: P1 Developer Documentation Metadata Specialist

Adds comprehensive YAML frontmatter to all developer documentation files.
"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# File classifications
FILE_CATEGORIES = {
    # API References (expert level)
    'api_reference': {
        'patterns': ['API_REFERENCE', 'API_GUIDE', 'CLI-CODEX'],
        'skill_level': 'expert',
        'type': 'reference',
        'code_examples': True,
        'api_reference': True,
    },
    
    # Implementation Guides (advanced level)
    'implementation': {
        'patterns': ['IMPLEMENTATION', 'INTEGRATION_PATTERNS', 'ARCHITECTURE'],
        'skill_level': 'advanced',
        'type': 'guide',
        'code_examples': True,
        'api_reference': False,
    },
    
    # Quickstart/Getting Started (beginner level)
    'quickstart': {
        'patterns': ['QUICKSTART', 'QUICK_START', 'QUICK_REFERENCE', 'HOW_TO_RUN'],
        'skill_level': 'beginner',
        'type': 'guide',
        'code_examples': True,
        'api_reference': False,
    },
    
    # Deployment Guides (intermediate level)
    'deployment': {
        'patterns': ['DEPLOYMENT', 'RELEASE', 'BUILD', 'DOCKER', 'KUBERNETES'],
        'skill_level': 'intermediate',
        'type': 'guide',
        'code_examples': True,
        'api_reference': False,
    },
    
    # Setup and Installation (beginner level)
    'setup': {
        'patterns': ['SETUP', 'install.md', 'INSTALLATION', 'config.md'],
        'skill_level': 'beginner',
        'type': 'guide',
        'code_examples': True,
        'api_reference': False,
    },
    
    # Testing/Coverage (intermediate level)
    'testing': {
        'patterns': ['COVERAGE', 'E2E', 'TEST', 'checks.md', 'smoke_checks'],
        'skill_level': 'intermediate',
        'type': 'guide',
        'code_examples': True,
        'api_reference': False,
    },
    
    # Contributing/Development (intermediate level)
    'contributing': {
        'patterns': ['CONTRIBUTING', 'DEVELOPMENT.md', 'ROADMAP'],
        'skill_level': 'intermediate',
        'type': 'guide',
        'code_examples': False,
        'api_reference': False,
    },
    
    # Reference Documentation (intermediate level)
    'reference': {
        'patterns': ['reference.md', 'README.md', 'OVERVIEW'],
        'skill_level': 'intermediate',
        'type': 'reference',
        'code_examples': False,
        'api_reference': False,
    },
    
    # Usage/Operations (beginner level)
    'usage': {
        'patterns': ['usage.md', 'troubleshooting.md', 'OPERATOR', 'MONITORING'],
        'skill_level': 'beginner',
        'type': 'guide',
        'code_examples': True,
        'api_reference': False,
    },
}

# Technology mappings
TECH_MAPPINGS = {
    'DESKTOP_APP': {'languages': ['Python'], 'frameworks': ['PyQt6']},
    'LEATHER_BOOK': {'languages': ['Python'], 'frameworks': ['PyQt6']},
    'WEB': {'languages': ['Python', 'JavaScript'], 'frameworks': ['Flask', 'React']},
    'DEPLOYMENT': {'languages': ['Python', 'Shell'], 'frameworks': ['Docker', 'Kubernetes']},
    'HYDRA': {'languages': ['Python'], 'frameworks': ['FastAPI']},
    'TARL': {'languages': ['Python'], 'frameworks': ['Temporal']},
    'MCP': {'languages': ['Python'], 'frameworks': []},
    'PROMETHEUS': {'languages': ['Python'], 'frameworks': ['Prometheus']},
    'KUBERNETES': {'languages': ['YAML'], 'frameworks': ['Kubernetes']},
    'DOCKER': {'languages': ['Shell'], 'frameworks': ['Docker']},
    'GRADLE': {'languages': ['JavaScript', 'Groovy'], 'frameworks': ['Gradle']},
    'CLI': {'languages': ['Python'], 'frameworks': []},
    'API': {'languages': ['Python'], 'frameworks': ['Flask', 'FastAPI']},
    'GUI': {'languages': ['Python'], 'frameworks': ['PyQt6']},
    'E2E': {'languages': ['Python'], 'frameworks': ['pytest']},
}

def classify_file(file_path: str) -> Tuple[str, Dict]:
    """Classify file into category based on filename patterns."""
    file_name = os.path.basename(file_path)
    
    for category, config in FILE_CATEGORIES.items():
        for pattern in config['patterns']:
            if pattern in file_name.upper():
                return category, config.copy()
    
    # Default classification
    return 'reference', {
        'skill_level': 'intermediate',
        'type': 'reference',
        'code_examples': False,
        'api_reference': False,
    }

def detect_technologies(file_path: str, content: str) -> Dict[str, List[str]]:
    """Detect languages and frameworks from filename and content."""
    file_name = os.path.basename(file_path).upper()
    languages = set()
    frameworks = set()
    
    # Check filename patterns
    for tech, mapping in TECH_MAPPINGS.items():
        if tech in file_name:
            languages.update(mapping['languages'])
            frameworks.update(mapping['frameworks'])
    
    # Check content for code blocks
    code_blocks = re.findall(r'```(\w+)', content)
    for lang in code_blocks:
        lang_lower = lang.lower()
        if lang_lower in ['python', 'py']:
            languages.add('Python')
        elif lang_lower in ['javascript', 'js', 'jsx']:
            languages.add('JavaScript')
        elif lang_lower in ['typescript', 'ts', 'tsx']:
            languages.add('TypeScript')
        elif lang_lower in ['bash', 'sh', 'shell']:
            languages.add('Shell')
        elif lang_lower in ['yaml', 'yml']:
            languages.add('YAML')
        elif lang_lower in ['dockerfile']:
            frameworks.add('Docker')
    
    # Default to Python if no language detected (most common in this project)
    if not languages:
        languages.add('Python')
    
    return {
        'languages': sorted(list(languages)),
        'frameworks': sorted(list(frameworks)) if frameworks else []
    }

def detect_prerequisites(file_path: str, content: str) -> List[str]:
    """Detect prerequisite documentation from content."""
    prerequisites = []
    file_name = os.path.basename(file_path)
    
    # Deployment guides need setup docs
    if 'DEPLOYMENT' in file_name.upper():
        prerequisites.append('[[install]]')
        prerequisites.append('[[config]]')
    
    # API docs need architecture understanding
    if 'API' in file_name.upper():
        prerequisites.append('[[ARCHITECTURE]]')
    
    # Integration guides need core concepts
    if 'INTEGRATION' in file_name.upper():
        prerequisites.append('[[README]]')
        prerequisites.append('[[ARCHITECTURE]]')
    
    # Advanced guides need quickstart
    if 'HYDRA' in file_name.upper() or 'TARL' in file_name.upper():
        prerequisites.append('[[QUICK_START]]')
    
    # E2E testing needs basic setup
    if 'E2E' in file_name.upper() or 'TEST' in file_name.upper():
        prerequisites.append('[[install]]')
        prerequisites.append('[[DEVELOPMENT]]')
    
    return prerequisites

def detect_implements_code(file_path: str, content: str) -> List[str]:
    """Detect which source files this document describes."""
    implements = []
    file_name = os.path.basename(file_path).upper()
    
    # Map documentation to source files
    doc_to_code_map = {
        'AI_PERSONA': ['src/app/core/ai_persona.py', 'src/app/gui/ai_persona_ui.py'],
        'LEATHER_BOOK': ['src/app/gui/leather_book_interface.py', 'src/app/gui/leather_book_dashboard.py'],
        'LEARNING_REQUEST': ['src/app/core/learning_request_manager.py'],
        'COMMAND_MEMORY': ['src/app/core/command_override.py', 'src/app/core/memory_expansion.py'],
        'IMAGE_GENERATION': ['src/app/core/image_generator.py', 'src/app/gui/image_generation.py'],
        'HYDRA': ['src/app/core/hydra_50_engine.py', 'src/app/core/hydra_50_telemetry.py'],
        'TARL': ['src/app/core/tarl_orchestrator.py'],
        'MCP': ['src/app/core/mcp_integration.py'],
    }
    
    for doc_key, code_files in doc_to_code_map.items():
        if doc_key in file_name:
            implements.extend(code_files)
    
    return implements

def has_frontmatter(content: str) -> bool:
    """Check if file already has YAML frontmatter."""
    return content.strip().startswith('---')

def generate_metadata(file_path: str, content: str) -> str:
    """Generate comprehensive YAML frontmatter for a developer doc."""
    file_name = os.path.basename(file_path)
    subdirectory = os.path.basename(os.path.dirname(file_path))
    
    # Extract title from first header or filename
    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
    else:
        title = file_name.replace('.md', '').replace('_', ' ').title()
    
    # Generate ID from filename
    doc_id = file_name.replace('.md', '').lower().replace('_', '-')
    
    # Classify file
    category, config = classify_file(file_path)
    
    # Detect technologies
    tech = detect_technologies(file_path, content)
    
    # Detect prerequisites
    prerequisites = detect_prerequisites(file_path, content)
    
    # Detect implementations
    implements = detect_implements_code(file_path, content)
    
    # Build metadata
    metadata_lines = [
        '---',
        f'title: "{title}"',
        f'id: {doc_id}',
        'type: guide' if config['type'] == 'guide' else 'type: reference',
        'area: development',
        'status: active',
        'version: "1.0"',
        f'created_date: "{datetime.now().strftime("%Y-%m-%d")}"',
        f'updated_date: "{datetime.now().strftime("%Y-%m-%d")}"',
        'author: AGENT-026',
        '',
        '# Classification',
        'tags:',
        '  - development',
    ]
    
    # Add subdirectory-based tags
    if subdirectory and subdirectory != 'developer':
        metadata_lines.append(f'  - {subdirectory}')
    
    # Add category-specific tags
    if 'api' in category or 'API' in file_name.upper():
        metadata_lines.append('  - api')
    if 'deployment' in category:
        metadata_lines.append('  - deployment')
    if 'testing' in category:
        metadata_lines.append('  - testing')
    if 'security' in file_name.lower():
        metadata_lines.append('  - security')
    
    # Developer-specific metadata
    metadata_lines.extend([
        '',
        '# Developer Metadata',
        f'skill_level: {config["skill_level"]}',
        'audience:',
        '  - developer',
    ])
    
    # Add additional audience
    if config['skill_level'] == 'expert':
        metadata_lines.append('  - architect')
    if 'deployment' in category:
        metadata_lines.append('  - devops')
    if 'security' in file_name.lower():
        metadata_lines.append('  - security_engineer')
    
    # Languages and frameworks
    metadata_lines.append('')
    metadata_lines.append('languages:')
    for lang in tech['languages']:
        metadata_lines.append(f'  - {lang}')
    
    if tech['frameworks']:
        metadata_lines.append('')
        metadata_lines.append('frameworks:')
        for fw in tech['frameworks']:
            metadata_lines.append(f'  - {fw}')
    
    # Code examples flag
    metadata_lines.extend([
        '',
        f'code_examples: {str(config["code_examples"]).lower()}',
        f'api_reference: {str(config["api_reference"]).lower()}',
    ])
    
    # Prerequisites
    if prerequisites:
        metadata_lines.append('')
        metadata_lines.append('prerequisites:')
        for prereq in prerequisites:
            metadata_lines.append(f'  - {prereq}')
    
    # Implementation relationships
    if implements:
        metadata_lines.append('')
        metadata_lines.append('implements:')
        for impl in implements:
            metadata_lines.append(f'  - {impl}')
    
    # Related docs
    metadata_lines.extend([
        '',
        'related_docs:',
        '  - [[README]]',
    ])
    
    if 'QUICKSTART' in file_name.upper() or 'QUICK_START' in file_name.upper():
        metadata_lines.append('  - [[DEVELOPMENT]]')
    elif 'DEPLOYMENT' in file_name.upper():
        metadata_lines.append('  - [[PRODUCTION_RELEASE_GUIDE]]')
    elif 'API' in file_name.upper():
        metadata_lines.append('  - [[INTEGRATION_GUIDE]]')
    
    metadata_lines.append('---')
    metadata_lines.append('')
    
    return '\n'.join(metadata_lines)

def process_file(file_path: str) -> bool:
    """Process a single file to add metadata."""
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has frontmatter
        if has_frontmatter(content):
            print(f"⏭️  SKIP: {os.path.basename(file_path)} (already has frontmatter)")
            return False
        
        # Generate metadata
        metadata = generate_metadata(file_path, content)
        
        # Combine metadata + content
        new_content = metadata + content
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ ADDED: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: {os.path.basename(file_path)} - {e}")
        return False

def main():
    """Main execution function."""
    developer_dir = Path(r"T:\Project-AI-main\docs\developer")
    
    # Find all markdown files
    all_files = list(developer_dir.rglob("*.md"))
    
    print(f"Found {len(all_files)} developer documentation files")
    print("=" * 80)
    
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    for file_path in sorted(all_files):
        result = process_file(str(file_path))
        if result is True:
            processed_count += 1
        elif result is False:
            skipped_count += 1
        else:
            error_count += 1
    
    print("=" * 80)
    print(f"\nSUMMARY:")
    print(f"  ✅ Processed: {processed_count}")
    print(f"  ⏭️  Skipped: {skipped_count}")
    print(f"  ❌ Errors: {error_count}")
    print(f"  📊 Total: {len(all_files)}")

if __name__ == "__main__":
    main()
