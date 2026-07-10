# Classification Model

Six levels, strictly ordered. Everything an agent produces is classified.
Escalation is monotonic within a run — nothing downgrades silently.

| Level | Rank | Meaning | Feeds writer? | Redaction | Quarantine |
|---|---|---|---|---|---|
| OPEN | 10 | safe operational data | yes | no | no |
| CONTROLLED | 20 | change-bearing, review required | yes | no | no |
| RESTRICTED | 30 | operationally sensitive | no | no | no |
| SECRET | 40 | private/dangerous values | only declared secret writer, redacted | yes | yes |
| PHANTOM | 50 | artifact with no producing run record | no* | no | yes |
| BLACK | 60 | unknown / malformed / unauthorized / corrupted | no* | no | yes |

\* Exception: a task with the explicit registry grant
`black_evidence_allowed: true` (validated to report/digest/quarantine task
types; in the seed, only `phantom-report`) or a quarantine-class agent.
This is the code form of "unless the task is specifically allowed."

## Assignment rules

- Secret-pattern match in any finding → SECRET, value redacted at capture
  (`first4...last4`, or `***` for short values). Private key material is
  withheld entirely.
- Artifact without a run record → PHANTOM; a phantom finding turns the
  producing lane BLACK.
- Malformed registry, invalid evidence hash, unknown builtin, malformed
  lock → BLACK.
- Workflow Guardian: critical finding → RESTRICTED (SECRET if in the
  secrets category); high → CONTROLLED; unparseable workflow → BLACK.
