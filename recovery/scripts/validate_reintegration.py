#!/usr/bin/env python3
"""
Phase 3 Reintegration Validator
Validates naming conventions, module boundaries, and dependency graphs
"""
import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple


class ReintegrationValidator:
    def __init__(self, recovery_path: str = "recovery"):
        self.recovery_path = Path(recovery_path)
        self.issues = []
        self.naming_violations = []
        self.boundary_violations = []
        self.circular_deps = []
        self.validated_files = []
        
    def validate_naming_conventions(self) -> bool:
        """Validate file naming conventions"""
        print("\n[1/4] Validating naming conventions...")
        
        conventions = {
            'uppercase_docs': r'^[A-Z][A-Z0-9_]*\.md$',
            'snake_case_scripts': r'^[a-z][a-z0-9_]*\.(py|sh|ps1)$',
            'kebab_case_api': r'^[a-z][a-z0-9-]*-api\.yaml$',
        }
        
        for file_path in self.recovery_path.rglob('*'):
            if not file_path.is_file():
                continue
                
            filename = file_path.name
            
            # Skip marker files
            if filename in ['PHASE_2_COMPLETE.md', 'PHASE_2_COMPLETION_REPORT.md', 'README.md']:
                continue
            
            # Check API specs
            if 'api_docs' in str(file_path) and filename.endswith('.yaml'):
                if not re.match(conventions['kebab_case_api'], filename):
                    self.naming_violations.append(f"API spec not kebab-case: {file_path}")
            
            # Check scripts
            elif filename.endswith(('.py', '.sh', '.ps1')):
                if not re.match(conventions['snake_case_scripts'], filename):
                    self.naming_violations.append(f"Script not snake_case: {file_path}")
            
            # Check markdown docs (most should be uppercase or PascalCase)
            elif filename.endswith('.md') and 'docs' in str(file_path):
                if not (re.match(conventions['uppercase_docs'], filename) or 
                       filename[0].isupper()):
                    self.naming_violations.append(f"Doc not uppercase: {file_path}")
        
        if self.naming_violations:
            print(f"  ⚠️  Found {len(self.naming_violations)} naming violations")
            return False
        else:
            print("  ✅ All naming conventions valid")
            return True
    
    def validate_module_boundaries(self) -> bool:
        """Validate module boundaries and structure"""
        print("\n[2/4] Validating module boundaries...")
        
        expected_structure = {
            'api_docs': ['*.yaml', 'README.md'],
            'architecture': ['*.md'],
            'docs': ['**/*.md'],
            'md_files': ['*.md'],
            'readmes': ['**/README.md'],
            'runbooks': ['*.md']
        }
        
        for subdir, patterns in expected_structure.items():
            subpath = self.recovery_path / subdir
            if not subpath.exists():
                self.boundary_violations.append(f"Missing expected directory: {subdir}")
                continue
            
            files = list(subpath.rglob('*'))
            if not any(f.is_file() for f in files):
                self.boundary_violations.append(f"Empty directory: {subdir}")
        
        # Check for files in wrong locations
        for file_path in self.recovery_path.rglob('*.yaml'):
            if 'api_docs' not in str(file_path):
                self.boundary_violations.append(f"API spec outside api_docs: {file_path}")
        
        if self.boundary_violations:
            print(f"  ⚠️  Found {len(self.boundary_violations)} boundary violations")
            return False
        else:
            print("  ✅ Module boundaries valid")
            return True
    
    def check_circular_dependencies(self) -> bool:
        """Check for circular dependencies in documentation"""
        print("\n[3/4] Checking for circular dependencies...")
        
        doc_graph = {}
        
        # Build dependency graph from markdown links
        for md_file in self.recovery_path.rglob('*.md'):
            if md_file.is_file():
                try:
                    content = md_file.read_text(encoding='utf-8')
                    links = re.findall(r'\[.*?\]\((.*?\.md)\)', content)
                    doc_graph[str(md_file)] = [str(md_file.parent / link) for link in links]
                except Exception as e:
                    self.issues.append(f"Error reading {md_file}: {e}")
        
        # Simple cycle detection (DFS)
        def has_cycle(node, visited, rec_stack):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in doc_graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor, visited, rec_stack):
                        return True
                elif neighbor in rec_stack:
                    self.circular_deps.append((node, neighbor))
                    return True
            
            rec_stack.remove(node)
            return False
        
        visited = set()
        for node in doc_graph:
            if node not in visited:
                has_cycle(node, visited, set())
        
        if self.circular_deps:
            print(f"  ⚠️  Found {len(self.circular_deps)} circular dependencies")
            return False
        else:
            print("  ✅ No circular dependencies")
            return True
    
    def scan_for_junk(self) -> List[str]:
        """Scan for junk files that should not be staged"""
        print("\n[4/4] Scanning for junk patterns...")
        
        junk_patterns = [
            r'\.tmp$',
            r'\.temp$',
            r'\.bak$',
            r'\.swp$',
            r'~$',
            r'^\.DS_Store$',
            r'^Thumbs\.db$',
            r'^\._',
            r'\.log$',
            r'\.cache$',
        ]
        
        junk_files = []
        for file_path in self.recovery_path.rglob('*'):
            if not file_path.is_file():
                continue
            
            filename = file_path.name
            for pattern in junk_patterns:
                if re.search(pattern, filename):
                    junk_files.append(str(file_path))
                    break
        
        if junk_files:
            print(f"  ⚠️  Found {len(junk_files)} junk files")
        else:
            print("  ✅ No junk files found")
        
        return junk_files
    
    def validate_all(self) -> Tuple[bool, Dict]:
        """Run all validations"""
        print("=" * 60)
        print("PHASE 3: REINTEGRATION VALIDATION")
        print("=" * 60)
        
        naming_ok = self.validate_naming_conventions()
        boundaries_ok = self.validate_module_boundaries()
        deps_ok = self.check_circular_dependencies()
        junk_files = self.scan_for_junk()
        
        all_valid = naming_ok and boundaries_ok and deps_ok
        
        report = {
            "validation_passed": all_valid,
            "naming_conventions": {
                "valid": naming_ok,
                "violations": self.naming_violations
            },
            "module_boundaries": {
                "valid": boundaries_ok,
                "violations": self.boundary_violations
            },
            "circular_dependencies": {
                "valid": deps_ok,
                "cycles": [{"from": c[0], "to": c[1]} for c in self.circular_deps]
            },
            "junk_files": junk_files,
            "total_files_scanned": sum(1 for _ in self.recovery_path.rglob('*') if _.is_file()),
            "issues": self.issues
        }
        
        print("\n" + "=" * 60)
        if all_valid:
            print("✅ VALIDATION PASSED - Ready for staging")
        else:
            print("❌ VALIDATION FAILED - Issues must be resolved")
        print("=" * 60)
        
        return all_valid, report


def main():
    validator = ReintegrationValidator("recovery")
    is_valid, report = validator.validate_all()
    
    # Save report
    report_path = Path("audit/reintegration_validation.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Validation report saved to: {report_path}")
    
    return 0 if is_valid else 1


if __name__ == "__main__":
    exit(main())
