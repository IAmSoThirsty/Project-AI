# Documentation Maintenance Scripts

This directory contains production-grade scripts for automated documentation maintenance in Project-AI.

## 📋 Overview

The documentation maintenance system consists of three integrated components:

1. **Test Documentation Updater** - Parses CI test artifacts and updates documentation
2. **Historical Documentation Organizer** - Moves obsolete docs to historical archive
3. **Master Maintenance System** - Orchestrates both components

## 🚀 Quick Start

### Run Complete Maintenance (Recommended)

```bash
# Run full maintenance (updates test docs + organizes historical docs)
python scripts/run_documentation_maintenance.py

# Dry run to preview changes
python scripts/run_documentation_maintenance.py --dry-run

# Skip git commit
python scripts/run_documentation_maintenance.py --no-commit
```

### Run Individual Components

```bash
# Update test documentation only
python scripts/update_test_documentation.py

# Organize historical docs only
python scripts/organize_historical_docs.py

# Check files older than 14 days
python scripts/organize_historical_docs.py --age-threshold 14
```

## 📦 Scripts

### 1. `run_documentation_maintenance.py` ⭐

**Master orchestration script** - Run this after CI tests complete.

**Features:**
- Runs test documentation updater
- Runs historical docs organizer  
- Generates master report
- Commits changes to git

**Usage:**
```bash
python scripts/run_documentation_maintenance.py [OPTIONS]

Options:
  --dry-run, -d           Preview changes without making them
  --no-commit             Skip git commit step
  --check-age             Enable age-based checking (default: enabled)
  --no-check-age          Disable age-based checking
  --age-threshold DAYS    Age threshold in days (default: 7)
  --verbose, -v           Enable verbose logging
```

**Outputs:**
- `documentation_maintenance_report.md` - Master report
- `test_documentation_update_summary.md` - Test updates
- `historical_docs_organization_report.md` - Historical org
- `documentation_maintenance.log` - Combined log

---

### 2. `update_test_documentation.py`

**Test documentation updater** - Parses CI artifacts and updates docs.

**Features:**
- Multi-format parser (JSON, Markdown, JUnit XML, pytest JSON)
- Category-level pass/fail statistics
- Automated badge generation
- Failed test surfacing
- Reference-based documentation updates

**Configuration:** `.test-report-updater.config.json`

**Usage:**
```bash
python scripts/update_test_documentation.py [OPTIONS]

Options:
  --config, -c PATH       Path to config file (default: .test-report-updater.config.json)
  --dry-run, -d           Run without making changes
  --no-commit             Skip git commit step
  --verbose, -v           Enable verbose logging
```

**Artifact Sources:**
- `ci-reports/*.json` - CI test reports
- `test_execution_reports/EXECUTION_SUMMARY.md` - Execution summary
- `test-results.json` - pytest JSON results
- `test-results.xml` - JUnit XML results

**Documentation Targets:**
- `README.md` - Test badges and summary
- `COMPLETE_TEST_SUITE_SUMMARY.md` - Overall stats and category breakdown
- `security_test_category_pass_fail_report.md` - Detailed pass/fail table

**Outputs:**
- Updated documentation files
- `test_documentation_update_summary.md`
- `test_report_updater.log`

---

### 3. `organize_historical_docs.py`

**Historical documentation organizer** - Moves obsolete docs to archive.

**Features:**
- Pattern-based obsolescence detection
- Age-based assessment (configurable threshold)
- Usefulness verification
- Reference updating
- Historical index generation

**Usage:**
```bash
python scripts/organize_historical_docs.py [OPTIONS]

Options:
  --dry-run, -d           Preview changes without making them
  --interactive, -i       Ask before moving each file
  --check-age             Enable age-based checking (default: enabled)
  --no-check-age          Disable age-based checking
  --age-threshold DAYS    Age threshold in days (default: 7)
  --verbose, -v           Enable verbose logging
```

**Obsolescence Criteria:**
1. **Pattern matching:** Files matching `*_COMPLETE.md`, `*_SUMMARY.md`, `*_IMPLEMENTATION.md`, etc.
2. **Content keywords:** Files containing "complete", "summary", "implemented", etc.
3. **Age-based:** Files older than threshold (7 days default) that are not actively maintained

**Usefulness Assessment:**
- Checks for active maintenance indicators
- Verifies recent update markers
- Analyzes content for utility
- Preserves essential documentation

**Protected Files:**
- `README.md`
- `CHANGELOG.md`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `CONSTITUTION.md`
- `COMPLETE_TEST_SUITE_SUMMARY.md`
- `DEVELOPER_QUICK_REFERENCE.md`
- `PROGRAM_SUMMARY.md`
- `TECHNICAL_WHITE_PAPER.md`

**Outputs:**
- `docs/historical/` - Archive directory
- `docs/historical/README.md` - Historical index
- `historical_docs_organization_report.md`
- `historical_docs_organizer.log`

---

## ⚙️ Configuration

### Test Documentation Updater Config

Location: `.test-report-updater.config.json`

```json
{
  "artifact_sources": {
    "ci_reports": {
      "enabled": true,
      "path": "ci-reports/*.json",
      "format": "json"
    }
  },
  "documentation_targets": [
    {
      "path": "README.md",
      "sections": {
        "test_badges": {
          "markers": ["<!-- TEST_BADGES_START -->", "<!-- TEST_BADGES_END -->"]
        }
      }
    }
  ],
  "badge_templates": {
    "tests_total": "![Tests](https://img.shields.io/badge/tests-{total}-{color})"
  }
}
```

**Key Sections:**
- `artifact_sources` - Define where to find test results
- `documentation_targets` - Specify which files to update
- `badge_templates` - Customize badge URLs
- `output` - Configure commit behavior

---

## 🔄 CI/CD Integration

### GitHub Actions Workflow

The system integrates with GitHub Actions via `.github/workflows/update-test-docs.yml`:

**Triggers:**
- After test workflows complete (workflow_run)
- Manual dispatch
- Daily schedule (2 AM UTC)

**Process:**
1. Checkout repository
2. Set up Python
3. Run documentation maintenance
4. Upload reports as artifacts
5. Create PR with changes
6. Auto-merge if checks pass

**Manual Trigger:**
```bash
gh workflow run update-test-docs.yml
```

**With Options:**
```bash
gh workflow run update-test-docs.yml \
  -f dry_run=true \
  -f skip_commit=false
```

---

## 📊 Reports

### Master Report

`documentation_maintenance_report.md` - Overview of all maintenance activities

### Test Documentation Update Report

`test_documentation_update_summary.md` - Detailed test statistics

**Contents:**
- Overall statistics
- Category breakdown
- Updated documentation files
- Configuration used

### Historical Documentation Organization Report

`historical_docs_organization_report.md` - Archive activity details

**Contents:**
- Age assessment results
- Files moved to historical
- References updated
- Active documents list

---

## 🔍 Examples

### Dry Run Before Committing

```bash
# Preview what would change
python scripts/run_documentation_maintenance.py --dry-run

# Review the reports
cat documentation_maintenance_report.md

# Run for real if satisfied
python scripts/run_documentation_maintenance.py
```

### Check Old Files

```bash
# Find and assess files older than 30 days
python scripts/organize_historical_docs.py \
  --age-threshold 30 \
  --dry-run

# Move them if appropriate
python scripts/organize_historical_docs.py \
  --age-threshold 30
```

### Update Only Test Docs

```bash
# Just update test documentation
python scripts/update_test_documentation.py --verbose

# Check what was updated
git diff README.md COMPLETE_TEST_SUITE_SUMMARY.md
```

### Interactive Mode

```bash
# Review each file before moving
python scripts/organize_historical_docs.py --interactive
```

---

## 🛠️ Development

### Adding New Artifact Sources

Edit `.test-report-updater.config.json`:

```json
{
  "artifact_sources": {
    "my_custom_source": {
      "enabled": true,
      "path": "custom-reports/*.json",
      "format": "json",
      "priority": 5
    }
  }
}
```

### Adding New Documentation Targets

```json
{
  "documentation_targets": [
    {
      "path": "MY_DOC.md",
      "sections": {
        "my_section": {
          "markers": ["<!-- MY_SECTION_START -->", "<!-- MY_SECTION_END -->"]
        }
      }
    }
  ]
}
```

### Customizing Obsolescence Patterns

Edit `scripts/organize_historical_docs.py`:

```python
OBSOLETE_PATTERNS = [
    r'.*_COMPLETE\.md$',
    r'.*_SUMMARY\.md$',
    # Add your patterns here
]
```

---

## 🐛 Troubleshooting

### No Test Artifacts Found

**Problem:** Script reports no artifacts found

**Solution:**
1. Check that CI tests have run
2. Verify artifact paths in config
3. Ensure artifacts are committed or available

```bash
# Check for artifacts
ls -la ci-reports/
ls -la test-artifacts/
```

### References Not Updated

**Problem:** Old references remain after moving files

**Solution:**
1. Check that files were actually moved
2. Verify reference format (markdown links vs plain text)
3. Run organizer again with `--verbose`

```bash
# Find remaining references
grep -r "MOVED_FILE.md" *.md
```

### Git Commit Fails

**Problem:** Unable to commit changes

**Solution:**
1. Check git is configured
2. Verify file permissions
3. Ensure no conflicts

```bash
# Configure git
git config user.name "Your Name"
git config user.email "your@email.com"

# Check status
git status
```

---

## 📚 Additional Resources

- **Configuration Reference:** `.test-report-updater.config.json`
- **CI Workflow:** `.github/workflows/update-test-docs.yml`
- **Test Reports:** `ci-reports/`
- **Historical Archive:** `docs/historical/`

---

## 🔐 Security

- Scripts use read-only access to artifacts
- Git commits use configured credentials
- No external network calls (except git push)
- All file operations are logged

---

## 📝 License

Part of Project-AI - See main LICENSE file

---

*Generated for Project-AI Documentation Maintenance System v1.0.0*
