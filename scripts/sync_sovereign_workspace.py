"""
Sovereign Workspace Synchronization Utility

This script propagates canonical specifications from Project-AI (the Monolith)
to other listed repositories in the sovereign workspace.

Canonical Specs:
- Identity & Meta-Identity
- Canonical Bundle & Constitutional Laws
- Governance & Audit Abstractions

Integration Pattern:
- Files are synced to a dedicated `core/specs/` or `integrated_specs/` directory.
- This maintain "native but removable" property.
"""

import os
import shutil
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Canonical Source Paths (relative to Project-AI root)
SOURCE_SPECS = {
    "identity": "src/app/core/identity.py",
    "meta_identity": "src/app/core/meta_identity.py",
    "canonical_bundle": "src/app/miniature_office/core/canonical_bundle.py",
    "governance": "src/app/core/governance.py",
    "domain_base": "src/app/core/domain_base.py",
}

# Target Repositories (Basenames)
TARGET_REPOS = [
    "Cerberus",
    "TTP",
    "The_Triumvirate",
    "Thirsty-Lang",
    "Thirstys-Projects-Miniature-Office",
    "Thirstys-waterfall",
]

def sync_repos(base_dir: Path):
    """Synchronize Project-AI specs to target repositories."""
    project_ai_root = base_dir / "Project-AI"
    
    if not project_ai_root.exists():
        logger.error(f"Project-AI root not found at {project_ai_root}")
        return

    for repo_name in TARGET_REPOS:
        target_root = base_dir / repo_name
        if not target_root.exists():
            logger.warning(f"Target repository {repo_name} not found at {target_root}. Skipping.")
            continue
            
        logger.info(f"Syncing specs to {repo_name}...")
        
        # Standardized integration path
        # For Thirsty-Lang and others, we use src/core/specs or similar
        # To be "native but removable", we create a unified 'integrated_specs' dir
        integration_dir = target_root / "src" / "core" / "integrated_specs"
        integration_dir.mkdir(parents=True, exist_ok=True)
        
        # Add a README to explain the removable nature
        readme_path = integration_dir / "README.md"
        readme_path.write_text(
            "# Integrated Canonical Specifications\n\n"
            "This directory contains canonical specifications synchronized from Project-AI.\n"
            "These files are intended to be used natively by this repository's logic.\n\n"
            "**Removability**: This directory and its contents can be safely removed if this "
            "repository needs to operate independently of the Project-AI monolith.\n"
        )

        for spec_name, rel_path in SOURCE_SPECS.items():
            src_path = project_ai_root / rel_path
            dst_path = integration_dir / os.path.basename(rel_path)
            
            if src_path.exists():
                shutil.copy2(src_path, dst_path)
                logger.info(f"  [+] Synced {spec_name} -> {dst_path.relative_to(target_root)}")
            else:
                logger.warning(f"  [!] Source spec {spec_name} not found at {src_path}")

    logger.info("Synchronization complete.")

if __name__ == "__main__":
    # Assuming the current working directory is the sovereign-repos folder
    # or parent of Project-AI
    repo_parent = Path("c:/Users/Quencher/.gemini/antigravity/scratch/sovereign-repos")
    sync_repos(repo_parent)
