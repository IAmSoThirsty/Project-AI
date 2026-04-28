#!/usr/bin/env python3
"""Simple cyclomatic complexity analyzer."""
import os
import ast

def calculate_complexity(node):
    """Calculate cyclomatic complexity of a function."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
            complexity += 1
        elif isinstance(child, ast.ExceptHandler):
            complexity += 1
        elif isinstance(child, (ast.And, ast.Or)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity

def analyze_file(filepath):
    """Analyze complexity of all functions in a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filepath)
        
        results = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                complexity = calculate_complexity(node)
                if complexity > 10:
                    results.append({
                        'file': filepath,
                        'function': node.name,
                        'line': node.lineno,
                        'complexity': complexity
                    })
        return results
    except Exception as e:
        return []

def main():
    """Main analysis function."""
    all_complex = []
    
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                results = analyze_file(filepath)
                all_complex.extend(results)
    
    # Sort by complexity descending
    all_complex.sort(key=lambda x: x['complexity'], reverse=True)
    
    print(f"\n=== Functions with Complexity > 10 ===")
    print(f"Total: {len(all_complex)} functions")
    print("\nTop 20 most complex functions:")
    for item in all_complex[:20]:
        print(f"{item['complexity']:3d}  {item['function']:40s} {item['file']}:{item['line']}")

if __name__ == '__main__':
    main()
