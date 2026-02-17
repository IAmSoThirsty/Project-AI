# Thirsty-lang Linguist Submission Checklist

Use this checklist to ensure your submission to github/linguist is complete and correct.

## Pre-Submission Checklist

### Repository Setup

- [ ] Fork github/linguist repository
- [ ] Clone your fork locally
- [ ] Create new branch: `git checkout -b add-thirsty-lang`
- [ ] Install dependencies: `bundle install`
- [ ] Verify Ruby environment works

### Files Review

- [ ] Review `languages.yml` - ensure all fields are correct
- [ ] Review `grammars/thirsty.tmLanguage.json` - validate JSON syntax
- [ ] Review sample files - ensure they demonstrate language features
- [ ] Check that at least 3 sample files are included (✓ 5 provided)
- [ ] Verify file extensions match in all places

### Language Definition Validation

- [ ] Language name: "Thirsty-lang"
- [ ] Type: "programming"
- [ ] Color: "#00BFFF"
- [ ] Extensions: .thirsty, .thirstyplus, .thirstyplusplus, .thirstofgods
- [ ] TextMate scope: "source.thirsty"
- [ ] Language ID: 472923847 (unique)
- [ ] Interpreters: node, python3

### Grammar Validation

- [ ] JSON syntax is valid
- [ ] scopeName matches tm_scope in languages.yml
- [ ] Keywords defined correctly
- [ ] String patterns work
- [ ] Number patterns work
- [ ] Comment patterns work
- [ ] Operator patterns work

### Sample Files Validation

- [ ] hello.thirsty - basic example
- [ ] variables.thirsty - variable types
- [ ] hydration.thirsty - simple program
- [ ] control-flow.thirstyplus - conditionals
- [ ] basic-protection.thirsty - security features
- [ ] All samples have proper file extensions
- [ ] All samples demonstrate valid syntax
- [ ] Samples include comments explaining features

## Installation Steps

### Using Automated Script

- [ ] Run: `./submit.sh /path/to/linguist`
- [ ] Review output for any errors
- [ ] Verify all files copied correctly

### Manual Installation

- [ ] Copy languages.yml content to lib/linguist/languages.yml
- [ ] Place in correct alphabetical position (under "T")
- [ ] Copy grammar to vendor/grammars/thirsty.tmLanguage.json
- [ ] Update grammars.yml with grammar reference
- [ ] Copy samples to samples/Thirsty-lang/
- [ ] Verify all files in correct locations

## Testing Checklist

### Local Testing

- [ ] Run full test suite: `bundle exec rake test`
- [ ] All tests pass (or only expected failures)
- [ ] No new warnings or errors

### Language Detection Testing

- [ ] Test hello.thirsty: `bundle exec bin/linguist samples/Thirsty-lang/hello.thirsty`
- [ ] Output shows: "100.00% (X lines) Thirsty-lang"
- [ ] Test all sample files individually
- [ ] All samples detected as Thirsty-lang

### Grammar Testing

- [ ] Open sample file in editor with grammar
- [ ] Keywords highlighted correctly
- [ ] Strings highlighted correctly
- [ ] Comments highlighted correctly
- [ ] Numbers highlighted correctly
- [ ] Operators highlighted correctly

### Sample Generation

- [ ] Run: `bundle exec rake samples`
- [ ] Check generated samples.json
- [ ] Verify Thirsty-lang appears in samples
- [ ] Verify all sample files listed

## Git Workflow

### Commit Changes

- [ ] Stage all changes: `git add -A`
- [ ] Review changes: `git status` and `git diff --cached`
- [ ] Commit: `git commit -m "Add support for Thirsty-lang"`
- [ ] Verify commit contains all necessary files

### Files to Commit

- [ ] lib/linguist/languages.yml (modified)
- [ ] vendor/grammars/thirsty.tmLanguage.json (new)
- [ ] grammars.yml (modified)
- [ ] samples/Thirsty-lang/*.thirsty* (new files)

### Push and PR

- [ ] Push branch: `git push origin add-thirsty-lang`
- [ ] Go to GitHub and create pull request
- [ ] Use PR_TEMPLATE.md for description
- [ ] Add all checklist items to PR description
- [ ] Request review from linguist maintainers

## Pull Request Checklist

### PR Description

- [ ] Clear title: "Add support for Thirsty-lang"
- [ ] Comprehensive description
- [ ] Language overview included
- [ ] Syntax examples included
- [ ] Features list included
- [ ] Repository links included
- [ ] Author information included
- [ ] All checklist items checked

### PR Quality

- [ ] No unrelated changes included
- [ ] Commit message is clear
- [ ] No merge conflicts
- [ ] CI/CD passes (if applicable)
- [ ] Responds to review comments promptly

## Post-Submission

### Monitoring

- [ ] Watch PR for comments/reviews
- [ ] Respond to feedback within 48 hours
- [ ] Make requested changes if needed
- [ ] Re-test after any changes

### After Merge

- [ ] Star the linguist repository
- [ ] Thank reviewers in comments
- [ ] Update Thirsty-lang documentation
- [ ] Announce language recognition
- [ ] Test in real GitHub repositories

## Common Issues and Solutions

### Issue: "Language already exists"

- [ ] Check if Thirsty-lang already in languages.yml
- [ ] Verify language_id is unique
- [ ] Search for conflicting extensions

### Issue: "Grammar scope mismatch"

- [ ] Verify scopeName in grammar matches tm_scope in languages.yml
- [ ] Both should be "source.thirsty"

### Issue: "Tests failing"

- [ ] Check Ruby version compatibility
- [ ] Ensure all dependencies installed
- [ ] Review test output for specific errors
- [ ] Check that samples have correct extensions

### Issue: "Language not detected"

- [ ] Verify file has correct extension
- [ ] Check languages.yml is valid YAML
- [ ] Ensure no syntax errors in definition
- [ ] Test with different sample files

### Issue: "Samples not representative"

- [ ] Review sample files content
- [ ] Ensure variety of language features
- [ ] Add more complex examples if needed
- [ ] Include comments explaining syntax

## Additional Resources

- [ ] Read linguist CONTRIBUTING.md
- [ ] Review other language PRs as examples
- [ ] Check linguist documentation
- [ ] Join linguist discussions if needed

## Final Verification

Before submitting PR:

- [ ] All checklist items above are complete
- [ ] All tests pass locally
- [ ] Language detection works
- [ ] Grammar highlights correctly
- [ ] PR description is complete
- [ ] No typos or formatting issues
- [ ] Confident submission is high quality

---

**Status**: Ready for submission when all items checked
**Last Review**: 2026-01-28
**Reviewer**: _______________
**Date**: _______________

**Notes:**
