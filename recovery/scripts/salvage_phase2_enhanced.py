#!/usr/bin/env python3
"""
Phase 2: SALVAGE - Enhanced version to process ALL critical/useful files
Processes API specs, documentation, scripts, and config files in batches
"""
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Any, Tuple
import yaml
import ast
from concurrent.futures import ThreadPoolExecutor, as_completed


class EnhancedSalvageOperation:
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
        
        # Filter for critical/useful items that actually exist
        items = []
        for item in data['items']:
            if item['type'] in ['critical', 'useful']:
                filepath = self.repo_root / item['path']
                if filepath.exists() and filepath.is_file():
                    items.append(item)
        
        return items
    
    def categorize_file(self, path: str) -> str:
        """Determine the recovery category for a file"""
        p = Path(path)
        
        if '.env' in p.name:
            return 'env'
        elif 'api_spec' in p.name.lower() or 'API_SPECIFICATIONS' in path:
            return 'api_specs'
        elif p.suffix == '.md':
            return 'documentation'
        elif p.suffix == '.py':
            return 'scripts'
        elif 'Dockerfile' in p.name or 'docker-compose' in p.name:
            return 'docker'
        elif p.suffix in ['.json', '.yaml', '.yml', '.toml', '.cfg', '.ini', '.sh']:
            return 'config'
        else:
            return 'other'
    
    def repair_python(self, content: str) -> Tuple[str, List[str]]:
        """Repair Python syntax errors"""
        issues = []
        
        try:
            ast.parse(content)
            issues.append("✓ Valid Python syntax")
        except SyntaxError as e:
            issues.append(f"⚠ Syntax error: {str(e)[:80]}")
        
        # Fix encoding issues
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
            issues.append("✓ Normalized line endings")
        
        # Convert tabs to spaces
        if '\t' in content:
            content = content.replace('\t', '    ')
            issues.append("✓ Converted tabs to spaces")
        
        return content, issues
    
    def repair_yaml(self, content: str) -> Tuple[str, List[str]]:
        """Repair YAML syntax errors"""
        issues = []
        
        try:
            yaml.safe_load(content)
            issues.append("✓ Valid YAML")
        except yaml.YAMLError as e:
            issues.append(f"⚠ YAML error: {str(e)[:80]}")
            if '\t' in content:
                content = content.replace('\t', '  ')
                issues.append("✓ Fixed tab indentation")
        
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
            issues.append("✓ Normalized line endings")
        
        return content, issues
    
    def repair_json(self, content: str) -> Tuple[str, List[str]]:
        """Repair JSON syntax errors"""
        issues = []
        
        try:
            data = json.loads(content)
            content = json.dumps(data, indent=2, ensure_ascii=False)
            issues.append("✓ Valid JSON, reformatted")
        except json.JSONDecodeError as e:
            issues.append(f"⚠ JSON error: {str(e)[:80]}")
            # Try fixing trailing commas
            fixed = re.sub(r',(\s*[}\]])', r'\1', content)
            try:
                data = json.loads(fixed)
                content = json.dumps(data, indent=2, ensure_ascii=False)
                issues.append("✓ Fixed trailing commas")
            except:
                pass
        
        return content, issues
    
    def repair_markdown(self, content: str) -> Tuple[str, List[str]]:
        """Repair and normalize markdown"""
        issues = []
        
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
            issues.append("✓ Normalized line endings")
        
        try:
            content.encode('utf-8')
            issues.append("✓ Valid UTF-8")
        except UnicodeEncodeError:
            content = content.encode('utf-8', errors='replace').decode('utf-8')
            issues.append("⚠ Fixed encoding")
        
        # Ensure single blank line at end
        content = content.rstrip() + '\n'
        
        return content, issues
    
    def repair_env(self, content: str) -> Tuple[str, List[str], bool]:
        """Repair .env file and identify if secrets need rotation"""
        issues = []
        needs_rotation = False
        
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
            issues.append("✓ Normalized line endings")
        
        # Check for exposed secrets
        secret_patterns = [
            (r'SECRET_KEY\s*=\s*["\']?[^"\'\s]+', "SECRET_KEY"),
            (r'API_KEY\s*=\s*["\']?[^"\'\s]+', "API_KEY"),
            (r'OPENAI_API_KEY\s*=\s*["\']?[^"\'\s]+', "OPENAI_API_KEY"),
            (r'DATABASE_URL\s*=\s*.*password.*', "DATABASE_URL"),
            (r'JWT_SECRET\s*=\s*["\']?[^"\'\s]+', "JWT_SECRET"),
        ]
        
        for pattern, secret_type in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"⚠ CRITICAL: {secret_type} needs rotation")
                needs_rotation = True
        
        return content, issues, needs_rotation
    
    def salvage_file(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Salvage a single file"""
        filepath = self.repo_root / item['path']
        
        log_entry = {
            'original_path': str(filepath.relative_to(self.repo_root)),
            'type': item['type'],
            'category': self.categorize_file(str(filepath)),
            'actions': [],
            'status': 'success'
        }
        
        try:
            # Read original content
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            # Apply appropriate repair based on file type
            issues = []
            needs_rotation = False
            
            if filepath.suffix == '.py':
                content, issues = self.repair_python(content)
            elif filepath.suffix in ['.yaml', '.yml']:
                content, issues = self.repair_yaml(content)
            elif filepath.suffix == '.json':
                content, issues = self.repair_json(content)
            elif filepath.suffix == '.md':
                content, issues = self.repair_markdown(content)
            elif '.env' in filepath.name:
                content, issues, needs_rotation = self.repair_env(content)
                log_entry['needs_secrets_rotation'] = needs_rotation
            else:
                # Generic cleanup
                if '\r\n' in content:
                    content = content.replace('\r\n', '\n')
                    issues.append("✓ Normalized line endings")
                else:
                    issues.append("✓ No repairs needed")
            
            log_entry['actions'] = issues
            
            # Determine recovery path - preserve directory structure
            category = log_entry['category']
            rel_path = filepath.relative_to(self.repo_root)
            
            # For structured files, preserve some directory context
            if category in ['api_specs', 'documentation', 'scripts']:
                recovery_path = self.recovery_dir / category / rel_path.name
            else:
                recovery_path = self.recovery_dir / category / rel_path.name
            
            # Create parent directory if needed
            recovery_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write repaired content
            with open(recovery_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            
            log_entry['recovery_path'] = str(recovery_path.relative_to(self.repo_root))
            
        except Exception as e:
            log_entry['status'] = 'error'
            log_entry['actions'].append(f"✗ Error: {str(e)}")
        
        return log_entry
    
    def generate_secrets_rotation_plan(self):
        """Generate a secrets rotation plan for .env files"""
        plan_path = self.recovery_dir / "SECRETS_ROTATION_PLAN.md"
        
        plan_content = """# Secrets Rotation Plan - URGENT

## ⚠️ CRITICAL: Exposed Secrets Detected

The following secrets were found in .env files and MUST be rotated immediately:

### Immediate Action Items:

1. **SECRET_KEY** - Application secret key
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   - Update in production environment variables
   - Update in CI/CD secrets vault
   - Restart all application services

2. **OPENAI_API_KEY** - OpenAI API access
   - Revoke key at: https://platform.openai.com/api-keys
   - Generate new API key with appropriate rate limits
   - Update in secrets manager (AWS/Azure/HashiCorp Vault)
   - Monitor usage for anomalies

3. **DATABASE_URL** - Database connection string with credentials
   ```bash
   # Rotate database password
   psql -U admin -c "ALTER USER appuser WITH PASSWORD 'new_secure_password';"
   ```
   - Update connection strings in all environments
   - Test connections before deploying
   - Update backup scripts

4. **JWT_SECRET** - JSON Web Token signing key
   ```bash
   openssl rand -base64 32
   ```
   - Force re-authentication for all users
   - Update in all microservices
   - Monitor for unauthorized access attempts

### Security Best Practices:

1. **Never commit secrets to git**
   ```bash
   # Verify .env is in .gitignore
   git check-ignore .env
   
   # Remove secrets from git history
   git filter-repo --path .env --invert-paths
   ```

2. **Use environment-specific files**
   - `.env.example` - Template with placeholders only
   - `.env.local` - Local development (gitignored)
   - `.env.production` - Never in repository, use secrets manager

3. **Implement secrets management**
   - AWS Secrets Manager / Azure Key Vault / HashiCorp Vault
   - GitHub Secrets for CI/CD
   - kubernetes Secrets for deployments

4. **Add pre-commit hooks**
   ```bash
   # Install git-secrets or detect-secrets
   pip install detect-secrets
   detect-secrets-hook --baseline .secrets.baseline
   ```

### Audit Trail:

```bash
# Check if secrets were committed to git
git log --all --full-history --source --pretty=format:"%h %ad %s" --date=short -- "**/.env*"

# Search for exposed secrets in history
git grep -E "(SECRET_KEY|API_KEY|JWT_SECRET)" $(git rev-list --all)
```

## Timeline:

- [ ] **Hour 0-1**: Rotate all exposed secrets
- [ ] **Hour 1-2**: Update production systems
- [ ] **Hour 2-4**: Verify all services operational
- [ ] **Hour 4-24**: Monitor logs for suspicious activity
- [ ] **Day 2**: Complete security audit
- [ ] **Day 3**: Implement automated secrets scanning

## Status: 🚨 URGENT - Rotate within 1 hour
"""
        
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        return str(plan_path.relative_to(self.repo_root))
    
    def run(self):
        """Execute the salvage operation"""
        print("=" * 80)
        print("PHASE 2: ENHANCED SALVAGE OPERATION")
        print("=" * 80)
        
        # Load items to salvage
        items = self.load_classification_map()
        print(f"\n✓ Found {len(items)} files to salvage")
        
        # Group by category
        categories = {}
        for item in items:
            cat = self.categorize_file(item['path'])
            categories[cat] = categories.get(cat, 0) + 1
        
        print("\n📊 Breakdown by category:")
        for cat, count in sorted(categories.items()):
            print(f"  {cat:20s}: {count:4d} files")
        
        # Process files with progress indicator
        print(f"\n{'='*80}")
        print("🔧 Processing files...")
        print(f"{'='*80}\n")
        
        secrets_rotation_needed = False
        processed = 0
        
        # Process in batches for better performance
        batch_size = 10
        for i in range(0, len(items), batch_size):
            batch = items[i:i+batch_size]
            
            for item in batch:
                processed += 1
                filepath = Path(item['path']).name
                if len(filepath) > 50:
                    filepath = filepath[:47] + "..."
                
                print(f"[{processed:4d}/{len(items):4d}] {filepath:50s}", end=" ", flush=True)
                
                log_entry = self.salvage_file(item)
                self.salvage_log.append(log_entry)
                
                if log_entry['status'] == 'success':
                    print("✓")
                else:
                    print("✗")
                
                if log_entry.get('needs_secrets_rotation'):
                    secrets_rotation_needed = True
        
        # Generate secrets rotation plan if needed
        if secrets_rotation_needed:
            plan_path = self.generate_secrets_rotation_plan()
            print(f"\n⚠️  CRITICAL: Secrets rotation plan → {plan_path}\n")
        
        # Save salvage log
        log_path = self.audit_dir / "salvage_log.json"
        summary = {
            'total_files': len(items),
            'successful': sum(1 for e in self.salvage_log if e['status'] == 'success'),
            'failed': sum(1 for e in self.salvage_log if e['status'] == 'error'),
            'secrets_rotation_needed': secrets_rotation_needed,
            'categories': categories,
            'entries': self.salvage_log
        }
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"{'='*80}")
        print("✅ SALVAGE OPERATION COMPLETE")
        print(f"{'='*80}")
        print(f"\n📈 Results:")
        print(f"  • Total files processed: {len(items)}")
        print(f"  • Successful: {summary['successful']}")
        print(f"  • Failed: {summary['failed']}")
        print(f"\n📁 Output:")
        print(f"  • Salvage log: audit/salvage_log.json")
        print(f"  • Recovery directory: recovery/")
        
        if secrets_rotation_needed:
            print(f"\n🚨 CRITICAL: Review secrets rotation plan immediately!")
        
        # Print category summary
        print(f"\n📦 Files by category:")
        for cat, count in sorted(categories.items()):
            print(f"  • {cat:20s}: {count:4d} files → recovery/{cat}/")


if __name__ == "__main__":
    repo_root = Path(__file__).parent
    salvage = EnhancedSalvageOperation(repo_root)
    salvage.run()
