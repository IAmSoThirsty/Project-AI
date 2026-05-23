---
type: source-doc
tags: [thirsty-lang, utf, quickstart, onboarding, language]
created: 2026-05-20
last_verified: 2026-05-20
status: current
related_systems: [utf, thirsty-lang, tarl, shadow-thirst, tscg]
stakeholders: [developers, education-team, language-team]
content_category: technical
review_cycle: quarterly
---

# Thirsty-Lang Quickstart (UTF v1.2)

**Full Reference:** [21-thirsty-lang.md](./21-thirsty-lang.md)

## What You Are Running

Thirsty-Lang is the human-readable source language in the UTF (Universal Thirsty Family) stack:

1. Thirsty-Lang -> source syntax (`.thirsty`)
2. T.A.R.L. -> governance policy checks
3. Shadow Thirst -> mutation simulation
4. TSCG / TSCG-B -> symbolic + binary governance encoding

## Core Keywords

- `drink` - declare/bind values
- `pour` - output values
- `sip` - read input
- `thirsty` / `hydrated` - conditional branching
- `glass` - function
- `reservoir` - mutable store
- `shield` / `sanitize` / `armor` - security-first constructs

## Hello, Thirsty

```thirsty
drink name = "World"
pour "Hello, " + name
```

Save as `hello.thirsty`.

## Run It (UTF Python Runtime)

```powershell
py -3.12 -m src.utf.thirsty_lang.cli check hello.thirsty
py -3.12 -m src.utf.thirsty_lang.cli run hello.thirsty
```

## Open REPL

```powershell
py -3.12 -m src.utf.thirsty_lang.cli repl
```

## Governance Mode Reminder

UTF is governance-first: governance precedes execution. For policy-governed flows, pair source programs with TARL policy and Shadow Thirst promotion paths described in the full reference.

## Next Steps

1. Read [21-thirsty-lang.md](./21-thirsty-lang.md) sections 5-11 for TARL, Shadow Thirst, and security model.
2. Explore UTF examples under `src/utf/examples/`.
3. Use `doctor` for stack readiness checks:

```powershell
py -3.12 -m src.utf.thirsty_lang.cli doctor src/utf
```

