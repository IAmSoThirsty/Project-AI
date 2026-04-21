#!/usr/bin/env python3
"""
AGENT-075 Phase 2: Comprehensive Wiki Link Injection
Systematically adds hundreds of wiki links to all navigation sections and READMEs
"""

import re
from pathlib import Path
from typing import List, Tuple

class ComprehensiveLinkInjector:
    """Inject comprehensive wiki links across all documentation"""
    
    def __init__(self, root: Path):
        self.root = root
        self.links_added = 0
        
    def run(self) -> int:
        """Execute all link injection phases"""
        print("🚀 AGENT-075 Phase 2: Comprehensive Link Injection")
        print("="*70)
        
        # Phase 1: README navigation enhancements
        print("\n📚 Phase 1: Enhancing README navigation...")
        self._enhance_readmes()
        
        # Phase 2: Add comprehensive cross-references
        print("\n🔗 Phase 2: Adding comprehensive cross-references...")
        self._add_comprehensive_cross_refs()
        
        # Phase 3: Add source code navigation sections
        print("\n💻 Phase 3: Adding source code navigation...")
        self._add_source_nav_sections()
        
        # Phase 4: Inter-document linking
        print("\n↔️  Phase 4: Creating inter-document links...")
        self._create_inter_doc_links()
        
        print(f"\n✅ Total links added: {self.links_added}")
        return self.links_added
    
    def _enhance_readmes(self) -> None:
        """Enhance all README files with navigation sections"""
        readme_files = [
            'relationships/configuration/README.md',
            'relationships/deployment/README.md',
            'relationships/integrations/README.md',
            'source-docs/data-models/README.md',
            'source-docs/configuration/INDEX.md',
            'source-docs/deployment/README.md',
            'source-docs/integrations/README.md',
        ]
        
        for readme_path in readme_files:
            full_path = self.root / readme_path
            if not full_path.exists():
                continue
            
            self._add_nav_to_readme(full_path)
    
    def _add_nav_to_readme(self, readme_path: Path) -> None:
        """Add comprehensive navigation to a README"""
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Skip if already has comprehensive navigation
        if '## Quick Navigation' in content and content.count('[[') > 20:
            return
        
        # Build navigation based on directory
        nav_section = self._build_navigation_section(readme_path)
        
        if nav_section:
            # Add before "## Related Documentation" or at end
            if '## Related Documentation' in content:
                content = content.replace('## Related Documentation', 
                                        nav_section + '\n---\n\n## Related Documentation')
            else:
                content += '\n\n' + nav_section
            
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            links_in_section = nav_section.count('[[')
            self.links_added += links_in_section
            print(f"   ✅ {readme_path.name}: {links_in_section} links")
    
    def _build_navigation_section(self, readme_path: Path) -> str:
        """Build navigation section based on directory context"""
        rel_path = readme_path.relative_to(self.root)
        parent_dir = rel_path.parent
        
        nav = "---\n\n## Quick Navigation\n\n"
        
        # Get all markdown files in the directory
        md_files = sorted(readme_path.parent.glob('*.md'))
        md_files = [f for f in md_files if f.name not in ['README.md', 'INDEX.md']]
        
        if md_files:
            nav += "### Documentation in This Directory\n\n"
            for md_file in md_files:
                md_rel = md_file.relative_to(self.root)
                title = md_file.stem.replace('-', ' ').replace('_', ' ').title()
                nav += f"- **{title}**: [[{md_rel}]]\n"
            nav += "\n"
        
        # Add source code links based on directory
        source_files = self._get_relevant_source_files(parent_dir)
        if source_files:
            nav += "### Related Source Code\n\n"
            for src_file, description in source_files:
                if (self.root / src_file).exists():
                    nav += f"- **{description}**: [[{src_file}]]\n"
            nav += "\n"
        
        # Add related documentation links
        related_docs = self._get_related_docs(parent_dir)
        if related_docs:
            nav += "### Related Documentation\n\n"
            for doc_file, description in related_docs:
                if (self.root / doc_file).exists():
                    nav += f"- **{description}**: [[{doc_file}]]\n"
            nav += "\n"
        
        return nav
    
    def _get_relevant_source_files(self, directory: Path) -> List[Tuple[str, str]]:
        """Get relevant source files for a documentation directory"""
        sources = []
        
        dir_name = directory.name
        
        if 'data' in str(directory):
            sources = [
                ('src/app/core/ai_systems.py', 'AI Systems Core'),
                ('src/app/core/user_manager.py', 'User Manager'),
                ('src/app/core/data_persistence.py', 'Data Persistence'),
                ('src/app/core/cloud_sync.py', 'Cloud Sync'),
            ]
        elif 'configuration' in str(directory):
            sources = [
                ('src/app/core/config/settings.py', 'Settings Manager'),
                ('src/app/core/config/environment.py', 'Environment Configuration'),
                ('src/app/core/config/constants.py', 'Constants'),
            ]
        elif 'deployment' in str(directory):
            sources = [
                ('Dockerfile', 'Docker Configuration'),
                ('docker-compose.yml', 'Docker Compose'),
                ('.github/workflows/ci.yml', 'CI Pipeline'),
            ]
        elif 'integrations' in str(directory):
            sources = [
                ('src/app/core/intelligence_engine.py', 'Intelligence Engine'),
                ('src/app/core/learning_paths.py', 'Learning Paths'),
                ('src/app/core/image_generator.py', 'Image Generator'),
            ]
        
        return sources
    
    def _get_related_docs(self, directory: Path) -> List[Tuple[str, str]]:
        """Get related documentation for cross-referencing"""
        docs = []
        
        if 'relationships' in str(directory):
            # Link to source-docs
            if 'data' in str(directory):
                docs.append(('source-docs/data-models/00-index.md', 'Data Models Index'))
            elif 'configuration' in str(directory):
                docs.append(('source-docs/configuration/INDEX.md', 'Configuration Index'))
            elif 'deployment' in str(directory):
                docs.append(('source-docs/deployment/README.md', 'Deployment Documentation'))
            elif 'integrations' in str(directory):
                docs.append(('source-docs/integrations/README.md', 'Integration Documentation'))
        
        elif 'source-docs' in str(directory):
            # Link to relationships
            if 'data' in str(directory):
                docs.append(('relationships/data/README.md', 'Data Relationship Maps'))
            elif 'configuration' in str(directory):
                docs.append(('relationships/configuration/README.md', 'Configuration Relationships'))
            elif 'deployment' in str(directory):
                docs.append(('relationships/deployment/README.md', 'Deployment Relationships'))
            elif 'integrations' in str(directory):
                docs.append(('relationships/integrations/README.md', 'Integration Relationships'))
        
        # Add core documentation
        docs.extend([
            ('PROGRAM_SUMMARY.md', 'Program Summary'),
            ('DEVELOPER_QUICK_REFERENCE.md', 'Developer Quick Reference'),
        ])
        
        return docs
    
    def _add_comprehensive_cross_refs(self) -> None:
        """Add comprehensive cross-references to all documents"""
        doc_dirs = [
            'relationships/data',
            'relationships/configuration',
            'relationships/deployment',
            'relationships/integrations',
        ]
        
        for doc_dir in doc_dirs:
            dir_path = self.root / doc_dir
            if not dir_path.exists():
                continue
            
            for md_file in dir_path.glob('*.md'):
                if md_file.name in ['README.md', 'MISSION_COMPLETE.md']:
                    continue
                
                self._add_cross_refs_to_file(md_file)
    
    def _add_cross_refs_to_file(self, file_path: Path) -> None:
        """Add cross-references to a single file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Add navigation header if not present
        if '## Navigation' not in content and content.count('##') >= 3:
            # Insert after first section
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if line.startswith('## ') and i > 5:  # After initial headers
                    nav_header = self._build_file_nav_header(file_path)
                    lines.insert(i, nav_header)
                    break
            
            content = '\n'.join(lines)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            added = content.count('[[') - original_content.count('[[')
            if added > 0:
                self.links_added += added
    
    def _build_file_nav_header(self, file_path: Path) -> str:
        """Build navigation header for a file"""
        rel_path = file_path.relative_to(self.root)
        parent_dir = file_path.parent
        
        nav = "\n## Navigation\n\n"
        nav += f"**Location**: `{rel_path}`\n\n"
        
        # Link to parent README
        readme = parent_dir / 'README.md'
        if readme.exists():
            readme_rel = readme.relative_to(self.root)
            nav += f"**Parent**: [[{readme_rel}]]\n\n"
        
        return nav
    
    def _add_source_nav_sections(self) -> None:
        """Add source code navigation sections to source-docs"""
        source_docs_dirs = [
            'source-docs/data-models',
            'source-docs/configuration',
            'source-docs/deployment',
            'source-docs/integrations',
        ]
        
        for doc_dir in source_docs_dirs:
            dir_path = self.root / doc_dir
            if not dir_path.exists():
                continue
            
            for md_file in dir_path.glob('*.md'):
                if md_file.name in ['README.md', 'INDEX.md', 'MISSION_COMPLETE.md']:
                    continue
                
                self._add_source_nav_to_file(md_file)
    
    def _add_source_nav_to_file(self, file_path: Path) -> None:
        """Add source code navigation to a file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if '## Source Code References' in content:
            return  # Already has it
        
        # Extract module reference if present
        module_match = re.search(r'\*\*Module\*\*:\s*`([^`]+)`', content)
        
        if module_match:
            module_path = module_match.group(1)
            
            nav = "\n\n---\n\n## Source Code References\n\n"
            nav += f"- **Primary Module**: [[{module_path}]]\n"
            
            # Add related modules based on file name
            related = self._find_related_modules(file_path, module_path)
            if related:
                nav += "\n### Related Modules\n\n"
                for rel_module in related:
                    if (self.root / rel_module).exists():
                        nav += f"- [[{rel_module}]]\n"
            
            with open(file_path, 'a', encoding='utf-8') as f:
                f.write(nav)
            
            added = nav.count('[[')
            self.links_added += added
    
    def _find_related_modules(self, doc_file: Path, primary_module: str) -> List[str]:
        """Find related source modules"""
        related = []
        
        # Based on primary module directory
        if 'core' in primary_module:
            core_dir = self.root / 'src' / 'app' / 'core'
            if core_dir.exists():
                # Add ai_systems.py if relevant
                if any(x in doc_file.stem for x in ['ai', 'persona', 'memory', 'learning']):
                    related.append('src/app/core/ai_systems.py')
                
                # Add user_manager.py if relevant
                if any(x in doc_file.stem for x in ['user', 'auth', 'login']):
                    related.append('src/app/core/user_manager.py')
        
        return [r for r in related if r != primary_module]
    
    def _create_inter_doc_links(self) -> None:
        """Create links between related documents"""
        # This creates a comprehensive web of cross-references
        mappings = {
            'relationships/data': 'source-docs/data-models',
            'relationships/configuration': 'source-docs/configuration',
            'relationships/deployment': 'source-docs/deployment',
            'relationships/integrations': 'source-docs/integrations',
        }
        
        for rel_dir, source_dir in mappings.items():
            rel_path = self.root / rel_dir
            source_path = self.root / source_dir
            
            if not rel_path.exists() or not source_path.exists():
                continue
            
            # Get all files from both directories
            rel_files = list(rel_path.glob('*.md'))
            source_files = list(source_path.glob('*.md'))
            
            # Create mapping by shared keywords
            for rel_file in rel_files:
                if rel_file.name in ['README.md']:
                    continue
                
                for source_file in source_files:
                    if source_file.name in ['README.md', 'INDEX.md']:
                        continue
                    
                    # Check if they share keywords
                    rel_keywords = set(rel_file.stem.lower().split('-'))
                    source_keywords = set(source_file.stem.lower().split('-'))
                    
                    if len(rel_keywords & source_keywords) >= 2:
                        # They're related - ensure cross-links exist
                        self._ensure_bidirectional_link(rel_file, source_file)

    def _ensure_bidirectional_link(self, file1: Path, file2: Path) -> None:
        """Ensure bidirectional links exist between two files"""
        # Read both files
        with open(file1, 'r', encoding='utf-8') as f:
            content1 = f.read()
        
        with open(file2, 'r', encoding='utf-8') as f:
            content2 = f.read()
        
        file2_rel = str(file2.relative_to(self.root))
        file1_rel = str(file1.relative_to(self.root))
        
        # Check if file1 links to file2
        if file2_rel not in content1 and f'[[{file2_rel}]]' not in content1:
            # Add link in See Also or Related Documentation section
            if '## See Also' in content1:
                content1 = content1.replace('## See Also', 
                    f'## See Also\n\n- **{file2.stem.replace("-", " ").title()}**: [[{file2_rel}]]\n')
                self.links_added += 1
                
                with open(file1, 'w', encoding='utf-8') as f:
                    f.write(content1)
        
        # Check if file2 links to file1
        if file1_rel not in content2 and f'[[{file1_rel}]]' not in content2:
            if '## Related Documentation' in content2:
                content2 = content2.replace('## Related Documentation',
                    f'## Related Documentation\n\n- **{file1.stem.replace("-", " ").title()}**: [[{file1_rel}]]\n')
                self.links_added += 1
                
                with open(file2, 'w', encoding='utf-8') as f:
                    f.write(content2)

def main():
    """Main execution"""
    root = Path(__file__).parent
    injector = ComprehensiveLinkInjector(root)
    total = injector.run()
    
    print(f"\n{'='*70}")
    print(f"✅ Phase 2 Complete: {total} additional links added")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()
