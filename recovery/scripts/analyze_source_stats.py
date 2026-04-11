#!/usr/bin/env python3
"""Extract statistics for source files only"""

import json

# Load the data
with open('audit/comments_coverage.json', 'r') as f:
    data = json.load(f)

# Filter to source files
source_dirs = ['src', 'plugins', 'api', 'governance', 'orchestrator', 'kernel', 'tarl', 'integrations']

print("=" * 80)
print("CODE COMMENTS COVERAGE ANALYSIS - SOURCE FILES ONLY")
print("=" * 80)

for lang in ['python', 'javascript', 'typescript']:
    files = data['details'][lang]
    src_files = [f for f in files if any(f['file'].startswith(f'.\\{d}') for d in source_dirs)]
    
    if not src_files:
        continue
    
    print(f"\n{lang.upper()} FILES:")
    print(f"  Total source files: {len(src_files)}")
    
    total_funcs = sum(f.get('functions', 0) for f in src_files)
    total_classes = sum(f.get('classes', 0) for f in src_files)
    total_docs = sum(f.get('documented', 0) for f in src_files)
    total_todos = sum(f.get('todos', 0) for f in src_files)
    total_commented = sum(f.get('commented_code', 0) for f in src_files)
    
    if lang == 'python':
        total_items = total_funcs + total_classes
        print(f"  Functions: {total_funcs}")
        print(f"  Classes: {total_classes}")
    else:
        total_items = total_funcs
        print(f"  Functions/Components: {total_funcs}")
    
    print(f"  Documented: {total_docs}")
    if total_items > 0:
        coverage = (total_docs / total_items) * 100
        print(f"  Coverage: {coverage:.2f}%")
        print(f"  Undocumented: {total_items - total_docs}")
    
    print(f"  TODO/FIXME markers: {total_todos}")
    print(f"  Commented code blocks: {total_commented}")
    
    # Top files by function count
    print(f"\n  Top 10 files by size:")
    sorted_files = sorted(src_files, key=lambda x: x.get('functions', 0), reverse=True)[:10]
    for i, f in enumerate(sorted_files, 1):
        funcs = f.get('functions', 0)
        docs = f.get('documented', 0)
        cov = (docs / max(funcs, 1)) * 100
        file_path = f['file'].replace('.\\', '')
        print(f"    {i:2}. {file_path}")
        print(f"        {funcs} functions, {docs} documented ({cov:.1f}%)")
    
    # Files with 0% coverage
    no_docs = [f for f in src_files if f.get('documented', 0) == 0 and f.get('functions', 0) > 0]
    if no_docs:
        print(f"\n  Files with 0% documentation: {len(no_docs)}")
        for f in sorted(no_docs, key=lambda x: x.get('functions', 0), reverse=True)[:5]:
            file_path = f['file'].replace('.\\', '')
            funcs = f.get('functions', 0)
            print(f"    - {file_path} ({funcs} functions)")

print("\n" + "=" * 80)
print("ACTIONABLE ITEMS")
print("=" * 80)

# Files with TODOs
all_files = data['details']['python'] + data['details']['javascript'] + data['details']['typescript']
src_files_all = [f for f in all_files if any(f['file'].startswith(f'.\\{d}') for d in source_dirs)]
todo_files = [(f['file'].replace('.\\', ''), f.get('todos', 0)) 
              for f in src_files_all if f.get('todos', 0) > 0]

if todo_files:
    print(f"\nFiles with TODO/FIXME markers ({len(todo_files)} files):")
    for file, count in sorted(todo_files, key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {count:3} - {file}")

# Files with commented code
commented_files = [(f['file'].replace('.\\', ''), f.get('commented_code', 0)) 
                   for f in src_files_all if f.get('commented_code', 0) > 0]

if commented_files:
    print(f"\nFiles with commented code blocks ({len(commented_files)} files):")
    for file, count in sorted(commented_files, key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {count:3} - {file}")

print("\n" + "=" * 80)
