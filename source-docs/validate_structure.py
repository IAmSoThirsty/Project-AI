#!/usr/bin/env python3
"""
Source Documentation Structure Validator

This script validates the source-docs/ directory structure to ensure:
- All required subdirectories exist (core, agents, gui, supporting)
- Each subdirectory contains a README.md file
- Master README exists with proper structure
- No orphaned files outside documented structure
- Proper markdown formatting and link validity

Usage:
    python validate_structure.py              # Validate structure
    python validate_structure.py --tree       # Generate directory tree
    python validate_structure.py --check-links # Validate all markdown links
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import List, Tuple, Dict


class Color:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


class SourceDocsValidator:
    """Validates source-docs directory structure and documentation"""
    
    REQUIRED_SUBDIRS = ['core', 'agents', 'gui', 'supporting']
    ROOT_DIR = Path(__file__).parent
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []
    
    def validate(self) -> bool:
        """
        Run all validation checks
        
        Returns:
            bool: True if all checks passed, False otherwise
        """
        print(f"{Color.BOLD}Source Documentation Structure Validator{Color.END}")
        print("=" * 60)
        print()
        
        self._check_subdirectories()
        self._check_readme_files()
        self._check_master_readme()
        self._check_orphaned_files()
        self._check_markdown_formatting()
        
        self._print_results()
        
        return len(self.errors) == 0
    
    def _check_subdirectories(self):
        """Verify all required subdirectories exist"""
        print(f"{Color.BLUE}Checking subdirectories...{Color.END}")
        
        for subdir in self.REQUIRED_SUBDIRS:
            subdir_path = self.ROOT_DIR / subdir
            if subdir_path.exists() and subdir_path.is_dir():
                self.successes.append(f"✓ Subdirectory '{subdir}/' exists")
            else:
                self.errors.append(f"✗ Required subdirectory '{subdir}/' not found")
        
        print()
    
    def _check_readme_files(self):
        """Verify each subdirectory contains README.md"""
        print(f"{Color.BLUE}Checking README files...{Color.END}")
        
        for subdir in self.REQUIRED_SUBDIRS:
            readme_path = self.ROOT_DIR / subdir / "README.md"
            if readme_path.exists() and readme_path.is_file():
                # Check file is not empty
                if readme_path.stat().st_size > 0:
                    self.successes.append(f"✓ README.md exists in '{subdir}/'")
                    self._validate_readme_content(readme_path, subdir)
                else:
                    self.errors.append(f"✗ README.md in '{subdir}/' is empty")
            else:
                self.errors.append(f"✗ README.md not found in '{subdir}/'")
        
        print()
    
    def _validate_readme_content(self, readme_path: Path, subdir: str):
        """Validate README content structure"""
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required sections
        required_sections = [
            'Purpose',
            'Related Documentation'
        ]
        
        for section in required_sections:
            if f"## {section}" in content or f"### {section}" in content:
                self.successes.append(f"  ✓ '{subdir}/README.md' has '{section}' section")
            else:
                self.warnings.append(f"  ⚠ '{subdir}/README.md' missing '{section}' section")
    
    def _check_master_readme(self):
        """Verify master README.md exists and has proper structure"""
        print(f"{Color.BLUE}Checking master README...{Color.END}")
        
        master_readme = self.ROOT_DIR / "README.md"
        if not master_readme.exists():
            self.errors.append("✗ Master README.md not found")
            print()
            return
        
        self.successes.append("✓ Master README.md exists")
        
        with open(master_readme, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check word count (should be 500+ words)
        word_count = len(content.split())
        if word_count >= 500:
            self.successes.append(f"✓ Master README has {word_count} words (>= 500)")
        else:
            self.warnings.append(f"⚠ Master README has only {word_count} words (< 500)")
        
        # Check for links to all subdirectories
        for subdir in self.REQUIRED_SUBDIRS:
            if f"[{subdir}/](./{subdir}/README.md)" in content or \
               f"source-docs/{subdir}/" in content:
                self.successes.append(f"✓ Master README links to '{subdir}/'")
            else:
                self.warnings.append(f"⚠ Master README may not link to '{subdir}/'")
        
        # Check required sections
        required_sections = [
            'Overview',
            'Directory Structure',
            'Documentation Standards',
            'Validation'
        ]
        
        for section in required_sections:
            if f"## {section}" in content:
                self.successes.append(f"✓ Master README has '{section}' section")
            else:
                self.warnings.append(f"⚠ Master README missing '{section}' section")
        
        print()
    
    def _check_orphaned_files(self):
        """Check for files outside documented structure"""
        print(f"{Color.BLUE}Checking for orphaned files...{Color.END}")
        
        allowed_files = {
            'README.md',
            'validate_structure.py',
            'TREE.md',
            '__pycache__'
        }
        
        allowed_dirs = set(self.REQUIRED_SUBDIRS)
        
        orphaned = []
        for item in self.ROOT_DIR.iterdir():
            if item.name.startswith('.'):
                continue  # Ignore hidden files
            
            if item.is_file() and item.name not in allowed_files:
                orphaned.append(item.name)
            elif item.is_dir() and item.name not in allowed_dirs and item.name != '__pycache__':
                orphaned.append(f"{item.name}/")
        
        if orphaned:
            self.warnings.append(f"⚠ Orphaned files/directories found: {', '.join(orphaned)}")
        else:
            self.successes.append("✓ No orphaned files found")
        
        print()
    
    def _check_markdown_formatting(self):
        """Validate markdown formatting in all README files"""
        print(f"{Color.BLUE}Checking markdown formatting...{Color.END}")
        
        all_readmes = [self.ROOT_DIR / "README.md"]
        for subdir in self.REQUIRED_SUBDIRS:
            readme_path = self.ROOT_DIR / subdir / "README.md"
            if readme_path.exists():
                all_readmes.append(readme_path)
        
        for readme_path in all_readmes:
            self._validate_markdown(readme_path)
        
        print()
    
    def _validate_markdown(self, file_path: Path):
        """Validate individual markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        relative_path = file_path.relative_to(self.ROOT_DIR)
        
        # Check for malformed links
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        links = re.findall(link_pattern, content)
        
        for link_text, link_url in links:
            if link_url.startswith('http'):
                continue  # External links not validated
            
            # Check relative links
            if link_url.startswith('./') or link_url.startswith('../'):
                target = (file_path.parent / link_url).resolve()
                if not target.exists():
                    self.warnings.append(
                        f"⚠ Broken link in '{relative_path}': [{link_text}]({link_url})"
                    )
        
        # Check for proper heading hierarchy
        headings = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        prev_level = 0
        for heading_marks, heading_text in headings:
            level = len(heading_marks)
            if level > prev_level + 1 and prev_level > 0:
                self.warnings.append(
                    f"⚠ Heading level skip in '{relative_path}': {heading_text}"
                )
            prev_level = level
    
    def _print_results(self):
        """Print validation results summary"""
        print(f"\n{Color.BOLD}Validation Results{Color.END}")
        print("=" * 60)
        print()
        
        if self.successes:
            print(f"{Color.GREEN}✓ Successes ({len(self.successes)}):{Color.END}")
            for success in self.successes:
                print(f"  {success}")
            print()
        
        if self.warnings:
            print(f"{Color.YELLOW}⚠ Warnings ({len(self.warnings)}):{Color.END}")
            for warning in self.warnings:
                print(f"  {warning}")
            print()
        
        if self.errors:
            print(f"{Color.RED}✗ Errors ({len(self.errors)}):{Color.END}")
            for error in self.errors:
                print(f"  {error}")
            print()
        
        # Final verdict
        print("=" * 60)
        if self.errors:
            print(f"{Color.RED}{Color.BOLD}VALIDATION FAILED{Color.END}")
            print(f"Fix {len(self.errors)} error(s) before proceeding.")
            return False
        elif self.warnings:
            print(f"{Color.YELLOW}{Color.BOLD}VALIDATION PASSED WITH WARNINGS{Color.END}")
            print(f"Consider addressing {len(self.warnings)} warning(s).")
            return True
        else:
            print(f"{Color.GREEN}{Color.BOLD}VALIDATION PASSED{Color.END}")
            print("All checks successful!")
            return True
    
    def generate_tree(self, output_file: str = "TREE.md"):
        """
        Generate directory tree documentation
        
        Args:
            output_file: Output filename for tree documentation
        """
        print(f"{Color.BLUE}Generating directory tree...{Color.END}")
        
        tree_lines = [
            "# Source Documentation Directory Tree",
            "",
            f"**Generated:** {self._get_timestamp()}",
            "",
            "```",
            "source-docs/",
        ]
        
        # Add subdirectories and their contents
        for subdir in sorted(self.REQUIRED_SUBDIRS):
            subdir_path = self.ROOT_DIR / subdir
            if subdir_path.exists():
                tree_lines.append(f"├── {subdir}/")
                
                # List files in subdirectory
                files = sorted([f.name for f in subdir_path.iterdir() if f.is_file()])
                for i, file in enumerate(files):
                    if i == len(files) - 1:
                        tree_lines.append(f"│   └── {file}")
                    else:
                        tree_lines.append(f"│   ├── {file}")
        
        # Add root-level files
        root_files = sorted([
            f.name for f in self.ROOT_DIR.iterdir()
            if f.is_file() and not f.name.startswith('.')
        ])
        
        for i, file in enumerate(root_files):
            if i == len(root_files) - 1:
                tree_lines.append(f"└── {file}")
            else:
                tree_lines.append(f"├── {file}")
        
        tree_lines.append("```")
        tree_lines.append("")
        tree_lines.append("## Statistics")
        tree_lines.append("")
        tree_lines.append(f"- **Subdirectories:** {len(self.REQUIRED_SUBDIRS)}")
        tree_lines.append(f"- **Total Files:** {len(root_files) + sum(len(list((self.ROOT_DIR / d).iterdir())) for d in self.REQUIRED_SUBDIRS if (self.ROOT_DIR / d).exists())}")
        tree_lines.append("")
        
        # Write to file
        output_path = self.ROOT_DIR / output_file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(tree_lines))
        
        print(f"{Color.GREEN}✓ Directory tree written to '{output_file}'{Color.END}")
        print()
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Validate source-docs directory structure"
    )
    parser.add_argument(
        '--tree',
        action='store_true',
        help='Generate directory tree documentation'
    )
    parser.add_argument(
        '--check-links',
        action='store_true',
        help='Validate all markdown links (included by default)'
    )
    
    args = parser.parse_args()
    
    validator = SourceDocsValidator()
    
    if args.tree:
        validator.generate_tree()
    else:
        success = validator.validate()
        sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
