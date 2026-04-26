#!/usr/bin/env python3
"""
AGENT-074 Phase 3: Cross-Document Navigation Links
Adds comprehensive cross-references between related documentation files
"""

import re
from pathlib import Path
from typing import Dict, List


class CrossDocLinker:
    """Add cross-document navigation links"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.links_added = 0
        
        # Cross-document relationship mapping
        self.cross_doc_links = {
            # GUI documentation cross-references
            "relationships/gui/00_MASTER_INDEX.md": [
                "relationships/gui/01_DASHBOARD_RELATIONSHIPS.md",
                "relationships/gui/02_PANEL_RELATIONSHIPS.md",
                "relationships/gui/03_HANDLER_RELATIONSHIPS.md",
                "relationships/gui/04_UTILS_RELATIONSHIPS.md",
                "relationships/gui/05_PERSONA_PANEL_RELATIONSHIPS.md",
                "relationships/gui/06_IMAGE_GENERATION_RELATIONSHIPS.md",
                "source-docs/gui/README.md",
            ],
            "relationships/gui/01_DASHBOARD_RELATIONSHIPS.md": [
                "source-docs/gui/leather_book_dashboard.md",
                "source-docs/gui/leather_book_interface.md",
                "relationships/gui/02_PANEL_RELATIONSHIPS.md",
            ],
            "relationships/gui/02_PANEL_RELATIONSHIPS.md": [
                "source-docs/gui/leather_book_dashboard.md",
                "relationships/gui/01_DASHBOARD_RELATIONSHIPS.md",
            ],
            "relationships/gui/03_HANDLER_RELATIONSHIPS.md": [
                "source-docs/gui/dashboard_handlers.md",
                "relationships/gui/01_DASHBOARD_RELATIONSHIPS.md",
            ],
            "relationships/gui/04_UTILS_RELATIONSHIPS.md": [
                "source-docs/gui/dashboard_utils.md",
            ],
            "relationships/gui/05_PERSONA_PANEL_RELATIONSHIPS.md": [
                "source-docs/gui/persona_panel.md",
            ],
            "relationships/gui/06_IMAGE_GENERATION_RELATIONSHIPS.md": [
                "source-docs/gui/image_generation.md",
            ],
            
            # Temporal documentation cross-references
            "relationships/temporal/README.md": [
                "relationships/temporal/01_WORKFLOW_CHAINS.md",
                "relationships/temporal/02_ACTIVITY_DEPENDENCIES.md",
                "relationships/temporal/03_TEMPORAL_INTEGRATION.md",
                "relationships/temporal/04_TEMPORAL_GOVERNANCE.md",
                "source-docs/temporal/README.md",
            ],
            "relationships/temporal/01_WORKFLOW_CHAINS.md": [
                "source-docs/temporal/WORKFLOWS_COMPREHENSIVE.md",
                "relationships/temporal/02_ACTIVITY_DEPENDENCIES.md",
            ],
            "relationships/temporal/02_ACTIVITY_DEPENDENCIES.md": [
                "source-docs/temporal/ACTIVITIES_COMPREHENSIVE.md",
                "relationships/temporal/01_WORKFLOW_CHAINS.md",
            ],
            "relationships/temporal/03_TEMPORAL_INTEGRATION.md": [
                "source-docs/temporal/WORKER_CLIENT_COMPREHENSIVE.md",
            ],
            "relationships/temporal/04_TEMPORAL_GOVERNANCE.md": [
                "source-docs/temporal/WORKFLOWS_COMPREHENSIVE.md",
                "relationships/temporal/01_WORKFLOW_CHAINS.md",
            ],
            
            # Source doc to relationship maps
            "source-docs/gui/leather_book_dashboard.md": [
                "relationships/gui/01_DASHBOARD_RELATIONSHIPS.md",
                "relationships/gui/02_PANEL_RELATIONSHIPS.md",
            ],
            "source-docs/gui/leather_book_interface.md": [
                "relationships/gui/01_DASHBOARD_RELATIONSHIPS.md",
            ],
            "source-docs/gui/dashboard_handlers.md": [
                "relationships/gui/03_HANDLER_RELATIONSHIPS.md",
            ],
            "source-docs/gui/dashboard_utils.md": [
                "relationships/gui/04_UTILS_RELATIONSHIPS.md",
            ],
            "source-docs/gui/persona_panel.md": [
                "relationships/gui/05_PERSONA_PANEL_RELATIONSHIPS.md",
            ],
            "source-docs/gui/image_generation.md": [
                "relationships/gui/06_IMAGE_GENERATION_RELATIONSHIPS.md",
            ],
            "source-docs/temporal/WORKFLOWS_COMPREHENSIVE.md": [
                "relationships/temporal/01_WORKFLOW_CHAINS.md",
                "relationships/temporal/04_TEMPORAL_GOVERNANCE.md",
            ],
            "source-docs/temporal/ACTIVITIES_COMPREHENSIVE.md": [
                "relationships/temporal/02_ACTIVITY_DEPENDENCIES.md",
            ],
            "source-docs/temporal/WORKER_CLIENT_COMPREHENSIVE.md": [
                "relationships/temporal/03_TEMPORAL_INTEGRATION.md",
            ],
        }
        
        # Architecture documentation references
        self.arch_doc_links = [
            "PROGRAM_SUMMARY.md",
            "DEVELOPER_QUICK_REFERENCE.md",
            ".github/instructions/ARCHITECTURE_QUICK_REF.md",
            "DESKTOP_APP_QUICKSTART.md",
        ]
    
    def process_all(self):
        """Add cross-document navigation links"""
        print("🚀 AGENT-074 Phase 3: Cross-document linking...")
        
        for source_doc, target_docs in self.cross_doc_links.items():
            self._add_nav_links(source_doc, target_docs)
        
        print(f"\n✅ Total cross-doc links added: {self.links_added}")
        return self.links_added
    
    def _add_nav_links(self, source_doc: str, target_docs: List[str]):
        """Add navigation links to related documentation"""
        source_path = self.base_path / source_doc
        
        if not source_path.exists():
            return
        
        print(f"  📝 {source_path.name}...")
        
        with open(source_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_links = 0
        
        # Check if "Related Documentation" section exists
        if "## 📚 Related Documentation" in content or "## Related Documentation" in content:
            # Section exists - add links to it
            section_pattern = r'(## 📚 Related Documentation|## Related Documentation)\s*\n'
            match = re.search(section_pattern, content)
            
            if match:
                insertion_point = match.end()
                
                # Check which links are not already there
                new_links = []
                for target_doc in target_docs:
                    # Check if this link already exists
                    link_pattern = rf'\[\[{re.escape(target_doc)}\]\]'
                    if not re.search(link_pattern, content):
                        new_links.append(target_doc)
                
                if new_links:
                    # Build new link section
                    link_text = "\n### Cross-References\n\n"
                    for target_doc in new_links:
                        # Get friendly name from file path
                        friendly_name = Path(target_doc).stem.replace('_', ' ').replace('-', ' ').title()
                        link_text += f"- [[{target_doc}|{friendly_name}]]\n"
                        file_links += 1
                        self.links_added += 1
                    
                    # Insert links
                    content = content[:insertion_point] + link_text + content[insertion_point:]
        else:
            # Section doesn't exist - create it before final sections
            insertion_patterns = [
                r'\n## 🔗 Source Code References',
                r'\n## Source Code References',
                r'\n## 📝 Maintenance Notes',
                r'\n## ✅ Completion',
                r'\n---\n\*\*Generated by',
                r'\n---\n\*\*End of',
            ]
            
            insertion_point = len(content)
            for pattern in insertion_patterns:
                match = re.search(pattern, content)
                if match:
                    insertion_point = match.start()
                    break
            
            # Build new section
            section_text = "\n\n---\n\n## 📚 Related Documentation\n\n"
            section_text += "### Cross-References\n\n"
            
            for target_doc in target_docs:
                # Get friendly name from file path
                friendly_name = Path(target_doc).stem.replace('_', ' ').replace('-', ' ').title()
                section_text += f"- [[{target_doc}|{friendly_name}]]\n"
                file_links += 1
                self.links_added += 1
            
            # Insert section
            content = content[:insertion_point] + section_text + content[insertion_point:]
        
        # Write back if changes were made
        if content != original_content:
            with open(source_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"    ✅ {file_links} links added")
        else:
            print(f"    ⚠️  No new links added")


def main():
    linker = CrossDocLinker()
    total = linker.process_all()
    
    print("\n" + "="*70)
    print("🎯 Phase 3 Complete")
    print("="*70)
    print(f"✅ Total cross-doc links added: {total}")
    print("="*70)


if __name__ == "__main__":
    main()
