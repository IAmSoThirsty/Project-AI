#!/usr/bin/env python3
"""
Phase 2: SALVAGE - Repair and restore critical and useful files
"""
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Any
import yaml
import ast


class SalvageOperation:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.recovery_dir = repo_root / "recovery"
        self.audit_dir = repo_root / "audit"
        self.salvage_log: List[Dict[str, Any]] = []
        
    def load_classification_map(self) -> List[Dict[str, Any]]:
        """Load the classification map and filter for critical/useful items"""
        map_file = self.audit_dir / "classification_map.json"
        with open(map_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return [item for item in data['items'] 
                if item['type'] in ['critical', 'useful'] 
                and Path(item['path']).exists()]
    
    def categorize_file(self, path: str) -> str:
        """Determine the recovery category for a file"""
        p = Path(path)
        
        if '.env' in p.name:
            return 'env'
        elif p.suffix in ['.yaml', '.yml'] and 'api' in path.lower():
            return 'api_specs'
        elif p.suffix == '.md':
            return 'documentation'
        elif p.suffix == '.py':
            return 'scripts'
        elif 'Dockerfile' in p.name:
            return 'docker'
        elif p.suffix in ['.json', '.yaml', '.yml', '.toml', '.cfg', '.ini']:
            return 'config'
        else:
            return 'other'
    
    def repair_python(self, content: str, filepath: str) -> tuple[str, List[str]]:
        """Repair Python syntax errors"""
        issues = []
        
        # Check for syntax errors
        try:
            ast.parse(content)
            issues.append("✓ Valid Python syntax")
        except SyntaxError as e:
            issues.append(f"⚠ Syntax error at line {e.lineno}: {e.msg}")
            # Try basic fixes
            lines = content.split('\n')
            if e.lineno and e.lineno <= len(lines):
                # Try to fix common issues
                line = lines[e.lineno - 1]
                # Fix missing colons
                if 'expected :' in str(e.msg).lower():
                    lines[e.lineno - 1] = line.rstrip() + ':'
                    content = '\n'.join(lines)
                    issues.append(f"✓ Fixed missing colon at line {e.lineno}")
        
        # Fix encoding issues
        if content.count('\r\n') > 0:
            content = content.replace('\r\n', '\n')
            issues.append("✓ Normalized line endings")
        
        # Ensure consistent indentation (4 spaces)
        lines = content.split('\n')
        fixed_lines = []
        for line in lines:
            if line.startswith('\t'):
                # Convert tabs to 4 spaces
                fixed_lines.append(line.replace('\t', '    ', 1))
            else:
                fixed_lines.append(line)
        content = '\n'.join(fixed_lines)
        
        return content, issues
    
    def repair_yaml(self, content: str, filepath: str) -> tuple[str, List[str]]:
        """Repair YAML syntax errors"""
        issues = []
        
        try:
            yaml.safe_load(content)
            issues.append("✓ Valid YAML syntax")
        except yaml.YAMLError as e:
            issues.append(f"⚠ YAML error: {str(e)[:100]}")
            # Try to fix common issues
            # Fix tab indentation
            if '\t' in content:
                content = content.replace('\t', '  ')
                issues.append("✓ Replaced tabs with spaces")
        
        # Normalize line endings
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
            issues.append("✓ Normalized line endings")
        
        return content, issues
    
    def repair_json(self, content: str, filepath: str) -> tuple[str, List[str]]:
        """Repair JSON syntax errors"""
        issues = []
        
        try:
            data = json.loads(content)
            # Re-format with consistent style
            content = json.dumps(data, indent=2, ensure_ascii=False)
            issues.append("✓ Valid JSON, reformatted")
        except json.JSONDecodeError as e:
            issues.append(f"⚠ JSON error at line {e.lineno}: {e.msg}")
            # Try to fix common issues
            # Fix trailing commas
            content = re.sub(r',(\s*[}\]])', r'\1', content)
            try:
                data = json.loads(content)
                content = json.dumps(data, indent=2, ensure_ascii=False)
                issues.append("✓ Fixed trailing commas")
            except:
                pass
        
        return content, issues
    
    def repair_markdown(self, content: str, filepath: str) -> tuple[str, List[str]]:
        """Repair and normalize markdown"""
        issues = []
        
        # Normalize line endings
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
            issues.append("✓ Normalized line endings")
        
        # Fix encoding issues
        try:
            content.encode('utf-8')
            issues.append("✓ Valid UTF-8 encoding")
        except UnicodeEncodeError:
            content = content.encode('utf-8', errors='replace').decode('utf-8')
            issues.append("⚠ Fixed encoding issues")
        
        # Ensure single blank line at end
        content = content.rstrip() + '\n'
        
        return content, issues
    
    def repair_env(self, content: str, filepath: str) -> tuple[str, List[str], bool]:
        """Repair .env file and identify if secrets need rotation"""
        issues = []
        needs_rotation = False
        
        # Normalize line endings
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
            issues.append("✓ Normalized line endings")
        
        # Check for exposed secrets
        lines = content.split('\n')
        secret_patterns = [
            (r'SECRET_KEY\s*=\s*["\']?[^"\'\s]+', "SECRET_KEY"),
            (r'API_KEY\s*=\s*["\']?[^"\'\s]+', "API_KEY"),
            (r'OPENAI_API_KEY\s*=\s*["\']?[^"\'\s]+', "OPENAI_API_KEY"),
            (r'DATABASE_URL\s*=\s*.*password.*', "DATABASE_URL"),
            (r'JWT_SECRET\s*=\s*["\']?[^"\'\s]+', "JWT_SECRET"),
        ]
        
        for pattern, secret_type in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"⚠ CRITICAL: {secret_type} found - NEEDS ROTATION")
                needs_rotation = True
        
        return content, issues, needs_rotation
    
    def salvage_file(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Salvage a single file"""
        filepath = Path(item['path'])
        
        log_entry = {
            'original_path': str(filepath),
            'type': item['type'],
            'category': self.categorize_file(str(filepath)),
            'actions': [],
            'status': 'success'
        }
        
        try:
            # Read original content
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            log_entry['actions'].append(f"✓ Read {len(content)} bytes")
            
            # Apply appropriate repair based on file type
            issues = []
            needs_rotation = False
            
            if filepath.suffix == '.py':
                content, issues = self.repair_python(content, str(filepath))
            elif filepath.suffix in ['.yaml', '.yml']:
                content, issues = self.repair_yaml(content, str(filepath))
            elif filepath.suffix == '.json':
                content, issues = self.repair_json(content, str(filepath))
            elif filepath.suffix == '.md':
                content, issues = self.repair_markdown(content, str(filepath))
            elif '.env' in filepath.name:
                content, issues, needs_rotation = self.repair_env(content, str(filepath))
                log_entry['needs_secrets_rotation'] = needs_rotation
            else:
                # Generic cleanup
                if '\r\n' in content:
                    content = content.replace('\r\n', '\n')
                    issues.append("✓ Normalized line endings")
                else:
                    issues.append("✓ No repairs needed")
            
            log_entry['actions'].extend(issues)
            
            # Determine recovery path
            category = log_entry['category']
            recovery_path = self.recovery_dir / category / filepath.name
            
            # Create parent directory if needed
            recovery_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write repaired content
            with open(recovery_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            
            log_entry['recovery_path'] = str(recovery_path)
            log_entry['actions'].append(f"✓ Saved to {recovery_path}")
            
        except Exception as e:
            log_entry['status'] = 'error'
            log_entry['actions'].append(f"✗ Error: {str(e)}")
        
        return log_entry
    
    def generate_secrets_rotation_plan(self):
        """Generate a secrets rotation plan for .env files"""
        plan_path = self.recovery_dir / "SECRETS_ROTATION_PLAN.md"
        
        plan_content = """# Secrets Rotation Plan

## CRITICAL: Exposed Secrets Detected

The following secrets were found in .env files and MUST be rotated immediately:

### Action Items:

1. **SECRET_KEY**
   - Generate new key: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - Update in production environment
   - Update in CI/CD secrets
   - Restart affected services

2. **OPENAI_API_KEY**
   - Revoke exposed key at https://platform.openai.com/api-keys
   - Generate new API key
   - Update in secure secrets manager
   - Never commit to git again

3. **DATABASE_URL**
   - Rotate database password
   - Update connection strings in production
   - Update in secrets manager
   - Test connections

4. **JWT_SECRET**
   - Generate new JWT secret
   - Force re-authentication for all users
   - Update in all services
   - Monitor for unauthorized access

### Best Practices Going Forward:

1. Use environment-specific .env files (.env.local, .env.production)
2. Add .env to .gitignore (already present)
3. Use secrets management tools (AWS Secrets Manager, Azure Key Vault, HashiCorp Vault)
4. Use .env.example for templates with placeholder values
5. Implement secrets scanning in CI/CD pipeline

### Immediate Steps:

```bash
# 1. Rotate all exposed secrets immediately
# 2. Update secrets in production
# 3. Monitor logs for suspicious activity
# 4. Run security audit:
git log --all --full-history -- "*/.env*"
```

## Status: ⚠️ URGENT - Rotate all secrets within 24 hours
"""
        
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        return str(plan_path)
    
    def run(self):
        """Execute the salvage operation"""
        print("=" * 70)
        print("PHASE 2: SALVAGE OPERATION")
        print("=" * 70)
        
        # Load items to salvage
        items = self.load_classification_map()
        print(f"\n✓ Found {len(items)} files to salvage")
        
        # Group by category
        categories = {}
        for item in items:
            cat = self.categorize_file(item['path'])
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\nBreakdown by category:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat:20s}: {count:3d} files")
        
        # Process each file
        print(f"\n{'='*70}")
        print("Processing files...")
        print(f"{'='*70}\n")
        
        secrets_rotation_needed = False
        
        for i, item in enumerate(items, 1):
            print(f"[{i}/{len(items)}] {item['path']}")
            log_entry = self.salvage_file(item)
            self.salvage_log.append(log_entry)
            
            for action in log_entry['actions']:
                print(f"  {action}")
            
            if log_entry.get('needs_secrets_rotation'):
                secrets_rotation_needed = True
            
            print()
        
        # Generate secrets rotation plan if needed
        if secrets_rotation_needed:
            plan_path = self.generate_secrets_rotation_plan()
            print(f"⚠️  CRITICAL: Secrets rotation plan created at {plan_path}\n")
        
        # Save salvage log
        log_path = self.audit_dir / "salvage_log.json"
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump({
                'total_files': len(items),
                'successful': sum(1 for entry in self.salvage_log if entry['status'] == 'success'),
                'failed': sum(1 for entry in self.salvage_log if entry['status'] == 'error'),
                'secrets_rotation_needed': secrets_rotation_needed,
                'entries': self.salvage_log
            }, f, indent=2)
        
        print(f"{'='*70}")
        print("SALVAGE OPERATION COMPLETE")
        print(f"{'='*70}")
        print(f"\n✓ Processed: {len(items)} files")
        print(f"✓ Successful: {sum(1 for e in self.salvage_log if e['status'] == 'success')}")
        print(f"✗ Failed: {sum(1 for e in self.salvage_log if e['status'] == 'error')}")
        print(f"\n✓ Salvage log: {log_path}")
        print(f"✓ Recovery directory: {self.recovery_dir}")
        
        if secrets_rotation_needed:
            print(f"\n⚠️  CRITICAL: Review secrets rotation plan immediately!")


if __name__ == "__main__":
    repo_root = Path(__file__).parent
    salvage = SalvageOperation(repo_root)
    salvage.run()
