# Local Agent Facility — Thirsty's Standards V3

## Facility layout

All runtime state lives under `.project-ai/automation/` inside the governed
repo. Nothing else on the machine is touched.

    evidence/<agent>/<run_id>/   evidence.yaml | output.yaml, stdout.txt, stderr.txt
    reports/                     writer Markdown reports
    digests/                     governance + morning digests
    patches/                     MUST remain empty in the first swarm
    quarantine/<CLASS>/          quarantine records (pending human review)
    audit/YYYY-MM-DD.audit.jsonl append-only audit spine
    locks/<agent>.lock.json      one lock per agent
    cache/                       metadata-only cache index

## Facility modes

    GREEN      normal operations
    YELLOW     reduced schedules (hourly+ lanes continue, nightly blocked)
    ORANGE     essential watchers only
    RED        heartbeat/lock/runaway/phantom lanes only
    BLACKSITE  everything blocked except quarantine-class agents

Mode is set by a human in `taar.toml`. Agents never change it.

## Concurrency limits (taar.toml)

max_total_processes 6, max_active_workers 3, max_active_readers 2,
max_active_writers 1, max_heavy_agents 1, and zero git mutators, patch
writers, or branch writers in the first swarm.

## The Arbiter note

Between stateless runs, the human operator is the arbiter of record.
The audit spine and evidence tree exist so that arbitration can eventually
be performed from records instead of presence.
