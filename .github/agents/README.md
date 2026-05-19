# Governance Auditor Agent - README

## Quick Start

Invoke this agent from Copilot CLI with:

```bash
@governance-auditor audit [scope]
```

**Scope options:**
- `full` - Complete codebase scan (all 7 phases)
- `core` - Focus on `src/app/core/**`
- `agents` - Focus on `src/app/agents/**`
- `governance` - Focus on `src/app/governance/**`
- `api` - Focus on `api/**` and `web/backend/**`
- `file:<path>` - Audit specific file (e.g., `file:src/app/core/intelligence_engine.py`)

## What This Agent Does

Systematically scans Project-AI codebase for governance violations:

1. **Execution bypasses** - Actions that skip `ExecutionGate.execute()`
2. **Silent allow paths** - Weak fallbacks that bypass deny-by-default
3. **Unaudited state changes** - Actions without `acceptance_ledger` recording
4. **Direct provider calls** - OpenAI/HuggingFace calls without governance
5. **Missing deny-path tests** - Test gaps for policy violations
6. **Mutable audit trails** - UPDATE/DELETE on immutable event logs
7. **Authority assumptions** - Ungoverned privilege checks

## Output

Generates two artifacts:

1. **Inline summary** - Top 5 Critical/High findings with file:line citations
2. **Full markdown report** - Session workspace: `files/governance_audit_report_{timestamp}.md`

## Example Usage

### Full Codebase Audit
```bash
@governance-auditor audit full
```

### Focused Audits
```bash
# Check intelligence engine for OpenAI bypasses
@governance-auditor audit file:src/app/core/intelligence_engine.py

# Scan all governance modules
@governance-auditor audit governance

# Verify API endpoints have proper authorization
@governance-auditor audit api
```

## Integration with Development Workflow

**Before PR merge:**
```bash
@governance-auditor audit full
```

**After adding new provider integration:**
```bash
@governance-auditor audit file:src/app/core/new_provider.py
```

**Weekly governance health check:**
```bash
@governance-auditor audit core
```

## Report Format

Each finding includes:
- **Severity** (Critical/High/Medium/Low)
- **Exact location** (file:line)
- **Code snippet** (with context)
- **Why it matters** (threat scenario)
- **Minimal safe patch** (step-by-step fix)
- **Required tests** (deny-path coverage)
- **Verification command** (pytest command)

## Read-Only Guarantee

This agent:
- ✅ Reads any file needed for analysis
- ✅ Writes reports to session workspace only
- ✅ Uses SQL for finding tracking (session DB only)
- ❌ Never modifies codebase files
- ❌ Never runs destructive commands

## Canonical Validation

All audit reports include recommendation:
```bash
PYTHONIOENCODING=utf-8 PYTHONPATH=src py -3.12 canonical/replay.py
```
Must show: **5/5 invariants pass** after any fixes applied.

## Maintenance

Agent configuration: `.github/agents/governance-auditor.agent.md`

Update scan patterns quarterly or when new bypass vectors discovered.

---

*Enforce the governance contract. No execution without authorization. No action without audit. Deny-by-default everywhere.*
