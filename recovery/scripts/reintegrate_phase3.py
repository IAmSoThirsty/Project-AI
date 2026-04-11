#!/usr/bin/env python3
"""
Phase 3: Reintegration Script
Moves validated files from recovery/ to proper locations and stages them
"""
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List


class ReintegrationManager:
    def __init__(self):
        self.recovery_path = Path("recovery")
        self.reintegration_map = {
            "files_moved": [],
            "files_staged": [],
            "errors": []
        }
        
    def prepare_target_directories(self):
        """Ensure target directories exist"""
        targets = [
            "docs/architecture",
            "docs/api",
            "docs/operations",
            "docs/runbooks",
            "API_SPECIFICATIONS",
            "scripts/recovery"
        ]
        
        for target in targets:
            Path(target).mkdir(parents=True, exist_ok=True)
            
    def move_api_specs(self) -> int:
        """Move API specifications to API_SPECIFICATIONS/"""
        print("\n[1/5] Moving API specifications...")
        count = 0
        
        api_source = self.recovery_path / "api_docs"
        if not api_source.exists():
            print("  ⚠️  No api_docs directory found")
            return 0
        
        for yaml_file in api_source.glob("*.yaml"):
            # Skip redundant files
            if "REDUNDANT" in yaml_file.name:
                print(f"  ⏭️  Skipping redundant: {yaml_file.name}")
                continue
            
            target = Path("API_SPECIFICATIONS") / yaml_file.name
            
            # Check if file already exists and is identical
            if target.exists():
                if target.read_bytes() == yaml_file.read_bytes():
                    print(f"  ✓ Already exists (identical): {yaml_file.name}")
                    continue
                else:
                    print(f"  ⚠️  Conflict: {yaml_file.name} - backing up existing")
                    backup = Path("API_SPECIFICATIONS") / f"{yaml_file.stem}.backup.yaml"
                    shutil.copy2(target, backup)
            
            shutil.copy2(yaml_file, target)
            self.reintegration_map["files_moved"].append({
                "source": str(yaml_file),
                "target": str(target),
                "type": "api_spec"
            })
            count += 1
            print(f"  ✅ Moved: {yaml_file.name}")
        
        print(f"  📊 Moved {count} API specifications")
        return count
    
    def move_architecture_docs(self) -> int:
        """Move architecture documentation to docs/architecture/"""
        print("\n[2/5] Moving architecture documentation...")
        count = 0
        
        arch_source = self.recovery_path / "architecture"
        if not arch_source.exists():
            print("  ⚠️  No architecture directory found")
            return 0
        
        for md_file in arch_source.glob("*.md"):
            # Skip phase markers
            if "PHASE_2" in md_file.name:
                continue
            
            target = Path("docs/architecture") / md_file.name
            
            if target.exists():
                if target.read_bytes() == md_file.read_bytes():
                    print(f"  ✓ Already exists (identical): {md_file.name}")
                    continue
            
            shutil.copy2(md_file, target)
            self.reintegration_map["files_moved"].append({
                "source": str(md_file),
                "target": str(target),
                "type": "architecture"
            })
            count += 1
            print(f"  ✅ Moved: {md_file.name}")
        
        print(f"  📊 Moved {count} architecture docs")
        return count
    
    def organize_recovered_docs(self) -> int:
        """Organize recovered documentation"""
        print("\n[3/5] Organizing recovered documentation...")
        count = 0
        
        docs_source = self.recovery_path / "docs" / "docs"
        if not docs_source.exists():
            print("  ⚠️  No docs/docs directory found")
            return 0
        
        # Map subdirectories to targets
        mapping = {
            "developer": "docs/developer",
            "operations": "docs/operations",
            "runbooks": "docs/runbooks",
            "architecture": "docs/architecture",
            "security_compliance": "docs/security_compliance",
            "governance": "docs/governance",
            "reports": "docs/reports"
        }
        
        for subdir, target_dir in mapping.items():
            source_dir = docs_source / subdir
            if not source_dir.exists():
                continue
            
            Path(target_dir).mkdir(parents=True, exist_ok=True)
            
            for md_file in source_dir.rglob("*.md"):
                rel_path = md_file.relative_to(source_dir)
                target = Path(target_dir) / rel_path
                target.parent.mkdir(parents=True, exist_ok=True)
                
                if target.exists():
                    if target.read_bytes() == md_file.read_bytes():
                        continue
                
                shutil.copy2(md_file, target)
                self.reintegration_map["files_moved"].append({
                    "source": str(md_file),
                    "target": str(target),
                    "type": "documentation"
                })
                count += 1
        
        print(f"  📊 Organized {count} documentation files")
        return count
    
    def move_runbooks(self) -> int:
        """Move runbooks to docs/runbooks/"""
        print("\n[4/5] Moving runbooks...")
        count = 0
        
        runbooks_source = self.recovery_path / "runbooks"
        if not runbooks_source.exists():
            print("  ⚠️  No runbooks directory found")
            return 0
        
        for md_file in runbooks_source.rglob("*.md"):
            rel_path = md_file.relative_to(runbooks_source)
            target = Path("docs/runbooks") / rel_path
            target.parent.mkdir(parents=True, exist_ok=True)
            
            if target.exists():
                if target.read_bytes() == md_file.read_bytes():
                    continue
            
            shutil.copy2(md_file, target)
            self.reintegration_map["files_moved"].append({
                "source": str(md_file),
                "target": str(target),
                "type": "runbook"
            })
            count += 1
            print(f"  ✅ Moved: {md_file.name}")
        
        print(f"  📊 Moved {count} runbooks")
        return count
    
    def update_gitignore(self):
        """Update .gitignore with junk patterns"""
        print("\n[5/5] Updating .gitignore...")
        
        junk_patterns = [
            "",
            "# Phase 3 Recovery - Junk Patterns",
            "*.tmp",
            "*.temp",
            "*.bak",
            "*.swp",
            "*~",
            ".DS_Store",
            "Thumbs.db",
            "._*",
            "*.log",
            "*.cache",
            "",
            "# Recovery artifacts",
            "recovery/",
            "audit/*.db",
            "audit/temp_*.json",
            ""
        ]
        
        gitignore_path = Path(".gitignore")
        
        if gitignore_path.exists():
            content = gitignore_path.read_text(encoding='utf-8')
            
            # Check if patterns already exist
            if "# Phase 3 Recovery" in content:
                print("  ✓ .gitignore already updated")
                return
            
            # Append patterns
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write('\n'.join(junk_patterns))
            
            print("  ✅ Updated .gitignore with junk patterns")
        else:
            print("  ⚠️  No .gitignore found - creating one")
            gitignore_path.write_text('\n'.join(junk_patterns), encoding='utf-8')
    
    def save_reintegration_map(self):
        """Save reintegration map to audit/"""
        map_path = Path("audit/reintegration_map.json")
        map_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(map_path, 'w', encoding='utf-8') as f:
            json.dump(self.reintegration_map, f, indent=2)
        
        print(f"\n📄 Reintegration map saved to: {map_path}")
    
    def execute(self):
        """Execute full reintegration"""
        print("=" * 60)
        print("PHASE 3: REINTEGRATION")
        print("=" * 60)
        
        self.prepare_target_directories()
        
        api_count = self.move_api_specs()
        arch_count = self.move_architecture_docs()
        docs_count = self.organize_recovered_docs()
        runbooks_count = self.move_runbooks()
        self.update_gitignore()
        
        total_moved = api_count + arch_count + docs_count + runbooks_count
        
        self.reintegration_map["summary"] = {
            "total_files_moved": total_moved,
            "api_specs": api_count,
            "architecture_docs": arch_count,
            "documentation": docs_count,
            "runbooks": runbooks_count
        }
        
        self.save_reintegration_map()
        
        print("\n" + "=" * 60)
        print(f"✅ REINTEGRATION COMPLETE")
        print(f"   Total files moved: {total_moved}")
        print("=" * 60)
        
        return total_moved


def main():
    manager = ReintegrationManager()
    total = manager.execute()
    return 0 if total > 0 else 1


if __name__ == "__main__":
    exit(main())
