# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-17 | TIME: 10:40               #
# COMPLIANCE: Sovereign Substrate / Level 1-2 Cognitive Dept                   #
# ============================================================================ #

---
description: Brutal audit for Code Deus (Cognitive Dept) and Architect Tier-1 systems.
---

### 🧠 Code Deus / Cognitive Dept Audit

This workflow verifies the primary cognitive loop, architect logic, and the hierarchical orchestration of the sovereign intent.

// turbo
1. **Architect Self-Analysis**: Execute the architect agent to audit its own codebase and manifest generation logic.
```bash
python tools/architect_agent.py --target src/thirsty_lang/src/thirsty_interpreter.py
```

// turbo
2. **Cognition Kernel Trace**: Path verification for the Cognition Kernel's core services registration.
```bash
python tools/path_integrity_agent.py --target src/app/core/cognition_kernel.py
```

// turbo
3. **Intent Alignment**: Verify that the Cognitive Dept's logic in `trunk/mid/Cognitive_Dept` aligns with the metatheoretical kernel.
```bash
python src/thirsty_lang/src/thirsty_interpreter.py src/app/core/metatheoretical_kernel.thirsty
```

// turbo
4. **Dead Logic Sweep**: Detect unreferenced cognitive pathways or deprecated agent reasoning modules.
```bash
python tools/dead_code_agent.py --target trunk/mid/Cognitive_Dept
```

### 📊 Report
- `governance/CODE_DEUS_COG_AUDIT.md`
