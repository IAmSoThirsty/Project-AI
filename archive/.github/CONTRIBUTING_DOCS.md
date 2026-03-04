<!--                                         [2026-03-03 13:45] -->
<!--                                        Productivity: Out-Dated(archive) -->
# Contributing Documentation to Project-AI

Thank you for contributing to Project-AI documentation! This guide will help you place your documentation in the correct location.

## Quick Start

1. **Read the [Documentation Structure Guide](../docs/DOCUMENTATION_STRUCTURE_GUIDE.md)** - Complete guide with decision tree
2. **Choose the correct folder** based on your audience
3. **Follow naming conventions** (see below)
4. **Update cross-references** in README.md if needed
5. **Submit your PR** with a clear description

## Documentation Folder Structure

```
docs/
├── executive/           # For: Executives, investors, auditors, end users
├── architecture/        # For: Architects, senior engineers, technical leads
├── governance/          # For: Ethics teams, legal, compliance officers
├── security_compliance/ # For: Security engineers, auditors, pen testers
├── developer/           # For: Developers, DevOps, SRE teams
└── internal/            # For: Internal engineering team only
```

## Quick Decision Guide

**Where should my documentation go?**

- 📊 Business value, investor pitch, user guide? → `executive/`
- 🏗️ System architecture, design patterns? → `architecture/`
- ⚖️ Ethics, policy, AGI rights, licensing? → `governance/`
- 🔒 Security, compliance, incident response? → `security_compliance/`
- 💻 How to install, API docs, deployment? → `developer/`
- 🔧 Internal notes, WIP, legacy docs? → `internal/`

## Naming Conventions

### External-Facing Folders (executive, architecture, governance, security_compliance, developer)

**Use clear, professional terminology:**

- ✅ "Governing Council" (not "Triumvirate")
- ✅ "Ethics Framework" (not "Four Laws" in marketing materials)
- ✅ "Security Sentinel" (not "Cerberus")
- ✅ "Ethics Agent" (not "Galahad")
- ✅ "Governance System" (not "Codex Deus Maximus")

**File naming:**

- Use descriptive names: `API_AUTHENTICATION_GUIDE.md`
- Avoid generic names: `auth.md`, `notes.md`
- Use uppercase for multi-word files
- Use hyphens or underscores consistently

### Internal Folder

**Internal terminology is acceptable:**

- ✅ Triumvirate, Cerberus, Galahad, Codex Deus Maximus
- ✅ Internal jargon, abbreviations, codenames
- ✅ Casual or informal tone
- ✅ Any file naming convention

## Adding New Documentation

### Step 1: Choose Location

Use the decision tree in [docs/DOCUMENTATION_STRUCTURE_GUIDE.md](../docs/DOCUMENTATION_STRUCTURE_GUIDE.md)

### Step 2: Create Your File

```bash

# Example: Adding an API guide

cd docs/developer
vim NEW_API_GUIDE.md
```

### Step 3: Follow the Template

Use appropriate template from [docs/DOCUMENTATION_STRUCTURE_GUIDE.md](../docs/DOCUMENTATION_STRUCTURE_GUIDE.md#-document-templates)

### Step 4: Update References

If your document is important enough to reference from README.md:

```bash

# Edit README.md to add a link

vim README.md

# Add link in appropriate section:

# - [Your New Doc](docs/folder/YOUR_DOC.md) - Brief description

```

### Step 5: Update Folder README

If adding a major document, update the folder's README.md:

```bash

# Example: Adding to developer folder

vim docs/developer/README.md

# Add to "Key Documents" section

```

### Step 6: Submit PR

Create a PR with:

- **Title**: `docs: Add [document name]`
- **Description**: Explain what the doc covers and why it's needed
- **Checklist**:
  - [ ] Placed in correct folder
  - [ ] Used appropriate terminology
  - [ ] Updated cross-references
  - [ ] Updated folder README if major doc

## Moving Existing Documentation

If you find documentation in the wrong place:

### Step 1: Identify Correct Location

Use the decision tree to find where it should go.

### Step 2: Move the File

```bash

# Use git mv to preserve history

git mv docs/old/FILE.md docs/correct/FILE.md
```

### Step 3: Update References

```bash

# Find all references

grep -r "old/FILE.md" docs/ README.md .github/

# Update each reference to new path

# old/FILE.md → correct/FILE.md

```

### Step 4: Test Links

```bash

# Verify no broken links

# Check README.md and other docs that link to moved file

```

### Step 5: Commit

```bash
git add .
git commit -m "docs: Move FILE.md to correct folder (docs/correct/)"
```

## Documentation Standards

### Writing Style

**Executive documents:**

- Clear, professional language
- Avoid technical jargon
- Focus on business value
- Include executive summaries

**Technical documents:**

- Precise technical language
- Include code examples
- Add diagrams where helpful
- Link to related docs

**Developer guides:**

- Step-by-step instructions
- Command examples
- Troubleshooting sections
- Prerequisites clearly stated

### Markdown Formatting

```markdown

# Main Title (H1 - one per document)

## Section (H2)

### Subsection (H3)

- Bullet points for lists
- Use `code` for commands, file names
- Use **bold** for emphasis
- Use *italic* sparingly

```bash

# Code blocks with language

command --flag value
```

[Links](path/to/doc.md) with descriptive text
```

### File Naming

- Use descriptive names: `API_AUTHENTICATION_GUIDE.md`
- Be consistent: All caps or all lowercase for multi-word files
- Avoid spaces: Use underscores or hyphens
- Include document type: `_GUIDE.md`, `_REFERENCE.md`, `_QUICKSTART.md`

## Common Mistakes to Avoid

❌ **Don't:**

- Put user guides in internal/
- Use internal codenames in executive docs
- Create generic file names like `notes.md` or `temp.md`
- Forget to update cross-references after moving files
- Mix internal and external terminology in the same document

✅ **Do:**

- Choose the correct folder based on audience
- Use clear, descriptive names
- Update all references when moving files
- Follow existing document structure in each folder
- Include examples and diagrams where helpful

## Examples

### Good Documentation Placement

✅ **Executive Summary of Q4 Features**

- Location: `docs/executive/Q4_2024_FEATURES_SUMMARY.md`
- Terminology: "Governing Council", professional language
- Audience: Executives, investors

✅ **Kernel Architecture Deep Dive**

- Location: `docs/architecture/KERNEL_ARCHITECTURE_DETAILED.md`
- Terminology: Technical, precise
- Audience: Senior engineers, architects

✅ **CLI Command Reference**

- Location: `docs/developer/cli/COMMAND_REFERENCE.md`
- Terminology: Technical, practical
- Audience: Developers

✅ **Implementation Notes for Sprint 42**

- Location: `docs/internal/SPRINT_42_NOTES.md`
- Terminology: Internal codenames OK
- Audience: Engineering team

### Bad Documentation Placement

❌ **User Guide in internal/**

- Should be: `docs/executive/USER_GUIDE.md`

❌ **Security Policy with "Cerberus" in title**

- Should use: "Security Sentinel" for external docs
- Or place in: `docs/internal/` if using internal names

❌ **API Reference in root docs/**

- Should be: `docs/developer/api/API_REFERENCE.md`

## Questions?

- **Read**: [docs/DOCUMENTATION_STRUCTURE_GUIDE.md](../docs/DOCUMENTATION_STRUCTURE_GUIDE.md)
- **Check**: Folder README files for guidance
- **Ask**: In your PR description if unsure

Thank you for helping keep Project-AI documentation well-organized! 🎉
