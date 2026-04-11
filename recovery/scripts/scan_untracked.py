#!/usr/bin/env python3
"""
PHASE 0 - SCANNER 1: Untracked Files Discovery
Scans for all untracked and ignored files in the repository
"""
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from collections import defaultdict

def get_file_category(filepath):
    """Categorize file by extension and location"""
    ext = Path(filepath).suffix.lower()
    path_parts = Path(filepath).parts
    
    # Source code extensions
    source_exts = {'.py', '.js', '.ts', '.java', '.kt', '.kts', '.go', '.rs', '.c', '.cpp', 
                   '.h', '.hpp', '.cs', '.rb', '.php', '.swift', '.m', '.mm', '.tsx', '.jsx'}
    
    # Config extensions
    config_exts = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf', '.xml', 
                   '.properties', '.env', '.config'}
    
    # Build artifacts
    build_patterns = {'.gradle', '.class', '.pyc', '.pyo', '.o', '.so', '.dll', '.exe', 
                     '.jar', '.war', '.ear', '.lock', '.bin'}
    
    # Data files
    data_exts = {'.db', '.sqlite', '.sqlite3', '.csv', '.json', '.xml', '.log', '.txt'}
    
    # Check for temp/cache directories
    if any(p in ['.gradle', 'node_modules', '__pycache__', '.cache', 'build', 
                 'dist', 'target', '.pytest_cache', '.mypy_cache'] for p in path_parts):
        return 'temp'
    
    if ext in source_exts:
        return 'source'
    elif ext in config_exts or filepath.endswith('.gitignore'):
        return 'config'
    elif ext in build_patterns:
        return 'build'
    elif ext in data_exts:
        return 'data'
    else:
        return 'unknown'

def get_ignored_files():
    """Get list of ignored files using git"""
    try:
        result = subprocess.run(
            ['git', 'ls-files', '--others', '--ignored', '--exclude-standard'],
            capture_output=True,
            text=True,
            check=True
        )
        return [f.strip() for f in result.stdout.splitlines() if f.strip()]
    except subprocess.CalledProcessError as e:
        print(f"Error running git command: {e}")
        return []

def process_files():
    """Process all untracked/ignored files and generate report"""
    scan_timestamp = datetime.utcnow().isoformat() + 'Z'
    
    # Get ignored files
    ignored_files = get_ignored_files()
    
    print(f"Found {len(ignored_files)} ignored files")
    
    files_data = []
    total_size = 0
    by_category = defaultdict(int)
    by_extension = defaultdict(int)
    
    for filepath in ignored_files:
        try:
            full_path = Path(filepath)
            
            # Skip if file doesn't exist (could be a directory pattern)
            if not full_path.exists():
                continue
            
            if full_path.is_file():
                stat = full_path.stat()
                size_bytes = stat.st_size
                modified = datetime.fromtimestamp(stat.st_mtime).isoformat() + 'Z'
                
                extension = full_path.suffix.lower() if full_path.suffix else '(none)'
                category = get_file_category(str(filepath))
                
                files_data.append({
                    'path': str(filepath).replace('\\', '/'),
                    'size_bytes': size_bytes,
                    'modified': modified,
                    'category': category,
                    'extension': extension
                })
                
                total_size += size_bytes
                by_category[category] += 1
                by_extension[extension] += 1
                
        except (OSError, PermissionError, ValueError) as e:
            # Skip files that can't be accessed (symlinks, permission issues, etc.)
            continue
    
    # Sort by size for largest files
    sorted_files = sorted(files_data, key=lambda x: x['size_bytes'], reverse=True)
    largest_files = [
        {'path': f['path'], 'size_bytes': f['size_bytes']} 
        for f in sorted_files[:20]
    ]
    
    # Build report
    report = {
        'scan_timestamp': scan_timestamp,
        'total_count': len(files_data),
        'total_size_bytes': total_size,
        'files': files_data,
        'summary': {
            'by_category': dict(by_category),
            'by_extension': dict(sorted(by_extension.items(), key=lambda x: x[1], reverse=True)[:30]),
            'largest_files': largest_files
        }
    }
    
    # Write to output file
    output_dir = Path('audit')
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / 'untracked_files.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n=== SCAN COMPLETE ===")
    print(f"Total files: {len(files_data)}")
    print(f"Total size: {total_size:,} bytes ({total_size / (1024*1024):.2f} MB)")
    print(f"\nBy category:")
    for cat, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")
    print(f"\nReport written to: {output_file}")
    
    return report

if __name__ == '__main__':
    process_files()
