# Local Agent Rulebook (Area 51 Mode)

Rules of engagement for every agent admitted to the facility. These are
enforced in code (registry validation + executor admission), not by
convention.

## Admission law

- No agent runs without a registry entry. Unknown agent → DENIED, audited.
- No command runs unless declared by the task AND allowed by the agent AND
  granted by a capability. Exact string match. No interpretation.
- No output path is writable unless declared by the task AND within the
  agent's allowed write paths.
- Registry invalid → the entire facility fails closed. Nothing runs.
- Facility mode gates schedules. BLACKSITE blocks everything except
  quarantine-class agents.
- `human_approval_required: true` denies, because no approval channel
  exists yet. Absence of an approval mechanism means NO, never yes.

## Conduct law

- Readers and watchers never write outside the evidence tree.
- Writers consume only hash-valid evidence from their declared sources.
- BLACK and PHANTOM evidence feeds no writer, except a task carrying the
  explicit `black_evidence_allowed` grant (phantom-report) or a
  quarantine-class agent.
- SECRET evidence feeds only a declared secret-handling writer, and every
  rendered value is redacted. An unredacted secret in any output is a
  critical defect.
- Locks: one lock per agent. Active lock denies. Stale lock denies and is
  reported — only the lock watcher lane may expire it. Nothing silently
  deletes a lock.
- Command failure is evidence, not error. ruff finding problems is the
  point. A command that cannot execute is FAILED; a timeout is KILLED.
- Quarantine means no trust — never deletion. There is no declassification
  path in code; declassification is a human act.

## Forbidden in the first swarm (everywhere, always)

merge, push, publish, deploy, delete, apply_patch, branch creation,
source mutation, registry mutation (except explicit `taar init`),
schedule mutation, capability self-grant, lock deletion, audit editing.
