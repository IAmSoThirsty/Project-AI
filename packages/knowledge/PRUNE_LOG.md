# Corpus Prune Log

Audit record of files removed from the source corpus `T:\07-Research\Hatter Information`
before ingestion into the Project-AI knowledge layer. Files are deleted from the external
source folder (the user's files) per explicit user decision; hashes are retained here so the
pruning is auditable without keeping the content.

Scope of the retained corpus: **computers, ethical hacking, and technology**. Personal-life
documents and un-ingestable assets are removed; user-authored technical specifications are kept.

| # | File | Reason | Size (bytes) | SHA-256 | Decided by | Date |
|---|------|--------|--------------|---------|-----------|------|
| 1 | `Cash_App_September_2025_Account_Statement_015eca…c489.pdf` | Personal financial record (not in scope) | 41452 | `ae4f76b4a499669ead7ac01665866c00867f0d6f522306d20d10607984f7e90d` | user | 2026-07-07 |
| 2 | `youtube.pdf` | Image-only PDF, no text layer — un-ingestable as-is | 2593625 | `5d57c14a7008d0c98dada31bca8dcda546b287bc96e48bc0b5422552469e6ded` | user | 2026-07-07 |

## Explicitly retained (reviewed, kept by user decision)

- `Security_Analysis_-_1934_-_Ben_Graham__David_Dodd.pdf` — finance; may relate to `thirstys-trading-hub`.
- `Franchise Value - A Modern Approach to Security Analysis.[2004.ISBN0471647888].pdf` — finance.
- `13things.pdf` — "13 Things The Government Doesn't Want You To Know".
- `How-to-Get-Your-Message-Out.pdf` — DEFCON 19 talk (mesh comms), in-scope technology.

## Personal-document scan (complete)

A bounded, parallel first-page scan of all 288 remaining PDFs (indicators: names, account
statements, routing/account numbers, SSN/DOB, licenses, invoices, payment apps) returned
**0 hits** on 2026-07-07. No additional personal-life documents were found; the Cash App
statement (row 1) was the only one. The 17 `.doc` / 4 `.ppt` / 4 `.html` files were not
text-scanned (legacy/markup formats) but are unambiguously technical by title.
