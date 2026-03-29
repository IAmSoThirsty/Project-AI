# ============================================================================ #
# STATUS: ACTIVE | TIER: MASTER | DATE: 2026-03-17 | TIME: 10:52               #
# COMPLIANCE: Sovereign Substrate / Meta-Workflow Layer                         #
# ============================================================================ #

---
description: Workflow for workflows - meta-audit of the workflow system itself.
---

### 🔄 Workflow Meta-Audit

This workflow audits the completeness, metadata compliance, and technical validity of all established workflows in `.agent/workflows/`.

// turbo
1. **Workflow Manifest**: Identify all workflow files and verify their `TIER: MASTER` status.
```bash
python tools/architect_agent.py --target .agent/workflows --pattern "*.md"
```

// turbo
2. **Metadata Consistency**: Verify that all workflows follow the required header/shield/metadata standard.
```bash
grep -L "STATUS: ACTIVE | TIER: MASTER" .agent/workflows/*.md
```

// turbo
3. **Turbo Compliance**: Ensure all command blocks are annotated with `// turbo` for autonomous audit execution.
```bash
grep -L "// turbo" .agent/workflows/*.md
```

// turbo
4. **Dead Workflow Detection**: Identify workflows that reference non-existent scripts or deprecated agents.
```bash
python tools/path_integrity_agent.py --target .agent/workflows
```

### 📊 Report
- `governance/WORKFLOW_META_AUDIT.md`
