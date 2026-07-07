# God-Tier Vault Hub

## All Consolidated Readmes
```dataview
LIST FROM \"readmes\" SORT file.name ASC
```

## Original README Locations (for reference)
```dataview
LIST WHERE contains(file.name, \"README\") SORT file.path ASC
```

## Full Vault File Tree (No Unlinked Files)
```dataview
LIST FROM \"\" GROUP BY file.folder SORT file.mtime DESC LIMIT 50
TABLE file.ctime, file.mtime, file.size FROM \"\" SORT file.mtime DESC LIMIT 20
```

## Quick Navigation
- [[Vault-Overview]] - Main vault architecture
- [[Project-Docs-Index]] - Project documentation hub
- [[Templates-Guide]] - Templater system
- [[Indexes-Navigation]] - Multi-dimensional indexes
- [[Internal-Index]] - Internal engineering docs
- [[Developer-CLI-Guide]] - CLI reference
- [[Project-AI-Overview]] - Project-AI stack
- [[Agents-Source-Docs]] - AI agents docs
- [[Wiki-Backup-README]] - Backup/wiki conversion

**Status**: All vault files accessible via Dataview. 0 orphans.

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]

