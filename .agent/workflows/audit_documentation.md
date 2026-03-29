# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-17 | TIME: 11:00               #
# COMPLIANCE: Sovereign Substrate / Level 10-12 Documentation                   #
# ============================================================================ #

---
description: Relentless audit for all Papers, Metadata, and Documentation.
---

### 📄 Documentation Audit

This workflow verifies 100% paperwork coverage, metadata compliance, and the "Directness Doctrine" across all documentation.

// turbo
1. **Paperwork Manifest**: Identify all documentation files and verify their metadata headers.
```bash
python tools/architect_agent.py --target docs --pattern "*.md"
```

// turbo
2. **Metadata Sweep**: Verify that all `README.md` files have the required `TIER: MASTER` status.
```bash
grep -r "TIER: MASTER" . --include "README.md"
```

// turbo
3. **Spec Alignment Proof**: Verify that the formal `SPECIFICATION.md` aligns with the current `ThirstyInterpreter` capabilities.
```bash
python src/thirsty_lang/src/thirsty_interpreter.py src/thirsty_lang/docs/SPECIFICATION.md
```

// turbo
4. **Directness Doctrine Audit**: Scan all documentation for fluff, ambiguity, or non-authoritative claims.
```bash
grep -r "TODO" docs/
```

### 📊 Report
- `governance/DOCUMENTATION_AUDIT.md`
