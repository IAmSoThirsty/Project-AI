# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-17 | TIME: 11:08               #
# COMPLIANCE: Sovereign Substrate / Thirsty-Lang UTF Ecosystem                  #
# ============================================================================ #

---
description: Relentless audit for Thirsty-Lang and all UTF member repositories.
---

### 🍹 UTF / Thirsty-Lang Ecosystem Audit

This workflow verifies the linguistic substrate, the interpreter, and all UTF member repositories for Master-Tier alignment.

// turbo
1. **Interpreter Robustness**: Run the absolute stress test suite against the `ThirstyInterpreter`.
```bash
python src/thirsty_lang/src/thirsty_interpreter.py --stress-test
```

// turbo
2. **UTF Source Alignment**: Verify that the `tarl` and `thirsty_lang` modules are fully synchronized.
```bash
python tools/path_integrity_agent.py --target src/thirsty_lang
```

// turbo
3. **Linguistic Proof Map**: Map all `.thirsty` files in the ecosystem and verify their execution status.
```bash
python tools/architect_agent.py --target . --pattern "*.thirsty"
```

// turbo
4. **Member Repo Integrity**: Verify the `UTF-8` compliance marker across all integrated member modules.
```bash
grep -r "UTF-8" src/thirsty_lang
```

### 📊 Report
- `governance/UTF_LANG_AUDIT.md`
