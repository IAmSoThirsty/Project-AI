#!/usr/bin/env python3
"""
Code Comments Coverage Analyzer
Scans Python, JavaScript, and TypeScript files to analyze comment coverage
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Directories to exclude
EXCLUDE_DIRS = {
    '.venv', '.venv_prod', 'node_modules', '.next', 'venv', 'env',
    '__pycache__', '.git', 'build', 'dist', 'archive', 'external',
    '.pytest_cache', 'coverage', '.mypy_cache'
}

# File patterns to exclude
EXCLUDE_PATTERNS = {
    'test', 'spec', '__init__.py', 'conftest.py', 
    '.min.js', '.bundle.js', 'vendor', 'lib/site-packages'
}

def should_exclude_file(file_path: str) -> bool:
    """Check if file should be excluded from analysis"""
    path_parts = file_path.split(os.sep)
    
    # Check for excluded directories
    if any(excluded in path_parts for excluded in EXCLUDE_DIRS):
        return True
    
    # Check for excluded patterns
    file_name = os.path.basename(file_path)
    if any(pattern in file_name.lower() for pattern in EXCLUDE_PATTERNS):
        return True
    
    return False

def analyze_python_file(file_path: str) -> Dict:
    """Analyze Python file for docstrings and comments"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}
    
    # Count functions and methods
    func_pattern = r'^\s*(def|async\s+def)\s+(\w+)\s*\('
    functions = re.findall(func_pattern, content, re.MULTILINE)
    func_count = len(functions)
    
    # Count classes
    class_pattern = r'^\s*class\s+(\w+)'
    classes = re.findall(class_pattern, content, re.MULTILINE)
    class_count = len(classes)
    
    # Count docstrings (triple quotes after def/class)
    docstring_pattern = r'(def|class)\s+\w+[^:]*:\s*\n\s*(""".*?"""|\'\'\'.*?\'\'\')'
    docstrings = re.findall(docstring_pattern, content, re.DOTALL)
    docstring_count = len(docstrings)
    
    # Count inline comments
    inline_comments = len(re.findall(r'^\s*#[^!]', content, re.MULTILINE))
    
    # Count TODO/FIXME
    todos = len(re.findall(r'#\s*(TODO|FIXME|XXX|HACK)', content, re.IGNORECASE))
    
    # Count commented code blocks (lines starting with # that look like code)
    commented_code = len(re.findall(r'^\s*#\s*(def|class|import|from|if|for|while|return)', content, re.MULTILINE))
    
    return {
        'functions': func_count,
        'classes': class_count,
        'documented': docstring_count,
        'inline_comments': inline_comments,
        'todos': todos,
        'commented_code': commented_code
    }

def analyze_javascript_file(file_path: str) -> Dict:
    """Analyze JavaScript/TypeScript file for JSDoc and comments"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        return {'error': str(e)}
    
    # Count functions (regular, arrow, async)
    func_patterns = [
        r'^\s*function\s+\w+\s*\(',
        r'^\s*(const|let|var)\s+\w+\s*=\s*(async\s+)?\([^)]*\)\s*=>',
        r'^\s*async\s+function\s+\w+\s*\(',
        r'^\s*\w+\s*\([^)]*\)\s*\{',  # method definitions
    ]
    func_count = sum(len(re.findall(pattern, content, re.MULTILINE)) for pattern in func_patterns)
    
    # Count React components
    component_pattern = r'(export\s+)?(const|function)\s+([A-Z]\w+)\s*[=:].*?(?:React\.FC|FunctionComponent|\([^)]*\)\s*(?::|=>))'
    components = re.findall(component_pattern, content, re.DOTALL)
    func_count += len(components)
    
    # Count JSDoc comments
    jsdoc_pattern = r'/\*\*.*?\*/'
    jsdocs = re.findall(jsdoc_pattern, content, re.DOTALL)
    jsdoc_count = len(jsdocs)
    
    # Count inline comments
    inline_comments = len(re.findall(r'^\s*//', content, re.MULTILINE))
    
    # Count TODO/FIXME
    todos = len(re.findall(r'/[/*]\s*(TODO|FIXME|XXX|HACK)', content, re.IGNORECASE))
    
    # Count commented code blocks
    commented_code = len(re.findall(r'^\s*//\s*(function|const|let|var|if|for|while|return|import)', content, re.MULTILINE))
    
    return {
        'functions': func_count,
        'documented': jsdoc_count,
        'inline_comments': inline_comments,
        'todos': todos,
        'commented_code': commented_code
    }

def scan_repository() -> Dict:
    """Scan entire repository for comment coverage"""
    results = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_files_scanned': 0,
            'python': {'files': 0, 'functions': 0, 'classes': 0, 'documented': 0, 'coverage_pct': 0},
            'javascript': {'files': 0, 'functions': 0, 'documented': 0, 'coverage_pct': 0},
            'typescript': {'files': 0, 'functions': 0, 'documented': 0, 'coverage_pct': 0}
        },
        'todos_fixmes': {'count': 0, 'files': []},
        'commented_code_blocks': {'count': 0, 'files': []},
        'details': {
            'python': [],
            'javascript': [],
            'typescript': []
        }
    }
    
    root_dir = Path('.')
    
    # Scan Python files
    print("Scanning Python files...")
    for py_file in root_dir.rglob('*.py'):
        file_path = str(py_file)
        if should_exclude_file(file_path):
            continue
        
        analysis = analyze_python_file(file_path)
        if 'error' in analysis:
            continue
        
        # Only include files with actual code
        if analysis['functions'] > 0 or analysis['classes'] > 0:
            results['details']['python'].append({
                'file': file_path,
                **analysis
            })
            results['summary']['python']['files'] += 1
            results['summary']['python']['functions'] += analysis['functions']
            results['summary']['python']['classes'] += analysis['classes']
            results['summary']['python']['documented'] += analysis['documented']
            
            if analysis['todos'] > 0:
                results['todos_fixmes']['count'] += analysis['todos']
                results['todos_fixmes']['files'].append(file_path)
            
            if analysis['commented_code'] > 0:
                results['commented_code_blocks']['count'] += analysis['commented_code']
                results['commented_code_blocks']['files'].append(file_path)
    
    # Scan JavaScript files
    print("Scanning JavaScript files...")
    for js_file in root_dir.rglob('*.js'):
        file_path = str(js_file)
        if should_exclude_file(file_path):
            continue
        
        analysis = analyze_javascript_file(file_path)
        if 'error' in analysis or analysis['functions'] == 0:
            continue
        
        results['details']['javascript'].append({
            'file': file_path,
            **analysis
        })
        results['summary']['javascript']['files'] += 1
        results['summary']['javascript']['functions'] += analysis['functions']
        results['summary']['javascript']['documented'] += analysis['documented']
        
        if analysis['todos'] > 0:
            results['todos_fixmes']['count'] += analysis['todos']
            results['todos_fixmes']['files'].append(file_path)
        
        if analysis['commented_code'] > 0:
            results['commented_code_blocks']['count'] += analysis['commented_code']
            results['commented_code_blocks']['files'].append(file_path)
    
    # Scan TypeScript files
    print("Scanning TypeScript files...")
    for ts_file in list(root_dir.rglob('*.ts')) + list(root_dir.rglob('*.tsx')):
        file_path = str(ts_file)
        if should_exclude_file(file_path):
            continue
        
        analysis = analyze_javascript_file(file_path)
        if 'error' in analysis or analysis['functions'] == 0:
            continue
        
        results['details']['typescript'].append({
            'file': file_path,
            **analysis
        })
        results['summary']['typescript']['files'] += 1
        results['summary']['typescript']['functions'] += analysis['functions']
        results['summary']['typescript']['documented'] += analysis['documented']
        
        if analysis['todos'] > 0:
            results['todos_fixmes']['count'] += analysis['todos']
            results['todos_fixmes']['files'].append(file_path)
        
        if analysis['commented_code'] > 0:
            results['commented_code_blocks']['count'] += analysis['commented_code']
            results['commented_code_blocks']['files'].append(file_path)
    
    # Calculate coverage percentages
    for lang in ['python', 'javascript', 'typescript']:
        total_items = results['summary'][lang]['functions']
        if lang == 'python':
            total_items += results['summary'][lang]['classes']
        
        if total_items > 0:
            documented = results['summary'][lang]['documented']
            coverage = (documented / total_items) * 100
            results['summary'][lang]['coverage_pct'] = round(coverage, 2)
            results['summary'][lang]['undocumented'] = total_items - documented
        else:
            results['summary'][lang]['undocumented'] = 0
    
    results['summary']['total_files_scanned'] = (
        results['summary']['python']['files'] +
        results['summary']['javascript']['files'] +
        results['summary']['typescript']['files']
    )
    
    # Deduplicate file lists
    results['todos_fixmes']['files'] = list(set(results['todos_fixmes']['files']))
    results['commented_code_blocks']['files'] = list(set(results['commented_code_blocks']['files']))
    
    return results

def main():
    print("Starting code comments coverage analysis...")
    results = scan_repository()
    
    # Create audit directory if it doesn't exist
    os.makedirs('audit', exist_ok=True)
    
    # Write results to JSON file
    output_file = 'audit/comments_coverage.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Analysis complete!")
    print(f"✓ Results written to: {output_file}")
    print(f"\nSummary:")
    print(f"  Total files scanned: {results['summary']['total_files_scanned']}")
    print(f"  Python: {results['summary']['python']['files']} files, {results['summary']['python']['coverage_pct']}% coverage")
    print(f"  JavaScript: {results['summary']['javascript']['files']} files, {results['summary']['javascript']['coverage_pct']}% coverage")
    print(f"  TypeScript: {results['summary']['typescript']['files']} files, {results['summary']['typescript']['coverage_pct']}% coverage")
    print(f"  TODO/FIXME markers: {results['todos_fixmes']['count']}")
    print(f"  Commented code blocks: {results['commented_code_blocks']['count']}")

if __name__ == '__main__':
    main()
