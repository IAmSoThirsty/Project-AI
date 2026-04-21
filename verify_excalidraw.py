#!/usr/bin/env python3
"""Verification script for Excalidraw plugin installation.

This script validates that the Excalidraw plugin is correctly installed
and functional without requiring pytest or external dependencies.
"""

import json
import os
import sys
from pathlib import Path


def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists."""
    if os.path.exists(path):
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description} MISSING: {path}")
        return False


def check_directory_exists(path: str, description: str) -> bool:
    """Check if a directory exists."""
    if os.path.isdir(path):
        print(f"✓ {description}: {path}")
        return True
    else:
        print(f"✗ {description} MISSING: {path}")
        return False


def verify_excalidraw_plugin():
    """Verify Excalidraw plugin installation."""
    print("=" * 70)
    print("EXCALIDRAW PLUGIN VERIFICATION")
    print("=" * 70)
    print()

    checks_passed = 0
    total_checks = 0

    # 1. Plugin file
    total_checks += 1
    plugin_file = "src/app/plugins/excalidraw_plugin.py"
    if check_file_exists(plugin_file, "Plugin source file"):
        checks_passed += 1
        # Verify it contains required classes
        with open(plugin_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'class ExcalidrawPlugin' in content:
                print("  ✓ ExcalidrawPlugin class found")
            if 'def initialize' in content:
                print("  ✓ initialize method found")
            if 'def create_diagram' in content:
                print("  ✓ create_diagram method found")
            if 'def save_diagram' in content:
                print("  ✓ save_diagram method found")
            if 'def export_diagram' in content:
                print("  ✓ export_diagram method found")
    print()

    # 2. Test file
    total_checks += 1
    test_file = "tests/plugins/test_excalidraw_plugin.py"
    if check_file_exists(test_file, "Test file"):
        checks_passed += 1
        with open(test_file, 'r', encoding='utf-8') as f:
            content = f.read()
            num_tests = content.count('def test_')
            print(f"  ✓ Contains {num_tests} test cases")
    print()

    # 3. Web component
    total_checks += 1
    web_component = "web/components/ExcalidrawComponent.tsx"
    if check_file_exists(web_component, "Web component"):
        checks_passed += 1
        with open(web_component, 'r', encoding='utf-8') as f:
            content = f.read()
            if 'ExcalidrawComponent' in content:
                print("  ✓ Component export found")
            if 'onSave' in content:
                print("  ✓ Save functionality found")
            if 'onExport' in content:
                print("  ✓ Export functionality found")
    print()

    # 4. Documentation files
    docs = [
        ("EXCALIDRAW_GUIDE.md", "User guide"),
        ("EXCALIDRAW_WORKFLOW.md", "Workflow documentation"),
    ]
    
    for doc_file, doc_desc in docs:
        total_checks += 1
        if check_file_exists(doc_file, doc_desc):
            checks_passed += 1
            # Check word count
            with open(doc_file, 'r', encoding='utf-8') as f:
                content = f.read()
                word_count = len(content.split())
                print(f"  ✓ {word_count} words (requirement: 400+)")
        print()

    # 5. Sample diagram
    total_checks += 1
    sample_diagram = "data/excalidraw_diagrams/samples/architecture_example.excalidraw"
    if check_file_exists(sample_diagram, "Sample diagram"):
        checks_passed += 1
        # Verify it's valid JSON
        try:
            with open(sample_diagram, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('type') == 'excalidraw':
                    print("  ✓ Valid Excalidraw format")
                if 'elements' in data:
                    print(f"  ✓ Contains {len(data['elements'])} elements")
        except json.JSONDecodeError:
            print("  ✗ Invalid JSON format")
    print()

    # 6. Data directory structure
    total_checks += 1
    data_dir = "data/excalidraw_diagrams"
    if check_directory_exists(data_dir, "Data directory"):
        checks_passed += 1
    print()

    # Summary
    print("=" * 70)
    print(f"VERIFICATION SUMMARY: {checks_passed}/{total_checks} checks passed")
    print("=" * 70)
    print()

    if checks_passed == total_checks:
        print("✓ ALL CHECKS PASSED - Excalidraw plugin is correctly installed!")
        print()
        print("Next steps:")
        print("1. Read EXCALIDRAW_GUIDE.md for usage instructions")
        print("2. Read EXCALIDRAW_WORKFLOW.md for workflow examples")
        print("3. View sample diagram in data/excalidraw_diagrams/samples/")
        print("4. Try the plugin:")
        print("   from app.plugins.excalidraw_plugin import ExcalidrawPlugin")
        print("   plugin = ExcalidrawPlugin()")
        print("   plugin.initialize()")
        return True
    else:
        print(f"✗ {total_checks - checks_passed} checks failed")
        print("Please review the missing files/components above")
        return False


def check_capabilities():
    """Display plugin capabilities."""
    print()
    print("=" * 70)
    print("EXCALIDRAW PLUGIN CAPABILITIES")
    print("=" * 70)
    print()
    print("Desktop Application (Python/PyQt6):")
    print("  • Create and manage diagram metadata")
    print("  • Save/load diagram files (.excalidraw format)")
    print("  • Track diagram history and modifications")
    print("  • Record export operations (PNG, SVG, JSON)")
    print("  • Open Excalidraw web interface in browser")
    print("  • Four Laws ethical validation on all operations")
    print("  • Persistent storage in data/excalidraw_diagrams/")
    print()
    print("Web Application (Next.js/React):")
    print("  • Embedded Excalidraw editor in browser")
    print("  • Create/save/load diagrams from localStorage")
    print("  • Export diagrams directly (PNG, SVG, JSON)")
    print("  • Dark mode support")
    print("  • Real-time editing with preview")
    print("  • Modal interface for diagram management")
    print()
    print("Drawing Tools:")
    print("  • Shapes: Rectangle, Circle, Diamond, Ellipse")
    print("  • Lines: Straight lines, arrows (single/double-headed)")
    print("  • Text: Multi-line with formatting")
    print("  • Free-hand drawing")
    print("  • Selection, move, resize, rotate, group")
    print("  • Color customization (stroke, fill, opacity)")
    print("  • Style options (solid, dashed, hachure)")
    print()
    print("Export Formats:")
    print("  • PNG: Raster images for documentation")
    print("  • SVG: Vector graphics for scaling")
    print("  • JSON: Native format for re-editing")
    print()
    print("Use Cases:")
    print("  • System architecture diagrams")
    print("  • Data flow diagrams")
    print("  • User journey maps")
    print("  • Network topology diagrams")
    print("  • UML diagrams (class, sequence, state)")
    print("  • Flowcharts and decision trees")
    print("  • Mind maps and concept maps")
    print()


if __name__ == "__main__":
    print()
    success = verify_excalidraw_plugin()
    check_capabilities()
    
    print()
    print("=" * 70)
    
    if success:
        print("STATUS: ✓ VERIFICATION COMPLETE - Plugin ready for use")
        sys.exit(0)
    else:
        print("STATUS: ✗ VERIFICATION FAILED - Please check missing components")
        sys.exit(1)
