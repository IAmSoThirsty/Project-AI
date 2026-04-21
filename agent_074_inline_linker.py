#!/usr/bin/env python3
"""
AGENT-074 Phase 2: Aggressive Inline Link Expansion
Adds comprehensive component-level inline links to reach ~300 target
"""

import re
from pathlib import Path
from typing import Dict, List


class InlineLinker:
    """Add comprehensive inline component links to documentation"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.links_added = 0
        
        # Comprehensive component mapping for GUI
        self.gui_components = {
            # Classes
            "LeatherBookInterface": "src/app/gui/leather_book_interface.py",
            "LeatherBookDashboard": "src/app/gui/leather_book_dashboard.py",
            "DashboardHandlers": "src/app/gui/dashboard_handlers.py",
            "DashboardErrorHandler": "src/app/gui/dashboard_utils.py",
            "AsyncWorker": "src/app/gui/dashboard_utils.py",
            "DashboardAsyncManager": "src/app/gui/dashboard_utils.py",
            "PersonaPanel": "src/app/gui/persona_panel.py",
            "ImageGenerationWorker": "src/app/gui/image_generation.py",
            "ImageGenerationLeftPanel": "src/app/gui/image_generation.py",
            "ImageGenerationRightPanel": "src/app/gui/image_generation.py",
            "StatsPanel": "src/app/gui/leather_book_dashboard.py",
            "ProactiveActionsPanel": "src/app/gui/leather_book_dashboard.py",
            "UserChatPanel": "src/app/gui/leather_book_dashboard.py",
            "AIResponsePanel": "src/app/gui/leather_book_dashboard.py",
            "AINeuralHead": "src/app/gui/leather_book_dashboard.py",
            "IntroInfoPage": "src/app/gui/leather_book_interface.py",
            
            # Core systems
            "AIPersona": "src/app/core/ai_systems.py",
            "FourLaws": "src/app/core/ai_systems.py",
            "MemoryExpansionSystem": "src/app/core/ai_systems.py",
            "LearningRequestManager": "src/app/core/ai_systems.py",
            "PluginManager": "src/app/core/ai_systems.py",
            "CommandOverrideSystem": "src/app/core/command_override.py",
            "ImageGenerator": "src/app/core/image_generator.py",
            "UserManager": "src/app/core/user_manager.py",
            
            # Functions/methods
            "sanitize_input": "src/app/security/data_validation.py",
            "validate_length": "src/app/security/data_validation.py",
            "validate_email": "src/app/security/data_validation.py",
            "get_desktop_adapter": "src/app/interfaces/desktop/integration.py",
        }
        
        # Comprehensive component mapping for Temporal
        self.temporal_components = {
            # Workflows
            "TriumvirateWorkflow": "temporal/workflows/triumvirate_workflow.py",
            "TriumvirateStepWorkflow": "temporal/workflows/triumvirate_workflow.py",
            "RedTeamCampaignWorkflow": "temporal/workflows/security_agent_workflows.py",
            "EnhancedRedTeamCampaignWorkflow": "temporal/workflows/enhanced_security_workflows.py",
            "CodeSecuritySweepWorkflow": "temporal/workflows/enhanced_security_workflows.py",
            "EnhancedCodeSecuritySweepWorkflow": "temporal/workflows/enhanced_security_workflows.py",
            "ConstitutionalMonitoringWorkflow": "temporal/workflows/enhanced_security_workflows.py",
            "EnhancedConstitutionalMonitoringWorkflow": "temporal/workflows/enhanced_security_workflows.py",
            "SafetyTestingWorkflow": "temporal/workflows/enhanced_security_workflows.py",
            "AILearningWorkflow": "temporal/workflows/activities.py",
            "ImageGenerationWorkflow": "temporal/workflows/activities.py",
            
            # Activities (top 20)
            "run_triumvirate_pipeline": "temporal/workflows/triumvirate_workflow.py",
            "validate_input_activity": "temporal/workflows/triumvirate_workflow.py",
            "run_codex_inference": "temporal/workflows/triumvirate_workflow.py",
            "run_galahad_reasoning": "temporal/workflows/triumvirate_workflow.py",
            "enforce_output_policy": "temporal/workflows/triumvirate_workflow.py",
            "run_red_team_campaign": "temporal/workflows/security_agent_activities.py",
            "run_red_team_attack": "temporal/workflows/security_agent_activities.py",
            "evaluate_attack": "temporal/workflows/security_agent_activities.py",
            "create_forensic_snapshot": "temporal/workflows/atomic_security_activities.py",
            "generate_sarif": "temporal/workflows/atomic_security_activities.py",
            "validate_learning_content": "temporal/workflows/activities.py",
            "request_human_approval": "temporal/workflows/activities.py",
            "store_knowledge": "temporal/workflows/activities.py",
            "update_memory_system": "temporal/workflows/activities.py",
            
            # Governance
            "TemporalLaw": "gradle_evolution/constitutional/temporal_law.py",
            "TemporalLawEnforcer": "gradle_evolution/constitutional/temporal_law.py",
            "PolicyEnforcementWorkflow": "temporal/workflows/enhanced_security_workflows.py",
        }
    
    def process_all(self):
        """Process all documentation and add comprehensive inline links"""
        print("🚀 AGENT-074 Phase 2: Aggressive inline linking...")
        
        # Process GUI docs
        gui_docs = [
            "relationships/gui/00_MASTER_INDEX.md",
            "relationships/gui/01_DASHBOARD_RELATIONSHIPS.md",
            "relationships/gui/02_PANEL_RELATIONSHIPS.md",
            "relationships/gui/03_HANDLER_RELATIONSHIPS.md",
            "relationships/gui/04_UTILS_RELATIONSHIPS.md",
            "relationships/gui/05_PERSONA_PANEL_RELATIONSHIPS.md",
            "relationships/gui/06_IMAGE_GENERATION_RELATIONSHIPS.md",
            "source-docs/gui/dashboard_handlers.md",
            "source-docs/gui/dashboard_utils.md",
            "source-docs/gui/image_generation.md",
            "source-docs/gui/leather_book_dashboard.md",
            "source-docs/gui/leather_book_interface.md",
            "source-docs/gui/persona_panel.md",
        ]
        
        for doc_file in gui_docs:
            self._add_inline_links(doc_file, self.gui_components, "GUI")
        
        # Process Temporal docs
        temporal_docs = [
            "relationships/temporal/README.md",
            "relationships/temporal/01_WORKFLOW_CHAINS.md",
            "relationships/temporal/02_ACTIVITY_DEPENDENCIES.md",
            "relationships/temporal/03_TEMPORAL_INTEGRATION.md",
            "relationships/temporal/04_TEMPORAL_GOVERNANCE.md",
            "source-docs/temporal/WORKFLOWS_COMPREHENSIVE.md",
            "source-docs/temporal/ACTIVITIES_COMPREHENSIVE.md",
            "source-docs/temporal/WORKER_CLIENT_COMPREHENSIVE.md",
        ]
        
        for doc_file in temporal_docs:
            self._add_inline_links(doc_file, self.temporal_components, "Temporal")
        
        print(f"\n✅ Total inline links added: {self.links_added}")
        return self.links_added
    
    def _add_inline_links(self, doc_file: str, components: Dict[str, str], domain: str):
        """Add inline links for all component references in a file"""
        doc_path = self.base_path / doc_file
        
        if not doc_path.exists():
            return
        
        print(f"  📝 {doc_path.name}...")
        
        with open(doc_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        file_links = 0
        
        # For each component, find all occurrences and link them
        for component, source_file in components.items():
            # Skip if file doesn't mention this component
            if component not in content:
                continue
            
            # Pattern: Find component name NOT already in a link
            # Match component in code blocks `Component`, bold **Component**, or plain Component
            # But NOT if followed by [[ (already linked)
            
            patterns = [
                # Match `Component` not followed by [[
                (rf'`{re.escape(component)}`(?!\s*\[\[)', f'`{component}` [[{source_file}]]'),
                # Match **Component** not followed by [[
                (rf'\*\*{re.escape(component)}\*\*(?!\s*\[\[)', f'**{component}** [[{source_file}]]'),
                # Match Component in lists/headings (word boundary)
                (rf'\b{re.escape(component)}\b(?![`\*\[])', f'{component} [[{source_file}]]'),
            ]
            
            for pattern, replacement in patterns:
                # Find all matches
                matches = list(re.finditer(pattern, content))
                
                if matches:
                    # Link up to first 3 occurrences to balance completeness with readability
                    for match in matches[:3]:
                        # Check if already in a link section or code block
                        start = match.start()
                        
                        # Skip if in a code fence
                        if self._is_in_code_block(content, start):
                            continue
                        
                        # Skip if already linked
                        if '[[' in content[max(0, start-10):start+10]:
                            continue
                        
                        # Add the link
                        matched_text = match.group(0)
                        content = content[:start] + replacement + content[match.end():]
                        file_links += 1
                        self.links_added += 1
                        
                        # Break after one successful link per pattern to avoid conflicts
                        break
        
        # Write back if changes were made
        if content != original_content:
            with open(doc_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"    ✅ {file_links} links added")
        else:
            print(f"    ⚠️  No new links added")
    
    def _is_in_code_block(self, content: str, position: int) -> bool:
        """Check if position is inside a code block (```...```)"""
        # Count code fences before this position
        before = content[:position]
        fence_count = before.count('```')
        
        # If odd number of fences, we're inside a code block
        return fence_count % 2 == 1


def main():
    linker = InlineLinker()
    total = linker.process_all()
    
    print("\n" + "="*70)
    print("🎯 Phase 2 Complete")
    print("="*70)
    print(f"✅ Total inline links added: {total}")
    print("="*70)


if __name__ == "__main__":
    main()
