# Project-AI

![Verified POC Surface](https://img.shields.io/badge/surface-verified_POC-2f6f46)
![Python 3.12](https://img.shields.io/badge/python-3.12-3776AB)
![Local First](https://img.shields.io/badge/runtime-local_first-3b4b5a)
![Obsidian Backed](https://img.shields.io/badge/memory-obsidian_backed-6f42c1)

Project-AI is a research workspace for building and testing local AI governance,
memory, and agentic tooling. This branch is the polished GitHub-facing surface:
it highlights only verified proofs of concept and gives newcomers a clear path
through the repo.

This branch does not claim the entire monorepo is production-ready. It presents
the verified pieces first, with evidence and scope boundaries.

## Why This Exists

Project-AI is exploring a practical question: how can a local AI workspace grow
memory, structure, verification, and agency without losing track of what is
actually proven?

The current answer is intentionally grounded: start with a Caregiver Scribe that
learns the workspace, writes its maps into Obsidian, and keeps public claims tied
to reproducible evidence.

## Start Here For Newcomers

If you are checking out Project-AI for the first time, start here:

1. Read this README to understand the verified surface.
2. Open [docs/START_HERE.md](docs/START_HERE.md) for the guided first pass.
3. Open [docs/VERIFIED_POC_MANIFEST.md](docs/VERIFIED_POC_MANIFEST.md) to see
   exactly what has been verified and how.
4. Run the focused verification commands below.
5. Explore the Caregiver Scribe outputs in your Obsidian vault.
6. Treat everything outside the verified manifest as experimental until proven.

## Quick Verification

From the repository root:

```powershell
$env:PYTHONPATH = "src"
py -3.12 -m pytest tests\test_personal_agent.py -q
py -3.12 .\scripts\verify_poc_surface.py
```

Expected result:

```text
tests/test_personal_agent.py .... 4 passed
Verified POC branch surface checks passed.
```

## Verified Proofs Of Concept

| POC | Status | What Is Verified |
| --- | --- | --- |
| Caregiver Scribe | Verified | The agent can map the Obsidian vault, then map Project-AI files as navigable metadata. |
| Obsidian-backed knowledge map | Verified | Generated scribe maps and JSONL manifests are written into the configured Obsidian vault. |
| Personal-agent CLI access | Verified | The direct script and Project-AI CLI package path both expose the scribe. |
| Branch-face verification | Verified | A focused checker enforces that README claims match the verified manifest. |

Detailed evidence lives in the
[Verified POC Manifest](docs/VERIFIED_POC_MANIFEST.md).

## Documentation Path

For a clean read-through:

| Document | Purpose |
| --- | --- |
| [Start Here](docs/START_HERE.md) | First-pass guide for newcomers. |
| [Verified POC Manifest](docs/VERIFIED_POC_MANIFEST.md) | Evidence and scope boundaries for each verified claim. |
| [Personal Agent](docs/PERSONAL_AGENT.md) | Caregiver Scribe usage and configuration. |
| [Reviewer Guide](docs/REVIEWER_GUIDE.md) | How to evaluate this branch without getting lost in the monorepo. |
| [POC Branch Policy](docs/POC_BRANCH_POLICY.md) | Rules for keeping the branch face evidence-first. |

## Main POC: Caregiver Scribe

The Caregiver Scribe is the first active agent role in this branch. Its job is
not to act as a general autonomous executor. Its job is to become the scribe:
learn the workspace, map the files, and write useful navigation back into
Obsidian.

Run:

```powershell
py -3.12 .\scripts\personal_agent.py scribe status
py -3.12 .\scripts\personal_agent.py scribe absorb-vault
py -3.12 .\scripts\personal_agent.py scribe learn-repo
```

Verified local result:

```text
Vault files indexed: 130
Project-AI files indexed: 6175
```

Generated scribe outputs are written here:

```text
wiki/_Scribe/Project-AI/
```

Key files:

- `00 Scribe Home.md`
- `Vault Navigation Map.md`
- `vault_manifest.jsonl`
- `Project-AI File Index.md`
- `repo_file_manifest.jsonl`

These generated outputs are ignored by git because they can contain private
local navigation state.

## Repository Layout

High-level areas newcomers will see:

| Path | Purpose | Branch-Face Status |
| --- | --- | --- |
| `src/app/personal_agent.py` | Caregiver Scribe implementation | Verified POC |
| `scripts/personal_agent.py` | Direct local launcher | Verified POC |
| `tests/test_personal_agent.py` | Focused scribe tests | Verified POC |
| `config/personal_agent.json` | Scribe and local-model config | Verified POC |
| `wiki/` | Obsidian vault | Source for scribe navigation |
| `docs/` | Policies, manifests, and project notes | Mixed; manifest is authoritative |
| `src/`, `api/`, `engines/`, `security/` | Experimental implementation areas | Not branch-face verified unless listed in manifest |

## For Reviewers

This branch is designed to be reviewed from the outside in:

1. Confirm the README only lists manifest-backed POCs.
2. Run the quick verification commands.
3. Inspect the focused scribe implementation and tests.
4. Treat older broad architecture documents as background research, not claims.

The reviewer flow is documented in
[docs/REVIEWER_GUIDE.md](docs/REVIEWER_GUIDE.md).

## Project-AI CLI

The package CLI exposes the personal scribe commands:

```powershell
$env:PYTHONPATH = "src"
py -3.12 -m app.cli personal scribe-status
py -3.12 -m app.cli personal absorb-vault
py -3.12 -m app.cli personal learn-repo
```

The direct script is the simplest local path:

```powershell
py -3.12 .\scripts\personal_agent.py scribe status
```

## What This Branch Is

- A professional GitHub front door for verified Project-AI POCs.
- A local-first workspace centered on the Caregiver Scribe.
- A branch where claims must point to commands and evidence.
- A cleaner way for reviewers to understand what works today.

## What This Branch Is Not

- Not a production release.
- Not an AGI claim.
- Not a claim that the entire monorepo is complete.
- Not a guarantee that historical documents in the repo are current.
- Not a public promise for every experimental subsystem.

## Branch Discipline

Do not add a capability to this README unless it has:

1. A named entry in [docs/VERIFIED_POC_MANIFEST.md](docs/VERIFIED_POC_MANIFEST.md).
2. A local verification command.
3. A recorded result.
4. A clear scope boundary.

If a feature is promising, experimental, partial, blocked, or merely designed,
it stays out of the branch face until verified.

See [docs/POC_BRANCH_POLICY.md](docs/POC_BRANCH_POLICY.md) for the policy.
