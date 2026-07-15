# Project-AI Skills Library

Vendored from `T:\00-Active\thirsty-skill-library` on 2026-07-15. Contains **79** ChatGPT-Skills-format specialist skills (constitutional/governance + Thirsty orchestration).

## Structure

Each skill is a self-contained folder:

```
skills/<skill-name>/
  SKILL.md                 # frontmatter + workflow + quality gate
  agents/openai.yaml       # ChatGPT Skills interface manifest
  references/              # constitutional rules, schemas, templates
```

`CATALOG.json` is the machine-readable index (name, description, objective, outputs) mirrored from the upstream library. This README is the human index.

## Integration status

- **Vendored (additive):** all 79 skills copied under `skills/` with original structure preserved.
- **Not yet wired into runtime:** no `registry/*.yaml` (agents/capabilities/tasks) entries created. These are ChatGPT-Skills-format artifacts; mapping them into Beginnings' TAAR agent runner is a separate, governance-authority-touching step (see `CONTINUITY.md`).
- **Upstream format:** ChatGPT Skills (`SKILL.md` + `agents/openai.yaml`). Beginnings' own agent system uses `registry/*.yaml`; the two are not automatically interoperable.

## Skills by family

### Thirsty-native orchestration & workspace (4)

| Skill | Purpose |
| --- | --- |
| `thirsty-context-router` | Resolve ambiguous project terms and select the correct internal or public context before work begins. |
| `thirsty-knowledge-synthesizer` | Synthesize grounded knowledge across repositories, papers, specifications, websites, and internal documents. |
| `thirsty-work-orchestrator` | Coordinate end-to-end Thirstys Workshop workflows across context routing, ingestion, synthesis, governance, engineering, research, publication, and hostile review. |
| `thirsty-workspace-ingest` | Inventory and classify uploaded folders, repositories, papers, notes, and archives. |

### Constitutional design, review & translation (6)

| Skill | Purpose |
| --- | --- |
| `constitutional-diff-interpreter` | Interpret the governance meaning of changes between constitutional versions. |
| `constitutional-precedent-manager` | Organize and reason over prior governance decisions as precedent. |
| `constitutional-red-team` | Perform hostile review of constitutional and governance structures. |
| `constitutional-system-architect` | Design or evaluate governed-AI constitutional systems. |
| `constitutional-test-generator` | Generate tests from constitutional language and governance requirements. |
| `constitutional-translation-layer` | Translate between constitutional provisions, legal language, software policy, agent instructions, runtime controls, and human-readable rights. |

### Governance assurance & debt (2)

| Skill | Purpose |
| --- | --- |
| `governance-debt-register` | Track accumulated governance compromises such as unenforced policy, stale grants, missing appeals, temporary exceptions, and untested clauses. |
| `governance-traceability-auditor` | Audit traceability from governance principles through requirements, policies, controls, code, tests, and evidence. |

### Skill governance & lifecycle (8)

| Skill | Purpose |
| --- | --- |
| `skill-composition-auditor` | Audit whether combining individually acceptable skills creates contradictory, unsafe, circular, or overly powerful workflows. |
| `skill-constitution-auditor` | Audit whether a skill complies with governing principles for authority, tools, data, provenance, uncertainty, escalation, and user agency. |
| `skill-dependency-resolver` | Map skill dependencies, call permissions, cycles, foundational services, and version constraints. |
| `skill-drift-detector` | Detect when real usage exceeds a skill intended scope or users rely on unintended behavior. |
| `skill-evolution-manager` | Manage skill versions, migrations, compatibility, deprecation, and historical behavior. |
| `skill-observability-ledger` | Define or review records of significant skill invocations, sources, tools, decisions, outputs, effects, uncertainty, and governing versions. |
| `skill-permission-manifest` | Generate and validate machine-readable declarations of skill connectors, reads, writes, external effects, approvals, retention assumptions, and allowed calls. |
| `skill-regression-tester` | Run or design fixed evaluation suites whenever a skill changes. |

### Q hostile-review orchestration (1)

| Skill | Purpose |
| --- | --- |
| `q-orchestrator` | Coordinate Q hostile review using assumptions, epistemic status, contradictions, absent stakeholders, power, falsification, reversibility, mission drift, and attention allocation. |

### amendment-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `amendment-impact-simulator` | Evaluate proposed constitutional amendments before adoption. |

### architecture-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `architecture-decision-recorder` | Turn discussions, experiments, and changes into durable architecture decision records. |

### assumption-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `assumption-registry` | Create and maintain a live inventory of project assumptions. |

### attention-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `attention-allocation-advisor` | Prioritize limited attention using uncertainty reduction, constitutional importance, dependency centrality, leverage, urgency, and opportunity cost. |

### capability-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `capability-change-impact-review` | Reassess governance when an AI system gains materially new autonomy, planning, persuasion, tool use, memory, replication, or social influence. |

### concept-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `concept-lineage-tracer` | Trace how an idea, term, mechanism, or policy evolved across time and artifacts. |

### consent-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `consent-revocation-designer` | Design and audit meaningful consent and withdrawal mechanisms. |

### contradiction-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `contradiction-engine` | Find incompatible statements across repositories, papers, policies, conversations, and specifications. |

### counterfactual-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `counterfactual-governance-simulator` | Compare how alternative governance structures might have handled an event. |

### critic-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `critic-response-builder` | Process serious criticism by steelmanning objections, separating valid points from misunderstandings, and planning corrections or response. |

### decision-* (specialist) (2)

| Skill | Purpose |
| --- | --- |
| `decision-reconstruction` | Reconstruct consequential decisions from available evidence. |
| `decision-threshold-controller` | Define evidence and approval thresholds for reversible experiments, public claims, releases, amendments, partnerships, and irreversible deployments. |

### delegation-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `delegation-chain-auditor` | Trace delegated authority through principals, agents, subagents, tools, and external systems. |

### dependency-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `dependency-sovereignty-auditor` | Find external dependencies that can undermine independence or constitutional guarantees, including providers, hosting, identity, registries, data, funding, domains, and trust anchors. |

### emergency-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `emergency-powers-auditor` | Audit exception and emergency powers. |

### epistemic-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `epistemic-status-enforcer` | Apply explicit epistemic status to meaningful claims. |

### evidence-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `evidence-portfolio-manager` | Track positive, negative, contradictory, missing, and replicated evidence supporting major claims. |

### experiment-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `experiment-governance-designer` | Design experiments with explicit technical and constitutional boundaries, evidence thresholds, monitoring, rollback, and expansion criteria. |

### falsification-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `falsification-planner` | Design the strongest practical attempts to prove a theory, architecture, or governance claim wrong. |

### governed-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `governed-agent-designer` | Design agents with explicit purpose, jurisdiction, authority, tools, memory, delegation, escalation, refusal, audit, shutdown, and recovery boundaries. |

### hostile-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `hostile-unknowns-review` | Identify what is omitted, unasked, assumed, strategically ignored, or rendered invisible in a plan, architecture, paper, or decision. |

### human-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `human-agi-relations-reviewer` | Evaluate systems for durable human-AGI relations. |

### identity-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `identity-continuity-auditor` | Assess agent identity continuity across model upgrades, forks, restores, migrations, and memory changes. |

### incentive-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `incentive-compatibility-reviewer` | Assess whether actors benefit from following governance rules or are rewarded for evasion. |

### incident-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `incident-constitutional-review` | Run a constitutional postmortem after failure or near miss. |

### institutional-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `institutional-capture-simulator` | Model gradual capture of governance institutions. |

### jurisdiction-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `jurisdiction-boundary-mapper` | Map where human, agent, institutional, and constitutional authority begins and ends. |

### legitimacy-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `legitimacy-modeler` | Evaluate why affected parties should regard a governance system as legitimate. |

### memory-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `memory-governance-designer` | Design constitutional rules for agent memory admission, provenance, correction, expiry, access, isolation, inheritance, deletion, and contested records. |

### metric-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `metric-corruption-auditor` | Red-team metrics, benchmarks, KPIs, and thresholds for gaming, proxy failure, invisibility, and goal distortion. |

### mission-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `mission-drift-detector` | Compare current projects, priorities, partnerships, and behavior against declared mission and governing commitments. |

### model-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `model-agent-provenance-auditor` | Track what model, instructions, tools, memory, policies, data, and human interventions produced an output. |

### moral-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `moral-uncertainty-register` | Track unresolved moral assumptions and how decisions change under alternative ethical frameworks. |

### multi-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `multi-agent-treaty-designer` | Design agreements between independently governed agents or systems. |

### novelty-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `novelty-boundary-auditor` | Separate genuine novelty from recombination, renaming, parallel discovery, or overlooked prior art. |

### paper-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `paper-repository-consistency-checker` | Compare papers, repositories, diagrams, specifications, release notes, and public descriptions for consistency. |

### partnership-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `partnership-due-diligence` | Evaluate potential collaborators, institutions, platforms, and projects for mission, governance, technical, reputation, and dependency alignment. |

### power-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `power-distribution-analyzer` | Map actual power rather than formal authority. |

### prior-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `prior-art-literature-mapper` | Map current literature, prior art, and adjacent work around a concept or mechanism. |

### project-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `project-fragmentation-detector` | Detect when one conceptual project has split into incompatible repositories, branches, specifications, or communities. |

### proof-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `proof-obligation-generator` | Identify what must be demonstrated before accepting architectural, safety, governance, or research claims. |

### protocol-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `protocol-interoperability-auditor` | Audit whether separately governed systems can interact safely. |

### public-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `public-claim-risk-reviewer` | Review public statements for unsupported certainty, accidental commitments, terminology risk, misinterpretation, and inconsistency. |

### repository-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `repository-architecture-cartographer` | Map a repository as an architectural system. |

### research-* (specialist) (3)

| Skill | Purpose |
| --- | --- |
| `research-claim-auditor` | Audit scholarly and technical claims for evidence, overstatement, falsifiability, citation gaps, and reproducibility. |
| `research-publication-pipeline` | Coordinate manuscript and release preparation across papers, repositories, metadata, DOI, ORCID, SSRN, Zenodo, and project sites. |
| `research-question-generator` | Generate research questions from contradictions, gaps, failed tests, assumptions, and decision needs. |

### reversibility-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `reversibility-exit-review` | Evaluate whether actions can be undone and whether affected parties can meaningfully exit. |

### rights-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `rights-remedy-auditor` | Check whether every stated right has detection, standing, appeal, enforcement, restoration, and remedy. |

### scenario-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `scenario-constitution-tester` | Stress-test constitutions through extended social and institutional scenarios such as scarcity, conflict, capability shifts, misinformation, succession, and collapse. |

### semantic-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `semantic-canonicalizer` | Maintain canonical terminology across projects. |

### spec-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `spec-to-implementation-planner` | Convert research, governance, or product specifications into executable engineering plans. |

### stakeholder-* (specialist) (2)

| Skill | Purpose |
| --- | --- |
| `stakeholder-absence-detector` | Identify affected but absent or unrepresented stakeholders, including future persons, nonusers, maintainers, dependent institutions, and artificial agents. |
| `stakeholder-translation-engine` | Translate technical and governance work for researchers, architects, policymakers, partners, or the public without weakening meaning. |

### strategic-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `strategic-coherence-auditor` | Check whether research, repositories, publications, partnerships, and product work reinforce one another. |

### uncertainty-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `uncertainty-triggered-escalation` | Define when missing information, conflicting evidence, model uncertainty, normative ambiguity, unknown authority, or irreversible consequences require escalation. |

### unfinished-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `unfinished-work-recovery` | Find abandoned but potentially valuable work across branches, drafts, issues, notes, and publications. |

### value-* (specialist) (1)

| Skill | Purpose |
| --- | --- |
| `value-conflict-adjudicator` | Structure conflicts between values such as autonomy, safety, privacy, fairness, and collective welfare. |

## Machine-readable index

`CATALOG.json` — 79 entries, each with `name`, `description`, `objective`, `outputs`.

## Usage

- **Browse:** open any `skills/<name>/SKILL.md`.
- **Reference composition:** each SKILL.md ends with a `## Composition` section naming sibling skills to prefer.
- **Wire into Beginnings (future):** if these become TAAR-invokable, add `registry/agents.yaml` + `registry/capabilities.yaml` entries per skill and a continuity record. Do NOT grant governance authority without per-skill constitutional review (see `skill-constitution-auditor`).
