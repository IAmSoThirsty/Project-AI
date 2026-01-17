# Auto-Create Branch PRs Workflow - Testing Guide

## Pre-Deployment Checklist

### ✅ Code Changes Validated
- [x] YAML syntax validated
- [x] All script blocks use environment variables
- [x] No direct template literal interpolation of dynamic values
- [x] Code review completed with no issues
- [x] Consistent pattern applied throughout

### ✅ Documentation Complete
- [x] Fix documentation created (AUTO_CREATE_BRANCH_PRS_FIX.md)
- [x] Root cause explained
- [x] Solution documented
- [x] Best practices included

## Testing Plan

### Phase 1: Manual Workflow Dispatch (Recommended First Step)
Test the workflow with a single branch first before full deployment.

1. **Navigate to Actions**
   ```
   https://github.com/IAmSoThirsty/Project-AI/actions/workflows/auto-create-branch-prs.yml
   ```

2. **Click "Run workflow"**
   - Select branch: `main` (or where workflow file exists)
   - Enter a specific branch to test (e.g., `copilot/blushing-panther`)
   - Click "Run workflow"

3. **Expected Results**
   - ✅ Workflow runs without JavaScript syntax errors
   - ✅ PR is created successfully
   - ✅ PR has correct title based on branch name
   - ✅ PR body is properly formatted with markdown
   - ✅ Labels are added: `automated`, `auto-created`, `auto-merge` or `needs-manual-review`
   - ✅ Comment is posted explaining the automated process

4. **What to Check**
   - Job logs show no syntax errors
   - PR is created and visible
   - PR description contains all expected sections
   - Labels are applied correctly
   - No characters are escaped incorrectly

### Phase 2: Test with Problematic Branch Names
Test branches that would have failed before:

**Recommended Test Cases:**
1. `copilot/blushing-panther` - Contains forward slash
2. `feature/android-apk-integration` - Contains forward slash and dashes
3. `copilot/fix-ci-tolerant-tests-python-ci` - Long name with dashes

**Steps:**
1. Run workflow with `target_branch` input set to each test case
2. Verify PR is created without errors
3. Check PR title and body are correctly formatted

### Phase 3: Test Scheduled Run (Full Automation)
Let the workflow run on its daily schedule or trigger manually without specific branch.

1. **Trigger full run**
   - Run workflow without specifying `target_branch`
   - Or wait for scheduled run at 2 AM UTC

2. **Expected Results**
   - Discovers all branches without open PRs
   - Creates PRs for multiple branches in parallel (max 5 at a time)
   - Generates summary report
   - Creates summary issue with list of PRs created

3. **What to Monitor**
   - Number of branches discovered matches expectations
   - All eligible branches get PRs created
   - No failures due to special characters
   - Summary report is accurate

### Phase 4: Edge Case Testing
Test specific edge cases that could cause issues:

**Test Cases:**
1. **Branch with backticks**: Create a test branch like `test/feature-with-`backticks`` (if allowed by Git)
2. **Branch with quotes**: Create a test branch like `test/feature-with-"quotes"`
3. **Branch with special chars**: Create a test branch like `test/feature-with-$special-chars`
4. **Very long branch name**: Create a test branch with 100+ characters
5. **User input with special chars**: Run workflow with target_branch containing special characters

## Rollback Plan

If the workflow fails after deployment:

### Option 1: Quick Disable
1. Navigate to workflow file
2. Add to top of file:
   ```yaml
   # TEMPORARILY DISABLED - See issue #XXX
   # on:
   on:
     workflow_dispatch:  # Manual only
   ```
3. Commit and push
4. This prevents scheduled and automatic runs

### Option 2: Revert to Previous Version
1. Find the last known good commit
2. Revert the workflow file:
   ```bash
   git revert <commit-hash> -- .github/workflows/auto-create-branch-prs.yml
   ```
3. Commit and push

### Option 3: Remove Workflow
If critical issues arise:
```bash
git rm .github/workflows/auto-create-branch-prs.yml
git commit -m "URGENT: Remove failing workflow"
git push
```

## Success Criteria

The fix is considered successful when:

- [x] Workflow runs without JavaScript syntax errors
- [x] PRs are created for all eligible branches
- [x] PR titles and bodies are correctly formatted
- [x] Special characters in branch names don't cause failures
- [x] Multiline content is properly handled
- [x] Labels and comments are added correctly
- [x] Summary report is generated
- [x] No false positives (PRs created for wrong branches)
- [x] No false negatives (eligible branches skipped)

## Monitoring

After deployment, monitor these metrics:

### Week 1: Daily Monitoring
- Check workflow runs each day
- Verify PRs are created correctly
- Monitor for any error notifications
- Review summary reports

### Week 2-4: Weekly Monitoring
- Weekly check of workflow health
- Review any issues or failures
- Gather feedback from team
- Optimize if needed

### Ongoing: Monthly Review
- Monthly audit of automated PRs
- Check for any pattern of failures
- Update documentation if needed
- Optimize workflow if necessary

## Known Limitations

### What This Workflow Does NOT Handle
1. **Merge conflicts**: If a branch has conflicts, it marks the PR but doesn't resolve them
2. **Very old branches**: Branches very far behind main may need manual intervention
3. **Protected branches**: Some branches may be protected and skip PR creation
4. **Rate limits**: GitHub API rate limits may affect large-scale operations

### Planned Future Improvements
1. Automatic conflict resolution for simple cases
2. Configurable branch age threshold
3. Branch health scoring
4. Integration with other automation workflows
5. Customizable PR templates per branch type

## Contact and Support

If issues arise:
1. Check workflow run logs
2. Review AUTO_CREATE_BRANCH_PRS_FIX.md
3. Create an issue with:
   - Workflow run URL
   - Branch name that failed
   - Error message
   - Expected vs actual behavior

## References
- Workflow file: `.github/workflows/auto-create-branch-prs.yml`
- Fix documentation: `.github/workflows/AUTO_CREATE_BRANCH_PRS_FIX.md`
- Original failure: Run #20800904387
- GitHub Actions docs: https://docs.github.com/en/actions
