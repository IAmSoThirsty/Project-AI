# AI Agents Documentation

> Recovered/reference material only: this directory is not current release
> evidence or deployment approval. The successor remains fail-closed until
> the current pre-deployment checklist and CAB evidence bundle pass.

**Created by**: AGENT-033 (Source Code Documentation Specialist)
**Date**: 2026-04-20
**Status**: Documentation-ready reference; not runtime deployment approval

---

## Quick Start

**New to agents?** Start here: [SOURCE_DOCS_AGENTS_INDEX.md](./SOURCE_DOCS_AGENTS_INDEX.md)

**Visual learner?** See: [AGENT_COLLABORATION_DIAGRAM.md](./AGENT_COLLABORATION_DIAGRAM.md)

**Project manager?** Read: [AGENT_033_DELIVERABLE_SUMMARY.md](./AGENT_033_DELIVERABLE_SUMMARY.md)

---

## Agent Documentation

| Agent | Purpose | Document | Word Count |
|-------|---------|----------|------------|
| **OversightAgent** | Compliance monitoring & enforcement | [oversight.md](./oversight.md) | 5,850 |
| **ValidatorAgent** | Input validation & security | [validator.md](./validator.md) | 7,300 |
| **PlannerAgent** | Task orchestration (legacy) | [planner.md](./planner.md) | 5,900 |
| **ExplainabilityAgent** | Decision transparency | [explainability.md](./explainability.md) | 8,200 |

**Total Documentation**: 38,200 words across 7 files

---

## Directory Structure

```
agents/
├── README.md                             (this file)
├── SOURCE_DOCS_AGENTS_INDEX.md           (navigation hub)
├── AGENT_COLLABORATION_DIAGRAM.md        (architecture diagrams)
├── AGENT_033_DELIVERABLE_SUMMARY.md      (completion report)
├── oversight.md                          (OversightAgent docs)
├── planner.md                            (PlannerAgent docs)
├── validator.md                          (ValidatorAgent docs)
└── explainability.md                     (ExplainabilityAgent docs)
```

---

## Quality Standards

All documentation meets:

✅ **Completeness**: 1,200+ words per agent (avg: 6,813 words)
✅ **Metadata**: 100% YAML frontmatter compliance
✅ **Examples**: 3+ usage scenarios per agent (16 total)
✅ **Performance**: Benchmarks & complexity analysis included
✅ **Troubleshooting**: Common issues with solutions
✅ **Four Laws**: Explicit integration documented
✅ **Cross-References**: Links to CognitionKernel, related agents

---

## Key Concepts

### Three-Tier Architecture

- **Tier 1 (Governance)**: OversightAgent - sovereign authority
- **Tier 2 (Execution)**: ValidatorAgent, ExplainabilityAgent - service functions
- **Tier 3 (Legacy)**: PlannerAgent - ungoverned stub (deprecated)

### CognitionKernel Integration

All agents (except PlannerAgent) inherit from `KernelRoutedAgent`:

```python
from app.core.kernel_integration import KernelRoutedAgent

class MyAgent(KernelRoutedAgent):
    def __init__(self, kernel=None):
        super().__init__(
            kernel=kernel,
            execution_type=ExecutionType.AGENT_ACTION,
            default_risk_level="medium"
        )
```

### Four Laws Hierarchy

1. **Zeroth Law**: Humanity preservation (highest priority)
2. **First Law**: Human safety (enforced by ValidatorAgent)
3. **Second Law**: User partnership (allowed unless conflicts)
4. **Third Law**: System preservation (lowest priority)

---

## Contributing

When adding new agent documentation:

1. Copy template from existing agent docs
2. Include all required YAML frontmatter fields
3. Document constructor + all public methods
4. Add 3+ usage scenarios (simple → complex)
5. Explain Four Laws integration
6. Include performance benchmarks
7. Add troubleshooting section
8. Cross-reference related agents

---

## Related Documentation

- **[CognitionKernel](../core/cognition-kernel.md)**: Central governance system
- **[Four Laws](../core/four-laws-ethics.md)**: Ethical framework
- **[Platform Tiers](../core/platform-tiers.md)**: Authority hierarchy

---

**Maintainer**: Architecture Team
**Review Cycle**: Quarterly
**Next Review**: 2026-07-20

<!-- sovereign-vault-index-link -->
Central Index: [[Sovereign Vault Index]]
