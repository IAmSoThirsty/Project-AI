---
description: "Master index for all agent customization instructions and governance protocols."
tags: [index, navigation, governance, agents, instructions]
created: 2026-05-13
status: current
---

# Agent Customization Instructions — Master Index

This directory contains mandatory governance protocols for all AI agents and IDE copilots operating in Project-AI.

## 🚨 Mandatory Reading Order

**All agents must follow instructions in this order:**

1. **[copilot_workspace_profile.md](../.github/copilot_workspace_profile.md)** — Foundation governance policy (takes precedence)
2. **[mandatory-structured-generation-default.instructions.md](./mandatory-structured-generation-default.instructions.md)** — Coding protocol (requirements contract, design, pseudocode, implementation, review)
3. **[governance-enforced-development.instructions.md](./governance-enforced-development.instructions.md)** — Execution gates, fail-closed, no bypass paths
4. **[agent-development-protocol.instructions.md](./agent-development-protocol.instructions.md)** — Creating/modifying agents with kernel integration
5. **[governance-testing-protocol.instructions.md](./governance-testing-protocol.instructions.md)** — Testing denials, audits, invariants, evidence
6. **[audit-evidence-protocol.instructions.md](./audit-evidence-protocol.instructions.md)** — Tamper-evident audit trails, RFC 3161 timestamping
7. **[governance-code-review.instructions.md](./governance-code-review.instructions.md)** — Review checklist: bypass detection, fail-closed verification

## 📚 Instruction Categories

### Core Governance (Mandatory for All)
- **governance-enforced-development.instructions.md** — No bypass paths, fail-closed, audit everything
- **mandatory-structured-generation-default.instructions.md** — No silent assumptions, adversarial self-review
- **obsidian-vault-write-boundary.instructions.md** — Read everywhere, write in vault only

### Agent Development (For Agent Creation/Modification)
- **agent-development-protocol.instructions.md** — Creating governed agents, risk levels, kernel integration
- **governance-testing-protocol.instructions.md** — Testing denials, audit generation, invariant compliance
- **governance-code-review.instructions.md** — Review checklist for PR approval

### Audit & Compliance (For Evidence Generation)
- **audit-evidence-protocol.instructions.md** — Evidence bundles, tamper-evident trails, RFC 3161

### Tool-Specific
- **codacy.instructions.md** — Codacy MCP integration for code quality analysis

### Reference
- **ARCHITECTURE_QUICK_REF.md** — Visual diagrams, data flows, system architecture
- **IMPLEMENTATION_SUMMARY.md** — Implementation status and integration points

## 🎯 Quick Navigation by Task

### Task: Creating a New Agent
**Read in order:**
1. agent-development-protocol.instructions.md (agent template)
2. governance-enforced-development.instructions.md (governance patterns)
3. governance-testing-protocol.instructions.md (test patterns)

**Key files to reference:**
- `src/app/agents/README.md` — Agent classification
- `src/app/core/kernel_integration.py` — Base classes
- `canonical/scenario.yaml` — Ground truth behavior

### Task: Modifying Existing Code
**Read in order:**
1. governance-enforced-development.instructions.md (no bypass paths)
2. mandatory-structured-generation-default.instructions.md (structured approach)
3. governance-testing-protocol.instructions.md (test denial paths)

**Key files to verify:**
- Run: `py -3.12 canonical/replay.py` (must show 5/5)
- Check: `data/governance_drift_alerts/` (no new alerts)

### Task: Code Review
**Read:**
1. governance-code-review.instructions.md (review checklist)

**Key verification:**
- [ ] No bypass paths
- [ ] Fail-closed behavior
- [ ] Denial tests present
- [ ] Canonical replay passes

### Task: Debugging Governance Issues
**Read:**
1. audit-evidence-protocol.instructions.md (evidence structure)
2. governance-testing-protocol.instructions.md (validation patterns)

**Key files to inspect:**
- `data/evidence/` — Evidence bundles
- `data/governance_drift_alerts/` — Denial alerts
- `data/acceptance_ledger/` — Acceptance ledger entries

## 🔒 Enforcement Hierarchy

**Priority 1: Workspace Profile (Overrides All)**
- `.github/copilot_workspace_profile.md`
- Defines: Production-grade standards, no minimal/skeleton code, full integration

**Priority 2: Mandatory Protocols (Cannot Be Skipped)**
- `mandatory-structured-generation-default.instructions.md`
- `governance-enforced-development.instructions.md`
- Enforced by: Pre-commit hooks, CI pipeline

**Priority 3: Domain-Specific Protocols (Required for Specific Tasks)**
- `agent-development-protocol.instructions.md` (for agent work)
- `governance-testing-protocol.instructions.md` (for testing)
- `audit-evidence-protocol.instructions.md` (for evidence)

**Priority 4: Tool-Specific Instructions (When Tools Used)**
- `codacy.instructions.md` (when using Codacy MCP)
- `obsidian-vault-write-boundary.instructions.md` (for vault writes)

## ⚙️ Configuration Metadata

All instruction files follow this frontmatter pattern:

```yaml
---
description: "Brief description of what this instruction covers"
applyTo: "**"  # or specific path pattern
tags: [governance, agents, testing, etc.]
created: YYYY-MM-DD
status: mandatory|current|deprecated
enforcement: pre-commit|pull-request|ci|manual
---
```

### ApplyTo Patterns
- `"**"` — All files (universal instructions)
- `"src/app/agents/**"` — Agent files only
- `"tests/**"` — Test files only
- `"**/*.py"` — All Python files

### Status Values
- **mandatory** — Must be followed (enforced by tooling)
- **current** — Active guidance (enforced by review)
- **deprecated** — Superseded by newer instruction

## 📋 Compliance Checklist

Before committing code, verify:

- [ ] **No bypass paths** — All actions route through governance
- [ ] **Fail-closed** — Denials prevent execution
- [ ] **Audit evidence** — Evidence bundles generated
- [ ] **Denial tests** — Every action has denial test
- [ ] **Canonical replay** — `py -3.12 canonical/replay.py` shows 5/5
- [ ] **Structured generation** — Requirements, design, pseudocode, implementation, review
- [ ] **Documentation** — Changes reflected in docs

## 🛠️ Tooling Support

### Pre-commit Hooks
Located: `.git/hooks/pre-commit`
Validates:
- Mandatory structured generation protocol
- Governance pattern compliance
- UTF-8 encoding

### CI Pipeline
Located: `.github/workflows/ci.yml`
Runs:
- Governance compliance tests
- Canonical scenario replay
- Evidence integrity validation

### Canonical Replay
Command: `py -3.12 canonical/replay.py`
Validates: 5 core invariants
- Escalation requires severity
- No bypass on high risk
- All denials audited
- Capability verification enforced
- Evidence chain intact

## 🔗 External References

### Documentation
- `docs/governance/` — Governance policy documentation
- `docs/nirl/NIRL_IMPLEMENTATION.md` — NIRL cascade reference
- `src/utf/docs/CANONICAL_STACK.md` — UTF stack reference

### Implementation
- `src/app/core/execution_gate.py` — Execution gate
- `src/app/core/cognition_kernel.py` — Cognition kernel
- `src/app/core/kernel_integration.py` — Agent integration
- `canonical/scenario.yaml` — Canonical governance scenario

### Validation
- `canonical/replay.py` — Invariant validation suite
- `tests/` — Test suites with governance tests
- `data/evidence/` — Evidence bundle storage

## 💡 Common Patterns

### Pattern: Governed Action
```python
from app.core.execution_gate import ExecutionGate

gate = ExecutionGate()
approved, result = gate.execute(
    domain="my_domain",
    action="my_action",
    context={"session_id": sid, "request_text": "..."},
    executor_fn=lambda ctx: perform_action(ctx),
)

if not approved:
    return {"success": False, "reason": result}
return result
```

### Pattern: Governed Agent
```python
from app.core.kernel_integration import KernelRoutedAgent

class MyAgent(KernelRoutedAgent):
    def __init__(self, kernel=None):
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium",
        )
    
    def my_action(self, args):
        return self._execute_through_kernel(
            action=self._do_action,
            action_name="MyAgent.my_action",
            action_args=(args,),
            requires_approval=True,
            risk_level="medium",
        )
```

### Pattern: Denial Test
```python
def test_action_denial():
    approved, result = gate.execute(
        domain="test",
        action="forbidden",
        context={"deny": True},
        executor_fn=lambda ctx: {"should_not_execute": True},
    )
    
    assert not approved
    assert "should_not_execute" not in str(result)
```

## 🎓 Learning Path

### For New Contributors
1. Read workspace profile: `.github/copilot_workspace_profile.md`
2. Read mandatory protocol: `mandatory-structured-generation-default.instructions.md`
3. Read governance basics: `governance-enforced-development.instructions.md`
4. Review agent examples: `src/app/agents/oversight.py`, `validator.py`, `explainability.py`
5. Run canonical replay: `py -3.12 canonical/replay.py`

### For Agent Developers
1. Read agent protocol: `agent-development-protocol.instructions.md`
2. Read testing protocol: `governance-testing-protocol.instructions.md`
3. Study kernel integration: `src/app/core/kernel_integration.py`
4. Review classification: `src/app/agents/AGENT_CLASSIFICATION.md`

### For Reviewers
1. Read review checklist: `governance-code-review.instructions.md`
2. Read enforcement guide: `governance-enforced-development.instructions.md`
3. Understand evidence: `audit-evidence-protocol.instructions.md`

## 📞 Questions?

If governance requirements are unclear:

1. **Read canonical scenario**: `canonical/scenario.yaml` (ground truth behavior)
2. **Run replay**: `py -3.12 canonical/replay.py` (see governance in action)
3. **Review agents**: `src/app/agents/` (real implementations)
4. **Check evidence**: `data/evidence/` (see audit trails)
5. **Ask**: Request clarification rather than implementing without governance

## 📝 Maintenance

**Last Updated**: 2026-05-13  
**Maintained By**: AI Systems Team  
**Review Cycle**: Quarterly  
**Next Review**: 2026-08-13

**Recent Changes**:
- 2026-05-13: Created governance instruction suite (5 new files)
- 2026-05-13: Added master index with task-based navigation

**Deprecated Instructions**: None
