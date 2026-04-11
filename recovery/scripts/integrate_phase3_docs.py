#!/usr/bin/env python3
"""
Phase 3 Documentation Reintegration
Reorganizes docs/ by module boundaries, integrating recovered files.
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Set
import re

# Constants
RECOVERY_DOCS = Path("recovery/docs/docs")
RECOVERY_ARCH = Path("recovery/architecture")
TARGET_DOCS = Path("docs")
TARGET_ARCH = Path("docs/architecture")
AUDIT_DIR = Path("audit")

# Module mapping (src/ to docs/architecture/)
MODULE_MAPPING = {
    "app": "APP_ARCHITECTURE.md",
    "cognition": "COGNITION_ARCHITECTURE.md",
    "data": "DATA_ARCHITECTURE.md",
    "features": "FEATURES_ARCHITECTURE.md",
    "governance": "GOVERNANCE_ARCHITECTURE.md",
    "integrations": "INTEGRATIONS_ARCHITECTURE.md",
    "interpreter": "INTERPRETER_ARCHITECTURE.md",
    "plugins": "PLUGINS_ARCHITECTURE.md",
    "psia": "PSIA_ARCHITECTURE.md",
    "security": "SECURITY_ARCHITECTURE.md",
    "shadow_thirst": "SHADOW_THIRST_ARCHITECTURE.md",
    "thirsty_lang": "THIRSTY_LANG_ARCHITECTURE.md",
}

def count_broken_links(file_path: Path) -> int:
    """Count broken links in a markdown file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        # Pattern for markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        links = re.findall(link_pattern, content)
        
        broken = 0
        for text, link in links:
            # Skip external links, anchors
            if link.startswith(('http://', 'https://', '#', 'mailto:')):
                continue
            
            # Check if local file exists
            if link.startswith('/'):
                target = Path(link.lstrip('/'))
            else:
                target = (file_path.parent / link).resolve()
            
            if not target.exists():
                broken += 1
        
        return broken
    except Exception as e:
        print(f"Warning: Could not check links in {file_path}: {e}")
        return 0

def integrate_recovery_docs() -> Dict:
    """Main integration function."""
    results = {
        "files_integrated": 0,
        "junk_deleted": 2,  # Already deleted in Phase 2
        "module_coverage": "0%",
        "broken_links_remaining": 0,
        "operations": {
            "copied_from_recovery_docs": 0,
            "copied_from_recovery_arch": 0,
            "modules_with_docs": 0,
            "total_modules": len(MODULE_MAPPING)
        },
        "files": []
    }
    
    print("🚀 Phase 3 Documentation Reintegration Starting...")
    print("=" * 60)
    
    # Ensure target directories exist
    TARGET_DOCS.mkdir(parents=True, exist_ok=True)
    TARGET_ARCH.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Copy repaired files from recovery/docs/docs → docs/
    print("\n📁 Step 1: Copying 101 repaired files from recovery/docs...")
    if RECOVERY_DOCS.exists():
        copied_files = []
        for src_file in RECOVERY_DOCS.rglob("*"):
            if src_file.is_file():
                # Preserve directory structure relative to recovery/docs/docs
                rel_path = src_file.relative_to(RECOVERY_DOCS)
                dest_file = TARGET_DOCS / rel_path
                
                # Create parent directories
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(src_file, dest_file)
                copied_files.append(str(rel_path))
                results["operations"]["copied_from_recovery_docs"] += 1
                
                # Track file
                results["files"].append({
                    "path": str(rel_path),
                    "source": "recovery/docs",
                    "size_bytes": src_file.stat().st_size
                })
        
        print(f"   ✅ Copied {len(copied_files)} files from recovery/docs")
    else:
        print(f"   ⚠️  Warning: {RECOVERY_DOCS} not found")
    
    # Step 2: Copy new architecture docs from recovery/architecture → docs/architecture/
    print("\n📐 Step 2: Adding new architecture docs from recovery/architecture...")
    if RECOVERY_ARCH.exists():
        arch_files = []
        for src_file in RECOVERY_ARCH.glob("*.md"):
            if src_file.name != "PHASE_2_COMPLETION_REPORT.md":
                dest_file = TARGET_ARCH / src_file.name
                shutil.copy2(src_file, dest_file)
                arch_files.append(src_file.name)
                results["operations"]["copied_from_recovery_arch"] += 1
                
                # Track file
                results["files"].append({
                    "path": f"architecture/{src_file.name}",
                    "source": "recovery/architecture",
                    "size_bytes": src_file.stat().st_size
                })
        
        print(f"   ✅ Copied {len(arch_files)} architecture docs")
        print(f"   Files: {', '.join(arch_files[:5])}{'...' if len(arch_files) > 5 else ''}")
    else:
        print(f"   ⚠️  Warning: {RECOVERY_ARCH} not found")
    
    # Step 3: Verify module boundaries
    print("\n🔍 Step 3: Verifying module boundary coverage...")
    src_dir = Path("src")
    if src_dir.exists():
        existing_modules = [d.name for d in src_dir.iterdir() if d.is_dir() and not d.name.startswith(('_', '.'))]
        
        modules_with_docs = []
        for module, arch_doc in MODULE_MAPPING.items():
            arch_path = TARGET_ARCH / arch_doc
            if arch_path.exists():
                modules_with_docs.append(module)
                print(f"   ✅ {module:20s} ↔ {arch_doc}")
            else:
                print(f"   ⚠️  {module:20s} ↔ {arch_doc} (MISSING)")
        
        results["operations"]["modules_with_docs"] = len(modules_with_docs)
        coverage = (len(modules_with_docs) / len(MODULE_MAPPING)) * 100
        results["module_coverage"] = f"{coverage:.0f}%"
        
        print(f"\n   📊 Module Coverage: {len(modules_with_docs)}/{len(MODULE_MAPPING)} ({coverage:.0f}%)")
    else:
        print("   ⚠️  src/ directory not found")
    
    # Step 4: Count broken links in integrated files
    print("\n🔗 Step 4: Analyzing broken links in integrated documentation...")
    total_broken = 0
    checked_files = 0
    
    for md_file in TARGET_DOCS.rglob("*.md"):
        broken = count_broken_links(md_file)
        total_broken += broken
        checked_files += 1
    
    results["broken_links_remaining"] = total_broken
    print(f"   📊 Checked {checked_files} files, found {total_broken} broken links")
    
    # Calculate total files integrated
    results["files_integrated"] = (
        results["operations"]["copied_from_recovery_docs"] + 
        results["operations"]["copied_from_recovery_arch"]
    )
    
    # Step 5: Generate report
    print("\n📄 Step 5: Generating reintegration report...")
    report_path = AUDIT_DIR / "reintegration_docs.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"   ✅ Report saved to {report_path}")
    
    print("\n" + "=" * 60)
    print("✨ Phase 3 Documentation Reintegration COMPLETE")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   • Files integrated: {results['files_integrated']}")
    print(f"   • Junk deleted: {results['junk_deleted']} (from Phase 2)")
    print(f"   • Module coverage: {results['module_coverage']}")
    print(f"   • Broken links remaining: {results['broken_links_remaining']}")
    
    return results

if __name__ == "__main__":
    results = integrate_recovery_docs()
    
    # Exit with success
    exit(0)
