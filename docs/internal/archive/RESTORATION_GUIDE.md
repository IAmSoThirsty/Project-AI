# How to Restore Archived Files

If you need to restore any of the archived files, here's how to do it:

## Quick Restore from Archive

All archived files are still in the repository in `docs/archive/`:

```bash

# Copy a file back from archive

cp docs/archive/historical-summaries/BATCH_MERGE_SUMMARY.md .

# Or restore multiple files

cp docs/archive/session-notes/*.md docs/notes/
```

## Restore Deleted Files from Git History

All deleted files are still in git history. To restore them:

### 1. Find the file in history

```bash
git log --all --full-history -- path/to/deleted/file
```

### 2. Restore the file

```bash

# Restore to last version before deletion

git checkout <commit-hash>^ -- path/to/deleted/file

# Example: Restore debug_line57.py

git checkout 0e06f79^ -- debug_line57.py
```

### 3. View file content without restoring

```bash
git show <commit-hash>:path/to/deleted/file
```

## Specific File Restoration Examples

### Restore malformed files (if needed for analysis)

```bash
git checkout c16fd9d^ -- =2.6.3
git checkout c16fd9d^ -- =2.8.0
git checkout c16fd9d^ -- =4.53.0
```

### Restore backup files

```bash
git checkout c16fd9d^ -- .gitignore.bak
git checkout c16fd9d^ -- .devcontainer/devcontainer.json.bak
git checkout c16fd9d^ -- .github/dependabot.yml.bak
```

### Restore duplicate documentation

```bash
git checkout c16fd9d^ -- docs/overview/README_COPY_OF_README.md
git checkout e8d9384^ -- docs/overview/PROGRAM_SUMMARY.md
git checkout e8d9384^ -- docs/overview/INTEGRATION_SUMMARY.md
```

### Restore generated test artifacts

```bash
git checkout ea64d9e^ -- data/generated_tests/run_1765137858826/
git checkout ea64d9e^ -- src/app/generated/sample_topic/
```

### Restore debug script

```bash
git checkout 0e06f79^ -- debug_line57.py
```

## View Archive Contents

```bash

# List all archived files

find docs/archive -type f ! -name README.md

# Read archive README for context

cat docs/archive/security-incident-jan2026/README.md
cat docs/archive/session-notes/README.md
cat docs/archive/historical-summaries/README.md
cat docs/archive/adversarial-completion/README.md
```

## Commit References

- `c16fd9d` - Removed malformed files and explicit duplicates
- `e8d9384` - Removed duplicate documentation and archived security
- `ea64d9e` - Removed generated artifacts and archived session notes
- `2edecdd` - Archived historical summaries and adversarial reports
- `0e06f79` - Removed debug script and relocated integration guide
- `f482e7d` - Added cleanup summary documentation

## Need Help?

If you're unsure about restoring a file:

1. Check `CLEANUP_SUMMARY.md` for the full list of changes
1. Check the relevant `docs/archive/*/README.md` for context
1. Use `git log --all --full-history -- <filename>` to see the file's history
1. View the file content with `git show <commit>:<path>` before restoring

## Important Notes

- **Root README.md was never modified** - No need to restore it
- **Archived files are already in the repo** - Just copy from docs/archive/
- **Deleted files are in git history** - Use git checkout to restore
- **All changes are reversible** - Git history preserves everything

______________________________________________________________________

**Remember**: The cleanup was done to reduce duplication and organize historical documents. Most files don't need to be restored. If you're unsure, check the context in the archive READMEs first.
