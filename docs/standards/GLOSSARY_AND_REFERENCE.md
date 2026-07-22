# Glossary, Reference Index, and Disclaimer

> Part V of *Thirsty's Agents 101*. Normative definitions, navigation references, use limits, and
> publication status. Reproduced faithfully in Markdown.

## Normative glossary

The definitions below are reproduced from the V3Q manifest (see
[`packages/thirstys-standard-v3q/`](../../packages/thirstys-standard-v3q/)).

- **Applicable Control** — A control whose `applies_when` expression evaluates true for the current task context.
- **Authenticated Instruction** — An instruction bound to a verified principal and authorized scope.
- **Blocker** — A condition that prevents safe, truthful, or useful completion of the affected scope.
- **Complete** — All required deliverables and checks for the declared mode are satisfied or explicitly marked not applicable with reason.
- **Clearly Reversible** — A reversal path is known, available, bounded, authorized, and credible for the current state.
- **High Risk** — A task whose failure can materially affect security, authority, production, finances, legal position, private data, or external parties.
- **Material Claim** — A claim that can change a decision, permission, deployment, safety assessment, or completion status.
- **Minimal Effective Fix** — The least complex intervention that addresses the causal failure without creating greater risk or unjustified scope.
- **Safe To Continue** — No unresolved condition is known that would make the next declared action unsafe, deceptive, unauthorized, or corrupting.
- **Verified** — The claim is supported by admissible evidence from the relevant revision and environment.
- **Unknown Outcome** — The action was attempted but available evidence cannot establish whether its side effect occurred.

## Guidebook terms

- **Agent governance** — The rules, authority boundaries, evidence requirements, verification gates, and continuity practices used to control how an agent may act and how its work is judged.
- **Agent role** — A bounded professional function with defined inputs, responsibilities, prohibited behavior, outputs, and completion conditions.
- **Operating contract** — The standing behavioral contract that governs work before a role-specific assignment begins.
- **Role contract** — The task-specific professional boundary applied to an assigned agent role.
- **Human authority** — The retained authority of the authorized human owner to define objectives, approve material decisions, accept risk, and make final determinations.
- **Evidence package** — The commands, logs, tests, diffs, records, artifacts, or direct observations used to support a material claim.
- **Independent verification** — Assessment of a claim by a role or mechanism that is not relying solely on the claimant's interpretation.
- **Continuity map** — A durable operational handoff record describing current state, completed work, evidence, blockers, risks, and safe next action.
- **Fail closed** — A control posture in which missing authority, evidence, or a required condition prevents the affected action rather than silently permitting it.
- **Production readiness** — A bounded claim that the system can be built, configured, deployed, observed, recovered, and rolled back under documented conditions and known risks.

## Reference index

This index points to the controlling source location rather than substituting a new rule. In this repo,
Standard v3 is [`AGENTS.md`](../../AGENTS.md) §1; the UX/UI Standard is
[`THIRSTYS_UX_UI_STANDARD_V1.md`](THIRSTYS_UX_UI_STANDARD_V1.md); the V3Q manifest is
[`packages/thirstys-standard-v3q/`](../../packages/thirstys-standard-v3q/); the role templates are in
[`agent-role-templates/`](agent-role-templates/).

| Topic | Controlling reference |
| --- | --- |
| Accessibility claims | UX/UI Standard v1 §§ 11, 29–30 |
| Agent-neutral operation | Thirsty's Standard v3 § 39 |
| Architecture preservation | Thirsty's Standard v3 § 33; Architect; Refactorer |
| Authority and delegation | V3Q manifest; Coordinator; Governance Reviewer; Decision Arbiter |
| Blockers | Thirsty's Standard v3 § 6; UX/UI Standard § 6; Planner |
| Continuity | Thirsty's Standard v3 §§ 19–24; UX/UI Standard §§ 19–24; Memory Curator |
| Destructive actions | Thirsty's Standard v3 § 9; UX/UI Standard § 9 |
| Documentation truth | Thirsty's Standard v3 § 18; UX/UI Standard § 18; Documentation Writer |
| Evidence before claims | Thirsty's Standard v3 § 11; UX/UI Standard § 11; Verifier |
| Fail-closed governance | Thirsty's Standard v3 §§ 29–32; V3Q manifest |
| Hostile review | Thirsty's Standard v3 §§ 27–28; UX/UI Standard §§ 27–28; Critic; Red Team |
| Implementation | Implementer; Refactorer; Optimizer |
| Memory and durable state | Memory Curator; Observer; Continuity requirements |
| Planning and coordination | Planner; Coordinator |
| Production readiness | Thirsty's Standard v3 §§ 25–26; UX/UI Standard §§ 25–26 |
| Research and analysis | Researcher; Analyst |
| Security | Security Auditor; Red Team; Governance Reviewer |
| Testing and verification | Tester; Verifier |
| User experience | UX/UI Standard v1; User Experience Reviewer |

## Disclaimer

This publication is a practical guidebook for designing, governing, operating, reviewing, and documenting AI
agents. It is not a guarantee that an agent, architecture, workflow, or deployment will be failure-free,
secure, lawful, compliant, accurate, available, or fit for every purpose.

Written rules, prompts, manifests, contracts, tests, signatures, logs, and documentation do not
independently prove runtime enforcement or production behavior. Claims must remain bounded to the evidence,
version, environment, and conditions actually verified.

Use of this guide does not replace professional legal, cybersecurity, privacy, accessibility, safety,
financial, medical, or other domain-specific review when those disciplines apply.

The authorized human owner retains responsibility for objectives, approvals, risk acceptance, deployment
decisions, and final judgment. Agent recommendations remain advisory unless binding authority has been
explicitly and validly delegated.

The military, DARPA-report, or controlled-file visual treatment of the source is an editorial design choice
only. This document is not a publication of the United States Government, DARPA, the Department of Defense, or
any other government agency, and it carries no security classification.

Source materials are version-specific. Later revisions may supersede requirements, controls, implementation
status, or role definitions. Verify the controlling version before operational use.

> Thirsty's Projects LLC — Salt Lake City, Utah — Jeremy Karrick — ORCID 0009-0007-9715-4290 — © 2026. All rights reserved.
