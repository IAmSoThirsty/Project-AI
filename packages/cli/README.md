# Project-AI Operator CLI

The `project-ai` development CLI consumes the HTTP gateway. It does not import
or invoke governance, capability, execution, Arbiter, or RLP internals.

Configuration:

- `PROJECT_AI_API_URL` defaults to `http://127.0.0.1:8000`.
- `PROJECT_AI_API_TOKEN` is required for protected commands.

Canary values are read from `--value-file`; they are never accepted as command
arguments, which keeps them out of shell history and process listings.
