#!/usr/bin/env python3
"""
Module Status Annotation Tool

Adds STATUS headers to Python modules to indicate maturity level.

Status Levels:
- SOLID: Fully functional, tested, production-ready
- PARTIAL: Works but incomplete, has TODOs/limitations  
- STUB: Minimal implementation, not functional
- DESIGN: Design/spec only, no working code

Usage:
    python annotate_modules.py --status SOLID --files "src/app/cli.py,src/cognition/triumvirate.py"
    python annotate_modules.py --scan src/app/core/  # Analyze and suggest
"""

import argparse
import re
from datetime import datetime
from pathlib import Path
from typing import Literal

StatusLevel = Literal["SOLID", "PARTIAL", "STUB", "DESIGN"]


def count_todos(filepath: Path) -> int:
    """Count TODO/FIXME markers in a file."""
    content = filepath.read_text(encoding="utf-8", errors="ignore")
    return len(re.findall(r"#\s*(TODO|FIXME)", content, re.IGNORECASE))


def has_tests(filepath: Path) -> bool:
    """Check if file has corresponding tests."""
    test_file = filepath.parent.parent.parent / "tests" / f"test_{filepath.stem}.py"
    return test_file.exists()


def analyze_file(filepath: Path) -> dict:
    """Analyze a Python file to suggest status level."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")
        
        # Count various indicators
        todo_count = count_todos(filepath)
        has_classes = bool(re.search(r"^class\s+\w+", content, re.MULTILINE))
        has_functions = bool(re.search(r"^def\s+\w+", content, re.MULTILINE))
        has_main = "__main__" in content
        line_count = len([l for l in lines if l.strip() and not l.strip().startswith("#")])
        has_imports = bool(re.search(r"^import\s+|^from\s+", content, re.MULTILINE))
        
        # Suggest status
        if line_count < 20 and (not has_classes and not has_functions):
            suggested = "STUB"
        elif todo_count > 5 or not has_imports:
            suggested = "PARTIAL"
        elif has_tests(filepath) and has_classes:
            suggested = "SOLID"
        elif line_count > 100 and has_classes:
            suggested = "PARTIAL"
        else:
            suggested = "PARTIAL"
        
        return {
            "path": str(filepath),
            "todos": todo_count,
            "has_classes": has_classes,
            "has_functions": has_functions,
            "has_main": has_main,
            "lines": line_count,
            "suggested_status": suggested,
            "has_tests": has_tests(filepath),
        }
    except Exception as e:
        return {"path": str(filepath), "error": str(e)}


def add_status_header(filepath: Path, status: StatusLevel, dependencies: str = ""):
    """Add or update STATUS header in a Python file."""
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
        lines = content.split("\n")
        
        # Remove existing STATUS header if present
        lines = [l for l in lines if not l.startswith("# STATUS:")]
        
        # Find where to insert (after shebang/encoding, before docstring)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("#!") or "coding" in line or "# -*-" in line:
                insert_idx = i + 1
                continue
            if line.strip() and not line.startswith("#"):
                break
            insert_idx = i + 1
        
        # Create status header
        header_lines = [
            f"# STATUS: {status}",
            f"# Last verified: {datetime.now().strftime('%Y-%m-%d')}",
        ]
        if dependencies:
            header_lines.append(f"# Dependencies: {dependencies}")
        header_lines.append("")
        
        # Insert header
        for i, line in enumerate(header_lines):
            lines.insert(insert_idx + i, line)
        
        # Write back
        filepath.write_text("\n".join(lines), encoding="utf-8")
        return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Module Status Annotation Tool")
    parser.add_argument("--status", choices=["SOLID", "PARTIAL", "STUB", "DESIGN"])
    parser.add_argument("--files", help="Comma-separated list of files to annotate")
    parser.add_argument("--scan", help="Directory to scan and suggest status")
    parser.add_argument("--dependencies", default="", help="Dependencies to note")
    
    args = parser.parse_args()
    
    if args.scan:
        # Scan and suggest
        scan_path = Path(args.scan)
        files = list(scan_path.rglob("*.py"))
        print(f"\nAnalyzing {len(files)} files in {scan_path}...")
        
        results = [analyze_file(f) for f in files if "__pycache__" not in str(f)]
        
        # Group by suggested status
        by_status = {}
        for r in results:
            if "error" in r:
                continue
            status = r["suggested_status"]
            by_status.setdefault(status, []).append(r)
        
        for status in ["SOLID", "PARTIAL", "STUB", "DESIGN"]:
            if status in by_status:
                print(f"\n{status}: {len(by_status[status])} files")
                for r in by_status[status][:5]:  # Show first 5
                    print(f"  {r['path']} (TODOs: {r['todos']}, Lines: {r['lines']})")
    
    elif args.files and args.status:
        # Annotate specified files
        files = [Path(f.strip()) for f in args.files.split(",")]
        success = 0
        for filepath in files:
            if filepath.exists():
                if add_status_header(filepath, args.status, args.dependencies):
                    print(f"✓ Annotated {filepath} as {args.status}")
                    success += 1
            else:
                print(f"✗ File not found: {filepath}")
        print(f"\nAnnotated {success}/{len(files)} files")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
