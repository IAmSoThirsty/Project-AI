# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-17 | TIME: 11:10               #
# COMPLIANCE: Sovereign Substrate / Autonomous Agent Integrity                  #
# ============================================================================ #

---
description: Brutal audit for all Sovereign Agents and Cognitive Loops.
---

### 🤖 Sovereign Agent Audit

This workflow verifies the identity, baseline, and cognitive loop integrity of every agent in the ecosystem.

// turbo
1. **Agent Baseline Verification**: Verify the baseline configuration for all core agents.
```bash
python tools/architect_agent.py --target .agent/rules
```

// turbo
2. **Cognitive Loop Integrity**: Trace the execution path from the Cognition Kernel to individual agent tools.
```bash
python tools/path_integrity_agent.py --target src/app/core/cognition_kernel.py
```

// turbo
3. **Identity Root Proof**: Verify the identity root of the active sovereign session.
```bash
python src/thirsty_lang/src/thirsty_interpreter.py src/app/core/metatheoretical_kernel.thirsty
```

// turbo
4. **Agent Tool Maturity**: Scan all agent tool definitions for `TIER: MASTER` compliance.
```bash
python tools/stub_hunter_agent.py --target src/app/core --pattern "*agent*"
```

### 📊 Report
- `governance/AGENT_AUDIT.md`
