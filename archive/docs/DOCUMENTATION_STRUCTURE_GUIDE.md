<!--                                         [2026-03-03 13:45] -->
<!--                                        Productivity: Out-Dated(archive) -->
# Project-AI Documentation Structure Guide

This guide explains the documentation organization for Project-AI and helps contributors place their documentation in the correct location.

## 📁 Folder Structure Overview

```
docs/
├── executive/           # Business-oriented, investor-friendly materials
├── architecture/        # Technical architecture and system design
├── governance/          # Ethics, policy, and governance systems
├── security_compliance/ # Security, compliance, and audit documentation
├── developer/           # Developer guides, APIs, and installation
└── internal/            # Internal engineering notes and legacy docs
```

## 🎯 Decision Tree: Where Does My Document Go?

### Ask Yourself:

1. **Is this for executives, investors, or auditors?**

   → Place in `docs/executive/`

   - Examples: Executive summaries, whitepapers, business case studies, user guides

1. **Is this about system architecture or design?**

   → Place in `docs/architecture/`

   - Examples: Architecture diagrams, system design docs, component specifications

1. **Is this about ethics, governance, or policy?**

   → Place in `docs/governance/`

   - Examples: AGI charter, Four Laws, licensing, governance frameworks
   - **External use**: Use "Governing Council" instead of "Triumvirate"
   - **Internal use**: Internal codenames go in `docs/internal/`

1. **Is this about security, compliance, or auditing?**

   → Place in `docs/security_compliance/`

   - Examples: Security policies, incident playbooks, compliance checklists, RBAC guides

1. **Is this for developers or operators?**

   → Place in `docs/developer/`

   - Examples: Installation guides, API docs, CLI references, deployment guides

1. **Is this internal engineering notes or legacy docs?**

   → Place in `docs/internal/`

   - Examples: Implementation summaries, session notes, work-in-progress, archived docs

## 📋 Document Type Reference

| Document Type            | Destination Folder                | Examples                                |
| ------------------------ | --------------------------------- | --------------------------------------- |
| Executive Summary        | `executive/`                      | Business overviews, ROI analysis        |
| Whitepaper               | `executive/`                      | Technical papers for business audiences |
| User Guide               | `executive/`                      | End-user documentation                  |
| System Architecture      | `architecture/`                   | Architecture diagrams, system design    |
| Component Design         | `architecture/`                   | Service specifications, data flows      |
| Integration Architecture | `architecture/`                   | How systems connect                     |
| Ethics Framework         | `governance/`                     | Four Laws, AGI rights                   |
| Policy Document          | `governance/`                     | Decision-making policies                |
| Licensing                | `governance/`                     | Open source licenses, legal             |
| AGI Identity             | `governance/`                     | Identity specifications                 |
| Security Policy          | `security_compliance/`            | Security frameworks, policies           |
| Incident Playbook        | `security_compliance/`            | Incident response procedures            |
| Compliance Guide         | `security_compliance/`            | GDPR, HIPAA, SOC2 compliance            |
| Threat Model             | `security_compliance/`            | Security threat modeling                |
| Audit Report             | `security_compliance/`            | Security audit results                  |
| Installation Guide       | `developer/`                      | Setup and installation                  |
| API Reference            | `developer/api/`                  | REST API, GraphQL, gRPC docs            |
| CLI Documentation        | `developer/cli/`                  | Command-line usage                      |
| Deployment Guide         | `developer/deployment/`           | Production deployment                   |
| Quickstart               | `developer/`                      | Getting started quickly                 |
| Implementation Summary   | `internal/`                       | Internal implementation notes           |
| Session Notes            | `internal/archive/session-notes/` | Dev session records                     |
| Legacy Documentation     | `internal/archive/`               | Superseded documentation                |
| Work in Progress         | `internal/`                       | Draft docs not ready for public         |

## 🚀 Adding New Documentation

### For Pull Requests

When adding new documentation files:

1. **Choose the correct folder** using the decision tree above
1. **Use clear, descriptive filenames**
   - Good: `API_AUTHENTICATION_GUIDE.md`
   - Bad: `auth.md`, `temp.md`, `notes.md`
1. **Follow naming conventions**:
   - Executive/External: Use clear names, avoid internal codenames
   - Developer: Use technical but clear names
   - Internal: Any naming is acceptable
1. **Update the folder's README** if adding a major document
1. **Check for cross-references** and update links in other docs

### Terminology Guidelines

#### External-Facing Documents (executive, architecture, governance, security_compliance, developer)

- ✅ Use: "Governing Council" (not "Triumvirate")
- ✅ Use: "Ethics Framework" (not "Four Laws" in marketing)
- ✅ Use: "Security Sentinel" (not "Cerberus" in user docs)
- ✅ Use: "Ethics Agent" (not "Galahad" in user docs)
- ✅ Use: "Governance System" (not "Codex Deus Maximus")

#### Internal Documents (internal folder only)

- ✅ OK to use: Triumvirate, Cerberus, Galahad, Codex Deus Maximus
- ✅ OK to use: Internal codenames, jargon, abbreviations

## 🔄 Moving Existing Documentation

If you find documentation in the wrong location:

1. **Identify the correct folder** using this guide
1. **Move the file**: `git mv old/path/file.md new/path/file.md`
1. **Update cross-references**: Search for links to the old path
1. **Update README files**: Update both old and new folder READMEs
1. **Test all links**: Ensure no broken references

### Command Examples

```bash

# Move a file to the correct folder

git mv docs/SOME_FILE.md docs/architecture/SOME_FILE.md

# Search for references to update

grep -r "SOME_FILE.md" docs/ README.md

# Stage all changes

git add .

# Commit with descriptive message

git commit -m "docs: Move SOME_FILE.md to architecture folder"
```

## 📚 Updating Cross-References

When moving files, update references in:

1. **README.md** (root)
1. **Other documentation files** that link to the moved file
1. **Folder README files**
1. **.github/copilot-instructions.md** (if referenced)
1. **Any code comments** that reference the documentation

### Search and Replace Pattern

```bash

# Find all references to a moved file

grep -r "path/to/old/FILE.md" .

# Use your editor's find-and-replace to update all references

# Old: docs/FILE.md

# New: docs/architecture/FILE.md

```

## 🎨 Document Templates

### Executive Summary Template

```markdown

# [Project/Feature Name]: Executive Summary

## Overview

[Business-level description]

## Business Value

[Why this matters to stakeholders]

## Key Benefits

- Benefit 1
- Benefit 2

## Compliance & Risk

[Compliance considerations]

## Next Steps

[Recommended actions]
```

### Architecture Document Template

```markdown

# [System/Component] Architecture

## Overview

[High-level description]

## Architecture Diagram

[ASCII art or reference to image]

## Components

### Component 1

[Description, responsibilities]

## Data Flow

[How data moves through the system]

## Integration Points

[How this integrates with other systems]

## Technical Decisions

[Key architectural decisions and rationale]
```

## 🔍 Folder Quick Reference

| If your doc is about...              | Put it in...           |
| ------------------------------------ | ---------------------- |
| Business value, ROI, investor pitch  | `executive/`           |
| System design, architecture patterns | `architecture/`        |
| AI ethics, policy, governance        | `governance/`          |
| Security, compliance, auditing       | `security_compliance/` |
| How to install, use APIs, deploy     | `developer/`           |
| Internal notes, WIP, legacy          | `internal/`            |

## 📞 Questions?

If you're unsure where a document should go:

1. Review this guide's decision tree
1. Check the folder README files
1. Look at similar existing documents
1. When in doubt, ask in your PR description

______________________________________________________________________

**Remember**: Good documentation organization helps everyone find what they need quickly. Take the extra minute to place your docs correctly!
