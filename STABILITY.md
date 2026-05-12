# Thirsty-Lang Stability Contract

**Applies to**: Thirsty Core 1.x  
**Effective**: v1.0.0

---

## Guarantees

**Valid Core 1.x programs will not break.**  
Any program that runs correctly under a Thirsty Core 1.0 interpreter will produce identical output under any Thirsty Core 1.x interpreter.

**Governed semantics may expand but not silently weaken.**  
New `requires` clause types, new authority classes, and new TARL verdict forms may be added in minor releases. Existing governance rules will never be silently relaxed — a `DENY` verdict will not become `ALLOW` without an explicit policy change.

**Security keywords cannot become no-ops.**  
`shield`, `sanitize`, `armor`, `morph`, `detect`, and `defend` will never be parsed and ignored. If their semantics evolve, programs using them will receive a diagnostic at check time, not silent behavioral change.

**Deny-by-default behavior is semver-protected.**  
In `mode governed`, the absence of a matching policy always produces `DENY`. This cannot be changed in a patch or minor release.

---

## What Is Not Guaranteed

- **Error message text** — Error messages may be improved in any release. Only `THIRSTY-Exxx` codes are stable.
- **Phase 3+ type system** — `Result[T,E]`, enums, structs, interfaces, and generics are Phase 3 additions. Their syntax is not subject to Core 1.x compatibility until they reach stable status in a numbered release.
- **Standard library expansion** — New namespaces and new functions within existing namespaces may be added in any minor release. Existing function signatures will not change.
- **Internal interpreter behavior** — Stack depth limits, caching behavior, and execution order within a single expression are implementation details and may change.

---

## Versioning

Thirsty-Lang follows semantic versioning: `MAJOR.MINOR.PATCH`.

- `PATCH` — Bug fixes only. No language changes.
- `MINOR` — Additive language features. All 1.x programs remain valid.
- `MAJOR` — Breaking changes permitted. A migration guide will be published.
