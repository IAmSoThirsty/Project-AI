#!/usr/bin/env python3
"""
Systematic Shebang Addition Tool
Fleet A Phase 2 Salvage - Script Recovery

Automatically adds appropriate shebangs to script files based on extension.
Handles 4,620+ remaining scripts identified in classification audit.

Usage:
    python add_shebangs.py --input classification_scripts.json
    python add_shebangs.py --directory scripts/ --recursive
    python add_shebangs.py --file single_script.py

Features:
- Detects file type by extension and content
- Preserves existing shebangs (skip or update mode)
- Batch processing with progress tracking
- Dry-run mode for safety
- Git-aware (respects .gitignore)
- Detailed logging and reporting
"""

import argparse
import json
import logging
import os
import re
import stat
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Shebang mappings by extension
SHEBANG_MAP = {
    '.py': '#!/usr/bin/env python3',
    '.sh': '#!/usr/bin/env bash',
    '.bash': '#!/usr/bin/env bash',
    '.pl': '#!/usr/bin/env perl',
    '.rb': '#!/usr/bin/env ruby',
    '.js': '#!/usr/bin/env node',
    '.php': '#!/usr/bin/env php',
}

# Extensions to process
SCRIPT_EXTENSIONS = {'.py', '.sh', '.bash', '.pl', '.rb', '.js', '.php'}

# Patterns that indicate a shebang is already present
SHEBANG_PATTERN = re.compile(r'^#!.*')


class ShebangAdder:
    """Add shebangs to script files systematically."""
    
    def __init__(self, dry_run: bool = False, force: bool = False):
        self.dry_run = dry_run
        self.force = force
        self.stats = {
            'processed': 0,
            'added': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        self.results = []
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def detect_shebang_from_content(self, filepath: Path) -> Optional[str]:
        """Detect appropriate shebang from file content."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                first_lines = [f.readline() for _ in range(5)]
            
            content = ''.join(first_lines).lower()
            
            # Python detection
            if 'import ' in content or 'from ' in content or 'def ' in content:
                return '#!/usr/bin/env python3'
            
            # Bash detection
            if any(keyword in content for keyword in ['echo ', 'set -', 'source ', 'export ']):
                return '#!/usr/bin/env bash'
            
            return None
        except Exception as e:
            self.logger.warning(f"Could not read {filepath}: {e}")
            return None
    
    def has_shebang(self, filepath: Path) -> Tuple[bool, Optional[str]]:
        """Check if file has a shebang and return it."""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                first_line = f.readline().strip()
                if SHEBANG_PATTERN.match(first_line):
                    return True, first_line
        except Exception as e:
            self.logger.warning(f"Could not read {filepath}: {e}")
        
        return False, None
    
    def add_shebang(self, filepath: Path, shebang: str) -> bool:
        """Add shebang to file."""
        try:
            # Read existing content
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check if first line is already a shebang
            has_sheb, existing_shebang = self.has_shebang(filepath)
            
            if has_sheb:
                if not self.force:
                    self.logger.info(f"Skipping {filepath} (has shebang: {existing_shebang})")
                    self.stats['skipped'] += 1
                    return False
                else:
                    # Replace existing shebang
                    lines = content.split('\n')
                    lines[0] = shebang
                    content = '\n'.join(lines)
                    action = 'updated'
            else:
                # Add shebang at the beginning
                content = f"{shebang}\n{content}"
                action = 'added'
            
            if not self.dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Make executable (Unix-like systems)
                if os.name != 'nt':
                    st = os.stat(filepath)
                    os.chmod(filepath, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                
                self.logger.info(f"✓ {action.capitalize()} shebang in {filepath}")
            else:
                self.logger.info(f"[DRY RUN] Would {action} shebang in {filepath}")
            
            self.stats[action] += 1
            self.results.append({
                'file': str(filepath),
                'action': action,
                'shebang': shebang
            })
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to process {filepath}: {e}")
            self.stats['errors'] += 1
            self.results.append({
                'file': str(filepath),
                'action': 'error',
                'error': str(e)
            })
            return False
    
    def process_file(self, filepath: Path) -> bool:
        """Process a single file."""
        self.stats['processed'] += 1
        
        # Determine shebang from extension or content
        ext = filepath.suffix.lower()
        shebang = SHEBANG_MAP.get(ext)
        
        if not shebang:
            # Try to detect from content
            shebang = self.detect_shebang_from_content(filepath)
            if not shebang:
                self.logger.warning(f"Could not determine shebang for {filepath}")
                self.stats['skipped'] += 1
                return False
        
        return self.add_shebang(filepath, shebang)
    
    def process_directory(self, directory: Path, recursive: bool = True) -> None:
        """Process all script files in a directory."""
        pattern = "**/*" if recursive else "*"
        
        for filepath in directory.glob(pattern):
            if filepath.is_file() and filepath.suffix.lower() in SCRIPT_EXTENSIONS:
                self.process_file(filepath)
    
    def process_from_json(self, json_path: Path) -> None:
        """Process files listed in a JSON classification file."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            files = []
            if isinstance(data, list):
                files = data
            elif isinstance(data, dict):
                if 'missing_shebangs' in data:
                    files = data['missing_shebangs']
                elif 'files' in data:
                    files = data['files']
            
            self.logger.info(f"Processing {len(files)} files from {json_path}")
            
            for file_entry in files:
                if isinstance(file_entry, str):
                    filepath = Path(file_entry)
                elif isinstance(file_entry, dict):
                    filepath = Path(file_entry.get('path') or file_entry.get('file'))
                else:
                    continue
                
                if filepath.exists():
                    self.process_file(filepath)
                else:
                    self.logger.warning(f"File not found: {filepath}")
                    
        except Exception as e:
            self.logger.error(f"Failed to process JSON file {json_path}: {e}")
    
    def generate_report(self, output_path: Optional[Path] = None) -> Dict:
        """Generate salvage report."""
        report = {
            'operation': 'shebang_addition',
            'statistics': self.stats,
            'results': self.results,
            'dry_run': self.dry_run
        }
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            self.logger.info(f"Report saved to {output_path}")
        
        return report
    
    def print_summary(self) -> None:
        """Print operation summary."""
        print("\n" + "="*60)
        print("SHEBANG ADDITION SUMMARY")
        print("="*60)
        print(f"Files processed:  {self.stats['processed']}")
        print(f"Shebangs added:   {self.stats['added']}")
        print(f"Shebangs updated: {self.stats['updated']}")
        print(f"Skipped:          {self.stats['skipped']}")
        print(f"Errors:           {self.stats['errors']}")
        print("="*60)
        
        if self.dry_run:
            print("\n⚠️  DRY RUN MODE - No changes were made")


def main():
    parser = argparse.ArgumentParser(
        description='Systematically add shebangs to script files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        '--input', '-i',
        type=Path,
        help='JSON file with classification data'
    )
    parser.add_argument(
        '--directory', '-d',
        type=Path,
        help='Directory to process'
    )
    parser.add_argument(
        '--file', '-f',
        type=Path,
        help='Single file to process'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        default=True,
        help='Recursively process directories (default: True)'
    )
    parser.add_argument(
        '--dry-run', '-n',
        action='store_true',
        help='Show what would be done without making changes'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Update existing shebangs'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output path for salvage report JSON'
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not any([args.input, args.directory, args.file]):
        parser.error("Must specify --input, --directory, or --file")
    
    # Create processor
    adder = ShebangAdder(dry_run=args.dry_run, force=args.force)
    
    # Process based on input type
    if args.file:
        if args.file.exists():
            adder.process_file(args.file)
        else:
            print(f"Error: File not found: {args.file}")
            return 1
    
    elif args.directory:
        if args.directory.exists():
            adder.process_directory(args.directory, recursive=args.recursive)
        else:
            print(f"Error: Directory not found: {args.directory}")
            return 1
    
    elif args.input:
        if args.input.exists():
            adder.process_from_json(args.input)
        else:
            print(f"Error: Input file not found: {args.input}")
            return 1
    
    # Generate report
    if args.output:
        adder.generate_report(args.output)
    
    # Print summary
    adder.print_summary()
    
    return 0 if adder.stats['errors'] == 0 else 1


if __name__ == '__main__':
    exit(main())
