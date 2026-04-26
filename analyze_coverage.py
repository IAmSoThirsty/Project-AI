#!/usr/bin/env python3
"""Script to analyze docstring and type hint coverage."""
import os
import ast

def analyze_functions(filepath):
    """Analyze functions in a Python file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read())
        
        stats = {'total': 0, 'with_docstring': 0, 'with_type_hints': 0}
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                stats['total'] += 1
                if ast.get_docstring(node):
                    stats['with_docstring'] += 1
                if node.returns or any(arg.annotation for arg in node.args.args):
                    stats['with_type_hints'] += 1
        
        return stats
    except Exception:
        return {'total': 0, 'with_docstring': 0, 'with_type_hints': 0}

def main():
    """Main analysis function."""
    all_stats = {'total': 0, 'with_docstring': 0, 'with_type_hints': 0}

    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                stats = analyze_functions(filepath)
                for key in all_stats:
                    all_stats[key] += stats[key]

    if all_stats['total'] > 0:
        doc_pct = 100 * all_stats['with_docstring'] / all_stats['total']
        type_pct = 100 * all_stats['with_type_hints'] / all_stats['total']
    else:
        doc_pct = type_pct = 0

    print(f"Function docstring coverage: {all_stats['with_docstring']}/{all_stats['total']} ({doc_pct:.1f}%)")
    print(f"Type hint coverage: {all_stats['with_type_hints']}/{all_stats['total']} ({type_pct:.1f}%)")

if __name__ == '__main__':
    main()
