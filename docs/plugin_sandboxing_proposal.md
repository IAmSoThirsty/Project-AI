# Plugin Sandboxing Proposal

Goal: design a practical, incremental approach to isolate third-party plugins so they cannot execute unintended code paths, access sensitive data, or escalate privileges. The intent is to provide concrete options, trade-offs, and an implementation roadmap that fits the Project-AI architecture (desktop PyQt6 app + optional web components).

This document summarizes research findings and proposes a phased plan.

---

## Threat model (short)

- Malicious or buggy plugin code can: access local files, exfiltrate secrets, call network APIs, run long-running or CPU/memory intensive tasks, or escalate by invoking system commands.
- Plugins are Python code authored by third parties and executed within the same runtime as the app unless explicitly isolated.

Assumptions:

- The host app trusts a limited set of core APIs it exposes to plugins.
- Users may install third-party plugins from the community.

Key security goals:

- Prevent arbitrary filesystem/network access by plugins.
- Limit CPU/memory usage and execution time.
- Enforce least-privilege API surface (only plugin API calls allowed).
- Maintain reasonable developer ergonomics for safe plugins.

---

## Technical options (summary)

1. Process Isolation (Recommended baseline)

- Run each plugin in a separate OS process.
- Use a minimal subprocess runner that exposes only a JSON-RPC API over stdin/stdout or a local socket.
- Advantages: simple, works cross-platform, straightforward to kill/restart, can apply OS-level controls (nice/rlimit) and monitor health.
- Drawbacks: IPC overhead, more complex debugging, cross-platform hardening differences.

2. Containerization (Docker) for high-assurance deployments

- Run untrusted plugins in lightweight containers with strict seccomp/namespace limits and read-only mounts.
- Advantages: strong isolation, network controls, resource limits.
- Drawbacks: Requires Docker on host (not suitable for end-user desktop by default), heavier.

3. Restricted Python interpreter (PyPy sandbox / subinterpreters / restrictedexec)

- Use Python's subinterpreters or a restricted VM that limits builtins and modules available to plugin code.
- Advantages: runs on host without heavy OS dependencies.
- Drawbacks: Python currently has weak sandboxing guarantees; subinterpreters do not guarantee security for untrusted code.

4. WebAssembly (WASM) or Pyodide

- Compile plugin logic to WASM (via Rust, AssemblyScript) or run Python in Pyodide inside a WASM runtime.
- Advantages: Strong isolation; limited syscalls; deterministic environment.
- Drawbacks: Porting effort; plugin authors must target WASM; limited library support.

5. Language-based sandboxing (e.g., running plugins in a separate Node/JS sandbox or a restricted JVM)

- Not ideal for Python-native plugin ecosystem.

---

## Recommended phased plan (practical)

Phase 0 — Governance + API hardening (Immediate)

- Document and publish a Plugin API contract that lists allowed functions and data structures.
- Make plugin registration explicit and require a manifest with declared capabilities (file access, network, sensors, etc.).
- Add a plugin review checklist and signing mechanism for first-party/verified plugins.

Phase 1 — Process Isolation with JSON-RPC (Baseline, short-term)

- Implement a lightweight plugin runner that spawns plugins as subprocesses.
- Communication: JSON lines (newline-delimited JSON) over stdin/stdout or socket with a small framing protocol.
- Host exposes a narrow RPC: `initialize`, `handle_event`, `shutdown`, and specific `data_request` APIs.
- Enforce resource limits with `resource.setrlimit()` (Linux) and adjusted priorities on Windows (Job Objects or platform APIs).
- Monitor heartbeat and a watchdog that kills long-running or memory-hungry plugin processes.
- Provide a debug mode where the plugin can run in-process for development convenience.

Phase 2 — Capability-based access control + policy engine (medium-term)

- Require plugin manifests to request capabilities; user or admin approves capabilities at install time.
- Implement a policy engine that allows/denies requests (e.g., plugin wants to read `data/` vs. only read `/data/plugins/<id>/public`).
- Log and audit capability use; surface violations to UI and disable plugin on misuse.

Phase 3 — Optional container sandbox (high-assurance)

- For enterprise or advanced users, offer an optional container runtime that executes plugins inside containers with strict networking, filesystem, and seccomp policies.
- Provide a docker-compose profile to run trusted-or-untrusted plugins in containers.

Phase 4 — WASM plugin SDK (long-term research)

- Investigate a WASM-based plugin runtime (wasmtime, wasm3) where plugin code runs as WASM module and communicates via a well-defined host API.
- This can provide stronger guarantees and portable isolation, but is higher effort.

---

## Concrete API + Protocol suggestion (Process Model)

- Plugin manifest (`plugin.json`):
  - `name`, `version`, `id`, `capabilities` (array), `entry_point` (script path)

- Host launches plugin:
  - `python plugin_runner.py --plugin-dir /path/to/plugin` which spawns plugin subprocess `python plugin_main.py`
  - Runner applies resource limits and drops privileges if possible

- RPC messages (JSONL):
  - Host -> Plugin: `{ "id": "uuid", "method": "init", "params": { ... } }`
  - Plugin -> Host: `{ "id": "uuid", "result": {...} }` or `{ "id":"uuid","error":"..." }`

- Allowed host-provided APIs (examples):
  - `get_user_profile()` → returns non-sensitive fields only
  - `post_event(name, payload)` → plugin not allowed to send raw network requests
  - `store_plugin_data(key, value)` → sandboxed storage under plugin directory

---

## Operational considerations

- **Telemetry & audit:** Log all plugin invocations and responses with correlation IDs.
- **Update & signing:** Support signed plugin packages (GPG or vendor signing) to avoid supply chain attacks.
- **User consent:** UI should show requested capabilities and last activity with an option to revoke.
- **Testing:** Add plugin compatibility tests that run plugins in a simulated runner in CI.

---

## Implementation roadmap (milestones)

1. Publish Plugin API manifest schema and capability model (1 week)
2. Implement `plugin_runner.py` (subprocess runner) and small sample plugin to demonstrate API (2-3 weeks)
3. Add resource manager and watchdog (1 week)
4. Add UI for plugin install + capability consent (2 weeks)
5. Provide optional Docker container mode and admin docs (2 weeks)
6. Research WASM as long-term improvement (ongoing)

---

## Short proposal summary (one-liner)

Run untrusted plugins in separate processes with a minimal JSON-RPC API, capability manifests, runtime resource limits, and an audit trail; optionally offer container/WASM modes for higher assurance.
