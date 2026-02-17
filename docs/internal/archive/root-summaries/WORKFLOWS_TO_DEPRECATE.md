# Workflows That Can Be Safely Deprecated

## Overview

Now that **Codex Deus Ultimate** (`codex-deus-ultimate.yml`) consolidates all functionality, the following 28 workflows can be deprecated.

## Migration Strategy

### Option 1: Move to Deprecated Folder (Recommended)

```bash
mkdir -p .github/workflows/deprecated
mv .github/workflows/<workflow>.yml .github/workflows/deprecated/
```

### Option 2: Delete Completely

```bash
git rm .github/workflows/<workflow>.yml
```

## Workflows to Deprecate

### ✅ Phase 2-9: Security & Testing (12 workflows)

1. **ci.yml** → Replaced by Phase 4-5 (Code Quality + Testing)
1. **ci-consolidated.yml** → Replaced by Phase 4-5
1. **security-consolidated.yml** → Replaced by Phase 2 (Pre-Flight Security)
1. **coverage-threshold-enforcement.yml** → Replaced by Phase 6 (Coverage Enforcement)
1. **adversarial-redteam.yml** → Replaced by Phase 3 (AI Safety)
1. **periodic-security-verification.yml** → Replaced by Phase 2 + Schedule
1. **trivy-container-security.yml** → Replaced by Phase 9 (Container Security)
1. **checkov-cloud-config.yml** → Replaced by Phase 9 (Container Security)
1. **node-ci.yml** → Replaced by Phase 5 (Node Tests)
1. **tarl-ci.yml** → Replaced by Phase 5 (Integration Tests)
1. **ai-model-security.yml** → Replaced by Phase 3 (Model Security)
1. **validate-guardians.yml** → Replaced by Phase 5 (Integration Tests)

### ✅ Phase 10-11: Automation (6 workflows)

13. **pr-automation-consolidated.yml** → Replaced by Phase 11 (PR Automation)
01. **issue-management-consolidated.yml** → Replaced by Phase 11 (Issue Triage)
01. **auto-create-branch-prs.yml** → Replaced by Phase 10 (Auto-Fix)
01. **dependabot.yml** → Keep for configuration, but automation in Phase 11
01. **post-merge-validation.yml** → Replaced by Phase 13 (Post-Merge)
01. **validate-waivers.yml** → Replaced by Phase 5 (Integration Tests)

### ✅ Phase 12: Release (5 workflows)

19. **build-release.yml** → Replaced by Phase 7 + 12 (Build + Release)
01. **sbom.yml** → Replaced by Phase 8 (SBOM Generation)
01. **sign-release-artifacts.yml** → Replaced by Phase 8 + 12 (Signing)
01. **release.yml** → Replaced by Phase 12 (Release Management)

### ✅ Phase 14: Cleanup (1 workflow)

23. **prune-artifacts.yml** → Replaced by Phase 14 (Artifact Cleanup)

### ✅ Specialty Workflows (5 workflows)

24. **main.yml** → Likely duplicate of ci.yml, verify before removing
01. **codex-deus-monolith.yml** → Predecessor to this workflow, can deprecate
01. **snn-mlops-cicd.yml** → Check if specialized logic needed, else deprecate
01. **gpt_oss_integration.yml** → Check if specialized logic needed, else deprecate
01. **jekyll-gh-pages.yml** → Keep if docs site needed, else deprecate

## Workflows to Keep

### Keep These - Not Replaced

- **dependabot.yml** - Configuration file for Dependabot (not a workflow, per se)
- Any project-specific workflows not covered by the 15 phases

## Deprecation Checklist

### Before Deprecating

- [ ] Verify Codex Deus Ultimate runs successfully on a test PR
- [ ] Confirm all security scans still execute
- [ ] Validate test coverage is maintained
- [ ] Check release process works end-to-end
- [ ] Review any custom logic in old workflows not covered

### During Deprecation

- [ ] Create `.github/workflows/deprecated/` directory
- [ ] Move old workflows to deprecated folder
- [ ] Update README.md to reference new workflow
- [ ] Update CONTRIBUTING.md with new workflow docs
- [ ] Update branch protection rules if needed

### After Deprecation

- [ ] Monitor Codex Deus Ultimate for 1-2 weeks
- [ ] Check for any missed functionality
- [ ] Delete deprecated folder after 30 days if no issues

## Migration Commands

```bash

# Create deprecated folder

mkdir -p .github/workflows/deprecated

# Move all deprecated workflows at once

mv .github/workflows/ci.yml .github/workflows/deprecated/
mv .github/workflows/ci-consolidated.yml .github/workflows/deprecated/
mv .github/workflows/security-consolidated.yml .github/workflows/deprecated/
mv .github/workflows/pr-automation-consolidated.yml .github/workflows/deprecated/
mv .github/workflows/issue-management-consolidated.yml .github/workflows/deprecated/
mv .github/workflows/coverage-threshold-enforcement.yml .github/workflows/deprecated/
mv .github/workflows/adversarial-redteam.yml .github/workflows/deprecated/
mv .github/workflows/periodic-security-verification.yml .github/workflows/deprecated/
mv .github/workflows/build-release.yml .github/workflows/deprecated/
mv .github/workflows/sbom.yml .github/workflows/deprecated/
mv .github/workflows/trivy-container-security.yml .github/workflows/deprecated/
mv .github/workflows/checkov-cloud-config.yml .github/workflows/deprecated/
mv .github/workflows/auto-create-branch-prs.yml .github/workflows/deprecated/
mv .github/workflows/post-merge-validation.yml .github/workflows/deprecated/
mv .github/workflows/sign-release-artifacts.yml .github/workflows/deprecated/
mv .github/workflows/prune-artifacts.yml .github/workflows/deprecated/
mv .github/workflows/node-ci.yml .github/workflows/deprecated/
mv .github/workflows/tarl-ci.yml .github/workflows/deprecated/
mv .github/workflows/ai-model-security.yml .github/workflows/deprecated/
mv .github/workflows/release.yml .github/workflows/deprecated/
mv .github/workflows/validate-guardians.yml .github/workflows/deprecated/
mv .github/workflows/validate-waivers.yml .github/workflows/deprecated/
mv .github/workflows/codex-deus-monolith.yml .github/workflows/deprecated/

# Check before moving these (may have special logic)

# mv .github/workflows/main.yml .github/workflows/deprecated/

# mv .github/workflows/snn-mlops-cicd.yml .github/workflows/deprecated/

# mv .github/workflows/gpt_oss_integration.yml .github/workflows/deprecated/

# mv .github/workflows/jekyll-gh-pages.yml .github/workflows/deprecated/

# Commit changes

git add .github/workflows/
git commit -m "🏛️ Migrate to Codex Deus Ultimate - Move old workflows to deprecated/"
git push
```

## Verification After Deprecation

```bash

# List active workflows

ls -1 .github/workflows/*.yml

# Expected output:

# codex-deus-ultimate.yml

# dependabot.yml (configuration)

# (any project-specific workflows to keep)

# List deprecated workflows

ls -1 .github/workflows/deprecated/*.yml

# Should show 23-28 deprecated workflows

```

## Rollback Plan

If issues are discovered after deprecation:

```bash

# Restore specific workflow

mv .github/workflows/deprecated/<workflow>.yml .github/workflows/

# Or restore all workflows

mv .github/workflows/deprecated/*.yml .github/workflows/

# Temporarily disable Codex Deus Ultimate

# Edit: .github/workflows/codex-deus-ultimate.yml

# Add at top: `if: false`

```

## Notes

- **dependabot.yml** is a configuration file, not a workflow file, but may appear in workflows directory
- Some repos use `main.yml` as an alias for `ci.yml` - check if duplicate before removing
- Review specialized workflows (SNN MLOps, GPT OSS) for unique logic not covered by Codex Deus Ultimate
- Jekyll workflow may be needed if you have a GitHub Pages docs site

## Timeline Recommendation

1. **Week 1**: Deploy Codex Deus Ultimate, monitor alongside old workflows
1. **Week 2**: Move old workflows to deprecated/ folder
1. **Week 3-4**: Monitor for any missed functionality
1. **Week 5**: Delete deprecated/ folder if no issues

______________________________________________________________________

**Created:** 2024 **Status:** Ready for Execution **Safety Level:** High (reversible via git history)
