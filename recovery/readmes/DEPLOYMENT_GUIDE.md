# README Salvage Deployment Guide

## Quick Deployment

To deploy all recovered READMEs to their original locations:

```powershell

# Run deployment script

python deploy_readmes.py
```

Or manually:

```powershell

# Navigate to recovery directory

cd recovery\readmes

# For each file, restore to original location

# Example for critical files:

Copy-Item "src_governance_README.md" "..\..\src\governance\README.md" -Force
Copy-Item "src_app_core_README.md" "..\..\src\app\core\README.md" -Force
Copy-Item "data_README.md" "..\..\data\README.md" -Force
```

## Pre-Deployment Checklist

- [ ] Review `PHASE_2_README_SALVAGE_COMPLETE.md`
- [ ] Inspect sample READMEs in `recovery/readmes/`
- [ ] Verify template compliance
- [ ] Check critical module READMEs
- [ ] Backup existing READMEs (if any)

## Deployment Script

Create `deploy_readmes.py`:

```python
#!/usr/bin/env python3
import json
import shutil
from pathlib import Path

# Load salvage log

with open('audit/salvage_log_readmes.json', 'r') as f:
    log = json.load(f)

deployed = []
failed = []

# Deploy repaired READMEs

for item in log['repaired']:
    src = Path(item['recovery_path'])
    dst = Path(item['original_path'])
    
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        deployed.append(str(dst))
        print(f"✅ Deployed: {dst}")
    except Exception as e:
        failed.append({'path': str(dst), 'error': str(e)})
        print(f"❌ Failed: {dst} - {e}")

# Deploy new READMEs

for item in log['created']:
    src = Path(item['recovery_path'])
    dst = Path(item['path'])
    
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        deployed.append(str(dst))
        print(f"✅ Created: {dst}")
    except Exception as e:
        failed.append({'path': str(dst), 'error': str(e)})
        print(f"❌ Failed: {dst} - {e}")

print(f"\n📊 Deployment Summary:")
print(f"   Deployed: {len(deployed)}")
print(f"   Failed: {len(failed)}")

# Save deployment log

deployment_log = {
    'deployed': deployed,
    'failed': failed
}

with open('audit/deployment_log_readmes.json', 'w') as f:
    json.dump(deployment_log, f, indent=2)

print(f"\n📄 Deployment log saved to: audit/deployment_log_readmes.json")
```

## Post-Deployment Validation

```powershell

# Verify deployed files

python -c "import os; paths = ['src/governance/README.md', 'src/app/core/README.md', 'data/README.md']; [print(f'✅ {p}' if os.path.exists(p) else f'❌ {p}') for p in paths]"

# Run documentation linter (if available)

markdownlint **/*.md

# Check for broken links

markdown-link-check README.md
```

## Rollback Procedure

If issues are found:

```powershell

# Restore from backup

git checkout -- src/governance/README.md
git checkout -- src/app/core/README.md

# Or revert all

git checkout -- **/*README.md
```

## Git Commit

```bash
git add src/governance/README.md src/app/core/README.md
git add data/README.md tests/unit/README.md
git add infra/kubernetes/README.md infra/terraform/README.md
git commit -m "docs: salvage and repair 60 README files

- Repaired 45 broken READMEs with missing sections
- Created 15 new READMEs for critical modules
- Added installation, usage, API docs to all READMEs
- Ensured template compliance (title, overview, installation, usage, API, contributing, license)

Fleet B Phase 2 salvage operation complete.
Success rate: 93.8%

Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"
```

## Directory Structure After Deployment

```
src/
├── governance/
│   └── README.md ✅
├── app/
│   └── core/
│       └── README.md ✅
├── kernel/
│   └── README.md ✅
├── runtime/
│   └── README.md ✅
├── api/
│   └── README.md ✅
└── services/
    └── README.md ✅

tests/
├── unit/
│   └── README.md ✅
└── integration/
    └── README.md ✅

infra/
├── kubernetes/
│   └── README.md ✅
├── terraform/
│   └── README.md ✅
└── docker/
    └── README.md ✅

data/
├── README.md ✅
└── datasets/
    └── README.md ✅
```

## Support

For issues or questions:

1. Check `audit/salvage_log_readmes.json` for details
2. Review `PHASE_2_README_SALVAGE_COMPLETE.md`
3. Inspect recovered files in `recovery/readmes/`
