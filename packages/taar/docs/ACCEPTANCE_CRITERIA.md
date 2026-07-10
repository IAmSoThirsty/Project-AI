# Acceptance Criteria

Encoded in tests/ (87 tests, all passing at ship time).

## Registry & config
- Valid seed loads with zero validation errors (44 agents).
- Missing/malformed registry file → RegistryError (fail closed).
- Duplicates, unknown references, undeclared commands, out-of-bounds
  output paths, destructive flags, forbidden capability types → rejected.
- Config never creates registry files implicitly; `taar init` is the only
  writer, and it refuses to overwrite without `--force`.

## Admission & locks
- Unknown/disabled agents denied and audited. Invalid registry denies all.
- BLACKSITE denies non-quarantine agents. human_approval_required denies.
- Writer without evidence, or with a tampered hash, is denied (BLACK).
- Active or stale lock denies; stale locks are reported, never silently
  deleted; foreign run_id cannot release a lock; locks always release
  after success or failure.

## Evidence & audit
- Bundles carry run/agent/task/git-state/commands/findings/hash; hash is
  stable, excludes itself, and detects tampering.
- Audit is valid JSONL, append-only, hash-per-record, and covers admitted,
  denied, succeeded, failed, and escalation events.

## Classification & secrets
- Escalation is monotonic. SECRET requires redaction; BLACK/PHANTOM
  require quarantine. No unredacted secret in evidence, reports, or CLI.
- SECRET evidence feeds only the declared secret writer; BLACK/PHANTOM
  feed only the declared handler.

## Phantom & forbidden actions
- Unaccounted artifacts detected → BLACK; patch files flagged critical.
- No mutating capability exists; an 8-agent sequence leaves source
  untouched and patches/ empty.

## Workflow Guardian
- Dangerous example → SECRET with all seven pattern classes flagged.
- Hardened example → OPEN. Unparseable → BLACK. Harden is draft-only.
