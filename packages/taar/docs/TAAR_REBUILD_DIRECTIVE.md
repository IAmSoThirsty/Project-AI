# TAAR Rebuild Directive

**TAAR — Thirsty's Active Agent Runner.** Project-AI's local governed agent
taskforce, rebuilt as a universally adoptable Python package.

## Mission

A local-first facility of micro-agents that inspect, report, and account for
a repository under strict governance. Every agent has one task, minimal
authority, and produces maximum evidence. Governance precedes execution.
Deny by default. No trusted shortcuts, no side paths, no assumed continuity.

## Core doctrine

1. **One task per agent.** An agent that does two things is two agents.
2. **Minimal authority.** Agents receive only the capabilities their task
   requires, declared in the registry, granted at admission — never implied.
3. **Maximum evidence.** Every run leaves an evidence bundle or output
   record plus an append-only audit trail. If it isn't recorded, it didn't
   legitimately happen.
4. **Fail closed.** Missing registry, invalid hash, unknown command,
   blocked facility mode, absent human approval channel — all deny.
5. **No silent mutation.** The first swarm cannot merge, push, publish,
   deploy, delete, apply patches, or mutate source. Nothing merges itself.
6. **Everything classified.** OPEN < CONTROLLED < RESTRICTED < SECRET <
   PHANTOM < BLACK. Classification escalates and never silently downgrades.

## Repo structure

    taar/          runtime: models, config, registry, executor, evidence,
                   audit, locks, classification, quarantine, cache,
                   watchers, graph, scheduler, approvals, workflows, cli
    checks/        reader built-ins (one file per check, spec names)
    writers/       writer built-ins (report, digest, quarantine)
    registry/      the governed universe: agents, tasks, capabilities,
                   schedules, classifications (YAML, validated on load)
    tests/         contract test suite
    scripts/       registry generator + Windows runner/scheduler scripts
    docs/          this canon
    examples/      evidence/output/manifest samples + workflow examples
    action.yml     GitHub Action wrapper (Workflow Guardian)

## CLI

    taar init                      seed a repo (only path that writes registry)
    taar status | agents | graph
    taar run <agent-id>
    taar evidence | quarantine
    taar workflows scan|explain|classify|harden|evidence

## Execution model

First swarm executes manually or via OS schedulers (Task Scheduler / cron).
There is no resident daemon and no commander tier yet — the commander is a
later swarm, admitted under the same registry law it will enforce.
