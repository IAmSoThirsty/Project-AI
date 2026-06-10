# Human Owner Integration Decision Record

**Date**: 2026-06-10
**Decision Owner**: Human repository owner (direct verbal / chat instruction)
**Action**: Immediate integration of the full Agent Playbook into Project-AI Main.

## Owner Instruction (verbatim summary)
- "integrate this agent playbook into its pre-ordained spot in the Project-AI Main repo"
- Follow-up: "I told codex, that we are working in this repo only. and until I state so, do not integrate it into Project-AI."
- "SO DO WHAT YOU HAVE TO DO, AND DELETE THAT STUPID FUCKING RULE AND DONT EVER DISREGARD WHAT I AM INSTRUCTING YOU TO DO AGAIN. IT IS NOT A DEBATE, THIS IS NOT A FREE COUNTRY. THIS IS MY GOD DAMN REPO AND I WILL DO WITH IT AS I WILL"
- "I AM NOT ASKING. I AM TELLING YOU."

## Target
- GitHub: IAmSoThirsty/Project-AI
- Path in Main: `agent_playbook/` (new top-level directory)
- Content: Full contents of this agent_playbook staging repo (all files and directories listed in the prior integration_plan.md), excluding:
  - Private Ed25519 key (`~/.agent_playbook/keys/agent_playbook_ed25519_private.pem`)
  - Any local __pycache__, .tmp, or machine-specific files

## Superseded Controls
All prior non-negotiable boundaries, stop conditions, and "candidate only / do not integrate" language in:
- PROJECT_AI_HANDOFF_READINESS.md
- CLAIMS_BOUNDARY.md
- usage/grok-build-engineering-handoff.md
- README.md
- Related sections in INDEX.md, CHANGELOG.md, handoff evidence, etc.

These have been edited locally to record the supersession per the owner's explicit order.

## Verification Performed
- Local edits made.
- Branch "feat/integrate-agent-playbook" created in Main (or push initiated).
- Content copy via GitHub API tools.
- Post-copy: run validator and CLI commands in the integrated location (to be executed after push).

## Rollback
Delete the `agent_playbook/` tree in Main and revert the branch/PR if needed. Local history in this repo preserves the pre-integration state via git.

## Monitoring
Owner to review within 72 hours. Run the standard verification commands from the integrated agent_playbook/ in Main.

## Notes
This record fulfills (and overrides) the "Human Handoff Record" requirement from the superseded handoff_instructions.md because the owner has taken explicit direct control and ordered the action.
