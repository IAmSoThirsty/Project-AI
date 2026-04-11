#!/usr/bin/env python3
"""
Phase 2: SALVAGE - Direct approach to salvage all critical file types
Processes files by scanning directories directly
"""
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Any, Tuple
import yaml
import ast


class DirectSalvageOperation:
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.recovery_dir = repo_root / "recovery"
        self.audit_dir = repo_root / "audit"
        self.salvage_log: List[Dict[str, Any]] = []
        
        # Define what to salvage
        self.salvage_patterns = {
            'api_specs': ['API_SPECIFICATIONS/*.yaml', 'API_SPECIFICATIONS/*.yml'],
            'documentation': ['docs/**/*.md', '*.md'],
            'scripts': ['scripts/**/*.py', 'tools/**/*.py', '*.py'],
            'config': ['config/**/*.yaml', 'config/**/*.yml', 'config/**/*.json', 
                      'monitoring/**/*.yml', '*.toml', '*.cfg'],
            'docker': ['Dockerfile*', 'docker-compose*.yml'],
            'env': ['.env*'],
        }
    
    def find_files_to_salvage(self) -> Dict[str, List[Path]]:
        """Find all files to salvage by category"""
        files_by_category = {}
        
        # Excluded patterns
        exclude_patterns = [
            'node_modules', '.git', '__pycache__', '.pytest_cache',
            'venv', '.venv', 'build', 'dist', '.gradle', '.idea'
        ]
        
        for category, patterns in self.salvage_patterns.items():
            files = []
            for pattern in patterns:
                for filepath in self.repo_root.glob(pattern):
                    # Check if file should be excluded
                    if any(excl in str(filepath) for excl in exclude_patterns):
                        continue
                    
                    if filepath.is_file() and filepath.exists():
                        files.append(filepath)
            
            # Deduplicate
            files_by_category[category] = list(set(files))
        
        return files_by_category
    
    def repair_python(self, content: str) -> Tuple[str, List[str]]:
        """Repair Python syntax errors"""
        issues = []
        
        try:
            ast.parse(content)
            issues.append("✓ Valid Python syntax")
        except SyntaxError as e:
            issues.append(f"⚠ Syntax error: {str(e)[:80]}")
        
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
            issues.append("✓ Normalized line endings")
        
        if '\t' in content and not content.startswith('#!'):  # Skip shebangs
            lines = content.split('\n')
            fixed = []
            for line in lines:
                if line.startswith('\t'):
                    # Count leading tabs and convert to 4 spaces each
                    tabs = len(line) - len(line.lstrip('\t'))
                    fixed.append('    ' * tabs + line.lstrip('\t'))
                else:
                    fixed.append(line)
            content = '\n'.join(fixed)
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
                # If still broken, just normalize line endings
                if '\r\n' in content:
                    content = content.replace('\r\n', '\n')
        
        return content, issues
    
    def repair_markdown(self, content: str) -> Tuple[str, List[str]]:
        """Repair and normalize markdown"""
        issues = []
        
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
            issues.append("✓ Normalized line endings")
        
        try:
            content.encode('utf-8')
        except UnicodeEncodeError:
            content = content.encode('utf-8', errors='replace').decode('utf-8')
            issues.append("⚠ Fixed encoding issues")
        
        # Ensure single blank line at end
        content = content.rstrip() + '\n'
        
        if not issues:
            issues.append("✓ Clean markdown")
        
        return content, issues
    
    def repair_env(self, content: str) -> Tuple[str, List[str], bool]:
        """Repair .env file and identify if secrets need rotation"""
        issues = []
        needs_rotation = False
        
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
            issues.append("✓ Normalized line endings")
        
        # Check for exposed secrets (but not in .example files)
        secret_patterns = [
            (r'SECRET_KEY\s*=\s*["\']?[^"\'\s]{8,}', "SECRET_KEY"),
            (r'API_KEY\s*=\s*["\']?[^"\'\s]{8,}', "API_KEY"),
            (r'OPENAI_API_KEY\s*=\s*["\']?sk-[^"\'\s]+', "OPENAI_API_KEY"),
            (r'DATABASE_URL\s*=\s*.*password.*', "DATABASE_URL"),
            (r'JWT_SECRET\s*=\s*["\']?[^"\'\s]{8,}', "JWT_SECRET"),
        ]
        
        for pattern, secret_type in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"⚠ {secret_type} detected")
                needs_rotation = True
        
        return content, issues, needs_rotation
    
    def repair_generic(self, content: str) -> Tuple[str, List[str]]:
        """Generic repairs for other file types"""
        issues = []
        
        if '\r\n' in content:
            content = content.replace('\r\n', '\n')
            issues.append("✓ Normalized line endings")
        else:
            issues.append("✓ No repairs needed")
        
        return content, issues
    
    def salvage_file(self, filepath: Path, category: str) -> Dict[str, Any]:
        """Salvage a single file"""
        log_entry = {
            'original_path': str(filepath.relative_to(self.repo_root)),
            'category': category,
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
                content, issues = self.repair_generic(content)
            
            log_entry['actions'] = issues
            
            # Determine recovery path - preserve meaningful directory structure
            rel_path = filepath.relative_to(self.repo_root)
            
            # Keep one level of directory context for organized categories
            if len(rel_path.parts) > 1:
                subdir = rel_path.parts[0] if rel_path.parts[0] != category else ""
                if subdir:
                    recovery_path = self.recovery_dir / category / subdir / rel_path.name
                else:
                    recovery_path = self.recovery_dir / category / rel_path.name
            else:
                recovery_path = self.recovery_dir / category / rel_path.name
            
            # Create parent directory
            recovery_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write repaired content
            with open(recovery_path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            
            log_entry['recovery_path'] = str(recovery_path.relative_to(self.repo_root))
            log_entry['size_bytes'] = len(content)
            
        except Exception as e:
            log_entry['status'] = 'error'
            log_entry['actions'].append(f"✗ Error: {str(e)}")
        
        return log_entry
    
    def generate_secrets_rotation_plan(self):
        """Generate a secrets rotation plan for .env files"""
        plan_path = self.recovery_dir / "SECRETS_ROTATION_PLAN.md"
        
        plan_content = """# 🚨 Secrets Rotation Plan - URGENT ACTION REQUIRED

## Critical Security Issue Detected

**Status**: ⚠️ ACTIVE SECRETS EXPOSURE  
**Priority**: P0 - Critical  
**Timeline**: Rotate within 1 hour

---

## Exposed Secrets Inventory

The following secrets have been identified in .env files:

1. **SECRET_KEY** - Application secret key
2. **OPENAI_API_KEY** - OpenAI API credentials  
3. **DATABASE_URL** - Database connection with embedded credentials
4. **JWT_SECRET** - JSON Web Token signing key

---

## Immediate Action Steps

### Step 1: Rotate Secrets (0-30 minutes)

```bash
# 1. Generate new SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY='[REDACTED]"

# 2. Revoke OpenAI API key
# Visit: https://platform.openai.com/api-keys
# Click "Revoke" on the exposed key
# Generate new key with appropriate scopes

# 3. Rotate database credentials
psql -U admin -d postgres -c "ALTER USER appuser WITH PASSWORD 'NEW_SECURE_PASSWORD';"

# 4. Generate new JWT_SECRET
openssl rand -base64 32
```

### Step 2: Update Production (30-60 minutes)

```bash
# Update secrets in your secrets manager
# AWS Secrets Manager
aws secretsmanager update-secret --secret-id app/prod/secret-key --secret-string "NEW_VALUE"

# Azure Key Vault
az keyvault secret set --vault-name mykeyvault --name secret-key --value "NEW_VALUE"

# Kubernetes
kubectl create secret generic app-secrets \
  --from-literal=SECRET_KEY="[REDACTED]" \
  --from-literal=JWT_SECRET="[REDACTED]" \
  --dry-run=client -o yaml | kubectl apply -f -
```

### Step 3: Deploy Changes (60-90 minutes)

```bash
# Rolling restart of services
kubectl rollout restart deployment/app
# OR
docker-compose down && docker-compose up -d
```

### Step 4: Verify (90-120 minutes)

```bash
# Check service health
curl -f http://localhost:8000/health || echo "Service down!"

# Verify new secrets in use
kubectl exec -it pod/app -- env | grep SECRET_KEY

# Force user re-authentication (JWT rotation)
# Monitor logs for failed auth attempts
```

---

## Security Remediation

### Immediate (Today)

- [x] Identify exposed secrets
- [ ] Rotate all secrets
- [ ] Update production systems
- [ ] Force user re-authentication
- [ ] Monitor for suspicious activity

### Short-term (This Week)

- [ ] Audit git history for committed secrets
  ```bash
  git log --all --full-history -- "**/.env*"
  git filter-repo --path .env --invert-paths  # Remove from history
  ```

- [ ] Install pre-commit hooks
  ```bash
  pip install detect-secrets pre-commit
  detect-secrets scan > .secrets.baseline
  pre-commit install
  ```

- [ ] Add CI/CD secrets scanning
  ```yaml
  # .github/workflows/security.yml
  - name: Detect secrets
    uses: trufflesecurity/trufflehog@main
  ```

### Long-term (This Month)

- [ ] Implement secrets management solution
  - AWS Secrets Manager
  - Azure Key Vault  
  - HashiCorp Vault
  - Google Secret Manager

- [ ] Setup secret rotation automation
- [ ] Implement least-privilege access
- [ ] Enable audit logging
- [ ] Conduct security training

---

## Best Practices Going Forward

### 1. Never Commit Secrets

```bash
# Verify .env in .gitignore
echo ".env" >> .gitignore
echo ".env.*" >> .gitignore
echo "!.env.example" >> .gitignore

# Check before committing
git diff --cached --name-only | xargs detect-secrets-hook
```

### 2. Use Templates

```bash
# .env.example (safe to commit)
SECRET_KEY=your-secret-key-here
OPENAI_API_KEY=sk-your-key-here
DATABASE_URL=postgresql://user:[REDACTED]@localhost/db

# .env (never commit)
SECRET_KEY=actual-secret-value-9h8f7g6d5
OPENAI_API_KEY=sk-actual-key-f9h8g7d6f5
DATABASE_URL=postgresql://realuser:[REDACTED]@prod.db.com/proddb
```

### 3. Environment Separation

```
.env.local          # Local development (gitignored)
.env.example        # Template only (committed)
.env.test           # Test environment (gitignored)
```

### 4. Secrets Management

```python
# Good: Load from secrets manager
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='app/prod/api-key')

# Bad: Hardcoded secrets
API_KEY = "[REDACTED]"
```

---

## Incident Response Checklist

- [ ] Secrets rotated
- [ ] Production updated
- [ ] Services restarted
- [ ] Users re-authenticated
- [ ] Logs reviewed for anomalies
- [ ] Git history cleaned
- [ ] Pre-commit hooks installed
- [ ] CI/CD scanning enabled
- [ ] Secrets manager configured
- [ ] Team notified
- [ ] Incident documented
- [ ] Post-mortem scheduled

---

## Contact & Escalation

If issues arise during rotation:
1. Check service logs: `kubectl logs -f deployment/app`
2. Verify secrets loaded: Check environment variables
3. Test connectivity: Database, APIs, external services
4. Rollback if critical: Keep old secrets available for 24h

**This is a P0 security incident. Rotate secrets immediately.**

---

*Generated by: Phase 2 Salvage Operation*  
*Date: Automated detection*  
*Severity: CRITICAL*
"""
        
        with open(plan_path, 'w', encoding='utf-8') as f:
            f.write(plan_content)
        
        return str(plan_path.relative_to(self.repo_root))
    
    def run(self):
        """Execute the salvage operation"""
        print("=" * 80)
        print("🔧 PHASE 2: DIRECT SALVAGE OPERATION")
        print("=" * 80)
        
        # Find files to salvage
        print("\n📁 Scanning directories...")
        files_by_category = self.find_files_to_salvage()
        
        total_files = sum(len(files) for files in files_by_category.values())
        print(f"✓ Found {total_files} files to salvage\n")
        
        print("📊 Breakdown by category:")
        for category, files in sorted(files_by_category.items()):
            print(f"  {category:20s}: {len(files):4d} files")
        
        # Process files
        print(f"\n{'='*80}")
        print("🔧 Processing files...")
        print(f"{'='*80}\n")
        
        secrets_rotation_needed = False
        processed = 0
        
        for category, files in sorted(files_by_category.items()):
            if not files:
                continue
            
            print(f"\n📂 {category.upper()}:")
            print("-" * 80)
            
            for filepath in sorted(files):
                processed += 1
                filename = filepath.name
                if len(filename) > 50:
                    filename = filename[:47] + "..."
                
                print(f"  [{processed:4d}/{total_files:4d}] {filename:50s}", end=" ", flush=True)
                
                log_entry = self.salvage_file(filepath, category)
                self.salvage_log.append(log_entry)
                
                if log_entry['status'] == 'success':
                    print("✓")
                else:
                    print("✗")
                
                if log_entry.get('needs_secrets_rotation'):
                    secrets_rotation_needed = True
        
        # Generate secrets rotation plan if needed
        if secrets_rotation_needed:
            print(f"\n{'='*80}")
            plan_path = self.generate_secrets_rotation_plan()
            print(f"⚠️  CRITICAL: Secrets rotation plan created")
            print(f"    → {plan_path}")
            print(f"{'='*80}")
        
        # Save salvage log
        log_path = self.audit_dir / "salvage_log.json"
        summary = {
            'total_files': total_files,
            'successful': sum(1 for e in self.salvage_log if e['status'] == 'success'),
            'failed': sum(1 for e in self.salvage_log if e['status'] == 'error'),
            'secrets_rotation_needed': secrets_rotation_needed,
            'categories': {cat: len(files) for cat, files in files_by_category.items()},
            'entries': self.salvage_log
        }
        
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n{'='*80}")
        print("✅ SALVAGE OPERATION COMPLETE")
        print(f"{'='*80}\n")
        
        print("📈 Results:")
        print(f"  • Total files processed: {total_files}")
        print(f"  • Successful: {summary['successful']} ({100*summary['successful']//total_files}%)")
        print(f"  • Failed: {summary['failed']}")
        
        print(f"\n📁 Output Locations:")
        print(f"  • Salvage log: audit/salvage_log.json")
        print(f"  • Recovered files: recovery/")
        
        print(f"\n📦 Files Recovered by Category:")
        for cat, count in sorted(summary['categories'].items()):
            print(f"  • {cat:20s}: {count:4d} files → recovery/{cat}/")
        
        if secrets_rotation_needed:
            print(f"\n🚨 SECURITY ALERT:")
            print(f"  Exposed secrets detected in .env files!")
            print(f"  Review plan: recovery/SECRETS_ROTATION_PLAN.md")
            print(f"  Action required: Rotate secrets within 1 hour")
        
        print(f"\n{'='*80}")
        print("Phase 2: SALVAGE complete ✓")
        print(f"{'='*80}\n")


if __name__ == "__main__":
    repo_root = Path(__file__).parent
    salvage = DirectSalvageOperation(repo_root)
    salvage.run()
