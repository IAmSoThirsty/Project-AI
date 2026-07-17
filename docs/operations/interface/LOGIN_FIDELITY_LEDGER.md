# Control Center Login Fidelity Ledger

**Status:** Verified refinement, not a production-accessibility claim  
**Figma board:** <https://www.figma.com/board/5YzwgM4psogklwhu9pJR58>  
**Accepted concept:** `docs/operations/interface/concepts/control-center-sign-in.png`  
**Desktop render:** `C:\Users\Quencher\.codex\visualizations\2026\07\15\019f66ca-df58-7f70-9dbe-84ed249d9f79\operator-console-sign-in-refined.png`  
**Mobile render:** `C:\Users\Quencher\.codex\visualizations\2026\07\15\019f66ca-df58-7f70-9dbe-84ed249d9f79\operator-console-sign-in-refined-mobile.png`

## Refinement brief

Preserve the accepted split-screen composition, dark navy palette, blue action,
three assurance rows, and restrained form. Refine the governance terminology and add
a factual local-instance indicator without turning the browser into a trust anchor.

## Fidelity review

| Comparison point | Concept evidence | Render evidence | Result |
|---|---|---|---|
| Composition | Assurance rail left; authentication workspace right | Same split composition and divider | Preserved |
| Hierarchy | Brand, governing statement, assurances, environment; form heading and fields | Same order and visual weight | Preserved |
| Palette | Near-black navy, restrained borders, blue primary action | Same palette and semantic accent treatment | Preserved |
| Controls | Labeled username/password fields, inline icons, reveal control, full-width Continue | Same control family; code-native labels and controls | Preserved |
| Governance copy | Identity is separated from execution authority | Terminology strengthened to authentication, governance policy, server identity, scoped capability, and execution gate | Intentional refinement |
| Instance assurance | Local development and no browser machine token | Server-reported local sovereign instance; no cloud login, machine identity, or execution token in browser | Strengthened |
| Responsive behavior | Desktop reference | 390×844 render retains brand, governing statement, instance identity, form, and recovery path without horizontal overflow | Verified |
| Foreground contrast | White primary text over near-black surfaces | Authentication shell now explicitly establishes its foreground instead of relying on root inheritance | Corrected after native screenshot review |

## Above-the-fold copy diff

Intentional user-directed changes:

- `Your account identifies who is requesting work. It does not grant execution authority.`
  → `Authentication establishes identity. Authority is evaluated independently by governance policy.`
- `Server-side session` → `Server-authenticated session`.
- `Execution gate remains decisive` → `Governance gate remains authoritative`.
- The third assurance now states that capabilities resolve per request.
- `Local development` now identifies the configured local sovereign instance.
- The browser boundary now excludes both machine identity and execution tokens.

No navigation, form field, primary action, recovery action, or decorative copy was added.

## Verification boundary

The browser was checked at 1536×1024 and 390×844. A final native desktop recapture
also caught and closed an inherited foreground-color defect. Login successfully transitioned to
Command Center, and browser logs contained no warnings or errors. Axe-core covers the
sign-in DOM with rendered color contrast disabled because JSDOM cannot measure pixels.
Rendered contrast, screen-reader behavior, and production assistive-technology
acceptance remain separate required gates.
