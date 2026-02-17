# Branch Protection Configuration

This document outlines the required branch protection rules for the `main` branch to enforce the persistent repository defaults.

## Required Settings

### Branch Protection Rules for `main`

These settings must be configured in the GitHub repository settings under **Settings → Branches → Branch protection rules**.

#### 1. Require a pull request before merging

- ✅ **Enabled**
- Number of required approvals: 1 (automated by workflow)
- Dismiss stale pull request approvals when new commits are pushed: ✅ Enabled
- Require review from Code Owners: ⬜ Optional

#### 2. Require status checks to pass before merging

- ✅ **Enabled** (CRITICAL)
- Require branches to be up to date before merging: ✅ Enabled

**Required status checks:**

- `test` (from ci.yml)
- `lint` (from ci.yml)
- `tests` (from ci.yml)
- `Auto Review PR` (from auto-pr-handler.yml)
- `Validate Main Branch Health` (from post-merge-validation.yml)

#### 3. Require conversation resolution before merging

- ✅ **Enabled**
- All review comments must be resolved before merge

#### 4. Require signed commits

- ⬜ Optional (recommended for security)

#### 5. Require linear history

- ✅ **Enabled**
- Enforces squash merging or rebase, preventing merge commits
- Ensures clean, linear git history

#### 6. Include administrators

- ✅ **Enabled** (enforce rules for administrators too)

#### 7. Restrict who can push to matching branches

- ⬜ Optional (leave open for automated workflows)

#### 8. Allow force pushes

- ❌ **Disabled** (CRITICAL)
- Prevents force pushes that could break history

#### 9. Allow deletions

- ❌ **Disabled** (CRITICAL)
- Prevents accidental branch deletion

## Automated Enforcement

The following workflows enforce these requirements automatically:

### 1. **CI Workflow** (`ci.yml`)

- Runs comprehensive tests, linting, and type checking
- NO LONGER uses `|| true` - failures will properly block merges
- Status checks are now mandatory

### 2. **Auto PR Handler** (`auto-pr-handler.yml`)

- Automatically reviews ALL pull requests
- Runs tests and linting checks
- Auto-approves PRs that pass all checks
- Auto-merges passing PRs to main (no manual intervention)

### 3. **Auto-Fix Failures** (`auto-fix-failures.yml`)

- Detects failing CI checks
- Automatically applies fixes for:
  - Linting issues (ruff)
  - Import sorting (isort)
  - Code formatting (black)
- Commits fixes and triggers CI re-run
- Retries until checks pass

### 4. **Post-Merge Validation** (`post-merge-validation.yml`)

- Runs immediately after every merge to main
- Validates:
  - ✅ Zero merge conflicts
  - ✅ Zero linting errors
  - ✅ Zero test failures
- Generates comprehensive health report
- Creates urgent issues if main branch is unhealthy
- Comments on merged PRs with validation results

## Security Considerations

### Workflow File Protection

⚠️ **IMPORTANT**: While this automation provides significant efficiency, consider these security best practices:

1. **Workflow File Changes**: PRs that modify `.github/workflows/` files should be reviewed manually before merge

   - Add a required review for workflow changes via CODEOWNERS file
   - Example CODEOWNERS entry: `.github/workflows/* @IAmSoThirsty`

1. **External Contributors**: Consider requiring manual approval for PRs from external contributors

   - Can be configured in branch protection: "Require approval from specific users"
   - Protects against malicious PRs from unknown sources

1. **Sensitive Code Areas**: High-security code (authentication, encryption, payment processing) should have:

   - Required code owner reviews
   - Additional manual validation
   - Separate security scanning workflows

### Recommended CODEOWNERS Configuration

Create `.github/CODEOWNERS` file:

```

# Workflow files require owner review

/.github/workflows/ @IAmSoThirsty

# Security-sensitive code requires review

/src/app/core/user_manager.py @IAmSoThirsty
/src/app/core/command_override.py @IAmSoThirsty
```

This allows automation for most PRs while protecting critical files.

## Configuration Instructions

### Step 1: Configure Branch Protection via GitHub UI

1. Navigate to: `https://github.com/IAmSoThirsty/Project-AI/settings/branches`
1. Click "Add branch protection rule"
1. Enter branch name pattern: `main`
1. Configure all settings as listed above
1. Click "Create" or "Save changes"

### Step 2: Verify Automated Workflows

All workflows are already deployed in `.github/workflows/`:

- ✅ `ci.yml` - Enhanced with mandatory checks
- ✅ `auto-pr-handler.yml` - Enhanced for all PRs with auto-merge
- ✅ `auto-fix-failures.yml` - NEW: Automatic failure remediation
- ✅ `post-merge-validation.yml` - NEW: Post-merge health validation

### Step 3: Test the Configuration

1. Create a test PR with intentional linting errors
1. Verify auto-fix workflow detects and fixes errors
1. Verify CI blocks merge until fixes are applied
1. Verify auto-merge occurs after checks pass
1. Verify post-merge validation runs and reports health

## Workflow Behavior

### For All Pull Requests:

1. **PR Created/Updated**

   - `auto-pr-handler.yml` triggers
   - Runs lint and test checks
   - Comments with results
   - Approves if all checks pass

1. **CI Failures Detected**

   - `auto-fix-failures.yml` triggers
   - Attempts automatic fixes
   - Commits fixes to PR branch
   - CI re-runs automatically

1. **All Checks Pass**

   - Auto-approval granted
   - Auto-merge enabled
   - PR merges to main automatically (NO MANUAL APPROVAL NEEDED)

1. **Merge Complete**

   - `post-merge-validation.yml` triggers on main
   - Validates main branch health
   - Reports:
     - ✅ Zero conflicts
     - ✅ Zero linting errors
     - ✅ Zero test failures
   - Comments success on merged PR

### Failure Recovery:

If main branch becomes unhealthy:

1. Post-merge validation detects issue
1. Creates urgent GitHub issue with details
1. Auto-fix workflow attempts remediation
1. Issue closed automatically when health restored

## Benefits

### ✅ Requirement 1: Automatic Review & Merge

- All PRs automatically reviewed with full CI/CD
- Auto-merge on passing checks (no manual approval)

### ✅ Requirement 2: Automatic Failure Fixing

- Auto-fix workflow remediates common issues
- Authorized to modify code, config, workflows
- Retries until successful

### ✅ Requirement 3: Branch Protection

- Main branch protected with mandatory status checks
- Direct merges only (no intermediate branches via linear history)
- Main never has test failures or conflicts

### ✅ Requirement 4: Post-Merge Validation

- Automatic conflict detection
- Zero failing tests guarantee
- Comprehensive health reports
- Immediate issue creation for problems

## Monitoring

### Health Dashboard

View real-time status:

- Actions tab: `https://github.com/IAmSoThirsty/Project-AI/actions`
- Filter by workflow to see individual automation runs

### Reports

- Main health reports: Artifacts from post-merge-validation workflow
- Auto-fix summaries: Comments on PRs from auto-fix workflow
- Merge confirmations: Comments on PRs after successful validation

## Maintenance

### Updating Required Checks

When adding new CI checks, update:

1. Branch protection rules in GitHub UI
1. Status check requirements in `auto-pr-handler.yml`
1. This documentation

### Workflow Dependencies

- All workflows use `actions/checkout@v4`
- Python 3.11 is standard across workflows
- Dependencies installed from `requirements.txt`

## Troubleshooting

### Issue: PR not auto-merging

- Verify all required status checks pass
- Check branch protection rules are configured
- Ensure `auto-pr-handler.yml` workflow completed successfully

### Issue: Auto-fix not triggering

- Verify `auto-fix-failures.yml` workflow is enabled
- Check PR has failures that trigger the workflow
- Review workflow run logs in Actions tab

### Issue: Main branch unhealthy after merge

- Check post-merge validation workflow logs
- Review created GitHub issue for details
- Auto-fix will attempt remediation automatically

## Notes

- These are **persistent defaults** - they apply to all current and future PRs
- No manual approval required for merges (fully automated)
- Main branch is guaranteed conflict-free with passing tests
- Branch protection enforced via GitHub settings + workflows
- All automation runs on GitHub Actions (no external dependencies)
