#!/usr/bin/env python3
"""
God Tier Architecture Verification Script

Validates that Project-AI meets all criteria for God Tier architecture
with monolithic oversight for scope and knowledge.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class GodTierVerifier:
    """Verifies God Tier architecture criteria."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.results: Dict[str, List[Tuple[str, bool, str]]] = {
            "monolithic_density": [],
            "scope_oversight": [],
            "knowledge_oversight": [],
            "god_tier_components": []
        }
    
    def verify_monolithic_density(self) -> bool:
        """Verify monolithic density criteria."""
        print("\n🔍 Verifying Monolithic Density...")
        
        # Count Python files
        src_dir = self.repo_root / "src" / "app"
        py_files = list(src_dir.rglob("*.py"))
        py_count = len(py_files)
        
        test_result = py_count >= 200
        self.results["monolithic_density"].append((
            f"Python modules count: {py_count}",
            test_result,
            f"Expected: ≥200, Got: {py_count}"
        ))
        print(f"  {'✅' if test_result else '❌'} Python modules: {py_count}")
        
        # Count lines of code
        total_lines = 0
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except:
                pass
        
        test_result = total_lines >= 80000
        self.results["monolithic_density"].append((
            f"Total lines of code: {total_lines:,}",
            test_result,
            f"Expected: ≥80,000, Got: {total_lines:,}"
        ))
        print(f"  {'✅' if test_result else '❌'} Lines of code: {total_lines:,}")
        
        # Check for core systems
        core_dir = src_dir / "core"
        core_files = list(core_dir.glob("*.py")) if core_dir.exists() else []
        test_result = len(core_files) >= 10
        self.results["monolithic_density"].append((
            f"Core system modules: {len(core_files)}",
            test_result,
            f"Expected: ≥10, Got: {len(core_files)}"
        ))
        print(f"  {'✅' if test_result else '❌'} Core modules: {len(core_files)}")
        
        return all(result[1] for result in self.results["monolithic_density"])
    
    def verify_scope_oversight(self) -> bool:
        """Verify scope oversight components."""
        print("\n🔍 Verifying Scope Oversight...")
        
        # Check for CognitionKernel
        cognition_kernel = self.repo_root / "src" / "app" / "core" / "cognition_kernel.py"
        test_result = cognition_kernel.exists()
        self.results["scope_oversight"].append((
            "CognitionKernel (central routing)",
            test_result,
            f"File exists: {test_result}"
        ))
        print(f"  {'✅' if test_result else '❌'} CognitionKernel")
        
        # Check for OversightAgent
        oversight_agent = self.repo_root / "src" / "app" / "agents" / "oversight.py"
        test_result = oversight_agent.exists()
        self.results["scope_oversight"].append((
            "OversightAgent (monitoring)",
            test_result,
            f"File exists: {test_result}"
        ))
        print(f"  {'✅' if test_result else '❌'} OversightAgent")
        
        # Check for FourLaws in ai_systems
        ai_systems = self.repo_root / "src" / "app" / "core" / "ai_systems.py"
        has_fourlaws = False
        if ai_systems.exists():
            with open(ai_systems, 'r', encoding='utf-8') as f:
                content = f.read()
                has_fourlaws = "FourLaws" in content or "class FourLaws" in content
        
        self.results["scope_oversight"].append((
            "FourLaws (ethical scope)",
            has_fourlaws,
            f"Found in ai_systems.py: {has_fourlaws}"
        ))
        print(f"  {'✅' if has_fourlaws else '❌'} FourLaws")
        
        # Check for CommandOverride
        has_command_override = False
        if ai_systems.exists():
            with open(ai_systems, 'r', encoding='utf-8') as f:
                content = f.read()
                has_command_override = "CommandOverride" in content
        
        command_override_file = self.repo_root / "src" / "app" / "core" / "command_override.py"
        has_command_override = has_command_override or command_override_file.exists()
        
        self.results["scope_oversight"].append((
            "CommandOverride (admin control)",
            has_command_override,
            f"Found: {has_command_override}"
        ))
        print(f"  {'✅' if has_command_override else '❌'} CommandOverride")
        
        return all(result[1] for result in self.results["scope_oversight"])
    
    def verify_knowledge_oversight(self) -> bool:
        """Verify knowledge oversight components."""
        print("\n🔍 Verifying Knowledge Oversight...")
        
        # Check for KnowledgeCurator
        knowledge_curator = self.repo_root / "src" / "app" / "agents" / "knowledge_curator.py"
        test_result = knowledge_curator.exists()
        self.results["knowledge_oversight"].append((
            "KnowledgeCurator (central governance)",
            test_result,
            f"File exists: {test_result}"
        ))
        print(f"  {'✅' if test_result else '❌'} KnowledgeCurator")
        
        # Check for MemoryExpansionSystem in ai_systems
        ai_systems = self.repo_root / "src" / "app" / "core" / "ai_systems.py"
        has_memory = False
        if ai_systems.exists():
            with open(ai_systems, 'r', encoding='utf-8') as f:
                content = f.read()
                has_memory = "MemoryExpansionSystem" in content or "class MemoryExpansionSystem" in content
        
        self.results["knowledge_oversight"].append((
            "MemoryExpansionSystem (knowledge accumulation)",
            has_memory,
            f"Found in ai_systems.py: {has_memory}"
        ))
        print(f"  {'✅' if has_memory else '❌'} MemoryExpansionSystem")
        
        # Check for LearningRequestManager
        has_learning = False
        if ai_systems.exists():
            with open(ai_systems, 'r', encoding='utf-8') as f:
                content = f.read()
                has_learning = "LearningRequestManager" in content
        
        self.results["knowledge_oversight"].append((
            "LearningRequestManager (approval workflow)",
            has_learning,
            f"Found in ai_systems.py: {has_learning}"
        ))
        print(f"  {'✅' if has_learning else '❌'} LearningRequestManager")
        
        # Check for cybersecurity knowledge
        cybersec_knowledge = self.repo_root / "src" / "app" / "core" / "cybersecurity_knowledge.py"
        test_result = cybersec_knowledge.exists()
        self.results["knowledge_oversight"].append((
            "CybersecurityKnowledge (domain expertise)",
            test_result,
            f"File exists: {test_result}"
        ))
        print(f"  {'✅' if test_result else '❌'} CybersecurityKnowledge")
        
        return all(result[1] for result in self.results["knowledge_oversight"])
    
    def verify_god_tier_components(self) -> bool:
        """Verify God Tier component documentation."""
        print("\n🔍 Verifying God Tier Components...")
        
        # Check for God Tier documentation
        docs = [
            ("GOD_TIER_IMPLEMENTATION_SUMMARY_NEW.md", "God Tier System"),
            ("GOD_TIER_INTELLIGENCE_SYSTEM.md", "Intelligence System"),
            (".github/workflows/CODEX_DEUS_MONOLITH.md", "Codex Deus Monolith")
        ]
        
        for doc_file, doc_name in docs:
            doc_path = self.repo_root / doc_file
            test_result = doc_path.exists()
            self.results["god_tier_components"].append((
                f"{doc_name} documentation",
                test_result,
                f"File exists: {test_result}"
            ))
            print(f"  {'✅' if test_result else '❌'} {doc_name}")
        
        # Check for multi-modal components
        multimodal_files = [
            "src/app/core/voice_models.py",
            "src/app/core/visual_cue_models.py",
            "src/app/core/conversation_context_engine.py",
            "src/app/core/multimodal_fusion.py"
        ]
        
        multimodal_count = sum(1 for f in multimodal_files if (self.repo_root / f).exists())
        test_result = multimodal_count >= 2  # At least some multi-modal components
        self.results["god_tier_components"].append((
            f"Multi-modal components: {multimodal_count}/4",
            test_result,
            f"Found {multimodal_count} multi-modal files"
        ))
        print(f"  {'✅' if test_result else '❌'} Multi-modal components: {multimodal_count}/4")
        
        return all(result[1] for result in self.results["god_tier_components"])
    
    def generate_report(self) -> None:
        """Generate final verification report."""
        print("\n" + "=" * 80)
        print("GOD TIER ARCHITECTURE VERIFICATION REPORT")
        print("=" * 80)
        
        categories = {
            "monolithic_density": "MONOLITHIC DENSITY",
            "scope_oversight": "SCOPE OVERSIGHT",
            "knowledge_oversight": "KNOWLEDGE OVERSIGHT",
            "god_tier_components": "GOD TIER COMPONENTS"
        }
        
        all_passed = True
        
        for category, title in categories.items():
            print(f"\n{title}")
            print("-" * 80)
            
            results = self.results[category]
            passed = sum(1 for _, result, _ in results if result)
            total = len(results)
            
            for test_name, result, details in results:
                status = "✅ PASS" if result else "❌ FAIL"
                print(f"  {status}: {test_name}")
                if not result:
                    print(f"         {details}")
            
            category_passed = passed == total
            print(f"\n  Category Result: {passed}/{total} passed")
            
            if not category_passed:
                all_passed = False
        
        print("\n" + "=" * 80)
        print("FINAL VERDICT")
        print("=" * 80)
        
        if all_passed:
            print("\n✅ ✅ ✅  GOD TIER ARCHITECTURE VERIFIED  ✅ ✅ ✅")
            print("\nProject-AI IS God Tier Architected with Monolithical Oversight")
            print("for Scope and Knowledge.")
            print("\nAll verification criteria PASSED.")
        else:
            print("\n⚠️  VERIFICATION INCOMPLETE")
            print("\nSome criteria not met. Review failures above.")
        
        print("\n" + "=" * 80)
    
    def run_verification(self) -> bool:
        """Run all verification checks."""
        print("=" * 80)
        print("GOD TIER ARCHITECTURE VERIFICATION")
        print("=" * 80)
        print(f"\nRepository: {self.repo_root}")
        
        monolithic_ok = self.verify_monolithic_density()
        scope_ok = self.verify_scope_oversight()
        knowledge_ok = self.verify_knowledge_oversight()
        god_tier_ok = self.verify_god_tier_components()
        
        self.generate_report()
        
        return monolithic_ok and scope_ok and knowledge_ok and god_tier_ok


def main():
    """Main entry point."""
    # Determine repository root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent if script_dir.name == "scripts" else script_dir
    
    # Create verifier
    verifier = GodTierVerifier(repo_root)
    
    # Run verification
    success = verifier.run_verification()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
