#!/usr/bin/env python3
"""
Phase 1 Classifier: Tag all .md files with TYPE, STATE, CONFIDENCE
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

REPO_ROOT = Path(__file__).parent
AUDIT_DIR = REPO_ROOT / "audit"

# Classification rules
CRITICAL_PATTERNS = [
    r"^README\.md$",
    r"^SECURITY\.md$",
    r"^CONTRIBUTING\.md$",
    r"^LICENSE\.md$",
    r"^CODE_OF_CONDUCT\.md$",
    r"^API_SPECIFICATIONS/",
    r"^docs/architecture/",
    r"^docs/governance/",
    r"^governance/",
]

USEFUL_PATTERNS = [
    r"^TEAM_.*_REPORT\.md$",
    r"^TEAM_.*_DELIVERABLES.*\.md$",
    r"^TEAM_.*_COMPLETION_REPORT\.md$",
    r".*_AUDIT.*\.md$",
    r".*_SUMMARY\.md$",
    r"^docs/",
    r"^QUICKSTART\.md$",
    r"^INSTALL\.md$",
    r"^CHANGELOG\.md$",
    r"^P0_RUNBOOKS/",
    r"^The_Guide_Book\.md$",
]

JUNK_PATTERNS = [
    r"node_modules[/\\]",
    r"\.venv[/\\]",
    r"\.uv-",
    r"[/\\]vendor[/\\]",
    r"[/\\]build[/\\]",
    r"[/\\]dist[/\\]",
    r"\.gradle[/\\]",
    r"[/\\]target[/\\]",
    r"__pycache__[/\\]",
    r"site-packages[/\\]",
    r"\.git[/\\]",
    r"archive-v0[/\\]",
    r"\.cargo[/\\]",
    r"\.npm[/\\]",
]

REDUNDANT_KEYWORDS = [
    "backup",
    "copy",
    "old",
    "deprecated",
    "archive",
    "temp",
    "tmp",
]


def classify_file(file_path: str, file_info: Dict) -> Dict:
    """Classify a single .md file"""
    path_lower = file_path.lower()
    name_lower = Path(file_path).name.lower()
    
    # Initialize classification
    file_type = "useful"  # Default
    state = "unknown"
    confidence = 0.5
    reason = ""
    
    # Rule 1: JUNK - vendor directories
    for pattern in JUNK_PATTERNS:
        if re.search(pattern, file_path, re.IGNORECASE):
            file_type = "junk"
            state = "unknown"
            confidence = 1.0
            reason = f"Matches junk pattern: {pattern}"
            return {
                "path": file_path,
                "type": file_type,
                "state": state,
                "confidence": confidence,
                "reason": reason,
            }
    
    # Rule 2: CRITICAL - core docs
    for pattern in CRITICAL_PATTERNS:
        if re.search(pattern, file_path, re.IGNORECASE):
            file_type = "critical"
            confidence = 0.9
            
            # Check state based on file size and recent updates
            if file_info.get("Length", 0) > 1000:
                state = "complete"
                confidence = 0.95
                reason = f"Critical doc matching pattern: {pattern}, substantial content"
            elif file_info.get("Length", 0) > 100:
                state = "partial"
                confidence = 0.85
                reason = f"Critical doc matching pattern: {pattern}, minimal content"
            else:
                state = "broken"
                confidence = 0.9
                reason = f"Critical doc matching pattern: {pattern}, but file too small"
            
            return {
                "path": file_path,
                "type": file_type,
                "state": state,
                "confidence": confidence,
                "reason": reason,
            }
    
    # Rule 3: USEFUL - secondary docs
    for pattern in USEFUL_PATTERNS:
        if re.search(pattern, file_path, re.IGNORECASE):
            file_type = "useful"
            confidence = 0.8
            
            # Check state
            if file_info.get("Length", 0) > 2000:
                state = "complete"
                confidence = 0.85
                reason = f"Useful doc matching pattern: {pattern}, substantial content"
            elif file_info.get("Length", 0) > 500:
                state = "partial"
                confidence = 0.75
                reason = f"Useful doc matching pattern: {pattern}, moderate content"
            else:
                state = "unknown"
                confidence = 0.6
                reason = f"Useful doc matching pattern: {pattern}, limited content"
            
            return {
                "path": file_path,
                "type": file_type,
                "state": state,
                "confidence": confidence,
                "reason": reason,
            }
    
    # Rule 4: REDUNDANT - duplicates, backups
    for keyword in REDUNDANT_KEYWORDS:
        if keyword in path_lower:
            file_type = "redundant"
            state = "unknown"
            confidence = 0.8
            reason = f"Contains redundant keyword: {keyword}"
            return {
                "path": file_path,
                "type": file_type,
                "state": state,
                "confidence": confidence,
                "reason": reason,
            }
    
    # Default: useful but low confidence
    file_type = "useful"
    state = "unknown"
    confidence = 0.3
    reason = "Default classification - needs manual review"
    
    # Adjust based on file size
    if file_info.get("Length", 0) > 3000:
        state = "complete"
        confidence = 0.5
        reason = "Substantial content, likely complete"
    elif file_info.get("Length", 0) > 1000:
        state = "partial"
        confidence = 0.4
        reason = "Moderate content, possibly partial"
    elif file_info.get("Length", 0) < 100:
        state = "broken"
        confidence = 0.6
        reason = "Very small file, likely broken or stub"
    
    return {
        "path": file_path,
        "type": file_type,
        "state": state,
        "confidence": confidence,
        "reason": reason,
    }


def main():
    """Main classification workflow"""
    
    # Load inventory
    inventory_path = AUDIT_DIR / "md_files_inventory.json"
    print(f"Loading inventory from: {inventory_path}")
    
    with open(inventory_path, "r", encoding="utf-8") as f:
        inventory = json.load(f)
    
    total_files = len(inventory)
    print(f"Total files to classify: {total_files}")
    
    # Classify all files
    classified_files = []
    type_counts = {"critical": 0, "useful": 0, "redundant": 0, "junk": 0}
    state_counts = {"complete": 0, "partial": 0, "broken": 0, "unknown": 0}
    confidence_dist = {"high": 0, "medium": 0, "low": 0}
    
    for i, file_info in enumerate(inventory, 1):
        if i % 500 == 0:
            print(f"Processing file {i}/{total_files}...")
        
        rel_path = file_info.get("RelativePath", "")
        
        classification = classify_file(rel_path, file_info)
        classified_files.append(classification)
        
        # Update counts
        type_counts[classification["type"]] += 1
        state_counts[classification["state"]] += 1
        
        # Confidence distribution
        if classification["confidence"] >= 0.8:
            confidence_dist["high"] += 1
        elif classification["confidence"] >= 0.5:
            confidence_dist["medium"] += 1
        else:
            confidence_dist["low"] += 1
    
    # Group by type
    classified_by_type = {
        "critical": [f for f in classified_files if f["type"] == "critical"],
        "useful": [f for f in classified_files if f["type"] == "useful"],
        "redundant": [f for f in classified_files if f["type"] == "redundant"],
        "junk": [f for f in classified_files if f["type"] == "junk"],
    }
    
    # Create output
    output = {
        "total_files": total_files,
        "classified": {
            "critical": classified_by_type["critical"],
            "useful": classified_by_type["useful"],
            "redundant": classified_by_type["redundant"],
            "junk": classified_by_type["junk"],
        },
        "by_state": state_counts,
        "confidence_distribution": confidence_dist,
        "files": classified_files,
    }
    
    # Write output
    output_path = AUDIT_DIR / "classification_md.json"
    print(f"\nWriting classification to: {output_path}")
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print("\n" + "="*60)
    print("CLASSIFICATION SUMMARY")
    print("="*60)
    print(f"\nTotal files classified: {total_files}")
    print("\nBy TYPE:")
    for type_name, count in type_counts.items():
        pct = (count / total_files * 100) if total_files > 0 else 0
        print(f"  {type_name:12s}: {count:5d} ({pct:5.1f}%)")
    
    print("\nBy STATE:")
    for state_name, count in state_counts.items():
        pct = (count / total_files * 100) if total_files > 0 else 0
        print(f"  {state_name:12s}: {count:5d} ({pct:5.1f}%)")
    
    print("\nBy CONFIDENCE:")
    for conf_level, count in confidence_dist.items():
        pct = (count / total_files * 100) if total_files > 0 else 0
        print(f"  {conf_level:12s}: {count:5d} ({pct:5.1f}%)")
    
    print("\n" + "="*60)
    print(f"Classification complete! Output: {output_path}")
    print("="*60)


if __name__ == "__main__":
    main()
