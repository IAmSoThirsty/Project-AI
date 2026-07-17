# Atlas Projections Fidelity Ledger

**Status:** Implemented and visually inspected on 2026-07-16  
**Reference:** `concepts/control-center-atlas-projections.png`  
**Desktop evidence:** `C:\Users\Quencher\.codex\visualizations\2026\07\15\019f66ca-df58-7f70-9dbe-84ed249d9f79\atlas-projections-desktop.png`  
**Narrow evidence:** `C:\Users\Quencher\.codex\visualizations\2026\07\15\019f66ca-df58-7f70-9dbe-84ed249d9f79\atlas-projections-mobile.png`

## Comparison ledger

| Reference element | Implemented evidence | Result |
|---|---|---|
| Atlas Projections title, analytical subtitle, and four-part boundary rail | Same title, subtitle, and `Analysis only / Not a recommendation / No governance verdict / No execution` rail | Matched |
| Two-column projection input/result workspace | Two-column desktop workspace; form and result reflow to one column at 920 px | Matched |
| Structured claim, evidence, and driver controls | Canonical claim types, RS/SS/TS stack, A-D evidence tiers, bounded confidence/value fields, and add/remove controls | Matched to runtime contract |
| Posterior, uncertainty, evidence count, stack, and projection digest | All five values render from the API response; hashes are copyable | Matched |
| Explicit analytical-evidence notice and audit receipt | Notice is retained verbatim; audit hash and timestamp come from the durable relay receipt | Matched |
| Durable projection history with expandable detail | Newest-first table includes claim, type, metrics, stack, date, receipt, input/output/projection/audit hashes, creator, evidence, and drivers | Matched and expanded |
| Dark navy Control Center shell, fine borders, blue/green semantic accents | Existing shell tokens and Lucide icon set are reused without a separate visual vocabulary | Matched |
| Narrow layout without clipped form controls | Form reflows at 390 px; the history table remains intentionally horizontally scrollable inside a contained region | Matched after overflow repair |

## Copy and contract differences

- The concept uses illustrative claim types such as `Risk`; the implementation exposes the
  canonical Atlas values: `factual`, `predictive`, `agency`, `causal`, and `correlational`.
- The concept labels evidence `Tier 1` and `Tier 2`; the runtime contract is the Atlas
  `A`, `B`, `C`, and `D` tier enum, so the interface uses those exact values.
- The implementation adds input and output SHA-256 values to expanded history detail.
  These are required to identify the persisted request and result independently.
- The desktop reference uses production sample identity and timestamps. Browser evidence
  truthfully shows the local-development environment and the QA Owner session.
- The implemented form is taller than the reference because every bounded field retains a
  visible label and native form control. The desktop viewport shows the result and history
  header/first row; the remaining durable detail continues below the fold.

## Measured acceptance

- Desktop viewport: `1536x1024`; document width `1536`; no horizontal overflow.
- Narrow viewport: `390x844`; document width `390`; no page-level horizontal overflow.
- Narrow history table: `702` px intrinsic width inside a `360` px contained scroll region.
- Real browser flow covered Owner sign-in, route load, POST creation, deterministic result,
  durable history refresh, expanded receipt detail, and native screenshots.
- Final authenticated route inspection reported no browser console errors and no HTTP
  responses at or above 400.
- Automated axe-core coverage for the completed projection state reports no violations
  with color contrast excluded from jsdom, consistent with the existing suite boundary.

## Known deviation

The 1536x1024 reference compresses the complete form, result, and expanded history detail
into one frame. The implementation prioritizes explicit labels and touch-safe controls, so
the expanded evidence hashes are below the initial desktop fold. This is an intentional
usability deviation, not a claim of pixel identity.
