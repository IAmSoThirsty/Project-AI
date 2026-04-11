#!/usr/bin/env python3
"""Create comprehensive summary of comments coverage"""

import json
import os

# Load the data
with open('audit/comments_coverage.json', 'r') as f:
    data = json.load(f)

# Exclude patterns for dependencies/libraries
exclude_patterns = [
    '.venv', 'venv', 'node_modules', '.next', '__pycache__',
    'site-packages', '.uv-', 'archive', 'external', '.pytest',
    'Lib\\site-packages', 'lib/python', 'cpython-'
]

def is_source_file(path):
    """Determine if file is actual source code"""
    return not any(pattern in path for pattern in exclude_patterns)

print("=" * 90)
print(" " * 20 + "CODE COMMENTS COVERAGE ANALYSIS")
print("=" * 90)
print(f"\nTimestamp: {data['timestamp']}")
print(f"Total files scanned: {data['summary']['total_files_scanned']:,}")

print("\n" + "=" * 90)
print("OVERALL COVERAGE (ALL FILES)")
print("=" * 90)

for lang in ['python', 'javascript', 'typescript']:
    lang_data = data['summary'][lang]
    print(f"\n{lang.upper()}:")
    print(f"  Files: {lang_data['files']:,}")
    if lang == 'python':
        print(f"  Functions: {lang_data['functions']:,}")
        print(f"  Classes: {lang_data['classes']:,}")
        total = lang_data['functions'] + lang_data['classes']
        print(f"  Total items: {total:,}")
    else:
        print(f"  Functions/Components: {lang_data['functions']:,}")
    print(f"  Documented: {lang_data['documented']:,}")
    print(f"  Undocumented: {lang_data['undocumented']:,}")
    print(f"  Coverage: {lang_data['coverage_pct']:.2f}%")

print("\n" + "=" * 90)
print("SOURCE CODE ONLY (EXCLUDING DEPENDENCIES)")
print("=" * 90)

for lang in ['python', 'javascript', 'typescript']:
    files = data['details'][lang]
    src_files = [f for f in files if is_source_file(f['file'])]
    
    if not src_files:
        continue
    
    print(f"\n{lang.upper()}:")
    print(f"  Source files: {len(src_files):,}")
    
    total_funcs = sum(f.get('functions', 0) for f in src_files)
    total_classes = sum(f.get('classes', 0) for f in src_files)
    total_docs = sum(f.get('documented', 0) for f in src_files)
    total_inline = sum(f.get('inline_comments', 0) for f in src_files)
    total_todos = sum(f.get('todos', 0) for f in src_files)
    total_commented = sum(f.get('commented_code', 0) for f in src_files)
    
    if lang == 'python':
        total_items = total_funcs + total_classes
        print(f"  Functions: {total_funcs:,}")
        print(f"  Classes: {total_classes:,}")
        print(f"  Total items: {total_items:,}")
    else:
        total_items = total_funcs
        print(f"  Functions/Components: {total_funcs:,}")
    
    print(f"  Documented: {total_docs:,}")
    if total_items > 0:
        coverage = (total_docs / total_items) * 100
        print(f"  Coverage: {coverage:.2f}%")
        print(f"  Undocumented: {total_items - total_docs:,}")
    
    print(f"  Inline comments: {total_inline:,}")
    print(f"  TODO/FIXME markers: {total_todos}")
    print(f"  Commented code blocks: {total_commented}")
    
    # Key directories
    key_dirs = ['api', 'governance', 'orchestrator', 'src', 'kernel', 'plugins', 'integrations']
    for dir_name in key_dirs:
        dir_files = [f for f in src_files if f'{os.sep}{dir_name}{os.sep}' in f['file'] or f['file'].startswith(dir_name)]
        if dir_files:
            dir_funcs = sum(f.get('functions', 0) for f in dir_files)
            dir_classes = sum(f.get('classes', 0) for f in dir_files)
            dir_docs = sum(f.get('documented', 0) for f in dir_files)
            dir_items = dir_funcs + dir_classes if lang == 'python' else dir_funcs
            if dir_items > 0:
                dir_cov = (dir_docs / dir_items) * 100
                print(f"    {dir_name}/: {len(dir_files)} files, {dir_items} items, {dir_docs} docs ({dir_cov:.1f}%)")
    
    # Top undocumented files
    undoc_files = [(f['file'], f.get('functions', 0) + f.get('classes', 0), f.get('documented', 0)) 
                   for f in src_files if f.get('documented', 0) == 0]
    undoc_files = sorted(undoc_files, key=lambda x: x[1], reverse=True)[:5]
    
    if undoc_files:
        print(f"\n  Top undocumented files:")
        for path, items, docs in undoc_files:
            short_path = path if len(path) < 60 else '...' + path[-57:]
            print(f"    - {short_path} ({items} items)")

print("\n" + "=" * 90)
print("ACTIONABLE ITEMS")
print("=" * 90)

# All source files with TODOs
all_files = data['details']['python'] + data['details']['javascript'] + data['details']['typescript']
src_files_all = [f for f in all_files if is_source_file(f['file'])]

total_todos = sum(f.get('todos', 0) for f in src_files_all)
total_commented_code = sum(f.get('commented_code', 0) for f in src_files_all)

print(f"\nTODO/FIXME markers: {total_todos}")
todo_files = [(f['file'], f.get('todos', 0)) for f in src_files_all if f.get('todos', 0) > 0]
if todo_files:
    todo_files = sorted(todo_files, key=lambda x: x[1], reverse=True)[:10]
    print(f"Top files with TODOs:")
    for path, count in todo_files:
        short_path = path if len(path) < 70 else '...' + path[-67:]
        print(f"  {count:3} - {short_path}")

print(f"\nCommented code blocks: {total_commented_code}")
commented_files = [(f['file'], f.get('commented_code', 0)) for f in src_files_all if f.get('commented_code', 0) > 0]
if commented_files:
    commented_files = sorted(commented_files, key=lambda x: x[1], reverse=True)[:10]
    print(f"Top files with commented code:")
    for path, count in commented_files:
        short_path = path if len(path) < 70 else '...' + path[-67:]
        print(f"  {count:3} - {short_path}")

print("\n" + "=" * 90)
print("RECOMMENDATIONS")
print("=" * 90)

print("""
1. PRIORITY AREAS FOR DOCUMENTATION:
   - TypeScript files have the lowest coverage (8.51%) - focus on React components
   - JavaScript files need improvement (21.69%)
   - Python is better but still needs work (29.34%)

2. CODE CLEANUP:
   - Review and resolve TODO/FIXME markers
   - Remove or uncomment code blocks that are commented out
   - Consider using feature flags instead of commented code

3. DOCUMENTATION STANDARDS:
   - Establish minimum documentation requirements (e.g., all public APIs)
   - Add JSDoc/docstrings for all exported functions/classes
   - Document complex algorithms and business logic
   - Include type information in TypeScript

4. AUTOMATION:
   - Add linting rules to enforce documentation standards
   - Use documentation coverage tools in CI/CD pipeline
   - Consider documentation generation tools (Sphinx, JSDoc, TypeDoc)
""")

print("=" * 90)
print(f"\nFull report saved to: audit/comments_coverage.json")
print("=" * 90)
