# Project-AI Operator CLI

The `project-ai` development CLI consumes the HTTP gateway. It does not import
or invoke governance, capability, execution, Arbiter, or RLP internals.

Configuration:

- `PROJECT_AI_API_URL` defaults to `http://127.0.0.1:8000`.
- `PROJECT_AI_API_TOKEN` is required for protected commands.

Canary values are read from `--value-file`; they are never accepted as command
arguments, which keeps them out of shell history and process listings.

Atlas commands:

- `project-ai atlas-status` reads the public analysis-only Atlas status.
- `project-ai atlas-sludge --snapshot-file snapshot.json --archetype hidden_elites`
  sends a Reality Stack snapshot to the protected gateway Sludge route.

The CLI still talks only to the HTTP gateway. It does not import Atlas,
governance, capability, execution, Arbiter, or RLP internals.
