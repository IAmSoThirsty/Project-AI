# First Swarm Manifest

The first swarm is the report-only tier: it observes, verifies, accounts,
and writes reports. It cannot change anything.

## Membership

All 44 seed agents (see AGENT_SPECIFICATIONS.md). Every agent: autonomy 0,
`destructive_access: false`, no network, no patch/branch/push/merge/
publish/deploy/delete capabilities. Registry validation rejects any
capability of a forbidden type, so the constraint is structural, not
behavioral.

## Manual run order

See examples/first_swarm_manifest.example.yaml for the canonical sequence.
Rule: a writer is admissible only after its reader's evidence exists and
its hash validates.

## Exit criteria for the first swarm

1. Full manual sequence runs clean in GREEN mode.
2. Phantom lane proves detection: an unaccounted artifact turns the lane
   BLACK and only the declared handler can report it.
3. Secret lane proves redaction: no unredacted value in any evidence,
   report, or CLI output.
4. Audit spine reconstructs every run without gaps.
5. Zero mutations outside `.project-ai/automation/`.

The test suite encodes all five criteria.
