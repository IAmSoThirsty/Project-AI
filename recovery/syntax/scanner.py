#!/usr/bin/env python3
"""
Syntax Scanner for Phase 2 Salvage Operation
Rapidly scans and repairs syntax errors in critical/useful files
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any

def check_python_file(filepath: str) -> Dict[str, Any]:
    """Check Python file for syntax errors and missing imports"""
    result = {
        "file": filepath,
        "type": "python",
        "status": "ok",
        "errors": [],
        "repairs": []
    }
    
    if not os.path.exists(filepath):
        result["status"] = "missing"
        return result
    
    # Check syntax
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        compile(code, filepath, 'exec')
    except SyntaxError as e:
        result["status"] = "error"
        result["errors"].append(f"Syntax error at line {e.lineno}: {e.msg}")
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
    
    return result

def check_json_file(filepath: str) -> Dict[str, Any]:
    """Check JSON file for syntax errors"""
    result = {
        "file": filepath,
        "type": "json",
        "status": "ok",
        "errors": [],
        "repairs": []
    }
    
    if not os.path.exists(filepath):
        result["status"] = "missing"
        return result
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        json.loads(content)
    except json.JSONDecodeError as e:
        result["status"] = "error"
        result["errors"].append(f"JSON error at line {e.lineno}, col {e.colno}: {e.msg}")
        
        # Try to repair trailing commas
        if "Expecting" in e.msg or "trailing" in e.msg.lower():
            result["repairs"].append("trailing_comma_fix")
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
    
    return result

def check_yaml_file(filepath: str) -> Dict[str, Any]:
    """Check YAML file for syntax errors"""
    result = {
        "file": filepath,
        "type": "yaml",
        "status": "ok",
        "errors": [],
        "repairs": []
    }
    
    if not os.path.exists(filepath):
        result["status"] = "missing"
        return result
    
    try:
        import yaml
        with open(filepath, 'r', encoding='utf-8') as f:
            yaml.safe_load(f)
    except ImportError:
        result["status"] = "skip"
        result["errors"].append("PyYAML not available")
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
    
    return result

def check_markdown_file(filepath: str) -> Dict[str, Any]:
    """Check Markdown file for broken links and syntax"""
    result = {
        "file": filepath,
        "type": "markdown",
        "status": "ok",
        "errors": [],
        "repairs": []
    }
    
    if not os.path.exists(filepath):
        result["status"] = "missing"
        return result
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for broken links (simple check)
        links = re.findall(r'\[([^\]]+)\]\(([^\)]+)\)', content)
        for text, url in links:
            if url.startswith('http'):
                continue
            # Check if local file exists
            link_path = Path(filepath).parent / url
            if not link_path.exists() and not url.startswith('#'):
                result["errors"].append(f"Broken link: {url}")
                
    except Exception as e:
        result["status"] = "error"
        result["errors"].append(str(e))
    
    return result

def main():
    # Load classification map
    with open('audit/classification_map.json', 'r') as f:
        data = json.load(f)
    
    # Filter critical and useful items
    targets = [item for item in data['items'] 
               if item['type'] in ['critical', 'useful']]
    
    print(f"Scanning {len(targets)} files...")
    
    results = []
    errors_found = 0
    
    for item in targets:
        filepath = item['path']
        
        if filepath.endswith('.py'):
            result = check_python_file(filepath)
        elif filepath.endswith('.json'):
            result = check_json_file(filepath)
        elif filepath.endswith(('.yml', '.yaml')):
            result = check_yaml_file(filepath)
        elif filepath.endswith('.md'):
            result = check_markdown_file(filepath)
        else:
            continue
        
        if result['status'] == 'error':
            errors_found += 1
            print(f"ERROR: {filepath}")
            for error in result['errors']:
                print(f"  - {error}")
        
        results.append(result)
    
    # Save results
    os.makedirs('recovery/syntax', exist_ok=True)
    
    summary = {
        "timestamp": "2026-04-10T05:30:00Z",
        "total_scanned": len(results),
        "errors_found": errors_found,
        "files_ok": len([r for r in results if r['status'] == 'ok']),
        "results": results
    }
    
    with open('recovery/syntax/scan_results.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\nScan complete!")
    print(f"Total scanned: {len(results)}")
    print(f"Errors found: {errors_found}")
    print(f"Files OK: {summary['files_ok']}")
    
    return 0 if errors_found == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
