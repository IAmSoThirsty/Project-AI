# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-17 | TIME: 11:05               #
# COMPLIANCE: Sovereign Substrate / Tool & Script Maturity                     #
# ============================================================================ #

---
description: Relentless audit for all tools, scripts, and automation manifests.
---

### 🛠️ Tools / Scripts Audit

This workflow verifies the maturity, stability, and metadata of every script in the `tools/` and `scripts/` directories.

// turbo
1. **Tool Manifest Verification**: Verify that every tool has a corresponding entry in the `governance/` directory.
```bash
python tools/architect_agent.py --target tools
```

// turbo
2. **Automation Resilience**: Stress test the `completion_tracker_agent.py` under heavy commit volume.
```bash
python tools/completion_tracker_agent.py --stress
```

// turbo
3. **Script Metadata Compliance**: Verify the `TIER: MASTER` header in all utility scripts.
```bash
grep -L "TIER: MASTER" tools/*.py
```

// turbo
4. **Stub Hunter (Tools)**: Ensure no tools contain unimplemented placeholders or debug stubs.
```bash
python tools/stub_hunter_agent.py --target tools
```

### 📊 Report
- `governance/TOOLS_AUDIT.md`
