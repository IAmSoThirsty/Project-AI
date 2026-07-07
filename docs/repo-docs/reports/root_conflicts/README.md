# Root Cleanup Conflict Files

These files were moved here during root cleanup because a file with the same name already existed in `docs/reports/` **with different content**.

## Why this folder exists

To avoid data loss, conflicts were preserved instead of overwritten.

## Resolution process

1. Compare each file in this folder with its counterpart in `docs/reports/`.
2. Decide one canonical version (or merge both).
3. Move merged/final content to `docs/reports/`.
4. Remove resolved conflict files from this folder.

## Scope

- Created by cleanup on 2026-04-28
- Initial conflict count: 13 files

## Resolution status

- ✅ Conflict set resolved on 2026-04-28
- Canonical versions were promoted into `docs/reports/`
- This directory now serves as audit/process documentation only
