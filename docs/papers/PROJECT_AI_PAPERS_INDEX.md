# Custom Skill Library — karrick1995

All nine skills validated with `agentskills validate` and saved to user scope. They load automatically when their triggers are matched.

| # | Skill | Primary Trigger |
|---|-------|----------------|
| 1 | `sovereign-response-contract` | Any technical/code/architecture request — enforces [CONTEXT]/[ARCHITECTURE]/[FULL IMPLEMENTATION]/[INVARIANTS]/[FAILURE MODES] |
| 2 | `forensic-repo-audit` | "audit", "review", "inventory", "fact-check" a repo — zero-hallucination file:line evidence |
| 3 | `project-ai-context` | Mentions of Project-AI, Waterfall, Monolith, Cerberus, Triumvirate, TTP, TARL, NIRL, UTF, Thirsty-Lang |
| 4 | `microservice-generator` | "new microservice", "FastAPI service", "Dockerized service", "add a service to Project-AI" |
| 5 | `tarl-nirl-security-review` | "security review", "threat model", "TARL check", "NIRL check", "Cerberus posture" |
| 6 | `zenodo-paper-prep` | "publish to Zenodo", "DOI", "CITATION.cff", "version bump", preprint prep |
| 7 | `constitutional-framework-author` | Drafting/extending AGI governance papers, constitutional specs, RFCs |
| 8 | `obsidian-knowledge-ingest` | "add to vault", "ingest into Obsidian", MOC creation, tag taxonomy enforcement |
| 9 | `letta-agent-module` | "Letta agent", "MemGPT", long-running agent with memory + hooks |

## Interop Chains

- **Code delivery:** `sovereign-response-contract` + `project-ai-context` + (`microservice-generator` | `letta-agent-module`)
- **Review / audit:** `forensic-repo-audit` + `tarl-nirl-security-review`
- **Publication:** `constitutional-framework-author` + `zenodo-paper-prep` + `obsidian-knowledge-ingest`

## Manage

Skills are managed at [perplexity.ai/computer/skills](https://www.perplexity.ai/computer/skills).
